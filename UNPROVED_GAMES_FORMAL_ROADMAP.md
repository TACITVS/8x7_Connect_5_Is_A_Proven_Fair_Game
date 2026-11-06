# Formal Verification Roadmap: Solved Combinatorial Games Awaiting Machine Proof

[![Back to Main Repository](https://img.shields.io/badge/⬅_Back_to_Main_Landing_Page-README.md-2563eb?style=for-the-badge)](README.md)
[![Follow-Up Paper II](https://img.shields.io/badge/📘_Paper_II-Hilbert--Erdős_Book_Proof-8b5cf6?style=for-the-badge)](HILBERT_ERDOS_PEN_AND_PAPER_PROOF.md)
[![Appendix Note](https://img.shields.io/badge/🎲_Appendix-Classic_7x6_Connect--4-ec4899?style=for-the-badge)](APPENDIX_CLASSIC_CONNECT4_7x6.md)

> **Abstract:** Between 1980 and 2026, computer scientists and combinatorial game theorists resolved the exact game-theoretic values of over a dozen classic board games. However, virtually **every single one of these historic solutions relies on unverified C/C++ code, ad-hoc retrograde databases, or proprietary mainframe scripts**. None of them had been formally mechanized inside interactive theorem provers (Rocq/Coq, Lean 4, or Isabelle/HOL).
>
> Following our complete machine-checked formal proof of **8x7 Connect-5 (`game_value = Draw`)**, this document provides a comprehensive scientific catalog and execution roadmap of famous solved board games awaiting zero-axiom deductive formalization.

---

## 1. Summary Catalog of Solved Board Games Awaiting Formal Verification

| Board Game | Dimensions / State Space | Game-Theoretic Value | Original Computational Solver | Formal Theorem Prover Status | Core Mathematical Structure |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **Nine Men's Morris (Mill)** | 24 points (10^10 states) | **Exact Draw** | Ralph Gasser (1993, ETH Zurich) | ❌ **Unverified** | 3-Phase DAG Retrograde Induction, D4 Dihedral Symmetry |
| **Classic Connect-Four** | 7x6 grid (4.53 x 10^12) | **Win White (P1)** | Allen (1988), Allis (1988), Tromp (1995) | ❌ **Unverified** | Claimeven (57/69 lines), Center Column 3 Pigeonhole, Odd-Threat Zugzwang |
| **Even-Height Connect-Four** | 6x6, 8x6, 8x8 | **Win Black (P2)** | John Tromp (1995–2015) | ❌ **Unverified** | Parity Inversion, Strong Domino Traps, Zugzwang Exploitation |
| **Qubic (3D Connect-Four)** | 4x4x4 (10^13 states) | **Win White (P1)** | Patashnik (1980), Allis (1994) | ❌ **Unverified** | 64-Bit Exact Hardware Saturation, 76 Winning Lines, VCF/VCT Search |
| **Quarto** | 4x4 grid (16 pieces) | **Exact Draw** | Luc Goossens (1998) | ❌ **Unverified** | (Z_2)^4 Affine Hypercube Symmetry, Lean 4 Quotient Types |
| **Pentago** | 6x6 (4 rotating quadrants) | **Win White (P1)** | Geoffrey Irving (2014) | ❌ **Unverified** | D4 Symmetries + 90-degree Quadrant Rotations, Retrograde Databases |
| **Freestyle Gomoku** | 15x15 (10^105 states) | **Win White (P1)** | Victor Allis (1993 PhD Thesis) | ❌ **Unverified** | Inductive Threat-Space Search (VCF / VCT), Proof-Number Search |
| **Hex (7x7 and 8x8)** | 49 and 64 cells | **Win White (P1)** | Hayward, Henderson et al. (2002) | ❌ **Unverified** | Virtual Connection H-Search, Resistance Networks, Carrier Sets |
| **Chomp (3xn and nxn)** | Arbitrary rectangular grid | **Win White (P1)** | David Gale (1974), Zeilberger (2001) | ❌ **Unverified** | Poset Ideal Games, Constructive Winning First-Move Formulas |
| **Domineering (6x6 and 8x8)** | Grid tiling by 2x1 dominoes | **Partisan Values** | Conway (1976), Bullock (2002) | ❌ **Unverified** | Combinatorial Game Theory, Surreal Numbers, Dyadic Rational Values |

---

## 2. In-Depth Analysis by Game Category

### Category A: Connection & Gravity Games (Direct Extension of Our Repository)
1. **Classic Connect-Four (7x6, k = 4):**
   - *State Space:* 4,531,985,219,092 positions (100 times smaller than 8x7 Connect-5).
   - *Bitboard:* 7 columns of 7 bits (6 active + 1 sentinel) = 49 bits, fitting within a single `uint64_t`.
   - *Book Proof:* As proved in our Appendix ([`APPENDIX_CLASSIC_CONNECT4_7x6.md`](APPENDIX_CLASSIC_CONNECT4_7x6.md)), pure Claimeven double-blocks 57 of the 69 winning lines (82.6%) at Move 0, while the single center column c = 3 crosses all 12 remaining horizontal lines!
2. **Even-Height Connect-Four (6x6 and 8x6):**
   - Proves John Tromp's counterintuitive theorem: when column height is even, the **second player wins** because Player 1 is forced to move first into the bottom cell of an even-length column, surrendering the upper response cell to Player 2 across the entire board.
3. **Qubic (4x4x4 3D Connect-Four):**
   - Exactly 64 board cells (zero wasted bits in a 64-bit word) and exactly 76 winning lines (the exact same number of lines as 8x7 Connect-5).
   - Solved by Oren Patashnik (1980) on Bell Labs mainframes using 1,500 hours; re-solved by Victor Allis (1994) using Threat-Space Search.

### Category B: Classical Antiquity & Symmetry-Rich Board Games
1. **Nine Men's Morris (Mill / Merels):**
   - One of the oldest board games in human history, dating back to at least 1400 BC (carved into the roof of the temple at Kurna, Egypt).
   - Solved as an **Exact Draw** by Ralph Gasser (1993, ETH Zurich) under Juerg Nievergelt.
   - 24 vertices and 16 mills. State space is approximately 10^10 positions, partitioned into 3 distinct phases: Placement (18 plies), Movement, and Flying.
   - 24 vertices fit into 24-bit bitboards (48 bits for both players in a single 64-bit integer), with D4 dihedral symmetry reduction (8-fold).
2. **Pentago (6x6 with 4 Rotating Quadrants):**
   - Invented in 2004 by Tomas Floden; solved as a First-Player Win in 2014 by Geoffrey Irving using Cray supercomputers (3.0 x 10^15 states reduced to 4.0 x 10^9 symmetric states).
   - After each stone placement, the player rotates one of the four 3x3 sub-grids 90 degrees clockwise or counterclockwise.
3. **Quarto:**
   - 16 distinct pieces characterized by 4 binary properties: (tall/short, red/blue, square/circular, hollow/solid).
   - The unique twist: the moving player chooses which piece the *opponent* must place on the board.
   - Solved as an Exact Draw by Luc Goossens (1998).

### Category C: Combinatorial Game Theory & Poset Games
1. **Chomp:**
   - John Nash's classic Strategy-Stealing argument proves that Player 1 must have a winning first move, but the proof is completely non-constructive (it does not tell you which square of chocolate to eat!).
   - Explicit winning strategies are only known for 2xn, 3xn, and nxn boards.
2. **Domineering:**
   - Invented by Goeran Andersson and featured by John Horton Conway in *On Numbers and Games* (1976) and Berlekamp, Conway, and Guy in *Winning Ways for your Mathematical Plays* (1982).
   - Evaluates directly to Conway numbers (+1, -1/2, *).

---

## 3. Next Project: Nine Men's Morris (Mill)

We select **Nine Men's Morris** as our immediate next formal verification project. Its complete 3-phase lifecycle, 24-point topology, and 16-mill structure make it the ideal bridge between pure pen-and-paper algebra and formal retrograde certificate verification.
