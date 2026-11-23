"""Фото товаров для карточек: квадрат 480x480 без полей.
Предметные снимки на белом: обрезать белые поля, товар в белый квадрат с ровным отступом 6%.
Обычные фото: обрезка по центру в квадрат. Оригиналы копируются в src/satu-img-orig/ один раз."""
import glob
import shutil
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path("/Users/farik/claude/Projects/himmaks")
SRC_DIR, ORIG = ROOT / "site/img/p", ROOT / "src/satu-img-orig"
ORIG.mkdir(exist_ok=True)
SIZE, MARGIN = 480, 0.06

for f in sorted(glob.glob(str(SRC_DIR / "*.webp"))):
    name = Path(f).name
    if not (ORIG / name).exists():
        shutil.copy2(f, ORIG / name)
    raw = Image.open(ORIG / name)
    if raw.mode in ("RGBA", "LA", "P"):
        raw = raw.convert("RGBA")
        bgw = Image.new("RGBA", raw.size, (255, 255, 255, 255))
        raw = Image.alpha_composite(bgw, raw)
    im = raw.convert("RGB")
    w, h = im.size
    white = Image.new("RGB", im.size, (255, 255, 255))
    mask = ImageChops.difference(im, white).convert("L").point(lambda v: 255 if v > 18 else 0)
    box = mask.getbbox() or (0, 0, w, h)
    edge = [im.getpixel((x, y)) for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    on_white = all(min(px) > 235 for px in edge)
    if on_white:
        obj = im.crop(box)
        ow, oh = obj.size
        side = int(max(ow, oh) / (1 - 2 * MARGIN))
        canvas = Image.new("RGB", (side, side), (255, 255, 255))
        canvas.paste(obj, ((side - ow) // 2, (side - oh) // 2))
        out = canvas.resize((SIZE, SIZE), Image.LANCZOS)
        kind = "packshot"
    else:
        s = min(w, h)
        out = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((SIZE, SIZE), Image.LANCZOS)
        kind = "photo"
    out.save(f, "WEBP", quality=82, method=6)
    print(name, kind, (w, h))
