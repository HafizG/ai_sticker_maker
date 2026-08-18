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

def make_animated_webp(pil_img, out_path, banner_text, stroke_color="#BE123C"):
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

def make_tray(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((88, 88), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

# ══════════════════════════════════════════════════
# 1. FIX PACK 4: br-casal-fofo
# ══════════════════════════════════════════════════
print("Processing Pack 4: br-casal-fofo...")
pack_dir_4 = os.path.join(PACKS_BASE_DIR, 'br-casal-fofo')
os.makedirs(pack_dir_4, exist_ok=True)

couple_photos = [
    ("DIVIDINDO AÇAÍ 🥣❤️", os.path.join(ARTIFACT_DIR, "couple_acai_photo_1787067751856.jpg")),
    ("SNUGGLE NO COBERTOR ☕🥰", os.path.join(ARTIFACT_DIR, "hug_blanket_photo_1787063951947.jpg")),
    ("JANTAR ROMÂNTICO 🍷✨", os.path.join(ARTIFACT_DIR, "kiss_dinner_photo_1787062958947.jpg")),
    ("BRINCADEIRA A DOIS 😂❤️", os.path.join(ARTIFACT_DIR, "hug_back_photo_1787064173256.jpg")),
    ("PASSEIO NA CHUVA ☔💕", os.path.join(ARTIFACT_DIR, "kiss_rain_photo_1787062780818.jpg")),
    ("MOMENTO FOFO 🥰", os.path.join(ARTIFACT_DIR, "kiss_cheek_photo_1787062858855.jpg")),
    ("SEMPRE AO SEU LADO 🥺❤️", os.path.join(ARTIFACT_DIR, "hug_comfort_photo_1787064119276.jpg")),
    ("REENCONTRO DO CASAL ✈️💖", os.path.join(ARTIFACT_DIR, "kiss_airport_photo_1787063080280.jpg")),
]

for idx, (title, img_p) in enumerate(couple_photos, 1):
    cutout = extract_pure_transparent_sticker(img_p)
    out_webp = os.path.join(pack_dir_4, f"{idx}.webp")
    frame0 = make_animated_webp(cutout, out_webp, title, "#BE123C")
    if idx == 1:
        make_tray(frame0, os.path.join(pack_dir_4, "tray_icon.png"))
    print(f"Pack 4: Generated {idx}.webp")

print("Pack 4 (br-casal-fofo) finished successfully!\n")

# ══════════════════════════════════════════════════
# 2. FIX PACK 5: br-coracao-paixao
# ══════════════════════════════════════════════════
print("Processing Pack 5: br-coracao-paixao...")
pack_dir_5 = os.path.join(PACKS_BASE_DIR, 'br-coracao-paixao')
os.makedirs(pack_dir_5, exist_ok=True)

heart_definitions = [
    ("RUBI DA PAIXÃO 💎❤️", "ruby", "#9F1239"),
    ("DIAMANTE DE OURO ✨", "diamond", "#D97706"),
    ("FOGO DA PAIXÃO 🔥", "fire", "#DC2626"),
    ("NEON CYBERPUNK ⚡", "neon", "#0891B2"),
    ("ROSA NO CORAÇÃO 🌹", "rose", "#BE123C"),
    ("GALÁXIA DE AMOR 🌌", "galaxy", "#4338CA"),
    ("GOTA DE CRISTAL 💧", "water", "#0284C7"),
    ("FLECHA DO CUPIDO 💘", "cupid", "#E11D48"),
]

for idx, (title, h_type, stroke_c) in enumerate(heart_definitions, 1):
    def draw_heart(d, c, ht=h_type):
        if ht == "ruby":
            pts = [(512, 860), (220, 480), (220, 320), (360, 200), (512, 340), (664, 200), (804, 320), (804, 480)]
            d.polygon(pts, fill="#E11D48")
            d.polygon([(512, 860), (512, 340), (360, 200)], fill="#BE123C")
            d.polygon([(512, 860), (512, 340), (664, 200)], fill="#F43F5E")
            d.polygon([(220, 320), (360, 200), (512, 340)], fill="#FB7185")
            d.polygon([(804, 320), (664, 200), (512, 340)], fill="#FDA4AF")
        elif ht == "diamond":
            pts = [(512, 860), (220, 480), (220, 320), (360, 200), (512, 340), (664, 200), (804, 320), (804, 480)]
            d.polygon(pts, fill="#F59E0B")
            d.polygon([(512, 860), (512, 340), (360, 200)], fill="#D97706")
            d.polygon([(512, 860), (512, 340), (664, 200)], fill="#FDE047")
            d.polygon([(220, 320), (360, 200), (512, 340)], fill="#FEF08A")
            for sx, sy in [(280, 280), (740, 300), (512, 820)]:
                d.polygon([(sx, sy-35), (sx+10, sy-10), (sx+35, sy), (sx+10, sy+10), (sx, sy+35), (sx-10, sy+10), (sx-35, sy), (sx-10, sy-10)], fill="white")
        elif ht == "fire":
            d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#DC2626")
            d.pieslice([240, 200, 520, 480], 180, 0, fill="#DC2626")
            d.pieslice([504, 200, 784, 480], 180, 0, fill="#DC2626")
            d.polygon([(512, 780), (340, 480), (380, 320), (512, 420), (644, 320), (684, 480)], fill="#F59E0B")
            d.polygon([(512, 700), (400, 480), (440, 380), (512, 460), (584, 380), (624, 480)], fill="#FEF08A")
        elif ht == "neon":
            d.polygon([(512, 860), (200, 460), (280, 240), (512, 380), (744, 240), (824, 460)], fill="#0F172A", outline="#EC4899", width=22)
            d.pieslice([220, 180, 520, 480], 180, 0, fill="#0F172A", outline="#EC4899", width=22)
            d.pieslice([504, 180, 804, 480], 180, 0, fill="#0F172A", outline="#EC4899", width=22)
            d.polygon([(512, 760), (280, 460), (340, 300), (512, 420), (684, 300), (744, 460)], outline="#06B6D4", width=12)
        elif ht == "rose":
            d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#FCE7F3", outline="#F43F5E", width=12)
            d.pieslice([240, 200, 520, 480], 180, 0, fill="#FCE7F3", outline="#F43F5E", width=12)
            d.pieslice([504, 200, 784, 480], 180, 0, fill="#FCE7F3", outline="#F43F5E", width=12)
            d.ellipse([420, 420, 604, 604], fill="#BE123C")
            d.ellipse([460, 450, 564, 554], fill="#E11D48")
            d.ellipse([484, 474, 540, 530], fill="#FDA4AF")
            d.polygon([(380, 560), (320, 600), (380, 640)], fill="#15803D")
            d.polygon([(644, 560), (704, 600), (644, 640)], fill="#15803D")
        elif ht == "galaxy":
            d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#1E1B4B")
            d.pieslice([240, 200, 520, 480], 180, 0, fill="#1E1B4B")
            d.pieslice([504, 200, 784, 480], 180, 0, fill="#1E1B4B")
            d.ellipse([360, 420, 664, 620], fill="#6366F1")
            d.ellipse([420, 460, 604, 580], fill="#A855F7")
            d.ellipse([470, 490, 554, 550], fill="#F472B6")
            for sx, sy in [(340, 360), (680, 340), (440, 680), (580, 660), (512, 520)]:
                d.ellipse([sx-10, sy-10, sx+10, sy+10], fill="white")
        elif ht == "water":
            d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#0284C7")
            d.pieslice([240, 200, 520, 480], 180, 0, fill="#0284C7")
            d.pieslice([504, 200, 784, 480], 180, 0, fill="#0284C7")
            d.ellipse([340, 400, 684, 640], outline="#E0F2FE", width=12)
            d.ellipse([400, 450, 624, 590], outline="#E0F2FE", width=8)
        else: # cupid
            d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#BE123C")
            d.pieslice([240, 200, 520, 480], 180, 0, fill="#BE123C")
            d.pieslice([504, 200, 784, 480], 180, 0, fill="#BE123C")
            d.line([(140, 680), (884, 320)], fill="#F59E0B", width=18)
            d.polygon([(860, 290), (920, 300), (890, 360)], fill="#D97706")
            d.polygon([(140, 650), (100, 700), (160, 710)], fill="#D97706")
            
    cutout = render_diecut_sticker(draw_heart)
    out_webp = os.path.join(pack_dir_5, f"{idx}.webp")
    frame0 = make_animated_webp(cutout, out_webp, title, stroke_c)
    if idx == 1:
        make_tray(frame0, os.path.join(pack_dir_5, "tray_icon.png"))
    print(f"Pack 5: Generated {idx}.webp")

print("Pack 5 (br-coracao-paixao) finished successfully!")
