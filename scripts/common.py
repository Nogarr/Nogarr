"""Valores compartidos por los scripts del README animado."""
import os

USERNAME = os.environ.get("GH_USERNAME", "Nogarr")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
DATA = os.path.join(ROOT, "data")
BUILD = os.path.join(ROOT, "build")

# Paleta tipo terminal de GitHub (modo oscuro); las tarjetas tienen fondo propio,
# así que se ven bien tanto en el tema claro como en el oscuro.
BG = "#0d1117"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#39d353"
ACCENT2 = "#58a6ff"
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# Alto común para que retrato y tarjeta queden alineados lado a lado
CARD_HEIGHT = 420
PORTRAIT_WIDTH = 370
INFO_WIDTH = 490
HEATMAP_WIDTH = PORTRAIT_WIDTH + INFO_WIDTH  # 860

for d in (ASSETS, DATA, BUILD):
    os.makedirs(d, exist_ok=True)
