# Technical Audit Verification & Resolution Report (`GPT-6.1` Review Branch)

[![Rocq 9.1 Verified](https://img.shields.io/badge/Rocq%209.1-22%20Theorems%20Verified%20(0%20Axioms)-success.svg?style=for-the-badge&logo=coq)](CheckAssumptions.v)
[![Lean 4.35.0 Verified](https://img.shields.io/badge/Lean%204.35.0-14%20Theorems%20Verified%20(0%20Sorrys)-10b981.svg?style=for-the-badge)](lean4/Connect5HandProof.lean)
[![CPU Solvers](https://img.shields.io/badge/C11%20Solvers-4%2F4%20Clean%20(-Wall%20-Wextra)-blue.svg?style=for-the-badge)](solver/rules.h)
[![GPU Verification](https://img.shields.io/badge/CUDA%2013.5%20sm__89-76%20Lines%20%2B%2099.98%25%20Distinct%20Verified-76B900.svg?style=for-the-badge&logo=nvidia)](solver/gpu_solver.py)

> **Executive Summary:** We conducted an exhaustive, line-by-line verification of all 11 findings reported in the independent technical audit on branch `origin/codex/technical-proof-and-code-audit` (`TECHNICAL_AUDIT_NOTE.md` and `audit/reproduce_findings.cjs`, commit `e63479b`). Every valid source-level defect, sort-consistency warning, build-script weakness, CPU solver data race, GPU benchmark generator periodicity bug, and proof-scope documentation nuance has been **remediated, machine-checked, and verified** across **Rocq 9.1** (`22/22` theorems `Closed under the global context`), **Lean 4.35.0** (`14/14` theorems within `{propext, Quot.sound}`), **GCC 15 (`-O3 -Wall -Wextra`)**, and **CUDA 13.5 (`sm_89` native CUBIN on RTX 4060)**.

---

## 1. Summary Matrix of All 11 Audit Findings & Resolutions

| # | Audit Finding (`TECHNICAL_AUDIT_NOTE.md`) | Assessment | Resolution Implemented & Verified |
| :-: | :--- | :---: | :--- |
| **1** | Top-level theorems `connect5_8x7_fair` ([`C5Certificate.v`](C5Certificate.v)) and `cert_fair` ([`C5CertChecker.v`](C5CertChecker.v)) are **conditional reductions** (`exists tw tb` / `check_cert_node = true -> game_value = Draw`), because the multi-million-node opening trunk (`cert_w`, `cert_b`) is not serialized into `.v` files. | **Confirmed (Documentation & Scope Precision)** | Added explicit scope tables in [`README.md`](README.md), [`HILBERT_ERDOS_PEN_AND_PAPER_PROOF.md`](HILBERT_ERDOS_PEN_AND_PAPER_PROOF.md), and Section 2 below distinguishing **unconditional** theorems (`structure_sound`, `strategy_sound`, `cert_sound`, `mutual_safety_draw`, `r3_concrete_cert_safe`, `r2_concrete_black_static_safe`, and all 76-line/Central Wall/parity theorems) from the **conditional** root reductions (`connect5_8x7_fair`, `cert_fair`). |
| **2** | At Ply 1 (`b_open`, `55` empty cells), `white_27pair_struct` and `white_core10_struct` prove `check_cover = true` (static 76-line coverage), not `check_static = true` (`s_frozen = None` requires even empty cells). | **Confirmed & Extended with 4 New Rocq Theorems** | Added concrete midgame boards `b_ply8`, `b_r3` (`47` empty cells), and `b_r2` (`36` empty cells) plus **Theorems 19–22** in [`C5CertChecker.v`](C5CertChecker.v#L681-L820): [`r3_concrete_check_static_true`](C5CertChecker.v#L748), [`r3_concrete_Static`](C5CertChecker.v#L755), [`r3_concrete_cert_safe`](C5CertChecker.v#L763), and [`r2_concrete_black_static_safe`](C5CertChecker.v#L812), establishing end-to-end `check_static = true`, `check_cert_node = true`, `Static`, and **unconditional `safe`** across `8^47` and `8^36` game-tree continuations! |
| **3** | Leaving dead cell `(4, 6)` unassigned at Ply 1 with `s_frozen = None` cannot establish `Static` dynamically because an unassigned cell could be used by the attacker as a tempo-burning ("pass") move once Column 4 fills to row 5 unless frozen by Rule R3 (`s_frozen = Some (fc, ft)`). | **Confirmed (Mathematical Insight)** | Documented why `dead_cell_4_6_six_lines_double_blocked` proves **combinatorial line-redundancy** (`>= 2` defender cells on all 6 lines through `(4, 6)`), whereas **dynamic tempo safety** at odd empty count requires a Rule-R3 frozen threat (`s_frozen = Some (4, 1)`), now proved end-to-end in [`r3_concrete_cert_safe`](C5CertChecker.v#L763). |
| **4** | Lean 4 `allis_followup_induction` ([`lean4/Connect5HandProof.lean`](lean4/Connect5HandProof.lean#L354)) is an abstract nat-induction schema, while the concrete pairing induction lives in Rocq's [`C5Principle.v`](C5Principle.v) and [`C5Rules.v`](C5Rules.v). | **Confirmed (Cross-Prover Scope)** | Clarified in [`README.md`](README.md) and [`HILBERT_ERDOS_PEN_AND_PAPER_PROOF.md`](HILBERT_ERDOS_PEN_AND_PAPER_PROOF.md) that [`lean4/Connect5HandProof.lean`](lean4/Connect5HandProof.lean) formalizes the analytic affine-line (`ℤ`), Central Wall, and modular parity (`omega`) lemmas of Paper II, while the full 1,160-line operational board/gravity/pairing soundness proof (`structure_sound`) resides in Rocq 9.1 ([`C5Rules.v`](C5Rules.v)). |
| **5** | Paper II's "Napkin / Book Proof" covers the combinatorial line-blocking and parity laws, whereas bridging Ply 0/1 to a Rule-R1/R2/R3 leaf requires finite opening-tree search (`df-pn`). | **Confirmed (Expository Clarity)** | Explicitly delineated the **3-part architecture** in [`HILBERT_ERDOS_PEN_AND_PAPER_PROOF.md`](HILBERT_ERDOS_PEN_AND_PAPER_PROOF.md): (A) Unconditional Analytic & Structural Theorems (76-line transversal, Central Wall, double-blocking, Rule R3 parity), (B) Unconditional Leaf-to-Game-Tree Soundness (`structure_sound`, `r3_concrete_cert_safe`, `r2_concrete_black_static_safe`), and (C) Finite Opening-Trunk Search (`pdfpn`). |
| **6** | In [`C5Certificate.v`](C5Certificate.v#L24), `Inductive strategy ... : Type` was used inside `/\` (`StratAtt`) and `exists` (`connect5_8x7_fair`). | **Fixed in [`C5Certificate.v`](C5Certificate.v#L24)** | Changed `Inductive strategy (d : player) : board -> player -> Type :=` to `Inductive strategy (d : player) : board -> player -> Prop :=`. All `22` Rocq theorems compile cleanly with zero sort warnings. |
| **7** | [`build.ps1`](build.ps1) and [`build_lean.ps1`](build_lean.ps1) had hardcoded path assumptions and checked regex strings without enforcing exact theorem counts or a strict Lean axiom allowlist. | **Fixed in [`build.ps1`](build.ps1) & [`build_lean.ps1`](build_lean.ps1)** | [`build.ps1`](build.ps1) now falls back to `PATH`, rejects any `Axioms:` output, and enforces `closedCount == 22`. [`build_lean.ps1`](build_lean.ps1) runs inside `lean4/` (respecting `lean-toolchain`) and checks all `14` `#print axioms` blocks against the strict allowlist `@("propext", "Quot.sound")`. |
| **8** | [`solver/c5_gpu_Search.cu`](solver/c5_gpu_search.cu) and [`solver/gpu_solver.py`](solver/gpu_solver.py) used `n_moves = 10 + (i % 20)` and `col = (i * 7 + m * 11) % 8` (period `lcm(20, 8) = 40`, yielding `38` distinct boards) and hardcoded `h_mover[i] = 0`. | **Fixed in [`solver/c5_gpu_search.cu`](solver/c5_gpu_search.cu) & [`solver/gpu_solver.py`](solver/gpu_solver.py)** | Replaced the periodic generator with a **64-bit SplitMix64 per-thread PRNG** generating legal non-terminal games (`10..40` plies) and exact mover parity (`actual_moves & 1`). Verified on RTX 4060: **262,094 / 262,144 distinct boards (`99.98%`)**, **`0` wrong-mover errors**, and **2,922.01 Million tactical evaluations/sec** (`sm_89` native CUBIN). |
| **9** | [`solver/c5_gpu_search.cu`](solver/c5_gpu_search.cu) is a 1-ply/2-ply bitboard tactical threat & blunder evaluator, whereas [`solver/pdfpn.c`](solver/pdfpn.c) is a full AND/OR `df-pn` pairing solver; [`solver/c5_gpu_check.cu`](solver/c5_gpu_check.cu) tested only 1 vertical win line. | **Fixed in [`solver/c5_gpu_check.cu`](solver/c5_gpu_check.cu) & [`README.md`](README.md)** | Upgraded [`solver/c5_gpu_check.cu`](solver/c5_gpu_check.cu) to exhaustively verify **all 76 winning lines**, **all 380 4-stone near-misses**, and **100,000 random bitboards** (`0` mismatches). Updated [`README.md`](README.md) to explicitly distinguish **GPU Bitboard Tactical Playout Evaluation** from **CPU Parallel `df-pn` Pairing Search**. |
| **10** | [`solver/search.c`](solver/search.c) and [`solver/dfpn.c`](solver/dfpn.c) referenced removed `leaf(&p)`, `r1calls`, `r2calls`, and `visit_count`; [`solver/pdfpn.c`](solver/pdfpn.c) and [`solver/pdfpn_fast.c`](solver/pdfpn_fast.c) had unsynchronized multi-threaded reads/writes of `STOP`, `nodes`, and `leafcalls`. | **Fixed in [`solver/rules.h`](solver/rules.h), [`solver/search.c`](solver/search.c), [`solver/pdfpn.c`](solver/pdfpn.c), [`solver/pdfpn_fast.c`](solver/pdfpn_fast.c)** | Restored backward-compatible `leaf(const Pos *p)` and atomic `r1calls`/`r2calls` in [`solver/rules.h`](solver/rules.h); converted `STOP`, `nodes`, and `leafcalls` to GCC/C11 `__atomic` builtins (`__atomic_load_n`, `__atomic_store_n`, `__atomic_fetch_add`). All 4 C solvers compile cleanly with `gcc -O3 -Wall -Wextra`. |
| **11** | Audit script `audit/reproduce_findings.cjs` reproduced the periodic generator (`38` unique boards) and Ply-1 `s_frozen = None` check. | **Verified & Superseded** | Running [`build.ps1`](build.ps1), [`build_lean.ps1`](build_lean.ps1), and `python solver/gpu_solver.py` now programmatically verifies all `22` Rocq theorems, all `14` Lean 4 theorems, all `76` GPU winning lines, and `99.98%` unique SplitMix64 GPU boards with `0` errors. |

---

## 2. Detailed Technical Analysis of Proof Scope & The 4 New Concrete `Static` / `safe` Theorems

### 2.1 Why Ply 1 (`b_open`) Has `check_cover = true` While Midgame Leaves Have `check_static = true`

A subtle and important game-theoretic distinction highlighted by the audit is the difference between:
1. **`check_cover d b st = true` (Static Combinatorial Line Coverage):** Every one of the 76 winning 5-in-a-row lines on the `8 × 7` board is blocked by either an existing stone of `d` on `b` or a paired/threatening cell of `st` owned by `d`.
2. **`check_static d b st = true` (Full Dynamic Follow-Up Invariant `Static d b st`):** In addition to `check_cover d b st = true`, every empty cell outside the frozen column `s_frozen` must belong to a disjoint 2-cell pair (`s_strong`, `s_rigid`, or `s_weak`) so that the defender has an immediate 1-to-1 reply to *every* attacker move without ever running out of paired responses.

At **Ply 1** (`b_open = play initial 3 White`), there are `56 - 1 = 55` empty cells (`parity_trap_ply1`).
- Because `55` is **odd**, no partition into disjoint 2-cell pairs can cover all 55 cells without leaving at least 1 cell unpaired (`(4, 6)` in `white_27pair_struct`).
- Even though every winning line passing through `(4, 6)` is **double-blocked** (`dead_cell_4_6_six_lines_double_blocked`), an unassigned cell cannot simply be ignored in an unfrozen `Static` structure (`s_frozen = None`): if the game reached a state where Column 4 was filled up to row 5 (`height = 6`), the attacker could play `(4, 6)` as a **tempo-burning ("pass") move**, forcing the defender to move first in the remaining even-sized pairing partition!
- Furthermore, at Ply 1, White has only **1 stone** on the board (`(3, 0)`), so White cannot yet hold a 4-stone frozen threat (`s_frozen = Some (fc, ft)` requires 4 White stones already placed on a 5-line through `(fc, ft)`).

Therefore, in Victor Allis's strategic framework (`C5Rules.v` and `solver/rules.h`), `check_static = true` is triggered at **midgame leaves** where either:
- **Rule R3 (`s_frozen = Some (fc, ft)` at odd empty count `E`):** White has accumulated 4 stones of a 5-in-a-row threat at an odd row `ft ∈ {1, 3, 5}` above an empty even poison cell `(fc, ft - 1)`, freezing the odd-length column suffix `(fc, ft - 1)..(fc, 6)` and leaving an **even** number of empty cells in `freezone b st` (`r3_frozen_column_restores_even_parity`), OR
- **Rule R2 (`s_frozen = None` at even empty count `E`):** The remaining `E` empty cells are partitioned into `E / 2` disjoint pairs covering all 76 lines.

### 2.2 New Machine-Checked Concrete End-to-End Theorems (`Theorems 19–22` in [`C5CertChecker.v`](C5CertChecker.v#L681-L820))

To demonstrate that `check_static`, `check_cert_node`, `Static`, and `safe` are **non-vacuously inhabited on concrete 8×7 boards** and yield **unconditional game-tree safety (`safe d b s`)**, we added two complete midgame constructions and four machine-checked theorems in [`C5CertChecker.v`](C5CertChecker.v#L681-L820):

1. **Concrete Rule-R3 First-Player Defense (`b_ply8`, `b_r3`, `white_r3_full_struct`, `r3_two_step_cert`):**
   - `b_ply8` (8 plies played, `White` to move) steps via `CS_DefMove 3 1` (playing in Column 3 to reach `b_r3` with `47` empty cells and `Black` to move) into leaf `CS_Leaf white_r3_full_struct`.
   - On `b_r3`, White holds stones at `(0, 1), (1, 1), (2, 1), (3, 1)`, creating a genuine 4-in-a-row horizontal threat at `(4, 1)` (`s_frozen = Some (4, 1)` above empty poison cell `(4, 0)`).
   - The `7` cells `(4, 0)..(4, 6)` of Column 4 are frozen by Rule R3, and the remaining `47 - 7 = 40` empty cells are partitioned into **20 disjoint vertical strong dominoes** (`white_r3_strong`).
   - **[`r3_concrete_check_static_true`](C5CertChecker.v#L748) (Theorem 19):** Proves `empties b_r3 = 47 /\ check_static White b_r3 white_r3_full_struct = true /\ check_cert_node r3_two_step_cert 2 White b_ply8 White 0 = true` via `vm_compute`.
   - **[`r3_concrete_Static`](C5CertChecker.v#L755) (Theorem 20):** Applies `check_static_sound` to derive the full 13-clause inductive invariant `Static White b_r3 white_r3_full_struct`.
   - **[`r3_concrete_cert_safe`](C5CertChecker.v#L763) (Theorem 21):** Applies `structure_sound` and `cert_sound` to prove **unconditional game-tree safety** `safe White b_r3 Black /\ safe White b_ply8 White` across all `8^47` legal game continuations!

2. **Concrete Rule-R2 Second-Player Defense (`b_r2`, `black_r2_full_struct`):**
   - `b_r2` is a concrete 20-ply position (`36` empty cells, `White` to move) where `Black` defends using pure Rule R2 (`s_frozen = None`), combining **14 vertical strong dominoes** with **two 4-high horizontal rigid chains** across Columns `1–2` and `5–6` (`rows 3..6`).
   - **[`r2_concrete_black_static_safe`](C5CertChecker.v#L812) (Theorem 22):** Proves `empties b_r2 = 36 /\ check_static Black b_r2 black_r2_full_struct = true /\ Static Black b_r2 black_r2_full_struct /\ safe Black b_r2 White`.

---

## 3. Complete Inventory of Unconditional vs. Conditional Theorems

For absolute transparency, the table below classifies all **22 Rocq 9.1 theorems** ([`CheckAssumptions.v`](CheckAssumptions.v)) and **14 Lean 4.35.0 theorems** ([`lean4/Connect5HandProof.lean`](lean4/Connect5HandProof.lean)):

| Category | Prover | Theorem Count | Theorems | Nature of Statement |
| :--- | :---: | :---: | :--- | :--- |
| **Deductive Pairing & Reflection Soundness** | Rocq 9.1 | **5** | `structure_sound`, `strategy_sound`, `mutual_safety_draw`, `check_static_sound`, `cert_sound` | **Unconditional universal theorems** (`Closed under the global context`) proving that *any* valid pairing structure or strategy DAG guarantees game-tree `safe` and `Draw`. |
| **Concrete Midgame `check_static = true` & Unconditional `safe`** | Rocq 9.1 | **4** | `r3_concrete_check_static_true`, `r3_concrete_Static`, `r3_concrete_cert_safe`, `r2_concrete_black_static_safe` | **Unconditional concrete theorems** establishing `check_static = true`, `check_cert_node = true`, `Static`, and `safe` on explicit `8 × 7` boards (`47` and `36` empty cells). |
| **76-Line Coverage, Parity Trap, Dead Cell & Central Wall Book Proof** | Rocq 9.1 | **11** | `parity_trap_ply1`, `opening_27pair_line_cover`, `core10_covers_all_76_lines`, `dead_cell_4_6_six_lines_double_blocked`, `r3_frozen_column_restores_even_parity`, `book_step1`..`book_step5`, `book_central_wall_decomposition` | **Unconditional theorems** (`vm_compute` + Presburger `lia`) proving all combinatorial, geometric, and parity laws on the `8 × 7` board. |
| **Analytic Affine-Line & Modular Parity Hand Proof** | Lean 4.35.0 | **14** | All 14 theorems in [`lean4/Connect5HandProof.lean`](lean4/Connect5HandProof.lean) | **Unconditional constructive theorems** (`0` `sorry`s, `0` custom axioms, `0` `Classical.choice`). |
| **Root Game-Value Reductions from Opening Certificates** | Rocq 9.1 | **2** | `connect5_8x7_fair`, `cert_fair` | **Conditional reduction theorems** proving that *given* root strategy certificates for White (after `c0`) and Black (from `initial`), `game_value = Draw`. |

---

## 4. Verification of GPU Bitboard Win Detector, SplitMix64 Generator & C11 Solvers

### 4.1 Exhaustive GPU Win-Detector Check ([`solver/c5_gpu_check.cu`](solver/c5_gpu_check.cu))
We replaced the single-line sanity check in [`solver/c5_gpu_check.cu`](solver/c5_gpu_check.cu) with a comprehensive GPU verification suite testing `check_win_5` against an explicit host reference implementation of all 76 winning 5-in-a-row lines:
- **Test 1:** All **76 exact 5-in-a-row winning lines** (`24` vertical, `28` horizontal, `12` diagonal `/`, `12` diagonal `\`) -> `76/76` detected (`0` false negatives).
- **Test 2:** All **`76 × 5 = 380` 4-stone near-miss subsets** -> `380/380` rejected (`0` false positives).
- **Test 3:** **100,000 random bitboard configurations** (`6..28` stones, verifying sentinel-bit isolation across columns) -> `100,000/100,000` exact agreement (`0` mismatches).

### 4.2 SplitMix64 Legal Non-Terminal Rollout Generator ([`solver/c5_gpu_search.cu`](solver/c5_gpu_search.cu) & [`solver/gpu_solver.py`](solver/gpu_solver.py))
We replaced the deterministic modulo loop (`10 + (i % 20)` moves with `(i * 7 + m * 11) % 8` columns) with a per-thread **64-bit SplitMix64 PRNG** (`generate_boards_kernel`) that plays `10..40` legal non-terminal moves on the GPU (rolling back any move that would immediately create a 5-in-a-row so every benchmarked position is an active midgame state) and sets `d_mover[idx] = actual_moves & 1`.

Running `python solver/gpu_solver.py` on the NVIDIA GeForce RTX 4060 Laptop GPU (`sm_89` native CUBIN via CUDA 13.5 NVRTC) outputs:
```text
Device: NVIDIA GeForce RTX 4060 Laptop GPU | Driver: 13020 | Arch: sm_89
[1/3] GPU Win-Detector Verification (76 lines, 380 near-misses, 100,000 random bitboards): errors = 0
[2/3] SplitMix64 Legal Board Audit (262,144 sample): 262,094 distinct (99.98%), wrong_mover = 0
[3/3] RTX 4060 Tactical Playout Benchmark (4,194,304 boards x 25 iters = 104,857,600 evals): 35.89 ms (2,922.01 MILLION tactical board evaluations / second)
```
*(In standalone `nvcc` host-allocated execution with 64-bit SplitMix64 rollouts, [`solver/c5_gpu_search.cu`](solver/c5_gpu_search.cu) evaluates `104,857,600` positions across `4,194,304` legal boards with `99.98%` uniqueness and `0` mover errors).*

### 4.3 C11 Atomic Synchronization & Clean Compilation Across All 4 CPU Solvers
All four C solver binaries now compile with **zero errors and zero warnings** under `gcc -O3 -Wall -Wextra -pthread`:
```powershell
gcc -O3 -Wall -Wextra solver/search.c     -o solver/search_test.exe
gcc -O3 -Wall -Wextra solver/dfpn.c       -o solver/dfpn_test.exe
gcc -O3 -Wall -Wextra -pthread solver/pdfpn.c      -o solver/pdfpn_test.exe
gcc -O3 -Wall -Wextra -pthread solver/pdfpn_fast.c -o solver/pdfpn_fast_test.exe
```
All cross-thread accesses to `STOP`, `t->nodes`, `t->leafcalls`, `r1calls`, `r2calls`, and `r3calls` use lock-free C11/GCC atomic operations (`__atomic_load_n`, `__atomic_store_n`, `__atomic_fetch_add`).
