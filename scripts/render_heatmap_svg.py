"""Paso 5: data/contributions.json -> assets/contrib-heatmap.svg
Grilla 53x7 con datos reales; los cuadrados entran en diagonal y una
serpiente roja se pasea solo por los días sin commits."""
import datetime as dt, json, os, random
from collections import deque
from common import ASSETS, DATA, BG, BORDER, FG, MUTED, FONT, HEATMAP_WIDTH

SNAKE_LEN = 7          # cuadraditos de la serpiente
SNAKE_STEP = 0.32      # segundos por casillero (más alto = más lenta)
SNAKE_STEPS = 420      # largo del recorrido antes de repetir
SNAKE_COLORS = ["#ff4d4d", "#f85149", "#e5484d", "#da3633", "#c62828", "#b31d1d", "#8e1519"]

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def main():
    data = json.load(open(os.path.join(DATA, "contributions.json")))
    days = data["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # domingo
    W = HEATMAP_WIDTH
    left, top, gap = 40, 56, 3
    cell = (W - left - 20 - gap * 52) / 53
    H = int(top + 7 * (cell + gap) + 30)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{data["total"]} contribuciones en el último año">',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
         f'<g font-family="{FONT}">',
         f'<text x="20" y="28" font-size="13" fill="{FG}"><tspan fill="#39d353">$</tspan> git log --since="1 year" | wc -l <tspan fill="{MUTED}">→</tspan> <tspan font-weight="700">{data["total"]}</tspan> contribuciones</text>']
    last_month = None
    empty = {}  # (col,row) -> (x,y) de días sin contribuciones
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        col = (date - start).days // 7
        row = (date.weekday() + 1) % 7
        x = left + col * (cell + gap)
        y = top + row * (cell + gap)
        if row == 0 and date.month != last_month and date.day <= 7:
            o.append(f'<text x="{x:.1f}" y="{top - 8}" font-size="10" fill="{MUTED}">{MESES[date.month - 1]}</text>')
            last_month = date.month
        lvl = d["level"]
        if lvl == 0 and date <= dt.date.today():
            empty[(col, row)] = (x, y)
        if lvl == 4 and (d.get("count") or 0) >= 20:
            lvl = 5
        begin = 0.2 + (col + row) * 0.022
        tip = f'{d.get("count") if d.get("count") is not None else "?"} contribuciones · {d["date"]}'
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.5" fill="{PALETTE[lvl]}" opacity="0"><title>{tip}</title>'
                 f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.3f}s" dur="0.3s" fill="freeze"/>'
                 f'<animate attributeName="y" from="{y - 6:.1f}" to="{y:.1f}" begin="{begin:.3f}s" dur="0.3s" fill="freeze"/></rect>')
    o += snake_svg(empty, cell)
    for r, name in ((1, "lun"), (3, "mié"), (5, "vie")):
        o.append(f'<text x="12" y="{top + r * (cell + gap) + cell - 2:.1f}" font-size="10" fill="{MUTED}">{name}</text>')
    ly = H - 16
    o.append(f'<text x="{W - 20 - 6 * 16 - 60}" y="{ly + 9}" font-size="10" fill="{MUTED}">menos</text>')
    for i, c in enumerate(PALETTE):
        o.append(f'<rect x="{W - 20 - 6 * 16 - 20 + i * 16}" y="{ly}" width="11" height="11" rx="2" fill="{c}"/>')
    o.append(f'<text x="{W - 32}" y="{ly + 9}" font-size="10" fill="{MUTED}">más</text>')
    o.append('</g></svg>')
    with open(os.path.join(ASSETS, "contrib-heatmap.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print("OK -> assets/contrib-heatmap.svg")


def _neighbors(c, empty):
    col, row = c
    for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (col + dc, row + dr)
        if n in empty:
            yield n


def _largest_component(empty):
    seen, best = set(), []
    for c in empty:
        if c in seen:
            continue
        comp, q = [], deque([c])
        seen.add(c)
        while q:
            cur = q.popleft()
            comp.append(cur)
            for n in _neighbors(cur, empty):
                if n not in seen:
                    seen.add(n)
                    q.append(n)
        if len(comp) > len(best):
            best = comp
    return set(best)


def _shortest(a, b, cells):
    prev, q = {a: None}, deque([a])
    while q:
        cur = q.popleft()
        if cur == b:
            break
        for n in _neighbors(cur, cells):
            if n not in prev:
                prev[n] = cur
                q.append(n)
    path, cur = [], b
    while cur is not None and cur in prev:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]


def _walk(cells, steps):
    """Paseo que prefiere casilleros poco visitados y no se muerde la cola."""
    rng = random.Random(dt.date.today().toordinal())  # cambia cada día, estable en el día
    start = min(cells)
    path, visits = [start], {start: 1}
    for _ in range(steps):
        cur = path[-1]
        body = set(path[-SNAKE_LEN:])
        opts = [n for n in _neighbors(cur, cells) if n not in body] or list(_neighbors(cur, cells))
        if not opts:
            break
        rng.shuffle(opts)
        nxt = min(opts, key=lambda n: visits.get(n, 0))
        visits[nxt] = visits.get(nxt, 0) + 1
        path.append(nxt)
    back = _shortest(path[-1], start, cells)  # vuelve al inicio para que el loop no salte
    return path + back[1:]


def snake_svg(empty, cell):
    cells = _largest_component(empty)
    if len(cells) < SNAKE_LEN + 2:
        return []
    route = _walk(cells, SNAKE_STEPS)
    pts = [empty[c] for c in route]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    dur = len(pts) * SNAKE_STEP
    appear = 3.2  # arranca cuando terminó de entrar la grilla
    out = ['<g>']
    for i in range(SNAKE_LEN):
        color = SNAKE_COLORS[min(i, len(SNAKE_COLORS) - 1)]
        size = cell if i == 0 else cell - 1
        off = (cell - size) / 2
        out.append(
            f'<rect x="{off:.1f}" y="{off:.1f}" width="{size:.1f}" height="{size:.1f}" rx="2.5" fill="{color}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{appear + i * SNAKE_STEP:.2f}s"/>'
            f'<animateMotion path="{d}" dur="{dur:.1f}s" begin="{appear + i * SNAKE_STEP:.2f}s" repeatCount="indefinite" calcMode="linear"/>'
            '</rect>')
    out.append('</g>')
    return out


if __name__ == "__main__":
    main()
