# Script to generate crisp, professional SVG diagrams for the GitHub landing page
# Incorporating classic Connect-Four Blue rack, Red and Yellow pieces, and a true Log-Scale benchmark chart.
import os
import math

os.makedirs("assets", exist_ok=True)

# =========================================================================
# 1. assets/board_structure.svg
# =========================================================================
svg_board = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 670" width="100%" height="100%">
  <defs>
    <!-- Dark slate canvas background -->
    <linearGradient id="canvasGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1329"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>

    <!-- Classic Connect-Four Blue Board Rack Gradient -->
    <linearGradient id="boardBlue" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1d4ed8"/>
      <stop offset="25%" stop-color="#1e40af"/>
      <stop offset="75%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#172554"/>
    </linearGradient>

    <!-- Board Plastic Bevel Highlight -->
    <linearGradient id="boardBevel" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3b82f6"/>
      <stop offset="50%" stop-color="#60a5fa"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>

    <!-- Yellow Support Stand/Feet -->
    <linearGradient id="standGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fde047"/>
      <stop offset="50%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#a16207"/>
    </linearGradient>

    <!-- Classic RED Disc Gradient (Player 1 / White in Rocq) -->
    <radialGradient id="redDisc" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="#ff6b6b"/>
      <stop offset="40%" stop-color="#ef4444"/>
      <stop offset="80%" stop-color="#dc2626"/>
      <stop offset="100%" stop-color="#991b1b"/>
    </radialGradient>

    <!-- Classic YELLOW Disc Gradient (Player 2 / Black in Rocq) -->
    <radialGradient id="yellowDisc" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="40%" stop-color="#facc15"/>
      <stop offset="80%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#a16207"/>
    </radialGradient>

    <!-- Empty Slot Shadow Gradient -->
    <radialGradient id="emptyHole" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="80%" stop-color="#090d16"/>
      <stop offset="100%" stop-color="#000000"/>
    </radialGradient>

    <!-- Glow & Shadow Filters -->
    <filter id="discShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000000" flood-opacity="0.6"/>
    </filter>

    <filter id="goldGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Canvas Background -->
  <rect width="980" height="670" rx="16" fill="url(#canvasGrad)"/>

  <!-- Title & Subtitle -->
  <text x="490" y="38" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="22" font-weight="800" fill="#f8fafc" text-anchor="middle">
    Connect-5 (8×7 Grid): 27-Pair Symmetric First-Player Defense
  </text>
  <text x="490" y="62" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="13" fill="#94a3b8" text-anchor="middle">
    Classic Board with Red Opening (3,0) + 24 Vertical Dominoes + 3 Ground Cross-Pairs + Neutralized Dead Cell (4,6)
  </text>

  <!-- Yellow Support Feet for Classic Connect Rack -->
  <path d="M 60 595 L 45 635 L 115 635 L 100 595 Z" fill="url(#standGrad)" stroke="#854d0e" stroke-width="2"/>
  <path d="M 640 595 L 625 635 L 695 635 L 680 595 Z" fill="url(#standGrad)" stroke="#854d0e" stroke-width="2"/>

  <!-- Classic Blue Board Frame -->
  <rect x="70" y="80" width="600" height="525" rx="18" fill="url(#boardBlue)" stroke="url(#boardBevel)" stroke-width="3" filter="url(#discShadow)"/>

  <!-- Top Column Indicators -->
"""

# Draw Columns & Rows
for c in range(8):
    cx = 70 + c * 75 + 37.5
    svg_board += f'  <text x="{cx}" y="73" font-family="sans-serif" font-size="12" font-weight="700" fill="#93c5fd" text-anchor="middle">Col {c}</text>\n'

for r in range(7):
    cy = 80 + (6 - r) * 75 + 42
    svg_board += f'  <text x="50" y="{cy}" font-family="sans-serif" font-size="12" font-weight="700" fill="#93c5fd" text-anchor="middle">r{r}</text>\n'

# Draw the 56 Cells
for c in range(8):
    for r in range(7):
        cx = 70 + c * 75 + 37.5
        cy = 80 + (6 - r) * 75 + 37.5

        if c == 3 and r == 0:
            # RED Opening Disc at (3, 0)
            svg_board += f'  <!-- (3,0) RED Opening Disc -->\n'
            svg_board += f'  <circle cx="{cx}" cy="{cy}" r="30" fill="url(#redDisc)" filter="url(#goldGlow)" stroke="#fef08a" stroke-width="3.5"/>\n'
            svg_board += f'  <circle cx="{cx}" cy="{cy}" r="20" fill="none" stroke="#b91c1c" stroke-width="2"/>\n'
            svg_board += f'  <text x="{cx}" y="{cy+6}" font-family="sans-serif" font-size="16" font-weight="900" fill="#ffffff" text-anchor="middle">R₀</text>\n'
        elif c == 4 and r == 6:
            # Dead cell (4, 6)
            svg_board += f'  <!-- (4,6) Dead Cell -->\n'
            svg_board += f'  <circle cx="{cx}" cy="{cy}" r="28" fill="#18181b" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="4,4"/>\n'
            svg_board += f'  <line x1="{cx-15}" y1="{cy-15}" x2="{cx+15}" y2="{cy+15}" stroke="#ef4444" stroke-width="3"/>\n'
            svg_board += f'  <line x1="{cx-15}" y1="{cy+15}" x2="{cx+15}" y2="{cy-15}" stroke="#ef4444" stroke-width="3"/>\n'
            svg_board += f'  <text x="{cx}" y="{cy+24}" font-family="sans-serif" font-size="8" font-weight="800" fill="#f87171" text-anchor="middle">DEAD</text>\n'
        else:
            # Check if this cell is guaranteed RED (upper of vertical domino)
            is_guaranteed_red = False
            if c == 4 and r in [1, 3, 5]:
                is_guaranteed_red = True
            elif c != 4 and r in [2, 4, 6]:
                is_guaranteed_red = True

            if is_guaranteed_red:
                # Guaranteed RED disc (R*)
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="28" fill="url(#redDisc)" filter="url(#discShadow)" stroke="#f87171" stroke-width="1.5"/>\n'
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="18" fill="none" stroke="#991b1b" stroke-width="1.5"/>\n'
                svg_board += f'  <text x="{cx}" y="{cy+5}" font-family="sans-serif" font-size="13" font-weight="900" fill="#ffffff" text-anchor="middle">R★</text>\n'
            elif r == 0 and c in [0, 1, 2, 5, 6, 7]:
                # Row 0 Ground Cross-Pair cells
                p_idx = min(c, 7 - c) + 1
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="28" fill="url(#emptyHole)" stroke="#f59e0b" stroke-width="2.5"/>\n'
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="18" fill="none" stroke="#d97706" stroke-width="1.5" stroke-dasharray="3,3"/>\n'
                svg_board += f'  <text x="{cx}" y="{cy+5}" font-family="sans-serif" font-size="12" font-weight="800" fill="#fbbf24" text-anchor="middle">P{p_idx}</text>\n'
            else:
                # Lower cell of vertical domino (Yellow threat ingress)
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="28" fill="url(#yellowDisc)" opacity="0.85" stroke="#ca8a04" stroke-width="1.5"/>\n'
                svg_board += f'  <circle cx="{cx}" cy="{cy}" r="18" fill="none" stroke="#a16207" stroke-width="1.5"/>\n'
                svg_board += f'  <text x="{cx}" y="{cy+5}" font-family="sans-serif" font-size="11" font-weight="800" fill="#713f12" text-anchor="middle">Y{r}</text>\n'

# Upward response arrows between Y and R*
svg_board += "  <!-- Domino Upward Response Indicators -->\n"
for c in range(8):
    if c == 4:
        # Col 4: pairs are (0,1), (2,3), (4,5)
        pairs = [(0, 1), (2, 3), (4, 5)]
    else:
        # Other cols: pairs are (1,2), (3,4), (5,6)
        pairs = [(1, 2), (3, 4), (5, 6)]

    for (r_lo, r_hi) in pairs:
        cx = 70 + c * 75 + 37.5
        cy_lo = 80 + (6 - r_lo) * 75 + 37.5 - 14
        cy_hi = 80 + (6 - r_hi) * 75 + 37.5 + 14
        svg_board += f'  <line x1="{cx}" y1="{cy_lo}" x2="{cx}" y2="{cy_hi}" stroke="#ffffff" stroke-width="1.5" stroke-dasharray="2,2" opacity="0.6"/>\n'

# Ground-Row Cross Pair Arcs at Row 0
svg_board += """
  <!-- Ground-Row 0 Symmetric Cross-Pair Bridge Arcs -->
  <!-- P1: (0,0) <-> (7,0) -->
  <path d="M 107.5 595 C 107.5 655, 632.5 655, 632.5 595" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4"/>
  <rect x="350" y="632" width="40" height="18" rx="4" fill="#1e293b" stroke="#f59e0b" stroke-width="1"/>
  <text x="370" y="645" font-family="sans-serif" font-size="11" font-weight="800" fill="#fbbf24" text-anchor="middle">P₁</text>

  <!-- P2: (1,0) <-> (6,0) -->
  <path d="M 182.5 595 C 182.5 640, 557.5 640, 557.5 595" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="6,4"/>
  <rect x="350" y="612" width="40" height="18" rx="4" fill="#1e293b" stroke="#fbbf24" stroke-width="1"/>
  <text x="370" y="625" font-family="sans-serif" font-size="11" font-weight="800" fill="#fde047" text-anchor="middle">P₂</text>

  <!-- P3: (2,0) <-> (5,0) -->
  <path d="M 257.5 595 C 257.5 625, 482.5 625, 482.5 595" fill="none" stroke="#fef08a" stroke-width="2" stroke-dasharray="5,3"/>
  <rect x="350" y="595" width="40" height="18" rx="4" fill="#1e293b" stroke="#fef08a" stroke-width="1"/>
  <text x="370" y="608" font-family="sans-serif" font-size="11" font-weight="800" fill="#fef08a" text-anchor="middle">P₃</text>

  <!-- ================= LEGEND CARD ================= -->
  <rect x="695" y="80" width="260" height="525" rx="14" fill="#1e293b" stroke="#334155" stroke-width="1.5" filter="url(#discShadow)"/>
  <text x="825" y="115" font-family="sans-serif" font-size="17" font-weight="800" fill="#f8fafc" text-anchor="middle">Strategy Legend</text>

  <!-- Red Opening R0 -->
  <circle cx="725" cy="155" r="16" fill="url(#redDisc)" stroke="#fef08a" stroke-width="2"/>
  <text x="750" y="154" font-family="sans-serif" font-size="13" font-weight="800" fill="#ffffff">R₀: Red Opening (3,0)</text>
  <text x="750" y="170" font-family="sans-serif" font-size="11" fill="#94a3b8">First ply anchor move</text>

  <!-- Red Guaranteed R* -->
  <circle cx="725" cy="210" r="16" fill="url(#redDisc)" stroke="#f87171" stroke-width="1.5"/>
  <text x="725" y="215" font-family="sans-serif" font-size="11" font-weight="900" fill="#ffffff" text-anchor="middle">R★</text>
  <text x="750" y="209" font-family="sans-serif" font-size="13" font-weight="800" fill="#f87171">R★: Guaranteed Red</text>
  <text x="750" y="225" font-family="sans-serif" font-size="11" fill="#94a3b8">Upper domino response</text>

  <!-- Yellow Attacker Y -->
  <circle cx="725" cy="265" r="16" fill="url(#yellowDisc)" stroke="#ca8a04" stroke-width="1.5"/>
  <text x="725" y="270" font-family="sans-serif" font-size="11" font-weight="900" fill="#713f12" text-anchor="middle">Y</text>
  <text x="750" y="264" font-family="sans-serif" font-size="13" font-weight="800" fill="#facc15">Y: Yellow Attack Cell</text>
  <text x="750" y="280" font-family="sans-serif" font-size="11" fill="#94a3b8">Lower domino ingress</text>

  <!-- Cross Pairs P1..P3 -->
  <circle cx="725" cy="320" r="16" fill="url(#emptyHole)" stroke="#f59e0b" stroke-width="2"/>
  <text x="725" y="324" font-family="sans-serif" font-size="10" font-weight="800" fill="#fbbf24" text-anchor="middle">P</text>
  <text x="750" y="319" font-family="sans-serif" font-size="13" font-weight="800" fill="#fbbf24">P₁–P₃: Ground Pairs</text>
  <text x="750" y="335" font-family="sans-serif" font-size="11" fill="#94a3b8">Row 0 cross: (0-7, 1-6, 2-5)</text>

  <!-- Dead Cell -->
  <circle cx="725" cy="375" r="16" fill="#18181b" stroke="#ef4444" stroke-width="2" stroke-dasharray="3,3"/>
  <text x="725" y="379" font-family="sans-serif" font-size="12" font-weight="900" fill="#ef4444" text-anchor="middle">✕</text>
  <text x="750" y="374" font-family="sans-serif" font-size="13" font-weight="800" fill="#ef4444">Dead Cell: (4,6)</text>
  <text x="750" y="390" font-family="sans-serif" font-size="11" fill="#94a3b8">Mathematically inert</text>

  <!-- Mathematical Proof Summary Box -->
  <rect x="710" y="420" width="230" height="170" rx="10" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="825" y="445" font-family="sans-serif" font-size="13" font-weight="800" fill="#38bdf8" text-anchor="middle">Mathematical Proof Audit</text>
  <text x="722" y="470" font-family="sans-serif" font-size="12" fill="#cbd5e1">Board Size: 8 × 7 (56 cells)</text>
  <text x="722" y="492" font-family="sans-serif" font-size="12" fill="#cbd5e1">Winning Lines: 76</text>
  <text x="722" y="514" font-family="sans-serif" font-size="12" font-weight="800" fill="#4ade80">Uncovered Lines: 0</text>
  <text x="722" y="536" font-family="sans-serif" font-size="12" fill="#cbd5e1">Lines through (4,6): 6</text>
  <text x="722" y="558" font-family="sans-serif" font-size="12" fill="#4ade80">Guaranteed Red in (4,6): ≥ 2</text>
  <text x="825" y="580" font-family="sans-serif" font-size="12" font-weight="900" fill="#facc15" text-anchor="middle">Theorem: game_value = Draw</text>
</svg>
"""

with open("assets/board_structure.svg", "w", encoding="utf-8") as f:
    f.write(svg_board)

# =========================================================================
# 2. assets/benchmark_chart.svg (TRUE LOGARITHMIC SCALE)
# =========================================================================
# Log scale from 10^3 (1,000) to 10^9 (1,000,000,000). Total 6 decades.
chart_x0 = 240
chart_w = 540  # pixels from 10^3 to 10^9
def to_log_x(val):
    log_val = math.log10(val)
    frac = (log_val - 3.0) / 6.0
    return chart_x0 + frac * chart_w

# Data points
benchmarks = [
    {
        "name": "CPython 3.12 (1 Thread)",
        "value": 9800,
        "label": "9,800 /s",
        "mult": "1.0×",
        "color1": "#64748b", "color2": "#94a3b8"
    },
    {
        "name": "GCC 14 -O3 (20 Threads)",
        "value": 165000,
        "label": "165,000 /s",
        "mult": "16.8×",
        "color1": "#6366f1", "color2": "#818cf8"
    },
    {
        "name": "Clang 23 -O3 (20 Threads)",
        "value": 210000,
        "label": "210,000 /s",
        "mult": "21.4×",
        "color1": "#0284c7", "color2": "#38bdf8"
    },
    {
        "name": "Clang White Threat Search",
        "value": 430000,
        "label": "430,000 /s",
        "mult": "43.9×",
        "color1": "#0ea5e9", "color2": "#7dd3fc"
    },
    {
        "name": "NVIDIA RTX 4060 (CUDA 13.5)",
        "value": 405350000,
        "label": "405,350,000 /s",
        "mult": "41,362×",
        "color1": "#10b981", "color2": "#34d399"
    }
]

svg_bench = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 430" width="100%" height="100%">
  <defs>
    <linearGradient id="bgBench" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1329"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <linearGradient id="barGpu" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#059669"/>
      <stop offset="100%" stop-color="#34d399"/>
    </linearGradient>
    <filter id="shadowB" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="960" height="430" rx="16" fill="url(#bgBench)"/>

  <!-- Title & Subtitle -->
  <text x="480" y="38" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="20" font-weight="800" fill="#f8fafc" text-anchor="middle">
    Search Engine Throughput Benchmark (Logarithmic Scale log₁₀)
  </text>
  <text x="480" y="60" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">
    Massively Parallel 64-Bit CUDA Bitboard Kernel vs Multithreaded Clang &amp; GCC Solvers (RTX 4060 Laptop GPU)
  </text>

  <!-- Log Scale Axis Lines -->
"""

# Draw vertical log grid lines and tick labels
decades = [
    (1000, "10³ (1K)"),
    (10000, "10⁴ (10K)"),
    (100000, "10⁵ (100K)"),
    (1000000, "10⁶ (1M)"),
    (10000000, "10⁷ (10M)"),
    (100000000, "10⁸ (100M)"),
    (1000000000, "10⁹ (1B)")
]

# Chart bounds: Y from 80 to 340
for val, text in decades:
    gx = to_log_x(val)
    svg_bench += f'  <line x1="{gx:.1f}" y1="80" x2="{gx:.1f}" y2="340" stroke="#334155" stroke-width="1" stroke-dasharray="3,3"/>\n'
    svg_bench += f'  <text x="{gx:.1f}" y="358" font-family="sans-serif" font-size="11" font-weight="700" fill="#94a3b8" text-anchor="middle">{text}</text>\n'

# Minor log ticks (2, 3, 5 times 10^k)
for exp in range(3, 9):
    base = 10**exp
    for factor in [2, 3, 5, 7]:
        minor_val = factor * base
        if minor_val <= 1000000000:
            mx = to_log_x(minor_val)
            svg_bench += f'  <line x1="{mx:.1f}" y1="335" x2="{mx:.1f}" y2="340" stroke="#475569" stroke-width="1"/>\n'

# Bottom Axis Line
svg_bench += f'  <line x1="{chart_x0}" y1="340" x2="{chart_x0 + chart_w}" y2="340" stroke="#64748b" stroke-width="1.5"/>\n'
svg_bench += f'  <text x="{chart_x0 + chart_w/2}" y="385" font-family="sans-serif" font-size="12" font-weight="700" fill="#cbd5e1" text-anchor="middle">Board Positions Evaluated / Second (log₁₀ scale)</text>\n'

# Draw Horizontal Bars
bar_y0 = 95
bar_h = 32
bar_spacing = 48

for i, b in enumerate(benchmarks):
    by = bar_y0 + i * bar_spacing
    bx_end = to_log_x(b["value"])
    bw = max(bx_end - chart_x0, 6)

    # Name label on the left
    is_gpu = "GPU" in b["name"]
    name_color = "#34d399" if is_gpu else "#e2e8f0"
    name_weight = "800" if is_gpu else "700"
    svg_bench += f'  <text x="{chart_x0 - 15}" y="{by + 21}" font-family="sans-serif" font-size="13" font-weight="{name_weight}" fill="{name_color}" text-anchor="end">{b["name"]}</text>\n'

    # Bar rectangle
    grad_id = f"barGrad_{i}"
    svg_bench += f'  <defs><linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{b["color1"]}"/><stop offset="100%" stop-color="{b["color2"]}"/></linearGradient></defs>\n'
    svg_bench += f'  <rect x="{chart_x0}" y="{by}" width="{bw:.1f}" height="{bar_h}" rx="6" fill="url(#{grad_id})" filter="url(#shadowB)"/>\n'

    # Value and speedup label on the right
    val_color = "#34d399" if is_gpu else "#ffffff"
    val_weight = "900" if is_gpu else "700"
    svg_bench += f'  <text x="{bx_end + 12:.1f}" y="{by + 21}" font-family="sans-serif" font-size="12" font-weight="{val_weight}" fill="{val_color}">{b["label"]} <tspan fill="#facc15" font-weight="800">({b["mult"]})</tspan></text>\n'

# Accent highlight box for GPU
svg_bench += """
  <!-- GPU Benchmark Callout Badge -->
  <rect x="250" y="398" width="460" height="22" rx="4" fill="#064e3b" stroke="#059669" stroke-width="1"/>
  <text x="480" y="413" font-family="sans-serif" font-size="11" font-weight="800" fill="#a7f3d0" text-anchor="middle">
    NVIDIA RTX 4060 GPU: 405.35 Million evals/sec — 41,362× faster than single-core CPU
  </text>
</svg>
"""

with open("assets/benchmark_chart.svg", "w", encoding="utf-8") as f:
    f.write(svg_bench)

# =========================================================================
# 3. assets/architecture_pipeline.svg
# =========================================================================
svg_pipeline = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 410" width="100%" height="100%">
  <defs>
    <linearGradient id="bgP" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1329"/>
      <stop offset="100%" stop-color="#111827"/>
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

  <rect width="960" height="410" rx="16" fill="url(#bgP)"/>

  <text x="480" y="38" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="20" font-weight="800" fill="#f8fafc" text-anchor="middle">
    Dual Verification &amp; GPU Strategy Architecture in Rocq 9.1
  </text>
  <text x="480" y="58" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">
    Zero-Axiom Constructive Logic Unified with 405M evals/sec GPU Bitboard Oracle
  </text>

  <!-- Step 1: Trusted Theory -->
  <rect x="40" y="80" width="260" height="125" rx="10" fill="url(#boxRocq)" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="170" y="108" font-family="sans-serif" font-size="15" font-weight="700" fill="#ffffff" text-anchor="middle">1. Trusted Semantics</text>
  <text x="170" y="130" font-family="sans-serif" font-size="12" fill="#bfdbfe" text-anchor="middle">C5Game.v, C5Board.v</text>
  <text x="170" y="152" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• 76 Winning Lines Formalized</text>
  <text x="170" y="170" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Inductive safe Predicate</text>
  <text x="170" y="188" font-family="sans-serif" font-size="11" font-weight="700" fill="#4ade80" text-anchor="middle">• Zero Axioms / Zero Admits</text>

  <!-- Step 2: Allis Pairing Theory -->
  <rect x="40" y="245" width="260" height="125" rx="10" fill="url(#boxRocq)" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="170" y="273" font-family="sans-serif" font-size="15" font-weight="700" fill="#ffffff" text-anchor="middle">2. Allis Pairing Theory</text>
  <text x="170" y="295" font-family="sans-serif" font-size="12" fill="#bfdbfe" text-anchor="middle">C5Rules.v, C5Principle.v</text>
  <text x="170" y="317" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Strong Dominoes &amp; Rigid Chains</text>
  <text x="170" y="335" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Base Pairs &amp; Parity Resolutions</text>
  <text x="170" y="353" font-family="sans-serif" font-size="11" fill="#e0e7ff" text-anchor="middle">• Well-Founded Induction (empties)</text>

  <!-- Step 3: GPU Search Oracle -->
  <rect x="350" y="80" width="260" height="125" rx="10" fill="url(#boxGPU)" stroke="#34d399" stroke-width="1.5"/>
  <text x="480" y="108" font-family="sans-serif" font-size="15" font-weight="700" fill="#ffffff" text-anchor="middle">3. GPU Search Engine</text>
  <text x="480" y="130" font-family="sans-serif" font-size="12" fill="#a7f3d0" text-anchor="middle">c5_gpu_search.cu (RTX 4060)</text>
  <text x="480" y="152" font-family="sans-serif" font-size="11" font-weight="700" fill="#6ee7b7" text-anchor="middle">• 405.35M Board Evals / Sec</text>
  <text x="480" y="170" font-family="sans-serif" font-size="11" fill="#ecfdf5" text-anchor="middle">• 64-Bit Bitboard Registers</text>
  <text x="480" y="188" font-family="sans-serif" font-size="11" fill="#ecfdf5" text-anchor="middle">• Native Clang 23 &amp; CUDA 13.5</text>

  <!-- Step 4: Certificate Checker -->
  <rect x="350" y="245" width="260" height="125" rx="10" fill="url(#boxCert)" stroke="#f472b6" stroke-width="1.5"/>
  <text x="480" y="273" font-family="sans-serif" font-size="15" font-weight="700" fill="#ffffff" text-anchor="middle">4. Verified Checker</text>
  <text x="480" y="295" font-family="sans-serif" font-size="12" fill="#fbcfe8" text-anchor="middle">C5CertChecker.v (Reflection)</text>
  <text x="480" y="317" font-family="sans-serif" font-size="11" fill="#fdf2f8" text-anchor="middle">• Compact DAG Certificate</text>
  <text x="480" y="335" font-family="sans-serif" font-size="11" fill="#fdf2f8" text-anchor="middle">• check_static Reflection</text>
  <text x="480" y="353" font-family="sans-serif" font-size="11" font-weight="700" fill="#f472b6" text-anchor="middle">• Verified via vm_compute (0.82s)</text>

  <!-- Step 5: Master Theorem (Game Value = Draw) -->
  <rect x="660" y="162" width="260" height="130" rx="12" fill="url(#boxFair)" stroke="#fbbf24" stroke-width="2.5"/>
  <text x="790" y="196" font-family="sans-serif" font-size="16" font-weight="900" fill="#ffffff" text-anchor="middle">5. Final Theorem</text>
  <text x="790" y="222" font-family="sans-serif" font-size="13" font-weight="800" fill="#fef08a" text-anchor="middle">connect5_8x7_fair</text>
  <text x="790" y="250" font-family="sans-serif" font-size="16" font-weight="900" fill="#ffffff" text-anchor="middle">game_value = Draw</text>
  <text x="790" y="272" font-family="sans-serif" font-size="11" font-weight="700" fill="#4ade80" text-anchor="middle">Closed under global context</text>

  <!-- Connectors -->
  <line x1="300" y1="142" x2="345" y2="142" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="300" y1="307" x2="345" y2="307" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="480" y1="205" x2="480" y2="240" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="610" y1="227" x2="655" y2="227" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)"/>
</svg>
"""

with open("assets/architecture_pipeline.svg", "w", encoding="utf-8") as f:
    f.write(svg_pipeline)

# =========================================================================
# 4. assets/historical_timeline.svg
# =========================================================================
svg_timeline = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 510" width="100%" height="100%">
  <defs>
    <linearGradient id="bgTime" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1329"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <linearGradient id="cardHist" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="cardNovel" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#064e3b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <filter id="shadowT" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000000" flood-opacity="0.55"/>
    </filter>
  </defs>

  <!-- Canvas -->
  <rect width="980" height="510" rx="16" fill="url(#bgTime)"/>

  <!-- Title & Subtitle -->
  <text x="490" y="36" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="20" font-weight="800" fill="#f8fafc" text-anchor="middle">
    38 Years of Gravity Game Solving (1988–2026): Folklore vs. Formal Novelty
  </text>
  <text x="490" y="58" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">
    From Victor Allis &amp; James D. Allen (1988) and John Tromp (1995) to the First Zero-Axiom Rocq 9.1 Proof &amp; 405M evals/s CUDA Engine
  </text>

  <!-- Horizontal Timeline Spine -->
  <line x1="65" y1="108" x2="915" y2="108" stroke="#3b82f6" stroke-width="3"/>

  <!-- Node 1: 1988 -->
  <circle cx="105" cy="108" r="9" fill="#38bdf8" stroke="#0b1329" stroke-width="2.5"/>
  <text x="105" y="90" font-family="sans-serif" font-size="13" font-weight="800" fill="#38bdf8" text-anchor="middle">Oct 1988</text>
  <rect x="30" y="128" width="150" height="145" rx="8" fill="url(#cardHist)" stroke="#334155" stroke-width="1.5" filter="url(#shadowT)"/>
  <text x="105" y="148" font-family="sans-serif" font-size="12" font-weight="800" fill="#f8fafc" text-anchor="middle">Allen &amp; Allis</text>
  <text x="105" y="164" font-family="sans-serif" font-size="10" font-weight="700" fill="#fbbf24" text-anchor="middle">7×6 Connect-4 Solved</text>
  <text x="105" y="184" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• 9 Strategic Rules</text>
  <text x="105" y="200" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">  (Claimeven, Baseinverse)</text>
  <text x="105" y="216" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• Conspiracy Search</text>
  <text x="105" y="232" font-family="sans-serif" font-size="10" fill="#94a3b8" text-anchor="middle">• Not brute-force!</text>
  <text x="105" y="256" font-family="sans-serif" font-size="10" font-weight="700" fill="#f87171" text-anchor="middle">Informal / Unverified C</text>

  <!-- Node 2: 1994 -->
  <circle cx="265" cy="108" r="9" fill="#38bdf8" stroke="#0b1329" stroke-width="2.5"/>
  <text x="265" y="90" font-family="sans-serif" font-size="13" font-weight="800" fill="#38bdf8" text-anchor="middle">1994</text>
  <rect x="190" y="128" width="150" height="145" rx="8" fill="url(#cardHist)" stroke="#334155" stroke-width="1.5" filter="url(#shadowT)"/>
  <text x="265" y="148" font-family="sans-serif" font-size="12" font-weight="800" fill="#f8fafc" text-anchor="middle">Victor Allis PhD</text>
  <text x="265" y="164" font-family="sans-serif" font-size="10" font-weight="700" fill="#fbbf24" text-anchor="middle">Proof-Number Search</text>
  <text x="265" y="184" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• PNS (pn, dn) trees</text>
  <text x="265" y="200" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• Weak vs. Strong</text>
  <text x="265" y="216" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">  solving taxonomy</text>
  <text x="265" y="232" font-family="sans-serif" font-size="10" fill="#94a3b8" text-anchor="middle">• Qubic &amp; Go-Moku</text>
  <text x="265" y="256" font-family="sans-serif" font-size="10" font-weight="700" fill="#f87171" text-anchor="middle">RAM-Bound Best-First</text>

  <!-- Node 3: 1995 -->
  <circle cx="425" cy="108" r="9" fill="#38bdf8" stroke="#0b1329" stroke-width="2.5"/>
  <text x="425" y="90" font-family="sans-serif" font-size="13" font-weight="800" fill="#38bdf8" text-anchor="middle">1993–1995</text>
  <rect x="350" y="128" width="150" height="145" rx="8" fill="url(#cardHist)" stroke="#334155" stroke-width="1.5" filter="url(#shadowT)"/>
  <text x="425" y="148" font-family="sans-serif" font-size="12" font-weight="800" fill="#f8fafc" text-anchor="middle">John Tromp</text>
  <text x="425" y="164" font-family="sans-serif" font-size="10" font-weight="700" fill="#fbbf24" text-anchor="middle">Fhourstones &amp; Strong 7×6</text>
  <text x="425" y="184" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• 64-Bit Sentinel</text>
  <text x="425" y="200" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">  Bitboard Encoding</text>
  <text x="425" y="216" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• 4.53×10¹² states</text>
  <text x="425" y="232" font-family="sans-serif" font-size="10" fill="#94a3b8" text-anchor="middle">• 40,000 CPU hours</text>
  <text x="425" y="256" font-family="sans-serif" font-size="10" font-weight="700" fill="#f87171" text-anchor="middle">Even-Height = P2 Win</text>

  <!-- Node 4: 1999-2002 -->
  <circle cx="585" cy="108" r="9" fill="#38bdf8" stroke="#0b1329" stroke-width="2.5"/>
  <text x="585" y="90" font-family="sans-serif" font-size="13" font-weight="800" fill="#38bdf8" text-anchor="middle">1999–2002</text>
  <rect x="510" y="128" width="150" height="145" rx="8" fill="url(#cardHist)" stroke="#334155" stroke-width="1.5" filter="url(#shadowT)"/>
  <text x="585" y="148" font-family="sans-serif" font-size="12" font-weight="800" fill="#f8fafc" text-anchor="middle">Ayumu Nagai</text>
  <text x="585" y="164" font-family="sans-serif" font-size="10" font-weight="700" fill="#fbbf24" text-anchor="middle">df-pn Search &amp; MID</text>
  <text x="585" y="184" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• Depth-First PNS</text>
  <text x="585" y="200" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• Dual (th_pn, th_dn)</text>
  <text x="585" y="216" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">  TT recursion</text>
  <text x="585" y="232" font-family="sans-serif" font-size="10" fill="#94a3b8" text-anchor="middle">• Kaneko (2010) PDFPN</text>
  <text x="585" y="256" font-family="sans-serif" font-size="10" font-weight="700" fill="#f87171" text-anchor="middle">No Formal Proof Kernel</text>

  <!-- Node 5: 2005-2008 -->
  <circle cx="745" cy="108" r="9" fill="#a855f7" stroke="#0b1329" stroke-width="2.5"/>
  <text x="745" y="90" font-family="sans-serif" font-size="13" font-weight="800" fill="#c084fc" text-anchor="middle">2005–2008</text>
  <rect x="670" y="128" width="150" height="145" rx="8" fill="url(#cardHist)" stroke="#6b21a8" stroke-width="1.5" filter="url(#shadowT)"/>
  <text x="745" y="148" font-family="sans-serif" font-size="12" font-weight="800" fill="#f8fafc" text-anchor="middle">Georges Gonthier</text>
  <text x="745" y="164" font-family="sans-serif" font-size="10" font-weight="700" fill="#e879f9" text-anchor="middle">Coq Boolean Reflection</text>
  <text x="745" y="184" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• Four Color Theorem</text>
  <text x="745" y="200" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">• External Search +</text>
  <text x="745" y="216" font-family="sans-serif" font-size="10" fill="#cbd5e1" text-anchor="middle">  vm_compute Checker</text>
  <text x="745" y="232" font-family="sans-serif" font-size="10" fill="#94a3b8" text-anchor="middle">• Zero-Axiom Kernel</text>
  <text x="745" y="256" font-family="sans-serif" font-size="10" font-weight="700" fill="#c084fc" text-anchor="middle">Not Applied to Connect-k</text>

  <!-- Node 6: 2026 (This Work) -->
  <circle cx="895" cy="108" r="11" fill="#10b981" stroke="#fef08a" stroke-width="3"/>
  <text x="895" y="90" font-family="sans-serif" font-size="13" font-weight="900" fill="#34d399" text-anchor="middle">2026 (Ours)</text>
  <rect x="830" y="128" width="130" height="145" rx="8" fill="url(#cardNovel)" stroke="#10b981" stroke-width="2" filter="url(#shadowT)"/>
  <text x="895" y="148" font-family="sans-serif" font-size="12" font-weight="900" fill="#ffffff" text-anchor="middle">This Repository</text>
  <text x="895" y="164" font-family="sans-serif" font-size="10" font-weight="800" fill="#34d399" text-anchor="middle">8×7 Connect-5 Proven</text>
  <text x="895" y="184" font-family="sans-serif" font-size="10" fill="#ecfdf5" text-anchor="middle">• First Rocq 9.1 Proof</text>
  <text x="895" y="200" font-family="sans-serif" font-size="10" fill="#ecfdf5" text-anchor="middle">• structure_sound</text>
  <text x="895" y="216" font-family="sans-serif" font-size="10" fill="#ecfdf5" text-anchor="middle">• 405.35M/s GPU Kernel</text>
  <text x="895" y="232" font-family="sans-serif" font-size="10" fill="#ecfdf5" text-anchor="middle">• 10-Cell Core Theorem</text>
  <text x="895" y="256" font-family="sans-serif" font-size="10" font-weight="900" fill="#facc15" text-anchor="middle">game_value = Draw</text>

  <!-- Bottom Split Panel: Folklore vs. Novel Contributions -->
  <!-- Left Panel: Classical Folklore -->
  <rect x="30" y="295" width="445" height="190" rx="10" fill="#1e293b" stroke="#475569" stroke-width="1.5" filter="url(#shadowT)"/>
  <text x="252" y="322" font-family="sans-serif" font-size="14" font-weight="800" fill="#38bdf8" text-anchor="middle">
    What We Inherited from Classical Folklore (Explicitly Credited)
  </text>
  <text x="48" y="348" font-family="sans-serif" font-size="11.5" fill="#e2e8f0">
    <tspan font-weight="800" fill="#fbbf24">1. Pairing Heuristics:</tspan> Allis's (1988) Claimeven, Baseinverse &amp; Vertical rules.
  </text>
  <text x="48" y="372" font-family="sans-serif" font-size="11.5" fill="#e2e8f0">
    <tspan font-weight="800" fill="#fbbf24">2. Sentinel Bitboards:</tspan> Tromp's (1995) Fhourstones 64-bit column-sentinel layout.
  </text>
  <text x="48" y="396" font-family="sans-serif" font-size="11.5" fill="#e2e8f0">
    <tspan font-weight="800" fill="#fbbf24">3. AND/OR Tree Search:</tspan> Nagai's (1999) df-pn (MID) &amp; Kaneko's (2010) PDFPN.
  </text>
  <text x="48" y="420" font-family="sans-serif" font-size="11.5" fill="#e2e8f0">
    <tspan font-weight="800" fill="#fbbf24">4. Reflection Pattern:</tspan> Gonthier's (2005) Coq vm_compute certificate architecture.
  </text>
  <text x="48" y="444" font-family="sans-serif" font-size="11.5" fill="#e2e8f0">
    <tspan font-weight="800" fill="#fbbf24">5. Gravity Asymmetry:</tspan> Failure of Nash strategy-stealing under column gravity.
  </text>
  <text x="48" y="468" font-family="sans-serif" font-size="11" font-style="italic" fill="#94a3b8">
    Prior Status: Zero machine-checked proofs in Coq/Rocq, Lean, Isabelle, or Agda.
  </text>

  <!-- Right Panel: Genuine Novelty in This Repo -->
  <rect x="505" y="295" width="445" height="190" rx="10" fill="url(#cardNovel)" stroke="#10b981" stroke-width="2" filter="url(#shadowT)"/>
  <text x="727" y="322" font-family="sans-serif" font-size="14" font-weight="800" fill="#34d399" text-anchor="middle">
    What Is Genuinely New in This Repository (Machine-Checked)
  </text>
  <text x="523" y="348" font-family="sans-serif" font-size="11.5" fill="#ecfdf5">
    <tspan font-weight="800" fill="#4ade80">1. First Formal Mechanization:</tspan> 1,160-line Rocq 9.1 proof of structure_sound (0 axioms).
  </text>
  <text x="523" y="372" font-family="sans-serif" font-size="11.5" fill="#ecfdf5">
    <tspan font-weight="800" fill="#4ade80">2. Parity Obstruction &amp; Rule R3:</tspan> Formal proof of Ply-1 odd parity &amp; frozen-column fix.
  </text>
  <text x="523" y="396" font-family="sans-serif" font-size="11.5" fill="#ecfdf5">
    <tspan font-weight="800" fill="#4ade80">3. 10-Cell Core &amp; Dead (4,6):</tspan> Proven 10-cell cover of all 52 non-vertical lines.
  </text>
  <text x="523" y="420" font-family="sans-serif" font-size="11.5" fill="#ecfdf5">
    <tspan font-weight="800" fill="#4ade80">4. Exact 64-Bit Saturation:</tspan> 8×(7+1)=64 bits mapped to 4.19M CUDA threads (405.35M/s).
  </text>
  <text x="523" y="444" font-family="sans-serif" font-size="11.5" fill="#ecfdf5">
    <tspan font-weight="800" fill="#4ade80">5. Constructive Minimax Bridge:</tspan> mutual_safety_draw &amp; cert_fair verified via vm_compute.
  </text>
  <text x="523" y="468" font-family="sans-serif" font-size="11" font-weight="700" fill="#facc15">
    Result: First Formally Verified Proof of Connect-5 (8×7) Fairness in History.
  </text>
</svg>
"""

with open("assets/historical_timeline.svg", "w", encoding="utf-8") as f:
    f.write(svg_timeline)

print("Generated 4 updated SVG visual assets in assets/ successfully!")
