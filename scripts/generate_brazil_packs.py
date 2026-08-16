import os
import math
import random
from PIL import Image, ImageDraw, ImageFont

PACKS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', 'packs')

def get_font(size):
    font_paths = [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
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

def draw_brazil_flag(draw, box):
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    
    # Green background
    draw.rectangle([x0, y0, x1, y1], fill=(0, 156, 59, 255), outline=(0, 100, 35, 255), width=4)
    
    # Yellow rhombus
    rhombus = [
        (x0 + w * 0.5, y0 + h * 0.12),
        (x1 - w * 0.08, y0 + h * 0.5),
        (x0 + w * 0.5, y1 - h * 0.12),
        (x0 + w * 0.08, y0 + h * 0.5)
    ]
    draw.polygon(rhombus, fill=(255, 223, 0, 255))
    
    # Blue circle
    cr = min(w, h) * 0.22
    cx, cy = x0 + w * 0.5, y0 + h * 0.5
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(0, 39, 118, 255))
    
    # White arc banner across circle
    arc_box = [cx - cr * 1.05, cy - cr * 0.3, cx + cr * 1.05, cy + cr * 0.9]
    draw.arc(arc_box, start=190, end=350, fill="white", width=max(3, int(cr*0.14)))

def save_static(img, path):
    img.save(path, format="WEBP", lossless=True)

def save_animated(frames, path, duration=120):
    frames[0].save(
        path,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        lossless=False,
        quality=90
    )

def create_pack_folder(pack_id):
    p = os.path.join(PACKS_BASE_DIR, pack_id)
    os.makedirs(p, exist_ok=True)
    return p

# ── 1. br-bandeira-nacional (Static) ──
def generate_br_bandeira_nacional():
    pack_dir = create_pack_folder('br-bandeira-nacional')
    font_lg = get_font(46)
    font_md = get_font(36)
    font_sm = get_font(28)

    # 1. Classic waving badge
    im = Image.new('RGBA', (512, 512), (0,0,0,0))
    d = ImageDraw.Draw(im)
    draw_brazil_flag(d, (56, 96, 456, 376))
    draw_text_centered(d, "BRASIL", (256, 430), font_lg, fill="#FFDF00", stroke_fill="#002776", stroke_width=6)
    save_static(im, os.path.join(pack_dir, "1.webp"))
    im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")

    # 2. Heart flag
    im = Image.new('RGBA', (512, 512), (0,0,0,0))
    d = ImageDraw.Draw(im)
    d.polygon([(256, 460), (60, 240), (120, 100), (256, 180), (392, 100), (452, 240)], fill=(0, 156, 59, 255))
    d.pieslice([60, 100, 256, 280], 180, 0, fill=(0, 156, 59, 255))
    d.pieslice([256, 100, 452, 280], 180, 0, fill=(0, 156, 59, 255))
    d.polygon([(256, 170), (400, 260), (256, 390), (112, 260)], fill=(255, 223, 0, 255))
    d.ellipse([196, 200, 316, 320], fill=(0, 39, 118, 255))
    draw_text_centered(d, "ORGULHO", (256, 70), font_md, fill="#009C3B", stroke_fill="white", stroke_width=4)
    save_static(im, os.path.join(pack_dir, "2.webp"))

    # 3. Round Seal / Ordem e Progresso
    im = Image.new('RGBA', (512, 512), (0,0,0,0))
    d = ImageDraw.Draw(im)
    d.ellipse([40, 40, 472, 472], fill=(0, 156, 59, 255), outline=(255, 223, 0, 255), width=10)
    d.polygon([(256, 90), (430, 256), (256, 422), (82, 256)], fill=(255, 223, 0, 255))
    d.ellipse([156, 156, 356, 356], fill=(0, 39, 118, 255))
    d.arc([160, 200, 352, 330], start=190, end=350, fill="white", width=12)
    draw_text_centered(d, "ORDEM E PROGRESSO", (256, 256), get_font(18), fill="white", stroke_fill="#002776", stroke_width=2)
    save_static(im, os.path.join(pack_dir, "3.webp"))

    # 4. Map Silhouette with Flag
    im = Image.new('RGBA', (512, 512), (0,0,0,0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([70, 70, 442, 390], radius=30, fill=(0, 156, 59, 255), outline="white", width=6)
    draw_brazil_flag(d, (100, 110, 412, 340))
    draw_text_centered(d, "PÁTRIA AMADA", (256, 440), font_lg, fill="#009C3B", stroke_fill="#FFDF00", stroke_width=5)
    save_static(im, os.path.join(pack_dir, "4.webp"))

    # 5. 100% Brasileiro
    im = Image.new('RGBA', (512, 512), (0,0,0,0))
    d = ImageDraw.Draw(im)
    d.rectangle([50, 140, 462, 370], fill=(255, 223, 0, 255), outline=(0, 156, 59, 255), width=8)
    draw_text_centered(d, "100%", (256, 210), get_font(60), fill="#002776", stroke_fill="white", stroke_width=6)
    draw_text_centered(d, "BRASILEIRO", (256, 300), font_lg, fill="#009C3B", stroke_fill="white", stroke_width=5)
    save_static(im, os.path.join(pack_dir, "5.webp"))

    # 6. É do Brasil
    im = Image.new('RGBA', (512, 512), (0,0,0,0))
    d = ImageDraw.Draw(im)
    d.ellipse([50, 80, 462, 432], fill=(0, 39, 118, 255), outline=(255, 223, 0, 255), width=8)
    draw_text_centered(d, "É DO", (256, 180), font_lg, fill="#FFDF00", stroke_fill="#009C3B", stroke_width=5)
    draw_text_centered(d, "BRASIL! 🇧🇷", (256, 280), get_font(52), fill="white", stroke_fill="#009C3B", stroke_width=5)
    save_static(im, os.path.join(pack_dir, "6.webp"))

    # 7. Green & Yellow Ribbon
    im = Image.new('RGBA', (512, 512), (0,0,0,0))
    d = ImageDraw.Draw(im)
    d.polygon([(60, 200), (256, 90), (452, 200), (390, 370), (256, 440), (122, 370)], fill=(0, 156, 59, 255), outline=(255, 223, 0, 255), width=6)
    d.ellipse([176, 180, 336, 340], fill=(255, 223, 0, 255))
    d.ellipse([206, 210, 306, 310], fill=(0, 39, 118, 255))
    draw_text_centered(d, "VAI BRASIL", (256, 260), font_sm, fill="white", stroke_fill="#002776", stroke_width=3)
    save_static(im, os.path.join(pack_dir, "7.webp"))

    # 8. Brazilian Shield Badge
    im = Image.new('RGBA', (512, 512), (0,0,0,0))
    d = ImageDraw.Draw(im)
    d.polygon([(256, 50), (440, 130), (390, 370), (256, 470), (122, 370), (72, 130)], fill=(0, 156, 59, 255), outline=(255, 223, 0, 255), width=8)
    draw_brazil_flag(d, (136, 160, 376, 330))
    draw_text_centered(d, "CAMPEÃO", (256, 410), font_md, fill="#FFDF00", stroke_fill="#002776", stroke_width=4)
    save_static(im, os.path.join(pack_dir, "8.webp"))


# ── 2. br-bandeira-animada (Animated) ──
def generate_br_bandeira_animada():
    pack_dir = create_pack_folder('br-bandeira-animada')
    font_lg = get_font(44)
    font_md = get_font(34)

    for st_idx in range(1, 9):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            if st_idx == 1:
                wave_offset = int(math.sin(phase) * 16)
                y_shift = int(math.cos(phase) * 10)
                draw_brazil_flag(d, (56, 110 + wave_offset, 456, 360 + wave_offset))
                draw_text_centered(d, "BRASIL!", (256, 420 + y_shift), font_lg, fill="#FFDF00", stroke_fill="#002776", stroke_width=6)
            elif st_idx == 2:
                scale = 1.0 + 0.12 * math.sin(phase)
                cx, cy = 256, 240
                r = int(140 * scale)
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 156, 59, 255), outline="#FFDF00", width=8)
                d.polygon([(cx, cy - r + 30), (cx + r - 30, cy), (cx, cy + r - 30), (cx - r + 30, cy)], fill=(255, 223, 0, 255))
                d.ellipse([cx - int(r*0.45), cy - int(r*0.45), cx + int(r*0.45), cy + int(r*0.45)], fill=(0, 39, 118, 255))
                draw_text_centered(d, "MEU BRASIL", (256, 430), font_md, fill="#009C3B", stroke_fill="white", stroke_width=4)
            elif st_idx == 3:
                draw_brazil_flag(d, (60, 100, 452, 350))
                star_size = int(15 + 10 * math.sin(phase + st_idx))
                for sx, sy in [(100, 80), (410, 90), (256, 50), (120, 380), (390, 370)]:
                    d.ellipse([sx - star_size, sy - star_size, sx + star_size, sy + star_size], fill="#FFDF00")
                draw_text_centered(d, "VIVA O BRASIL!", (256, 430), font_md, fill="#002776", stroke_fill="white", stroke_width=5)
            elif st_idx == 4:
                bounce = int(abs(math.sin(phase)) * 30)
                d.ellipse([140, 150 - bounce, 372, 382 - bounce], fill=(255, 223, 0, 255), outline=(0, 156, 59, 255), width=10)
                d.ellipse([200, 220 - bounce, 230, 260 - bounce], fill="black")
                d.ellipse([282, 220 - bounce, 312, 260 - bounce], fill="black")
                d.arc([200, 240 - bounce, 312, 330 - bounce], 20, 160, fill="black", width=6)
                draw_text_centered(d, "BRASILEIRÍSSIMO", (256, 430), font_md, fill="#009C3B", stroke_fill="white", stroke_width=4)
            elif st_idx == 5:
                rot = phase
                d.ellipse([80, 80, 432, 432], fill=(0, 39, 118, 255), outline=(0, 156, 59, 255), width=12)
                d.polygon([(256 + int(math.cos(rot)*140), 256 + int(math.sin(rot)*140)),
                           (256 + int(math.cos(rot+math.pi/2)*140), 256 + int(math.sin(rot+math.pi/2)*140)),
                           (256 + int(math.cos(rot+math.pi)*140), 256 + int(math.sin(rot+math.pi)*140)),
                           (256 + int(math.cos(rot+3*math.pi/2)*140), 256 + int(math.sin(rot+3*math.pi/2)*140))],
                          fill=(255, 223, 0, 255))
                draw_text_centered(d, "GIGANTE PELA NATUREZA", (256, 470), get_font(20), fill="#009C3B", stroke_fill="white", stroke_width=3)
            elif st_idx == 6:
                draw_brazil_flag(d, (90, 140, 422, 340))
                for ci in range(12):
                    cx = (ci * 40 + int(f * 25)) % 480 + 16
                    cy = (ci * 35 + int(f * 30)) % 400 + 40
                    color = "#FFDF00" if ci % 2 == 0 else "#009C3B"
                    d.rectangle([cx, cy, cx + 12, cy + 12], fill=color)
                draw_text_centered(d, "ALEGRIA PURA!", (256, 420), font_lg, fill="#009C3B", stroke_fill="#FFDF00", stroke_width=5)
            elif st_idx == 7:
                glow = int(20 * math.sin(phase))
                d.polygon([(160, 120), (352, 120), (320, 280), (280, 340), (280, 400), (340, 420), (172, 420), (232, 400), (232, 340), (192, 280)], fill="#FFD700", outline="#B8860B", width=6)
                d.ellipse([120 - glow, 150, 180, 230], outline="#FFD700", width=8)
                d.ellipse([332, 150, 392 + glow, 230], outline="#FFD700", width=8)
                draw_text_centered(d, "RUMO AO HEXA! ⭐", (256, 80), font_md, fill="#009C3B", stroke_fill="#FFDF00", stroke_width=4)
            else:
                wave = int(math.sin(phase) * 20)
                d.rounded_rectangle([70, 120 + wave, 442, 360 + wave], radius=25, fill=(0, 156, 59, 255), outline="#FFDF00", width=8)
                draw_text_centered(d, "ORGULHO 🇧🇷", (256, 240 + wave), font_lg, fill="white", stroke_fill="#002776", stroke_width=6)
                draw_text_centered(d, "VERDE E AMARELO", (256, 430), font_md, fill="#009C3B", stroke_fill="white", stroke_width=4)

            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 3. br-bolsonaro-dancando (Animated) ──
def generate_br_bolsonaro_dancando():
    pack_dir = create_pack_folder('br-bolsonaro-dancando')
    font_md = get_font(32)

    titles = [
        ("DANÇA DO CAPITÃO", "🕺"),
        ("É A CLOROQUINA!", "💊"),
        ("TÁ COM MEDO?", "😎"),
        ("VALEU, MEU BRASIL!", "🇧🇷"),
        ("VAI DAR BOM!", "👍"),
        ("GRITA MAIS ALTO!", "📢"),
        ("MITOU DEMAIS!", "🔥"),
        ("FORÇA & HONRA!", "⚡")
    ]

    for st_idx, (title, emoji) in enumerate(titles, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            arm_swing = int(math.sin(phase) * 35)
            bounce = int(abs(math.sin(phase)) * 20)
            hip_sway = int(math.cos(phase) * 18)
            
            d.ellipse([60, 60, 452, 452], fill=(230, 245, 230, 240), outline=(0, 156, 59, 255), width=6)
            
            leg_l = 380 - bounce
            leg_r = 380 - bounce + int(math.sin(phase)*15)
            d.line([(220 + hip_sway, 300 - bounce), (200 + hip_sway, leg_l)], fill="#1E293B", width=16)
            d.line([(292 + hip_sway, 300 - bounce), (312 + hip_sway, leg_r)], fill="#1E293B", width=16)
            
            d.polygon([
                (190 + hip_sway, 180 - bounce),
                (322 + hip_sway, 180 - bounce),
                (332 + hip_sway, 310 - bounce),
                (180 + hip_sway, 310 - bounce)
            ], fill="#1A365D")
            d.polygon([(240 + hip_sway, 180 - bounce), (272 + hip_sway, 180 - bounce), (260 + hip_sway, 210 - bounce), (252 + hip_sway, 210 - bounce)], fill="white")
            d.polygon([(252 + hip_sway, 205 - bounce), (260 + hip_sway, 205 - bounce), (266 + hip_sway, 290 - bounce), (256 + hip_sway, 300 - bounce), (246 + hip_sway, 290 - bounce)], fill="#FFDF00")

            head_x = 256 + hip_sway
            head_y = 135 - bounce
            d.ellipse([head_x - 45, head_y - 50, head_x + 45, head_y + 45], fill="#FFD1A4")
            d.arc([head_x - 48, head_y - 55, head_x + 48, head_y + 10], 170, 370, fill="#718096", width=14)
            if st_idx in (2, 3, 7):
                d.rectangle([head_x - 38, head_y - 12, head_x - 6, head_y + 10], fill="black")
                d.rectangle([head_x + 6, head_y - 12, head_x + 38, head_y + 10], fill="black")
                d.line([(head_x - 6, head_y - 2), (head_x + 6, head_y - 2)], fill="black", width=4)
            else:
                d.ellipse([head_x - 26, head_y - 10, head_x - 12, head_y + 4], fill="#4A5568")
                d.ellipse([head_x + 12, head_y - 10, head_x + 26, head_y + 4], fill="#4A5568")
            d.arc([head_x - 22, head_y + 5, head_x + 22, head_y + 28], 20, 160, fill="#9B2C2C", width=5)

            d.line([(192 + hip_sway, 195 - bounce), (315 + hip_sway, 305 - bounce)], fill="#009C3B", width=12)
            d.line([(195 + hip_sway, 198 - bounce), (318 + hip_sway, 308 - bounce)], fill="#FFDF00", width=6)

            if st_idx in (4, 5):
                d.line([(190 + hip_sway, 200 - bounce), (130, 160 - arm_swing)], fill="#1A365D", width=14)
                d.line([(322 + hip_sway, 200 - bounce), (382, 160 + arm_swing)], fill="#1A365D", width=14)
                d.ellipse([115, 145 - arm_swing, 140, 170 - arm_swing], fill="#FFD1A4")
                d.ellipse([370, 145 + arm_swing, 395, 170 + arm_swing], fill="#FFD1A4")
            else:
                d.line([(190 + hip_sway, 200 - bounce), (120, 240 + arm_swing)], fill="#1A365D", width=14)
                d.line([(322 + hip_sway, 200 - bounce), (390, 160 - arm_swing)], fill="#1A365D", width=14)
                d.ellipse([105, 230 + arm_swing, 130, 255 + arm_swing], fill="#FFD1A4")
                d.ellipse([380, 145 - arm_swing, 405, 170 - arm_swing], fill="#FFD1A4")

            draw_text_centered(d, f"{title} {emoji}", (256, 440), font_md, fill="#009C3B", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 4. br-beijo-apaixonado (Animated) ──
def generate_br_beijo_apaixonado():
    pack_dir = create_pack_folder('br-beijo-apaixonado')
    font_md = get_font(34)

    phrases = [
        "UM BEIJO MEU AMOR 💋",
        "BEIJO GOSTOSO 😘",
        "MIL BEIJINHOS 💕",
        "TE QUERO TANTO! ❤️",
        "BEIJO NA BOCA 👄",
        "VOU TE ENCHER DE BEIJO 🥰",
        "BEIJÃO PRA VOCÊ 💖",
        "ME DÁ UM BEIJO? 😍"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            scale = 1.0 + 0.15 * math.sin(phase)
            lip_w = int(160 * scale)
            lip_h = int(90 * scale)
            cx, cy = 256, 230
            
            for hi in range(5):
                h_phase = phase + hi * 1.2
                hx = int(cx + math.sin(h_phase) * (80 + hi * 30))
                hy = int(cy - (f * 15 + hi * 35) % 180 - 40)
                hs = int(16 + 8 * math.sin(h_phase))
                d.ellipse([hx - hs, hy - hs, hx + hs, hy + hs], fill=(255, 60, 120, 220))

            top_lip = [
                (cx - lip_w, cy),
                (cx - lip_w*0.5, cy - lip_h),
                (cx, cy - int(lip_h*0.4)),
                (cx + lip_w*0.5, cy - lip_h),
                (cx + lip_w, cy),
                (cx, cy - int(lip_h*0.1))
            ]
            bot_lip = [
                (cx - lip_w, cy),
                (cx - lip_w*0.4, cy + lip_h),
                (cx + lip_w*0.4, cy + lip_h),
                (cx + lip_w, cy),
                (cx, cy + int(lip_h*0.2))
            ]
            d.polygon(top_lip, fill=(235, 30, 85, 255))
            d.polygon(bot_lip, fill=(210, 20, 70, 255))
            d.ellipse([cx - int(lip_w*0.3), cy + int(lip_h*0.3), cx - int(lip_w*0.1), cy + int(lip_h*0.6)], fill=(255, 180, 200, 230))
            
            draw_text_centered(d, phrase, (256, 430), font_md, fill="#E11D48", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 5. br-abraco-carinhoso (Animated) ──
def generate_br_abraco_carinhoso():
    pack_dir = create_pack_folder('br-abraco-carinhoso')
    font_md = get_font(34)

    phrases = [
        "ABRAÇO APERTADO 🤗",
        "VEM CÁ ME ABRAÇAR 🥰",
        "SINTA MEU ABRAÇO 🫂",
        "CARINHO GOSTOSO ❤️",
        "ABRAÇO DE URSO 🐻",
        "TÔ COM SAUDADE 💕",
        "MEU COLO É SEU ✨",
        "ABRAÇO VIRTUAL 💌"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            squeeze = int(math.sin(phase) * 18)
            
            d.ellipse([140 + squeeze, 130, 270 + squeeze, 260], fill="#FBBF24")
            d.ellipse([120 + squeeze, 220, 280 + squeeze, 380], fill="#F59E0B")
            d.arc([175 + squeeze, 175, 205 + squeeze, 200], 180, 360, fill="#78350F", width=4)
            d.arc([220 + squeeze, 175, 250 + squeeze, 200], 180, 360, fill="#78350F", width=4)
            d.ellipse([160 + squeeze, 195, 185 + squeeze, 215], fill="#F87171")
            
            d.ellipse([240 - squeeze, 130, 370 - squeeze, 260], fill="#F472B6")
            d.ellipse([230 - squeeze, 220, 390 - squeeze, 380], fill="#EC4899")
            d.arc([260 - squeeze, 175, 290 - squeeze, 200], 180, 360, fill="#831843", width=4)
            d.arc([305 - squeeze, 175, 335 - squeeze, 200], 180, 360, fill="#831843", width=4)
            d.ellipse([325 - squeeze, 195, 350 - squeeze, 215], fill="#FDA4AF")

            d.line([(160 + squeeze, 260), (330 - squeeze, 280)], fill="#F59E0B", width=22)
            d.ellipse([315 - squeeze, 265, 345 - squeeze, 295], fill="#FBBF24")
            d.line([(350 - squeeze, 270), (180 + squeeze, 290)], fill="#EC4899", width=20)
            d.ellipse([165 + squeeze, 275, 195 + squeeze, 305], fill="#F472B6")

            hs = int(24 + 10 * math.sin(phase))
            d.ellipse([256 - hs, 90 - hs, 256 + hs, 90 + hs], fill="#EF4444")

            draw_text_centered(d, phrase, (256, 430), font_md, fill="#DB2777", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 6. br-figurinhas-hot (Animated) ──
def generate_br_figurinhas_hot():
    pack_dir = create_pack_folder('br-figurinhas-hot')
    font_md = get_font(34)

    phrases = [
        ("TÔ PEGANDO FOGO 🔥", "flame"),
        ("VOCÊ É UMA DELÍCIA 🤤", "peach"),
        ("QUERO VOCÊ AGORA 😏", "devil"),
        ("HOJE TEM... 😈", "wink"),
        ("CLIMA ESQUENTOU 🌶️", "pepper"),
        ("PROVOCAÇÃO PURA 💋", "lips"),
        ("QUERO SEU BEIJO 👅", "fire_heart"),
        ("VEM QUE EU TÔ FÁCIL 🔥", "flirt")
    ]

    for st_idx, (phrase, art_type) in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            flame_flicker = int(math.sin(phase) * 15)
            
            if art_type in ("flame", "flirt"):
                d.polygon([
                    (256, 90 + flame_flicker),
                    (330 + flame_flicker, 210),
                    (380, 320),
                    (310, 390),
                    (200, 390),
                    (130, 320),
                    (180 - flame_flicker, 210)
                ], fill="#EA580C")
                d.polygon([
                    (256, 170 + flame_flicker),
                    (300, 260),
                    (330, 340),
                    (256, 370),
                    (180, 340),
                    (210, 260)
                ], fill="#FACC15")
            elif art_type == "peach":
                d.ellipse([140, 160, 290, 350], fill="#FB923C")
                d.ellipse([220, 160, 370, 350], fill="#F97316")
                d.line([(256, 170), (256, 340)], fill="#C2410C", width=5)
                d.polygon([(256, 160), (280, 110), (240, 130)], fill="#22C55E")
            elif art_type == "pepper":
                d.polygon([(256, 120), (320, 220), (340, 320), (280, 370), (210, 340), (200, 220)], fill="#DC2626")
                d.rectangle([248, 90, 264, 125], fill="#15803D")
            else:
                d.ellipse([136, 130, 376, 370], fill="#9333EA")
                d.polygon([(160, 160), (120, 80 + flame_flicker), (200, 140)], fill="#7E22CE")
                d.polygon([(352, 160), (392, 80 + flame_flicker), (312, 140)], fill="#7E22CE")
                d.polygon([(190, 220), (230, 240), (190, 245)], fill="white")
                d.polygon([(322, 220), (282, 240), (322, 245)], fill="white")
                d.ellipse([200, 230, 218, 245], fill="black")
                d.ellipse([294, 230, 312, 245], fill="black")
                d.arc([210, 270, 302, 330], 20, 160, fill="black", width=6)

            draw_text_centered(d, phrase, (256, 435), font_md, fill="#EA580C", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 7. br-futebol-selecao (Static) ──
def generate_br_futebol_selecao():
    pack_dir = create_pack_folder('br-futebol-selecao')
    font_lg = get_font(44)
    font_sm = get_font(26)

    stickers_data = [
        ("SELEÇÃO BRASILEIRA 🇧🇷", "Amarelinha 10"),
        ("É GIGANTE O BRASIL!", "Canarinho"),
        ("VINI JR NA PONTA! ⚡", "Drible"),
        ("CAMISA 10 É DO BRASIL", "Jersey"),
        ("VAI PRA CIMA DELES!", "Trophy"),
        ("HEXA É NOSSO! ⭐⭐⭐⭐⭐⭐", "Stars"),
        ("TORCIDA MAIS APAIXONADA", "Cheer"),
        ("O PAÍS DO FUTEBOL ⚽", "Football")
    ]

    for st_idx, (title, sub) in enumerate(stickers_data, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        
        d.ellipse([80, 80, 432, 432], fill=(255, 223, 0, 255), outline=(0, 156, 59, 255), width=10)
        d.ellipse([156, 140, 356, 340], fill="white", outline="black", width=5)
        d.polygon([(256, 210), (286, 235), (274, 270), (238, 270), (226, 235)], fill="black")
        d.line([(256, 210), (256, 160)], fill="black", width=4)
        d.line([(286, 235), (330, 215)], fill="black", width=4)
        d.line([(274, 270), (310, 315)], fill="black", width=4)
        d.line([(238, 270), (202, 315)], fill="black", width=4)
        d.line([(226, 235), (182, 215)], fill="black", width=4)
        
        for star_x in [160, 200, 240, 280, 320, 360]:
            d.ellipse([star_x - 8, 100, star_x + 8, 116], fill="#009C3B")

        draw_text_centered(d, title, (256, 400), font_sm, fill="#002776", stroke_fill="white", stroke_width=4)
        draw_text_centered(d, "BRASIL", (256, 50), font_lg, fill="#009C3B", stroke_fill="#FFDF00", stroke_width=6)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 8. br-futebol-gols-animados (Animated) ──
def generate_br_futebol_gols_animados():
    pack_dir = create_pack_folder('br-futebol-gols-animados')
    font_lg = get_font(52)
    font_md = get_font(34)

    phrases = [
        "GOOOOOOL DO BRASIL! ⚽",
        "QUE GOLAÇO DE PLACA! 🔥",
        "CHAPELOU O ADVERSÁRIO! 🎩",
        "CANETA DESCONCERTANTE! 🪄",
        "DEFESAÇA HISTÓRICA! 🧤",
        "NA GAVETA ONDE A CORUJA DORME! 🦉",
        "É CAMPEÃO DO MUNDO! 🏆",
        "SAMBA NO PÉ & BOLA NA REDE! 🇧🇷"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            ball_x = int(140 + f * 45)
            ball_y = int(280 - math.sin(phase) * 50)
            
            d.rectangle([340, 120, 480, 360], outline="white", width=8)
            for gy in range(140, 360, 25):
                d.line([(340, gy), (480, gy)], fill=(200, 200, 200, 180), width=2)
            for gx in range(360, 480, 25):
                d.line([(gx, 120), (gx, 360)], fill=(200, 200, 200, 180), width=2)

            d.ellipse([ball_x - 35, ball_y - 35, ball_x + 35, ball_y + 35], fill="white", outline="black", width=4)
            d.polygon([(ball_x, ball_y - 12), (ball_x + 12, ball_y), (ball_x + 8, ball_y + 14), (ball_x - 8, ball_y + 14), (ball_x - 12, ball_y)], fill="black")

            d.line([(ball_x - 45, ball_y), (ball_x - 120, ball_y)], fill="#FFDF00", width=6)
            d.line([(ball_x - 40, ball_y - 15), (ball_x - 100, ball_y - 25)], fill="#009C3B", width=4)
            d.line([(ball_x - 40, ball_y + 15), (ball_x - 100, ball_y + 25)], fill="#009C3B", width=4)

            draw_text_centered(d, "G O L !", (256, 80), font_lg, fill="#009C3B", stroke_fill="#FFDF00", stroke_width=7)
            draw_text_centered(d, phrase, (256, 430), font_md, fill="#002776", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 9. br-memes-classicos (Static) ──
def generate_br_memes_classicos():
    pack_dir = create_pack_folder('br-memes-classicos')
    font_sm = get_font(26)

    memes = [
        ("NAZARÉ CONFUSA 📐", ["f(x) = ?", "cos(θ)", "√2 + π = 42"], "#F59E0B"),
        ("RINDO DE NERVOSO 😬", ["Kkkkkry", "Tudo sob controle (sqn)"], "#EF4444"),
        ("É SOBRE ISSO E TÁ TUDO BEM ✨", ["Paz interior", "Respira e não pira"], "#10B981"),
        ("TÔ PASSAGEIRA HOJE 💅", ["Sem paciência", "Plena"], "#EC4899"),
        ("CHOCADA EM CRISTO 😱", ["Passada", "Chocada"], "#8B5CF6"),
        ("AGORA PRONTO! 🙄", ["Lá vem história", "Era só o que faltava"], "#64748B"),
        ("OLHA ELE AÍ 🤡", ["O palhaço chegou", "Mico do ano"], "#F97316"),
        ("TÁ BOM, CLÁUDIA! 😴", ["Senta lá", "Aham, sei..."], "#06B6D4")
    ]

    for st_idx, (title, math_texts, color) in enumerate(memes, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        
        d.rounded_rectangle([40, 60, 472, 452], radius=25, fill="white", outline=color, width=8)
        
        d.ellipse([156, 120, 356, 320], fill=color)
        d.ellipse([190, 180, 220, 210], fill="white")
        d.ellipse([292, 180, 322, 210], fill="white")
        d.ellipse([200, 190, 215, 205], fill="black")
        d.ellipse([297, 190, 312, 205], fill="black")
        d.line([(210, 260), (302, 260)], fill="black", width=5)

        for idx, mt in enumerate(math_texts):
            my = 90 + idx * 30
            d.text((60, my), mt, font=font_sm, fill=color)

        draw_text_centered(d, title, (256, 400), font_sm, fill="black", stroke_fill="white", stroke_width=4)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 10. br-gretchen-rainha (Animated) ──
def generate_br_gretchen_rainha():
    pack_dir = create_pack_folder('br-gretchen-rainha')
    font_md = get_font(34)

    phrases = [
        "RAINHA DOS MEMES 👑",
        "DANÇA CONGA CONGA 💃",
        "DEBOCHE PURO 💅",
        "CHORANDO DE RIR 😂",
        "TOMANDO MEU CAFÉ ☕",
        "OLHAR 43 JULGADOR 👀",
        "PLENA E PODEROSA ✨",
        "BEIJINHO NO OMBRO 💋"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            hair_sway = int(math.sin(phase) * 18)
            dance_arm = int(math.cos(phase) * 30)
            
            d.ellipse([50, 50, 462, 462], fill=(255, 240, 245, 240), outline="#DB2777", width=6)
            d.ellipse([140 - hair_sway, 90, 372 + hair_sway, 310], fill="#1C1917")
            d.ellipse([186, 120, 326, 270], fill="#FCD34D")
            d.arc([205, 160, 245, 190], 180, 360, fill="black", width=5)
            d.arc([267, 160, 307, 190], 180, 360, fill="black", width=5)
            d.ellipse([226, 215, 286, 250], fill="#DC2626")
            
            d.polygon([(180, 270), (332, 270), (360, 380), (152, 380)], fill="#EC4899")
            d.line([(180, 280), (110, 220 + dance_arm)], fill="#FCD34D", width=14)
            d.line([(332, 280), (402, 220 - dance_arm)], fill="#FCD34D", width=14)

            d.polygon([(220, 80), (235, 110), (256, 75), (277, 110), (292, 80), (285, 120), (227, 120)], fill="#FBBF24")

            draw_text_centered(d, phrase, (256, 430), font_md, fill="#BE185D", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 11. br-flork-debochado (Static) ──
def generate_br_flork_debochado():
    pack_dir = create_pack_folder('br-flork-debochado')
    font_md = get_font(32)

    flork_quotes = [
        ("EU AVISEI NÉ? 🥱", "coffee"),
        ("HÁJA PACIÊNCIA! 🧘", "zen"),
        ("DEUS ME LIVRE MAS QUEM ME DERA 🙈", "cake"),
        ("CANCELADO COM SUCESSO ❌", "stamp"),
        ("CAGUEI PRA SUA OPINIÃO 💩", "sunglasses"),
        ("SÓ RESPONDO COM MEU ADVOGADO ⚖️", "tie"),
        ("TÔ COM PREGUIÇA ATÉ DE VIVER 🛌", "pillow"),
        ("PARABÉNS PELO PAPEL DE TROUXA 🤡", "clown")
    ]

    for st_idx, (quote, prop) in enumerate(flork_quotes, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        
        d.rounded_rectangle([40, 40, 472, 472], radius=30, fill="white", outline="black", width=6)
        
        d.arc([160, 110, 352, 320], 150, 30, fill="black", width=6)
        d.line([(165, 230), (165, 360)], fill="black", width=6)
        d.line([(347, 230), (347, 360)], fill="black", width=6)
        
        d.ellipse([215, 175, 230, 190], fill="black")
        d.ellipse([282, 175, 297, 190], fill="black")
        d.line([(225, 220), (287, 220)], fill="black", width=5)

        d.line([(165, 270), (110, 240)], fill="black", width=5)
        d.line([(347, 270), (402, 240)], fill="black", width=5)
        
        if prop == "coffee":
            d.rectangle([390, 220, 430, 260], fill="#78350F", outline="black", width=3)
        elif prop == "cake":
            d.polygon([(390, 250), (430, 250), (410, 210)], fill="#EC4899", outline="black", width=3)
        elif prop == "clown":
            d.ellipse([245, 195, 267, 217], fill="#EF4444")

        draw_text_centered(d, quote, (256, 415), font_md, fill="black", stroke_fill="white", stroke_width=3)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 12. br-bom-dia-boa-noite (Static) ──
def generate_br_bom_dia_boa_noite():
    pack_dir = create_pack_folder('br-bom-dia-boa-noite')
    font_md = get_font(34)
    font_sm = get_font(26)

    greetings = [
        ("BOM DIA COM DEUS! ☕✨", "Que seu dia seja abençoado", "#F59E0B"),
        ("BOA TARDE COM CARINHO 🌸", "Uma tarde cheia de paz", "#EC4899"),
        ("BOA NOITE ABENÇOADA 🌙⭐", "Durma em paz, Deus cuida de tudo", "#3B82F6"),
        ("BOM DIA GRUPO! 🌻", "Muita saúde e alegria hoje", "#10B981"),
        ("PASSANDO PRA TE DESEJAR PAZ 🕊️", "Receba meu abraço fraterno", "#8B5CF6"),
        ("BOM DIA FAMÍLIA QUERIDA ❤️", "Um dia iluminado a todos", "#EF4444"),
        ("DOCE NOITE DE DESCANSO 🛌💤", "Sonhos lindos e revigorantes", "#6366F1"),
        ("GRATIDÃO POR MAIS UM DIA 🙏", "Obrigado Senhor por tudo", "#D97706")
    ]

    for st_idx, (title, subtitle, color) in enumerate(greetings, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        
        d.rounded_rectangle([40, 50, 472, 462], radius=30, fill=(255, 255, 255, 245), outline=color, width=8)
        
        if "NOITE" in title:
            d.ellipse([180, 110, 320, 250], fill="#FACC15")
            d.ellipse([215, 95, 340, 240], fill="white")
            for sx, sy in [(140, 120), (370, 140), (200, 260), (340, 250)]:
                d.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill="#FACC15")
        else:
            d.ellipse([196, 100, 316, 220], fill="#FBBF24")
            d.rounded_rectangle([206, 200, 306, 280], radius=10, fill="#78350F", outline="white", width=4)
            d.arc([286, 215, 336, 265], 270, 90, fill="#78350F", width=6)

        draw_text_centered(d, title, (256, 340), font_md, fill=color, stroke_fill="white", stroke_width=4)
        draw_text_centered(d, subtitle, (256, 400), font_sm, fill="#4B5563", stroke_fill="white", stroke_width=3)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 13. br-vira-lata-caramelo (Static) ──
def generate_br_vira_lata_caramelo():
    pack_dir = create_pack_folder('br-vira-lata-caramelo')
    font_md = get_font(34)

    phrases = [
        "PATRIMÔNIO NACIONAL 🐕",
        "CADÊ A COXINHA? 🍗",
        "AU AU CARAMELO! 🐾",
        "SOU LINDO DEMAIS 😎",
        "ME DÁ UM CARINHO? 🥺",
        "CUIDANDO DO PORTÃO 🚪",
        "CARA DE QUEM FEZ ARTE 🐶",
        "VIRA-LATA RAIZ 🇧🇷"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        
        d.ellipse([60, 60, 452, 452], fill="#FEF3C7", outline="#D97706", width=8)
        d.ellipse([140, 140, 372, 340], fill="#D97706")
        d.ellipse([90, 130, 170, 260], fill="#B45309")
        d.ellipse([342, 130, 422, 260], fill="#B45309")
        d.ellipse([206, 220, 306, 320], fill="#FDE68A")
        d.ellipse([236, 235, 276, 265], fill="black")
        d.ellipse([244, 280, 268, 315], fill="#F87171")
        d.ellipse([186, 175, 226, 215], fill="black")
        d.ellipse([192, 180, 204, 192], fill="white")
        d.ellipse([286, 175, 326, 215], fill="black")
        d.ellipse([292, 180, 304, 192], fill="white")

        draw_text_centered(d, phrase, (256, 420), font_md, fill="#78350F", stroke_fill="white", stroke_width=5)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 14. br-carnaval-samba (Animated) ──
def generate_br_carnaval_samba():
    pack_dir = create_pack_folder('br-carnaval-samba')
    font_md = get_font(34)

    phrases = [
        "É CARNAVAL BRASIL! 🎭",
        "RITMO DO SAMBA 🥁",
        "GLITTER & CONFETE ✨",
        "ATRÁS DO TRIO ELÉTRICO 🚚",
        "ALEGRIA NÃO PARA! 💃",
        "SAMBA NO PÉ 🔥",
        "ME LEVA QUE EU VOU! 🥳",
        "FOLIA SEM FIM 🎶"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            mask_bob = int(math.sin(phase) * 14)
            
            for ci in range(16):
                cx = (ci * 32 + int(f * 20)) % 480 + 16
                cy = (ci * 28 + int(f * 35)) % 400 + 40
                colors = ["#F43F5E", "#8B5CF6", "#FACC15", "#10B981", "#06B6D4"]
                d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=colors[ci % len(colors)])

            for fa, color in [(-40, "#EC4899"), (-20, "#8B5CF6"), (0, "#FACC15"), (20, "#10B981"), (40, "#06B6D4")]:
                fx = int(256 + math.sin(math.radians(fa)) * 140)
                fy = int(140 - math.cos(math.radians(fa)) * 80 + mask_bob)
                d.polygon([(256, 190 + mask_bob), (fx - 15, fy), (fx, fy - 30), (fx + 15, fy)], fill=color)

            d.polygon([
                (120, 180 + mask_bob),
                (256, 210 + mask_bob),
                (392, 180 + mask_bob),
                (350, 270 + mask_bob),
                (256, 250 + mask_bob),
                (162, 270 + mask_bob)
            ], fill="#F59E0B", outline="#78350F", width=5)
            d.ellipse([160, 205 + mask_bob, 220, 245 + mask_bob], fill="white")
            d.ellipse([292, 205 + mask_bob, 352, 245 + mask_bob], fill="white")

            draw_text_centered(d, phrase, (256, 430), font_md, fill="#BE185D", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 15. br-girias-brasileiras (Static) ──
def generate_br_girias_brasileiras():
    pack_dir = create_pack_folder('br-girias-brasileiras')
    font_lg = get_font(56)
    font_md = get_font(32)

    girias = [
        ("EITA!", "Lascou tudo 🔥", "#EF4444"),
        ("VIXI!", "Nem te conto 👀", "#F59E0B"),
        ("TOP DEMAIS!", "Aprovado 100% ⭐", "#10B981"),
        ("VALEU FALOU!", "Partiu fui 🏃💨", "#3B82F6"),
        ("MANO DO CÉU!", "Tô chocado 😱", "#8B5CF6"),
        ("AFF NADA A VER!", "Paciência zero 🙄", "#EC4899"),
        ("PARTIU!", "Bora lá agora 🚀", "#06B6D4"),
        ("TÁ DE BRINCADEIRA?", "Não acredito 🤡", "#D97706")
    ]

    for st_idx, (word, sub, color) in enumerate(girias, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        
        d.rounded_rectangle([40, 70, 472, 380], radius=35, fill=color, outline="white", width=8)
        d.polygon([(140, 370), (110, 450), (200, 370)], fill=color)

        draw_text_centered(d, word, (256, 180), font_lg, fill="white", stroke_fill="black", stroke_width=6)
        draw_text_centered(d, sub, (256, 280), font_md, fill="#FEF08A", stroke_fill="black", stroke_width=4)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 16. br-casal-fofo (Animated) ──
def generate_br_casal_fofo():
    pack_dir = create_pack_folder('br-casal-fofo')
    font_md = get_font(34)

    phrases = [
        "CASAL PERFEITO ❤️",
        "AMO VOCÊ DEMAIS 🥰",
        "MINHA METADE 💕",
        "GRUDINHO GOSTOSO 🍯",
        "SEMPRE JUNTINHOS 👫",
        "VOCÊ É MEU TUDO ✨",
        "AMOR DA MINHA VIDA 💖",
        "NOSSO AMOR É LINDO 💍"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            pulse = int(math.sin(phase) * 12)
            
            d.ellipse([130, 140 + pulse, 240, 250 + pulse], fill="#93C5FD")
            d.ellipse([150, 175 + pulse, 168, 195 + pulse], fill="#1E3A8A")
            d.ellipse([200, 175 + pulse, 218, 195 + pulse], fill="#1E3A8A")
            d.arc([165, 200 + pulse, 205, 230 + pulse], 20, 160, fill="#1E3A8A", width=4)
            d.ellipse([140, 240 + pulse, 230, 360 + pulse], fill="#3B82F6")

            d.ellipse([272, 140 - pulse, 382, 250 - pulse], fill="#FBCFE8")
            d.ellipse([292, 175 - pulse, 310, 195 - pulse], fill="#831843")
            d.ellipse([342, 175 - pulse, 360, 195 - pulse], fill="#831843")
            d.arc([307, 200 - pulse, 347, 230 - pulse], 20, 160, fill="#831843", width=4)
            d.ellipse([282, 240 - pulse, 372, 360 - pulse], fill="#EC4899")
            d.polygon([(260, 130 - pulse), (285, 145 - pulse), (260, 160 - pulse)], fill="#EF4444")
            d.polygon([(310, 130 - pulse), (285, 145 - pulse), (310, 160 - pulse)], fill="#EF4444")

            hs = int(32 + 8 * math.sin(phase))
            d.ellipse([256 - hs, 270 - hs, 256 + hs, 270 + hs], fill="#EF4444")

            draw_text_centered(d, phrase, (256, 430), font_md, fill="#BE185D", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 17. br-zoeira-amigos (Static) ──
def generate_br_zoeira_amigos():
    pack_dir = create_pack_folder('br-zoeira-amigos')
    font_md = get_font(34)

    quotes = [
        ("LÁ VEM ELE DE NOVO 🙄", "#EF4444"),
        ("TÔ DE OLHO NO GOLPE 👀", "#F59E0B"),
        ("PERDI TUDO KKKKKK 😂", "#10B981"),
        ("NEM ME FALE UMA COISA DESSAS 🤦", "#3B82F6"),
        ("QUEM PERGUNTOU? 🎤", "#8B5CF6"),
        ("MANDOU MAL DEMAIS 👎", "#EC4899"),
        ("SÓ ACHO GRAÇA DISSO 🤡", "#D97706"),
        ("RESENHA DOS CRIAS 🤙", "#06B6D4")
    ]

    for st_idx, (quote, color) in enumerate(quotes, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        
        d.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#F1F5F9", outline=color, width=8)
        
        d.ellipse([146, 110, 366, 330], fill=color)
        d.ellipse([180, 170, 220, 210], fill="white")
        d.ellipse([292, 170, 332, 210], fill="white")
        d.ellipse([192, 180, 210, 200], fill="black")
        d.ellipse([304, 180, 322, 200], fill="black")
        d.arc([190, 220, 322, 290], 10, 170, fill="black", width=6)

        draw_text_centered(d, quote, (256, 400), font_md, fill="black", stroke_fill="white", stroke_width=4)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 18. br-passinho-funk (Animated) ──
def generate_br_passinho_funk():
    pack_dir = create_pack_folder('br-passinho-funk')
    font_md = get_font(34)

    phrases = [
        "MANDA O PASSINHO! 🕺",
        "NO RITMO DO BAILE 🔊",
        "SOLTA O GRAVE! 🎵",
        "SÓ QUEM É RAIZ 🔥",
        "DANÇA DEMAIS! 💃",
        "TOCANDO O TERROR ⚡",
        "BATIDÃO PESADO 🎧",
        "SINTONIA PURA ✨"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            leg_step = int(math.sin(phase) * 35)
            arm_pump = int(math.cos(phase) * 25)
            
            for bi in range(9):
                bx = 90 + bi * 40
                bh = int(40 + 60 * abs(math.sin(phase + bi * 0.7)))
                d.rectangle([bx, 320 - bh, bx + 24, 320], fill=(244, 63, 94, 180))

            d.line([(256, 210), (256, 310)], fill="#1E293B", width=18)
            d.line([(256, 310), (200 - leg_step, 390)], fill="#1E293B", width=14)
            d.line([(256, 310), (312 + leg_step, 390)], fill="#1E293B", width=14)
            d.line([(256, 230), (160, 200 + arm_pump)], fill="#F59E0B", width=14)
            d.line([(256, 230), (352, 200 - arm_pump)], fill="#F59E0B", width=14)
            d.ellipse([220, 110, 292, 180], fill="#FDE68A")
            d.arc([210, 95, 302, 150], 180, 360, fill="#EF4444", width=14)
            d.rectangle([210, 140, 302, 148], fill="#EF4444")
            d.rectangle([228, 135, 284, 155], fill="black")

            draw_text_centered(d, phrase, (256, 430), font_md, fill="#E11D48", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 19. br-lula-reacoes (Static) ──
def generate_br_lula_reacoes():
    pack_dir = create_pack_folder('br-lula-reacoes')
    font_md = get_font(34)

    quotes = [
        ("FAZ O L! 👆", "O amor venceu ❤️", "#EF4444"),
        ("COMPANHEIRO! ✊", "Tamo junto sempre", "#DC2626"),
        ("VAI TER PICANHA! 🥩", "Com cervejinha gelada", "#B91C1C"),
        ("O BRASIL VOLTOU! 🇧🇷", "Rumo ao futuro", "#009C3B"),
        ("NUNCA ANTES NA HISTÓRIA 📜", "Desse país...", "#B45309"),
        ("UM BRINDE AO POVO 🥂", "Saúde e dignidade", "#7C3AED"),
        ("SORRINDO PRA VIDA 😁", "Esperança renovada", "#2563EB"),
        ("UNIÃO & RECONSTRUÇÃO ⭐", "Paz no Brasil", "#EA580C")
    ]

    for st_idx, (title, sub, color) in enumerate(quotes, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        
        d.rounded_rectangle([40, 50, 472, 462], radius=30, fill="white", outline=color, width=8)
        
        d.ellipse([140, 110, 372, 330], fill=color)
        d.arc([160, 200, 352, 315], 0, 180, fill="white", width=22)
        d.rectangle([180, 170, 230, 205], outline="black", width=4)
        d.rectangle([282, 170, 332, 205], outline="black", width=4)
        d.line([(230, 187), (282, 187)], fill="black", width=4)
        d.arc([200, 210, 312, 260], 20, 160, fill="black", width=4)

        draw_text_centered(d, title, (256, 380), font_md, fill=color, stroke_fill="white", stroke_width=4)
        draw_text_centered(d, sub, (256, 425), get_font(26), fill="#4B5563", stroke_fill="white", stroke_width=3)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 20. br-coracao-paixao (Animated) ──
def generate_br_coracao_paixao():
    pack_dir = create_pack_folder('br-coracao-paixao')
    font_md = get_font(34)

    phrases = [
        "CORAÇÃO BATENDO FORTE 💓",
        "VOCÊ É MEU AMOR 💖",
        "EXPLOSÃO DE PAIXÃO 💥❤️",
        "CUPIDO ME ACERTOU 💘",
        "AMOR INFINITO ♾️",
        "BRILHO NOS OLHOS ✨",
        "MEU CORAÇÃO É SEU 💝",
        "TE AMO ETERNAMENTE 🌹"
    ]

    for st_idx, phrase in enumerate(phrases, 1):
        frames = []
        num_frames = 6
        for f in range(num_frames):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / num_frames) * 2 * math.pi
            
            scale = 1.0 + 0.18 * math.sin(phase)
            cx, cy = 256, 220
            r = int(120 * scale)
            
            d.polygon([(cx, cy + r), (cx - r, cy - int(r*0.2)), (cx, cy - int(r*0.6)), (cx + r, cy - int(r*0.2))], fill="#EF4444")
            d.pieslice([cx - r, cy - int(r*0.8), cx, cy + int(r*0.2)], 180, 0, fill="#EF4444")
            d.pieslice([cx, cy - int(r*0.8), cx + r, cy + int(r*0.2)], 180, 0, fill="#EF4444")

            for hi in range(6):
                h_angle = phase + hi * (math.pi / 3)
                hx = int(cx + math.cos(h_angle) * (r + 40))
                hy = int(cy + math.sin(h_angle) * (r + 40))
                hs = int(12 + 6 * math.sin(h_angle))
                d.ellipse([hx - hs, hy - hs, hx + hs, hy + hs], fill="#F472B6")

            draw_text_centered(d, phrase, (256, 430), font_md, fill="#E11D48", stroke_fill="white", stroke_width=5)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


if __name__ == "__main__":
    print("Generating 20 Brazil localized sticker packs...")
    generate_br_bandeira_nacional()
    print("1/20 br-bandeira-nacional done.")
    generate_br_bandeira_animada()
    print("2/20 br-bandeira-animada done.")
    generate_br_bolsonaro_dancando()
    print("3/20 br-bolsonaro-dancando done.")
    generate_br_beijo_apaixonado()
    print("4/20 br-beijo-apaixonado done.")
    generate_br_abraco_carinhoso()
    print("5/20 br-abraco-carinhoso done.")
    generate_br_figurinhas_hot()
    print("6/20 br-figurinhas-hot done.")
    generate_br_futebol_selecao()
    print("7/20 br-futebol-selecao done.")
    generate_br_futebol_gols_animados()
    print("8/20 br-futebol-gols-animados done.")
    generate_br_memes_classicos()
    print("9/20 br-memes-classicos done.")
    generate_br_gretchen_rainha()
    print("10/20 br-gretchen-rainha done.")
    generate_br_flork_debochado()
    print("11/20 br-flork-debochado done.")
    generate_br_bom_dia_boa_noite()
    print("12/20 br-bom-dia-boa-noite done.")
    generate_br_vira_lata_caramelo()
    print("13/20 br-vira-lata-caramelo done.")
    generate_br_carnaval_samba()
    print("14/20 br-carnaval-samba done.")
    generate_br_girias_brasileiras()
    print("15/20 br-girias-brasileiras done.")
    generate_br_casal_fofo()
    print("16/20 br-casal-fofo done.")
    generate_br_zoeira_amigos()
    print("17/20 br-zoeira-amigos done.")
    generate_br_passinho_funk()
    print("18/20 br-passinho-funk done.")
    generate_br_lula_reacoes()
    print("19/20 br-lula-reacoes done.")
    generate_br_coracao_paixao()
    print("20/20 br-coracao-paixao done.")
    print("All 20 Brazil sticker packs generated successfully!")
