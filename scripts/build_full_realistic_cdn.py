import os
import glob
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

def extract_transparent_sticker(img_path):
    """Accurately cuts out the subject & white border and makes outer checkerboard 100% transparent."""
    bgr = cv2.imread(img_path)
    if bgr is None:
        raise ValueError("Cannot open " + img_path)
    
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    
    # Foreground regions have saturation > 15 OR luminance < 200 (dark clothing/hair)
    color_mask = (sat > 14).astype(np.uint8) * 255
    dark_mask = (val < 190).astype(np.uint8) * 255
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

def save_static_sticker(pil_img, out_path, banner_text="", banner_color="#E11D48"):
    canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    pil_img.thumbnail((470, 470), Image.Resampling.LANCZOS)
    
    offset_y = (470 - pil_img.height) // 2
    offset_x = (512 - pil_img.width) // 2
    canvas.paste(pil_img, (offset_x, offset_y), pil_img)
    
    if banner_text:
        d = ImageDraw.Draw(canvas)
        font = get_font(28)
        draw_text_centered(d, banner_text, (256, 475), font, fill="white", stroke_fill=banner_color, stroke_width=5)
        
    canvas.save(out_path, format="WEBP", lossless=True)
    return canvas

def save_animated_sticker(pil_img, out_path, banner_text="", anim_type="pulse"):
    frames = []
    w, h = pil_img.size
    for f in range(6):
        phase = (f / 6.0) * 2 * math.pi
        canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        
        if anim_type == "pulse":
            scale = 0.94 + 0.08 * math.sin(phase)
            sw, sh = int(w * scale), int(h * scale)
            resized = pil_img.resize((sw, sh), Image.Resampling.LANCZOS)
            resized.thumbnail((470, 470), Image.Resampling.LANCZOS)
            ox = (512 - resized.width) // 2
            oy = (460 - resized.height) // 2
            canvas.paste(resized, (ox, oy), resized)
        elif anim_type == "sway":
            sway_x = int(math.sin(phase) * 16)
            pil_img_c = pil_img.copy()
            pil_img_c.thumbnail((460, 460), Image.Resampling.LANCZOS)
            ox = (512 - pil_img_c.width) // 2 + sway_x
            oy = (460 - pil_img_c.height) // 2
            canvas.paste(pil_img_c, (ox, oy), pil_img_c)
        else:
            bounce_y = int(abs(math.sin(phase)) * 16)
            pil_img_c = pil_img.copy()
            pil_img_c.thumbnail((460, 460), Image.Resampling.LANCZOS)
            ox = (512 - pil_img_c.width) // 2
            oy = (460 - pil_img_c.height) // 2 - bounce_y
            canvas.paste(pil_img_c, (ox, oy), pil_img_c)
            
        if banner_text:
            d = ImageDraw.Draw(canvas)
            font = get_font(28)
            draw_text_centered(d, banner_text, (256, 475), font, fill="#FEF08A", stroke_fill="#0F172A", stroke_width=5)
            
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

def save_tray_icon(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((90, 90), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

print("Pipeline builder defined successfully!")
