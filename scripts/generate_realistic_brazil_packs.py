import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

PACKS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', 'packs')

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

def draw_star(draw, center, r_outer, r_inner, points=5, fill="yellow", outline=None, width=1):
    cx, cy = center
    pts = []
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        angle = i * math.pi / points - math.pi / 2
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=fill, outline=outline, width=width)

def finalize_sticker(canvas, out_path, is_tray=False):
    """
    Ensures 100% genuine alpha transparency outside the content,
    trims whitespace if needed, scales to 512x512 with proper padding,
    and saves as crisp WebP.
    """
    # Crop to non-transparent bounding box
    bbox = canvas.getbbox()
    if bbox:
        cropped = canvas.crop(bbox)
    else:
        cropped = canvas
    
    target_size = (96, 96) if is_tray else (512, 512)
    max_dim = 90 if is_tray else 480
    
    cropped.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    
    out_img = Image.new('RGBA', target_size, (0, 0, 0, 0))
    offset = ((target_size[0] - cropped.width) // 2, (target_size[1] - cropped.height) // 2)
    out_img.paste(cropped, offset, cropped)
    
    if is_tray and out_path.endswith('.png'):
        out_img.save(out_path, format="PNG")
    else:
        out_img.save(out_path, format="WEBP", lossless=True)
    return out_img

def save_animated_webp(frames, out_path, duration=130):
    processed = []
    for f in frames:
        bbox = f.getbbox()
        cropped = f.crop(bbox) if bbox else f
        cropped.thumbnail((480, 480), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        offset = ((512 - cropped.width) // 2, (512 - cropped.height) // 2)
        canvas.paste(cropped, offset, cropped)
        processed.append(canvas)
        
    processed[0].save(
        out_path,
        format="WEBP",
        save_all=True,
        append_images=processed[1:],
        duration=duration,
        loop=0,
        lossless=False,
        quality=90
    )
    return processed[0]

def create_pack_folder(pack_id):
    p = os.path.join(PACKS_BASE_DIR, pack_id)
    os.makedirs(p, exist_ok=True)
    return p

# ── Helper for Die-Cut Sticker Effect ──
def create_sticker_badge(subject_img, banner_text="", banner_color="#E11D48", text_color="white"):
    """Wraps any subject image into a WhatsApp sticker with white die-cut contour & transparent background."""
    w, h = subject_img.size
    # Create mask of subject
    alpha = subject_img.split()[3] if subject_img.mode == 'RGBA' else Image.new('L', (w, h), 255)
    
    # Expand alpha mask to create white sticker outline
    outline_mask = alpha.filter(ImageFilter.MaxFilter(25))
    outline_mask = outline_mask.filter(ImageFilter.GaussianBlur(2))
    
    # Base canvas
    sticker = Image.new('RGBA', (w + 40, h + 60), (0, 0, 0, 0))
    white_layer = Image.new('RGBA', sticker.size, (255, 255, 255, 255))
    
    # Paste white border
    sticker.paste(white_layer, (20, 20), outline_mask)
    # Paste original subject
    sticker.paste(subject_img, (20, 20), subject_img if subject_img.mode == 'RGBA' else None)
    
    if banner_text:
        draw = ImageDraw.Draw(sticker)
        font = get_font(26)
        draw_text_centered(draw, banner_text, (sticker.width // 2, sticker.height - 25), font, fill=text_color, stroke_fill="black", stroke_width=4)
        
    return sticker

print("Realistic sticker generator module loaded!")
