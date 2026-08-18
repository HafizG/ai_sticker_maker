import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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

def make_real_animated_webp(pil_img, out_path, banner_text, stroke_color="#7E22CE", anim_type="bounce"):
    frames = []
    w, h = pil_img.size
    for f in range(6):
        phase = (f / 6.0) * 2 * math.pi
        canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        
        if anim_type == "bounce":
            scale = 0.94 + 0.06 * math.sin(phase)
            dy = int(math.sin(phase) * 8)
        elif anim_type == "sway":
            scale = 0.97 + 0.03 * math.sin(phase)
            dy = int(math.cos(phase) * 6)
        elif anim_type == "pulse":
            scale = 0.93 + 0.07 * math.sin(phase)
            dy = 0
        else:
            scale = 0.95 + 0.05 * math.sin(phase)
            dy = int(math.sin(phase) * 5)
            
        sw, sh = int(w * scale), int(h * scale)
        resized = pil_img.resize((sw, sh), Image.Resampling.LANCZOS)
        resized.thumbnail((450, 410), Image.Resampling.LANCZOS)
        
        ox = (512 - resized.width) // 2
        oy = (410 - resized.height) // 2 + 15 + dy
        canvas.paste(resized, (ox, oy), resized)
        
        d = ImageDraw.Draw(canvas)
        font = get_font(25)
        draw_text_centered(d, banner_text, (256, 475), font, fill="#FEF08A", stroke_fill=stroke_color, stroke_width=5)
        
        # Add subtle animated sparkle / laugh text
        if anim_type == "bounce" and (f % 2 == 0):
            d.text((360, 50), "HA!", font=get_font(28), fill="#FDE047", stroke_fill="black", stroke_width=3)
        elif anim_type == "pulse":
            # Sparkle flare
            sx, sy = 400 + int(math.sin(phase)*20), 80
            sz = 8 + (f % 3) * 6
            d.polygon([(sx, sy-sz), (sx+3, sy-3), (sx+sz, sy), (sx+3, sy+3), (sx, sy+sz), (sx-3, sy+3), (sx-sz, sy), (sx-3, sy-3)], fill="#FEF08A")
            
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
# BUILD 10 REAL PHOTOREALISTIC ANIMATED GRETCHEN STICKERS
# ══════════════════════════════════════════════════
print("Building 10 Real Photorealistic Animated Gretchen Stickers...")
pack_dir_6 = os.path.join(PACKS_BASE_DIR, 'br-gretchen-rainha')
os.makedirs(pack_dir_6, exist_ok=True)

gretchen_files = [
    ("gretchen_laughing_1786903694400.jpg", "GRETCHEN RINDO 😂", "#7E22CE", "bounce"),
    ("gretchen_coffee_real_1787080845018.jpg", "TOMANDO CAFÉ NA PAZ ☕", "#7E22CE", "sway"),
    ("gretchen_eyeroll_real_1787080863096.jpg", "REVIRANDO OS OLHOS 🙄", "#7E22CE", "pulse"),
    ("gretchen_conga_real_1787080883426.jpg", "CONGA CONGA CONGA 💃", "#BE123C", "bounce"),
    ("gretchen_crying_real_1787080905251.jpg", "CHORANDO COM ÓCULOS 😭", "#1E293B", "sway"),
    ("gretchen_typing_real_1787080927443.jpg", "DIGITANDO NERVOSA 💻", "#B45309", "bounce"),
    ("gretchen_curtain_real_1787080951274.jpg", "ESPIANDO NA CORTINA 👀", "#991B1B", "sway"),
    ("gretchen_mic_real_1787080978923.jpg", "DROP THE MIC 🎤", "#4338CA", "pulse"),
    ("gretchen_queen_real_1787081007694.jpg", "DEUSA DA INTERNET 👑", "#B45309", "pulse"),
    ("gretchen_sassy_real_1787081040432.jpg", "CHAMA NO DEBOCHE 💅", "#BE123C", "sway"),
]

for idx, (fname, title, color, atype) in enumerate(gretchen_files, 1):
    fpath = os.path.join(ARTIFACT_DIR, fname)
    cutout = extract_pure_transparent_sticker(fpath)
    out_webp = os.path.join(pack_dir_6, f"{idx}.webp")
    f0 = make_real_animated_webp(cutout, out_webp, title, color, atype)
    if idx == 1:
        make_tray(f0, os.path.join(pack_dir_6, "tray_icon.png"))
    print(f"Pack 6: Generated Real Photo Animated {idx}.webp -> {fname}")

print("\nPack 6 (br-gretchen-rainha) finished successfully with 10 REAL PHOTOREALISTIC animated stickers!")
