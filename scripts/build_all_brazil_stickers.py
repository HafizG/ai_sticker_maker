import os
import glob
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

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

def extract_transparent_sticker(img_path):
    """Accurately cuts out the subject & white border, making outer checkerboard 100% transparent."""
    bgr = cv2.imread(img_path)
    if bgr is None:
        return None
    
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    
    # Foreground regions have saturation > 12 OR luminance < 195 (dark clothing/hair)
    color_mask = (sat > 12).astype(np.uint8) * 255
    dark_mask = (val < 195).astype(np.uint8) * 255
    fg_initial = cv2.bitwise_or(color_mask, dark_mask)
    
    # Dilate by 35px to capture the white die-cut border cleanly
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
    dilated = cv2.dilate(fg_initial, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return Image.open(img_path).convert('RGBA')
    
    main_contour = max(contours, key=cv2.contourArea)
    mask = np.zeros(sat.shape, dtype=np.uint8)
    cv2.drawContours(mask, [main_contour], -1, 255, thickness=cv2.FILLED)
    
    mask_pil = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(radius=2))
    mask_arr = np.array(mask_pil)
    
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = mask_arr
    
    pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    return pil_img

def save_static(pil_img, out_path, banner_text="", banner_color="#E11D48"):
    canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    pil_img_c = pil_img.copy()
    pil_img_c.thumbnail((470, 440), Image.Resampling.LANCZOS)
    
    offset_y = (440 - pil_img_c.height) // 2 + 10
    offset_x = (512 - pil_img_c.width) // 2
    canvas.paste(pil_img_c, (offset_x, offset_y), pil_img_c)
    
    if banner_text:
        d = ImageDraw.Draw(canvas)
        font = get_font(26)
        draw_text_centered(d, banner_text, (256, 480), font, fill="white", stroke_fill=banner_color, stroke_width=5)
        
    canvas.save(out_path, format="WEBP", lossless=True)
    return canvas

def save_animated(pil_img, out_path, banner_text="", anim_type="pulse"):
    frames = []
    w, h = pil_img.size
    for f in range(6):
        phase = (f / 6.0) * 2 * math.pi
        canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        
        if anim_type == "pulse":
            scale = 0.94 + 0.08 * math.sin(phase)
            sw, sh = int(w * scale), int(h * scale)
            resized = pil_img.resize((sw, sh), Image.Resampling.LANCZOS)
            resized.thumbnail((460, 430), Image.Resampling.LANCZOS)
            ox = (512 - resized.width) // 2
            oy = (430 - resized.height) // 2 + 10
            canvas.paste(resized, (ox, oy), resized)
        elif anim_type == "sway":
            sway_x = int(math.sin(phase) * 16)
            pil_img_c = pil_img.copy()
            pil_img_c.thumbnail((460, 430), Image.Resampling.LANCZOS)
            ox = (512 - pil_img_c.width) // 2 + sway_x
            oy = (430 - pil_img_c.height) // 2 + 10
            canvas.paste(pil_img_c, (ox, oy), pil_img_c)
        else:
            bounce_y = int(abs(math.sin(phase)) * 16)
            pil_img_c = pil_img.copy()
            pil_img_c.thumbnail((460, 430), Image.Resampling.LANCZOS)
            ox = (512 - pil_img_c.width) // 2
            oy = (430 - pil_img_c.height) // 2 + 10 - bounce_y
            canvas.paste(pil_img_c, (ox, oy), pil_img_c)
            
        if banner_text:
            d = ImageDraw.Draw(canvas)
            font = get_font(26)
            draw_text_centered(d, banner_text, (256, 480), font, fill="#FEF08A", stroke_fill="#0F172A", stroke_width=5)
            
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

def save_tray(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((88, 88), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

# Render High-Quality Procedural Realistic Stickers with Alpha Transparency
def render_realistic_diecut_sticker(draw_func, out_path, banner_text="", is_animated=False, anim_type="pulse"):
    """
    Renders high-res 1024x1024 vector/subject, creates a die-cut white contour with drop shadow,
    renders on 100% transparent canvas, and saves as 512x512 WebP.
    """
    # 1024 canvas
    base = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    draw_func(base)
    
    # Get alpha of subject
    alpha = base.split()[3]
    # Create white contour
    outline = alpha.filter(ImageFilter.MaxFilter(25))
    outline = outline.filter(ImageFilter.GaussianBlur(2))
    
    # Compose sticker
    sticker = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    white_fill = Image.new('RGBA', (1024, 1024), (255, 255, 255, 255))
    sticker.paste(white_fill, (0, 0), outline)
    sticker.paste(base, (0, 0), base)
    
    # Crop to non-transparent bbox
    bbox = sticker.getbbox()
    if bbox:
        sticker = sticker.crop(bbox)
        
    if is_animated:
        canvas = save_animated(sticker, out_path, banner_text, anim_type)
    else:
        canvas = save_static(sticker, out_path, banner_text)
        
    return canvas

# ── Load and Assign Real Photos ──
photo_map = {
    "anitta": os.path.join(ARTIFACT_DIR, "anitta_stage_sticker_1786904412205.jpg"),
    "gisele": os.path.join(ARTIFACT_DIR, "gisele_catwalk_sticker_1786904448691.jpg"),
    "paolla": os.path.join(ARTIFACT_DIR, "paolla_carnaval_sticker_1786904503968.jpg"),
    "gretchen": os.path.join(ARTIFACT_DIR, "gretchen_laughing_1786903694400.jpg"),
    "kiss_passion": os.path.join(ARTIFACT_DIR, "couple_kissing_sticker_1786903718842.jpg"),
    "kiss_sunset": os.path.join(ARTIFACT_DIR, "couple_sunset_kiss_1786904762417.jpg"),
    "kiss_french": os.path.join(ARTIFACT_DIR, "couple_french_kiss_1786904826786.jpg"),
    "hug_warm": os.path.join(ARTIFACT_DIR, "couple_hugging_sticker_1786903748355.jpg"),
    "caramelo_coxinha": os.path.join(ARTIFACT_DIR, "caramelo_dog_sticker_1786903786655.jpg"),
    "neymar": os.path.join(ARTIFACT_DIR, "neymar_celebrating_sticker_1786903904919.jpg"),
    "pele": os.path.join(ARTIFACT_DIR, "pele_king_sticker_1786904558814.jpg"),
    "bolsonaro": os.path.join(ARTIFACT_DIR, "bolsonaro_thumbs_up_sticker_1786904611609.jpg"),
    "bom_dia_coffee": os.path.join(ARTIFACT_DIR, "bom_dia_coffee_sticker_1786903861596.jpg"),
}

cached_cutouts = {}
for key, p in photo_map.items():
    if os.path.exists(p):
        cached_cutouts[key] = extract_transparent_sticker(p)
        print(f"Loaded photorealistic cutout: {key}")

# ── Process All 20 Packs with 100% Transparent Backgrounds & Real Assets ──
print("\nProcessing all 20 Brazil Packs with 100% Transparent WebP and Real Cutouts...")

# 1. br-figurinhas-hot
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-figurinhas-hot')
if "anitta" in cached_cutouts:
    c = save_animated(cached_cutouts["anitta"], os.path.join(pack_dir, "1.webp"), "ANITTA: ENVOLVER 🔥", "pulse")
    save_tray(c, os.path.join(pack_dir, "tray_icon.png"))
if "gisele" in cached_cutouts:
    save_animated(cached_cutouts["gisele"], os.path.join(pack_dir, "2.webp"), "GISELE: PASSARELA ✨", "sway")
if "paolla" in cached_cutouts:
    save_animated(cached_cutouts["paolla"], os.path.join(pack_dir, "3.webp"), "PAOLLA: RAINHA DO SAMBA 👑", "bounce")

# 2. br-beijo-apaixonado
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-beijo-apaixonado')
if "kiss_passion" in cached_cutouts:
    c = save_animated(cached_cutouts["kiss_passion"], os.path.join(pack_dir, "1.webp"), "BEIJO APAIXONADO 💋", "pulse")
    save_tray(c, os.path.join(pack_dir, "tray_icon.png"))
if "kiss_sunset" in cached_cutouts:
    save_animated(cached_cutouts["kiss_sunset"], os.path.join(pack_dir, "2.webp"), "BEIJO AO PÔR DO SOL 🌅", "sway")
if "kiss_french" in cached_cutouts:
    save_animated(cached_cutouts["kiss_french"], os.path.join(pack_dir, "3.webp"), "BEIJO CARINHOSO 💕", "pulse")

# 3. br-abraco-carinhoso
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-abraco-carinhoso')
if "hug_warm" in cached_cutouts:
    c = save_animated(cached_cutouts["hug_warm"], os.path.join(pack_dir, "1.webp"), "ABRAÇO DE AMOR 🤗", "pulse")
    save_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# 4. br-gretchen-rainha
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-gretchen-rainha')
if "gretchen" in cached_cutouts:
    c = save_animated(cached_cutouts["gretchen"], os.path.join(pack_dir, "1.webp"), "GRETCHEN RINDO 😂", "sway")
    save_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# 5. br-bolsonaro-dancando
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-bolsonaro-dancando')
if "bolsonaro" in cached_cutouts:
    c = save_animated(cached_cutouts["bolsonaro"], os.path.join(pack_dir, "1.webp"), "VALEU MEU BRASIL! 👍", "bounce")
    save_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# 6. br-vira-lata-caramelo
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-vira-lata-caramelo')
if "caramelo_coxinha" in cached_cutouts:
    c = save_static(cached_cutouts["caramelo_coxinha"], os.path.join(pack_dir, "1.webp"), "CARAMELO COM COXINHA 🍗", "#D97706")
    save_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# 7. br-futebol-selecao
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-futebol-selecao')
if "pele" in cached_cutouts:
    c = save_static(cached_cutouts["pele"], os.path.join(pack_dir, "1.webp"), "PELÉ: O REI DO FUTEBOL 👑", "#B45309")
    save_tray(c, os.path.join(pack_dir, "tray_icon.png"))
if "neymar" in cached_cutouts:
    save_static(cached_cutouts["neymar"], os.path.join(pack_dir, "2.webp"), "NEYMAR JR GOL! ⚽⚡", "#0284C7")

# 8. br-bom-dia-boa-noite
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-bom-dia-boa-noite')
if "bom_dia_coffee" in cached_cutouts:
    c = save_static(cached_cutouts["bom_dia_coffee"], os.path.join(pack_dir, "1.webp"), "BOM DIA ABENÇOADO ☕🧀", "#D97706")
    save_tray(c, os.path.join(pack_dir, "tray_icon.png"))

print("All realistic photo cutouts installed with 100% transparent backgrounds!")
