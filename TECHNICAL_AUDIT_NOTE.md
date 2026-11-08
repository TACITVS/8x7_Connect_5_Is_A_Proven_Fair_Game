# Technical note: proof scope, strategy obligations, and solver reproducibility

Audited snapshot: `4315ed08291a37bb010cd58d5e229573e3f5db7e`.

This note records a source audit and independent finite calculations. The snapshot contains useful combinatorial results and a substantial proposed certificate-verification framework. It does not supply the concrete checked strategies needed to derive the advertised unconditional draw theorem. There is also a source-level Rocq sort mismatch and several solver and benchmark reproducibility issues.

This assessment does not establish that the game is a win for either player. It establishes a gap between the published evidence and the claim that the initial position has been formally proved to be a draw.

**1. Scope, method, and limits**

The audit covered the six Rocq theory files, the assumption-inspection script, the Lean development, the C/CUDA/Python solver sources, build scripts, README, companion Markdown discussions, and the main paper's LaTeX source. References below point to the audited commit so that later changes do not alter the evidence. The PDFs were not independently compared page by page with their source. The historical discussion was considered for its claims about this development; this note does not certify an exhaustive literature search or claims of priority.

The accompanying [reproduction script](audit/reproduce_findings.cjs) reconstructs the finite geometry, the relevant opening-structure conditions, the bitboard win detector, and the CUDA benchmark inputs. It uses JavaScript integer arithmetic and BigInt, with no external packages. Its assertions were executed successfully in a JavaScript runtime during this audit.

A working local compiler session was unavailable. No successful clean Rocq, Lean, C, or CUDA build is claimed here. The sort mismatch, stale C interfaces, and synchronization issues below are source-level findings; no compiler diagnostic or race-detector trace was obtained. The JavaScript checks are independent reconstructions, not executions or formal equivalence proofs of the original programs. No full-game search was completed.

**2. The game specification is recognizable, but the main theorem is conditional**

In this development, fairness means a draw under optimal play: both players can avoid losing. It does not express equal winning probabilities for human players.

The list-of-columns board, legal drop operation, 76 winning segments, and 56-ply minimax evaluation in [C5Game.v](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/C5Game.v) encode the expected finite game from the initial position. The 56-ply bound is sufficient because a legal move from a well-formed reachable board fills one of its 56 cells. The safety predicates are intended for positions where nobody has already won; their use should be assessed with that precondition in mind.

The important distinction is visible in [connect5_8x7_fair](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/C5Certificate.v#L291):

~~~coq
Theorem connect5_8x7_fair :
  (exists c0,
     legal initial c0 = true /\
     strategy White (play initial c0 White) Black) ->
  strategy Black initial White ->
  game_value = Draw.
~~~

Leaving aside the typing issue discussed below, this is an appropriate *conditional reduction*: defensive strategies for both sides imply a draw. It does not construct those strategies.

Similarly, [cert_fair](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/C5CertChecker.v#L424) requires two successful concrete calls to `check_cert_node`. The tracked tree contains the certificate datatype and checker, but no concrete pair of root certificates, no successful root-check equations for that pair, and no resulting unconditional theorem `game_value = Draw`.

An axiom-free proof of `P -> Q` does not prove `Q` until `P` has been established. Consequently, the generic soundness results cannot on their own support the headline claim.

**3. Line coverage is weaker than a valid defensive structure**

[checker definitions](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/C5CertChecker.v#L128) deliberately separates `check_cover` from `check_static`. Coverage checks whether every winning segment intersects a proposed blocking resource. The full static checker additionally checks board well-formedness, frozen threats, distinctness and emptiness of unit cells, pair geometry, partitioning, free-column constraints, and mode/parity requirements.

The concrete theorems `opening_27pair_line_cover` and `core10_covers_all_76_lines` establish only `check_cover = true`. They do not establish `check_static = true`.

There are explicit obstructions in the supplied values:

| Structure | Failing condition | Consequence |
| :--- | :--- | :--- |
| `white_27pair_struct` | Its 27 pairs cover 54 of the 55 empty cells. Cell `(4,6)` is unassigned; `s_free = []` and `s_frozen = None`. | `check_partition` rejects the structure. |
| `white_core10_struct` | It has `s_parity = false` and nine strong pairs. In that mode `check_mode` requires the strong and rigid lists to be empty and no frozen suffix. | `check_mode` rejects the structure. It also leaves empty cells outside the allowed partition. |

These facts follow directly from [the concrete opening structures](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/C5CertChecker.v#L454) and the checker definitions. The reproduction script independently confirms the first unassigned cell and the second mode failure. It does not claim to execute the complete Rocq checker.

Leaving a cell unpaired might be handled by a different invariant or a strategy transition. That requires an additional proof. Calling a cell geometrically redundant or double-blocked does not establish that the defender can spend the resulting tempo safely.

**4. The finite geometric observations are supported**

Independent enumeration agrees with the board geometry:

| Quantity | Independently obtained value |
| :--- | ---: |
| Horizontal five-cell segments | 28 |
| Vertical five-cell segments | 24 |
| Diagonal five-cell segments | 24 |
| Total | 76 |
| Nonvertical segments met by the ten-cell core | 52 of 52 |
| Nonvertical segments met by the seven-cell central wall | 40 of 52 |
| Segments containing `(4,6)` | 6 |
| Proposed upper cells on those six segments, in the script's enumeration order | 2, 4, 4, 4, 4, 2 |

The ten-cell transversal is

~~~text
{(3,0),
 (2,2), (2,4), (2,6),
 (4,1), (4,3), (4,5),
 (6,2), (6,4), (6,6)}.
~~~

[the Lean ten-cell theorem](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/lean4/Connect5HandProof.lean#L176) gives a convincing affine-line/parity argument for its nonvertical coverage. Every five-column window crosses columns 3 and 4 and at least one of columns 2 or 6. Odd-row intersections at column 4 meet the core directly. Even-row intersections can be treated at columns 2 or 6, with the ground-row exception covered by the opening stone and diagonal boundary cases handled separately.

The central wall consists of the four even-row cells of column 3 and the three odd-row cells of column 4. Its 40 covered nonvertical segments are all 28 horizontals plus 12 diagonals. The six wing cells in columns 2 and 6 cover the remaining 12 diagonals. [the central wall proofs](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/lean4/Connect5HandProof.lean#L427) formalizes this useful geometric decomposition.

The vertical-domino observation is also correct: each five-row window in rows 0 through 6 contains the pair of rows 1 and 2, or the pair 3 and 4.

These are coverage statements about sets and pairs. Turning them into a game strategy requires proving that the defender can secure the relevant stones or pair responses against every legal opponent move. The word "guaranteed" in the prose should be read as conditional on a valid strategic invariant, not as a consequence of coverage alone. No minimal-cardinality claim about the ten-cell set was established by this audit.

**5. The parity law does not supply the missing opening trunk**

After one opening move, 55 empty cells remain, so they cannot all be partitioned into disjoint two-cell pairs. This obstruction is correctly identified.

For a frozen threat at odd row `ft`, the suffix from row `ft - 1` through row 6 has `8 - ft` cells. If the total empty count is odd, removing that odd suffix leaves an even count. [the bounded parity law](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/C5CertChecker.v#L672) correctly expresses the arithmetic with relevant bounds.

The strategic application needs more than parity. A real defender threat must exist: the other four cells of a winning segment must already belong to the defender. The surrounding invariant must also ensure that an attacker move does not win before the defender's threatened reply.

At the one-stone opening position such a four-stone threat does not yet exist. A complete argument must provide legal defensive replies on every branch leading to a valid structure, a terminal draw, or a defender win. The companion paper's discussion of a finite opening trunk acknowledges this remaining task. Neither the odd-minus-odd identity nor double-blocking of `(4,6)` establishes that trunk. See [the companion paper](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/HILBERT_ERDOS_PEN_AND_PAPER_PROOF.md).

There is also an elementary documentation problem with describing a pure vertical Claimeven partition of all 56 cells: pairs `(c,2k)` and `(c,2k+1)` give three pairs per seven-cell column and leave its top cell unpaired. Additional handling of those top cells is required; the usual vertical picture alone supplies 24 pairs, not 28.

**6. A Rocq sort mismatch should prevent compilation as written**

[the strategy family and constructor](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/C5Certificate.v#L24) declares:

~~~coq
Inductive strategy (d : player) : board -> player -> Type :=
~~~

The `StratAtt` constructor then uses:

~~~coq
has_line (play b c (other d)) (other d) = false /\
strategy d (play b c (other d)) d
~~~

Rocq's standard `/` is `and (A B : Prop)`, whereas the right operand here has explicitly been declared in `Type`. The existential/conjunction in the main strategy theorem repeats that mismatch. This is a source-level typing problem under the ordinary Rocq rules, not an observed diagnostic from a build during this audit. The standard connective is defined in [Rocq's Logic.v](https://github.com/rocq-prover/rocq/blob/master/theories/Corelib/Init/Logic.v).

A repair would either make the strategy family propositional, or consistently express data-bearing branches using products/dependent pairs and state existence through an appropriate inhabitation proposition. Such a repair needs compilation and rechecking of the affected proofs; it does not construct the missing game strategies.

**7. Assumption inspection and the Lean development have narrower scope than the advertised conclusion**

[CheckAssumptions.v](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/CheckAssumptions.v) prints assumptions for named results. It does not instantiate the conditional fairness theorems or create strategy witnesses. "Closed under the global context" cannot discharge hypotheses explicitly present in a theorem's type.

No actual `Admitted` or `Axiom` declarations were found in the inspected Rocq files. That is useful source hygiene, but successful compilation and a proved unconditional result remain separate obligations.

The Lean development supports the analytic geometry and arithmetic. Its `zermelo_mutual_safety_draw` takes an abstract outcome and hypotheses excluding either winning outcome; its follow-up induction theorem assumes base cases and the invariant-preserving step. These are sensible abstract statements, but no operational Lean board strategy is supplied that establishes those hypotheses for the initial game. See [the Lean safety and induction statements](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/lean4/Connect5HandProof.lean#L342).

The README itself reports dependencies such as `propext` and `Quot.sound` for Lean results. "No custom axioms" is therefore a more precise description than an unqualified "zero axioms." These standard logical principles are not the missing strategic witnesses.

The build scripts also have limited auditing behavior. The Rocq script checks compilation exit codes and prints assumption output; it does not programmatically reject nonempty axiom reports. The Lean script checks for `sorryAx` in output, which is not a general allowlist of all permitted axioms. The Rocq executable path is machine-specific. The Lean script invokes a file from the repository root while the toolchain pin is under `lean4/`; a reproduction should explicitly select that pinned toolchain. See [build.ps1](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/build.ps1) and [build_lean.ps1](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/build_lean.ps1).

**8. The CUDA program performs shallow tactical evaluation**

[the CUDA evaluator](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/solver/c5_gpu_search.cu#L95) contains checks for existing wins, an immediate winning move, opponent double threats, some immediate blunders, and a central-column preference. Its default score means inconclusive. It contains no recursive minimax solution, no complete defensive strategy search, and no export of a Rocq strategy certificate.

The adaptation of a column-sentinel bitboard is reasonable. Independent comparison of its shift-and-mask win detector with explicit segment enumeration found:

- all 76 individual winning masks detected;
- all tested four-stone masks formed by removing a stone from those masks rejected;
- zero discrepancies on 100,000 deterministic generated bitboards with sentinel bits cleared.

The test generator uses a fixed seed. These are component-level checks on a JavaScript reconstruction, not CUDA execution, exhaustive testing of all bitboards, or formal equivalence with the Rocq board model.

The standalone CUDA check program exercises just one vertical win and is insufficient by itself to validate all directions and boundary cases.

**9. The supplied benchmark differs from the documented workload**

The CUDA main program fixes `N = 262144` and generates inputs using:

~~~cpp
int moves = 2 + (i % 20);
int c = (i * 7 + m * 11) % 8;
~~~

A board depends only on `i % 20` and `i % 8`, so the generator repeats with period dividing 40. Independent reconstruction yields **38 distinct board pairs among 262,144 inputs**.

Every input is evaluated with White as mover. Exactly 131,072 generated inputs have an odd number of played stones and therefore should have Black to move under the alternating-play model. These positions need not be invalid as bit patterns, but that mover selection does not represent their actual turn.

The checked-in program performs one launch for 262,144 positions. The README's reported workload of 104,857,600 positions with 4,194,304 threads is not reproduced by that source as written. See [the benchmark source](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/solver/c5_gpu_search.cu#L225) and [the documented benchmark](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/README.md#L440).

A repeated-input microbenchmark can measure throughput for its particular workload. It does not establish full-game solving throughput. Comparing a shallow GPU evaluation against a CPU search node that may perform expensive pairing analysis does not establish the advertised solving speedup; equivalent computations, representative inputs, timing details, and reproducible measurements are needed.

The reported 405.35 million evaluations per second and 41,362-fold speedup were not independently measured in this audit.

**10. CPU solver reproducibility and concurrency issues**

The supplied sources have interface inconsistencies:

- `solver/search.c` and `solver/dfpn.c` call `leaf(...)`, while the supplied header defines `leaf_x(...)`.
- Both files reference `r1calls` and `r2calls`; the supplied header explicitly says the old call counters were removed and does not declare them.

Without another wrapper or declarations, these translation units are not reproducible as supplied. This is a source inspection finding, not a captured compiler result. See [search.c](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/solver/search.c), [dfpn.c](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/solver/dfpn.c), and [rules.h](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/solver/rules.h#L248).

The parallel programs use a shared `volatile int STOP`. Workers write that flag and read it concurrently, and the progress reporter reads counters that workers increment without synchronization. `volatile` does not provide inter-thread synchronization; these conflicting non-atomic accesses constitute data-race concerns under the C memory model. The table's separate locks do not protect these accesses. Use appropriate atomics or locking and validate with a race detector. No claim is made here that a particular observed search result was corrupted. See [the shared stop flag](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/solver/pdfpn_fast.c#L20) and [the progress counters](https://github.com/TACITVS/8x7_Connect_5_Is_A_Proven_Fair_Game/blob/4315ed08291a37bb010cd58d5e229573e3f5db7e/solver/pdfpn_fast.c#L318).

Search success messages and internal extraction/counting routines are not replacements for serialized certificates accepted by the formal checker. The external engine can remain outside the trusted proof base only if its actual output is independently checked. The current gap is that such a checked output is not supplied.

**11. Reproduction and completion criteria**

Run the independent checks with Node.js:

~~~sh
node audit/reproduce_findings.cjs
~~~

The output includes the counts above, `white27Unassigned: [[4,6]]`, `whiteCoreModePass: false`, zero detector discrepancies, and the benchmark's 38 distinct inputs. These assertions verify only the stated reconstructions.

To complete the formal draw claim:

1. Repair source-level typing and interface issues and demonstrate clean builds from a pinned snapshot.
2. Publish complete defensive certificates for White after a specified legal opening and Black from the initial position.
3. Prove both root checks succeed using the full checker.
4. Derive an unconditional theorem such as:

   ~~~coq
   Theorem connect5_8x7_draw : game_value = Draw.
   ~~~

5. Provide automated reproduction with actual proof-assistant output and explicit allowed logical dependencies.
6. Publish benchmark inputs and equivalent CPU/GPU workloads, and keep tactical-evaluation rates distinct from complete search rates.

The supported contribution is the geometric coverage analysis and the proposed invariant/certificate framework. The unconditional initial-position draw, clean build claims for this snapshot, and advertised solver speedup are not established by the evidence audited here.
