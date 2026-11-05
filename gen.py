#!/usr/bin/env python3
"""Builds a layered-SVG illustration of a fox girl in a sunlit café and wraps it in an HTML page.

Coordinates: every layer uses viewBox 0 0 810 1440 (9:16).
Head parts are drawn in a local frame whose origin is the midpoint between the eyes,
then placed with translate(456,630) · sway · rotate(-6) · translate(0,-104) so the chin (0,104)
sits on the neck anchor.
"""
import math
import random
import sys

# usage: python3 gen.py [out.html] [--fragment]
#   default: a standalone index.html you can open in any browser
#   --fragment: page body only, as the Claude artifact host expects
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "index.html"
FRAGMENT = "--fragment" in sys.argv
R = random.Random(1105)


# ───────────────────────────── helpers ─────────────────────────────
def n(v):
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


def P(x, y):
    return f"{n(x)},{n(y)}"


def lerp(a, b, t):
    return a + (b - a) * t


def h2r(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def r2h(c):
    return "#" + "".join(f"{max(0, min(255, int(round(v)))):02x}" for v in c)


def mix(a, b, t):
    A, B = h2r(a), h2r(b)
    return r2h([lerp(A[i], B[i], t) for i in range(3)])


def sstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def cr(pts, closed=False, k=1.0, move=True):
    """Catmull-Rom spline through pts as SVG path data."""
    N = len(pts)
    out = "M" + P(*pts[0]) if move else ""
    for i in (range(N) if closed else range(N - 1)):
        if closed:
            p0, p1, p2, p3 = pts[(i - 1) % N], pts[i], pts[(i + 1) % N], pts[(i + 2) % N]
        else:
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1, p2 = pts[i], pts[i + 1]
            p3 = pts[i + 2] if i + 2 < N else pts[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        out += "C" + P(*c1) + " " + P(*c2) + " " + P(*p2)
    return out + ("Z" if closed else "")


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def bezd(p0, p1, p2, p3, t):
    u = 1 - t
    return (3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0]),
            3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1]))


def path(d, fill="none", **kw):
    attrs = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<path d="{d}" fill="{fill}"{attrs}/>'


def line(d, stroke, w, op=1, cap="round", extra=""):
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round" opacity="{op}"{extra}/>'


# ───────────────────────────── background layer ─────────────────────────────
def build_bg():
    defs = """
<linearGradient id="bWall" x1="0" y1="0" x2="810" y2="0" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#e9ad52"/><stop offset=".6" stop-color="#c98236"/><stop offset=".74" stop-color="#5e3218"/>
 <stop offset=".9" stop-color="#341b0d"/><stop offset="1" stop-color="#4a2913"/></linearGradient>
<radialGradient id="bSun" cx="200" cy="290" r="720" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#fffef6"/><stop offset=".16" stop-color="#fff4c8"/><stop offset=".4" stop-color="#ffda84"/>
 <stop offset=".68" stop-color="#f0ac4a"/><stop offset="1" stop-color="#c47a2c"/></radialGradient>
<radialGradient id="bSun2" cx="800" cy="150" r="460" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#fff3c8"/><stop offset=".5" stop-color="#f6c460"/><stop offset="1" stop-color="#a85f26"/></radialGradient>
<linearGradient id="bPillar" x1="600" y1="0" x2="700" y2="0" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#9c5f2c"/><stop offset=".22" stop-color="#5a3118"/><stop offset="1" stop-color="#26130a"/></linearGradient>
<linearGradient id="bCounter" x1="0" y1="990" x2="0" y2="1440" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#8a5428"/><stop offset=".25" stop-color="#4a2a15"/><stop offset="1" stop-color="#1e1009"/></linearGradient>
<radialGradient id="bBokeh"><stop offset="0" stop-color="#fffbe8" stop-opacity=".25"/><stop offset=".78" stop-color="#fffbe8" stop-opacity=".6"/><stop offset="1" stop-color="#fffbe8" stop-opacity="0"/></radialGradient>
<radialGradient id="bBokehW"><stop offset="0" stop-color="#ffd27e" stop-opacity=".35"/><stop offset=".75" stop-color="#ffc062" stop-opacity=".75"/><stop offset="1" stop-color="#ffb04a" stop-opacity="0"/></radialGradient>
<radialGradient id="bBokehP"><stop offset="0" stop-color="#c9a2ff" stop-opacity=".4"/><stop offset=".75" stop-color="#b48af0" stop-opacity=".7"/><stop offset="1" stop-color="#9a6ae0" stop-opacity="0"/></radialGradient>
<radialGradient id="bLamp"><stop offset="0" stop-color="#fff8dc" stop-opacity="1"/><stop offset=".25" stop-color="#ffdf96" stop-opacity=".55"/><stop offset="1" stop-color="#ffb84a" stop-opacity="0"/></radialGradient>
<linearGradient id="bRay" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffbe6" stop-opacity=".75"/><stop offset=".6" stop-color="#fff4cc" stop-opacity=".25"/><stop offset="1" stop-color="#fff2c4" stop-opacity="0"/></linearGradient>
<linearGradient id="pGlass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset=".35" stop-color="#fff" stop-opacity=".04"/><stop offset=".55" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="pBun" cx=".38" cy=".3" r=".8"><stop offset="0" stop-color="#ffe2a6"/><stop offset=".55" stop-color="#e7a656"/><stop offset="1" stop-color="#b8692c"/></radialGradient>
<radialGradient id="pPuff" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="#fff0cf"/><stop offset=".6" stop-color="#f0c27c"/><stop offset="1" stop-color="#c88a44"/></radialGradient>
<filter id="fB4" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="3.6"/></filter>
<filter id="fB18" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="18"/></filter>
<filter id="fB1" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.2"/></filter>
"""
    far = []
    far.append('<rect x="-60" y="-60" width="930" height="1560" fill="url(#bWall)"/>')
    far.append('<rect x="-60" y="-60" width="664" height="1062" fill="url(#bSun)"/>')
    far.append('<rect x="700" y="-60" width="170" height="660" fill="url(#bSun2)"/>')

    # sunlit foliage outside the window, heavily blurred
    pal = ["#fffbe6", "#fff0b8", "#ffe08e", "#f8c867", "#ecb04f", "#d9a446", "#c48c38"]
    fol = []
    for _ in range(80):
        x, y = R.uniform(-40, 600), R.uniform(-40, 990)
        dist = math.hypot(x - 200, y - 290) / 760
        idx = int(dist * len(pal) + R.uniform(-1.4, 1.4))
        idx = max(0, min(len(pal) - 1, idx))
        fol.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(R.uniform(22, 80))}" fill="{pal[idx]}" opacity="{R.uniform(.3, .65):.2f}"/>')
    for _ in range(14):  # right window foliage
        x, y = R.uniform(700, 860), R.uniform(-40, 560)
        fol.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(R.uniform(20, 55))}" fill="{R.choice(pal[1:5])}" opacity="{R.uniform(.3, .6):.2f}"/>')
    far.append('<g filter="url(#fB18)">' + "".join(fol) + "</g>")

    # bokeh discs
    bk = []
    for _ in range(34):
        x, y = R.uniform(-20, 590), R.uniform(0, 960)
        bk.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(R.uniform(6, 22))}" fill="url(#bBokeh)" opacity="{R.uniform(.45, .95):.2f}"/>')
    for _ in range(10):
        x, y = R.uniform(712, 800), R.uniform(10, 560)
        bk.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(R.uniform(6, 16))}" fill="url(#bBokeh)" opacity="{R.uniform(.45, .9):.2f}"/>')
    far.append("<g>" + "".join(bk) + "</g>")

    # window frames, backlit so they read as soft brown bars
    far.append('<g fill="#6a3a18" opacity=".5">'
               '<rect x="138" y="-60" width="11" height="1062"/>'
               '<rect x="304" y="-60" width="17" height="1062"/>'
               '<rect x="462" y="-60" width="15" height="1062"/>'
               '<rect x="-60" y="78" width="664" height="12"/>'
               '<rect x="-60" y="456" width="664" height="18"/></g>')
    far.append('<g fill="#7a4520" opacity=".28">'
               '<rect x="58" y="-60" width="5" height="1062"/><rect x="224" y="-60" width="5" height="1062"/>'
               '<rect x="392" y="-60" width="5" height="1062"/><rect x="536" y="-60" width="5" height="1062"/>'
               '<rect x="-60" y="270" width="664" height="5"/><rect x="-60" y="700" width="664" height="6"/></g>')

    # pillar + right window + dark interior
    far.append('<rect x="600" y="-60" width="100" height="1560" fill="url(#bPillar)"/>')
    far.append('<g fill="#3a1f0e" opacity=".85"><rect x="700" y="-60" width="11" height="660"/>'
               '<rect x="774" y="-60" width="9" height="660"/><rect x="700" y="246" width="170" height="10"/>'
               '<rect x="700" y="586" width="170" height="18"/></g>')
    far.append('<rect x="700" y="600" width="170" height="900" fill="#2a160b"/>')
    far.append('<path d="M600,980C650,960 760,960 870,990V1500H600Z" fill="#20100a" opacity=".6"/>')
    wb = []
    for _ in range(12):
        x, y = R.uniform(708, 805), R.uniform(640, 1100)
        wb.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(R.uniform(5, 13))}" fill="url(#bBokehW)" opacity="{R.uniform(.5, 1):.2f}"/>')
    far.append("<g>" + "".join(wb) + "</g>")

    # wisteria-like purple blooms hanging in the right window
    pb = []
    for cx0, cy0, ln in ((735, 200, 120), (770, 180, 150), (800, 210, 110), (718, 260, 70)):
        for k in range(16):
            t = k / 15
            x = cx0 + R.uniform(-14, 14) * (1 - t * .6)
            y = cy0 + t * ln
            pb.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(lerp(11, 4, t) + R.uniform(-1.5, 1.5))}" '
                      f'fill="{R.choice(["#a77be6", "#8b5ad0", "#c4a0f4", "#9868dc"])}" opacity=".85"/>')
    far.append('<g>' + "".join(pb) + '</g>')
    far.append('<g opacity=".9">' + "".join(
        f'<circle cx="{n(R.uniform(705, 805))}" cy="{n(R.uniform(150, 360))}" r="{n(R.uniform(8, 18))}" fill="url(#bBokehP)"/>'
        for _ in range(6)) + '</g>')

    # hanging plants along the top
    leaves = []
    leaf_cols = ["#55602a", "#465020", "#6e7230", "#3a3e18", "#7d7a34"]
    for vx in (30, 95, 170, 250, 330, 405, 480, 560, 640, 690, 760):
        ln = R.uniform(70, 230)
        sway = R.uniform(-30, 30)
        pts = [(vx + sway * (i / 6) ** 2, -20 + ln * i / 6) for i in range(7)]
        leaves.append(line(cr(pts), "#3d3a18", 2.4, .8))
        for i in range(1, 15):
            t = i / 14
            x, y = bez(pts[0], pts[2], pts[4], pts[6], t)
            side = 1 if i % 2 else -1
            ang = side * R.uniform(25, 60)
            rx = R.uniform(9, 16) * (1 - t * .35)
            leaves.append(f'<ellipse cx="{n(x + side * rx * .7)}" cy="{n(y)}" rx="{n(rx)}" ry="{n(rx * .48)}" '
                          f'transform="rotate({n(ang)} {n(x + side * rx * .7)} {n(y)})" fill="{R.choice(leaf_cols)}" opacity=".92"/>')
    for _ in range(40):  # top foliage mass
        x = R.uniform(-30, 850)
        y = R.uniform(-30, 40)
        leaves.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(R.uniform(14, 26))}" ry="{n(R.uniform(7, 12))}" '
                      f'transform="rotate({n(R.uniform(-50, 50))} {n(x)} {n(y)})" fill="{R.choice(leaf_cols)}"/>')
    far.append("<g>" + "".join(leaves) + "</g>")

    # pendant lamp
    far.append('<circle cx="652" cy="70" r="110" fill="url(#bLamp)" opacity=".85"/>'
               '<path d="M652,-60V40" stroke="#2a1a10" stroke-width="2.5"/>'
               '<path d="M626,64C628,40 676,40 678,64Z" fill="#3b2414"/>'
               '<rect x="624" y="61" width="56" height="6" rx="3" fill="#b08442"/>'
               '<ellipse cx="652" cy="72" rx="12" ry="8" fill="#fff7d8"/>')

    # chalkboard menu at the left edge
    chalk = ['<rect x="-30" y="322" width="112" height="236" rx="4" fill="#5a381e"/>',
             '<rect x="-30" y="332" width="102" height="216" fill="#2f2a26"/>']
    for i, yy in enumerate(range(356, 540, 22)):
        ln = R.uniform(30, 58) if i else 50
        pts = [(-6 + j * ln / 5, yy + R.uniform(-2, 2)) for j in range(6)]
        chalk.append(line(cr(pts), "#efe8d6", 3 if i == 0 else 2.2, .6 if i == 0 else .42))
    far.append("".join(chalk))

    # counter under the window
    far.append('<rect x="-60" y="996" width="664" height="510" fill="url(#bCounter)"/>')
    far.append('<rect x="-60" y="992" width="664" height="8" fill="#c88a48" opacity=".8"/>')

    # ── pastry case (closer → less blur)
    pc = []
    pc.append('<rect x="-40" y="812" width="312" height="186" fill="#5a3418" opacity=".7"/>')
    pc.append('<rect x="-40" y="812" width="312" height="186" fill="#f3c06a" opacity=".18"/>')
    # lower shelf pastries: choux puffs with lavender cream + a wrapped treat
    for cx in (48, 118, 188):
        pc.append(f'<ellipse cx="{cx}" cy="972" rx="30" ry="6" fill="#3a1f0e" opacity=".35"/>')
        pc.append(f'<path d="M{cx - 30},968C{cx - 32},936 {cx - 14},924 {cx},924C{cx + 16},924 {cx + 32},938 {cx + 30},968Z" fill="url(#pPuff)"/>')
        pc.append(f'<path d="M{cx - 27},950C{cx - 10},944 {cx + 12},944 {cx + 27},950C{cx + 20},956 {cx - 20},956 {cx - 27},950Z" fill="#c9a6f2"/>')
        pc.append(f'<circle cx="{cx}" cy="921" r="5" fill="#9a62dc"/>')
        pc.append(f'<path d="M{cx - 14},932C{cx - 8},928 {cx + 2},927 {cx + 8},929" stroke="#fff5e0" stroke-width="3" fill="none" opacity=".7" stroke-linecap="round"/>')
    pc.append('<path d="M224,970L236,932L270,936L262,972Z" fill="#7d4bc4"/><path d="M230,952L266,955" stroke="#d8c0ff" stroke-width="3"/>')
    pc.append('<rect x="-40" y="980" width="312" height="7" fill="#f2dfbb" opacity=".9"/>')
    # glass front reflections
    pc.append('<rect x="-40" y="812" width="312" height="186" fill="url(#pGlass)"/>')
    pc.append(line("M20,826L-6,990", "#fff", 7, .22) + line("M200,826L176,990", "#fff", 4, .16))
    # top ledge
    pc.append('<rect x="-40" y="804" width="316" height="10" fill="#f8ead0"/>')
    pc.append('<rect x="-40" y="813" width="316" height="3" fill="#b78544" opacity=".8"/>')
    pc.append('<rect x="266" y="804" width="6" height="194" fill="#e3bd74"/>')
    # cake dome with two lavender-glazed buns
    pc.append('<ellipse cx="128" cy="806" rx="134" ry="7" fill="#fff6e6"/>')
    for cx, w in ((62, 92), (180, 98)):
        x0, x1 = cx - w / 2, cx + w / 2
        pc.append(f'<path d="M{n(x0)},804C{n(x0 - 2)},772 {n(cx - w * .3)},752 {cx},752C{n(cx + w * .3)},752 {n(x1 + 2)},772 {n(x1)},804Z" fill="url(#pBun)"/>')
        pc.append(line(cr([(x0 + 8, 772), (cx - 20, 766), (cx, 772), (cx + 18, 764), (x1 - 8, 774)]), "#a675ea", 6, .95))
        pc.append(line(cr([(x0 + 14, 786), (cx - 10, 780), (cx + 12, 786), (x1 - 12, 782)]), "#c7a3f7", 4, .9))
        for _ in range(10):
            pc.append(f'<circle cx="{n(R.uniform(x0 + 10, x1 - 10))}" cy="{n(R.uniform(758, 798))}" r="1.3" fill="#fff8ea" opacity=".9"/>')
    pc.append('<path d="M-12,806V744C-12,712 18,698 60,698H196C238,698 266,712 266,744V806Z" fill="#fff" opacity=".1" stroke="#fffaf0" stroke-width="2.5" stroke-opacity=".6"/>')
    pc.append('<circle cx="127" cy="692" r="7" fill="#f6e6c6" stroke="#fffaf0" stroke-opacity=".7"/>')
    pc.append(line("M8,732C4,752 4,780 8,800", "#fff", 7, .45) + line("M240,722C248,736 250,760 250,790", "#fff", 4, .35))
    pc.append(line("M30,708C70,702 120,701 150,702", "#fff", 4, .4))

    # ── light shafts
    rays = []
    for x0, w0, x1, w1, op in ((-40, 90, 380, 260, .32), (90, 50, 560, 190, .22), (-60, 60, 160, 210, .26),
                               (200, 40, 720, 160, .14), (20, 30, 470, 120, .2)):
        rays.append(f'<path d="M{x0},-60L{x0 + w0},-60L{x1 + w1},1300L{x1},1300Z" fill="url(#bRay)" opacity="{op}"/>')

    return (f'<defs>{defs}</defs>'
            f'<g filter="url(#fB4)">{"".join(far)}</g>'
            f'<g filter="url(#fB1)">{"".join(pc)}</g>'
            f'<g style="mix-blend-mode:screen">{"".join(rays)}</g>')


# ───────────────────────────── scene: shared defs ─────────────────────────────
SCENE_DEFS = """
<radialGradient id="gSkin" cx="-20" cy="10" r="140" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#fff3ea"/><stop offset=".6" stop-color="#ffe6d8"/><stop offset="1" stop-color="#f9cdb9"/></radialGradient>
<linearGradient id="gSkinB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6c7b2"/><stop offset=".35" stop-color="#ffe2d4"/><stop offset="1" stop-color="#ffe9de"/></linearGradient>
<linearGradient id="gNeck" x1="0" y1="600" x2="0" y2="700" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#e9a994"/><stop offset=".45" stop-color="#f8cdbb"/><stop offset="1" stop-color="#ffe3d6"/></linearGradient>
<linearGradient id="gHand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffeee4"/><stop offset=".7" stop-color="#ffdccc"/><stop offset="1" stop-color="#f0b8a4"/></linearGradient>
<radialGradient id="gBlush"><stop offset="0" stop-color="#ff8ea4" stop-opacity=".75"/><stop offset="1" stop-color="#ff8ea4" stop-opacity="0"/></radialGradient>
<linearGradient id="gSclera" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e4d6ee"/><stop offset=".45" stop-color="#fffaf8"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
<linearGradient id="gIris" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34105f"/><stop offset=".34" stop-color="#6331ad"/>
 <stop offset=".72" stop-color="#a978ec"/><stop offset="1" stop-color="#ead2ff"/></linearGradient>
<radialGradient id="gIrisGlow" cx=".5" cy=".85" r=".6"><stop offset="0" stop-color="#fbe9ff" stop-opacity=".85"/><stop offset="1" stop-color="#d9b2ff" stop-opacity="0"/></radialGradient>

<linearGradient id="gHair" x1="0" y1="-210" x2="0" y2="40" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#ffe49a"/><stop offset=".2" stop-color="#f9cd66"/><stop offset=".36" stop-color="#e5a141"/>
 <stop offset=".6" stop-color="#f2b955"/><stop offset=".85" stop-color="#fdd57e"/><stop offset="1" stop-color="#ffe6a6"/></linearGradient>
<linearGradient id="gHairSide" x1="0" y1="-80" x2="0" y2="160" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#e9ac4a"/><stop offset=".55" stop-color="#f7c862"/><stop offset="1" stop-color="#ffe3a0"/></linearGradient>
<linearGradient id="gHairBack" x1="0" y1="-60" x2="0" y2="190" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#d49a3e"/><stop offset="1" stop-color="#9c6024"/></linearGradient>
<linearGradient id="gTailBundle" x1="0" y1="-130" x2="0" y2="60" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#dc9a3c"/><stop offset=".5" stop-color="#f6c460"/><stop offset="1" stop-color="#eeb552"/></linearGradient>
<linearGradient id="gShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".38"/>
 <stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#5a2a00" stop-opacity=".22"/></linearGradient>
<linearGradient id="gCoreL" x1="0" y1="0" x2="0" y2="240" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#9a5e22"/><stop offset=".55" stop-color="#7a4a2a"/><stop offset="1" stop-color="#4a2486"/></linearGradient>
<linearGradient id="gCoreR" x1="0" y1="0" x2="0" y2="240" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#9a5e22"/><stop offset=".55" stop-color="#7a4a2a"/><stop offset="1" stop-color="#4a2486"/></linearGradient>
<linearGradient id="gEar" x1="0" y1="-290" x2="0" y2="-130" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#ffd77a"/><stop offset="1" stop-color="#d9973a"/></linearGradient>
<linearGradient id="gEarIn" x1="0" y1="-280" x2="0" y2="-150" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#fff6e4"/><stop offset=".6" stop-color="#ffe2b8"/><stop offset="1" stop-color="#e2a265"/></linearGradient>

<linearGradient id="gRib" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c79df8"/><stop offset=".5" stop-color="#9a5ddc"/><stop offset="1" stop-color="#6c34b4"/></linearGradient>
<linearGradient id="gRibTail" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a4fd0"/><stop offset="1" stop-color="#a874ea"/></linearGradient>

<linearGradient id="dBodice" x1="326" y1="0" x2="590" y2="0" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#3a2c46"/><stop offset=".25" stop-color="#231a2c"/><stop offset=".75" stop-color="#1a1321"/><stop offset="1" stop-color="#120d17"/></linearGradient>
<linearGradient id="dSkirt" x1="0" y1="1000" x2="0" y2="1440" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#2a1f33"/><stop offset=".4" stop-color="#1b1322"/><stop offset="1" stop-color="#0d0910"/></linearGradient>
<linearGradient id="dSleeveL" x1="230" y1="0" x2="370" y2="0" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#4a3a58"/><stop offset=".25" stop-color="#2a2033"/><stop offset="1" stop-color="#17111c"/></linearGradient>
<linearGradient id="dSleeveR" x1="550" y1="0" x2="680" y2="0" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#17111c"/><stop offset=".7" stop-color="#241a2c"/><stop offset="1" stop-color="#3c2e48"/></linearGradient>
<linearGradient id="dFore" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2d2236"/><stop offset="1" stop-color="#130e18"/></linearGradient>
<linearGradient id="dSatin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5e4a72"/><stop offset=".5" stop-color="#211829"/><stop offset="1" stop-color="#120c16"/></linearGradient>
<pattern id="pMesh" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
 <path d="M0,0V7M0,0H7" stroke="#140d18" stroke-width=".9" opacity=".75"/></pattern>
<pattern id="pLace" width="22" height="22" patternUnits="userSpaceOnUse">
 <circle cx="11" cy="11" r="5" fill="none" stroke="#6e5a82" stroke-width="1"/><circle cx="11" cy="11" r="1.6" fill="#6e5a82"/>
 <circle cx="0" cy="0" r="2.4" fill="none" stroke="#6e5a82" stroke-width=".9"/><circle cx="22" cy="0" r="2.4" fill="none" stroke="#6e5a82" stroke-width=".9"/>
 <circle cx="0" cy="22" r="2.4" fill="none" stroke="#6e5a82" stroke-width=".9"/><circle cx="22" cy="22" r="2.4" fill="none" stroke="#6e5a82" stroke-width=".9"/>
 <path d="M11,0V5M11,17V22M0,11H5M17,11H22" stroke="#6e5a82" stroke-width=".8"/></pattern>

<linearGradient id="gLiner" x1="282" y1="0" x2="368" y2="0" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#f2b866"/><stop offset=".4" stop-color="#d98d3e"/><stop offset="1" stop-color="#a95f26"/></linearGradient>
<radialGradient id="gMuffin" cx="300" cy="812" r="96" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#fff1c8"/><stop offset=".35" stop-color="#f6cd86"/><stop offset=".75" stop-color="#dc9a50"/><stop offset="1" stop-color="#b56e30"/></radialGradient>
<radialGradient id="gGem" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#f0dcff"/><stop offset=".4" stop-color="#a66cf0"/><stop offset="1" stop-color="#4a1b8e"/></radialGradient>

<linearGradient id="gTableTop" x1="0" y1="1086" x2="0" y2="1214" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#f0b673"/><stop offset=".2" stop-color="#cf8a4c"/><stop offset=".7" stop-color="#a5633a"/><stop offset="1" stop-color="#8a4f2c"/></linearGradient>
<linearGradient id="gTableEdge" x1="0" y1="1150" x2="0" y2="1240" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#7a4626"/><stop offset="1" stop-color="#3a1f10"/></linearGradient>
<linearGradient id="gUnder" x1="0" y1="1200" x2="0" y2="1440" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#0a0508" stop-opacity=".85"/><stop offset="1" stop-color="#0a0508" stop-opacity=".5"/></linearGradient>
<linearGradient id="gMug" x1="112" y1="0" x2="218" y2="0" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#fffdf6"/><stop offset=".18" stop-color="#ffffff"/><stop offset=".6" stop-color="#efe6dc"/><stop offset="1" stop-color="#cdbcab"/></linearGradient>
<radialGradient id="gCoffee" cx=".4" cy=".4" r=".7"><stop offset="0" stop-color="#8a5634"/><stop offset="1" stop-color="#3e2112"/></radialGradient>
<linearGradient id="gSteam" x1="0" y1="990" x2="0" y2="840" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".25" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="gTail" x1="640" y1="1200" x2="752" y2="770" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#b9772c"/><stop offset=".35" stop-color="#eab152"/><stop offset=".7" stop-color="#ffd884"/><stop offset=".92" stop-color="#fff2cf"/><stop offset="1" stop-color="#fffaf0"/></linearGradient>
"""


# ───────────────────────────── tail ─────────────────────────────
def build_tail():
    P0, P1, P2, P3 = (640, 1210), (728, 1124), (804, 954), (742, 782)

    def hw(t):
        return 28 + 56 * math.sin(math.pi * min(t, 1)) ** 0.7 - 20 * t ** 3

    def frame_at(t):
        c = bez(P0, P1, P2, P3, t)
        d = bezd(P0, P1, P2, P3, t)
        L = math.hypot(*d)
        tx, ty = d[0] / L, d[1] / L
        return c, (tx, ty), (-ty, tx)

    A, B = [], []
    N = 26
    for i in range(N + 1):
        t = i / N
        c, (tx, ty), (nx, ny) = frame_at(t)
        w = hw(t)
        for side, arr in ((1, A), (-1, B)):
            if i % 2 == 0:
                v = w + R.uniform(8, 13) * (1 - .4 * t)
                drift = 4
            else:
                v = w - R.uniform(2, 5)
                drift = 0
            arr.append((c[0] + side * nx * v + tx * drift, c[1] + side * ny * v + ty * drift))
    c, (tx, ty), (nx, ny) = frame_at(1)
    tip = [(c[0] + tx * 16 + nx * 10, c[1] + ty * 16 + ny * 10), (c[0] + tx * 30 + nx * 3, c[1] + ty * 30 + ny * 3),
           (c[0] + tx * 34 - nx * 2, c[1] + ty * 34 - ny * 2), (c[0] + tx * 18 - nx * 10, c[1] + ty * 18 - ny * 10)]
    outline = A + tip + B[::-1]
    body = path(cr(outline, closed=True), "url(#gTail)")
    cx0 = sum(p[0] for p in outline) / len(outline)
    halo_pts = []
    for i, p in enumerate(outline):
        q = outline[(i + 1) % len(outline)]
        o = outline[i - 1]
        ex, ey = q[0] - o[0], q[1] - o[1]
        L = math.hypot(ex, ey) or 1
        halo_pts.append((p[0] + ey / L * 6, p[1] - ex / L * 6))
    halo = path(cr(halo_pts, closed=True), "url(#gTail)", opacity=".35")
    tufts = []
    for arr, side in ((A, 1), (B, -1)):
        for i in range(0, len(arr) - 2, 2):
            p = arr[i]
            t = i / len(arr)
            c, (tx, ty), (nx, ny) = frame_at(min(t, 1))
            for j in range(2):
                ln = R.uniform(8, 15)
                ox, oy = side * nx * ln + tx * ln * .9, side * ny * ln + ty * ln * .9
                sx, sy = p[0] - side * nx * 4 + R.uniform(-4, 4), p[1] - side * ny * 4 + R.uniform(-4, 4)
                col = mix("#e0a246", "#fff3d2", min(1, t * 1.1))
                tufts.append(f'<path d="M{P(sx, sy)}q{P(ox * .4 - tx * 3, oy * .4 - ty * 3)} {P(ox, oy)}" stroke="{col}" stroke-width="{R.uniform(2, 3.4):.1f}" fill="none" stroke-linecap="round" opacity=".85"/>')
    body = halo + body + "".join(tufts)
    # soft lit core, offset toward the window side
    core = []
    for i in range(31):
        t = .04 + .94 * i / 30
        c, _, (nx, ny) = frame_at(t)
        w = hw(t)
        core.append((c[0] + nx * w * .55, c[1] + ny * w * .55))
    for i in range(30, -1, -1):
        t = .04 + .94 * i / 30
        c, _, (nx, ny) = frame_at(t)
        w = hw(t)
        core.append((c[0] - nx * w * .25, c[1] - ny * w * .25))
    glow = path(cr(core, closed=True), "#fff0bf", opacity=".38")
    shadow = []
    for i in range(31):
        t = .02 + .9 * i / 30
        c, _, (nx, ny) = frame_at(t)
        w = hw(t)
        shadow.append((c[0] - nx * (w + 2), c[1] - ny * (w + 2)))
    for i in range(30, -1, -1):
        t = .02 + .9 * i / 30
        c, _, (nx, ny) = frame_at(t)
        w = hw(t)
        shadow.append((c[0] - nx * w * .45, c[1] - ny * w * .45))
    shade = path(cr(shadow, closed=True), "#8a5020", opacity=".28")
    strokes = []
    for _ in range(80):
        t = R.uniform(.04, .97)
        u = R.uniform(-.92, .92)
        c, (tx, ty), (nx, ny) = frame_at(t)
        w = hw(t)
        x0, y0 = c[0] + nx * u * w, c[1] + ny * u * w
        ln = R.uniform(22, 48) * (1 - .4 * t)
        bend = u * 12
        x2, y2 = x0 + tx * ln + nx * bend, y0 + ty * ln + ny * bend
        mx, my = (x0 + x2) / 2 + nx * bend * .35, (y0 + y2) / 2 + ny * bend * .35
        light = u > -.2 and R.random() < .7
        col = R.choice(["#fff4cf", "#ffeab0", "#fffbea"]) if light else R.choice(["#b9772c", "#c98a3a", "#a8692a"])
        op = R.uniform(.25, .5) if light else R.uniform(.15, .3)
        strokes.append(f'<path d="M{P(x0, y0)}Q{P(mx, my)} {P(x2, y2)}" stroke="{col}" stroke-width="{R.uniform(2, 3.6):.1f}" fill="none" stroke-linecap="round" opacity="{op:.2f}"/>')
    rim = line(cr(A[8:]), "#fff7da", 2.6, .55)
    return (f'<g transform="translate(640,1210)"><g class="tail"><g transform="translate(-640,-1210)">'
            f'{body}{shade}{glow}{"".join(strokes)}{rim}</g></g></g>')


# ───────────────────────────── ringlets (drill curls) ─────────────────────────────
def ringlet(cx, y0, y1, r0, r1, turns, start, flip):
    total = turns * 2 * math.pi
    end = start + total
    s = -1 if flip else 1
    E = 0.42

    def r_at(t):
        return lerp(r0, r1, t ** .85)

    def band(t):
        return (1.0 * r_at(t) + 13) * min(1.0, (1 - t) * 2.6 + .08)

    def pt(th, lower):
        t = (th - start) / total
        r = r_at(t)
        yc = lerp(y0, y1, t)
        x = cx + s * r * math.cos(th)
        y = yc + E * r * math.sin(th) + (band(t) if lower else 0)
        return (x, y)

    gold_f, gold_b = "#f8c862", "#b8782c"
    purp_f, purp_b = "#b98cf3", "#6c3cb0"
    hi_g, hi_p = "#fff2c0", "#f1e4ff"
    # dark core so no background shows between loops
    core_l, core_r = [], []
    for i in range(21):
        t = i / 20
        r = r_at(t) * .92
        y = lerp(y0, y1, t) + E * r + band(t) * .5
        core_l.append((cx - r, y))
        core_r.append((cx + r, y))
    core = cr(core_l) + "L" + P(cx, y1 + 30) + "L" + P(*core_r[-1]) + cr(core_r[::-1], move=False) + "Z"
    core_fill = "url(#gCoreR)" if flip else "url(#gCoreL)"
    out = [path(core, core_fill)]
    bounds = [start]
    k = math.floor(start / math.pi + 1e-9) + 1
    while k * math.pi < end - 1e-6:
        bounds.append(k * math.pi)
        k += 1
    bounds.append(end)
    backs, fronts = [], []
    for a, b in zip(bounds[:-1], bounds[1:]):
        m = 16
        ths = [lerp(a, b, i / m) for i in range(m + 1)]
        up = [pt(q, False) for q in ths]
        lo = [pt(q, True) for q in ths]
        tm = ((a + b) / 2 - start) / total
        pf = sstep(.42, .97, tm)
        front = math.sin((a + b) / 2) > 0
        d = cr(up) + "L" + P(*lo[-1]) + cr(lo[::-1], move=False) + "Z"
        if front:
            col = mix(gold_f, purp_f, pf)
            hi = mix(hi_g, hi_p, pf)
            dark = mix("#a86a24", "#5a2a9c", pf)
            mids = [((p[0] + q[0]) / 2, p[1] * .66 + q[1] * .34) for p, q in zip(up, lo)]
            lows = [((p[0] + q[0]) / 2, p[1] * .18 + q[1] * .82) for p, q in zip(up, lo)]
            fronts.append(path(d, col, stroke=dark, stroke_width="1", stroke_opacity=".55") + path(d, "url(#gShade)")
                          + line(cr(mids[4:-3]), hi, max(1.5, band(tm) * .16), .8)
                          + line(cr(lows[3:-3]), dark, 1.2, .5))
        else:
            backs.append(path(d, mix(gold_b, purp_b, pf), stroke=mix("#8a5418", "#4a1e80", pf), stroke_width=".8"))
    return "".join(out) + "".join(backs) + "".join(fronts)


# ───────────────────────────── head pieces ─────────────────────────────
FACE = ("M-103,-70L-104,0C-104,30 -97,52 -77,72C-55,92 -25,102 0,104C25,102 55,92 77,72"
        "C97,52 104,30 104,0L103,-70C98,-150 -98,-150 -103,-70Z")


def clump_geo(xl, xr, yt, tx, ty, bend=0.0):
    w = xr - xl
    h = ty - yt
    return ((xl, yt), (xl + 1, yt + h * .5), (tx - w * .2 + bend, ty - h * .3), (tx, ty),
            (tx + w * .14 + bend, ty - h * .34), (xr - 1, yt + h * .45), (xr, yt))


def clump(xl, xr, yt, tx, ty, bend=0.0):
    a, l1, l2, t, r1, r2, b = clump_geo(xl, xr, yt, tx, ty, bend)
    return f"M{P(*a)}C{P(*l1)} {P(*l2)} {P(*t)}C{P(*r1)} {P(*r2)} {P(*b)}Z"


def clump_edges(xl, xr, yt, tx, ty, bend=0.0):
    a, l1, l2, t, r1, r2, b = clump_geo(xl, xr, yt, tx, ty, bend)
    left = [bez(a, l1, l2, t, u / 10) for u in range(5, 11)]
    right = [bez(t, r1, r2, b, u / 10) for u in range(0, 6)]
    return cr(left) + cr(right)


BANGS = [  # xl, xr, yt, tipx, tipy, bend
    (-136, -84, -150, -116, 2, -8),
    (-114, -52, -160, -88, -30, -6),
    (-84, -24, -168, -60, -20, -5),
    (-58, 4, -170, -32, -40, -4),
    (-28, 30, -172, -6, -28, 3),
    (2, 58, -170, 22, -42, 4),
    (26, 86, -168, 52, -24, 5),
    (54, 114, -160, 82, -36, 6),
    (84, 136, -150, 114, 0, 8),
]
BANG_ORDER = [0, 8, 1, 7, 2, 6, 3, 5, 4]

DOME = "M-128,-6C-140,-100 -92,-204 0,-210C92,-204 140,-100 128,-6L110,-80C90,-130 -90,-130 -110,-80Z"

SIDE_L = "M-128,-74C-144,-6 -140,74 -112,156C-104,120 -96,86 -93,50C-90,12 -95,-32 -104,-76Z"
SIDE_L2 = "M-116,-40C-124,20 -118,84 -100,126C-98,92 -97,58 -96,30C-95,0 -100,-24 -104,-44Z"


def mirror_d(d):
    """Mirror path data horizontally (x → -x). Works for the absolute M/L/C/Q/Z data used here."""
    out = []
    num = ""
    tokens = []
    for ch in d:
        if ch.isalpha():
            if num:
                tokens.append(num)
                num = ""
            tokens.append(ch)
        elif ch in ", ":
            if num:
                tokens.append(num)
                num = ""
        elif ch == "-" and num and num[-1] not in "e":
            tokens.append(num)
            num = "-"
        else:
            num += ch
    if num:
        tokens.append(num)
    cmd = None
    idx = 0
    res = []
    for tk in tokens:
        if tk.isalpha():
            cmd = tk
            idx = 0
            res.append(tk)
            continue
        v = float(tk)
        if cmd in "HV":
            if cmd == "H":
                v = -v
            res.append(n(v))
        else:
            if idx % 2 == 0:
                v = -v
            res.append(n(v))
            idx += 1
    # join with spaces, keep pairs readable
    s = ""
    for tk in res:
        if tk.isalpha():
            s += tk
        else:
            s += (" " if s and not s[-1].isalpha() else "") + tk
    return s


def eye(open_id):
    sclera = "M-31,-4C-29,-22 -12,-29 4,-29C18,-29 28,-23 31,-13C33,6 24,25 6,29C-10,32 -26,20 -31,-4Z"
    streaks = "".join(
        line(f"M{P(1 + 11 * math.cos(a), 3 + 13 * math.sin(a))}L{P(1 + 21 * math.cos(a), 3 + 26 * math.sin(a))}", "#ecd6ff", 1.1, .38)
        for a in [math.radians(d) for d in range(15, 170, 15)])
    return f"""
<path d="{sclera}" fill="url(#gSclera)"/>
<g clip-path="url(#cSclera)">
 <ellipse cx="1" cy="1" rx="23" ry="29" fill="url(#gIris)"/>
 <ellipse cx="1" cy="9" rx="20" ry="20" fill="url(#gIrisGlow)"/>
 {streaks}
 <ellipse cx="1" cy="-1" rx="9.5" ry="14" fill="#1c0533"/>
 <ellipse cx="1" cy="-1" rx="9.5" ry="14" fill="none" stroke="#5a2a9a" stroke-width="1.2" opacity=".6"/>
 <path d="M-26,-36H30V-9C14,-17 -10,-18 -26,-6Z" fill="#1d0638" opacity=".5"/>
 <ellipse cx="1" cy="1" rx="23" ry="29" fill="none" stroke="#2a0b4c" stroke-width="2.2"/>
 <path d="M-34,-34H34V-16C14,-25 -14,-26 -34,-12Z" fill="#7a5a90" opacity=".25"/>
</g>
<ellipse cx="-9" cy="-12" rx="7" ry="9.5" transform="rotate(-18 -9 -12)" fill="#fff"/>
<circle cx="11" cy="13" r="3.4" fill="#fff"/>
<circle cx="13" cy="-14" r="1.9" fill="#fff" opacity=".9"/>
<path d="M-14,8l1.2,-3.6 1.2,3.6 3.6,1.2 -3.6,1.2 -1.2,3.6 -1.2,-3.6 -3.6,-1.2z" fill="#fff" opacity=".85"/>
<path d="M-38,1C-37,-15 -24,-32 2,-34C18,-35 30,-29 36,-17C37,-14 36,-12 34,-12C28,-22 16,-28 2,-28C-18,-28 -30,-15 -33,-1Z" fill="#2a1320"/>
<path d="M-31,-12C-36,-16 -40,-19 -45,-18C-40,-14 -37,-9 -35,-4Z" fill="#2a1320"/>
<path d="M-25,-25L-32,-33L-21,-28ZM-15,-30L-19,-38L-10,-31Z" fill="#2a1320"/>
<path d="M-24,-30C-12,-34 6,-35 22,-30" fill="none" stroke="#6a3a4a" stroke-width="1.2" opacity=".55"/>
{line("M-27,18C-18,28 -4,32 10,31", "#7b3d4c", 1.6, .8)}
{line("M-29,11L-33,15", "#7b3d4c", 1.3, .7)}
{line("M-30,-39C-16,-47 8,-48 26,-39", "#cf8f82", 1.4, .55)}
"""


def bow(cx, cy, rot, sc, dark=False):
    if dark:
        loop, tailc, knot, crease, hi = "url(#dSatin)", "#1d1524", "#2e2338", "#0b070e", "#9c88b4"
    else:
        loop, tailc, knot, crease, hi = "url(#gRib)", "url(#gRibTail)", "#a56ce2", "#5a2a9c", "#e4d0ff"
    g = f"""<g transform="translate({n(cx)},{n(cy)}) rotate({n(rot)}) scale({sc})">
<path d="M-5,6C-12,26 -22,46 -32,64L-21,60L-17,71C-8,48 -1,27 3,8Z" fill="{tailc}"/>
<path d="M5,6C11,26 17,46 22,66L28,57L36,61C26,41 15,23 7,6Z" fill="{tailc}"/>
<path d="M-4,-2C-20,-32 -58,-34 -60,-6C-62,18 -30,22 -4,7Z" fill="{loop}"/>
<path d="M4,-2C20,-32 58,-34 60,-6C62,18 30,22 4,7Z" fill="{loop}"/>
{line("M-6,1C-22,-10 -40,-14 -52,-6", crease, 2.2, .75)}
{line("M6,1C22,-10 40,-14 52,-6", crease, 2.2, .75)}
{line("M-18,-24C-30,-28 -44,-24 -52,-15", hi, 3, .7)}
{line("M18,-24C30,-28 44,-24 52,-15", hi, 3, .55)}
<path d="M-9,-9C-4,-12 4,-12 9,-9C11,-2 11,4 9,9C4,12 -4,12 -9,9C-11,4 -11,-2 -9,-9Z" fill="{knot}"/>
{line("M-5,-6C-2,-8 2,-8 5,-6", hi, 2, .7)}
</g>"""
    return g


def ear(side):
    """side = 1 for her left (our right), -1 mirrored."""
    outer = "M30,-190C60,-238 112,-276 150,-290C162,-240 140,-168 104,-124Z"
    inner = "M54,-182C74,-222 112,-256 140,-272C144,-232 132,-184 110,-150Z"
    tufts = []
    for i in range(9):
        t = i / 8
        bx, by = lerp(56, 112, t), lerp(-182, -152, t)
        ln = R.uniform(18, 34) * (1 - .3 * t)
        ang = math.radians(lerp(-120, -70, t) + R.uniform(-8, 8))
        tx, ty = bx + math.cos(ang) * ln, by + math.sin(ang) * ln
        tufts.append(f"M{P(bx - 4, by + 2)}Q{P(bx + (tx - bx) * .5 - 3, by + (ty - by) * .5)} {P(tx, ty)}Q{P(bx + (tx - bx) * .5 + 4, by + (ty - by) * .5 + 2)} {P(bx + 5, by - 1)}Z")
    fur = "".join(line(f"M{P(lerp(70, 120, t), lerp(-190, -160, t))}Q{P(lerp(90, 135, t), -230)} {P(lerp(118, 140, t), -262)}", "#fffaf0", 1.2, .5)
                  for t in (.15, .5, .85))
    pivot = (67, -157)
    content = (path(outer, "url(#gEar)", stroke="#b8792c", stroke_width="1.4", stroke_opacity=".6") +
               path(inner, "url(#gEarIn)") +
               path("".join(tufts), "#fff8ec", opacity=".95") + fur +
               line("M32,-192C62,-238 112,-276 148,-289", "#fff5d0", 2.2, .6))
    cls = "ear-l" if side == 1 else "ear-r"
    g = (f'<g transform="translate({pivot[0]},{pivot[1]})"><g class="{cls}"><g transform="translate({-pivot[0]},{-pivot[1]})">'
         f"{content}</g></g></g>")
    return g if side == 1 else f'<g transform="scale(-1,1)">{g}</g>'


def head_back():
    d = ("M-122,-60C-154,0 -156,96 -142,184C-130,176 -118,190 -104,182C-90,194 -72,180 -58,188"
         "C-40,180 -20,192 0,186C20,192 40,180 58,188C72,180 90,194 104,182C118,190 130,176 142,184"
         "C156,96 154,0 122,-60Z")
    strands = "".join(line(f"M{P(x, -40)}C{P(x * 1.06, 40)} {P(x * 1.1, 110)} {P(x * 1.04, 180)}", "#8a5420", 1.2, .35)
                      for x in (-130, -112, -94, 94, 112, 130))
    return path(d, "url(#gHairBack)") + strands


def head_front():
    s = []
    # twin tails: bundle + ringlet on each side
    bundleL = "M-128,-124C-112,-80 -112,-30 -122,12C-132,30 -170,32 -182,12C-192,-34 -190,-86 -170,-128Z"
    for side in (-1, 1):
        bd = bundleL if side == -1 else mirror_d(bundleL)
        s.append(path(bd, "url(#gTailBundle)", stroke="#b8792c", stroke_width="1", stroke_opacity=".5"))
        s.append(path(bd, "url(#gShade)"))
        xs = [-176, -164, -150, -138, -128]
        for i, x in enumerate(xs):
            x = x * -side if side == 1 else x
            xm = x * (1 if side == -1 else 1)
            s.append(line(f"M{P(xm * .93, -110)}C{P(xm * 1.0, -70)} {P(xm * 1.02, -30)} {P(xm * 1.01, 6)}",
                          "#b8792c" if i % 2 else "#fff3c4", 1.3 if i % 2 else 2, .45 if i % 2 else .55))
        s.append(ringlet(side * 152, -4, 226, 35, 12, 3.0, math.pi * .02, side == 1))
    # ears (behind hair)
    s.append(ear(1))
    s.append(ear(-1))
    # face
    s.append(path(FACE, "url(#gSkin)"))
    # under-bang cast shadow + side shading, clipped to face
    bang_sh = "".join(clump(*b[:5], b[5]) for b in BANGS)
    s.append(f'<g clip-path="url(#cFace)"><path d="{bang_sh}" transform="translate(4,12)" fill="#eaa48e" opacity=".5"/>'
             f'<path d="{DOME}" transform="translate(0,14)" fill="#eaa48e" opacity=".5"/>'
             '<path d="M70,-40C96,0 98,50 70,90L120,110V-60Z" fill="#f2b9a4" opacity=".45"/>'
             '<path d="M-110,30C-96,60 -70,86 -40,100L-120,110Z" fill="#f2b9a4" opacity=".3"/></g>')
    s.append(line("M-100,26C-96,52 -78,72 -60,84C-40,97 -20,103 0,104C20,103 40,97 60,84C78,72 96,52 100,26",
                  "#d58c78", 1.6, .65))
    # blush
    for x in (-62, 62):
        s.append(f'<ellipse cx="{x}" cy="40" rx="26" ry="12" fill="url(#gBlush)"/>')
        s.append("".join(line(f"M{P(x - 12 + i * 8, 34)}L{P(x - 7 + i * 8, 44)}", "#ff6f8a", 1.4, .5) for i in range(3)))
    # nose + mouth
    s.append(line("M-1,38C1,41 3,42 6,41", "#d4846f", 1.7, .9))
    s.append('<circle cx="0" cy="35" r="1.6" fill="#fff" opacity=".7"/>')
    mouth = "M-14,66C-6,70 8,70 15,64C13,77 6,84 -1,84C-8,84 -13,76 -14,66Z"
    s.append(f'<g class="mouth"><path d="{mouth}" fill="#8f3346"/>'
             f'<g clip-path="url(#cMouth)"><path d="M-16,64C-6,69 8,69 17,62L17,67C8,73 -6,73 -16,70Z" fill="#fffaf8"/>'
             f'<ellipse cx="1" cy="82" rx="9" ry="5.5" fill="#ef8a94"/></g>'
             f'{line("M-16,65.5C-6,69.5 8,69.5 17,63", "#6e2433", 1.8, .9)}'
             f'{line("M-18,63.5L-15,66", "#c06a74", 1.2, .7)}{line("M17.5,61L19.5,63.5", "#c06a74", 1.2, .7)}</g>')
    # eyes (blink groups); right eye mirrored
    s.append('<g class="eyes-open">'
             f'<g transform="translate(-48,8)"><g class="blink"><g transform="translate(0,-6)">{eye("L")}</g></g></g>'
             f'<g transform="translate(48,8) scale(-1,1)"><g class="blink"><g transform="translate(0,-6)">{eye("R")}</g></g></g>'
             '</g>')
    s.append('<g class="eyes-happy">'
             + line("M-74,6C-62,-14 -34,-14 -22,6", "#2a1320", 5) + line("M22,6C34,-14 62,-14 74,6", "#2a1320", 5) +
             '</g>')
    # hair dome
    s.append(path(DOME, "url(#gHair)"))
    # bangs
    for i in BANG_ORDER:
        b = BANGS[i]
        d = clump(*b[:5], b[5])
        s.append(path(d, "url(#gHair)"))
        s.append(line(clump_edges(*b[:5], b[5]), "#b2732a", 1.2, .6))
        # inner strand lines
        xl, xr, yt, tx, ty, bend = b
        midx = (xl + xr) / 2
        s.append(line(f"M{P(midx, yt + 30)}Q{P(lerp(midx, tx, .6) + bend * .5, lerp(yt, ty, .6))} {P(lerp(midx, tx, .9), lerp(yt, ty, .9))}",
                      "#b9782c", 1.1, .35))
        s.append(line(f"M{P(lerp(midx, tx, .45) - 5, lerp(yt, ty, .45))}Q{P(lerp(midx, tx, .7) - 4 + bend * .4, lerp(yt, ty, .72))} {P(lerp(midx, tx, .92) - 2, lerp(yt, ty, .92))}",
                      "#fff4cf", 1.8, .6))
    # brows, drawn over the hair at low opacity
    s.append(line("M-78,-44C-64,-54 -46,-56 -28,-50", "#9a5a30", 2.6, .42))
    s.append(line("M78,-44C64,-54 46,-56 28,-50", "#9a5a30", 2.6, .42))
    # wisps
    s.append(path("M-44,-110C-46,-80 -48,-50 -45,-10C-42,-48 -40,-80 -38,-110Z", "#f8d47a", stroke="#c48b3a", stroke_width=".8", stroke_opacity=".6"))
    s.append(path("M40,-110C42,-80 44,-52 40,-14C38,-50 36,-80 34,-110Z", "#f8d47a", stroke="#c48b3a", stroke_width=".8", stroke_opacity=".6"))
    # angel-ring highlight on the dome
    ring_top = [(x, -152 - 40 * math.cos(x / 130 * math.pi / 2)) for x in range(-120, 121, 10)]
    ring_bot = []
    for i, x in enumerate(range(120, -121, -10)):
        base = -128 - 40 * math.cos(x / 130 * math.pi / 2)
        ring_bot.append((x, base + (6 if i % 2 == 0 else 0)))
    ring = cr(ring_top) + "L" + P(*ring_bot[0]) + cr(ring_bot, move=False) + "Z"
    s.append(f'<g clip-path="url(#cDome)"><path d="{ring}" fill="#fff8dc" opacity=".6"/></g>')
    # strand lines on the dome
    s.append(f'<g clip-path="url(#cDome)"><path d="M60,-200C120,-170 138,-90 128,-6L90,-6C110,-80 100,-150 60,-200Z" fill="#c9862f" opacity=".35"/></g>')
    for x in (-70, -30, 20, 64):
        s.append(line(f"M{P(x * .2, -206)}Q{P(x * .8, -176)} {P(x * 1.0, -140)}", "#c9862f", 1, .3))
    # side locks
    for d in (SIDE_L, mirror_d(SIDE_L)):
        s.append(path(d, "url(#gHairSide)", stroke="#c48b3a", stroke_width="1.1", stroke_opacity=".7"))
        s.append(path(d, "url(#gShade)"))
    for d in (SIDE_L2, mirror_d(SIDE_L2)):
        s.append(path(d, "#ffe7a2", stroke="#c9913e", stroke_width=".9", stroke_opacity=".6", opacity=".9"))
    # rim light on the left silhouette (window side)
    s.append(line("M-126,-20C-138,-110 -90,-200 0,-208", "#fffbe8", 3.2, .8))
    s.append(line("M-140,-30C-146,20 -140,90 -116,150", "#fffbe8", 2.2, .5))
    # ribbons at the twin-tail ties
    s.append(bow(-150, -112, -18, .92))
    s.append(bow(150, -118, 16, 1.12))
    return "".join(s)


def head_wrap(content, cls="sway"):
    return (f'<g transform="translate(456,630)"><g class="{cls}"><g transform="rotate(-6) translate(0,-104)">'
            f"{content}</g></g></g>")


# ───────────────────────────── body ─────────────────────────────
def ruffle(x0, y0, x1, y1, sag, depth, count, fill="#271d30", crease="#0d0910", hi="#5c4a70", lace=True, lace_col="#5e4c72"):
    tops, bots = [], []
    for i in range(count + 1):
        t = i / count
        x = lerp(x0, x1, t)
        yt = lerp(y0, y1, t) + sag * 4 * t * (1 - t)
        tops.append((x, yt))
        bots.append((x, yt + depth))
    out = []
    if lace:
        d = cr(tops) + "L" + P(bots[-1][0], bots[-1][1] + 5)
        for i in range(count, 0, -1):
            a, b = bots[i], bots[i - 1]
            for j in range(3):
                ax = lerp(a[0], b[0], j / 3)
                bx = lerp(a[0], b[0], (j + 1) / 3)
                ay = lerp(a[1], b[1], j / 3) + 5
                by = lerp(a[1], b[1], (j + 1) / 3) + 5
                bulge = depth * .45 * math.sin(math.pi * (j + .5) / 3) + 4
                d += "Q" + P((ax + bx) / 2, (ay + by) / 2 + bulge) + " " + P(bx, by)
        d += "Z"
        out.append(path(d, lace_col, opacity=".9"))
        out.append(path(d, "url(#pLace)", opacity=".8"))
    d = cr(tops) + "L" + P(*bots[-1])
    for i in range(count, 0, -1):
        a, b = bots[i], bots[i - 1]
        d += "Q" + P((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + depth * .5) + " " + P(*b)
    d += "Z"
    out.append(path(d, fill))
    for i in range(1, count):
        out.append(line(f"M{P(tops[i][0], tops[i][1] + 3)}L{P(bots[i][0], bots[i][1] + 1)}", crease, 1.6, .9))
    for i in range(count):
        mx = (tops[i][0] + tops[i + 1][0]) / 2
        my = (tops[i][1] + tops[i + 1][1]) / 2
        out.append(line(f"M{P(mx, my + 4)}L{P(mx, my + depth + depth * .3)}", hi, 3, .5))
    return "".join(out)


def finger(x0, y0, x1, y1, w, nail=True):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    h = w / 2
    b1 = (x0 + nx * h, y0 + ny * h)
    b2 = (x0 - nx * h, y0 - ny * h)
    t1 = (x1 - ux * h + nx * h * .92, y1 - uy * h + ny * h * .92)
    t2 = (x1 - ux * h - nx * h * .92, y1 - uy * h - ny * h * .92)
    d = (f"M{P(*b1)}L{P(*t1)}Q{P(x1 + nx * h * .92, y1 + ny * h * .92)} {P(x1, y1)}"
         f"Q{P(x1 - nx * h * .92, y1 - ny * h * .92)} {P(*t2)}L{P(*b2)}Z")
    out = path(d, "url(#gHand)", stroke="#d48a76", stroke_width=".9")
    if nail:
        cx, cy = x1 - ux * h * .95, y1 - uy * h * .95
        ang = math.degrees(math.atan2(uy, ux))
        out += (f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(h * .78)}" ry="{n(h * .6)}" transform="rotate({n(ang)} {n(cx)} {n(cy)})" fill="#ffd3da" stroke="#e6a6ae" stroke-width=".6"/>'
                f'<circle cx="{n(cx - ux * 1.5 + nx * 1.5)}" cy="{n(cy - uy * 1.5 + ny * 1.5)}" r="1.1" fill="#fff" opacity=".85"/>')
    return out


def muffin():
    s = []
    s.append('<path d="M282,858L368,858L360,922C340,928 310,928 290,922Z" fill="url(#gLiner)"/>')
    for i in range(13):
        t = i / 12
        xt, xb = lerp(286, 364, t), lerp(293, 357, t)
        s.append(line(f"M{P(xt, 860)}L{P(xb, 923)}", "#8f4a1c", 1.2, .45))
        if i < 12:
            s.append(line(f"M{P(xt + 3.2, 861)}L{P(xb + 2.7, 922)}", "#ffd598", 1.1, .35))
    s.append(path("M282,858L368,858L360,922C340,928 310,928 290,922Z", stroke="#8a4518", stroke_width="1.2", stroke_opacity=".6"))
    pts = []
    for i in range(29):
        phi = math.pi - math.pi * i / 28
        rm = 1 + .03 * math.sin(7 * phi + .5) + .018 * math.sin(13 * phi) + R.uniform(-.012, .012)
        pts.append((326 + 62 * math.cos(phi) * rm, 864 - 62 * math.sin(phi) * rm))
    d = cr(pts) + f"C{P(372, 878)} {P(282, 880)} {P(*pts[0])}Z"
    s.append(path(d, "url(#gMuffin)", stroke="#9a5a24", stroke_width="1.3", stroke_opacity=".7"))
    for _ in range(46):
        a = R.uniform(.15, 2.99)
        rr = R.uniform(.1, .92)
        x = 326 + 58 * math.cos(a) * rr
        y = 862 - 58 * math.sin(a) * rr
        if R.random() < .55:
            s.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(R.uniform(1.5, 3.4))}" ry="{n(R.uniform(1, 2.2))}" fill="#fff3d0" opacity="{R.uniform(.5, .9):.2f}"/>')
        else:
            s.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(R.uniform(1.5, 3.2))}" ry="{n(R.uniform(1, 2))}" fill="#a4602a" opacity="{R.uniform(.35, .6):.2f}"/>')
    s.append(line("M300,822C310,826 318,824 326,830", "#a8642c", 1.6, .6))
    s.append(line("M338,812C346,818 352,816 360,824", "#a8642c", 1.4, .5))
    s.append(line("M296,808C306,800 320,798 330,800", "#fff8e0", 3, .7))
    for _ in range(7):
        s.append(f'<circle cx="{n(R.uniform(286, 366))}" cy="{n(R.uniform(814, 856))}" r="{n(R.uniform(1.6, 2.6))}" fill="#b98af0" opacity=".9"/>')
    return "".join(s)


def body():
    s = []
    # skirt
    s.append('<path d="M342,996C298,1062 236,1170 186,1470H840C792,1250 680,1078 580,996Z" fill="url(#dSkirt)"/>')
    s.append('<path d="M342,996C298,1062 236,1170 186,1470H840C792,1250 680,1078 580,996Z" fill="url(#pLace)" opacity=".2"/>')
    for x0, x1, op in ((380, 300, .5), (430, 400, .45), (480, 500, .45), (530, 610, .5), (560, 700, .45), (600, 790, .4)):
        s.append(line(f"M{x0},1010C{lerp(x0, x1, .3)},1120 {lerp(x0, x1, .7)},1260 {x1},1450", "#3b2c48", 4, op))
        s.append(line(f"M{x0 + 14},1012C{lerp(x0, x1, .3) + 16},1120 {lerp(x0, x1, .7) + 18},1260 {x1 + 22},1450", "#09060b", 3, .6))
    s.append(path("M560,1010C600,1060 660,1160 700,1300", stroke="#6a5680", stroke_width="3", opacity=".35"))
    for d, w, op in (("M600,1030C650,1110 700,1220 730,1330", 16, .1), ("M640,1060C690,1140 735,1240 770,1340", 9, .14),
                     ("M570,1040C600,1120 630,1220 650,1320", 7, .1)):
        s.append(line(d, "#b9a4d8", w, op))
    s.append(ruffle(420, 1316, 840, 1350, 16, 26, 11, fill="#1f1727", hi="#4e3e62", lace_col="#4a3a5c"))
    # bodice
    bod = "M326,790C380,806 530,806 590,788C588,860 584,940 578,1004C520,1016 400,1016 340,1004C336,940 332,860 326,790Z"
    s.append(path(bod, "url(#dBodice)"))
    s.append(path(bod, "url(#pLace)", opacity=".18"))
    for x in (372, 400, 512, 540):
        s.append(line(f"M{x},830C{x - 2},880 {x + 2},950 {x},1000", "#0d0910", 2, .5))
        s.append(line(f"M{x + 6},834C{x + 4},880 {x + 8},950 {x + 6},998", "#4a3a5c", 1.6, .35))
    for k in range(7):  # lacing down the front
        y = 900 + k * 14
        s.append(line(f"M{P(447, y)}L{P(465, y + 7)}M{P(465, y)}L{P(447, y + 7)}", "#9a6ad8", 1.6, .8))
    s.append(line("M446,896V1004M466,896V1004", "#3d2f4a", 1.4, .8))
    s.append(path("M342,996C400,1012 520,1012 578,996L580,1010C520,1024 400,1024 340,1010Z", "#120c16"))
    # neck
    s.append('<path d="M431,596C432,640 430,668 426,694L488,694C484,668 482,640 483,596Z" fill="url(#gNeck)"/>')
    # shoulders / chest
    chest = "M430,662C422,694 398,708 366,716C338,723 318,742 314,774L316,808L598,808L600,774C596,742 576,723 548,716C516,708 492,694 484,662Z"
    s.append(path(chest, "url(#gSkinB)"))
    s.append(line("M430,664C422,694 398,708 366,716C338,723 318,742 314,774", "#fff6e6", 2.6, .85))
    s.append(line("M398,728C416,734 432,732 444,724", "#e3a58f", 1.4, .55))
    s.append(line("M468,724C480,732 496,734 514,728", "#e3a58f", 1.4, .55))
    s.append(path("M548,716C576,723 596,742 600,774L560,774C566,748 560,730 548,716Z", "#f2b9a4", opacity=".5"))
    # mesh yoke
    yoke = "M431,646C424,690 398,728 372,784L540,784C514,728 490,690 483,646Z"
    s.append(path(yoke, "#1b1320", opacity=".45"))
    s.append(path(yoke, "url(#pMesh)"))
    for fx_, fy_ in ((456, 700), (430, 738), (482, 738), (404, 770), (456, 768), (508, 770)):
        petals = "".join(f'<circle cx="{n(fx_ + 4.6 * math.cos(a))}" cy="{n(fy_ + 4.6 * math.sin(a))}" r="2.4"/>'
                         for a in [k * 2 * math.pi / 5 - math.pi / 2 for k in range(5)])
        s.append(f'<g fill="none" stroke="#140d18" stroke-width="1.2" opacity=".75">{petals}<circle cx="{fx_}" cy="{fy_}" r="1.6" fill="#140d18"/></g>')
    for side in (-1, 1):
        pts = []
        for i in range(15):
            t = i / 14
            x, y = bez((431, 646), (424, 690), (398, 728), (372, 784), t) if side == -1 else bez((483, 646), (490, 690), (514, 728), (540, 784), t)
            pts.append((x, y))
        lace = "".join(f'<circle cx="{n(x + side * 2)}" cy="{n(y)}" r="2.8" fill="none" stroke="#1b1320" stroke-width="1.4"/>' for x, y in pts)
        s.append(lace)
        s.append(line(cr(pts), "#1b1320", 2.2, .95))
    # choker + bow + gem
    s.append('<path d="M428,634C444,644 470,644 486,634L487,648C470,658 444,658 427,648Z" fill="#1b1320"/>')
    s.append(line("M430,637C446,646 468,646 484,637", "#5a4868", 1.2, .7))
    s.append('<path d="M456,650C444,636 428,638 430,652C432,664 446,662 456,650Z" fill="url(#dSatin)"/>'
             '<path d="M456,650C468,636 484,638 482,652C480,664 466,662 456,650Z" fill="url(#dSatin)"/>'
             '<ellipse cx="456" cy="651" rx="5.5" ry="6.5" fill="#2a2033"/>')
    s.append('<circle cx="456" cy="661" r="2.6" fill="none" stroke="#e2cf9e" stroke-width="1.4"/>')
    gem = "M456,664L467,670L469,684L462,695L450,695L443,684L445,670Z"
    s.append(path(gem, "url(#gGem)", stroke="#e2cf9e", stroke_width="1.6"))
    s.append(path("M451,672L461,672L463,684L456,689L449,684Z", "#c49af8", opacity=".85"))
    s.append(path("M456,664L467,670L461,672L451,672L445,670Z", "#6a30c0", opacity=".7"))
    s.append(path("M449,684L456,689L463,684L462,695L450,695Z", "#4a1a90", opacity=".6"))
    s.append('<path class="glint" d="M452,673l1,-4 1,4 4,1 -4,1 -1,4 -1,-4 -4,-1z" fill="#fff"/>')
    # upper sleeves
    slL = "M322,776C290,788 254,826 242,880C230,936 238,986 262,1012C290,1022 330,1018 352,1004C360,940 366,860 360,786Z"
    slR = "M594,776C628,790 664,828 672,884C680,940 668,990 640,1012C612,1022 574,1016 556,1002C552,940 548,860 552,788Z"
    for d, g in ((slL, "url(#dSleeveL)"), (slR, "url(#dSleeveR)")):
        s.append(path(d, g))
        s.append(path(d, "url(#pLace)", opacity=".28"))
    for a, b in (((300, 800), (262, 990)), ((330, 796), (300, 1000)), ((612, 800), (652, 990)), ((584, 798), (604, 1006))):
        s.append(line(f"M{P(*a)}Q{P(a[0] - 18 if a[0] < 450 else a[0] + 18, (a[1] + b[1]) / 2)} {P(*b)}", "#0b070e", 3, .6))
    s.append(line("M322,778C290,790 254,828 242,882C232,930 236,970 250,996", "#c9b0e0", 2.2, .55))
    s.append(line("M600,780C630,794 662,830 670,884", "#7a6590", 1.8, .4))
    # neckline frill
    s.append(ruffle(310, 772, 604, 770, 14, 24, 13, lace_col="#7d6a94"))
    # chest bow
    s.append(bow(456, 818, 0, 1.0, dark=True))
    # purple bow on the right sleeve
    s.append(bow(648, 870, 12, .78))
    # forearms
    s.append(path("M246,1002C236,972 240,936 258,902C276,896 312,896 326,904C340,936 344,976 334,1006C312,1024 268,1024 246,1002Z", "url(#dFore)"))
    s.append(path("M246,1002C236,972 240,936 258,902C276,896 312,896 326,904C340,936 344,976 334,1006C312,1024 268,1024 246,1002Z", "url(#pLace)", opacity=".25"))
    s.append(line("M262,1000C256,970 260,940 270,912", "#0b070e", 2.4, .6) + line("M310,1004C318,972 316,940 308,912", "#0b070e", 2.4, .6))
    s.append(line("M250,996C240,968 244,936 258,906", "#c9b0e0", 2, .5))
    foreR = "M640,980C600,960 480,900 420,890C404,888 392,900 390,914C390,932 400,944 418,946C480,958 580,1010 620,1030C646,1020 652,996 640,980Z"
    s.append(path(foreR, "url(#dFore)"))
    s.append(path(foreR, "url(#pLace)", opacity=".25"))
    s.append(line("M600,990C560,968 500,940 440,920", "#0b070e", 2.6, .6) + line("M612,1012C570,990 510,962 450,940", "#0b070e", 2.2, .5))
    s.append(line("M630,982C590,962 490,910 424,894", "#6a5680", 1.8, .45))
    # hands: backs of hands
    s.append(path("M262,918C258,896 262,872 276,860C284,854 292,858 292,866L294,916C284,924 270,924 262,918Z", "url(#gHand)", stroke="#d99a86", stroke_width="1.1"))
    s.append(path("M394,920C400,896 396,872 382,860C374,854 366,858 366,866L364,916C374,924 388,926 394,920Z", "url(#gHand)", stroke="#d99a86", stroke_width="1.1"))
    # cuffs
    s.append(f'<g transform="translate(292,914) rotate(180)">{ruffle(-42, 0, 42, 0, -8, 13, 6, fill="#2e2338", hi="#7a6890", lace_col="#a593bd")}</g>')
    s.append(f'<g transform="translate(400,922) rotate(104)">{ruffle(-34, 0, 34, 0, -6, 12, 5, fill="#2e2338", hi="#7a6890", lace_col="#a593bd")}</g>')
    # muffin
    s.append(muffin())
    # fingers (left hand → pointing right; right hand → pointing left)
    for (x0, y0, x1, y1, w) in ((284, 872, 316, 870, 12.5), (282, 886, 320, 885, 13), (284, 900, 315, 900, 12), (288, 912, 306, 913, 10)):
        s.append(finger(x0, y0, x1, y1, w))
    for (x0, y0, x1, y1, w) in ((378, 872, 345, 871, 12.5), (380, 886, 342, 886, 13), (378, 900, 347, 901, 12), (373, 912, 355, 913, 10)):
        s.append(finger(x0, y0, x1, y1, w))
    s.append(finger(272, 868, 292, 846, 12))
    s.append(finger(388, 870, 368, 847, 12))
    return "".join(s)


# ───────────────────────────── table, mug, steam ─────────────────────────────
def table():
    s = []
    s.append('<rect x="-40" y="1196" width="620" height="270" fill="url(#gUnder)"/>')
    s.append('<path d="M-80,1150C-80,1188 76,1214 225,1214C374,1214 530,1188 530,1150V1178C530,1216 374,1242 225,1242C76,1242 -80,1216 -80,1178Z" fill="url(#gTableEdge)"/>')
    s.append('<ellipse cx="225" cy="1150" rx="305" ry="64" fill="url(#gTableTop)"/>')
    grain = []
    for k in range(9):
        y = 1098 + k * 13 + R.uniform(-3, 3)
        pts = [(-80 + j * 76, y + R.uniform(-3, 3) + (j - 4) ** 2 * .3) for j in range(9)]
        grain.append(line(cr(pts), "#7a4424", R.uniform(.8, 1.6), R.uniform(.18, .35)))
    s.append('<g clip-path="url(#cTable)">' + "".join(grain) +
             '<ellipse cx="40" cy="1112" rx="150" ry="18" fill="#fff0c8" opacity=".35"/>'
             '<ellipse cx="200" cy="1110" rx="66" ry="11" fill="#5a2e14" opacity=".35"/>'
             '<path d="M120,1110C130,1140 140,1170 150,1200L190,1200C182,1170 176,1140 170,1110Z" fill="#fff6e0" opacity=".18"/>'
             '</g>')
    s.append(line("M-80,1150C-80,1110 76,1086 225,1086C374,1086 530,1110 530,1150", "#ffe2a6", 2.4, .75))
    s.append(line("M-80,1152C-80,1190 76,1214 225,1214C374,1214 530,1190 530,1152", "#ffcf8a", 1.6, .5))
    # mug
    s.append('<path d="M218,1010C254,1006 262,1064 218,1070V1056C244,1052 242,1022 218,1024Z" fill="#e9dfd2" stroke="#b8a490" stroke-width="1"/>')
    s.append('<path d="M112,990V1092C112,1108 218,1108 218,1092V990Z" fill="url(#gMug)"/>')
    s.append('<ellipse cx="165" cy="990" rx="53" ry="12" fill="#fffdf8" stroke="#d9cdbf" stroke-width="1"/>')
    s.append('<ellipse cx="165" cy="992" rx="46" ry="8.5" fill="url(#gCoffee)"/>')
    s.append('<ellipse cx="152" cy="990" rx="16" ry="2.6" fill="#d9a77a" opacity=".55"/>')
    s.append(line("M116,996V1088", "#fff", 3, .9))
    # fox silhouette logo
    s.append('<g transform="translate(160,1050) scale(.9)" fill="#1e1416">'
             '<path d="M-6,-24L-2,-14L4,-14L8,-24L9,-10C12,-6 11,-1 6,1C10,8 12,16 10,22H-8C-12,14 -10,6 -4,1C-9,-1 -10,-6 -8,-10Z"/>'
             '<path d="M9,20C22,22 28,10 22,0C30,8 30,24 16,28C10,30 4,28 2,24Z"/>'
             '</g>')
    # steam
    for i, (x, dx) in enumerate(((150, -10), (168, 12), (182, -6))):
        d = f"M{x},984C{x + dx},960 {x - dx},944 {x + dx * .6},918C{x + dx * 1.2},896 {x - dx * .4},876 {x + dx * .4},850"
        s.append(f'<path class="steam s{i}" d="{d}" fill="none" stroke="url(#gSteam)" stroke-width="{7 - i}" stroke-linecap="round"/>')
    return "".join(s)


def heart():
    return ('<g class="heart" transform="translate(600,420)"><g class="heart-in">'
            '<path d="M0,10C-14,0 -22,-8 -22,-18C-22,-26 -16,-31 -10,-31C-5,-31 -2,-28 0,-24C2,-28 5,-31 10,-31C16,-31 22,-26 22,-18C22,-8 14,0 0,10Z" fill="#b98af0" stroke="#fff" stroke-width="2.5"/>'
            '<path d="M-14,-20C-14,-24 -11,-26 -8,-26" stroke="#fff" stroke-width="2.5" fill="none" stroke-linecap="round" opacity=".8"/>'
            '</g></g>')


def build_scene():
    clips = (f'<clipPath id="cFace"><path d="{FACE}"/></clipPath>'
             '<clipPath id="cSclera"><path d="M-31,-4C-29,-22 -12,-29 4,-29C18,-29 28,-23 31,-13C33,6 24,25 6,29C-10,32 -26,20 -31,-4Z"/></clipPath>'
             '<clipPath id="cMouth"><path d="M-14,66C-6,70 8,70 15,64C13,77 6,84 -1,84C-8,84 -13,76 -14,66Z"/></clipPath>'
             f'<clipPath id="cDome"><path d="{DOME}"/></clipPath>'
             '<clipPath id="cTable"><ellipse cx="225" cy="1150" rx="305" ry="64"/></clipPath>')
    return (f"<defs>{SCENE_DEFS}{clips}</defs>"
            + build_tail()
            + head_wrap(head_back())
            + body()
            + head_wrap(head_front())
            + table()
            + heart())


# ───────────────────────────── fx layer ─────────────────────────────
def build_fx():
    defs = ('<radialGradient id="xVig" cx="405" cy="640" r="900" gradientUnits="userSpaceOnUse">'
            '<stop offset=".45" stop-color="#1a0c04" stop-opacity="0"/><stop offset="1" stop-color="#1a0c04" stop-opacity=".62"/></radialGradient>'
            '<radialGradient id="xGlow" cx="160" cy="260" r="520" gradientUnits="userSpaceOnUse">'
            '<stop offset="0" stop-color="#fff6d8" stop-opacity=".38"/><stop offset="1" stop-color="#fff6d8" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="xMote"><stop offset="0" stop-color="#fffbe8"/><stop offset=".4" stop-color="#fff3c4" stop-opacity=".7"/><stop offset="1" stop-color="#ffe9a0" stop-opacity="0"/></radialGradient>')
    motes = []
    for i in range(34):
        x, y = R.uniform(10, 640), R.uniform(80, 1100)
        r = R.uniform(2, 5.5)
        dur = R.uniform(9, 18)
        delay = -R.uniform(0, dur)
        dx, dy = R.uniform(-30, 50), R.uniform(-140, -60)
        op = R.uniform(.45, .95)
        motes.append(f'<circle class="mote" cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="url(#xMote)" '
                     f'style="--d:{dur:.1f}s;--delay:{delay:.1f}s;--dx:{dx:.0f}px;--dy:{dy:.0f}px;--o:{op:.2f}"/>')
    return (f"<defs>{defs}</defs>"
            '<rect width="810" height="1440" fill="url(#xGlow)" style="mix-blend-mode:screen"/>'
            + "".join(motes) +
            '<rect width="810" height="1440" fill="url(#xVig)"/>')


# ───────────────────────────── page ─────────────────────────────
CSS = r"""
:root {
  /* Layout: one framed 9:16 painting centred on an espresso ground, a single caption line beneath. */
  --ground: #170f0b;
  --ground-2: #24170f;
  --ink: #f4e6c9;
  --muted: #b79c78;
  --lilac: #c4a1f5;
  --frame-edge: #4a3020;
  --font-display: "Kaisei Decol", "Hiragino Mincho ProN", Georgia, serif;
  --font-body: "Zen Maru Gothic", ui-rounded, "Hiragino Maru Gothic ProN", system-ui, sans-serif;
  color-scheme: dark;
}
html { height: 100%; }
body {
  min-height: 100%;
  margin: 0;
  background: radial-gradient(120% 80% at 50% 30%, var(--ground-2), var(--ground) 70%) fixed, var(--ground);
  color: var(--ink);
  font-family: var(--font-body);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  box-sizing: border-box;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 18px 16px;
}
.stage {
  width: 100%;
  display: grid;
  place-items: center;
}
.frame {
  position: relative;
  width: min(100%, 560px, calc((100vh - 120px) * 9 / 16));
  width: min(100%, 560px, calc((100dvh - 120px - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px)) * 9 / 16));
  min-width: min(100%, 260px);
  aspect-ratio: 9 / 16;
  max-width: 100%;
  border-radius: 20px;
  overflow: hidden;
  background: #c98236;
  box-shadow: 0 0 0 1px var(--frame-edge), 0 30px 80px -20px #000, 0 0 120px -30px #f0b05a55;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.frame:focus-visible { outline: 3px solid var(--lilac); outline-offset: 4px; }
.layer { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.bg { will-change: transform; }
.fx { pointer-events: none; }
.caption {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: baseline;
  gap: 4px 14px;
  text-align: center;
  max-width: 560px;
}
.caption h1 {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 1.15rem;
  letter-spacing: .02em;
  text-wrap: balance;
}
.caption p { margin: 0; color: var(--muted); font-size: .8rem; letter-spacing: .04em; }
.caption b { color: var(--lilac); font-weight: 500; }

/* ── motion ── */
.blink { animation: blink 7s infinite; }
@keyframes blink {
  0%, 44%, 47.5%, 89%, 93.5%, 100% { transform: scaleY(1); }
  45.8% { transform: scaleY(.06); }
  90.2% { transform: scaleY(.06); }
  91.3% { transform: scaleY(1); }
  92.4% { transform: scaleY(.06); }
}
.sway { animation: sway 6.5s ease-in-out infinite alternate; }
@keyframes sway { from { transform: rotate(-1.4deg); } to { transform: rotate(1.6deg); } }
.tail { animation: tail 3.6s ease-in-out infinite alternate; }
@keyframes tail { from { transform: rotate(-3deg); } to { transform: rotate(4deg); } }
.ear-l { animation: twitch 6s infinite; }
.ear-r { animation: twitch 6s 2.7s infinite; }
@keyframes twitch {
  0%, 86%, 100% { transform: rotate(0); }
  88% { transform: rotate(-9deg); }
  90.5% { transform: rotate(5deg); }
  93% { transform: rotate(-3deg); }
  95.5% { transform: rotate(0); }
}
.steam { animation: steam 4.2s ease-in-out infinite; opacity: 0; }
.steam.s1 { animation-delay: -1.4s; }
.steam.s2 { animation-delay: -2.8s; }
@keyframes steam {
  0% { opacity: 0; transform: translateY(14px); }
  35% { opacity: .9; }
  100% { opacity: 0; transform: translateY(-46px); }
}
.mote { animation: drift var(--d) linear var(--delay) infinite; opacity: 0; }
@keyframes drift {
  0% { transform: translate(0, 0); opacity: 0; }
  15%, 80% { opacity: var(--o); }
  100% { transform: translate(var(--dx), var(--dy)); opacity: 0; }
}
.glint { transform-box: fill-box; transform-origin: center; animation: glint 3.2s ease-in-out infinite; }
@keyframes glint { 0%, 70%, 100% { opacity: 0; transform: scale(.3); } 80% { opacity: 1; transform: scale(1.2); } 90% { opacity: .2; transform: scale(.6); } }

/* ── tap reaction ── */
.eyes-happy { opacity: 0; }
.heart { opacity: 0; }
.happy .eyes-open { opacity: 0; }
.happy .eyes-happy { opacity: 1; }
.happy .tail { animation: wag .32s ease-in-out infinite alternate; }
@keyframes wag { from { transform: rotate(-6deg); } to { transform: rotate(7deg); } }
.happy .ear-l, .happy .ear-r { animation: perk .5s ease-out; }
@keyframes perk { 0% { transform: rotate(0); } 40% { transform: rotate(-12deg); } 100% { transform: rotate(0); } }
.happy .heart { opacity: 1; }
.happy .heart-in { animation: pop 1.5s ease-out forwards; }
@keyframes pop {
  0% { transform: translate(0, 20px) scale(.2); opacity: 0; }
  20% { transform: translate(0, 0) scale(1.15); opacity: 1; }
  100% { transform: translate(18px, -90px) scale(.9); opacity: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .blink, .sway, .tail, .ear-l, .ear-r, .steam, .mote, .glint,
  .happy .tail, .happy .ear-l, .happy .ear-r, .happy .heart-in { animation: none; }
  .steam { opacity: .6; }
  .mote { opacity: .6; }
}
"""

JS = r"""
(() => {
  const frame = document.querySelector('.frame');
  const scene = document.querySelector('.scene');
  const count = document.getElementById('shape-count');
  if (count) {
    const n = document.querySelectorAll('.frame :is(path,circle,ellipse,rect)').length;
    count.textContent = n.toLocaleString();
  }
  let timer;
  const hi = () => {
    scene.classList.remove('happy');
    void scene.getBoundingClientRect();
    scene.classList.add('happy');
    clearTimeout(timer);
    timer = setTimeout(() => scene.classList.remove('happy'), 1600);
  };
  frame.addEventListener('click', hi);
  frame.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); hi(); }
  });
})();
"""


def main():
    bg = build_bg()
    scene = build_scene()
    fx = build_fx()
    html = f"""<title>Golden Hour Fox Girl</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Kaisei+Decol:wght@500&family=Zen+Maru+Gothic:wght@500&display=swap">
<style>{CSS}</style>
<main class="stage">
<div class="frame" role="button" tabindex="0" aria-label="A fox girl with golden twin-tails and violet eyes holding a muffin in a sunlit café. Tap to say hi.">
<svg class="layer bg" viewBox="0 0 810 1440" aria-hidden="true">{bg}</svg>
<svg class="layer scene" viewBox="0 0 810 1440" aria-hidden="true">{scene}</svg>
<svg class="layer fx" viewBox="0 0 810 1440" aria-hidden="true">{fx}</svg>
</div>
</main>
<footer class="caption">
<h1>Golden hour at the café</h1>
<p><b id="shape-count">1,300+</b> SVG shapes · no image files · tap her to say hi</p>
</footer>
<script>{JS}</script>
"""
    if not FRAGMENT:
        html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + html.replace('<main class="stage">', '</head>\n<body>\n<main class="stage">', 1)
                + '</body>\n</html>\n')
    with open(OUT, "w") as f:
        f.write(html)
    print(f"wrote {OUT}: {len(html) / 1024:.1f} KB")


main()
