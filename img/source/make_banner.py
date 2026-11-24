"""Usage: python make_banner.py <gget_x_scverse_overview.svg> <liana logo.png> <out.svg>

gget SVG: https://scverse.org/img/blog/gget_x_scverse_overview.svg
logo: liana-py/docs/_static/logo.png

Build liana_x_scverse_overview.svg: scverse circle (from gget banner) -> LIANA+ hex -> neon capability panel -> return arrow."""
import base64
import sys

ref, logo, out = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(ref).read().splitlines()
# lines 1..213 of the gget SVG: header, defs, style, scverse circle with ecosystem logos (incl. centre scverse logo)
head = lines[:213]

NAVY, NAVY2 = "#383f56", "#262b3d"
RET = "#12a89d"  # return arrow: muted teal, no glow
CYAN, MAGENTA, ORANGE, GREEN, TEAL = "#00f5e4", "#e0216b", "#f07800", "#00c48c", "#1ccfc1"

# replace gget dark-mode rules for panel elements with ours; keep circle/return rules
style_fix = {
    '      #dbs-bg { fill: #151c2d; stroke: #2c3a5c; }': '',
    '      #dbs-title { fill: #c4d0ea; }': '',
    '      .pill rect { fill: #1e2740; stroke: #34446a; }': '',
    '      .pill text { fill: #e3e9f7; }': '',
    '      #more rect { fill: #1c2a4a; }': '',
    '      #more text { fill: #c4d0ea; }': '',
}
head = [style_fix.get(l, l) for l in head]
head = [l for l in head if l != '']
# add neon glow filter into <defs>
i = head.index("  </defs>")
head[i:i] = [
    '    <filter id="neon" x="-30%" y="-30%" width="160%" height="160%">',
    '      <feGaussianBlur stdDeviation="6" result="b"></feGaussianBlur>',
    '      <feMerge><feMergeNode in="b"></feMergeNode><feMergeNode in="SourceGraphic"></feMergeNode></feMerge>',
    '    </filter>',
    '    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">',
    f'      <feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="{CYAN}" flood-opacity="0.35"></feDropShadow>',
    '    </filter>',
]

b64 = base64.b64encode(open(logo, "rb").read()).decode()
body = []
A = body.append

# arrows (neon cyan)
for x0 in (565, 905):
    A(f'  <path d="M{x0} 400 L{x0+37} 400 L{x0+37} 388 L{x0+63} 410 L{x0+37} 432 L{x0+37} 420 L{x0} 420 Z" fill="{CYAN}" filter="url(#neon)"></path>')

# LIANA+ hex logo (logo png 490x562); hex centred at ~ (767, 410)
w = 300; h = w * 562 / 490
A(f'  <image x="{767 - w/2:.1f}" y="{410 - h/2:.1f}" width="{w}" height="{h:.1f}" href="data:image/png;base64,{b64}"></image>')

# capability panel
PX, PY, PW = 985, 60, 590
groups = [
    ("SINGLE-CELL", GREEN, ["CellPhoneDB", "CellChat", "consensus"]),
    ("SPATIAL", ORANGE, ["bivariate", "MISTy", "LRIC", "Inflow"]),
    ("MULTI-SAMPLE", TEAL, ["MOFA+", "Tensor-cell2cell"]),
    ("CONTRASTS & SIGNALLING", CYAN, ["PyDESeq2", "pyCrossTalkeR", "CORNETO"]),
    ("KNOWLEDGE", MAGENTA, ["OmniPath", "MetalinksDB"]),
]
y = PY + 110
rows = []
for title, col, pills in groups:
    rows.append(f'  <text x="{PX+38}" y="{y}" font-size="22" font-weight="700" letter-spacing="1.6" fill="{col}">{title.replace('&', '&amp;')}</text>')
    x = PX + 38; py = y + 16
    for p in pills:
        pw = int(len(p) * 14.2 + 34)
        rows.append(f'  <g class="pill"><rect x="{x}" y="{py}" width="{pw}" height="45" rx="11" fill="{NAVY2}" stroke="{col}" stroke-width="2"' + (' stroke-dasharray="6 5"' if p == "& more" else "") + '></rect>'
                    f'<text x="{x + pw/2:.0f}" y="{py+31}" text-anchor="middle" font-size="25" font-weight="700" fill="#f3f5fb">{p.replace('&', '&amp;')}</text></g>')
        x += pw + 14
    y += 104
PH = y - PY - 30
A(f'  <rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="22" fill="{NAVY}" stroke="{CYAN}" stroke-width="2.5" filter="url(#glow)"></rect>')
A(f'  <text x="{PX+38}" y="{PY+64}" font-size="28" font-weight="800" letter-spacing="1.4" fill="#ffffff">CELL-CELL COMMUNICATION <tspan fill="{MAGENTA}">+</tspan></text>')
body += rows

# return arrow (magenta neon) back to the scverse circle
bottom = PY + PH
ry = 810
A(f'  <g fill="none" stroke="{RET}" stroke-width="8" stroke-linecap="round">')
A(f'    <path d="M1280 {bottom+2} L1280 {ry-24} Q1280 {ry} 1256 {ry} L1130 {ry}"></path>')
A(f'    <path d="M500 {ry} L344 {ry} Q320 {ry} 320 {ry-24} L320 704"></path>')
A('  </g>')
A(f'  <path d="M320 656 L346 704 L294 704 Z" fill="{RET}"></path>')
A(f'  <text id="return" x="815" y="{ry+10}" text-anchor="middle" font-size="34" font-weight="700" fill="{RET}" stroke="#ffffff" stroke-width="6" paint-order="stroke" stroke-linejoin="round">results stored in AnnData / MuData</text>')

svg = "\n".join(head + body + ["</svg>", ""])
svg = svg.replace('viewBox="0 0 1626 870" width="1626" height="870"', 'viewBox="0 0 1626 880" width="1626" height="880"')
open(out, "w").write(svg)
print("bottom", bottom)
