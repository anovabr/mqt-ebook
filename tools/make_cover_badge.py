from PIL import Image, ImageDraw, ImageFont
import math, sys

SRC = sys.argv[2] if len(sys.argv) > 2 else "assets/img/capa_jolie_original.png"
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/img/capa_jolie.png"
ACCENT = (154, 59, 46)     # brand red #9a3b2e
TEXT = "VERSÃO DO AUTOR"

# Pick a bold TTF that exists on this machine (Linux / macOS / Windows).
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
]


def load_font(size):
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


im = Image.open(SRC).convert("RGBA")
W, H = im.size

# --- top-right corner ribbon --------------------------------------------------
reach = 215          # how far the ribbon reaches along each edge from the corner
thick = 54           # band thickness
length = int(reach * math.sqrt(2)) + 40

band = Image.new("RGBA", (length, thick), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
# main red band
bd.rectangle([0, 0, length, thick], fill=ACCENT + (255,))
# thin light rules near the edges for a printed-ribbon look
bd.line([(0, 4), (length, 4)], fill=(255, 255, 255, 150), width=2)
bd.line([(0, thick - 5), (length, thick - 5)], fill=(255, 255, 255, 150), width=2)

# centered bold text
fnt = load_font(26)
tb = bd.textbbox((0, 0), TEXT, font=fnt)
tw, th = tb[2] - tb[0], tb[3] - tb[1]
bd.text(((length - tw) / 2 - tb[0], (thick - th) / 2 - tb[1]), TEXT,
        font=fnt, fill=(255, 255, 255, 255))

# rotate to sit across the top-right corner (left-up -> right-down)
rot = band.rotate(45, expand=True, resample=Image.BICUBIC)
rw, rh = rot.size

# midpoint of the diagonal from (W-reach,0) to (W,reach)
cx, cy = W - reach / 2, reach / 2
paste_xy = (int(cx - rw / 2), int(cy - rh / 2))

# soft shadow underneath the ribbon
shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
shadow.paste(rot, (paste_xy[0] + 3, paste_xy[1] + 3), rot)
from PIL import ImageFilter
shadow = shadow.filter(ImageFilter.GaussianBlur(4))
im = Image.alpha_composite(im, shadow)

layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
layer.paste(rot, paste_xy, rot)
im = Image.alpha_composite(im, layer)

im.convert("RGB").save(OUT, "PNG")
print("saved", OUT, im.size)
