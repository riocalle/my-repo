#!/usr/bin/env python3
"""Independent legality check of a packing (row 167) — shares NO code with the engine (no numpy, no core.py).
Every input float is converted to Decimal exactly; cos/sin by their Taylor series at 60 digits; corners, wall
clearances and a separating-axis test on every pair at that precision. Rounding error ~1e-55, far below the margins.
    python3 verify_exact.py n102_s10.605828708.txt"""
import json, sys
from decimal import Decimal as D, getcontext
getcontext().prec = 60
PI = D("3.14159265358979323846264338327950288419716939937510582097494459")

def cs(t):                                     # cos, sin of an exact Decimal angle by range reduction + Taylor series
    k = (t / (PI / 2)).to_integral_value(); r = t - k * (PI / 2)
    c, s, term, i = D(0), D(0), D(1), 0
    while True:                                 # term = r^i / i!
        if i % 4 == 0: c += term
        elif i % 4 == 1: s += term
        elif i % 4 == 2: c -= term
        else: s -= term
        i += 1; term = term * r / i
        if abs(term) < D(10) ** -58: break
    for _ in range(int(k) % 4): c, s = -s, c    # rotate by +90° per quarter turn
    return c, s

if sys.argv[1].endswith(".txt"):                # the export format: '# s = …' header, then 'x y theta' rows
    rows = open(sys.argv[1]).read().splitlines()
    L = D(repr(float(next(r for r in rows if r.startswith("# s =")).split("=")[1])))
    sq = [[float(v) for v in r.split()] for r in rows if r.strip() and not r.startswith("#")]
else:
    d = json.load(open(sys.argv[1])); L = D(repr(float(d.get("L", d.get("s"))))); sq = d["squares"]
n = len(sq)
H = D("0.5"); C = []
for x, y, t in sq:
    x, y, t = D(repr(float(x))), D(repr(float(y))), D(repr(float(t))); c, s = cs(t)
    C.append([(x + c * a * H - s * b * H, y + s * a * H + c * b * H) for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))])
wall = min(min(min(p[0] for p in P), min(p[1] for p in P), L - max(p[0] for p in P), L - max(p[1] for p in P)) for P in C)
def gap(A, B):                                  # largest separation over the 4 edge normals (positive = disjoint)
    best = None
    for P in (A, B):
        for k in range(2):
            ex, ey = P[k + 1][0] - P[k][0], P[k + 1][1] - P[k][1]; nx, ny = -ey, ex    # |e| = 1 up to 1e-55
            pa = [p[0] * nx + p[1] * ny for p in A]; pb = [p[0] * nx + p[1] * ny for p in B]
            g = max(min(pa) - max(pb), min(pb) - max(pa)); best = g if best is None or g > best else best
    return best
worst = None; close = 0
for i in range(n):
    for j in range(i + 1, n):
        if (C[i][0][0] - C[j][0][0]) ** 2 + (C[i][0][1] - C[j][0][1]) ** 2 > 9: continue      # far apart (corner distance > 3)
        close += 1; g = gap(C[i], C[j]); worst = g if worst is None or g < worst else worst
ok = wall >= 0 and worst > 0
print(f"n = {n}, L = {L}: min wall clearance {wall:.3e}, min pair gap {worst:.3e} over {close} close pairs → {'LEGAL' if ok else 'NOT LEGAL'}")
