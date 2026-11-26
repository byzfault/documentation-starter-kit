"""Generate the page banners in public/banners.

Every banner is drawn by this script. No stock, no image model.
Run:  python scripts/banners.py [name ...]     (needs numpy, scipy, pillow)
"""
import os
import sys
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from PIL import Image

OUT_W, OUT_H = 1800, 600
S = 2  # supersample
W, H = OUT_W * S, OUT_H * S
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'public', 'banners')

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
XX /= S
YY /= S  # coordinates in output pixels


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)


# Brand palette (brand guidelines v1.0): Ink ground, Signal Blue into Glow into Mist. One accent.
INK, BLUE, GLOW, MIST = '#11151C', '#2F4BFF', '#7B93FF', '#F6F7F9'
PAL = {'brand': [BLUE, GLOW, '#B4C1FF', MIST]}
BG = {'brand': ('#0C0F15', '#141923')}


def ramp(t, pal):
    cols = np.stack([hexc(c) for c in PAL[pal]])
    t = np.clip(t, 0, 1) * (len(cols) - 1)
    i = np.clip(np.floor(t).astype(int), 0, len(cols) - 2)
    f = (t - i)[..., None]
    return cols[i] * (1 - f) + cols[i + 1] * f


def fbm(rng, scale, octaves=4, shape=(H, W), gain=0.5):
    """Smooth fractal noise in 0..1. scale = feature size in output px."""
    out = np.zeros(shape, dtype=np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        cell = scale * S / (2 ** o)
        gh, gw = int(shape[0] / cell) + 4, int(shape[1] / cell) + 4
        g = rng.random((gh, gw)).astype(np.float32)
        z = ndi.zoom(g, (shape[0] / (gh - 3), shape[1] / (gw - 3)), order=3)
        out += amp * z[:shape[0], :shape[1]]
        tot += amp
        amp *= gain
    out /= tot
    lo, hi = np.percentile(out, [1, 99])
    return np.clip((out - lo) / (hi - lo), 0, 1)


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def blur(img, sigma):
    """Gaussian blur, sigma in output px. Big blurs run at reduced size."""
    s = sigma * S
    if s > 12:
        k = 4
        small = img.reshape(H // k, k, W // k, k, -1).mean((1, 3))
        small = ndi.gaussian_filter(small, (s / k, s / k, 0))
        return ndi.zoom(small, (k, k, 1), order=1)
    return ndi.gaussian_filter(img, (s, s, 0))


_buf = []


def splat(light, x, y, col, w=1.0):
    """Queue points (output px coords) of light. col is (n,3) or (3,). flush() draws them."""
    x, y = np.asarray(x, dtype=np.float32), np.asarray(y, dtype=np.float32)
    xi = np.round(x * S).astype(np.int64)
    yi = np.round(y * S).astype(np.int64)
    ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
    col = np.broadcast_to(col, x.shape + (3,))[ok]
    w = np.broadcast_to(np.asarray(w, dtype=np.float32), x.shape)[ok]
    _buf.append(((yi * W + xi)[ok], (col * w[:, None]).astype(np.float32)))


def flush(light):
    if not _buf:
        return light
    idx = np.concatenate([b[0] for b in _buf])
    cw = np.concatenate([b[1] for b in _buf])
    _buf.clear()
    for c in range(3):
        light[..., c] += np.bincount(idx, weights=cw[:, c], minlength=W * H).reshape(H, W)
    return light


def background(pal, glow=(0.7, 0.5), glow_col=None, strength=0.22):
    c0, c1 = hexc(BG[pal][0]), hexc(BG[pal][1])
    t = (0.55 * XX / OUT_W + 0.45 * (1 - YY / OUT_H))[..., None]
    bg = c0 * (1 - t) + c1 * t
    gc = hexc(glow_col or PAL[pal][0])
    gx, gy = glow[0] * OUT_W, glow[1] * OUT_H
    g = np.exp(-(((XX - gx) / (0.42 * OUT_W)) ** 2 + ((YY - gy) / (0.75 * OUT_H)) ** 2))
    return bg + gc * g[..., None] * strength


def finish(name, bg, light, rng, bloom=0.7, gain=1.0):
    light = np.maximum(flush(light), 0) * gain
    light = light + bloom * 0.55 * blur(light, 5) + bloom * 0.45 * blur(light, 26)
    img = 1 - (1 - np.clip(bg, 0, 1)) * np.exp(-light)
    # soft vignette
    v = 1 - 0.28 * (((XX / OUT_W - 0.5) * 1.15) ** 2 + ((YY / OUT_H - 0.5) * 1.3) ** 2)
    img *= v[..., None]
    img = img.reshape(OUT_H, S, OUT_W, S, 3).mean((1, 3))
    img += rng.normal(0, 0.011, (OUT_H, OUT_W, 1)).astype(np.float32)
    out = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    os.makedirs(OUT_DIR, exist_ok=True)
    Image.fromarray(out).save(os.path.join(OUT_DIR, name + '.webp'), quality=84, method=6)
    print('wrote', name)


def lines_from_scalar(f, width=0.9, bold_every=0):
    """Iso-lines where f crosses n + 0.5. Constant width in output px."""
    gy, gx = np.gradient(f)
    grad = np.sqrt(gx ** 2 + gy ** 2) * S + 1e-6
    fr = f - np.floor(f)
    dist = np.abs(fr - 0.5) / grad
    line = np.exp(-(dist / width) ** 2)
    if bold_every:
        k = np.floor(f).astype(int) % bold_every == 0
        line = np.where(k, np.exp(-(dist / (width * 1.9)) ** 2) * 1.5, line * 0.75)
    return line


# ---------------------------------------------------------------- motifs

def orb(name, pal, seed):
    """Home: a warped ring of light."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=(0.72, 0.5), strength=0.10)
    n1, n2 = fbm(rng, 420, 3), fbm(rng, 420, 3)
    fine = fbm(rng, 90, 3)
    cx, cy = 0.83 * OUT_W, 0.52 * OUT_H
    dx = (XX - cx) + (n1 - 0.5) * 300
    dy = (YY - cy) * 1.25 + (n2 - 0.5) * 300
    r = np.sqrt(dx ** 2 + dy ** 2)
    ang = np.arctan2(dy, dx)
    R = 185
    wid = 62 + 46 * np.sin(ang * 2 + 1.1) + 30 * (fine - 0.5)
    ring = np.exp(-((r - R) / np.maximum(wid, 18)) ** 2)
    inner = smooth((r - R * 0.35) / (R * 0.6))
    ring *= 0.25 + 0.75 * inner
    ring *= smooth((XX / OUT_W - 0.64) / 0.10)  # keep the lockup side clear
    t = 0.5 + 0.5 * np.sin(ang * 1.0 + 0.6 + (n1 - 0.5) * 3)
    col = ramp(t * 0.85 + 0.15 * fine, pal)
    light = col * (ring * 1.25)[..., None]
    # fine silk strands along the ring
    strands = lines_from_scalar((r + fine * 40) / 9.0, width=0.7)
    light += col * (strands * ring * 0.55)[..., None]
    finish(name, bg, light, rng, bloom=0.9)


def flow(name, pal, seed, n=7000, steps=420, scale=380, spread=2.6, band=(0.15, 0.5, 0.9), glow=(0.6, 0.5)):
    """Silk strands following a noise field, left to right."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=glow, strength=0.16)
    small = (H // 8, W // 8)
    field = fbm(rng, scale / 8 * 1.0, 3, shape=small)
    mask = fbm(rng, 520 / 8, 2, shape=small)
    x = rng.uniform(-0.15 * OUT_W, 1.05 * OUT_W, n).astype(np.float32)
    y = rng.uniform(-0.1 * OUT_H, 1.1 * OUT_H, n).astype(np.float32)
    tone = rng.random(n).astype(np.float32)
    light = np.zeros((H, W, 3), dtype=np.float32)

    def look(a, px, py):
        return ndi.map_coordinates(a, [np.clip(py * S / 8, 0, small[0] - 1), np.clip(px * S / 8, 0, small[1] - 1)], order=1)

    t0 = look(field, x, y)
    col = ramp(0.75 * t0 + 0.25 * tone, pal)
    wgt = (0.25 + tone ** 3 * 1.6) * 0.30
    for _ in range(steps):
        a = (look(field, x, y) - 0.5) * spread
        x += np.cos(a) * 0.9
        y += np.sin(a) * 0.9
        m = look(mask, x, y)
        env = smooth((m - band[0]) / (band[1] - band[0])) * (0.35 + 0.65 * smooth(x / OUT_W / band[2] + 0.1))
        splat(light, x, y, col, wgt * env)
    finish(name, bg, light, rng, bloom=0.8)


def converge(name, pal, seed):
    """Agentic content designer: parallel detectors, one writer."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=(0.62, 0.5), strength=0.2)
    light = np.zeros((H, W, 3), dtype=np.float32)
    xm, ym = 0.60 * OUT_W, 0.5 * OUT_H
    K = 9
    ts = np.linspace(0, 1, 2600, dtype=np.float32)
    for k in range(K):
        y0 = OUT_H * (0.07 + 0.86 * k / (K - 1))
        col = ramp(np.array(k / (K - 1)) * 0.75, pal)
        for s in range(46):
            j = rng.normal(0, 13)
            ph, fr = rng.uniform(0, 6.28), rng.uniform(1.5, 4)
            e = smooth(ts) ** 1.15
            x = -20 + (xm + 20) * ts
            y = y0 + (ym - y0) * e + j * (1 - e) ** 0.8 + np.sin(ts * fr * 3 + ph) * 2.2 * (1 - e)
            w = 0.14 * (0.4 + rng.random() ** 2 * 1.8) * (0.45 + 0.55 * ts)
            splat(light, x, y, col, w)
        # stream head marker
        splat(light, np.full(40, 0.045 * OUT_W) + rng.normal(0, 1.2, 40), np.full(40, y0) + rng.normal(0, 1.2, 40), col, 0.5)
    # the single writer
    tx = np.linspace(xm, OUT_W + 20, 2600, dtype=np.float32)
    white = hexc(PAL[pal][3])
    for s in range(60):
        j = rng.normal(0, 1.6)
        splat(light, tx, np.full_like(tx, ym + j), white, 0.06)
    # mechanical checks: evenly spaced gates on the output line
    for gx in np.linspace(0.70, 0.94, 5):
        gy = np.linspace(ym - 34, ym + 34, 300, dtype=np.float32)
        for o in (-0.5, 0.5):
            splat(light, np.full_like(gy, gx * OUT_W + o), gy, hexc(PAL[pal][2]), 0.10 * np.exp(-((gy - ym) / 26) ** 4))
    # merge node
    d = np.sqrt((XX - xm) ** 2 + (YY - ym) ** 2)
    light += white * (np.exp(-(d / 7) ** 2) * 1.6 + np.exp(-((d - 19) / 1.3) ** 2) * 0.7)[..., None]
    finish(name, bg, light, rng, bloom=0.9)


def lattice(name, pal, seed, n=150, glow=(0.68, 0.45)):
    """A network: nodes and the links between them."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=glow, strength=0.18)
    light = np.zeros((H, W, 3), dtype=np.float32)
    cols, rows = 21, 8
    gx, gy = np.meshgrid(np.arange(cols), np.arange(rows))
    px = ((gx + 0.5 + rng.uniform(-0.42, 0.42, gx.shape)) / cols * 1.1 - 0.05).ravel() * OUT_W
    py = ((gy + 0.5 + rng.uniform(-0.42, 0.42, gy.shape)) / rows * 1.2 - 0.1).ravel() * OUT_H
    depth = rng.random(px.size)
    m = fbm(rng, 420, 2)
    act = m[np.clip((py * S).astype(int), 0, H - 1), np.clip((px * S).astype(int), 0, W - 1)]
    act = smooth((act - 0.3) / 0.45) * (0.3 + 0.7 * smooth(px / OUT_W * 1.3))
    tree = cKDTree(np.c_[px, py])
    _, nb = tree.query(np.c_[px, py], k=4)
    seen = set()
    for i in range(px.size):
        for j in nb[i, 1:]:
            if (j, i) in seen:
                continue
            seen.add((i, j))
            L = np.hypot(px[i] - px[j], py[i] - py[j])
            t = np.linspace(0, 1, int(L * S * 1.6) + 2, dtype=np.float32)
            a = act[i] * (1 - t) + act[j] * t
            col = ramp(a * 0.7 + 0.1, pal)
            splat(light, px[i] + (px[j] - px[i]) * t, py[i] + (py[j] - py[i]) * t, col, 0.02 + 0.32 * a ** 2)
    light = blur(flush(light), 0.5)
    for i in range(px.size):
        r = 1.6 + 4.2 * depth[i] * (0.4 + act[i])
        x0, x1 = int((px[i] - 30) * S), int((px[i] + 30) * S)
        y0, y1 = int((py[i] - 30) * S), int((py[i] + 30) * S)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
        if x0 >= x1 or y0 >= y1:
            continue
        d = np.sqrt((XX[y0:y1, x0:x1] - px[i]) ** 2 + (YY[y0:y1, x0:x1] - py[i]) ** 2)
        dot = smooth((r - d) / 1.2 + 0.5)
        ring = np.exp(-((d - r * 2.4) / 0.9) ** 2) * (act[i] > 0.6) * 0.5
        col = ramp(np.array(act[i] * 0.8 + 0.2), pal)
        light[y0:y1, x0:x1] += col * ((dot * (0.25 + 1.6 * act[i]) + ring))[..., None]
    finish(name, bg, light, rng, bloom=0.85)


def trails(name, pal, seed):
    """Traffic counting: vehicles as light crossing a count line."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=(0.62, 0.5), strength=0.12)
    light = np.zeros((H, W, 3), dtype=np.float32)
    lanes = 8
    xc = 0.62 * OUT_W
    warm, cool, white = hexc(MIST), hexc(GLOW), hexc(MIST)
    skew = -0.10  # slight tilt of the whole carriageway
    for ln in range(lanes):
        yl = OUT_H * (0.10 + 0.80 * ln / (lanes - 1))
        going_right = ln >= lanes // 2
        base = cool if going_right else warm
        # lane marking
        tx = np.arange(-50, OUT_W + 50, 0.5, dtype=np.float32)
        dash = ((tx // 26) % 2 == 0)
        ym = yl + OUT_H * 0.057
        if ln < lanes - 1:
            splat(light, tx, ym + (tx - xc) * skew, white, 0.012 * dash if ln != lanes // 2 - 1 else 0.035)
        x = rng.uniform(-200, 0)
        while x < OUT_W + 100:
            length = rng.choice([70, 110, 160, 260, 420], p=[0.3, 0.3, 0.2, 0.13, 0.07]) * rng.uniform(0.8, 1.2)
            t = np.arange(0, length, 0.35, dtype=np.float32)
            head = t / length if going_right else 1 - t / length
            crossing = (x < xc < x + length)
            for off, a in ((-5.5, 1.0), (5.5, 1.0), (0, 0.25)):
                for jj in (-0.5, 0, 0.5):
                    px = x + t
                    py = yl + off + jj + (px - xc) * skew
                    col = base * 0.7 + white * 0.3 if crossing else base
                    splat(light, px, py, col, a * (0.03 + 0.20 * head ** 3) * (1.7 if crossing else 0.8))
            x += length + rng.uniform(60, 380)
    light = blur(flush(light), 0.6) * 3.2
    # the count line
    d = np.abs((XX - xc) + (YY - OUT_H / 2) * 0.12)
    light += white * (np.exp(-(d / 1.1) ** 2) * 0.95 + np.exp(-(d / 14) ** 2) * 0.10)[..., None]
    finish(name, bg, light, rng, bloom=1.0)


def contours(name, pal, seed, mode='terrain', levels=15, glow=(0.65, 0.5)):
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=glow, strength=0.16)
    n = fbm(rng, 520, 3, gain=0.42)
    if mode == 'terrain':
        f = n * levels
        tone = n
        env = smooth((n - 0.12) / 0.5) * (0.4 + 0.6 * smooth(XX / OUT_W * 1.2))
        line = lines_from_scalar(f, 0.8, bold_every=5)
    elif mode == 'rings':  # growth rings
        cx, cy = 0.83 * OUT_W, 1.25 * OUT_H
        r = np.sqrt((XX - cx) ** 2 + ((YY - cy) * 1.1) ** 2)
        f = (r + (n - 0.5) * 170) / 24.0
        tone = np.clip(1.25 - r / (OUT_W * 0.8), 0, 1)
        env = (0.18 + 0.82 * tone ** 1.6) * (0.75 + 0.5 * fbm(rng, 200, 2))
        line = lines_from_scalar(f, 0.85, bold_every=4)
    else:  # ripples from two sources
        a = (0.70 * OUT_W, 0.48 * OUT_H)
        b = (0.36 * OUT_W, 0.95 * OUT_H)
        r1 = np.sqrt((XX - a[0]) ** 2 + (YY - a[1]) ** 2)
        r2 = np.sqrt((XX - b[0]) ** 2 + (YY - b[1]) ** 2)
        l1 = lines_from_scalar(r1 / 26.0, 0.9) * np.exp(-r1 / 620)
        l2 = lines_from_scalar(r2 / 26.0, 0.9) * np.exp(-r2 / 420) * 0.55
        line = l1 + l2 + 2.2 * l1 * l2
        tone = np.exp(-r1 / 520)
        env = 0.9
        d = r1
        line = line + np.exp(-(d / 6) ** 2) * 2.5
    col = ramp(tone * 0.9, pal)
    light = col * (line * env * 0.85)[..., None]
    finish(name, bg, light, rng, bloom=0.8)


def dots(name, pal, seed, cell=20.0, tokenise=True):
    """Halftone field. For MDES: solid values on the left become hollow tokens on the right."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=(0.66, 0.5), strength=0.2)
    n = fbm(rng, 480, 3)
    # rotate the grid a touch
    th = -0.16
    u = XX * np.cos(th) - YY * np.sin(th)
    v = XX * np.sin(th) + YY * np.cos(th)
    cu, cv = np.floor(u / cell), np.floor(v / cell)
    du, dv = u - (cu + 0.5) * cell, v - (cv + 0.5) * cell
    d = np.sqrt(du ** 2 + dv ** 2)
    # field sampled at cell centres so each dot is a clean disc
    ccx = (cu + 0.5) * cell * np.cos(-th) - (cv + 0.5) * cell * np.sin(-th)
    ccy = (cu + 0.5) * cell * np.sin(-th) + (cv + 0.5) * cell * np.cos(-th)
    ni = n[np.clip((ccy * S).astype(int), 0, H - 1), np.clip((ccx * S).astype(int), 0, W - 1)]
    wave = 0.5 + 0.5 * np.sin(ccx / 170.0 + ccy / 260.0 + ni * 5.0)
    amp = smooth((0.65 * wave + 0.55 * ni - 0.22) / 0.75)
    rad = cell * (0.10 + 0.36 * amp)
    disc = smooth((rad - d) / 1.1 + 0.5)
    if tokenise:
        t = smooth((ccx / OUT_W - 0.40) / 0.22)
        hole = smooth((rad - 2.1 - d) / 1.1 + 0.5) * t
        disc = disc - hole * 0.93
    col = ramp(0.15 + 0.8 * amp * (0.5 + 0.5 * ccx / OUT_W), pal)
    light = col * (disc * (0.07 + 0.62 * amp ** 1.5))[..., None]
    finish(name, bg, light, rng, bloom=0.75)


def blocks(name, pal, seed, cw=64.0, ch=44.0, gap=9.0, skew=0.0, hot=None, fill=0.5, glow=(0.66, 0.5)):
    """A board of cards. A few are lit."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=glow, strength=0.16)
    n = fbm(rng, 420, 2)
    u = XX + (YY - OUT_H / 2) * skew
    v = YY
    cu, cv = np.floor(u / cw), np.floor(v / ch + 0.5)
    lu, lv = u - (cu + 0.5) * cw, v - cv * ch
    hw, hh, rr = (cw - gap) / 2, (ch - gap) / 2, 5.0
    qx, qy = np.abs(lu) - (hw - rr), np.abs(lv) - (hh - rr)
    sd = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - rr
    ccx = (cu + 0.5) * cw - (cv * ch - OUT_H / 2) * skew
    ccy = cv * ch
    ni = n[np.clip((ccy * S).astype(int), 0, H - 1), np.clip((ccx * S).astype(int), 0, W - 1)]
    h = np.sin(cu * 127.1 + cv * 311.7 + seed) * 43758.5453
    rnd = h - np.floor(h)
    amp = smooth((ni * 0.75 + rnd * 0.45 - 0.35) / 0.6) * (0.3 + 0.7 * smooth(ccx / OUT_W * 1.25))
    outline = np.exp(-(sd / 0.8) ** 2)
    inside = smooth(-sd / 1.2 + 0.5)
    filled = (rnd > 1 - fill)
    # a line of "content" inside filled cards
    bar = inside * (np.abs(lv + hh * 0.35) < 1.6) * (lu < hw * (rnd * 1.2 - 0.5)) * (lu > -hw + 8)
    col = ramp(0.1 + 0.75 * amp, pal)
    inten = outline * (0.10 + 0.7 * amp) + inside * filled * amp ** 2 * 0.55 + bar * 0.5 * amp
    light = col * inten[..., None]
    if hot:
        hc = hexc(hot)
        is_hot = (rnd > 0.955) & (ni > 0.45)
        light = np.where(is_hot[..., None], hc * (outline * 1.3 + inside * 0.75)[..., None], light)
    finish(name, bg, light, rng, bloom=0.8)


def strata(name, pal, seed, lines=54):
    """Ridgelines, back to front."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=(0.62, 0.35), strength=0.2)
    light = np.zeros((H, W, 3), dtype=np.float32)
    n = fbm(rng, 300, 4, shape=(lines * 8, W), gain=0.55)
    x = np.arange(W, dtype=np.float32) / S
    env = np.exp(-((x / OUT_W - 0.64) / 0.26) ** 2) + 0.35 * np.exp(-((x / OUT_W - 0.22) / 0.14) ** 2)
    ys = []
    for i in range(lines):
        y0 = OUT_H * (0.30 + 0.78 * i / (lines - 1))
        ridge = np.maximum(n[i * 8] - 0.36, 0) ** 1.5
        ys.append(y0 - ridge * env * (150 + 130 * i / lines) + 0.0)
    ys = np.array(ys)
    front = np.full(W, 1e9, dtype=np.float32)
    for i in range(lines - 1, -1, -1):
        vis = ys[i] < front - 0.6
        lift = (OUT_H * (0.30 + 0.78 * i / (lines - 1)) - ys[i]) / 120.0
        col = ramp(np.clip(0.12 + lift * 0.9, 0, 1), pal)
        w = (0.22 + 0.9 * np.clip(lift, 0, 1)) * (0.35 + 0.65 * i / lines)
        for o in (-0.25, 0.25):
            splat(light, x[vis], ys[i][vis] + o, col[vis], w[vis] * 0.55)
        front = np.minimum(front, ys[i])
    light = blur(flush(light), 0.55) * 5.0
    finish(name, bg, light, rng, bloom=0.8)


def textlines(name, pal, seed):
    """Writing: a manuscript in perspective, with edits marked."""
    rng = np.random.default_rng(seed)
    bg = background(pal, glow=(0.66, 0.45), strength=0.16)
    light = np.zeros((H, W, 3), dtype=np.float32)
    th = -0.20
    row_h, x_left = 21.0, -200.0
    accent, ink = hexc(GLOW), hexc('#8A93A6')
    fade = fbm(rng, 500, 2)
    for col_i, x0 in enumerate(np.arange(x_left, OUT_W + 500, 470)):
        y = -420.0
        while y < OUT_H + 600:
            para = rng.integers(3, 8)
            if rng.random() < 0.3:  # heading
                segs = [(x0, rng.uniform(120, 230), 4.6, 1.0, False)]
                rows = [segs]
            else:
                rows = []
                for r in range(para):
                    xx, segs = x0, []
                    limit = x0 + (390 if r < para - 1 else rng.uniform(120, 330))
                    while xx < limit - 24:
                        wl = min(rng.uniform(16, 78), limit - xx)
                        segs.append((xx, wl, 2.5, 0.5, rng.random() < 0.045))
                        xx += wl + 8
                    rows.append(segs)
            for segs in rows:
                for (sx, wl, hh, a, edit) in segs:
                    t = np.arange(0, wl, 0.4, dtype=np.float32)
                    for o in np.arange(-hh, hh + 0.01, 0.5):
                        ux, uy = sx + t, np.full_like(t, y + o)
                        px = ux * np.cos(th) - uy * np.sin(th)
                        py = ux * np.sin(th) + uy * np.cos(th)
                        splat(light, px, py, accent if edit else ink, (0.11 if edit else 0.035) * a * 2)
                y += row_h
            y += row_h * 1.4
    light = blur(flush(light), 0.5) * 3.2
    mask = smooth((fade - 0.2) / 0.5) * (0.22 + 0.78 * smooth(XX / OUT_W * 1.15))
    light *= mask[..., None] * 1.5
    finish(name, bg, light, rng, bloom=0.7)


BANNERS = {
    'index': lambda: orb('index', 'brand', 11),
    'quick-start': lambda: flow('quick-start', 'brand', 4, spread=1.5, scale=520, steps=520),
    'agentic-content-designer': lambda: converge('agentic-content-designer', 'brand', 3),
    'ai-enablement': lambda: lattice('ai-enablement', 'brand', 8),
    'trafficcount': lambda: trails('trafficcount', 'brand', 5),
    'projects': lambda: blocks('projects', 'brand', 6, cw=118, ch=74, gap=14, skew=-0.35, fill=0.45),
    'architecture': lambda: contours('architecture', 'brand', 21, 'terrain'),
    'case-studies': lambda: dots('case-studies', 'brand', 31, cell=34.0, tokenise=False),
    'tools': lambda: blocks('tools', 'brand', 9, cw=40, ch=40, gap=8, fill=0.6),
    'delivery': lambda: strata('delivery', 'brand', 14),
    'history': lambda: contours('history', 'brand', 17, 'rings'),
    'mastercard': lambda: dots('mastercard', 'brand', 12),
    'starknet': lambda: lattice('starknet', 'brand', 23, glow=(0.6, 0.55)),
    'writing': lambda: textlines('writing', 'brand', 2),
    'known-issues': lambda: blocks('known-issues', 'brand', 13, cw=58, ch=58, gap=10, fill=0.25, hot=GLOW, glow=(0.6, 0.5)),
    'faq': lambda: flow('faq', 'brand', 19, spread=3.4, scale=300, n=8000),
    'contact': lambda: contours('contact', 'brand', 27, 'ripples'),
}

if __name__ == '__main__':
    for key in (sys.argv[1:] or BANNERS):
        BANNERS[key]()
