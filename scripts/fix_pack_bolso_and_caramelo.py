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

def draw_text_centered(draw, text, xy, font, fill="white", stroke_fill="black", stroke_width=4):
    cx, cy = xy
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
    val = hsv[:, :, 2]
    
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

def render_diecut_sticker(draw_func):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    draw_func(d, canvas)
    
    alpha = canvas.split()[3]
    outline = alpha.filter(ImageFilter.MaxFilter(31))
    
    sticker = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    white_fill = Image.new('RGBA', (1024, 1024), (255, 255, 255, 255))
    sticker.paste(white_fill, (0, 0), outline)
    sticker.paste(canvas, (0, 0), canvas)
    
    bbox = sticker.getbbox()
    if bbox:
        sticker = sticker.crop(bbox)
    return sticker

def make_animated_webp(pil_img, out_path, banner_text, stroke_color="#15803D"):
    frames = []
    w, h = pil_img.size
    for f in range(6):
        phase = (f / 6.0) * 2 * math.pi
        canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        
        scale = 0.94 + 0.08 * math.sin(phase)
        sw, sh = int(w * scale), int(h * scale)
        resized = pil_img.resize((sw, sh), Image.Resampling.LANCZOS)
        resized.thumbnail((450, 420), Image.Resampling.LANCZOS)
        
        ox = (512 - resized.width) // 2
        oy = (420 - resized.height) // 2 + 10
        canvas.paste(resized, (ox, oy), resized)
        
        d = ImageDraw.Draw(canvas)
        font = get_font(26)
        draw_text_centered(d, banner_text, (256, 480), font, fill="#FEF08A", stroke_fill=stroke_color, stroke_width=5)
        frames.append(canvas)
        
    frames[0].save(
        out_path,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=130,
        loop=0,
        lossless=False,
        quality=90
    )
    return frames[0]

def make_static_webp(pil_img, out_path, banner_text, banner_color="#D97706"):
    canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    pil_img_c = pil_img.copy()
    pil_img_c.thumbnail((470, 440), Image.Resampling.LANCZOS)
    
    ox = (512 - pil_img_c.width) // 2
    oy = (440 - pil_img_c.height) // 2 + 10
    canvas.paste(pil_img_c, (ox, oy), pil_img_c)
    
    if banner_text:
        d = ImageDraw.Draw(canvas)
        font = get_font(26)
        draw_text_centered(d, banner_text, (256, 480), font, fill="white", stroke_fill=banner_color, stroke_width=5)
        
    canvas.save(out_path, format="WEBP", lossless=True)
    return canvas

def make_tray(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((88, 88), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

# ══════════════════════════════════════════════════
# 1. FIX PACK 8: br-bolsonaro-dancando
# ══════════════════════════════════════════════════
print("Processing Pack 8: br-bolsonaro-dancando...")
pack_dir_8 = os.path.join(PACKS_BASE_DIR, 'br-bolsonaro-dancando')
os.makedirs(pack_dir_8, exist_ok=True)

bolso_p1 = os.path.join(ARTIFACT_DIR, "bolsonaro_thumbs_up_sticker_1786904611609.jpg")
c1 = extract_pure_transparent_sticker(bolso_p1)
f1 = make_animated_webp(c1, os.path.join(pack_dir_8, "1.webp"), "VALEU MEU BRASIL! 👍", "#15803D")
make_tray(f1, os.path.join(pack_dir_8, "tray_icon.png"))
print("Pack 8: Generated 1.webp")

bolso_scenes = [
    ("TURN DOWN FOR WHAT 😎", "thug"),
    ("DE JET SKI NA PRAIA 🌊", "jetski"),
    ("TÁ COM MEDO, PETISTA? 📢", "megaphone"),
    ("TOCANDO SANFONA 🪗", "accordion"),
    ("DANÇA DO CAPITÃO 🕺", "dance"),
    ("FLEXÃO MILITAR 💪", "pushup"),
    ("PASTEL NA FEIRA 🥟", "pastel"),
]

for idx, (title, scene_id) in enumerate(bolso_scenes, 2):
    def draw_bolso(d, c, s=scene_id):
        d.ellipse([260, 480, 764, 940], fill="#1E3A8A") # Navy suit
        d.line([(320, 500), (704, 900)], fill="#009C3B", width=45) # Presidential sash
        d.line([(330, 510), (714, 910)], fill="#FFDF00", width=20)
        d.ellipse([360, 200, 664, 540], fill="#FED7AA") # Face
        d.arc([350, 170, 674, 380], 180, 360, fill="#64748B", width=40) # Hair
        if s == "thug":
            d.rectangle([390, 320, 490, 380], fill="black")
            d.rectangle([534, 320, 634, 380], fill="black")
            d.line([(490, 340), (534, 340)], fill="black", width=8)
        elif s == "jetski":
            d.polygon([(180, 680), (844, 680), (720, 840), (280, 840)], fill="#0284C7", outline="#0369A1", width=8)
        elif s == "megaphone":
            d.polygon([(540, 380), (780, 280), (780, 480)], fill="#DC2626", outline="black", width=6)
        elif s == "accordion":
            d.rectangle([300, 520, 724, 760], fill="#DC2626", outline="black", width=6)
            for bx in range(320, 700, 35):
                d.line([(bx, 520), (bx, 760)], fill="white", width=4)
        elif s == "pastel":
            d.polygon([(560, 420), (720, 360), (700, 520)], fill="#FDE047", outline="#CA8A04", width=6)
        d.arc([440, 400, 584, 460], 0, 180, fill="black", width=8)
    cutout = render_diecut_sticker(draw_bolso)
    make_animated_webp(cutout, os.path.join(pack_dir_8, f"{idx}.webp"), title, "#15803D")
    print(f"Pack 8: Generated {idx}.webp")

print("Pack 8 (br-bolsonaro-dancando) finished successfully!\n")

# ══════════════════════════════════════════════════
# 2. FIX PACK 9: br-vira-lata-caramelo
# ══════════════════════════════════════════════════
print("Processing Pack 9: br-vira-lata-caramelo...")
pack_dir_9 = os.path.join(PACKS_BASE_DIR, 'br-vira-lata-caramelo')
os.makedirs(pack_dir_9, exist_ok=True)

dog_p1 = os.path.join(ARTIFACT_DIR, "caramelo_dog_sticker_1786903786655.jpg")
cdog = extract_pure_transparent_sticker(dog_p1)
fdog = make_static_webp(cdog, os.path.join(pack_dir_9, "1.webp"), "CARAMELO COM COXINHA 🍗", "#D97706")
make_tray(fdog, os.path.join(pack_dir_9, "tray_icon.png"))
print("Pack 9: Generated 1.webp")

dog_scenes = [
    ("NO BANQUINHO DO BOTECO 🍻", "bar"),
    ("COM A AMARELINHA 🇧🇷", "jersey"),
    ("DE CAPACETE NA OBRA 👷", "hardhat"),
    ("DORMINDO NA CALÇADA 😴", "sleep"),
    ("LATINDO PRA MOTO 🛵", "moto"),
    ("CAFUNÉ GOSTOSO 🥰", "scratch"),
    ("DE OLHO NO CHURRASCO 🍖", "bbq"),
]

for idx, (title, scene_id) in enumerate(dog_scenes, 2):
    def draw_caramelo(d, c, s=scene_id):
        d.ellipse([280, 340, 744, 840], fill="#D97706") # Head
        d.ellipse([180, 300, 340, 600], fill="#B45309") # Left Ear
        d.ellipse([684, 300, 844, 600], fill="#B45309") # Right Ear
        d.ellipse([380, 500, 644, 760], fill="#FDE68A") # Snout
        d.ellipse([460, 520, 564, 600], fill="black") # Nose
        d.ellipse([475, 630, 545, 710], fill="#F87171") # Tongue
        d.ellipse([360, 420, 440, 500], fill="#451A03") # Left Eye
        d.ellipse([584, 420, 664, 500], fill="#451A03") # Right Eye
        if s == "jersey":
            d.ellipse([260, 740, 764, 1000], fill="#FFDF00", outline="#009C3B", width=12)
        elif s == "hardhat":
            d.ellipse([320, 180, 704, 380], fill="#F59E0B", outline="#B45309", width=10)
        elif s == "bar":
            d.rectangle([200, 780, 824, 860], fill="#78350F", outline="#451A03", width=8)
        elif s == "bbq":
            d.line([(512, 700), (740, 600)], fill="#94A3B8", width=12)
            d.ellipse([700, 540, 820, 640], fill="#881337") # Meat skewer
    cutout = render_diecut_sticker(draw_caramelo)
    out_webp = os.path.join(pack_dir_9, f"{idx}.webp")
    make_static_webp(cutout, out_webp, title, "#D97706")
    print(f"Pack 9: Generated {idx}.webp")

print("Pack 9 (br-vira-lata-caramelo) finished successfully!")
