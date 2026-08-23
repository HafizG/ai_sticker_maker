import os
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PACKS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', 'packs')
MASTER_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', '_master.json')

def get_font(size, bold=True):
    font_paths = [
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\impact.ttf",
        "C:\\Windows\\Fonts\\seguiemj.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_bold_banner(draw, text, xy, font_size=28, fill="#FEF08A", stroke_fill="#002776", stroke_width=6):
    cx, cy = xy
    font = get_font(font_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = cx - tw / 2
    y = cy - th / 2
    draw.text((x, y), text, font=font, fill=fill, stroke_fill=stroke_fill, stroke_width=stroke_width)

def render_diecut_sticker(canvas):
    alpha = canvas.split()[3]
    outline = alpha.filter(ImageFilter.MaxFilter(25))
    
    w, h = canvas.size
    sticker = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    white_fill = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    sticker.paste(white_fill, (0, 0), outline)
    sticker.paste(canvas, (0, 0), canvas)
    
    bbox = sticker.getbbox()
    if bbox:
        sticker = sticker.crop(bbox)
    return sticker

def make_static_webp(pil_img, out_path, banner_text, text_stroke="#002776"):
    canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    pil_img_c = pil_img.copy()
    pil_img_c.thumbnail((470, 420), Image.Resampling.LANCZOS)
    
    ox = (512 - pil_img_c.width) // 2
    oy = (420 - pil_img_c.height) // 2 + 10
    canvas.paste(pil_img_c, (ox, oy), pil_img_c)
    
    if banner_text:
        d = ImageDraw.Draw(canvas)
        draw_bold_banner(d, banner_text, (256, 475), font_size=28, fill="#FEF08A", stroke_fill=text_stroke, stroke_width=6)
        
    canvas.save(out_path, format="WEBP", lossless=True)
    return canvas

def make_tray(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((88, 88), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

# ══════════════════════════════════════════════════
# BUILD 10 NEYMAR JR STICKERS
# ══════════════════════════════════════════════════
print("Building 10 Neymar Jr Stickers...")
pack_dir_ney = os.path.join(PACKS_BASE_DIR, 'br-neymar-jr')
os.makedirs(pack_dir_ney, exist_ok=True)

neymar_configs = [
    ("neymar_cutout_2.png", "NEYMAR JR GOL! ⚽⚡", "#002776"),
    ("neymar_cutout_6.png", "O PAI TÁ ON! 🕶️📱", "#15803D"),
    ("neymar_cutout_3.png", "RECEBA! É O NEY! 🇧🇷", "#002776"),
    ("neymar_cutout_9.png", "SHHH! FALA AGORA! 🤫", "#0F172A"),
    ("neymar_cutout_11.png", "TUDO PASSA! 🙏✨", "#7E22CE"),
    ("neymar_cutout_4.png", "BAILA NEYMAR! 🕺⚽", "#15803D"),
    ("neymar_cutout_8.png", "FOCO TOTAL NO JOGO 🎯", "#DC2626"),
    ("neymar_cutout_5.png", "VALEU, É NÓIS! 🤙🔥", "#D97706"),
    ("neymar_cutout_7.png", "DRIBLE DA VACA! 🐮💨", "#0284C7"),
    ("neymar_cutout_10.png", "CAMISA 10 DA SELEÇÃO 🔟💛", "#009C3B"),
]

for idx, (fname, title, stroke_col) in enumerate(neymar_configs, 1):
    fpath = fname if os.path.exists(fname) else f"neymar_cutout_1.png"
    im = Image.open(fpath).convert('RGBA')
    diecut = render_diecut_sticker(im)
    out_webp = os.path.join(pack_dir_ney, f"{idx}.webp")
    f_res = make_static_webp(diecut, out_webp, title, stroke_col)
    if idx == 1:
        make_tray(f_res, os.path.join(pack_dir_ney, "tray_icon.png"))
    print(f"Pack Neymar: Generated {idx}.webp")

# ══════════════════════════════════════════════════
# REGISTER IN _master.json
# ══════════════════════════════════════════════════
with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
    master_data = json.load(f)

master_data["packs"]["br-neymar-jr"] = {
    "name": "Neymar Jr Craque & Memes ⚽",
    "cat": ["sports", "trending"],
    "hidden": [],
    "animated_sticker_pack": False
}

if "br-neymar-jr" not in master_data["countries"]["BR"]["packs"]:
    master_data["countries"]["BR"]["packs"].append("br-neymar-jr")

with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=2, ensure_ascii=False)

print("Registered br-neymar-jr in _master.json successfully!")
