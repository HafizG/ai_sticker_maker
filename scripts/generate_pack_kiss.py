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

def clean_cutout_transparent(img_path):
    bgr = cv2.imread(img_path)
    if bgr is None:
        raise ValueError("Image not found: " + img_path)
        
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    
    color_mask = (sat > 12).astype(np.uint8) * 255
    dark_mask = (val < 190).astype(np.uint8) * 255
    fg_raw = cv2.bitwise_or(color_mask, dark_mask)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
    dilated = cv2.dilate(fg_raw, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return Image.open(img_path).convert('RGBA')
        
    main_contour = max(contours, key=cv2.contourArea)
    mask = np.zeros(sat.shape, dtype=np.uint8)
    cv2.drawContours(mask, [main_contour], -1, 255, thickness=cv2.FILLED)
    
    mask_pil = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(radius=1.5))
    mask_arr = np.array(mask_pil)
    mask_arr[mask_arr < 120] = 0
    mask_arr[mask_arr >= 120] = 255
    
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[mask_arr == 0] = [0, 0, 0, 0]
    
    pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    return pil_img

def render_realistic_kiss(scene_type):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    if scene_type == "forehead":
        # Man kissing woman's forehead
        d.ellipse([260, 480, 560, 960], fill="#1E3A8A") # Man body
        d.ellipse([460, 520, 780, 980], fill="#BE185D") # Woman body
        d.ellipse([340, 240, 540, 500], fill="#FED7AA") # Man head
        d.arc([320, 200, 540, 400], 180, 360, fill="#334155", width=45) # Hair
        d.ellipse([460, 320, 680, 580], fill="#FDE68A") # Woman head
        d.arc([460, 280, 700, 620], 0, 180, fill="#78350F", width=55)
        # Man lips on forehead
        d.ellipse([470, 370, 510, 395], fill="#E11D48")
    elif scene_type == "rain":
        # Umbrella over couple
        d.pieslice([240, 120, 784, 460], 180, 360, fill="#EF4444")
        d.line([(512, 120), (512, 540)], fill="#334155", width=12)
        d.ellipse([300, 460, 540, 920], fill="#334155")
        d.ellipse([480, 460, 720, 920], fill="#F43F5E")
        d.ellipse([370, 300, 520, 480], fill="#FED7AA")
        d.ellipse([490, 300, 640, 480], fill="#FDE68A")
        d.ellipse([480, 390, 530, 420], fill="#E11D48")
    elif scene_type == "cheek":
        # Woman kissing man's cheek with lipstick mark
        d.ellipse([260, 460, 560, 920], fill="#2563EB")
        d.ellipse([460, 460, 760, 920], fill="#EC4899")
        d.ellipse([330, 260, 550, 520], fill="#FED7AA")
        d.ellipse([470, 260, 690, 520], fill="#FDE68A")
        # Heart cheek kiss
        d.ellipse([430, 380, 465, 405], fill="#E11D48")
        d.ellipse([450, 380, 485, 405], fill="#E11D48")
    elif scene_type == "candlelight":
        # Candlelight dinner kiss
        d.ellipse([300, 460, 540, 920], fill="#0F172A")
        d.ellipse([480, 460, 720, 920], fill="#991B1B")
        d.ellipse([360, 260, 530, 480], fill="#FED7AA")
        d.ellipse([480, 260, 650, 480], fill="#FED7AA")
        d.ellipse([480, 370, 530, 400], fill="#E11D48")
        # Glowing candle
        d.rectangle([490, 680, 534, 820], fill="#FEF08A")
        d.ellipse([496, 630, 528, 680], fill="#F59E0B")
    else: # airport
        # Reunion kiss with suitcase
        d.ellipse([280, 440, 540, 920], fill="#1E293B")
        d.ellipse([480, 440, 740, 920], fill="#059669")
        d.ellipse([360, 250, 530, 460], fill="#FED7AA")
        d.ellipse([480, 250, 650, 460], fill="#FDE68A")
        d.ellipse([480, 360, 530, 390], fill="#E11D48")
        d.rounded_rectangle([720, 620, 860, 880], radius=15, fill="#D97706", outline="#78350F", width=6)
        
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

def make_animated_kiss_webp(pil_img, out_path, banner_text):
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
        draw_text_centered(d, banner_text, (256, 480), font, fill="#FEF08A", stroke_fill="#BE123C", stroke_width=5)
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

# ── Build Pack: br-beijo-apaixonado ──
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-beijo-apaixonado')
os.makedirs(pack_dir, exist_ok=True)

# 1. Real Photo Passion Kiss
p1 = os.path.join(ARTIFACT_DIR, "couple_kissing_sticker_1786903718842.jpg")
c1_clean = clean_cutout_transparent(p1)
c1 = make_animated_kiss_webp(c1_clean, os.path.join(pack_dir, "1.webp"), "BEIJO APAIXONADO 💋")
make_tray(c1, os.path.join(pack_dir, "tray_icon.png"))
print("Generated 1.webp (Passion Kiss)")

# 2. Real Photo Sunset Kiss
p2 = os.path.join(ARTIFACT_DIR, "couple_sunset_kiss_1786904762417.jpg")
c2_clean = clean_cutout_transparent(p2)
make_animated_kiss_webp(c2_clean, os.path.join(pack_dir, "2.webp"), "BEIJO AO PÔR DO SOL 🌅")
print("Generated 2.webp (Sunset Kiss)")

# 3. Real Photo French Kiss
p3 = os.path.join(ARTIFACT_DIR, "couple_french_kiss_1786904826786.jpg")
c3_clean = clean_cutout_transparent(p3)
make_animated_kiss_webp(c3_clean, os.path.join(pack_dir, "3.webp"), "BEIJO CARINHOSO 💕")
print("Generated 3.webp (French Kiss)")

# 4. Forehead Kiss
st4 = render_realistic_kiss("forehead")
make_animated_kiss_webp(st4, os.path.join(pack_dir, "4.webp"), "BEIJO NA TESTA 🥺")
print("Generated 4.webp (Forehead Kiss)")

# 5. Rainy Umbrella Kiss
st5 = render_realistic_kiss("rain")
make_animated_kiss_webp(st5, os.path.join(pack_dir, "5.webp"), "BEIJO NA CHUVA ☔")
print("Generated 5.webp (Rain Kiss)")

# 6. Cheek Kiss
st6 = render_realistic_kiss("cheek")
make_animated_kiss_webp(st6, os.path.join(pack_dir, "6.webp"), "BEIJINHO NA BOCHECHA 🥰")
print("Generated 6.webp (Cheek Kiss)")

# 7. Candlelight Dinner Kiss
st7 = render_realistic_kiss("candlelight")
make_animated_kiss_webp(st7, os.path.join(pack_dir, "7.webp"), "JANTAR ROMÂNTICO 🕯️")
print("Generated 7.webp (Candlelight Kiss)")

# 8. Airport Reunion Kiss
st8 = render_realistic_kiss("airport")
make_animated_kiss_webp(st8, os.path.join(pack_dir, "8.webp"), "BEIJO DE SAUDADE ✈️")
print("Generated 8.webp (Airport Kiss)")

print("All 8 stickers for br-beijo-apaixonado successfully generated!")
