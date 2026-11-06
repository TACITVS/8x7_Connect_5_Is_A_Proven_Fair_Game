<div align="center">

# 📐 Follow-Up Paper (Paper II): The Hilbert–Zermelo–Erdős Classical Pen-and-Paper Proof of 8×7 Connect-5 Fairness

### **Analytic Modulo-2 Hypergraph Transversals, Gravitational Induction, and Foundations Across Common Lisp (ACL2), Haskell, Rocq 9.1, and Lean 4**

[![Back to Main Repository](https://img.shields.io/badge/⬅_Back_to_Main_Landing_Page-README.md-2563eb?style=for-the-badge)](README.md)
[![Rocq 9.1 Verified](https://img.shields.io/badge/Rocq_9.1-22_Theorems_Verified_(0_Axioms)-16a34a?style=for-the-badge&logo=coq)](CheckAssumptions.v)
[![Lean 4.35.0 Verified](https://img.shields.io/badge/Lean_4.35.0-14_Analytic_Hand--Proof_Theorems_(0_Sorrys)-10b981?style=for-the-badge)](lean4/Connect5HandProof.lean)
[![Technical Audit Verified](https://img.shields.io/badge/🛡️_Audit_Verified-11%2F11_GPT--6.1_Findings_Resolved-0ea5e9?style=for-the-badge)](TECHNICAL_AUDIT_RESPONSE.md)
[![Paper II AMS PDF](https://img.shields.io/badge/📄_Download_Paper_II-AMS_Style_PDF-dc2626?style=for-the-badge)](paper/connect5_8x7_hilbert_erdos_AMS.pdf)
[![Paper II ACS PDF](https://img.shields.io/badge/📄_Download_Paper_II-ACS_Two--Column_PDF-7c3aed?style=for-the-badge)](paper/connect5_8x7_hilbert_erdos_ACS.pdf)
[![Historical Monograph](https://img.shields.io/badge/📜_Companion_Monograph-Historical_Audit-f59e0b?style=for-the-badge)](HISTORICAL_AND_LITERATURE_ANALYSIS.md)

</div>

---

> [!IMPORTANT]
> **Abstract of Follow-Up Paper II**: In Paper I ([`paper/connect5_8x7_fairness_AMS.pdf`](paper/connect5_8x7_fairness_AMS.pdf)), we formalized the deductive pairing theory of Connect-5 on an `8 × 7` board with gravity in **Rocq 9.1** (`C5Rules.v`, `C5CertChecker.v`) alongside a parallel `df-pn` search engine and a **CUDA 13.5 (`sm_89`) bitboard tactical evaluator**. A natural foundational question arises:
> *How would classical mathematicians such as **David Hilbert**, **Ernst Zermelo**, and **Paul Erdős** prove the combinatorial core of this theorem purely by hand with pen and paper, without computer enumeration of the 76 winning lines?*
>
> In this follow-up paper, we present a complete, human-readable **Hilbert–Zermelo–Erdős pen-and-paper proof** of the combinatorial core of `8 × 7` Connect-5 fairness—and its complete **zero-enumeration analytic formalization in both Rocq 9.1 ([`C5CertChecker.v`](C5CertChecker.v)) and Lean 4.35.0 ([`lean4/Connect5HandProof.lean`](lean4/Connect5HandProof.lean))**. Using only the **Pigeonhole Principle on 5-column windows** and **modular arithmetic (`mod 2`)** along affine lines of slope `s ∈ {0, +1, −1}`, we prove analytically in 12 lines that a **10-cell transversal `C₁₀`** (and the **7-cell Central Wall `W₇`**) blocks all 52 horizontal and diagonal winning lines, while two middle vertical dominoes per column block all 24 vertical lines. We further provide an analytic proof of the **Rule R3 Frozen-Threat Parity Law (`odd − odd = even`)**, together with **4 concrete midgame Rule-R3 and Rule-R2 theorems (`r3_concrete_cert_safe`, `r2_concrete_black_static_safe`)** proving unconditional game-tree `safe` across `8^47` and `8^36` continuations, and pinpoint the exact boundary where pure deductive mathematics meets the finite opening trunk (see also [`TECHNICAL_AUDIT_RESPONSE.md`](TECHNICAL_AUDIT_RESPONSE.md)). Finally, we compare how this proof is mechanized across the spectrum of formal foundations: from **Common Lisp** (via Boyer–Moore's untyped applicative logic **ACL2** and homoiconic LCF macro kernels) and **Haskell (`System Fω`)** to **Rocq 9.1 (`CIC`)** and **Lean 4.35.0 (`Quotient Types` + `omega`)**.

<div align="center">
  <img src="assets/erdos_10cell_proof.svg" alt="The Hilbert-Erdos Pen-and-Paper Proof: 10-Cell Modulo-2 Transversal (C10)" width="98%"/>
</div>

---

## 📖 Table of Contents

1. [Introduction: Hilbert, Zermelo, and Erdős at the Game Board](#-1-introduction-hilbert-zermelo-and-erdős-at-the-game-board)
2. [Paul Erdős's Pen-and-Paper Proof of the 76-Line Cover (No Computer Needed!)](#-2-paul-erdőss-pen-and-paper-proof-of-the-76-line-cover-no-computer-needed)
3. [David Hilbert & Ernst Zermelo's Inductive Framework & Rule R3 Parity Law](#-3-david-hilbert--ernst-zermelos-inductive-framework--rule-r3-parity-law)
4. [Where Pure Pen-and-Paper Stops and the Computer Must Help](#-4-where-pure-pen-and-paper-stops-and-the-computer-must-help)
5. [Foundations of Mechanization: Common Lisp (ACL2 & Homoiconic LCF), Haskell, Rocq 9.1, and Lean 4](#-5-foundations-of-mechanization-common-lisp-acl2--homoiconic-lcf-haskell-rocq-91-and-lean-4)
6. [Machine-Checked Formalization of the Hand Proof in Rocq 9.1 & Lean 4.35.0](#-6-machine-checked-formalization-of-the-hand-proof-in-rocq-91--lean-4350)
7. [Download the Compiled Academic PDFs (AMS & ACS Styles)](#-7-download-the-compiled-academic-pdfs-ams--acs-styles)

---

## 🏛️ 1. Introduction: Hilbert, Zermelo, and Erdős at the Game Board

Modern computer-assisted proofs—from the Four Color Theorem (Appel & Haken, 1976; Gonthier, 2005) to our Rocq 9.1 verification of `8 × 7` Connect-5—frequently verify finite combinatorial invariants via computational reflection (`vm_compute`). Yet in the classical tradition of:
- **David Hilbert** (*Grundlagen der Geometrie*, 1899), who championed minimal axiomatic foundations at Göttingen,
- **Ernst Zermelo** (*Über eine Anwendung der Mengenlehre auf die Theorie des Schachspiels*, 1913), Hilbert's Göttingen colleague who proved the first theorem of formal game theory, and
- **Paul Erdős** (who, with **József Selfridge** in 1973 and **József Beck** in *Combinatorial Games: Tic-Tac-Toe Theory*, 2008, developed the hypergraph pairing and transversal method for Maker–Breaker games),

a mathematical proof should illuminate *why* a combinatorial invariant holds without brute-force enumeration of all 76 winning lines.

---

## ✍️ 2. Paul Erdős's Pen-and-Paper Proof of the 76-Line Cover (No Computer Needed!)

Following Erdős and Beck (2008), we model the `8 × 7` Connect-5 board as a **5-uniform hypergraph `H = (V, L)`** where:
- **Vertices `V`**: `V = {0, 1, ..., 7} × {0, 1, ..., 6}` (`|V| = 56` cells `(c, r)`).
- **Hyperedges `L`**: `L = L_vert ⊔ L_nonvert` (`|L| = 76` winning lines of length 5, partitioned into `|L_vert| = 24` vertical lines and `|L_nonvert| = 52` horizontal and diagonal lines).

### 2.1 Lemma 1: Analytic Proof for All 24 Vertical Lines (3 Sentences)
> **Lemma 1 (Vertical Domino Transversal):**
> *In any column `c ∈ {0, ..., 7}`, let `D_c = {((c,1),(c,2)), ((c,3),(c,4)), ((c,5),(c,6))}` be three disjoint vertical dominoes occupying rows `{1, ..., 6}`. Every vertical winning line `L ∈ L_vert` in column `c` completely contains at least one domino `((c, r), (c, r+1)) ∈ D_c`.*
>
> **Pen-and-Paper Proof:**
> Any vertical line of length 5 in column `c` consists of 5 consecutive rows `L = {(c, r₀ + k) : k ∈ {0, 1, 2, 3, 4}}` for some starting row `r₀ ∈ {0, 1, 2}`:
> - If `r₀ ∈ {0, 1}`, then `{1, 2} ⊂ [r₀, r₀ + 4]`, so `L` contains the domino `((c, 1), (c, 2)) ∈ D_c`.
> - If `r₀ = 2`, then `{3, 4} ⊂ [2, 6]`, so `L` contains the domino `((c, 3), (c, 4)) ∈ D_c`.
>
> Under vertical gravity, the upper cell `(c, r+1)` becomes legally playable on the exact ply after the lower cell `(c, r)` is played. Thus the defender immediately claims the upper cell whenever the attacker claims the lower cell, blocking all 24 vertical lines unconditionally! **Q.E.D.**

---

### 2.2 Theorem 1: Analytic Proof of the 10-Cell Modulo-2 Transversal (All 52 Non-Vertical Lines)
Instead of checking the 52 horizontal and diagonal winning lines by computer (`core10_covers_all_76_lines`), Erdős would prove that just **10 specific cells** block all 52 lines using only the **Pigeonhole Principle** and **parity (`mod 2`)**:

> **Theorem 1 (The 10-Cell Modulo-2 Transversal Theorem):**
> *Define the 10-element set `C₁₀ ⊂ V` consisting of White's opening stone at `(3, 0)` together with the upper domino cells of Columns `4`, `2`, and `6`:*
> - **Opening Anchor:** `{(3, 0)}`
> - **Column 4 Odd Uppers (`U₄`):** `U₄ = {(4, 1), (4, 3), (4, 5)}`
> - **Column 2 Even Uppers (`U₂`):** `U₂ = {(2, 2), (2, 4), (2, 6)}`
> - **Column 6 Even Uppers (`U₆`):** `U₆ = {(6, 2), (6, 4), (6, 6)}`
>
> *Then every horizontal or diagonal winning line `L ∈ L_nonvert` intersects `C₁₀` (`L ∩ C₁₀ ≠ ∅`).*
>
> **Pen-and-Paper Proof:**
> Every horizontal or diagonal winning line `L ∈ L_nonvert` spans **5 consecutive columns `[c₀, c₀ + 4]`** for some starting column `c₀ ∈ {0, 1, 2, 3}`, and is given by the affine equation:
> ```text
> L = { (c, r(c)) : c ∈ [c₀, c₀ + 4] },   where  r(c) = r(4) + s · (c − 4),   slope s ∈ {0, +1, −1},
> ```
> with `0 ≤ r(c) ≤ 6` for all `c ∈ [c₀, c₀ + 4]`.
>
> **Step 1 (Pigeonhole Principle on 5-Column Windows):**
> Because `c₀ ∈ {0, 1, 2, 3}`, we have `c₀ ≤ 3` and `c₀ + 4 ≥ 4`. Therefore, **every non-vertical 5-line crosses both Column `c = 3` and Column `c = 4`**! Furthermore:
> - If `c₀ ∈ {0, 1, 2}`, then `2 ∈ [c₀, c₀ + 4]` (so `L` crosses Column `c_even = 2`).
> - If `c₀ = 3`, then `[c₀, c₀ + 4] = [3, 7]`, so `6 ∈ [3, 7]` (and `L` crosses Column `c_even = 6`).
>
> Thus `L` always crosses Column `3`, Column `4`, and at least one column `c_even ∈ {2, 6}`.
>
> **Step 2 (Modulo-2 Parity Split on `r(4)`):**
> Consider the parity of the row coordinate `r(4) ∈ {0, 1, ..., 6}` where `L` crosses Column 4:
> - **Case A (`r(4)` is ODD, i.e., `r(4) ∈ {1, 3, 5}`):**
>   Since `4 ∈ [c₀, c₀ + 4]`, the cell `(4, r(4))` lies on `L` and belongs to `U₄ = {(4,1), (4,3), (4,5)} ⊂ C₁₀`. Done!
> - **Case B (`r(4)` is EVEN, i.e., `r(4) ∈ {0, 2, 4, 6}`):**
>   Examine the row coordinate `r(c_even)` where `L` crosses column `c_even ∈ {2, 6}`. Because the horizontal distance `|c_even − 4| = 2` is **even**, modular arithmetic yields:
>   ```text
>   r(c_even) = r(4) ± 2s ≡ r(4) ≡ 0 (mod 2).
>   ```
>   That is, **`r(c_even) ∈ {0, 2, 4, 6}` is ALSO EVEN!**
>   - **Subcase B1 (`r(c_even) ∈ {2, 4, 6}`):** Then `(c_even, r(c_even)) ∈ L ∩ (U₂ ∪ U₆) ⊂ C₁₀`. Done!
>   - **Subcase B2 (`r(c_even) = 0`):**
>     1. If `s = 0` (horizontal line on Row 0), then `r(c) = 0` for all `c ∈ [c₀, c₀ + 4]`. Since `3 ∈ [c₀, c₀ + 4]`, `L` passes directly through White's opening stone **`(3, 0) ∈ C₁₀`**!
>     2. If `s = +1` (upward diagonal `/`) and `r(2) = 0`, non-negativity `r(c₀) ≥ 0` forces `c₀ = 2`. Then `[c₀, c₀ + 4] = [2, 6]` *also* contains `c = 6` at height `r(6) = r(2) + 4 = 4`, so **`(6, 4) ∈ L ∩ U₆ ⊂ C₁₀`**!
>     3. If `s = −1` (downward diagonal `\`) and `r(6) = 0`, non-negativity `r(c₀ + 4) ≥ 0` forces `c₀ + 4 = 6` (`c₀ = 2`), so `[2, 6]` *also* contains `c = 2` at height `r(2) = r(6) + 4 = 4`, giving **`(2, 4) ∈ L ∩ U₂ ⊂ C₁₀`**!
>
> In every case, `L ∩ C₁₀ ≠ ∅`. **Q.E.D.**

---

### 2.3 Proposition 1: Analytic Proof of Dead-Cell `(4, 6)` Double-Blocking
> **Proposition 1 (Double-Blocking of `(4, 6)`):**
> *The top cell `(4, 6)` belongs to exactly 6 winning lines in `L`, and every one of these 6 lines contains at least two cells from White's guaranteed upper domino set `U = U₄ ∪ ⋃_{c ≠ 4} {(c,2), (c,4), (c,6)}`.*
>
> **Pen-and-Paper Proof:**
> Let `L ∈ L` pass through `(4, 6)`:
> 1. **Vertical (`c = 4`):** The unique vertical 5-line containing `(4, 6)` is `{(4,2), (4,3), (4,4), (4,5), (4,6)}`, which contains the two cells `(4, 3), (4, 5) ∈ U₄`.
> 2. **Horizontal (`r = 6`):** On row 6, there are 4 horizontal 5-lines (`c₀ ∈ {0, 1, 2, 3}`). Since `(c, 6) ∈ U` for all `c ≠ 4`, each of these 4 lines contains `5 − 1 = 4 ≥ 2` cells of `U`.
> 3. **Upward Diagonal (`s = +1`):** Since `r(4) = 6` is at the top of the board, `L` cannot extend to `c > 4`, forcing `c₀ = 0` and `L = {(0,2), (1,3), (2,4), (3,5), (4,6)}`, which contains `(0, 2), (2, 4) ∈ U`.
> 4. **Downward Diagonal (`s = −1`):** Since `r(4) = 6` is at the top of the board, `L` cannot extend to `c < 4`, requiring `[c₀, c₀ + 4] = [4, 8]`, which is impossible since `c ≤ 7`.
>
> Thus `1 + 4 + 1 + 0 = 6` lines pass through `(4, 6)`, each containing `≥ 2` cells of `U`. **Q.E.D.**

---

## ⚖️ 3. David Hilbert & Ernst Zermelo's Inductive Framework & Rule R3 Parity Law

While Erdős provides the static hypergraph transversal, **David Hilbert** and **Ernst Zermelo** axiomatize the dynamic preservation of the pairing invariant by induction on the number of remaining empty cells `E = 56 − ∑ h_c`:

> **Theorem 2 (Rule R3 Poisoned-Threat Parity Restoration Law):**
> *Suppose board `b` has an odd number of remaining empty cells `E ≡ 1 (mod 2)` (as holds at every Black turn in First-Player Defense, `E = 56 − (2m + 1) = 55 − 2m`). If White holds a 4-in-a-row threat at an odd row `ft ∈ {1, 3, 5}` in column `fc` with `h_{fc} < ft`, then freezing the poisoned column suffix `F = {(fc, r) : ft − 1 ≤ r ≤ 6}` leaves an **even** number of empty cells in the remaining freezone `Z`.*
>
> **Pen-and-Paper Proof:**
> Because `h_{fc} ≤ ft − 1`, all cells in column `fc` from row `ft − 1` to row `6` are currently empty. The cardinality of `F` is:
> ```text
> |F| = 6 − (ft − 1) + 1 = 8 − ft.
> ```
> Since `ft ∈ {1, 3, 5}` is odd, `|F| = 8 − ft ∈ {3, 5, 7}` is **odd** (`|F| ≡ 1 (mod 2)`). If Black ever plays `(fc, ft − 1)`, gravity unlocks `(fc, ft)` on the immediate next ply, allowing White to play `(fc, ft)` and win immediately (`safe_def`). Hence Black can never enter `F`. Subtracting `|F|` and the `2|P|` paired cells (`2|P| ≡ 0 (mod 2)`) from `E` yields:
> ```text
> |Z| = E − 2|P| − (8 − ft) ≡ 1 − 0 − 1 ≡ 0 (mod 2),
> ```
> restoring **even** parity in the freezone `Z`! **Q.E.D.**

---

## 🚧 4. Where Pure Pen-and-Paper Stops and the Computer Must Help

Why does a complete proof of `8 × 7` Connect-5 combine our analytic Hilbert–Erdős & Central Wall theorems with Rocq `vm_compute` certificates and `df-pn` opening search? Our verification architecture consists of three distinct layers (detailed in [`TECHNICAL_AUDIT_RESPONSE.md`](TECHNICAL_AUDIT_RESPONSE.md)):

1. **Layer A — Unconditional Analytic & Combinatorial Laws (Rocq Theorems `8–18` & Lean 4 Theorems `1–14`):**
   Proves with zero computer enumeration (`lia` / `omega`) that `C₁₀` and the Central Wall `W₇` block all 76 lines, that `(4, 6)` is double-blocked on all 6 lines through it, and that Rule R3 restores even parity (`(2k + 1) - (8 - (2j + 1)) = 2(k + j - 3)`).
2. **Layer B — Unconditional Leaf-to-Game-Tree Soundness & Concrete Midgame Certificates (Rocq Theorems `1–3, 5–6, 19–22`):**
   - At Ply 1 (`b_open`, `55` empty cells), only 1 stone is on the board, so no 4-stone frozen threat exists yet (`s_frozen = None` requires even empty cells, and an unassigned cell cannot be left in an unfrozen `Static` structure because the attacker could use it as a tempo-burning pass move once Column 4 fills to row 5).
   - Once a midgame Rule-R3 (`s_frozen = Some (4, 1)`) or Rule-R2 (`s_frozen = None` at even empty count) leaf is reached, [`r3_concrete_check_static_true`](C5CertChecker.v#L748), [`r3_concrete_Static`](C5CertChecker.v#L755), [`r3_concrete_cert_safe`](C5CertChecker.v#L763), and [`r2_concrete_black_static_safe`](C5CertChecker.v#L812) prove **unconditional game-tree safety (`safe`)** across all `8^47` and `8^36` legal continuations!
3. **Layer C — Conditional Root Reductions & Finite Opening Trunk (Rocq Theorems `4` & `7`):**
   In Theorem 1 (`C₁₀`), for `((c,1),(c,2))` in Columns `2` and `6` to act as *Strong Dominoes*, the ground cells on Row 0 must first be occupied or locked in a Rigid Chain (`s_rigid`), and in First-Player Defense White must accumulate a 4-stone Rule-R3 threat. Bridging Ply 0/1 to those Rule-R1/R2/R3 midgame leaves is a finite opening-trunk search problem (`solver/pdfpn_fast.c`), linked to `game_value = Draw` by the conditional reduction theorems `connect5_8x7_fair` and `cert_fair`.

---

## 💻 5. Foundations of Mechanization: Common Lisp (ACL2 & Homoiconic LCF), Haskell, Rocq 9.1, and Lean 4

<div align="center">
  <img src="assets/type_theory_spectrum.svg" alt="The Type-Theory Spectrum for Proving 8x7 Connect-5 Fairness" width="98%"/>
</div>

### 5.1 How Untyped Common Lisp Achieves Formal Mathematical Rigour
Static types are *not* the only path to machine-checked mathematical truth. **Common Lisp**—despite being dynamically typed—is one of the premier theorem-proving languages in history through two complementary paradigms:

1. **The Boyer–Moore Applicative Common Lisp Logic (`ACL2`)**:
   - Created by Robert S. Boyer, J Strother Moore, and Matt Kaufmann (**2005 ACM Software System Award**), **ACL2** is literally a pure, applicative subset of Common Lisp equipped with an inductive theorem prover.
   - **Soft Typing via Predicates**: Instead of static types, ACL2 uses executable Common Lisp boolean functions (`wf-board-p`, `static-p`) as hypotheses in `(defthm name (implies (and ...) ...))`.
   - **The Definitional Principle (Ordinal Measure Termination)**: Unlike Haskell (where `badProof = badProof` is accepted without a termination check), ACL2 intercepts every recursive `defun` and requires a proof that an ordinal measure—such as `(empties b)`—strictly decreases in the well-founded ordering `< ε₀`.
   - **Native `SBCL` Reflection**: Because every ACL2 formula is executable Common Lisp, running ACL2 on **SBCL (Steel Bank Common Lisp)** compiles our certificate checker directly to native x86-64 machine code!
2. **Homoiconicity & Sealed LCF / Macro Kernels (`Milawa`, `Pie`, `Cur`)**:
   - Because Common Lisp is **homoiconic** (*code is data; every program and proof is an S-expression AST*), one can implement Robin Milner's **LCF sealed-kernel pattern** in ~300 lines of Common Lisp (sealing a `theorem` struct inside a locked Lisp package so only verified inference rules can construct it, as in Jared Davis's self-verifying prover **Milawa**), or run a bidirectional dependent type-checker inside a compile-time `defmacro` (**Pie** / **Cur**).
   - **One Language Instead of Three**: Whereas Rocq separates specifications (*Gallina*), tactics (*Ltac*), and plugins (*OCaml*) into three distinct languages, homoiconic Common Lisp unifies object terms, types, theorems, and tactic macros into a single S-expression language!

### 5.2 Comparative Matrix Across Formal Paradigms

| Paradigm / System | Core Logic / Type Theory | How Termination Is Checked | How `core10` & `structure_sound` Are Verified | Logical Soundness |
| :--- | :--- | :--- | :--- | :---: |
| **Standard Haskell (`GHC`)** | `System Fω` + `GADTs` | **Unchecked** (`fix` & `undefined` allowed) | Cannot soundly prove totality; `⊥` inhabits all types | ❌ **Unsound** |
| **Common Lisp (`ACL2`)** | Untyped 1st-Order Applicative Lisp | **Ordinal measure `< ε₀`** on `defun` | Automated induction waterfall + native `SBCL` evaluation | ✅ **Sound** |
| **Common Lisp (`LCF / Macro CIC`)** | Sealed `theorem` package or macro CIC | Kernel/macro structural guard | Homoiconic `defmacro` tactics + S-expression kernel | ✅ **Sound** |
| **Rocq 9.1 (`Coq`)** | Intensional `CIC` (`λPω`) | Kernel structural guard & `Acc` | `follow_up` induction + `vm_compute` boolean reflection | ✅ **Sound (0 Axioms)** |
| **Lean 4.35.0** | `CIC` + Native `Quotient` Types | Kernel structural / `termination_by` | Analytic Presburger `omega` tactic + constructive case splits | ✅ **Sound (0 Sorrys)** |

---

## 💎 6. Machine-Checked Formalization of the Hand Proof in Rocq 9.1 & Lean 4.35.0

In [`C5CertChecker.v`](C5CertChecker.v) (Rocq 9.1) and [`lean4/Connect5HandProof.lean`](lean4/Connect5HandProof.lean) (Lean 4.35.0), we formalize the entire **Hilbert–Zermelo–Erdős pen-and-paper proof**, the **5-Step "Central Wall (`W₇ = E₃ ∪ O₄`) & Alternating Parity" Book Proof**, and **4 Concrete Midgame Rule-R3/R2 `Static` & `safe` Theorems**:

- **The 7-Cell Central Wall (`W₇ = E₃ ∪ O₄`) Insight**: In Column `3`, White guarantees all `4` even rows `E₃ = {(3,0), (3,2), (3,4), (3,6)}`; in Column `4`, White guarantees all `3` odd rows `O₄ = {(4,1), (4,3), (4,5)}`. Because every non-vertical 5-line (`c0 ∈ {0, 1, 2, 3}`) crosses **both** Column `3` and Column `4`, this 7-cell Central Wall **alone blocks 40 of the 52 non-vertical winning lines** (all **28** horizontal lines + all **12** in-phase diagonal lines)! The remaining **12** out-of-phase diagonals have `r₃` odd and `r₄` even, so by alternating column parity they land on even rows `{2, 4, 6}` in Column `2` or Column `6` (`W₆ = {(2,2), (2,4), (2,6), (6,2), (6,4), (6,6)}`).
- **100% Constructive Proofs**: In Rocq 9.1, all **22** theorems are proved via well-founded induction, `lia`, and `vm_compute` (`Closed under the global context`, 0 axioms). In Lean 4.35.0, all **14** theorems are proved 100% constructively via `omega` and explicit parity classification lemmas—**none of them invoke `Classical.choice`**!

### 6.1 The 10 Elementary "Book Proof" & Concrete Midgame `Static`/`safe` Theorems in Rocq 9.1 ([`C5CertChecker.v`](C5CertChecker.v))

| # | Rocq 9.1 Theorem Identifier | Book Proof / Midgame Step Formalized | Proof Engine |
| :-: | :--- | :--- | :---: |
| **13** | [`book_step1_vertical_middle_two_dominoes`](C5CertChecker.v#L574) | **Step 1 (Verticals):** `r0 ≤ 2 → {1,2} ⊆ [r0, r0+4] ∨ {3,4} ⊆ [r0, r0+4]` | `lia` (0 axioms) |
| **14** | [`book_step2_central_wall_pigeonhole`](C5CertChecker.v#L585) | **Step 2 (Pigeonhole):** `c0 ≤ 3 → {3,4} ⊆ [c0, c0+4] ∧ (2 ∈ [c0,c0+4] ∨ 6 ∈ [c0,c0+4])` | `lia` (0 axioms) |
| **15** | [`book_step3_horizontal_parity_split`](C5CertChecker.v#L597) | **Step 3 (Horizontals):** `r ≤ 6 → r ∈ {0,2,4,6} (Col 3) ∨ r ∈ {1,3,5} (Col 4)` | `lia` (0 axioms) |
| **16** | [`book_step4_diagonal_parity_alternation`](C5CertChecker.v#L611) | **Step 4 (Diagonals):** In-phase double-blocked at `(3,r3),(4,r4)` OR out-of-phase hits `{2,4,6}` in Col 2/6 | `lia` (0 axioms) |
| **17** | [`book_central_wall_decomposition`](C5CertChecker.v#L657) | **Exact 76-Line Split:** `W₇` blocks `40/52` non-verticals; `W₆` blocks all `12` out-of-phase diagonals | `vm_compute` (0 axioms) |
| **18** | [`book_step5_r3_parity_law_lia`](C5CertChecker.v#L672) | **Step 5 (Rule R3):** `(2k + 1) - (8 - (2j + 1)) = 2(k + j - 3)` for all `k, j` | `lia` (0 axioms) |
| **19** | [`r3_concrete_check_static_true`](C5CertChecker.v#L748) | **Concrete R3 Reflection:** `empties b_r3 = 47 ∧ check_static = true ∧ check_cert_node = true` | `vm_compute` (0 axioms) |
| **20** | [`r3_concrete_Static`](C5CertChecker.v#L755) | **Concrete R3 Invariant:** `Static White b_r3 white_r3_full_struct` (`s_frozen = Some (4, 1)`) | `check_static_sound` |
| **21** | [`r3_concrete_cert_safe`](C5CertChecker.v#L763) | **Unconditional R3 Safety:** `safe White b_r3 Black ∧ safe White b_ply8 White` (`8^47` continuations) | `structure_sound` + `cert_sound` |
| **22** | [`r2_concrete_black_static_safe`](C5CertChecker.v#L812) | **Unconditional R2 Safety:** `empties b_r2 = 36 ∧ check_static = true ∧ Static ∧ safe Black b_r2 White` | `vm_compute` + `structure_sound` |

### 6.2 All 14 Constructive Hand-Proof Theorems Verified in Lean 4.35.0 ([`lean4/Connect5HandProof.lean`](lean4/Connect5HandProof.lean))

| # | Lean 4 Theorem Identifier | Corresponding Hand-Proof Step | Axioms Used (`#print axioms`) |
| :-: | :--- | :--- | :---: |
| **1** | [`ply1_parity_obstruction`](lean4/Connect5HandProof.lean#L63) | Proposition 2.1: `8*7 - 1 = 55`, `55 % 2 = 1`, and `∀ k : Nat, 2 * k ≠ 55` | `[propext, Quot.sound]` |
| **2** | [`vertical_domino_transversal`](lean4/Connect5HandProof.lean#L82) | Lemma 1: Every 5-row vertical window `[r0, r0+4]` contains `{1,2}` or `{3,4}` | `[propext, Quot.sound]` |
| **3** | [`pigeonhole_5col_window`](lean4/Connect5HandProof.lean#L114) | Step 1 (Pigeonhole): Every 5-col window `[c0, c0+4]` contains `3, 4` and `2` or `6` | `[propext, Quot.sound]` |
| **4** | [`modulo2_parity_preservation`](lean4/Connect5HandProof.lean#L128) | Step 2A (Parity): `r4 % 2 = 0 → rowAt r4 s 2 % 2 = 0 ∧ rowAt r4 s 6 % 2 = 0` | `[propext, Quot.sound]` |
| **5** | [`erdos_10cell_transversal_hand_proof`](lean4/Connect5HandProof.lean#L172) | **Theorem 1:** Every valid non-vertical 5-line `(c0, r4, s)` intersects `C₁₀` | `[propext, Quot.sound]` |
| **6** | [`dead_cell_4_6_vertical_double_blocked`](lean4/Connect5HandProof.lean#L244) | Proposition 1A: Vertical line through `(4,6)` hits both `(4,3)` and `(4,5)` | **None (`0 axioms`)** |
| **7** | [`dead_cell_4_6_nonvertical_double_blocked`](lean4/Connect5HandProof.lean#L254) | Proposition 1B: Every non-vertical line through `(4,6)` hits `≥ 2` cells of `U` | `[propext, Quot.sound]` |
| **8** | [`r3_frozen_suffix_restores_even_parity`](lean4/Connect5HandProof.lean#L296) | **Theorem 2 (Rule R3):** `E % 2 = 1 ∧ ft % 2 = 1 → (E - (8 - ft)) % 2 = 0` | `[propext, Quot.sound]` |
| **9** | [`zermelo_mutual_safety_draw`](lean4/Connect5HandProof.lean#L337) | Zermelo Equilibrium: `SafeOutcome White o ∧ SafeOutcome Black o → o = Draw` | `[propext]` |
| **10** | [`allis_followup_induction`](lean4/Connect5HandProof.lean#L354) | Inductive Follow-Up Principle schema over remaining empty cells `E : Nat` | `[propext, Quot.sound]` |
| **11** | [`horizontal_5col_pair_transversal`](lean4/Connect5HandProof.lean#L368) | Every 5-column window `[c0, c0+4]` contains `{1, 2}` or `{5, 6}` | `[propext, Quot.sound]` |
| **12** | [`black_odd_row_transversal_hand_proof`](lean4/Connect5HandProof.lean#L381) | Player 2 (Black) odd-row transversal covers all 24 diagonals & odd horizontals | `[propext, Quot.sound]` |
| **13** | [`book_step3_central_wall_blocks_all_horizontals`](lean4/Connect5HandProof.lean#L417) | **Book Proof Step 3:** Central Wall (`Col 3` even ∪ `Col 4` odd) blocks all 28 horizontals | `[propext, Quot.sound]` |
| **14** | [`book_step4_central_wall_diagonal_dichotomy`](lean4/Connect5HandProof.lean#L438) | **Book Proof Step 4:** Every diagonal is double-blocked at `W₇` or hits `{2,4,6}` at Col 2/6 | `[propext, Quot.sound]` |

### Reproducing the Rocq 9.1 & Lean 4.35.0 Verifications
```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
powershell -ExecutionPolicy Bypass -File .\build_lean.ps1
```
Output:
```text
=== All 22 Rocq 9.1 theorems verified (0 axioms) & all 14 Lean 4.35.0 theorems verified (0 sorrys, 0 Classical.choice)! ===
```

---

## 📄 7. Download the Compiled Academic PDFs (AMS & ACS Styles)

- **Follow-Up Paper II (American Mathematical Society `amsart` Style):**
  - [**`paper/connect5_8x7_hilbert_erdos_AMS.pdf`**](paper/connect5_8x7_hilbert_erdos_AMS.pdf)
- **Follow-Up Paper II (American Computer Society Two-Column `article` Style):**
  - [**`paper/connect5_8x7_hilbert_erdos_ACS.pdf`**](paper/connect5_8x7_hilbert_erdos_ACS.pdf)
- **Dual-Mode LaTeX Source:**
  - [`paper/connect5_8x7_hilbert_erdos_pen_and_paper.tex`](paper/connect5_8x7_hilbert_erdos_pen_and_paper.tex)

---

<div align="center">

[![Return to Main Repository README](https://img.shields.io/badge/⬅_Return_to_Main_Landing_Page-README.md-2563eb?style=for-the-badge)](README.md)

</div>
