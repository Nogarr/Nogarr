"""Paso 1 (se corre una vez, o cuando cambiás la foto).

Toma photo/source.jpg (o .png) si existe; si no, descarga tu avatar de GitHub.
Saca el fondo (rembg si está instalado; si no, un flood-fill desde los bordes),
sube el contraste con CLAHE y compone la cara sobre blanco -> build/prepped.png
"""
import glob, io, os, sys
import cv2
import numpy as np
import requests
from PIL import Image
from common import USERNAME, ROOT, BUILD


def load_source() -> Image.Image:
    local = sorted(glob.glob(os.path.join(ROOT, "photo", "source.*")))
    if local:
        print(f"Usando {local[0]}")
        return Image.open(local[0]).convert("RGB")
    url = f"https://github.com/{USERNAME}.png?size=460"
    print(f"Descargando avatar: {url}")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


def foreground_mask(img: Image.Image) -> np.ndarray:
    """Devuelve máscara 0..1 del sujeto."""
    try:
        from rembg import remove  # opcional: pip install rembg
        cut = remove(img)
        alpha = np.asarray(cut.split()[-1], dtype=np.float32) / 255.0
        print("Fondo removido con rembg")
        return alpha
    except Exception as e:  # noqa: BLE001
        print(f"rembg no disponible ({e.__class__.__name__}); uso flood-fill")
    gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    mask = np.zeros((h + 2, w + 2), np.uint8)
    flags = 4 | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8)
    # sembrar en el borde superior y laterales (donde suele estar la pared)
    seeds = [(x, 0) for x in range(0, w, 8)] + [(0, y) for y in range(0, h // 2, 8)] + [(w - 1, y) for y in range(0, h // 2, 8)]
    for (x, y) in seeds:
        if mask[y + 1, x + 1] == 0 and blur[y, x] > 150:
            cv2.floodFill(blur.copy(), mask, (x, y), 0, 18, 18, flags)
    bg = mask[1:-1, 1:-1] > 0
    bg = cv2.morphologyEx(bg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    alpha = (~bg).astype(np.float32)
    return cv2.GaussianBlur(alpha, (7, 7), 0)


def main():
    img = load_source()
    s = min(img.size)
    img = img.crop(((img.width - s) // 2, (img.height - s) // 2, (img.width + s) // 2, (img.height + s) // 2)).resize((460, 460))
    alpha = foreground_mask(img)
    gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray).astype(np.float32)
    out = gray * alpha + 255.0 * (1 - alpha)  # sujeto sobre blanco
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(os.path.join(BUILD, "prepped.png"))
    print("OK -> build/prepped.png")


if __name__ == "__main__":
    sys.exit(main())
