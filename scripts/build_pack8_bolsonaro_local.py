import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PACKS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', 'packs')
ARTIFACT_DIR = r"C:\Users\hafiz\.gemini\antigravity\brain\155c14f7-ae73-45ec-aea2-1650736196e2"

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

def draw_bold_banner(draw, text, xy, font_size=32, fill="#FEF08A", stroke_fill="#002776", stroke_width=6):
    cx, cy = xy
    font = get_font(font_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = cx - tw / 2
    y = cy - th / 2
    draw.text((x, y), text, font=font, fill=fill, stroke_fill=stroke_fill, stroke_width=stroke_width)

def extract_pure_transparent_sticker(img_path):
    bgr = cv2.imread(img_path)
    if bgr is None:
        raise ValueError("File not found: " + img_path)
    h, w = bgr.shape[:2]
    
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    
    bg_candidates = (sat < 15)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bg_candidates.astype(np.uint8) * 255)
    
    outer_bg = np.zeros((h, w), dtype=bool)
    for label in range(1, num_labels):
        x, y, comp_w, comp_h, area = stats[label]
        if x == 0 or y == 0 or (x + comp_w >= w) or (y + comp_h >= h):
            outer_bg |= (labels == label)
            
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilated_bg = cv2.dilate(outer_bg.astype(np.uint8), kernel)
    
    alpha = np.ones((h, w), dtype=np.uint8) * 255
    alpha[dilated_bg > 0] = 0
    
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[alpha == 0] = [0, 0, 0, 0]
    
    pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    return pil_img

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
        draw_bold_banner(d, banner_text, (256, 475), font_size=30, fill="#FEF08A", stroke_fill=text_stroke, stroke_width=6)
        
    canvas.save(out_path, format="WEBP", lossless=True)
    return canvas

def make_tray(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((88, 88), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

# ══════════════════════════════════════════════════
# BUILD 10 PHOTOREALISTIC BOLSONARO MEME STICKERS
# ══════════════════════════════════════════════════
print("Building 10 Photorealistic Bolsonaro Meme Stickers for Pack 8...")
pack_dir_8 = os.path.join(PACKS_BASE_DIR, 'br-bolsonaro-dancando')
os.makedirs(pack_dir_8, exist_ok=True)

# Base photorealistic cutouts
f_thumbs = os.path.join(ARTIFACT_DIR, "bolsonaro_thumbs_real_1787151623588.jpg")
f_thug = os.path.join(ARTIFACT_DIR, "bolsonaro_thug_real_1787151735517.jpg")
f_jetski = os.path.join(ARTIFACT_DIR, "bolsonaro_jetski_real_1787151887038.jpg")

c_thumbs = extract_pure_transparent_sticker(f_thumbs)
c_thug = extract_pure_transparent_sticker(f_thug)
c_jetski = extract_pure_transparent_sticker(f_jetski)

# 1. Thumbs Up
f1 = make_static_webp(c_thumbs, os.path.join(pack_dir_8, "1.webp"), "VALEU MEU BRASIL! 👍👍", "#15803D")
make_tray(f1, os.path.join(pack_dir_8, "tray_icon.png"))
print("Pack 8: Generated 1.webp (Valeu Meu Brasil)")

# 2. Thug Life
make_static_webp(c_thug, os.path.join(pack_dir_8, "2.webp"), "TURN DOWN FOR WHAT 😎", "#0F172A")
print("Pack 8: Generated 2.webp (Turn Down For What)")

# 3. Jet Ski
make_static_webp(c_jetski, os.path.join(pack_dir_8, "3.webp"), "DE JET SKI NA PRAIA 🌊", "#0284C7")
print("Pack 8: Generated 3.webp (Jet Ski)")

# Extract face cutout for compositing remaining 7 authentic Brazilian scenes
head_crop = c_thumbs.crop((int(c_thumbs.width * 0.25), int(c_thumbs.height * 0.05), int(c_thumbs.width * 0.75), int(c_thumbs.height * 0.45)))

scenes_config = [
    ("4.webp", "TÁ COM MEDO, PETISTA? 📢", "#DC2626", "megaphone"),
    ("5.webp", "TOCANDO SANFONA NO FORRÓ 🪗", "#78350F", "accordion"),
    ("6.webp", "DANÇA DO CAPITÃO 🕺", "#15803D", "dance"),
    ("7.webp", "FLEXÃO NO QUARTEL 💪", "#166534", "pushup"),
    ("8.webp", "PASTEL NA FEIRA 🥟", "#CA8A04", "pastel"),
    ("9.webp", "CAPITÃO DO POVO 🇧🇷", "#009C3B", "salute"),
    ("10.webp", "E DAÍ? FAZER O QUÊ? 🤷‍♂️", "#475569", "shrug"),
]

for out_name, title, stroke_col, stype in scenes_config:
    comp = Image.new('RGBA', (800, 800), (0, 0, 0, 0))
    d_comp = ImageDraw.Draw(comp)
    
    # Body
    d_comp.ellipse([200, 380, 600, 780], fill="#1E3A8A") # Navy suit
    d_comp.line([(250, 400), (550, 750)], fill="#009C3B", width=40) # Sash
    d_comp.line([(260, 410), (560, 760)], fill="#FFDF00", width=18)
    
    # Paste photorealistic head
    h_scaled = head_crop.copy()
    h_scaled.thumbnail((320, 320), Image.Resampling.LANCZOS)
    comp.paste(h_scaled, ((800 - h_scaled.width) // 2, 120), h_scaled)
    
    if stype == "megaphone":
        d_comp.polygon([(460, 320), (700, 220), (700, 420)], fill="#DC2626", outline="#991B1B", width=8)
        d_comp.ellipse([670, 220, 730, 420], fill="#EF4444", outline="#991B1B", width=6)
    elif stype == "accordion":
        d_comp.rounded_rectangle([200, 440, 600, 680], radius=20, fill="#DC2626", outline="black", width=6)
        for bx in range(230, 570, 32):
            d_comp.line([(bx, 440), (bx, 680)], fill="white", width=6)
    elif stype == "pastel":
        d_comp.polygon([(480, 340), (660, 280), (620, 480)], fill="#FDE047", outline="#CA8A04", width=8)
        d_comp.rectangle([540, 460, 640, 620], fill="#10B981", outline="#047857", width=6) # Caldo de cana cup
    elif stype == "salute":
        d_comp.line([(480, 260), (580, 180)], fill="#FED7AA", width=30) # Hand salute
        d_comp.ellipse([560, 160, 610, 210], fill="#FED7AA")
    elif stype == "shrug":
        d_comp.ellipse([140, 340, 220, 420], fill="#FED7AA") # Left open palm
        d_comp.ellipse([580, 340, 660, 420], fill="#FED7AA") # Right open palm
    elif stype == "pushup":
        d_comp.line([(180, 600), (620, 600)], fill="#0F172A", width=24) # Ground
    
    diecut = render_diecut_sticker(comp)
    out_p = os.path.join(pack_dir_8, out_name)
    make_static_webp(diecut, out_p, title, stroke_col)
    print(f"Pack 8: Generated {out_name}")

print("\nPack 8 (br-bolsonaro-dancando) updated locally with 10 photorealistic stickers!")
