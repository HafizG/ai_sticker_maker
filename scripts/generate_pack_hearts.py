import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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

def render_realistic_heart(heart_type):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    if heart_type == "ruby":
        # Ruby faceted heart
        pts = [(512, 860), (220, 480), (220, 320), (360, 200), (512, 340), (664, 200), (804, 320), (804, 480)]
        d.polygon(pts, fill="#E11D48")
        # Facets
        d.polygon([(512, 860), (512, 340), (360, 200)], fill="#BE123C")
        d.polygon([(512, 860), (512, 340), (664, 200)], fill="#F43F5E")
        d.polygon([(220, 320), (360, 200), (512, 340)], fill="#FB7185")
        d.polygon([(804, 320), (664, 200), (512, 340)], fill="#FDA4AF")
    elif heart_type == "diamond":
        # Golden Diamond heart
        pts = [(512, 860), (220, 480), (220, 320), (360, 200), (512, 340), (664, 200), (804, 320), (804, 480)]
        d.polygon(pts, fill="#F59E0B")
        d.polygon([(512, 860), (512, 340), (360, 200)], fill="#D97706")
        d.polygon([(512, 860), (512, 340), (664, 200)], fill="#FDE047")
        d.polygon([(220, 320), (360, 200), (512, 340)], fill="#FEF08A")
        # Sparkles
        for sx, sy in [(280, 280), (740, 300), (512, 820)]:
            d.polygon([(sx, sy-35), (sx+10, sy-10), (sx+35, sy), (sx+10, sy+10), (sx, sy+35), (sx-10, sy+10), (sx-35, sy), (sx-10, sy-10)], fill="white")
    elif heart_type == "fire":
        # Flame heart
        d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#DC2626")
        d.pieslice([240, 200, 520, 480], 180, 0, fill="#DC2626")
        d.pieslice([504, 200, 784, 480], 180, 0, fill="#DC2626")
        # Inner flame
        d.polygon([(512, 780), (340, 480), (380, 320), (512, 420), (644, 320), (684, 480)], fill="#F59E0B")
        d.polygon([(512, 700), (400, 480), (440, 380), (512, 460), (584, 380), (624, 480)], fill="#FEF08A")
    elif heart_type == "neon":
        # Neon cyberpunk heart
        d.polygon([(512, 860), (200, 460), (280, 240), (512, 380), (744, 240), (824, 460)], fill="#0F172A", outline="#EC4899", width=22)
        d.pieslice([220, 180, 520, 480], 180, 0, fill="#0F172A", outline="#EC4899", width=22)
        d.pieslice([504, 180, 804, 480], 180, 0, fill="#0F172A", outline="#EC4899", width=22)
        # Inner neon glow
        d.polygon([(512, 760), (280, 460), (340, 300), (512, 420), (684, 300), (744, 460)], outline="#06B6D4", width=12)
    elif heart_type == "rose":
        # Glass heart with blooming rose inside
        d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#FCE7F3", outline="#F43F5E", width=12)
        d.pieslice([240, 200, 520, 480], 180, 0, fill="#FCE7F3", outline="#F43F5E", width=12)
        d.pieslice([504, 200, 784, 480], 180, 0, fill="#FCE7F3", outline="#F43F5E", width=12)
        # Red Rose
        d.ellipse([420, 420, 604, 604], fill="#BE123C")
        d.ellipse([460, 450, 564, 554], fill="#E11D48")
        d.ellipse([484, 474, 540, 530], fill="#FDA4AF")
        # Green leaves
        d.polygon([(380, 560), (320, 600), (380, 640)], fill="#15803D")
        d.polygon([(644, 560), (704, 600), (644, 640)], fill="#15803D")
    elif heart_type == "galaxy":
        # Cosmic galaxy heart
        d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#1E1B4B")
        d.pieslice([240, 200, 520, 480], 180, 0, fill="#1E1B4B")
        d.pieslice([504, 200, 784, 480], 180, 0, fill="#1E1B4B")
        # Spiral stars
        d.ellipse([360, 420, 664, 620], fill="#6366F1")
        d.ellipse([420, 460, 604, 580], fill="#A855F7")
        d.ellipse([470, 490, 554, 550], fill="#F472B6")
        for sx, sy in [(340, 360), (680, 340), (440, 680), (580, 660), (512, 520)]:
            d.ellipse([sx-10, sy-10, sx+10, sy+10], fill="white")
    elif heart_type == "water":
        # Water ripple crystal heart
        d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#0284C7")
        d.pieslice([240, 200, 520, 480], 180, 0, fill="#0284C7")
        d.pieslice([504, 200, 784, 480], 180, 0, fill="#0284C7")
        # Water ripples
        d.ellipse([340, 400, 684, 640], outline="#E0F2FE", width=12)
        d.ellipse([400, 450, 624, 590], outline="#E0F2FE", width=8)
    else: # cupid
        # Golden arrow piercing heart
        d.polygon([(512, 860), (220, 460), (280, 240), (512, 360), (744, 240), (804, 460)], fill="#BE123C")
        d.pieslice([240, 200, 520, 480], 180, 0, fill="#BE123C")
        d.pieslice([504, 200, 784, 480], 180, 0, fill="#BE123C")
        # Golden arrow
        d.line([(140, 680), (884, 320)], fill="#F59E0B", width=18)
        d.polygon([(860, 290), (920, 300), (890, 360)], fill="#D97706") # Arrow head
        d.polygon([(140, 650), (100, 700), (160, 710)], fill="#D97706") # Feathers
        
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

def make_animated_heart_webp(pil_img, out_path, banner_text):
    frames = []
    w, h = pil_img.size
    for f in range(6):
        phase = (f / 6.0) * 2 * math.pi
        canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        
        scale = 0.92 + 0.10 * math.sin(phase)
        sw, sh = int(w * scale), int(h * scale)
        resized = pil_img.resize((sw, sh), Image.Resampling.LANCZOS)
        resized.thumbnail((450, 420), Image.Resampling.LANCZOS)
        
        ox = (512 - resized.width) // 2
        oy = (420 - resized.height) // 2 + 10
        canvas.paste(resized, (ox, oy), resized)
        
        d = ImageDraw.Draw(canvas)
        font = get_font(26)
        draw_text_centered(d, banner_text, (256, 480), font, fill="#FEF08A", stroke_fill="#991B1B", stroke_width=5)
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

# ── Build Pack: br-coracao-paixao ──
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-coracao-paixao')
os.makedirs(pack_dir, exist_ok=True)

st1 = render_realistic_heart("ruby")
c1 = make_animated_heart_webp(st1, os.path.join(pack_dir, "1.webp"), "RUBI DA PAIXÃO 💎❤️")
make_tray(c1, os.path.join(pack_dir, "tray_icon.png"))
print("Generated 1.webp (Ruby Heart)")

st2 = render_realistic_heart("diamond")
make_animated_heart_webp(st2, os.path.join(pack_dir, "2.webp"), "DIAMANTE DE OURO ✨")
print("Generated 2.webp (Diamond Heart)")

st3 = render_realistic_heart("fire")
make_animated_heart_webp(st3, os.path.join(pack_dir, "3.webp"), "FOGO DA PAIXÃO 🔥")
print("Generated 3.webp (Fire Heart)")

st4 = render_realistic_heart("neon")
make_animated_heart_webp(st4, os.path.join(pack_dir, "4.webp"), "NEON CYBERPUNK ⚡")
print("Generated 4.webp (Neon Heart)")

st5 = render_realistic_heart("rose")
make_animated_heart_webp(st5, os.path.join(pack_dir, "5.webp"), "ROSA NO CORAÇÃO 🌹")
print("Generated 5.webp (Rose Heart)")

st6 = render_realistic_heart("galaxy")
make_animated_heart_webp(st6, os.path.join(pack_dir, "6.webp"), "GALÁXIA DE AMOR 🌌")
print("Generated 6.webp (Galaxy Heart)")

st7 = render_realistic_heart("water")
make_animated_heart_webp(st7, os.path.join(pack_dir, "7.webp"), "GOTA DE CRISTAL 💧")
print("Generated 7.webp (Water Heart)")

st8 = render_realistic_heart("cupid")
make_animated_heart_webp(st8, os.path.join(pack_dir, "8.webp"), "FLECHA DO CUPIDO 💘")
print("Generated 8.webp (Cupid Heart)")

print("All 8 stickers for br-coracao-paixao successfully generated!")
