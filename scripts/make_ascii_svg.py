"""Genera assets/ascii-portrait.svg: un "Hi!" gigante hecho con cuadraditos
(mismo estilo que el mapa de contribuciones) que aparece fila por fila, despacio.
SVG puro con SMIL: no depende de las fuentes del visitante."""
import os
from xml.sax.saxutils import escape
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from common import ASSETS, BG, BORDER, FG, MUTED, ACCENT, FONT, CARD_HEIGHT, PORTRAIT_WIDTH

TEXT = "Hi!"
SUBTITLE = "soy Valentín, Full Stack Developer"
COLS = 38                 # ancho del "Hi!" en cuadraditos
GAP = 1.6                 # separación entre cuadraditos
ROW_DELAY = 0.22          # segundos entre fila y fila (más alto = más lento)
ROW_DUR = 0.7
PALETTE = ["#0e4429", "#006d32", "#26a641", "#39d353"]  # de borde a centro
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def text_mask():
    font_path = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
    S = 24  # px por cuadradito en el lienzo auxiliar
    W = COLS * S
    font = ImageFont.truetype(font_path, 400) if font_path else ImageFont.load_default()
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    box = tmp.textbbox((0, 0), TEXT, font=font)
    scale = (W * 0.96) / (box[2] - box[0])
    font = ImageFont.truetype(font_path, int(400 * scale)) if font_path else font
    box = tmp.textbbox((0, 0), TEXT, font=font)
    H = int((box[3] - box[1]) * 1.08)
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).text(((W - (box[2] - box[0])) / 2 - box[0], (H - (box[3] - box[1])) / 2 - box[1]), TEXT, fill=255, font=font)
    rows = max(1, round(H / S))
    small = np.asarray(img.resize((COLS, rows), Image.BOX), dtype=np.float32) / 255.0
    # "profundidad": qué tan adentro de la letra está cada cuadradito (para dar volumen con los verdes)
    depth = np.asarray(img.filter(ImageFilter.MinFilter(int(S * 1.5) | 1)).resize((COLS, rows), Image.BOX), dtype=np.float32) / 255.0
    return small, depth


def main():
    on, depth = text_mask()
    rows = on.shape[0]
    W, H = PORTRAIT_WIDTH, CARD_HEIGHT
    cell = (W - 40 - GAP * (COLS - 1)) / COLS
    block_h = rows * (cell + GAP)
    top = 62 + ((H - 62 - 80) - block_h) / 2
    left = 20

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{TEXT} {escape(SUBTITLE)}">',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>']
    for k, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        o.append(f'<circle cx="{18 + k * 16}" cy="17" r="5" fill="{c}"/>')
    o.append(f'<text x="{W / 2}" y="21" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">~/nogarr/hello.txt</text>')
    o.append(f'<text x="20" y="46" font-family="{FONT}" font-size="12" fill="{FG}"><tspan fill="{ACCENT}">$</tspan> cat hello.txt</text>')
    for r in range(rows):
        b = 0.6 + r * ROW_DELAY
        cells = []
        for c in range(COLS):
            if on[r, c] < 0.45:
                continue
            lvl = 1 + int(depth[r, c] > 0.5) + int(on[r, c] > 0.9)
            x = left + c * (cell + GAP)
            y = top + r * (cell + GAP)
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="1.3" fill="{PALETTE[min(lvl, 3)]}"/>')
        if cells:
            o.append(f'<g opacity="0">{"".join(cells)}'
                     f'<animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
                     f'<animateTransform attributeName="transform" type="translate" from="0 -6" to="0 0" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/></g>')
    end = 0.6 + rows * ROW_DELAY + ROW_DUR
    sy = top + block_h + 34
    o.append(f'<text x="{W / 2}" y="{sy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{FG}" opacity="0">{escape(SUBTITLE)}'
             f'<animate attributeName="opacity" from="0" to="1" begin="{end:.2f}s" dur="1s" fill="freeze"/></text>')
    end += 1.1
    o.append(f'<text x="20" y="{H - 18}" font-family="{FONT}" font-size="12" fill="{ACCENT}" opacity="0">$'
             f'<animate attributeName="opacity" from="0" to="1" begin="{end:.2f}s" dur="0.3s" fill="freeze"/></text>')
    o.append(f'<rect x="32" y="{H - 29}" width="7" height="13" fill="{ACCENT}" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="1.1s" begin="{end:.2f}s" repeatCount="indefinite"/></rect>')
    o.append('</svg>')
    with open(os.path.join(ASSETS, "ascii-portrait.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print(f"OK -> assets/ascii-portrait.svg ({COLS}x{rows}, se completa en {end:.1f}s)")


if __name__ == "__main__":
    main()
