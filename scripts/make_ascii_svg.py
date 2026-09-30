"""Paso 2: build/prepped.png -> assets/ascii-portrait.svg

Retrato ASCII monocromo que se "escribe" fila por fila (SMIL, sin JS).
"""
import os
from xml.sax.saxutils import escape
import numpy as np
from PIL import Image
from common import ASSETS, BUILD, BG, BORDER, FG, MUTED, ACCENT, FONT, CARD_HEIGHT, PORTRAIT_WIDTH

RAMP = " .`:-=+*cs#%@"  # de claro (vacío) a oscuro (denso)
COLS = 58
FONT_SIZE = 9.6
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE * 1.0
PAD_X = (PORTRAIT_WIDTH - COLS * CHAR_W) / 2
TOP = 38


def main():
    img = Image.open(os.path.join(BUILD, "prepped.png")).convert("L")
    rows = int((CARD_HEIGHT - TOP - 16) / LINE_H)
    arr = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    darkness = 1.0 - arr
    idx = np.clip((darkness * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    lines = ["".join(RAMP[i] for i in row) for row in idx]

    W, H = PORTRAIT_WIDTH, CARD_HEIGHT
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Retrato ASCII de Valentín Nogar">',
           '<defs>']
    for i in range(len(lines)):
        y = TOP + i * LINE_H - FONT_SIZE
        out.append(f'<clipPath id="r{i}"><rect x="{PAD_X - 2:.1f}" y="{y:.1f}" width="0" height="{LINE_H + 1:.1f}">'
                   f'<animate attributeName="width" from="0" to="{COLS * CHAR_W + 4:.1f}" begin="{0.3 + i * 0.045:.3f}s" dur="0.35s" fill="freeze"/></rect></clipPath>')
    out.append('</defs>')
    out.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>')
    # barra de ventana
    for k, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(f'<circle cx="{18 + k * 16}" cy="17" r="5" fill="{c}"/>')
    out.append(f'<text x="{W / 2}" y="21" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">~/nogarr/portrait.txt</text>')
    out.append(f'<g font-family="{FONT}" font-size="{FONT_SIZE}" fill="{FG}" xml:space="preserve">')
    for i, line in enumerate(lines):
        y = TOP + i * LINE_H
        out.append(f'<text x="{PAD_X:.1f}" y="{y:.1f}" clip-path="url(#r{i})" textLength="{COLS * CHAR_W:.1f}" lengthAdjust="spacing">{escape(line)}</text>')
    out.append('</g>')
    # cursor que parpadea al final
    out.append(f'<rect x="{PAD_X:.1f}" y="{H - 22}" width="7" height="12" fill="{ACCENT}"><animate attributeName="opacity" values="0;1;0" dur="1s" begin="{0.3 + len(lines) * 0.045:.2f}s" repeatCount="indefinite"/></rect>')
    out.append('</svg>')
    with open(os.path.join(ASSETS, "ascii-portrait.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"OK -> assets/ascii-portrait.svg ({COLS}x{len(lines)})")


if __name__ == "__main__":
    main()
