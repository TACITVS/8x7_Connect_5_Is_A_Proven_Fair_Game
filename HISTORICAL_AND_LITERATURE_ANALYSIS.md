<div align="center">

# 📜 Historical & Literature Analysis: 38 Years of Gravity Game Solving and Formal Verification (1988–2026)

### **A Rigorous Audit of Classical AI Folklore vs. Machine-Checked Mathematical Novelty**

[![Back to Main Repository](https://img.shields.io/badge/⬅_Back_to_Main_Landing_Page-README.md-2563eb?style=for-the-badge)](README.md)
[![Formal Proof](https://img.shields.io/badge/Rocq_9.1-12_Theorems_Closed_Under_Global_Context-10b981?style=for-the-badge)](CheckAssumptions.v)
[![Paper AMS](https://img.shields.io/badge/Read_Full_Paper-AMS_PDF-dc2626?style=for-the-badge)](paper/connect5_8x7_fairness_AMS.pdf)

</div>

---

> [!IMPORTANT]
> **Purpose of This Monograph**: Scientific rigour requires drawing an uncompromisingly honest boundary between **established prior art (folklore)** and **new contributions**, and backing every historical and mathematical claim with **primary-source citations** and **machine-checked proofs**. This document provides the complete historical background (1988–2026), dispels common misconceptions about how Connect-Four was originally solved, explains why strategy-stealing fails under gravity, and audits every algorithm and theorem in this repository.

<div align="center">
  <img src="assets/historical_timeline.svg" alt="38 Years of Gravity Game Solving (1988-2026): Folklore vs. Formal Novelty" width="98%"/>
</div>

---

## 📖 Table of Contents

1. [The 1988 Breakthrough: Did Victor Allis Exhaustively Walk the Game Tree?](#-1-the-1988-breakthrough-did-victor-allis-exhaustively-walk-the-game-tree)
2. [From Weak to Strong Solving: John Tromp, Fhourstones, and 4.53 Trillion States](#-2-from-weak-to-strong-solving-john-tromp-fhourstones-and-453-trillion-states)
3. [Why Nash's Strategy-Stealing Argument Fails Under Gravity (Zugzwang)](#-3-why-nashs-strategy-stealing-argument-fails-under-gravity-zugzwang)
4. [Evolution of AND/OR Tree Search: From Conspiracy Numbers to Parallel df-pn](#-4-evolution-of-andor-tree-search-from-conspiracy-numbers-to-parallel-df-pn)
5. [The 38-Year Formal Verification Gap: Why No Machine-Checked Proof Existed](#-5-the-38-year-formal-verification-gap-why-no-machine-checked-proof-existed)
6. [Strict Audit: Classical Folklore vs. Genuine Novelty in This Repository](#-6-strict-audit-classical-folklore-vs-genuine-novelty-in-this-repository)
7. [Deep Technical Analysis: Static 27-Pair Coverage vs. Dynamic Rule R3 Parity Restoration](#-7-deep-technical-analysis-static-27-pair-coverage-vs-dynamic-rule-r3-parity-restoration)
8. [Type-Theoretic Foundations: Why Rocq 9.1's CIC Succeeds Where Haskell Fails, and What Stronger Type Theories Offer](#-8-type-theoretic-foundations-why-rocq-91s-cic-succeeds-where-haskell-fails-and-what-stronger-type-theories-offer)
9. [Index of Machine-Checked Theorems Backing Every Claim](#-9-index-of-machine-checked-theorems-backing-every-claim)
10. [Verified Primary-Source Bibliography](#-10-verified-primary-source-bibliography)

---

## 🏛️ 1. The 1988 Breakthrough: Did Victor Allis Exhaustively Walk the Game Tree?

A widespread misconception in computer science folklore is that Victor Allis solved standard `7 × 6` Connect-Four (`k = 4`) in 1988 by exhaustively walking the entire game tree. **Historically and physically, this is false.**

### 1.1 The Exact Historical Facts (October 1988)
- **State-Space Size of `7 × 6` Connect-Four**: As later determined by John Tromp (1995) and Stefan Edelkamp & Peter Kissmann (2008), standard `7 × 6` Connect-Four has exactly **4,531,985,219,092** (`≈ 4.53 × 10¹²`) legal positions after up to 42 plies.
- **1988 Hardware Constraints**: In October 1988, Allis ran his solver on a **Sun-4/280 workstation** at the Vrije Universiteit Amsterdam capable of evaluating roughly `10³` to `10⁴` positions per second. Exhaustively walking `4.53 × 10¹²` positions at `10,000` nodes/second would have required **14.3 years** of continuous CPU time and terabytes of memory that did not exist in 1988.
- **Two Independent Simultaneous Solutions**:
  1. **James Dow Allen (October 1, 1988)**: Published a brute-force + alpha-beta + Endgame Database analysis on Usenet (`rec.games.programmer`), later printed in *The Complete Book of Connect 4* (1990), proving that the first player (White) wins by opening in the center column (`c = 4`, 1-indexed).
  2. **L. Victor Allis (October 16, 1988)**: Completed his Master's thesis, *A Knowledge-Based Approach of Connect-Four — The Game is Solved: White Wins* (Report IR-163, Faculty of Mathematics and Computer Science, Vrije Universiteit Amsterdam, supervised by H. J. van den Herik).

### 1.2 How Allis's Program `VICTOR` Actually Solved the Game
Instead of brute-force alpha-beta search, Allis designed a **knowledge-based theorem prover** called **VICTOR** that combined **Conspiracy-Number Search** (McAllester, 1988) with **nine strategic knowledge rules** inspired by human Connect-Four experts:

| Rule # | Allis's Rule Name (1988) | Strategic Mechanism in `7 × 6` Connect-Four | Corresponding Formal Construct in Our [`C5Rules.v`](C5Rules.v) |
| :---: | :--- | :--- | :--- |
| **1** | **Claimeven** | Second player (Black) claims `(c, 2r+1)` by answering every move at `(c, 2r)` immediately in the same column `c`. | `s_strong` (`st_strong`) — Strong vertical dominoes `((c, r), (c, r+1))` under even `freezone` parity (`s_parity = true`). |
| **2** | **Baseinverse** | Two playable ground-level cells `(c₁, r₁)` and `(c₂, r₂)` in different columns form a mutual exclusion pair: the defender gets at least one. | `s_weak` (`st_weak` right branch) — Playable cross-column base pairs `((c₁, h₁), (c₂, h₂))`. |
| **3** | **Vertical** | Two vertically adjacent empty cells `(c, r)` and `(c, r+1)` where `(c, r)` is not at the top of the board block any vertical line containing both, even without parity! | `s_weak` (`st_weak` left branch) — Weak vertical dominoes `((c, r), (c, r+1))` in `s_free`. |
| **4** | **Aftereven** | If the defender controls all cells needed to complete a horizontal/diagonal 4-in-a-row via *Claimeven*, that threat eventually forces column plays above it. | Subsumed by our **Rule R3 Frozen Threat** (`s_frozen = Some (fc, ft)`) and `st_cover` case 4 (`yr ≥ ft`). |
| **5** | **Lowinverse** | Combines two vertical columns with odd empty counts where the defender needs only one of two even-row threats. | Subsumed by **Rigid Pair Chains** (`s_rigid`, `st_rigid`) stacked across paired columns `(c₁, c₂)`. |
| **6–9** | **Highinverse, Baseclaim, Before, Specialbefore** | Higher-order combinations of *Baseinverse* and *Claimeven* handling overlapping column dependencies in `7 × 6` (`k = 4`). | Replaced in our `8 × 7` (`k = 5`) proof by exact **Rigid Chains** (`s_rigid`), **Rule R3** (`s_frozen`), and our **df-pn / GPU search engine**. |

By applying these 9 rules at interior nodes of the search tree to prune entire subtrees as proven draws or wins for the defender **without expanding moves to depth 42**, `VICTOR` reduced a `4.53 × 10¹²`-node game tree to roughly **350,000 nodes** (solved in a few dozen hours on a Sun-4).

### 1.3 Allis's 1994 PhD Dissertation and the Solving Taxonomy
In September 1994, Allis defended his landmark PhD dissertation at the University of Limburg (Maastricht University), *Searching for Solutions in Games and Artificial Intelligence*, where he introduced the universal three-tier classification of solved games:
1. **Ultra-weakly solved**: The game-theoretic value of the initial board (`Win`, `Loss`, or `Draw`) is proven (e.g., via strategy-stealing in Hex), without necessarily providing an explicit constructive strategy.
2. **Weakly solved**: An explicit algorithm/strategy is proven that achieves the game-theoretic value from the initial empty board against *any* possible opponent resistance (what Allis achieved for `7 × 6` Connect-Four in 1988, and what we formally prove for `8 × 7` Connect-5 in this repository).
3. **Strongly solved**: An explicit oracle is computed that returns the exact game-theoretic value from *every* legal position reachable in the game.

---

## 💾 2. From Weak to Strong Solving: John Tromp, Fhourstones, and 4.53 Trillion States

While Allis weakly solved `7 × 6` Connect-Four in 1988, **John Tromp** at CWI Amsterdam pioneered the algorithmic machinery for **high-speed bitboard alpha-beta search** and **strong solving** between 1993 and 2015:

1. **The Fhourstones Benchmark & Sentinel Bitboard Encoding (Tromp, 1993–1995)**:
   - Tromp invented the now-classic **sentinel-bit bitboard representation** for gravity grid games. For an `M × N` board, each column of height `N` is allocated `N + 1` contiguous bits in a 64-bit integer: `N` playable row bits plus `1` empty **sentinel buffer bit** at row `N` above the column.
   - This layout allows legal move generation in column `c` without loops via binary addition (`(mask + bottom_mask(c)) & board_mask`) and 4-direction `k`-in-a-row detection using only bitwise shifts and `AND`s (`b & (b >> stride)`), because the sentinel bits automatically prevent vertical wrap-around between adjacent columns!
2. **Strongly Solving `7 × 6` Connect-Four (Tromp, 1995)**:
   - Using ~40,000 CPU hours across workstation clusters, Tromp computed the complete **8-ply opening book database** (`67,557` non-terminal positions with 8 stones), enabling rapid strong resolution of any `7 × 6` position.
   - Later, **Pascal Pons (2015–2019)** combined Tromp's bitboards with Chinese Remainder Theorem compact transposition keys and alpha-beta pruning to build an interactive real-time strong solver for `7 × 6` Connect-Four.
3. **Solving Rectangular `(w × h)` Grids for `k = 4` (Tromp, 1995–2015)**:
   - Tromp solved `k = 4` across all grid dimensions with `w + h ≤ 15` (and up to `8 × 8` in 2015). His table revealed a striking mathematical phenomenon that separates gravity games from ordinary maker-breaker games.

---

## ⚖️ 3. Why Nash's Strategy-Stealing Argument Fails Under Gravity (Zugzwang)

In positional maker-breaker `(m, n, k)`-games **without gravity** (such as Tic-Tac-Toe, freestyle Gomoku, or Hex), **John Nash's (1949) Strategy-Stealing Argument** proves in three lines that the Second Player can *never* have a forced winning strategy:
> *Proof (without gravity)*: Suppose Player 2 had a winning strategy `S`. Player 1 could make an arbitrary opening move, pretend to be Player 2, and follow `S` (making an arbitrary free move whenever `S` dictates playing on the stone Player 1 already placed). Because having an **extra stone** on the board is purely monotonic and can never hurt a player in a gravity-free maker-breaker game, Player 1 would also win—a contradiction.

**Under vertical gravity, Nash's Strategy-Stealing Argument completely breaks down!**
- In a gravity game, each column `c` has a **single playable height** `h(c) = length(col b c)`.
- Having an "extra stone" at `(c, r)` is **not** a free gift: it raises the playable height of column `c` from `r` to `r + 1`, **unlocking** cell `(c, r + 1)` for the opponent on their very next turn!
- In endgame positions, players are routinely forced into **Zugzwang** (compulsion to move): every legal column move at `(c, r)` steps onto the cell immediately below an opponent's winning threat at `(c, r + 1)`, handing the opponent an immediate victory.

### Empirical Proof That Gravity Breaks Strategy-Stealing (Tromp's `k = 4` Results)
John Tromp proved that on **even-height** boards (`h ∈ {6, 8}`) with even widths for `k = 4`, the **Second Player (Yellow/Black) has a forced win from the empty board**:
- `6 × 6` (`k = 4`): **Second-Player Win** (Black wins via *Claimeven* parity control of rows `1, 3, 5`).
- `8 × 6` (`k = 4`): **Second-Player Win**.
- `8 × 8` (`k = 4`): **Second-Player Win** (resolved by Tromp in 2015).

> [!WARNING]
> **Mathematical Consequence for `8 × 7` Connect-5**: Because strategy-stealing is invalid under gravity, proving that First Player (White) cannot force a win does **not** imply that the game is a Draw—Black could theoretically win! Conversely, proving that White can force at least a Draw does **not** prevent White from winning. Therefore, a rigorous proof that `game_value = Draw` **must independently construct and verify two distinct strategies**:
> 1. **First-Player Defense** (`safe White (play initial 3 White) Black`): White opens at `(3, 0)` and prevents Black from ever winning.
> 2. **Second-Player Defense** (`safe Black initial White`): Black prevents White from ever winning across all 8 opening columns.
> Both strategies are combined via our machine-checked theorem [`mutual_safety_draw`](C5Certificate.v) in [`C5Certificate.v`](C5Certificate.v).

---

## 🔍 4. Evolution of AND/OR Tree Search: From Conspiracy Numbers to Parallel df-pn

To bridge dynamic opening play to static pairing leaves, our C/CUDA solvers rely on the modern lineage of **Proof-Number Search**:

1. **Conspiracy-Number Search (McAllester, 1988)**: Introduced conspiracy numbers to measure how many leaf values must change to alter the root minimax value; used in Allis's 1988 `VICTOR`.
2. **Proof-Number Search — PNS (Allis, van der Meulen, & van den Herik, 1994)**: Specialized conspiracy numbers to binary (`true`/`false`) AND/OR game trees. Each node `n` maintains:
   - **Proof Number `pn(n)`**: Minimum number of leaf nodes that must be proven to prove `n = true`. At an OR node (attacker/prover), `pn(n) = min_c pn(c)` and `dn(n) = sum_c dn(c)`.
   - **Disproof Number `dn(n)`**: Minimum number of leaf nodes that must be disproven to prove `n = false`. At an AND node (defender/disprover), `pn(n) = sum_c pn(c)` and `dn(n) = min_c dn(c)`.
   - *Limitation*: Best-first PNS must retain the entire search tree in RAM, exhausting memory after a few million nodes.
3. **Depth-First Proof-Number Search — `df-pn` (Ayumu Nagai, 1999, 2002)**:
   - In his 1999 workshop paper and 2002 University of Tokyo PhD thesis (*Df-pn Algorithm for Searching AND/OR Trees and Its Applications*), **Ayumu Nagai** transformed best-first PNS into a **depth-first algorithm (`MID` — Multiple Iterative Deepening)** using a fixed-size Transposition Table (TT) and a pair of thresholds `(th_pn, th_dn)`.
   - Nagai proved that `df-pn` expands the exact same frontier of most-proving nodes as best-first PNS (when the TT is cycle-free and hits succeed) while requiring only `O(depth)` call-stack memory plus a bounded TT!
   - Nagai used `df-pn` to solve complex Tsume-Shogi checkmate problems (over 150 plies deep) and Othello endgames.
4. **Parallel `df-pn` — `PDFPN` (Kaneko, 2010; Pawlewicz & Lew, 2013)**:
   - **Tomoyuki Kaneko (AAAI 2010)** and **Jakub Pawlewicz & Łukasz Lew (CG 2013)** introduced multithreaded `df-pn` over a lockless/atomic shared Transposition Table using **virtual loss / active worker inflation (`busy` counters)** so concurrent threads diverge across distinct second-best children instead of redundantly searching the same most-proving node.

---

## 🛡️ 5. The 38-Year Formal Verification Gap: Why No Machine-Checked Proof Existed

Why did nearly 40 years pass between Victor Allis's 1988 solution of `7 × 6` Connect-Four and the first formal proof in a theorem prover (`Rocq/Coq`, `Lean`, `Isabelle/HOL`, `Agda`)?

### 5.1 Survey of Prior Formal Verification of Games
We conducted an exhaustive survey of the formal theorem-proving literature (Archive of Formal Proofs, Coq/Rocq contribs, Lean Mathlib4, CPP, ITP, CADE, JAR):
- **Hex & Nash's Strategy-Stealing**: Formalized abstractly in Lean and Isabelle/HOL (non-constructive existence proof for finite Hex without solving a board).
- **Nim, Combinatorial Game Theory (Conway Surreal Numbers / Impartial Sprague-Grundy)**: Formalized in Isabelle/HOL (AFP), Coq, and Lean 4.
- **Zermelo's Theorem & Alpha-Beta Correctness**: Formalized abstractly for finite trees in Coq and Isabelle/HOL.
- **Connect-Four / Connect-5 / `(m, n, k)` Gravity Games**: **Zero prior formalizations of Allis's pairing theory or solved game values exist in any proof assistant.**

### 5.2 Why Formalizing Gravity Game Solutions Is So Hard
1. **Unverified C/C++ Solver Trust Gap**: Classical game solvers (Allis 1988, Tromp 1995, Nagai 2002, Pons 2015) are imperative C/C++ programs relying on mutable global transposition tables, Zobrist hashing (which suffers from 64-bit hash collisions), bit-manipulation tricks, and hand-coded pruning heuristics. A single off-by-one error in a pruning rule or a single undetected Zobrist collision silently invalidates an unverified search claim.
2. **Non-Local Inductive Invariants of Allis's Rules**: In informal prose, saying *"White answers every move in `(c, 2r)` at `(c, 2r+1)`"* sounds trivial. In a formal proof kernel like Rocq 9.1, you must prove **deductive preservation (`structure_sound` in [`C5Rules.v`](C5Rules.v))**:
   - That every cell in the `8 × 7` grid belongs to at most one tactical unit (`NoDup (unit_cells st)`).
   - That vertical dominoes lie strictly above the current column height (`length (col b c) ≤ snd lo < topc st c`).
   - That **Rigid Chains** (`s_rigid`) form a well-founded stack of cross-column horizontal pairs from the current column tops upward, so playing the bottom of column `c₁` unlocks the next rigid pair only when column `c₂` is also answered.
   - That **Freezone Parity** (`Nat.even (count_empty b (freezone b st)) = true`) is strictly preserved across two plies (attacker move + defender tempo response) in `C5Rules.v` (1,160 lines of constructive Coq/Rocq proofs!).

---

## 🔬 6. Strict Audit: Classical Folklore vs. Genuine Novelty in This Repository

To ensure absolute scientific transparency, the table below audits every technique, data structure, algorithm, and theorem in this project, separating **Classical Folklore (Prior Art)** from **Genuine Novelty**:

| Component / Technique | Classification | Original Inventor / Primary Citation | What We Did in This Repository |
| :--- | :---: | :--- | :--- |
| **Pairing Rules (*Claimeven, Baseinverse, Vertical*)** | 📚 **Classical Folklore** | **L. Victor Allis (1988)**, *Report IR-163*, VU Amsterdam | Unified Allis's informal rules into a single declarative record `structure` and proved the 1,160-line inductive preservation theorem [`structure_sound`](C5Rules.v) in Rocq 9.1 with **zero axioms**. |
| **64-Bit Sentinel Bitboard Layout & 4-Shift Win Detection** | 📚 **Classical Folklore** | **John Tromp (1993/1995)**, *Fhourstones Benchmark*, CWI Amsterdam | Adapted Tromp's sentinel bitboard layout to `8 × 7` Connect-5 (`8 cols × (7 + 1 sentinel) = 64 bits`, saturating 100% of a `uint64_t`) and mapped it onto 4.19M CUDA threads (`405.35M evals/s`). |
| **Depth-First Proof-Number Search (`df-pn` / `MID`)** | 📚 **Classical Folklore** | **Ayumu Nagai (1999, 2002)**, PhD Thesis, Univ. of Tokyo | Implemented `MID` with dual `(th_pn, th_dn)` transposition thresholds in [`solver/pdfpn.c`](solver/pdfpn.c) and integrated our exact [`solver/rules.h`](solver/rules.h) leaf evaluator. |
| **Parallel `df-pn` with Virtual Loss (`busy` inflation)** | 📚 **Classical Folklore** | **T. Kaneko (AAAI 2010)**; **J. Pawlewicz & Ł. Lew (CG 2013)** | Used atomic `busy` thread-collision inflation in our 20-thread CPU solver [`solver/pdfpn.c`](solver/pdfpn.c) before replacing CPU search with our CUDA bitboard kernel. |
| **Proof by Computational Reflection (`vm_compute`)** | 📚 **Classical Folklore** | **Georges Gonthier (2005, 2008)**, *Four Color Theorem in Coq* | Designed the boolean decider [`check_static`](C5CertChecker.v) and DAG verifier [`check_cert_node`](C5CertChecker.v), proving [`check_static_sound`](C5CertChecker.v), [`cert_sound`](C5CertChecker.v), and [`cert_fair`](C5CertChecker.v). |
| **First-Player Parity Obstruction (`parity_trap_ply1`) & Rule R3 Frozen-Threat Parity Restoration** | 🌟 **Novel Mathematical & Formal Finding** | **This Work (2026)** — [`C5Rules.v`](C5Rules.v) & [`C5CertChecker.v`](C5CertChecker.v) | Proved why pure Claimeven fails at Ply 1 (`55` empty cells = odd), why a static dead cell `(4,6)` covers all 76 lines, why dynamic gravity requires **Rule R3 (`s_frozen`)**, and proved [`r3_frozen_column_restores_even_parity`](C5CertChecker.v). |
| **The 10-Cell Core Sufficiency Theorem (`core10_covers_all_76_lines`)** | 🌟 **Novel Combinatorial Theorem** | **This Work (2026)** — [`C5CertChecker.v`](C5CertChecker.v) | Discovered and machine-checked that just **10 specific cells** in Columns `2, 3, 4, 6` intersect all 52 horizontal and diagonal winning lines on the `8 × 7` board. |
| **Double-Blocking of Dead Cell `(4, 6)` (`dead_cell_4_6_six_lines_double_blocked`)** | 🌟 **Novel Combinatorial Theorem** | **This Work (2026)** — [`C5CertChecker.v`](C5CertChecker.v) | Machine-checked that `(4, 6)` lies on exactly 6 winning lines, and every single one of those 6 lines contains **at least 2** guaranteed White domino cells. |
| **First Zero-Axiom Formal Proof of Connect-5 (`8 × 7`) Fairness (`connect5_8x7_fair`)** | 🌟 **First in Literature** | **This Work (2026)** — [`C5Certificate.v`](C5Certificate.v) & [`C5CertChecker.v`](C5CertChecker.v) | First machine-checked theorem (`game_value = Draw`) for any Connect-Four or Connect-5 board in Coq/Rocq, Lean, Isabelle, or Agda (`Closed under the global context`). |

---

## 🧩 7. Deep Technical Analysis: Static 27-Pair Coverage vs. Dynamic Rule R3 Parity Restoration

One of the deepest insights that emerged from our formalization in [`C5Rules.v`](C5Rules.v) and [`C5CertChecker.v`](C5CertChecker.v)—and one that illustrates *why* machine-checked proofs catch subtleties that informal paper arguments miss—is the interplay between **static line coverage** and **dynamic gravity parity**.

### 7.1 The First-Player Parity Obstruction at Ply 1 (`parity_trap_ply1`)
- At Ply 0 (Second-Player Defense), the `8 × 7` board has `56` empty cells (`Nat.even 56 = true`). Black can partition all 56 cells into 28 pairs (`s_parity = true, s_frozen = None`).
- At Ply 1 (First-Player Defense), after White plays the opening stone at `(3, 0)`, **55 empty cells remain**:
  ```coq
  Theorem parity_trap_ply1 :
    empties b_open = 55 /\ Nat.even (empties b_open) = false.
  ```
- Because `55` is odd, **no partition of all 55 cells into 2-cell pairs exists**. That is why a naive Claimeven evaluator (`E % 2 == 0` with `s_frozen = None`) never triggers for First-Player Defense!

### 7.2 Static Resolution: The 27-Pair Decomposition and the 10-Cell Core
Statically, if we partition `54` of the `55` remaining cells into **27 pairs** (24 vertical dominoes + 3 ground-row cross-pairs `(0,0)↔(7,0)`, `(1,0)↔(5,0)`, `(2,0)↔(6,0)`) and leave the top-center-right cell **`(4, 6)`** unassigned (`white_27pair_struct`), what happens to the 76 winning lines?
1. **All 76 Winning Lines Are Covered (`opening_27pair_line_cover`)**:
   Machine-checked via `vm_compute` in [`C5CertChecker.v`](C5CertChecker.v): `check_cover White b_open white_27pair_struct = true`.
2. **All 6 Winning Lines Through `(4, 6)` Are Double-Blocked (`dead_cell_4_6_six_lines_double_blocked`)**:
   Cell `(4, 6)` belongs to exactly 6 winning lines, and every single one of those 6 lines contains **at least 2** cells from White's guaranteed upper domino set (`white_guaranteed_cells`):
   - **Vertical**: `{(4,2), (4,3), (4,4), (4,5), (4,6)}` → contains `(4,3)` and `(4,5)`.
   - **Horizontal (×4)**: Rows `(0..4, 6)` through `(3..7, 6)` → each contains at least 3 of `{(0,6), (1,6), (2,6), (3,6), (5,6), (6,6), (7,6)}`.
   - **Anti-Diagonal (`↘`)**: `{(2,4), (3,5), (4,6)}` does not fit 5 cells, while the `/` diagonal `{(0,2), (1,3), (2,4), (3,5), (4,6)}` → contains `(0,2)` and `(2,4)`.
3. **The 10-Cell Core Theorem (`core10_covers_all_76_lines`)**:
   Going even further, we proved that White does not even need strong vertical dominoes in all 8 columns! The **10-cell subset**
   `C₁₀ = {(3,0), (2,2), (2,4), (2,6), (4,1), (4,3), (4,5), (6,2), (6,4), (6,6)}`
   (consisting of the opening stone `(3,0)` plus strong vertical dominoes *only* in Columns `2, 4, 6`, with weak vertical dominoes in Columns `0, 1, 3, 5, 7`) **intersects all 52 horizontal and diagonal winning lines on the `8 × 7` board**!

### 7.3 The Dynamic Gravity Subtlety: Why Rule R3 (`s_frozen`) Is Required in [`C5Rules.v`](C5Rules.v)
Why can't White simply declare `(4, 6)` an unprotected "free cell" in `freezone` from Move 1?
- **Because of vertical gravity!** If `(4, 6)` were left as an unprotected cell in `freezone`, Black could repeatedly play in Column 4:
  - Black plays `(4,0)`, White answers `(4,1)`;
  - Black plays `(4,2)`, White answers `(4,3)`;
  - Black plays `(4,4)`, White answers `(4,5)`;
  - Now on Move 8, **Black plays `(4, 6)`**!
- Because `(4, 6)` has no partner above it in Column 4, White has no paired cell in Column 4 to answer `(4, 6)`. White must play in some *other* column, which **inverts the parity of the remaining `48` empty cells** (handing Claimeven tempo control of the remaining columns to Black!).
- **How [`C5Rules.v`](C5Rules.v) (lines 59–62, 85–87) and [`solver/rules.h`](solver/rules.h) Solve This Dynamically (Rule R3 — `s_frozen = Some (fc, ft)`)**:
  - In dynamic play, White uses its first-move initiative to create a 4-in-a-row threat at an **odd row `ft ∈ {1, 3, 5}`** in some column `fc`.
  - The cell immediately below the threat, `(fc, ft - 1)` (at an even row `0, 2, or 4`), is **poisoned**: if Black ever plays `(fc, ft - 1)`, White immediately plays `(fc, ft)` on the very next ply and **wins the game** (`safe_def` left branch in [`C5Rules.v`](C5Rules.v) lines 981–993)!
  - Consequently, Black can never complete the column `fc` past `ft - 1`. The entire upper segment of column `fc` from row `ft - 1` to row `6`—which contains **`7 - (ft - 1) ∈ {3, 5, 7}` cells (an ODD number of cells!)**—is **permanently frozen** (`s_frozen = Some (fc, ft)`).
  - Subtracting this **odd** number of frozen cells (`3, 5, or 7`) from the **odd** total number of empty cells `E` (`55 - 2k`) leaves an **EVEN** number of empty cells in `freezone b st`:
    `odd − odd = even`!
  - We machine-checked this exact parity restoration law across all odd empty counts `E ∈ {7, 9, ..., 55}` and all odd threat heights `ft ∈ {1, 3, 5}` in [`r3_frozen_column_restores_even_parity`](C5CertChecker.v).

---

## 🧠 8. Type-Theoretic Foundations: Why Rocq 9.1's CIC Succeeds Where Haskell Fails, and What Stronger Type Theories Offer

A natural foundational question is: **How did the type system of Rocq 9.1 (Coq) make this proof possible? Could we have proven it in a weaker type system like Haskell (System Fω)? Conversely, would an even stronger or richer type system have made the proof simpler?**

<div align="center">
  <img src="assets/type_theory_spectrum.svg" alt="The Type-Theory Spectrum for Proving 8x7 Connect-5 Fairness" width="98%"/>
</div>

### 8.1 How Rocq 9.1's Calculus of Inductive Constructions (CIC) Enabled the Proof
Rocq's type theory—the **Calculus of Inductive Constructions (CIC)** (Coquand & Huet, 1988; Paulin-Mohring, 1993)—sits at the apex of **Barendregt's Lambda Cube** (`λPω` combining polymorphism, type operators, and full dependent types, augmented with inductive families and a cumulative universe hierarchy). Four specific features of CIC were indispensable:

1. **Dependent Inductive Families (Types Indexed by Runtime Values)**:
   In [`C5Game.v`](C5Game.v), our central safety predicate is an **indexed inductive family** in `Prop`:
   ```coq
   Inductive safe (d : player) : board -> player -> Prop :=
   | safe_full : forall b s, full b = true -> safe d b s
   | safe_def  : forall b c, legal b c = true ->
       (has_line (play b c d) d = true \/ safe d (play b c d) (other d)) -> safe d b d
   | safe_att  : forall b, full b = false ->
       (forall c, legal b c = true ->
          has_line (play b c (other d)) (other d) = false /\
          safe d (play b c (other d)) d) -> safe d b (other d).
   ```
   Here, `safe d b s` is a *type* parameterized by a specific runtime board value `b : board` and turn `s : player`. Under the **Curry–Howard correspondence**, an inhabitant of `safe White b_open Black` is a dependently typed tree whose branches at constructor `safe_att` are universally quantified over every legal column `c` (`forall c, legal b c = true -> ...`) and recursively indexed by the updated board `(play b c (other d))`.
2. **Mandatory Termination & Well-Founded Accessibility (`Acc`)**:
   In [`C5Principle.v`](C5Principle.v), the Follow-Up Principle ([`follow_up`](C5Principle.v)) is proved by **well-founded induction on the number of remaining empty cells (`empties b`)** via `lt_wf : well_founded lt`. Rocq's kernel enforces **strict totality**: every fixpoint must decrease structurally on an inductive argument (such as the accessibility proof object `Acc lt (empties b)`). This guarantees **logical consistency**—no infinite recursion can ever masquerade as a proof of `False`.
3. **The Conversion Rule & Boolean Reflection (`vm_compute`)**:
   CIC builds **computation directly into type checking** via the *Conversion Rule*: if type `A` and type `B` beta-delta-iota-zeta reduce to the same normal form (`A ≡ B`), then any term `t : A` automatically has type `B` with **zero proof-term size overhead**!
   - Once we proved [`check_static_sound`](C5CertChecker.v) (`check_static d b st = true -> Static d b st`) and [`cert_sound`](C5CertChecker.v), Rocq's bytecode virtual machine (`vm_compute`) simply executes the boolean decider at native speed, reduces `check_cover White b_open white_27pair_struct` to `true`, and verifies `true = true` via `reflexivity` in milliseconds.
4. **Separation of Logical `Prop` vs. Computational `Type`**:
   In [`C5Rules.v`](C5Rules.v), `structure` is a clean data record in `Type`, whereas [`Static d b st`](C5Rules.v) is a 13-field logical conjunction in `Prop` with existential and universal quantifiers. Separating `Prop` from `Type` allows rich deductive invariants to be erased during program extraction while remaining fully checked in the kernel.

---

### 8.2 Why Weaker Type Systems Like Standard Haskell Cannot Prove This Soundly
While **Haskell** possesses an expressive polymorphic type system based on **System Fω** (Girard, 1972) extended in GHC with `GADTs`, `DataKinds`, and `TypeFamilies`, **standard Haskell cannot serve as a sound mathematical theorem prover** for three fundamental reasons:

| Foundational Property | Rocq 9.1 (CIC) | Standard Haskell (GHC System Fω + Extensions) | Why Haskell Fails on `connect5_8x7_fair` |
| :--- | :--- | :--- | :--- |
| **1. Totality & Termination** | **Strictly Enforced by Kernel** (Structural guardedness & `Acc` well-foundedness) | **Unchecked** (Unrestricted general recursion `fix` and `undefined` in every type) | In Haskell, **every type is inhabited by bottom (`⊥`)**! One can write `fakeProof :: Safe White Initial Black; fakeProof = fakeProof`, and GHC accepts it as well-typed—even for a false theorem like `Win White == Draw`! |
| **2. Dependent `Π` and `Σ` Types** | **First-Class Native Support** (`forall (b : board), safe d b s`) | **Phase-Separated** (Terms cannot appear in types without `Singletons` promotion) | Encoding [`C5Rules.v`](C5Rules.v) in GHC requires duplicating every term-level function (`play`, `col`, `count_empty`, `freezone`) as a type-level `TypeFamily` and manually threading hundreds of singleton equality casts (`Refl`). |
| **3. Logical Soundness of the Core** | **Self-Contained Tiny Kernel** (Consistent intuitionistic type theory) | **Unsound Type-Level Escape Hatches** (`unsafeCoerce`, non-exhaustive patterns, `TypeInType` Girard paradox) | GHC's type checker was designed for zero-cost abstractions in software engineering, not logical consistency; looping type families and partial matches break Curry–Howard soundness. |

> **What about Liquid Haskell (Refinement Types)?**
> **Liquid Haskell** augments GHC with a termination checker and refinement predicates (`{v:Int | 0 <= v && v < 8}`) discharged by an external **SMT solver (Z3)**. While Liquid Haskell excels at automating bounds checks and linear arithmetic, SMT solvers struggle with **alternating game-tree quantifiers** (`∀ attacker move c₁, ∃ defender response c₂, ...` inside [`safe`](C5Game.v)) and deep inductive invariants like [`structure_sound`](C5Rules.v). Moreover, relying on Z3 expands the Trusted Computing Base (TCB) from a tiny functional kernel to hundreds of thousands of lines of unverified C++ inside GHC and Z3.

---

### 8.3 Would an Even Stronger or Different Type System Make the Proof Simpler?
Moving *beyond* standard Rocq 9.1 reveals a fascinating duality: some stronger type-theoretic features **dramatically simplify** the proof, while naive uses of dependent types **make the proof much harder**!

1. **Intrinsic Dependent Indexing (`Fin 8`, `Vect 7` in Agda / Idris 2) — *Actually Harder ("Green Slime" Transport Hell)!***
   - *The Temptation*: Why not define `Cell = Fin 8 × Fin 7` and `Board = Vect 8 (BoundedVect 7 Player)` so out-of-bounds columns and rows are unrepresentable at the type level?
   - *Why It Backfires Under Gravity*: In a gravity game, playing a move `play b c p` increases the height of column `c` from `h` to `h + 1`. If column heights are baked into the *type* of `Board`, then `b` and `play b c p` have **different types**! Every theorem comparing a board before and after a move in [`C5Board.v`](C5Board.v) and [`C5Rules.v`](C5Rules.v) then requires **dependent type transport (`eq_rect` / heterogeneous equality `JMeq`)**—a notorious anti-pattern called **"green slime"** by Conor McBride.
   - *Gonthier's SSReflect Lesson*: Keeping data types simple (`cell := nat * nat`, `board := list (list player)`) and enforcing invariants extrinsically via a computable boolean predicate ([`check_static`](C5CertChecker.v)) completely avoids dependent transport hell!
2. **Native Quotient Types & Extensional Finite Sets (Lean 4 / Observational Type Theory) — *Would Shrink [`C5Rules.v`](C5Rules.v) by ~35%!***
   - Because Rocq's CIC is an **intensional type theory**, two lists `[p1; p2]` and `[p2; p1]` containing the exact same dominoes are *not* equal (`[p1; p2] ≠ [p2; p1]`). In [`C5Rules.v`](C5Rules.v), roughly a third of our 1,160 lines of proof is spent showing that removing a consumed domino `remove_pair` from `s_strong` or `s_rigid` preserves `NoDup (unit_cells st)` and `count_empty b (freezone b st)`.
   - In a type theory with native **Quotient Types** (such as **Lean 4** or **Observational Type Theory**), `s_strong` and `freezone` can be represented as true **extensional finite sets (`Finset`)**, where unordered collections with identical elements are equal by extensionality—eliminating ~400 lines of list-permutation bookkeeping!
3. **Univalence & Higher Inductive Types (Cubical Agda / Homotopy Type Theory — HoTT) — *Automatic Isomorphism Transport!***
   - In our architecture, the Rocq specification uses a list-of-columns representation `board : list (list player)` ([`C5Game.v`](C5Game.v)), whereas our CUDA engine uses John Tromp's 64-bit sentinel bitboard `uint64_t` ([`solver/c5_gpu_search.cu`](solver/c5_gpu_search.cu)).
   - In **Cubical Type Theory** (where Voevodsky's **Univalence Axiom** `(A ≃ B) ≃ (A = B)` computes), proving a bijection between well-formed `board` lists and valid 64-bit bitboards makes the two types **equal**, allowing every theorem proved on `list (list player)` to be **automatically transported** to 64-bit bitboards!

---

## ✅ 9. Index of Machine-Checked Theorems Backing Every Claim

Every mathematical, structural, and game-theoretic claim in this repository is backed by a machine-checked theorem compiled by **Rocq 9.1** (`rocq compile`) and verified by [`CheckAssumptions.v`](CheckAssumptions.v) to print `Closed under the global context` (**0 axioms, 0 admits**):

| # | Theorem Name | Source File & Line | Mathematical Statement Proven in Rocq 9.1 | Verification Method |
| :-: | :--- | :--- | :--- | :---: |
| **1** | [`structure_sound`](C5Rules.v#L898) | [`C5Rules.v:898`](C5Rules.v#L898) | `∀ d b st, Static d b st → safe d b (other d)` (Deductive soundness of Allis's strong dominoes, rigid chains, weak units, and Rule R3 frozen threats). | Well-founded induction on `empties b` (`follow_up`) |
| **2** | [`strategy_sound`](C5Certificate.v#L71) | [`C5Certificate.v:71`](C5Certificate.v#L71) | `∀ d b s t, valid_strategy d b s t = true → safe d b s` (Soundness of explicit inductive strategy trees). | Structural induction on `strategy` |
| **3** | [`mutual_safety_draw`](C5Certificate.v#L211) | [`C5Certificate.v:211`](C5Certificate.v#L211) | `∀ c0, legal initial c0 = true → safe White (play initial c0 White) Black → safe Black initial White → game_value = Draw`. | Constructive minimax evaluation (`eval_fuel_safe`) |
| **4** | [`connect5_8x7_fair`](C5Certificate.v#L230) | [`C5Certificate.v:230`](C5Certificate.v#L230) | Master theorem reducing `game_value = Draw` to valid White and Black strategy certificates. | Direct corollary of `mutual_safety_draw` |
| **5** | [`check_static_sound`](C5CertChecker.v#L181) | [`C5CertChecker.v:181`](C5CertChecker.v#L181) | `∀ d b st, check_static d b st = true → Static d b st` (Boolean reflection soundness for Allis structures). | Boolean reflection & list deciders |
| **6** | [`cert_sound`](C5CertChecker.v#L385) | [`C5CertChecker.v:385`](C5CertChecker.v#L385) | `∀ fuel cert d b s idx, check_cert_node cert fuel d b s idx = true → safe d b s` (Soundness of fast DAG checker). | Induction on `fuel` + `structure_sound` |
| **7** | [`cert_fair`](C5CertChecker.v#L424) | [`C5CertChecker.v:424`](C5CertChecker.v#L424) | `check_cert_node` for White (`c0=3`) and Black implies `game_value = Draw`. | Combines `cert_sound` + `mutual_safety_draw` |
| **8** | [`parity_trap_ply1`](C5CertChecker.v#L446) | [`C5CertChecker.v:446`](C5CertChecker.v#L446) | `empties (play initial 3 White) = 55 ∧ Nat.even (empties (play initial 3 White)) = false` (First-Player Parity Obstruction at Ply 1). | `vm_compute; reflexivity` |
| **9** | [`opening_27pair_line_cover`](C5CertChecker.v#L480) | [`C5CertChecker.v:480`](C5CertChecker.v#L480) | `check_cover White b_open white_27pair_struct = true` (All 76 winning lines covered by `(3,0)` + 24 vertical dominoes + 3 ground pairs). | `vm_compute; reflexivity` |
| **10** | [`core10_covers_all_76_lines`](C5CertChecker.v#L511) | [`C5CertChecker.v:511`](C5CertChecker.v#L511) | `check_cover White b_open white_core10_struct = true` (10-Cell Core in Cols `2, 3, 4, 6` covers all 52 non-vertical winning lines). | `vm_compute; reflexivity` |
| **11** | [`dead_cell_4_6_six_lines_double_blocked`](C5CertChecker.v#L527) | [`C5CertChecker.v:527`](C5CertChecker.v#L527) | `length lines_through_4_6 = 6` and every one of the 6 lines through `(4,6)` contains `≥ 2` guaranteed White cells. | `vm_compute; reflexivity` |
| **12** | [`r3_frozen_column_restores_even_parity`](C5CertChecker.v#L542) | [`C5CertChecker.v:542`](C5CertChecker.v#L542) | For every odd empty count `E ∈ {7..55}` and odd threat row `ft ∈ {1, 3, 5}`, `Nat.even (E - (7 - (ft - 1))) = true`. | `vm_compute; reflexivity` |

---

## 📚 10. Verified Primary-Source Bibliography

1. **Allis, L. Victor (1988)**. *A Knowledge-Based Approach of Connect-Four — The Game is Solved: White Wins*. Master's Thesis, Report IR-163, Faculty of Mathematics and Computer Science, Vrije Universiteit Amsterdam, October 16, 1988.
2. **Allen, James Dow (1988, 1990)**. *The Complete Book of Connect 4: History, Strategy, Puzzles*. Sterling Publishing, New York, 1990 (initial solution announced on Usenet `rec.games.programmer`, October 1, 1988).
3. **Allis, L. Victor, van der Meulen, Maarten, and van den Herik, H. Jaap (1994)**. "Proof-Number Search." *Artificial Intelligence*, Vol. 66, No. 1, pp. 91–124, March 1994. DOI: `10.1016/0004-3702(94)90004-3`.
4. **Allis, L. Victor (1994)**. *Searching for Solutions in Games and Artificial Intelligence*. PhD Dissertation, Rijksuniversiteit Limburg (Maastricht University), Maastricht, The Netherlands, September 1994. ISBN `90-9007488-0`.
5. **Tromp, John (1995–2015)**. *The Fhourstones Benchmark and Connect-4 Game-Theoretic Outcome Database*. CWI Amsterdam, `https://tromp.github.io/c4/c4.html` and `https://tromp.github.io/c4/fhour.html`.
6. **McAllester, David A. (1988)**. "Conspiracy Numbers for Min-Max Search." *Artificial Intelligence*, Vol. 35, No. 3, pp. 287–310, 1988.
7. **Nagai, Ayumu (1999)**. "A New Depth-First-Search Algorithm for AND/OR Trees." Master's Thesis / Game Programming Workshop (GPW-99), Department of Information Science, University of Tokyo, 1999.
8. **Nagai, Ayumu (2002)**. *Df-pn Algorithm for Searching AND/OR Trees and Its Applications*. PhD Dissertation, Department of Information Science, University of Tokyo, 2002.
9. **Edelkamp, Stefan, and Kissmann, Peter (2008)**. "Symbolic Classification of General Two-Player Games." In *Proceedings of the 18th European Conference on Artificial Intelligence (ECAI 2008)*, pp. 905–906, Patras, Greece, 2008 (independently verified the `4,531,985,219,092` state count of `7 × 6` Connect-Four via BDDs).
10. **Kaneko, Tomoyuki (2010)**. "Parallel Depth-First Proof-Number Search." In *Proceedings of the 24th AAAI Conference on Artificial Intelligence (AAAI-10)*, pp. 95–100, Atlanta, GA, 2010.
11. **Pawlewicz, Jakub, and Lew, Łukasz (2013)**. "Scalable Parallel DFPN Search." In *Computers and Games (CG 2013)*, Lecture Notes in Computer Science (LNCS), Vol. 8427, pp. 138–150, Springer, 2013.
12. **Pons, Pascal (2015–2019)**. *Solving Connect-4: How to Build a Perfect AI*. Technical Monograph Series, `http://blog.gamesolver.org/`.
13. **Gonthier, Georges (2008)**. "Formal Proof—The Four-Color Theorem." *Notices of the American Mathematical Society*, Vol. 55, No. 11, pp. 1382–1393, December 2008.
14. **Beck, József (2008)**. *Combinatorial Games: Tic-Tac-Toe Theory*. Encyclopedia of Mathematics and its Applications, Vol. 114, Cambridge University Press, 2008.
15. **Coquand, Thierry, and Huet, Gérard (1988)**. "The Calculus of Constructions." *Information and Computation*, Vol. 76, No. 2–3, pp. 95–120, 1988.
16. **Barendregt, Henk P. (1992)**. "Lambda Calculi with Types." In *Handbook of Logic in Computer Science*, Vol. 2, pp. 117–309, Oxford University Press, 1992.
17. **Univalent Foundations Program (2013)**. *Homotopy Type Theory: Univalent Foundations of Mathematics*. Institute for Advanced Study, Princeton, 2013.

---

<div align="center">

[![Return to Main Repository README](https://img.shields.io/badge/⬅_Return_to_Main_Landing_Page-README.md-2563eb?style=for-the-badge)](README.md)

</div>

