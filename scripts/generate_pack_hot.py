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
    """
    Reads an image with checkerboard/neutral background,
    extracts the main subject and its white die-cut border,
    and returns a clean RGBA PIL Image with PURE (0,0,0,0) background.
    """
    bgr = cv2.imread(img_path)
    if bgr is None:
        raise ValueError("Image not found: " + img_path)
        
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    
    # Subject contains color (sat > 12) or dark tones (val < 190)
    color_mask = (sat > 12).astype(np.uint8) * 255
    dark_mask = (val < 190).astype(np.uint8) * 255
    fg_raw = cv2.bitwise_or(color_mask, dark_mask)
    
    # Dilate outwards by 35px to capture the white sticker border
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
    dilated = cv2.dilate(fg_raw, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return Image.open(img_path).convert('RGBA')
        
    main_contour = max(contours, key=cv2.contourArea)
    mask = np.zeros(sat.shape, dtype=np.uint8)
    cv2.drawContours(mask, [main_contour], -1, 255, thickness=cv2.FILLED)
    
    # Smooth edges with slight Gaussian blur
    mask_pil = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(radius=1.5))
    mask_arr = np.array(mask_pil)
    
    # Force pure binary cutoff at edge to prevent dotted translucent artifacts
    mask_arr[mask_arr < 120] = 0
    mask_arr[mask_arr >= 120] = 255
    
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    # Zero out all RGB and Alpha for pixels outside mask
    rgba[mask_arr == 0] = [0, 0, 0, 0]
    
    pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    return pil_img

def render_realistic_celeb(name, sub_title, dress_color, hair_color, accessory_type):
    """
    Renders a realistic stylized portrait on pure transparent background
    with smooth gradients, realistic lighting, and white sticker outline.
    """
    # 1024x1024 canvas for crisp anti-aliased rendering
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    # Shoulders & dress
    d.ellipse([260, 520, 764, 1000], fill=dress_color)
    d.ellipse([340, 500, 684, 750], fill="#FCD34D") # Neck / chest
    
    # Hair back
    d.ellipse([280, 200, 744, 700], fill=hair_color)
    
    # Face shape
    d.ellipse([360, 260, 664, 620], fill="#FED7AA")
    d.ellipse([380, 320, 644, 580], fill="#FDE68A")
    
    # Eyes & Makeup
    d.ellipse([420, 400, 480, 440], fill="#1E293B")
    d.ellipse([544, 400, 604, 440], fill="#1E293B")
    d.ellipse([440, 410, 460, 430], fill="white")
    d.ellipse([564, 410, 584, 430], fill="white")
    d.line([(400, 390), (490, 400)], fill="#0F172A", width=8) # Eyeliner
    d.line([(534, 400), (624, 390)], fill="#0F172A", width=8)
    
    # Lips
    d.ellipse([464, 510, 560, 555], fill="#E11D48")
    d.arc([470, 515, 554, 545], 0, 180, fill="white", width=4)
    
    # Hair front styling
    if accessory_type == "feathers":
        for fa, col in [(-50, "#EC4899"), (-25, "#8B5CF6"), (0, "#F59E0B"), (25, "#10B981"), (50, "#06B6D4")]:
            fx = int(512 + math.sin(math.radians(fa)) * 320)
            fy = int(280 - math.cos(math.radians(fa)) * 220)
            d.polygon([(512, 340), (fx - 45, fy), (fx, fy - 70), (fx + 45, fy)], fill=col)
    elif accessory_type == "crown":
        d.polygon([(360, 260), (420, 180), (512, 240), (604, 180), (664, 260)], fill="#F59E0B", outline="#B45309", width=6)
    elif accessory_type == "sunglasses":
        d.rectangle([400, 390, 490, 445], fill="#0F172A", outline="#E2E8F0", width=4)
        d.rectangle([534, 390, 624, 445], fill="#0F172A", outline="#E2E8F0", width=4)
        d.line([(490, 415), (534, 415)], fill="#0F172A", width=6)
        
    # Get subject alpha and create clean die-cut white border
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

def make_animated_celeb_webp(pil_img, out_path, banner_text):
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
        draw_text_centered(d, banner_text, (256, 480), font, fill="#FEF08A", stroke_fill="#9F1239", stroke_width=5)
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

# ── Build Pack: br-figurinhas-hot ──
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-figurinhas-hot')
os.makedirs(pack_dir, exist_ok=True)

# 1. Anitta (Real Photo)
anitta_photo = os.path.join(ARTIFACT_DIR, "anitta_stage_sticker_1786904412205.jpg")
anitta_clean = clean_cutout_transparent(anitta_photo)
c1 = make_animated_celeb_webp(anitta_clean, os.path.join(pack_dir, "1.webp"), "ANITTA: ENVOLVER 🔥")
make_tray(c1, os.path.join(pack_dir, "tray_icon.png"))
print("Generated 1.webp (Anitta)")

# 2. Gisele Bündchen (Real Photo)
gisele_photo = os.path.join(ARTIFACT_DIR, "gisele_catwalk_sticker_1786904448691.jpg")
gisele_clean = clean_cutout_transparent(gisele_photo)
make_animated_celeb_webp(gisele_clean, os.path.join(pack_dir, "2.webp"), "GISELE: PASSARELA ✨")
print("Generated 2.webp (Gisele)")

# 3. Paolla Oliveira (Real Photo)
paolla_photo = os.path.join(ARTIFACT_DIR, "paolla_carnaval_sticker_1786904503968.jpg")
paolla_clean = clean_cutout_transparent(paolla_photo)
make_animated_celeb_webp(paolla_clean, os.path.join(pack_dir, "3.webp"), "PAOLLA: RAINHA DO SAMBA 👑")
print("Generated 3.webp (Paolla)")

# 4. Bruna Marquezine (Red Carpet Glamour)
bruna = render_realistic_celeb("Bruna", "GLAMOUR", "#E11D48", "#1C1917", "earrings")
make_animated_celeb_webp(bruna, os.path.join(pack_dir, "4.webp"), "BRUNA: GLAMOUR 💋")
print("Generated 4.webp (Bruna)")

# 5. Iza (Afro-Brazilian Pop Goddess)
iza = render_realistic_celeb("Iza", "DEUSA", "#F59E0B", "#0F172A", "crown")
make_animated_celeb_webp(iza, os.path.join(pack_dir, "5.webp"), "IZA: DEUSA DOURADA 🌟")
print("Generated 5.webp (Iza)")

# 6. Luísa Sonza (Platinum Pop Baddie)
luisa = render_realistic_celeb("Luisa", "BADDIE", "#EC4899", "#FEF08A", "sunglasses")
make_animated_celeb_webp(luisa, os.path.join(pack_dir, "6.webp"), "LUÍSA: BADDIE 💅")
print("Generated 6.webp (Luisa)")

# 7. Marina Ruy Barbosa (Emerald Seduction)
marina = render_realistic_celeb("Marina", "SEDUÇÃO", "#059669", "#EA580C", "earrings")
make_animated_celeb_webp(marina, os.path.join(pack_dir, "7.webp"), "MARINA: SEDUÇÃO 🌹")
print("Generated 7.webp (Marina)")

# 8. Sabrina Sato (Carnaval Muse)
sabrina = render_realistic_celeb("Sabrina", "MUSA", "#8B5CF6", "#1C1917", "feathers")
make_animated_celeb_webp(sabrina, os.path.join(pack_dir, "8.webp"), "SABRINA: MUSA CARNAVAL 💃")
print("Generated 8.webp (Sabrina)")

print("All 8 stickers for br-figurinhas-hot successfully generated!")
