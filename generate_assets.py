# Script to generate crisp, professional SVG diagrams for the GitHub landing page
import os

os.makedirs("assets", exist_ok=True)

# 1. assets/board_structure.svg
svg_board = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 620" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="boardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e40af"/>
      <stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
    <radialGradient id="whiteStone" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="70%" stop-color="#e2e8f0"/>
      <stop offset="100%" stop-color="#94a3b8"/>
    </radialGradient>
    <radialGradient id="guaranteedWhite" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#67e8f9"/>
      <stop offset="60%" stop-color="#06b6d4"/>
      <stop offset="100%" stop-color="#0891b2"/>
    </radialGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="920" height="620" rx="16" fill="url(#bgGrad)"/>

  <!-- Title -->
  <text x="460" y="42" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="22" font-weight="700" fill="#f8fafc" text-anchor="middle">
    Connect-5 (8x7 Grid): 27-Pair Symmetric First-Player Defense
  </text>
  <text x="460" y="68" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="13" fill="#94a3b8" text-anchor="middle">
    White Opening at (3,0) + 24 Vertical Dominoes + 3 Row-0 Cross Pairs + Dead Cell at (4,6)
  </text>

  <!-- Board Frame -->
  <rect x="70" y="90" width="560" height="490" rx="12" fill="url(#boardGrad)" stroke="#3b82f6" stroke-width="2"/>

  <!-- Grid & Cells -->
  <!-- Columns 0..7 (width 70 each), Rows 0..6 (height 70 each, bottom=0) -->
"""

# Draw grid cells
for c in range(8):
    for r in range(7):
        cx = 70 + c * 70 + 35
        cy = 90 + (6 - r) * 70 + 35
        if c == 3 and r == 0:
            # White opening stone
            svg_board += f'  <!-- (3,0) White opening -->\n'
            svg_board += f'  <circle cx="{cx}" cy="{cy}" r="27" fill="url(#whiteStone)" filter="url(#glow)" stroke="#38bdf8" stroke-width="3"/>\n'
            svg_board += f'  <text x="{cx}" y="{cy+6}" font-family="sans-serif" font-size="16" font-weight="900" fill="#0f172a" text-anchor="middle">W₀</text>\n'
        elif c == 4 and r == 6:
            # Dead cell (4, 6)
            svg_board += f'  <!-- (4,6) Dead cell -->\n'
            svg_board += f'  <circle cx="{cx}" cy="{cy}" r="26" fill="#450a0a" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="4,4"/>\n'
            svg_board += f'  <text x="{cx}" y="{cy+6}" font-family="sans-serif" font-size="15" font-weight="800" fill="#f87171" text-anchor="middle">DEAD</text>\n'
        else:
            # Check if this is a White guaranteed upper cell:
            # Col 4 uppers: rows 1, 3, 5
            # Col 3 uppers: rows 2, 4, 6
            # Other cols: rows 2, 4, 6
            is_guaranteed = False
            if c == 4 and r in [1, 3, 5]: is_guaranteed = True
            elif c == 3 and r in [2, 4, 6]: is_guaranteed = True
            elif c in [0, 1, 2, 5, 6, 7] and r in [2, 4, 6]: is_guaranteed = True

            if is_guaranteed:
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="25" fill="url(#guaranteedWhite)" opacity="0.9" stroke="#e0f2fe" stroke-width="1.5"/>\n'
                svg_board += f'  <text x="{cx}" y="{cy+5}" font-family="sans-serif" font-size="13" font-weight="700" fill="#ffffff" text-anchor="middle">W*</text>\n'
            elif r == 0 and c in [0, 1, 2, 5, 6, 7]:
                # Cross-pair cells
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="25" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>\n'
                svg_board += f'  <text x="{cx}" y="{cy+5}" font-family="sans-serif" font-size="12" font-weight="700" fill="#fbbf24" text-anchor="middle">P{min(c, 7-c)+1}</text>\n'
            else:
                # Lower cell of vertical domino
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="25" fill="#0f172a" stroke="#475569" stroke-width="1.5"/>\n'
                svg_board += f'  <text x="{cx}" y="{cy+4}" font-family="sans-serif" font-size="11" fill="#64748b" text-anchor="middle">{c},{r}</text>\n'

# Add column & row headers
for c in range(8):
    svg_board += f'  <text x="{70 + c*70 + 35}" y="{82}" font-family="sans-serif" font-size="13" font-weight="700" fill="#93c5fd" text-anchor="middle">Col {c}</text>\n'
for r in range(7):
    svg_board += f'  <text x="{52}" y="{90 + (6-r)*70 + 40}" font-family="sans-serif" font-size="13" font-weight="700" fill="#93c5fd" text-anchor="middle">r{r}</text>\n'

# Draw row-0 cross pair arches: (0,0)-(7,0), (1,0)-(6,0), (2,0)-(5,0)
svg_board += """
  <!-- Row 0 Cross-Pair Arcs -->
  <path d="M 105 575 C 105 605, 595 605, 595 575" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4"/>
  <path d="M 175 575 C 175 595, 525 595, 525 575" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4"/>
  <path d="M 245 575 C 245 587, 455 587, 455 575" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4"/>

  <!-- Legend Card on the right -->
  <rect x="655" y="90" width="235" height="490" rx="12" fill="#1e293b" stroke="#334155" stroke-width="1.5"/>
  <text x="772" y="125" font-family="sans-serif" font-size="16" font-weight="700" fill="#f8fafc" text-anchor="middle">Strategy Legend</text>

  <!-- W0 -->
  <circle cx="685" cy="165" r="15" fill="url(#whiteStone)" stroke="#38bdf8" stroke-width="2"/>
  <text x="712" y="170" font-family="sans-serif" font-size="13" font-weight="700" fill="#f8fafc">W₀: White Opening (3,0)</text>

  <!-- W* -->
  <circle cx="685" cy="215" r="15" fill="url(#guaranteedWhite)" stroke="#e0f2fe" stroke-width="1.5"/>
  <text x="712" y="215" font-family="sans-serif" font-size="13" font-weight="700" fill="#67e8f9">W*: Guaranteed White</text>
  <text x="712" y="232" font-family="sans-serif" font-size="11" fill="#94a3b8">Upper of rigid domino</text>

  <!-- P1..P3 -->
  <circle cx="685" cy="275" r="15" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
  <text x="712" y="275" font-family="sans-serif" font-size="13" font-weight="700" fill="#fbbf24">P₁..P₃: Row-0 Pairs</text>
  <text x="712" y="292" font-family="sans-serif" font-size="11" fill="#94a3b8">3 Cross pairs (0-7, 1-6, 2-5)</text>

  <!-- DEAD -->
  <circle cx="685" cy="335" r="15" fill="#450a0a" stroke="#ef4444" stroke-width="2" stroke-dasharray="3,3"/>
  <text x="712" y="335" font-family="sans-serif" font-size="13" font-weight="700" fill="#f87171">Dead Cell: (4, 6)</text>
  <text x="712" y="352" font-family="sans-serif" font-size="11" fill="#94a3b8">Black cannot win through it</text>

  <!-- Stats Box -->
  <rect x="670" y="380" width="205" height="180" rx="8" fill="#0f172a" stroke="#3b82f6" stroke-width="1"/>
  <text x="772" y="405" font-family="sans-serif" font-size="13" font-weight="700" fill="#38bdf8" text-anchor="middle">Mathematical Audit</text>
  <text x="682" y="432" font-family="sans-serif" font-size="12" fill="#cbd5e1">Total Board Cells: 56</text>
  <text x="682" y="455" font-family="sans-serif" font-size="12" fill="#cbd5e1">Winning Lines: 76</text>
  <text x="682" y="478" font-family="sans-serif" font-size="12" fill="#4ade80" font-weight="700">Uncovered Lines: 0</text>
  <text x="682" y="501" font-family="sans-serif" font-size="12" fill="#cbd5e1">Lines through (4,6): 6</text>
  <text x="682" y="524" font-family="sans-serif" font-size="12" fill="#4ade80">Guaranteed White in (4,6): ≥2</text>
  <text x="682" y="547" font-family="sans-serif" font-size="11" fill="#38bdf8" font-weight="700">Result: Absolute Draw</text>
</svg>
"""

with open("assets/board_structure.svg", "w", encoding="utf-8") as f:
    f.write(svg_board)

# 2. assets/architecture_pipeline.svg
svg_pipeline = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 400" width="100%" height="100%">
  <defs>
    <linearGradient id="bgP" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="boxRocq" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
    <linearGradient id="boxGPU" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#065f46"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="boxCert" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#701a75"/>
      <stop offset="100%" stop-color="#a21caf"/>
    </linearGradient>
    <linearGradient id="boxFair" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#854d0e"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>
    </marker>
  </defs>

  <rect width="920" height="400" rx="16" fill="url(#bgP)"/>

  <text x="460" y="38" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="20" font-weight="700" fill="#f8fafc" text-anchor="middle">
    Dual Verification &amp; GPU Strategy Architecture in Rocq 9.1
  </text>

  <!-- Step 1: Trusted Theory -->
  <rect x="40" y="80" width="250" height="120" rx="10" fill="url(#boxRocq)" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="165" y="108" font-family="sans-serif" font-size="15" font-weight="700" fill="#ffffff" text-anchor="middle">1. Trusted Semantics</text>
  <text x="165" y="132" font-family="sans-serif" font-size="12" fill="#bfdbfe" text-anchor="middle">C5Game.v, C5Board.v</text>
  <text x="165" y="152" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• 76 Winning Lines Formalized</text>
  <text x="165" y="172" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Inductive safe Predicate</text>
  <text x="165" y="188" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Zero Axioms / Zero Admits</text>

  <!-- Step 2: Allis Pairing Theory -->
  <rect x="40" y="240" width="250" height="120" rx="10" fill="url(#boxRocq)" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="165" y="268" font-family="sans-serif" font-size="15" font-weight="700" fill="#ffffff" text-anchor="middle">2. Allis Pairing Theory</text>
  <text x="165" y="292" font-family="sans-serif" font-size="12" fill="#bfdbfe" text-anchor="middle">C5Rules.v, C5Principle.v</text>
  <text x="165" y="312" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Strong Dominoes &amp; Rigid Chains</text>
  <text x="165" y="332" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Base Pairs &amp; Frozen Threats</text>
  <text x="165" y="348" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Well-Founded Induction (empties)</text>

  <!-- Step 3: GPU Search Oracle -->
  <rect x="340" y="80" width="250" height="120" rx="10" fill="url(#boxGPU)" stroke="#34d399" stroke-width="1.5"/>
  <text x="465" y="108" font-family="sans-serif" font-size="15" font-weight="700" fill="#ffffff" text-anchor="middle">3. GPU Search Engine</text>
  <text x="465" y="132" font-family="sans-serif" font-size="12" fill="#a7f3d0" text-anchor="middle">c5_gpu_search.cu (RTX 4060)</text>
  <text x="465" y="152" font-family="sans-serif" font-size="11" fill="#ecfdf5" text-anchor="middle">• 405.35M Board Evals / Sec</text>
  <text x="465" y="172" font-family="sans-serif" font-size="11" fill="#ecfdf5" text-anchor="middle">• 64-Bit Bitboard Registers</text>
  <text x="465" y="188" font-family="sans-serif" font-size="11" fill="#ecfdf5" text-anchor="middle">• Clang 23 &amp; CUDA 13.5</text>

  <!-- Step 4: Certificate Checker -->
  <rect x="340" y="240" width="250" height="120" rx="10" fill="url(#boxCert)" stroke="#f472b6" stroke-width="1.5"/>
  <text x="465" y="268" font-family="sans-serif" font-size="15" font-weight="700" fill="#ffffff" text-anchor="middle">4. Verified Checker</text>
  <text x="465" y="292" font-family="sans-serif" font-size="12" fill="#fbcfe8" text-anchor="middle">C5CertChecker.v (Reflection)</text>
  <text x="465" y="312" font-family="sans-serif" font-size="11" fill="#fdf2f8" text-anchor="middle">• Compact DAG Certificate</text>
  <text x="465" y="332" font-family="sans-serif" font-size="11" fill="#fdf2f8" text-anchor="middle">• check_static Reflection</text>
  <text x="465" y="348" font-family="sans-serif" font-size="11" fill="#fdf2f8" text-anchor="middle">• Verified via vm_compute (&lt;2s)</text>

  <!-- Step 5: Master Theorem (Game Value = Draw) -->
  <rect x="640" y="160" width="240" height="120" rx="10" fill="url(#boxFair)" stroke="#fbbf24" stroke-width="2"/>
  <text x="760" y="195" font-family="sans-serif" font-size="16" font-weight="800" fill="#ffffff" text-anchor="middle">5. Final Theorem</text>
  <text x="760" y="222" font-family="sans-serif" font-size="13" font-weight="700" fill="#fef08a" text-anchor="middle">connect5_8x7_fair</text>
  <text x="760" y="248" font-family="sans-serif" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">game_value = Draw</text>
  <text x="760" y="268" font-family="sans-serif" font-size="11" fill="#fef9c3" text-anchor="middle">Closed under global context</text>

  <!-- Connectors -->
  <line x1="290" y1="140" x2="335" y2="140" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="290" y1="300" x2="335" y2="300" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="465" y1="200" x2="465" y2="235" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="590" y1="220" x2="635" y2="220" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)"/>
</svg>
"""

with open("assets/architecture_pipeline.svg", "w", encoding="utf-8") as f:
    f.write(svg_pipeline)

# 3. assets/benchmark_chart.svg
svg_bench = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 380" width="100%" height="100%">
  <defs>
    <linearGradient id="bgB" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="barGpu" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10b981"/>
      <stop offset="100%" stop-color="#34d399"/>
    </linearGradient>
    <linearGradient id="barClang" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#60a5fa"/>
    </linearGradient>
    <linearGradient id="barGcc" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#818cf8"/>
    </linearGradient>
    <linearGradient id="barBase" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#64748b"/>
      <stop offset="100%" stop-color="#94a3b8"/>
    </linearGradient>
  </defs>

  <rect width="920" height="380" rx="16" fill="url(#bgB)"/>

  <text x="460" y="38" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="20" font-weight="700" fill="#f8fafc" text-anchor="middle">
    Throughput Benchmark: CPU vs Clang vs NVIDIA RTX 4060 GPU
  </text>
  <text x="460" y="60" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">
    Logarithmic scale of board evaluations per second
  </text>

  <!-- Chart Axis & Labels -->
  <!-- Bar 1: Baseline CPU -->
  <text x="240" y="105" font-family="sans-serif" font-size="13" font-weight="700" fill="#cbd5e1" text-anchor="end">Baseline CPU (GCC 13)</text>
  <rect x="250" y="88" width="55" height="26" rx="4" fill="url(#barBase)"/>
  <text x="315" y="106" font-family="sans-serif" font-size="12" fill="#94a3b8">10,000 /s (1.0x)</text>

  <!-- Bar 2: pdfpn_fast (GCC 20 threads) -->
  <text x="240" y="160" font-family="sans-serif" font-size="13" font-weight="700" fill="#cbd5e1" text-anchor="end">pdfpn_fast (GCC 20T)</text>
  <rect x="250" y="143" width="130" height="26" rx="4" fill="url(#barGcc)"/>
  <text x="390" y="161" font-family="sans-serif" font-size="12" fill="#a5b4fc">90,000 /s (9.0x)</text>

  <!-- Bar 3: Native Clang 23 (20 threads) -->
  <text x="240" y="215" font-family="sans-serif" font-size="13" font-weight="700" fill="#cbd5e1" text-anchor="end">Native Clang 23 (20T)</text>
  <rect x="250" y="198" width="180" height="26" rx="4" fill="url(#barClang)"/>
  <text x="440" y="216" font-family="sans-serif" font-size="12" fill="#93c5fd" font-weight="700">210,000 /s (21.0x)</text>

  <!-- Bar 4: Single-Thread Clang White Search -->
  <text x="240" y="270" font-family="sans-serif" font-size="13" font-weight="700" fill="#cbd5e1" text-anchor="end">Clang Threat-Heuristic</text>
  <rect x="250" y="253" width="240" height="26" rx="4" fill="url(#barClang)"/>
  <text x="500" y="271" font-family="sans-serif" font-size="12" fill="#93c5fd">430,000 /s (43.0x)</text>

  <!-- Bar 5: NVIDIA RTX 4060 GPU (CUDA) -->
  <text x="240" y="325" font-family="sans-serif" font-size="14" font-weight="800" fill="#34d399" text-anchor="end">RTX 4060 GPU (CUDA 13.5)</text>
  <rect x="250" y="308" width="540" height="28" rx="4" fill="url(#barGpu)"/>
  <text x="800" y="327" font-family="sans-serif" font-size="13" font-weight="800" fill="#34d399">405,350,000 /s (~40,535x)</text>
</svg>
"""

with open("assets/benchmark_chart.svg", "w", encoding="utf-8") as f:
    f.write(svg_bench)

print("Generated 3 SVG visual assets in assets/ successfully!")
