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

def render_realistic_hug(scene_type):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    if scene_type == "airport":
        # Emotional reunion hug
        d.ellipse([260, 420, 560, 920], fill="#1E3A8A") # Man
        d.ellipse([460, 440, 760, 940], fill="#DB2777") # Woman
        d.ellipse([340, 220, 530, 450], fill="#FED7AA")
        d.ellipse([480, 240, 670, 470], fill="#FDE68A")
        # Suitcase
        d.rounded_rectangle([720, 580, 880, 880], radius=20, fill="#D97706", outline="#78350F", width=6)
    elif scene_type == "blanket":
        # Cozy blanket cuddle
        d.rounded_rectangle([220, 360, 804, 900], radius=80, fill="#93C5FD", outline="#1D4ED8", width=8)
        d.ellipse([340, 240, 510, 440], fill="#FED7AA")
        d.ellipse([490, 240, 660, 440], fill="#FDE68A")
        # Steaming mug
        d.rectangle([460, 580, 560, 680], fill="#F59E0B")
    elif scene_type == "mom":
        # Mother and child hug
        d.ellipse([340, 320, 740, 920], fill="#8B5CF6") # Mom
        d.ellipse([440, 200, 640, 420], fill="#FDE68A")
        d.ellipse([280, 540, 480, 880], fill="#F43F5E") # Child
        d.ellipse([320, 420, 460, 580], fill="#FED7AA")
    elif scene_type == "friends":
        # Best friends celebration hug
        d.ellipse([220, 420, 480, 920], fill="#10B981")
        d.ellipse([544, 420, 804, 920], fill="#F59E0B")
        d.ellipse([300, 240, 460, 440], fill="#FED7AA")
        d.ellipse([564, 240, 724, 440], fill="#FED7AA")
        d.ellipse([420, 160, 604, 340], fill="#EF4444") # Big heart above
    elif scene_type == "comfort":
        # Gentle comforting shoulder hug
        d.ellipse([260, 420, 560, 920], fill="#475569")
        d.ellipse([460, 440, 760, 940], fill="#0284C7")
        d.ellipse([340, 240, 520, 450], fill="#FED7AA")
        d.ellipse([480, 260, 660, 470], fill="#FDE68A")
    elif scene_type == "back":
        # Surprise back hug
        d.ellipse([320, 400, 680, 920], fill="#E11D48") # Front person
        d.ellipse([420, 220, 580, 420], fill="#FDE68A")
        d.ellipse([460, 360, 800, 900], fill="#1E293B") # Back person hugging
        d.ellipse([540, 200, 700, 400], fill="#FED7AA")
    else: # pets
        # Cute puppy and kitten cuddle
        d.ellipse([260, 420, 540, 760], fill="#D97706") # Dog
        d.ellipse([220, 360, 320, 520], fill="#B45309")
        d.ellipse([460, 440, 740, 760], fill="#94A3B8") # Cat
        d.polygon([(480, 360), (540, 460), (460, 460)], fill="#64748B")
        d.polygon([(660, 360), (720, 460), (640, 460)], fill="#64748B")
        
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

def make_animated_hug_webp(pil_img, out_path, banner_text):
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
        draw_text_centered(d, banner_text, (256, 480), font, fill="#FEF08A", stroke_fill="#9D174D", stroke_width=5)
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

# ── Build Pack: br-abraco-carinhoso ──
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-abraco-carinhoso')
os.makedirs(pack_dir, exist_ok=True)

# 1. Real Photo Couple Hug
p1 = os.path.join(ARTIFACT_DIR, "couple_hugging_sticker_1786903748355.jpg")
c1_clean = clean_cutout_transparent(p1)
c1 = make_animated_hug_webp(c1_clean, os.path.join(pack_dir, "1.webp"), "ABRAÇO DE AMOR 🤗")
make_tray(c1, os.path.join(pack_dir, "tray_icon.png"))
print("Generated 1.webp (Couple Hug)")

# 2. Airport Reunion Hug
st2 = render_realistic_hug("airport")
make_animated_hug_webp(st2, os.path.join(pack_dir, "2.webp"), "REENCONTRO NO AEROPORTO ✈️")
print("Generated 2.webp (Airport Hug)")

# 3. Blanket Cuddle
st3 = render_realistic_hug("blanket")
make_animated_hug_webp(st3, os.path.join(pack_dir, "3.webp"), "BURRITO DE COBERTOR 🌯")
print("Generated 3.webp (Blanket Cuddle)")

# 4. Mom & Child Loving Hug
st4 = render_realistic_hug("mom")
make_animated_hug_webp(st4, os.path.join(pack_dir, "4.webp"), "COLO DE MÃE ❤️")
print("Generated 4.webp (Mom Hug)")

# 5. Best Friends Hug
st5 = render_realistic_hug("friends")
make_animated_hug_webp(st5, os.path.join(pack_dir, "5.webp"), "ABRAÇO DE AMIGOS 🎉")
print("Generated 5.webp (Friends Hug)")

# 6. Gentle Comfort Hug
st6 = render_realistic_hug("comfort")
make_animated_hug_webp(st6, os.path.join(pack_dir, "6.webp"), "CONFORTO NO CORAÇÃO 🥺")
print("Generated 6.webp (Comfort Hug)")

# 7. Surprise Back Hug
st7 = render_realistic_hug("back")
make_animated_hug_webp(st7, os.path.join(pack_dir, "7.webp"), "ABRAÇO SURPRESA 🥰")
print("Generated 7.webp (Back Hug)")

# 8. Puppy & Kitten Cuddle
st8 = render_realistic_hug("pets")
make_animated_hug_webp(st8, os.path.join(pack_dir, "8.webp"), "CARINHO MAIS FOFO 🐶🐱")
print("Generated 8.webp (Pets Hug)")

print("All 8 stickers for br-abraco-carinhoso successfully generated!")
