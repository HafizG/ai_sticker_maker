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

def render_3d_heart_surface(htype):
    size = 1024
    x = np.linspace(-1.4, 1.4, size)
    y = np.linspace(1.4, -1.4, size)
    xx, yy = np.meshgrid(x, y)
    
    # Mathematical 3D Heart implicit manifold
    # (x^2 + (y - sqrt(|x|))^2) <= 1.0
    xx_h = xx * 1.15
    yy_h = (yy + 0.25) * 1.15
    
    dist_sq = xx_h**2 + (yy_h - np.sqrt(np.maximum(0, np.abs(xx_h))))**2
    inside = dist_sq <= 1.0
    
    # 3D Depth z(x,y)
    z = np.zeros_like(xx)
    z[inside] = np.sqrt(np.maximum(0, 1.0 - dist_sq[inside]))
    
    # Calculate 3D surface normals
    dz_dy, dz_dx = np.gradient(z)
    norm = np.sqrt(dz_dx**2 + dz_dy**2 + 1.0)
    nx = -dz_dx / norm
    ny = -dz_dy / norm
    nz = 1.0 / norm
    
    # Key light: upper left
    lx1, ly1, lz1 = -0.5, 0.6, 0.6
    diffuse1 = np.maximum(0, nx * lx1 + ny * ly1 + nz * lz1)
    
    # Specular (Blinn-Phong)
    vx, vy, vz = 0, 0, 1.0
    hx1, hy1, hz1 = lx1 + vx, ly1 + vy, lz1 + vz
    h1_len = np.sqrt(hx1**2 + hy1**2 + hz1**2)
    hx1, hy1, hz1 = hx1/h1_len, hy1/h1_len, hz1/h1_len
    specular1 = np.maximum(0, nx * hx1 + ny * hy1 + nz * hz1) ** 40
    
    # Rim light / Fresnel
    fresnel = ((1.0 - nz) ** 2.5) * np.maximum(0, nx * 0.5 - ny * 0.5 + nz * 0.5)
    
    if htype == "ruby":
        r = np.clip((diffuse1 * 200 + specular1 * 255 + fresnel * 180 + 50) * inside, 0, 255)
        g = np.clip((diffuse1 * 20 + specular1 * 240 + fresnel * 30 + 5) * inside, 0, 255)
        b = np.clip((diffuse1 * 40 + specular1 * 255 + fresnel * 60 + 10) * inside, 0, 255)
    elif htype == "gold":
        r = np.clip((diffuse1 * 230 + specular1 * 255 + fresnel * 255 + 70) * inside, 0, 255)
        g = np.clip((diffuse1 * 170 + specular1 * 255 + fresnel * 200 + 40) * inside, 0, 255)
        b = np.clip((diffuse1 * 20 + specular1 * 200 + fresnel * 50 + 5) * inside, 0, 255)
    elif htype == "fire":
        noise = (np.sin(xx*12) * np.cos(yy*12) + 1.0) * 0.5
        r = np.clip((diffuse1 * 240 + specular1 * 255 + noise * 100 + 80) * inside, 0, 255)
        g = np.clip((diffuse1 * 80 + specular1 * 220 + noise * 160 + 20) * inside, 0, 255)
        b = np.clip((specular1 * 180) * inside, 0, 255)
    elif htype == "neon":
        r = np.clip((diffuse1 * 30 + (1.0-nz)*255 + specular1 * 255) * inside, 0, 255)
        g = np.clip((diffuse1 * 10 + (1.0-nz)*50 + specular1 * 255) * inside, 0, 255)
        b = np.clip((diffuse1 * 40 + (1.0-nz)*220 + specular1 * 255) * inside, 0, 255)
    elif htype == "rose":
        r = np.clip((diffuse1 * 180 + specular1 * 255 + fresnel * 220 + 60) * inside, 0, 255)
        g = np.clip((diffuse1 * 30 + specular1 * 220 + fresnel * 100 + 10) * inside, 0, 255)
        b = np.clip((diffuse1 * 80 + specular1 * 255 + fresnel * 160 + 30) * inside, 0, 255)
    elif htype == "galaxy":
        r = np.clip((diffuse1 * 120 + np.sin(xx*6)*80 + specular1 * 255 + fresnel * 180 + 30) * inside, 0, 255)
        g = np.clip((diffuse1 * 40 + specular1 * 220 + fresnel * 80 + 10) * inside, 0, 255)
        b = np.clip((diffuse1 * 200 + np.cos(yy*6)*80 + specular1 * 255 + fresnel * 240 + 70) * inside, 0, 255)
    elif htype == "water":
        r = np.clip((diffuse1 * 20 + specular1 * 255 + fresnel * 180 + 10) * inside, 0, 255)
        g = np.clip((diffuse1 * 140 + specular1 * 255 + fresnel * 220 + 40) * inside, 0, 255)
        b = np.clip((diffuse1 * 240 + specular1 * 255 + fresnel * 255 + 90) * inside, 0, 255)
    elif htype == "cupid":
        r = np.clip((diffuse1 * 220 + specular1 * 255 + fresnel * 160 + 60) * inside, 0, 255)
        g = np.clip((diffuse1 * 30 + specular1 * 230 + fresnel * 40 + 10) * inside, 0, 255)
        b = np.clip((diffuse1 * 50 + specular1 * 255 + fresnel * 60 + 20) * inside, 0, 255)
    elif htype == "chocolate":
        r = np.clip((diffuse1 * 80 + specular1 * 180 + fresnel * 100 + 30) * inside, 0, 255)
        g = np.clip((diffuse1 * 45 + specular1 * 150 + fresnel * 60 + 15) * inside, 0, 255)
        b = np.clip((diffuse1 * 25 + specular1 * 100 + fresnel * 40 + 10) * inside, 0, 255)
    else: # holographic chrome
        hue = (xx*2 + yy*2 + nz*3) % (2*np.pi)
        r = np.clip((np.sin(hue)*120 + 135 + specular1*120) * inside, 0, 255)
        g = np.clip((np.sin(hue + 2.09)*120 + 135 + specular1*120) * inside, 0, 255)
        b = np.clip((np.sin(hue + 4.18)*120 + 135 + specular1*120) * inside, 0, 255)
        
    alpha = (inside * 255).astype(np.uint8)
    rgba = np.dstack([r.astype(np.uint8), g.astype(np.uint8), b.astype(np.uint8), alpha])
    
    img = Image.fromarray(rgba)
    
    # Extra 3D decorative details
    d = ImageDraw.Draw(img)
    if htype == "cupid":
        # 3D Golden Arrow through heart
        d.line([(120, 720), (904, 300)], fill="#F59E0B", width=24)
        d.polygon([(880, 260), (944, 280), (910, 344)], fill="#D97706")
        d.polygon([(120, 680), (80, 740), (140, 750)], fill="#D97706")
    elif htype == "chocolate":
        # Golden caramel drizzle
        d.arc([300, 360, 724, 600], 0, 180, fill="#F59E0B", width=14)
        d.arc([360, 440, 664, 680], 0, 180, fill="#F59E0B", width=12)
    elif htype == "gold" or htype == "ruby":
        # Diamond flares
        for sx, sy in [(340, 360), (680, 340), (512, 800)]:
            d.polygon([(sx, sy-35), (sx+8, sy-8), (sx+35, sy), (sx+8, sy+8), (sx, sy+35), (sx-8, sy+8), (sx-35, sy), (sx-8, sy-8)], fill="white")
            
    # Add clean die-cut sticker outline
    alpha_img = img.split()[3]
    outline = alpha_img.filter(ImageFilter.MaxFilter(25))
    
    sticker = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    white_fill = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    sticker.paste(white_fill, (0, 0), outline)
    sticker.paste(img, (0, 0), img)
    
    bbox = sticker.getbbox()
    if bbox:
        sticker = sticker.crop(bbox)
        
    return sticker

def make_animated_webp(pil_img, out_path, banner_text, stroke_color="#9F1239"):
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
        font = get_font(24)
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

# ── Build 10 Realistic 3D Hearts for br-coracao-paixao ──
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-coracao-paixao')
os.makedirs(pack_dir, exist_ok=True)

heart_configs = [
    ("RUBI 3D FACETADO 💎❤️", "ruby", "#9F1239"),
    ("DIAMANTE DE OURO 3D ✨", "gold", "#D97706"),
    ("FOGO DA PAIXÃO 3D 🔥", "fire", "#DC2626"),
    ("NEON CYBERPUNK 3D ⚡", "neon", "#0891B2"),
    ("ROSA DE CRISTAL 3D 🌹", "rose", "#BE123C"),
    ("GALÁXIA DE AMOR 3D 🌌", "galaxy", "#4338CA"),
    ("GOTA DE ÁGUA 3D 💧", "water", "#0284C7"),
    ("FLECHA DO CUPIDO 3D 💘", "cupid", "#E11D48"),
    ("CHOCOLATE TRUFADO 3D 🍫", "chocolate", "#78350F"),
    ("HOLOGRÁFICO 3D 🌈", "holo", "#7C3AED"),
]

for idx, (title, htype, sc) in enumerate(heart_configs, 1):
    stk = render_3d_heart_surface(htype)
    out_webp = os.path.join(pack_dir, f"{idx}.webp")
    f0 = make_animated_webp(stk, out_webp, title, sc)
    if idx == 1:
        make_tray(f0, os.path.join(pack_dir, "tray_icon.png"))
    print(f"Pack 5: Generated 3D Realistic Heart {idx}.webp")

print("\nPack 5 (br-coracao-paixao) updated with 10 3D realistic hearts successfully!")
