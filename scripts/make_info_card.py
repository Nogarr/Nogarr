"""Paso 3: tarjeta estilo neofetch -> assets/info-card.svg (editá LINES y volvé a correrlo)."""
import os
from xml.sax.saxutils import escape
from common import ASSETS, BG, BORDER, FG, MUTED, ACCENT, ACCENT2, FONT, CARD_HEIGHT, INFO_WIDTH

HEADER = "valentin@nogarr"
LINES = [
    ("Rol", "Full Stack Developer"),
    ("Base", "Buenos Aires, Argentina · Remoto"),
    ("Foco", "Sistemas de gestión a medida"),
    ("", ""),
    ("Lenguajes", "TypeScript · JavaScript · Python · SQL"),
    ("Frontend", "React · Next.js · Tailwind · Three.js"),
    ("Backend", "Node.js · NestJS · Fastify · REST APIs"),
    ("Datos", "PostgreSQL · Supabase (RLS) · MySQL"),
    ("Integr.", "n8n · WhatsApp API · Edge Functions"),
    ("Tools", "Git · Vercel · Claude Code · Cursor"),
    ("", ""),
    ("Ahora", "Backend de una fintech (NestJS + PG)"),
    ("Hice", "ERPs · CRMs con WhatsApp · talleres"),
    ("Contacto", "linkedin.com/in/nogar"),
]
FONT_SIZE = 13
LINE_H = 23
X = 24
KEY_W = 92


def main():
    W, H = INFO_WIDTH, CARD_HEIGHT
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Datos de Valentín Nogar">',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>']
    for k, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        o.append(f'<circle cx="{18 + k * 16}" cy="17" r="5" fill="{c}"/>')
    o.append(f'<text x="{W / 2}" y="21" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">nogarr@github: ~ neofetch</text>')
    o.append(f'<g font-family="{FONT}" font-size="{FONT_SIZE}">')
    y = 58
    items = [(HEADER, None, "head"), ("-" * len(HEADER), None, "rule")] + [(k, v, "kv") for k, v in LINES]
    for i, (k, v, kind) in enumerate(items):
        begin = 0.4 + i * 0.12
        anim = (f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.4s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="-8 0" to="0 0" begin="{begin:.2f}s" dur="0.4s" fill="freeze"/>')
        if kind == "head":
            o.append(f'<g opacity="0"><text x="{X}" y="{y}" font-weight="700"><tspan fill="{ACCENT}">valentin</tspan><tspan fill="{FG}">@</tspan><tspan fill="{ACCENT2}">nogarr</tspan></text>{anim}</g>')
        elif kind == "rule":
            o.append(f'<g opacity="0"><text x="{X}" y="{y}" fill="{MUTED}">{escape(k)}</text>{anim}</g>')
        elif k:
            o.append(f'<g opacity="0"><text x="{X}" y="{y}"><tspan fill="{ACCENT}" font-weight="700">{escape(k)}</tspan></text>'
                     f'<text x="{X + KEY_W}" y="{y}" fill="{FG}">{escape(v)}</text>{anim}</g>')
        y += LINE_H if (k or kind != "kv") else LINE_H * 0.5
    # fila de colores al final, como en neofetch
    colors = ["#161b22", "#f85149", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]
    begin = 0.4 + len(items) * 0.12
    o.append(f'<g opacity="0">' + "".join(f'<rect x="{X + j * 26}" y="{y - 6}" width="22" height="12" rx="2" fill="{c}"/>' for j, c in enumerate(colors)) +
             f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.4s" fill="freeze"/></g>')
    o.append('</g></svg>')
    with open(os.path.join(ASSETS, "info-card.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print("OK -> assets/info-card.svg")


if __name__ == "__main__":
    main()
