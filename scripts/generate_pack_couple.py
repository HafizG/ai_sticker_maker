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

def render_realistic_couple_scene(scene_type):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    if scene_type == "acai":
        # Couple sharing açaí bowl
        d.ellipse([240, 360, 500, 880], fill="#3B82F6") # Boy
        d.ellipse([524, 360, 784, 880], fill="#EC4899") # Girl
        d.ellipse([320, 200, 480, 400], fill="#FED7AA")
        d.ellipse([544, 200, 704, 400], fill="#FDE68A")
        # Purple açaí bowl in center
        d.ellipse([380, 600, 644, 840], fill="#581C87", outline="#7E22CE", width=10)
        d.ellipse([420, 640, 470, 690], fill="#EF4444") # Strawberry slice
        d.ellipse([550, 640, 600, 690], fill="#FBBF24") # Banana slice
    elif scene_type == "bike":
        # Tandem bicycle
        d.ellipse([260, 340, 480, 800], fill="#2563EB")
        d.ellipse([480, 340, 700, 800], fill="#F43F5E")
        d.ellipse([320, 180, 460, 360], fill="#FED7AA")
        d.ellipse([500, 180, 640, 360], fill="#FDE68A")
        # Bicycle wheels
        d.ellipse([180, 680, 420, 920], outline="#475569", width=14)
        d.ellipse([604, 680, 844, 920], outline="#475569", width=14)
    elif scene_type == "stars":
        # Stargazing on green hill
        d.chord([120, 640, 904, 1200], 180, 360, fill="#15803D")
        d.ellipse([320, 440, 520, 720], fill="#1E3A8A")
        d.ellipse([504, 440, 704, 720], fill="#BE185D")
        d.ellipse([360, 300, 480, 450], fill="#FED7AA")
        d.ellipse([544, 300, 664, 450], fill="#FDE68A")
        # Golden stars in sky
        for sx, sy in [(240, 180), (512, 120), (780, 200), (380, 100), (660, 140)]:
            d.polygon([(sx, sy-25), (sx+8, sy-8), (sx+25, sy), (sx+8, sy+8), (sx, sy+25), (sx-8, sy+8), (sx-25, sy), (sx-8, sy-8)], fill="#FDE047")
    elif scene_type == "cooking":
        # Cooking together with chef hats
        d.ellipse([260, 400, 520, 880], fill="#0284C7")
        d.ellipse([504, 400, 764, 880], fill="#E11D48")
        d.ellipse([340, 240, 480, 420], fill="#FED7AA")
        d.ellipse([544, 240, 684, 420], fill="#FDE68A")
        # Chef hats
        d.ellipse([330, 160, 490, 260], fill="white", outline="#94A3B8", width=4)
        d.ellipse([534, 160, 694, 260], fill="white", outline="#94A3B8", width=4)
        # Cake bowl
        d.ellipse([420, 640, 604, 820], fill="#78350F", outline="#D97706", width=8)
    elif scene_type == "dance":
        # Dancing in living room
        d.ellipse([280, 360, 540, 920], fill="#1E293B")
        d.ellipse([480, 360, 740, 920], fill="#F59E0B")
        d.ellipse([360, 200, 500, 380], fill="#FED7AA")
        d.ellipse([500, 200, 640, 380], fill="#FDE68A")
        # Music notes
        d.ellipse([760, 220, 800, 260], fill="#EC4899")
        d.line([(800, 240), (800, 160)], fill="#EC4899", width=8)
    elif scene_type == "piggyback":
        # Beach piggyback ride
        d.ellipse([340, 400, 684, 960], fill="#059669") # Boy
        d.ellipse([420, 240, 580, 430], fill="#FED7AA")
        d.ellipse([380, 280, 644, 600], fill="#F43F5E") # Girl on back
        d.ellipse([480, 140, 620, 310], fill="#FDE68A")
    elif scene_type == "bed":
        # Morning coffee in bed
        d.rounded_rectangle([200, 540, 824, 920], radius=50, fill="#FEF08A", outline="#CA8A04", width=8)
        d.ellipse([320, 360, 480, 560], fill="#FED7AA")
        d.ellipse([544, 360, 704, 560], fill="#FDE68A")
        d.rectangle([460, 680, 564, 780], fill="#78350F") # Steaming coffee
    else: # umbrella
        # Couple walking under cozy umbrella
        d.pieslice([240, 100, 784, 440], 180, 360, fill="#DB2777")
        d.line([(512, 100), (512, 500)], fill="#334155", width=10)
        d.ellipse([300, 440, 530, 920], fill="#334155")
        d.ellipse([490, 440, 720, 920], fill="#93C5FD")
        d.ellipse([360, 280, 500, 450], fill="#FED7AA")
        d.ellipse([500, 280, 640, 450], fill="#FDE68A")
        
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

def make_animated_couple_webp(pil_img, out_path, banner_text):
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

# ── Build Pack: br-casal-fofo ──
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-casal-fofo')
os.makedirs(pack_dir, exist_ok=True)

st1 = render_realistic_couple_scene("acai")
c1 = make_animated_couple_webp(st1, os.path.join(pack_dir, "1.webp"), "DIVIDINDO AÇAÍ 🥣❤️")
make_tray(c1, os.path.join(pack_dir, "tray_icon.png"))
print("Generated 1.webp (Açaí Bowl)")

st2 = render_realistic_couple_scene("bike")
make_animated_couple_webp(st2, os.path.join(pack_dir, "2.webp"), "BICICLETA A DOIS 🚲")
print("Generated 2.webp (Tandem Bike)")

st3 = render_realistic_couple_scene("stars")
make_animated_couple_webp(st3, os.path.join(pack_dir, "3.webp"), "OLHANDO AS ESTRELAS 🌌")
print("Generated 3.webp (Stargazing)")

st4 = render_realistic_couple_scene("cooking")
make_animated_couple_webp(st4, os.path.join(pack_dir, "4.webp"), "FAZENDO BOLO JUNTOS 🎂")
print("Generated 4.webp (Cooking Cake)")

st5 = render_realistic_couple_scene("dance")
make_animated_couple_webp(st5, os.path.join(pack_dir, "5.webp"), "DANÇANDO JUNTINHOS 🎵")
print("Generated 5.webp (Living Room Dance)")

st6 = render_realistic_couple_scene("piggyback")
make_animated_couple_webp(st6, os.path.join(pack_dir, "6.webp"), "PIGGYBACK NA PRAIA 🏖️")
print("Generated 6.webp (Piggyback)")

st7 = render_realistic_couple_scene("bed")
make_animated_couple_webp(st7, os.path.join(pack_dir, "7.webp"), "CAFÉ NA CAMA ☕🥰")
print("Generated 7.webp (Breakfast in Bed)")

st8 = render_realistic_couple_scene("umbrella")
make_animated_couple_webp(st8, os.path.join(pack_dir, "8.webp"), "PASSEIO NA CHUVA ☔")
print("Generated 8.webp (Umbrella Walk)")

print("All 8 stickers for br-casal-fofo successfully generated!")
