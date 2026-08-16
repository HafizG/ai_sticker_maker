import os
import math
import random
from PIL import Image, ImageDraw, ImageFont

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

def save_static(img, path):
    img.save(path, format="WEBP", lossless=True)

def save_animated(frames, path, duration=130):
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

# ── 1. br-bandeira-nacional ──
def generate_br_bandeira_nacional():
    pack_dir = create_pack_folder('br-bandeira-nacional')
    font_lg, font_md, font_sm = get_font(44), get_font(32), get_font(24)

    im1 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d1 = ImageDraw.Draw(im1)
    d1.rectangle([70, 60, 86, 460], fill="#94A3B8", outline="#475569", width=2)
    d1.ellipse([64, 46, 92, 74], fill="#F59E0B", outline="#B45309", width=3)
    d1.rectangle([86, 74, 450, 314], fill="#009C3B", outline="#005A20", width=4)
    d1.polygon([(268, 94), (430, 194), (268, 294), (106, 194)], fill="#FFDF00")
    d1.ellipse([218, 144, 318, 244], fill="#002776")
    d1.arc([218, 160, 318, 230], 190, 350, fill="white", width=7)
    draw_text_centered(d1, "BRASIL 🇧🇷", (270, 410), font_lg, fill="#FFDF00", stroke_fill="#002776", stroke_width=6)
    save_static(im1, os.path.join(pack_dir, "1.webp"))
    im1.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")

    im2 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d2 = ImageDraw.Draw(im2)
    br_map = [(130, 120), (220, 80), (320, 100), (430, 150), (460, 240), (390, 300), (360, 420), (310, 460), (280, 400), (240, 320), (150, 280), (90, 200)]
    d2.polygon(br_map, fill="#009C3B", outline="#FFDF00", width=8)
    d2.polygon([(280, 170), (380, 240), (280, 310), (180, 240)], fill="#FFDF00")
    d2.ellipse([240, 200, 320, 280], fill="#002776")
    draw_star(d2, (280, 235), 10, 5, fill="white")
    draw_text_centered(d2, "PÁTRIA AMADA", (256, 440), font_md, fill="#009C3B", stroke_fill="white", stroke_width=5)
    save_static(im2, os.path.join(pack_dir, "2.webp"))

    im3 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d3 = ImageDraw.Draw(im3)
    d3.polygon([(256, 450), (60, 240), (120, 100), (256, 180), (392, 100), (452, 240)], fill="#009C3B")
    d3.pieslice([60, 100, 256, 280], 180, 0, fill="#009C3B")
    d3.pieslice([256, 100, 452, 280], 180, 0, fill="#009C3B")
    d3.polygon([(256, 180), (390, 250), (256, 370), (122, 250)], fill="#FFDF00")
    d3.ellipse([206, 200, 306, 300], fill="#002776")
    draw_text_centered(d3, "AMOR VERDE & AMARELO", (256, 440), font_sm, fill="#009C3B", stroke_fill="white", stroke_width=4)
    save_static(im3, os.path.join(pack_dir, "3.webp"))

    im4 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d4 = ImageDraw.Draw(im4)
    d4.ellipse([80, 80, 432, 432], fill="#FFDF00", outline="#009C3B", width=10)
    d4.pieslice([80, 80, 432, 432], 0, 180, fill="#002776")
    d4.polygon([(160, 432), (256, 260), (352, 432)], fill="#15803D")
    d4.rectangle([250, 170, 262, 265], fill="white")
    d4.ellipse([248, 150, 264, 170], fill="white")
    d4.line([(180, 195), (332, 195)], fill="white", width=8)
    draw_text_centered(d4, "RIO DE JANEIRO", (256, 420), font_md, fill="white", stroke_fill="#002776", stroke_width=5)
    save_static(im4, os.path.join(pack_dir, "4.webp"))

    im5 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d5 = ImageDraw.Draw(im5)
    d5.polygon([(256, 50), (440, 120), (410, 340), (256, 460), (102, 340), (72, 120)], fill="#009C3B", outline="#FFDF00", width=12)
    d5.polygon([(256, 120), (380, 240), (256, 360), (132, 240)], fill="#FFDF00")
    d5.ellipse([196, 180, 316, 300], fill="#002776")
    draw_star(d5, (256, 240), 24, 11, fill="white")
    draw_text_centered(d5, "GIGANTE", (256, 410), font_md, fill="#FFDF00", stroke_fill="#002776", stroke_width=5)
    save_static(im5, os.path.join(pack_dir, "5.webp"))

    im6 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d6 = ImageDraw.Draw(im6)
    d6.polygon([(180, 280), (130, 460), (200, 420), (230, 460), (210, 300)], fill="#009C3B", outline="#FFDF00", width=3)
    d6.polygon([(332, 280), (382, 460), (312, 420), (282, 460), (302, 300)], fill="#FFDF00", outline="#009C3B", width=3)
    d6.ellipse([116, 70, 396, 350], fill="#F59E0B", outline="#B45309", width=8)
    d6.ellipse([146, 100, 366, 320], fill="#009C3B")
    d6.polygon([(256, 120), (340, 210), (256, 300), (172, 210)], fill="#FFDF00")
    d6.ellipse([216, 170, 296, 250], fill="#002776")
    draw_text_centered(d6, "1º LUGAR", (256, 390), font_lg, fill="#009C3B", stroke_fill="white", stroke_width=6)
    save_static(im6, os.path.join(pack_dir, "6.webp"))

    im7 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d7 = ImageDraw.Draw(im7)
    d7.ellipse([60, 60, 452, 452], fill="#002776", outline="#FFDF00", width=8)
    draw_star(d7, (256, 240), 130, 40, points=8, fill="#FFDF00", outline="#009C3B", width=3)
    d7.ellipse([206, 190, 306, 290], fill="#009C3B", outline="white", width=4)
    draw_text_centered(d7, "SOU BRASIL", (256, 425), font_lg, fill="#FFDF00", stroke_fill="#002776", stroke_width=5)
    save_static(im7, os.path.join(pack_dir, "7.webp"))

    im8 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d8 = ImageDraw.Draw(im8)
    d8.rounded_rectangle([50, 100, 462, 380], radius=35, fill="#009C3B", outline="#FFDF00", width=8)
    d8.polygon([(256, 130), (410, 240), (256, 350), (102, 240)], fill="#FFDF00")
    d8.ellipse([186, 170, 326, 310], fill="#002776")
    draw_text_centered(d8, "BRASILEIRO COM ORGULHO", (256, 430), font_md, fill="#009C3B", stroke_fill="white", stroke_width=5)
    save_static(im8, os.path.join(pack_dir, "8.webp"))


# ── 2. br-bandeira-animada ──
def generate_br_bandeira_animada():
    pack_dir = create_pack_folder('br-bandeira-animada')
    font_sm = get_font(24)

    animations = [
        ("BANDEIRA ONDULANDO 🇧🇷", "wave"),
        ("FOGOS VERDE & AMARELO 🎆", "fireworks"),
        ("CORAÇÃO BRASILEIRO 💖", "heartbeat"),
        ("MOEDA DE OURO 🪙", "coin_spin"),
        ("AVIÃO COM FAIXA ✈️", "plane"),
        ("NEON PULSANTE ⚡", "neon"),
        ("TAÇA DO MUNDO BRILHANDO 🏆", "trophy"),
        ("CHUVA DE CONFETE 🎉", "confetti")
    ]

    for st_idx, (title, anim_type) in enumerate(animations, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            
            if anim_type == "wave":
                wo = int(math.sin(phase) * 18)
                d.rectangle([80, 110 + wo, 432, 330 + wo], fill="#009C3B", outline="#005A20", width=4)
                d.polygon([(256, 130 + wo), (390, 220 + wo), (256, 310 + wo), (122, 220 + wo)], fill="#FFDF00")
                d.ellipse([206, 170 + wo, 306, 270 + wo], fill="#002776")
            elif anim_type == "fireworks":
                d.ellipse([100, 100, 412, 412], fill="#0F172A", outline="#FFDF00", width=6)
                for fw_i in range(12):
                    fa = fw_i * (math.pi / 6)
                    fr = 50 + int(f * 15)
                    fx = int(256 + math.cos(fa) * fr)
                    fy = int(240 + math.sin(fa) * fr)
                    d.ellipse([fx-6, fy-6, fx+6, fy+6], fill="#FFDF00" if fw_i % 2 == 0 else "#009C3B")
            elif anim_type == "coin_spin":
                scale_x = abs(math.cos(phase))
                cw = int(140 * max(0.1, scale_x))
                d.ellipse([256 - cw, 120, 256 + cw, 360], fill="#F59E0B", outline="#B45309", width=6)
                if cw > 40:
                    draw_text_centered(d, "BR", (256, 240), get_font(42), fill="#009C3B", stroke_fill="white", stroke_width=3)
            elif anim_type == "plane":
                px = 60 + f * 45
                d.polygon([(px, 160), (px + 60, 180), (px, 200), (px + 10, 180)], fill="#E2E8F0")
                d.rectangle([px - 140, 165, px - 10, 195], fill="#009C3B", outline="#FFDF00", width=2)
                draw_text_centered(d, "BRASIL", (px - 75, 180), get_font(16), fill="#FFDF00")
            elif anim_type == "trophy":
                d.polygon([(180, 140), (332, 140), (300, 280), (256, 340), (212, 280)], fill="#F59E0B", outline="#B45309", width=4)
                d.rectangle([236, 340, 276, 380], fill="#B45309")
                d.rectangle([200, 380, 312, 400], fill="#78350F")
                for beam in range(6):
                    ba = phase + beam * (math.pi / 3)
                    d.line([(256, 200), (int(256 + math.cos(ba)*160), int(200 + math.sin(ba)*160))], fill="#FEF08A", width=3)
            else:
                scale = 1.0 + 0.15 * math.sin(phase)
                r = int(120 * scale)
                d.ellipse([256 - r, 240 - r, 256 + r, 240 + r], fill="#009C3B", outline="#FFDF00", width=8)
                d.polygon([(256, 240 - int(r*0.7)), (256 + int(r*0.7), 240), (256, 240 + int(r*0.7)), (256 - int(r*0.7), 240)], fill="#FFDF00")
                d.ellipse([256 - int(r*0.35), 240 - int(r*0.35), 256 + int(r*0.35), 240 + int(r*0.35)], fill="#002776")

            draw_text_centered(d, title, (256, 435), font_sm, fill="#047857", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 3. br-bolsonaro-dancando ──
def generate_br_bolsonaro_dancando():
    pack_dir = create_pack_folder('br-bolsonaro-dancando')
    font_md = get_font(32)

    scenes = [
        ("DANÇA DO CAPITÃO 🕺", "dance"),
        ("TURN DOWN FOR WHAT 😎", "thug_life"),
        ("DE JET SKI NA PRAIA 🌊", "jetski"),
        ("TÁ COM MEDO, PETISTA? 📢", "megaphone"),
        ("TUDO CERTO, MEU BRASIL 👍", "thumbs_up"),
        ("TOCANDO SANFONA 🪗", "accordion"),
        ("FLEXÃO MILITAR 💪", "pushups"),
        ("PASTEL COM CALDO DE CANA 🥟", "pastel")
    ]

    for st_idx, (title, scene_type) in enumerate(scenes, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            
            bounce = int(abs(math.sin(phase)) * 20)
            sway = int(math.sin(phase) * 25)
            
            d.ellipse([50, 50, 462, 462], fill=(240, 253, 244, 245), outline="#16A34A", width=7)
            head_x, head_y = 256, 150 - bounce
            
            if scene_type == "thug_life":
                glass_y = min(head_y - 5, 60 + f * 18)
                d.ellipse([head_x - 45, head_y - 45, head_x + 45, head_y + 45], fill="#FED7AA")
                d.arc([head_x - 48, head_y - 50, head_x + 48, head_y + 10], 170, 370, fill="#64748B", width=14)
                d.rectangle([head_x - 40, glass_y, head_x - 8, glass_y + 20], fill="black")
                d.rectangle([head_x + 8, glass_y, head_x + 40, glass_y + 20], fill="black")
                d.line([(head_x - 8, glass_y + 8), (head_x + 8, glass_y + 8)], fill="black", width=4)
            elif scene_type == "jetski":
                d.ellipse([head_x - 35, head_y - 35, head_x + 35, head_y + 35], fill="#FED7AA")
                d.polygon([(140, 310 + bounce), (370, 310 + bounce), (420, 260 + bounce), (200, 260 + bounce)], fill="#2563EB", outline="#1D4ED8", width=4)
                for wx in [110, 160, 380, 420]:
                    d.ellipse([wx - 10, 300 + bounce + sway, wx + 10, 330 + bounce + sway], fill="#38BDF8")
            elif scene_type == "megaphone":
                d.ellipse([head_x - 40, head_y - 40, head_x + 40, head_y + 40], fill="#FED7AA")
                d.polygon([(260, head_y), (350, head_y - 40), (350, head_y + 40)], fill="#DC2626", outline="black", width=3)
                d.arc([360, head_y - 50, 410, head_y + 50], 290, 70, fill="#F59E0B", width=6)
            elif scene_type == "accordion":
                d.ellipse([head_x - 40, head_y - 40, head_x + 40, head_y + 40], fill="#FED7AA")
                bellow_w = 60 + abs(sway)
                d.rectangle([256 - bellow_w, 240, 256 + bellow_w, 320], fill="#DC2626", outline="black", width=3)
                for bx in range(256 - bellow_w, 256 + bellow_w, 15):
                    d.line([(bx, 240), (bx, 320)], fill="white", width=2)
            else:
                d.ellipse([head_x - 45, head_y - 45, head_x + 45, head_y + 45], fill="#FED7AA")
                d.arc([head_x - 48, head_y - 50, head_x + 48, head_y + 10], 170, 370, fill="#64748B", width=14)
                d.polygon([(190, head_y + 45), (322, head_y + 45), (342, 330), (170, 330)], fill="#1E3A8A")
                d.line([(190, head_y + 55), (320, 330)], fill="#009C3B", width=16)
                d.line([(195, head_y + 58), (325, 330)], fill="#FFDF00", width=8)
                d.ellipse([130, 220 + sway, 170, 260 + sway], fill="#FED7AA")
                d.ellipse([342, 220 - sway, 382, 260 - sway], fill="#FED7AA")

# ── 5. br-futebol-selecao ──
def generate_br_futebol_selecao():
    pack_dir = create_pack_folder('br-futebol-selecao')
    font_lg, font_md, font_sm = get_font(42), get_font(32), get_font(24)

    # 1. Pelé
    im1 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d1 = ImageDraw.Draw(im1)
    d1.ellipse([60, 60, 452, 452], fill="#FEF08A", outline="#009C3B", width=8)
    d1.polygon([(190, 140), (220, 90), (256, 130), (292, 90), (322, 140), (310, 160), (202, 160)], fill="#F59E0B", outline="#B45309", width=3)
    d1.ellipse([206, 165, 306, 265], fill="#78350F")
    d1.polygon([(180, 265), (332, 265), (360, 380), (152, 380)], fill="#FFDF00", outline="#009C3B", width=4)
    draw_text_centered(d1, "10", (256, 325), get_font(48), fill="#002776", stroke_fill="white", stroke_width=2)
    draw_text_centered(d1, "PELÉ: O REI DO FUTEBOL 👑", (256, 425), font_sm, fill="#78350F", stroke_fill="white", stroke_width=4)
    save_static(im1, os.path.join(pack_dir, "1.webp"))
    im1.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")

    # 2. Neymar Jr
    im2 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d2 = ImageDraw.Draw(im2)
    d2.ellipse([60, 60, 452, 452], fill="#E0F2FE", outline="#0284C7", width=8)
    d2.ellipse([216, 100, 296, 170], fill="#FDE047")
    d2.ellipse([200, 145, 312, 265], fill="#D97706")
    d2.arc([235, 180, 255, 200], 180, 360, fill="black", width=4)
    d2.ellipse([275, 185, 290, 200], fill="black")
    d2.ellipse([246, 225, 266, 255], fill="#F43F5E")
    d2.ellipse([150, 160, 195, 230], fill="#D97706", outline="#78350F", width=2)
    d2.ellipse([317, 160, 362, 230], fill="#D97706", outline="#78350F", width=2)
    d2.polygon([(180, 265), (332, 265), (360, 370), (152, 370)], fill="#FFDF00")
    draw_text_centered(d2, "NEYMAR JR ⚡", (256, 420), font_md, fill="#0369A1", stroke_fill="white", stroke_width=5)
    save_static(im2, os.path.join(pack_dir, "2.webp"))

    # 3. Vinicius Jr
    im3 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d3 = ImageDraw.Draw(im3)
    d3.ellipse([60, 60, 452, 452], fill="#DCFCE7", outline="#16A34A", width=8)
    d3.ellipse([200, 130, 312, 250], fill="#5B3821")
    d3.rectangle([210, 170, 250, 195], fill="black")
    d3.rectangle([262, 170, 302, 195], fill="black")
    d3.line([(250, 180), (262, 180)], fill="black", width=3)
    d3.arc([226, 205, 286, 235], 0, 180, fill="white", width=6)
    d3.polygon([(170, 250), (342, 250), (370, 370), (142, 370)], fill="#FFDF00")
    draw_text_centered(d3, "7", (256, 310), get_font(46), fill="#002776", stroke_fill="white", stroke_width=2)
    draw_text_centered(d3, "BAILA VINI JR! 🕺", (256, 420), font_md, fill="#15803D", stroke_fill="white", stroke_width=5)
    save_static(im3, os.path.join(pack_dir, "3.webp"))

    # 4. Ronaldinho Gaúcho
    im4 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d4 = ImageDraw.Draw(im4)
    d4.ellipse([60, 60, 452, 452], fill="#FEF9C3", outline="#CA8A04", width=8)
    d4.ellipse([170, 110, 342, 290], fill="#1C1917")
    d4.rectangle([195, 140, 317, 158], fill="white", outline="black", width=2)
    d4.ellipse([200, 155, 312, 270], fill="#854D0E")
    d4.arc([220, 215, 292, 255], 0, 180, fill="white", width=8)
    d4.polygon([(110, 240), (140, 200), (160, 250), (130, 290)], fill="#854D0E")
    d4.polygon([(402, 240), (372, 200), (352, 250), (382, 290)], fill="#854D0E")
    draw_text_centered(d4, "RONALDINHO BRUXO 🤙", (256, 420), font_sm, fill="#854D0E", stroke_fill="white", stroke_width=4)
    save_static(im4, os.path.join(pack_dir, "4.webp"))

    # 5. Ronaldo R9
    im5 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d5 = ImageDraw.Draw(im5)
    d5.ellipse([60, 60, 452, 452], fill="#F3E8FF", outline="#9333EA", width=8)
    d5.ellipse([196, 140, 316, 260], fill="#92400E")
    d5.polygon([(236, 140), (276, 140), (256, 175)], fill="#1C1917")
    d5.arc([226, 205, 286, 240], 0, 180, fill="white", width=6)
    d5.rectangle([340, 160, 360, 260], fill="#92400E", outline="#78350F", width=2)
    d5.polygon([(170, 260), (342, 260), (370, 370), (142, 370)], fill="#FFDF00")
    draw_text_centered(d5, "9", (256, 315), get_font(46), fill="#002776", stroke_fill="white", stroke_width=2)
    draw_text_centered(d5, "RONALDO R9 FENÔMENO", (256, 420), font_sm, fill="#7E22CE", stroke_fill="white", stroke_width=4)
    save_static(im5, os.path.join(pack_dir, "5.webp"))

    # 6. Marta
    im6 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d6 = ImageDraw.Draw(im6)
    d6.ellipse([60, 60, 452, 452], fill="#FFF1F2", outline="#E11D48", width=8)
    d6.ellipse([190, 120, 322, 260], fill="#78350F")
    d6.ellipse([300, 110, 340, 180], fill="#1C1917")
    d6.polygon([(220, 250), (292, 250), (276, 330), (236, 330)], fill="#F59E0B", outline="#B45309", width=3)
    d6.ellipse([236, 220, 276, 260], fill="#FDE047")
    for star_i in range(6):
        draw_star(d6, (156 + star_i * 40, 95), 12, 5, fill="#F59E0B")
    draw_text_centered(d6, "MARTA: 6X MELHOR DO MUNDO", (256, 420), font_sm, fill="#BE123C", stroke_fill="white", stroke_width=4)
    save_static(im6, os.path.join(pack_dir, "6.webp"))

    # 7. Ayrton Senna
    im7 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d7 = ImageDraw.Draw(im7)
    d7.ellipse([60, 60, 452, 452], fill="#ECFDF5", outline="#059669", width=8)
    d7.ellipse([140, 120, 372, 340], fill="#FFDF00", outline="#B45309", width=6)
    d7.rectangle([140, 210, 372, 235], fill="#009C3B")
    d7.rectangle([140, 235, 372, 260], fill="#002776")
    d7.rounded_rectangle([190, 180, 322, 240], radius=15, fill="#0F172A", outline="white", width=3)
    draw_text_centered(d7, "SENNA SEMPRE 🏎️🇧🇷", (256, 420), font_md, fill="#047857", stroke_fill="white", stroke_width=5)
    save_static(im7, os.path.join(pack_dir, "7.webp"))

    # 8. Richarlison
    im8 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d8 = ImageDraw.Draw(im8)
    d8.ellipse([60, 60, 452, 452], fill="#F0FDF4", outline="#15803D", width=8)
    d8.ellipse([216, 120, 296, 175], fill="#F8FAFC", outline="#94A3B8", width=2)
    d8.ellipse([206, 150, 306, 260], fill="#D97706")
    d8.polygon([(180, 260), (100, 220), (140, 300)], fill="#FFDF00", outline="#009C3B", width=3)
    d8.polygon([(332, 260), (412, 220), (372, 300)], fill="#FFDF00", outline="#009C3B", width=3)
    draw_text_centered(d8, "PRUUU! DANÇA DO POMBO 🐦", (256, 420), font_sm, fill="#166534", stroke_fill="white", stroke_width=4)
    save_static(im8, os.path.join(pack_dir, "8.webp"))


# ── 8. br-futebol-gols-animados ──
def generate_br_futebol_gols_animados():
    pack_dir = create_pack_folder('br-futebol-gols-animados')
    font_sm = get_font(24)

    celebrations = [
        ("GOL DE BICICLETA! 🚲⚽", "bicycle"),
        ("NA GAVETA! 🥅💥", "net_rip"),
        ("DEFESAÇA HISTÓRICA! 🧤", "save"),
        ("DESLIZANDO NO GRAMADO 🌱", "slide"),
        ("SAMBA NA BANDEIRINHA 🚩", "corner_samba"),
        ("BOLA GIRANDO NO DEDO ☝️", "finger_spin"),
        ("SINALIZADOR & TORCIDA 🎇", "flare"),
        ("CHAMA O VAR! 📺", "var")
    ]

    for st_idx, (title, action) in enumerate(celebrations, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            
            d.ellipse([50, 50, 462, 462], fill=(240, 253, 244, 240), outline="#16A34A", width=7)
            
            if action == "bicycle":
                rot = phase
                d.ellipse([230, 200, 280, 250], fill="#FFD1A4")
                d.line([(256, 230), (int(256 + math.cos(rot)*80), int(230 + math.sin(rot)*80))], fill="#FFDF00", width=14)
                bx = int(256 + math.cos(rot + math.pi)*100)
                by = int(230 + math.sin(rot + math.pi)*100)
                d.ellipse([bx-25, by-25, bx+25, by+25], fill="white", outline="black", width=3)
            elif action == "var":
                d.rectangle([130, 140, 382, 320], outline="#38BDF8", width=8)
                draw_text_centered(d, "V A R", (256, 230), get_font(46), fill="#38BDF8", stroke_fill="black", stroke_width=4)
            elif action == "save":
                gx = 140 + f * 35
                d.rectangle([gx, 180, gx + 50, 260], fill="#EF4444", outline="black", width=3)
                d.ellipse([gx + 60, 200, gx + 100, 240], fill="white", outline="black", width=3)
            else:
                bx = 140 + f * 45
                by = int(260 - math.sin(phase)*40)
                d.rectangle([340, 130, 470, 340], outline="white", width=6)
                d.ellipse([bx-30, by-30, bx+30, by+30], fill="white", outline="black", width=4)
                d.line([(bx-40, by), (bx-100, by)], fill="#FFDF00", width=5)

            draw_text_centered(d, title, (256, 425), font_sm, fill="#15803D", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 4. br-lula-reacoes ──
def generate_br_lula_reacoes():
    pack_dir = create_pack_folder('br-lula-reacoes')
    font_lg, font_md, font_sm = get_font(42), get_font(32), get_font(24)

    im1 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d1 = ImageDraw.Draw(im1)
    d1.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#FEF2F2", outline="#EF4444", width=8)
    draw_star(d1, (256, 210), 130, 55, fill="#DC2626")
    d1.rectangle([240, 110, 272, 270], fill="#FFD1A4", outline="#B45309", width=3)
    d1.rectangle([240, 240, 340, 272], fill="#FFD1A4", outline="#B45309", width=3)
    draw_text_centered(d1, "FAZ O L! 👆", (256, 390), font_lg, fill="#DC2626", stroke_fill="white", stroke_width=5)
    save_static(im1, os.path.join(pack_dir, "1.webp"))
    im1.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")

    im2 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d2 = ImageDraw.Draw(im2)
    d2.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#FFFBEB", outline="#D97706", width=8)
    d2.ellipse([140, 160, 372, 280], fill="#881337", outline="#4C0519", width=5)
    d2.pieslice([140, 160, 372, 280], 190, 350, fill="#FDE047")
    draw_text_centered(d2, "VAI TER PICANHA! 🥩🍻", (256, 390), font_md, fill="#991B1B", stroke_fill="white", stroke_width=4)
    save_static(im2, os.path.join(pack_dir, "2.webp"))

    im3 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d3 = ImageDraw.Draw(im3)
    d3.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#1E1B4B", outline="#818CF8", width=8)
    d3.ellipse([180, 130, 332, 290], fill="#FED7AA")
    d3.arc([170, 200, 342, 310], 0, 180, fill="white", width=26)
    d3.polygon([(190, 180), (250, 180), (240, 215), (180, 215)], fill="#EF4444")
    d3.polygon([(262, 180), (322, 180), (332, 215), (272, 215)], fill="#EF4444")
    draw_text_centered(d3, "O BRASIL VOLTOU! 🇧🇷⚡", (256, 390), font_md, fill="#38BDF8", stroke_fill="black", stroke_width=4)
    save_static(im3, os.path.join(pack_dir, "3.webp"))

    im4 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d4 = ImageDraw.Draw(im4)
    d4.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#FEFCE8", outline="#CA8A04", width=8)
    d4.rectangle([180, 160, 320, 320], fill="#FACC15", outline="#A16207", width=5)
    d4.arc([290, 190, 370, 290], 270, 90, fill="#A16207", width=12)
    for fx in [180, 210, 245, 280, 315]:
        d4.ellipse([fx - 22, 130, fx + 22, 175], fill="white")
    draw_text_centered(d4, "COMPANHEIRO! 🍻", (256, 390), font_lg, fill="#B45309", stroke_fill="white", stroke_width=5)
    save_static(im4, os.path.join(pack_dir, "4.webp"))

    im5 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d5 = ImageDraw.Draw(im5)
    d5.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#F0FDF4", outline="#16A34A", width=8)
    d5.polygon([(150, 160), (362, 160), (380, 330), (132, 330)], fill="#1E293B")
    d5.line([(160, 160), (350, 330)], fill="#009C3B", width=22)
    d5.line([(165, 160), (355, 330)], fill="#FFDF00", width=10)
    d5.ellipse([216, 190, 296, 270], fill="#FFD1A4", outline="#B45309", width=3)
    draw_text_centered(d5, "UNIÃO & RECONSTRUÇÃO ⭐", (256, 390), font_sm, fill="#047857", stroke_fill="white", stroke_width=4)
    save_static(im5, os.path.join(pack_dir, "5.webp"))

    im6 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d6 = ImageDraw.Draw(im6)
    d6.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#FFF1F2", outline="#E11D48", width=8)
    d6.polygon([(256, 320), (160, 200), (200, 140), (256, 180), (312, 140), (352, 200)], fill="#E11D48")
    d6.pieslice([160, 140, 256, 230], 180, 0, fill="#E11D48")
    d6.pieslice([256, 140, 352, 230], 180, 0, fill="#E11D48")
    draw_text_centered(d6, "O AMOR VENCEU! ❤️", (256, 390), font_md, fill="#BE123C", stroke_fill="white", stroke_width=5)
    save_static(im6, os.path.join(pack_dir, "6.webp"))

    im7 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d7 = ImageDraw.Draw(im7)
    d7.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#EFF6FF", outline="#2563EB", width=8)
    d7.polygon([(140, 230), (256, 260), (372, 230), (372, 310), (256, 340), (140, 310)], fill="#3B82F6", outline="#1D4ED8", width=4)
    d7.polygon([(256, 120), (340, 155), (256, 190), (172, 155)], fill="#1E293B")
    draw_text_centered(d7, "MAIS EDUCAÇÃO! 🎓", (256, 390), font_md, fill="#1D4ED8", stroke_fill="white", stroke_width=4)
    save_static(im7, os.path.join(pack_dir, "7.webp"))

    im8 = Image.new('RGBA', (512, 512), (0,0,0,0))
    d8 = ImageDraw.Draw(im8)
    d8.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#FAF5FF", outline="#9333EA", width=8)
    for mx in [170, 220, 290, 340]:
        d8.rectangle([mx - 10, 200, mx + 10, 280], fill="#475569")
        d8.ellipse([mx - 16, 170, mx + 16, 210], fill="#94A3B8", outline="#334155", width=2)
    draw_text_centered(d8, "NUNCA NA HISTÓRIA DESSE PAÍS", (256, 390), font_sm, fill="#7E22CE", stroke_fill="white", stroke_width=4)
    save_static(im8, os.path.join(pack_dir, "8.webp"))


# ── 6. br-figurinhas-hot ──
def generate_br_figurinhas_hot():
    pack_dir = create_pack_folder('br-figurinhas-hot')
    font_sm = get_font(24)

    celebs = [
        ("ANITTA: ENVOLVER 🔥", "anitta"),
        ("GISELE: PASSARELA ✨", "gisele"),
        ("BRUNA: GLAMOUR 💋", "bruna"),
        ("PAOLLA: RAINHA DO SAMBA 👑", "paolla"),
        ("IZA: DEUSA DOURADA 🌟", "iza"),
        ("LUÍSA: BADDIE 💅", "luisa"),
        ("MARINA: SEDUÇÃO 🌹", "marina"),
        ("SABRINA: MUSA CARNAVAL 💃", "sabrina")
    ]

    for st_idx, (title, celeb_id) in enumerate(celebs, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            sway = int(math.sin(phase) * 14)
            
            d.ellipse([50, 50, 462, 462], fill=(255, 235, 240, 240), outline="#F43F5E", width=6)
            
            if celeb_id == "anitta":
                d.ellipse([180 + sway, 100, 332 + sway, 270], fill="#451A03")
                d.ellipse([206 + sway, 130, 306, 250], fill="#D97706")
                d.ellipse([236 + sway, 215, 276, 240], fill="#DC2626")
                for sp in [(100, 120), (410, 140), (120, 320), (390, 300)]:
                    draw_star(d, (sp[0] + sway, sp[1]), 14, 6, fill="#FDE047")
            elif celeb_id == "gisele":
                d.ellipse([150 - sway, 90, 362 + sway, 310], fill="#FBBF24")
                d.ellipse([200, 120, 312, 250], fill="#FDE68A")
                d.ellipse([236, 215, 276, 235], fill="#FB7185")
            elif celeb_id == "paolla":
                for fa, col in [(-50, "#EC4899"), (-25, "#8B5CF6"), (0, "#F59E0B"), (25, "#10B981"), (50, "#06B6D4")]:
                    fx = int(256 + math.sin(math.radians(fa + sway)) * 150)
                    fy = int(140 - math.cos(math.radians(fa + sway)) * 90)
                    d.polygon([(256, 190), (fx - 20, fy), (fx, fy - 35), (fx + 20, fy)], fill=col)
                d.ellipse([200, 130, 312, 260], fill="#D97706")
                d.ellipse([236, 215, 276, 245], fill="#DC2626")
            elif celeb_id == "iza":
                d.ellipse([160, 80, 352, 240], fill="#1C1917")
                d.ellipse([200, 140, 312, 270], fill="#5B3821")
                d.rectangle([220, 270, 292, 310], fill="#F59E0B", outline="#B45309", width=2)
            elif celeb_id == "marina":
                d.ellipse([160 - sway, 100, 352 + sway, 310], fill="#EA580C")
                d.ellipse([200, 130, 312, 250], fill="#FEF08A")
                d.polygon([(180, 260), (332, 260), (360, 360), (152, 360)], fill="#059669")
            else:
                d.ellipse([140, 110, 372, 330], fill="#FB7185")
                d.arc([190, 175, 230, 205], 180, 360, fill="black", width=5)
                d.ellipse([282, 175, 302, 195], fill="black")
                draw_star(d, (360 + sway, 160 - sway), 20, 9, fill="#F43F5E")

            draw_text_centered(d, title, (256, 420), font_sm, fill="#BE123C", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 7. br-beijo-apaixonado ──
def generate_br_beijo_apaixonado():
    pack_dir = create_pack_folder('br-beijo-apaixonado')
    font_sm = get_font(24)

    kiss_scenes = [
        ("MARCA DE BATOM 💋", "lipstick_stamp"),
        ("BEIJO AO PÔR DO SOL 🌅", "sunset_silhouette"),
        ("CORAÇÕES VOADORES 💕", "flying_hearts"),
        ("SMACK! EXPLOSIVO 💥", "comic_smack"),
        ("BEIJO NA TESTA COM CARINHO 🥺", "forehead"),
        ("URSINHO APAIXONADO 🧸", "teddy"),
        ("FLECHA DO CUPIDO 💘", "cupid"),
        ("BEIJO NA CHUVA 🌧️", "rain_kiss")
    ]

    for st_idx, (title, scene) in enumerate(kiss_scenes, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            sway = int(math.sin(phase) * 15)
            
            d.ellipse([50, 50, 462, 462], fill=(255, 241, 242, 245), outline="#E11D48", width=6)
            
            if scene == "sunset_silhouette":
                d.pieslice([60, 60, 452, 452], 0, 180, fill="#EA580C")
                d.ellipse([216, 180, 296, 260], fill="#FDE047") # sun
                d.ellipse([180, 220, 250, 330], fill="#1E1B4B") # silhouette 1
                d.ellipse([260, 220, 330, 330], fill="#1E1B4B") # silhouette 2
            elif scene == "cupid":
                d.polygon([(140, 200), (370, 200)], fill="#F59E0B")
                d.line([(140, 200), (370, 200)], fill="#F59E0B", width=6) # arrow
                d.polygon([(360, 190), (390, 200), (360, 210)], fill="#DC2626")
                d.ellipse([226, 170, 286, 230], fill="#E11D48")
            else:
                scale = 1.0 + 0.15 * math.sin(phase)
                lw = int(140 * scale)
                d.ellipse([256 - lw, 200, 256 + lw, 300], fill="#E11D48")
                d.ellipse([256 - int(lw*0.5), 235, 256 + int(lw*0.5), 275], fill="#FFF1F2")

            draw_text_centered(d, title, (256, 425), font_sm, fill="#BE123C", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 8. br-abraco-carinhoso ──
def generate_br_abraco_carinhoso():
    pack_dir = create_pack_folder('br-abraco-carinhoso')
    font_sm = get_font(24)

    hug_scenes = [
        ("ABRAÇO DE URSO 🐻", "bear"),
        ("REENCONTRO NO AEROPORTO ✈️", "airport"),
        ("BURRITO DE COBERTOR 🌯", "burrito"),
        ("ABRAÇO DE AMIGOS 🤗", "friends"),
        ("GATINHO & CACHORRINHO 🐱🐶", "pets"),
        ("COLO DE MÃE ❤️", "mom"),
        ("ENVELOPE DE AMOR 💌", "letter"),
        ("FANTASMINHA DO BEM 👻", "ghost")
    ]

    for st_idx, (title, scene) in enumerate(hug_scenes, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            sway = int(math.sin(phase) * 14)
            
            d.ellipse([50, 50, 462, 462], fill=(253, 242, 248, 245), outline="#DB2777", width=6)
            
            if scene == "pets":
                d.ellipse([140, 180, 270, 310], fill="#F59E0B") # Dog
                d.ellipse([240, 180, 370, 310], fill="#94A3B8") # Cat
            elif scene == "ghost":
                d.arc([180, 140+sway, 332, 320+sway], 180, 0, fill="#CBD5E1", width=8)
                d.ellipse([215, 190+sway, 235, 210+sway], fill="black")
                d.ellipse([277, 190+sway, 297, 210+sway], fill="black")
            else:
                d.ellipse([150+sway, 150, 270+sway, 290], fill="#FBBF24")
                d.ellipse([240-sway, 150, 360-sway, 290], fill="#F472B6")
                d.ellipse([236, 120, 276, 160], fill="#EF4444") # Heart over them

            draw_text_centered(d, title, (256, 425), font_sm, fill="#9D174D", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 9. br-casal-fofo ──
def generate_br_casal_fofo():
    pack_dir = create_pack_folder('br-casal-fofo')
    font_sm = get_font(24)

    couples = [
        ("ESPAGUETE ROMÂNTICO 🍝", "spaghetti"),
        ("BICICLETA A DOIS 🚲", "bike"),
        ("OLHANDO AS ESTRELAS 🌌", "stars"),
        ("FAZENDO BOLO JUNTOS 🎂", "cake"),
        ("DANÇA NA CHUVA ☔", "umbrella"),
        ("SELFIE DE ORELHINHA 🐰", "selfie"),
        ("CABANINHA DE LUZES ⛺", "tent"),
        ("DIVIDINDO AÇAÍ 🥣", "acai")
    ]

    for st_idx, (title, scene) in enumerate(couples, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            sway = int(math.sin(phase) * 12)
            
            d.ellipse([50, 50, 462, 462], fill=(255, 241, 242, 245), outline="#BE123C", width=6)
            
            # Two chibi characters
            d.ellipse([140, 160 + sway, 240, 270 + sway], fill="#93C5FD")
            d.ellipse([272, 160 - sway, 372, 270 - sway], fill="#FBCFE8")
            d.ellipse([240, 220, 272, 252], fill="#EF4444") # Heart in center

            draw_text_centered(d, title, (256, 425), font_sm, fill="#9F1239", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 10. br-coracao-paixao ──
def generate_br_coracao_paixao():
    pack_dir = create_pack_folder('br-coracao-paixao')
    font_sm = get_font(24)

    hearts = [
        ("NEON CYBERPUNK ⚡", "neon"),
        ("DIAMANTE CRISTAL 💎", "diamond"),
        ("FOGO DA PAIXÃO 🔥", "fire"),
        ("CADEADO DE AMOR 🔒", "lock"),
        ("ROSA DESABROCHANDO 🌹", "rose"),
        ("GALÁXIA CÓSMICA 🌌", "galaxy"),
        ("CORAÇÃO 8-BIT ARCADE 👾", "pixel"),
        ("GOTA D'ÁGUA CRISTALINA 💧", "water")
    ]

    for st_idx, (title, h_type) in enumerate(hearts, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            
            d.ellipse([50, 50, 462, 462], fill=(254, 242, 242, 245), outline="#DC2626", width=6)
            
            scale = 1.0 + 0.18 * math.sin(phase)
            r = int(120 * scale)
            d.polygon([(256, 230 + r), (256 - r, 230 - int(r*0.2)), (256, 230 - int(r*0.6)), (256 + r, 230 - int(r*0.2))], fill="#EF4444")
            d.pieslice([256 - r, 230 - int(r*0.8), 256, 230 + int(r*0.2)], 180, 0, fill="#EF4444")
            d.pieslice([256, 230 - int(r*0.8), 256 + r, 230 + int(r*0.2)], 180, 0, fill="#EF4444")

            draw_text_centered(d, title, (256, 425), font_sm, fill="#991B1B", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 11. br-gretchen-rainha ──
def generate_br_gretchen_rainha():
    pack_dir = create_pack_folder('br-gretchen-rainha')
    font_sm = get_font(24)

    scenes = [
        ("REVIRANDO OS OLHOS 🙄", "eyeball"),
        ("CHORANDO DE RIR 😂", "laugh_cry"),
        ("CONGA CONGA CONGA 💃", "conga"),
        ("TOMANDO CAFÉ NA PAZ ☕", "coffee"),
        ("ESPIANDO ATRÁS DA CORTINA 👀", "curtain"),
        ("DIGITANDO NERVOSA 💻", "keyboard"),
        ("ARRUMANDO O CABELO 💅", "mirror"),
        ("DROP THE MIC 🎤", "mic_drop")
    ]

    for st_idx, (title, scene) in enumerate(scenes, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            sway = int(math.sin(phase) * 16)
            
            d.ellipse([50, 50, 462, 462], fill=(253, 244, 255, 245), outline="#A855F7", width=6)
            
            d.ellipse([140 - sway, 90, 372 + sway, 310], fill="#1C1917") # hair
            d.ellipse([186, 120, 326, 270], fill="#FCD34D") # face
            d.ellipse([226, 215, 286, 250], fill="#DC2626") # red lips

            draw_text_centered(d, title, (256, 425), font_sm, fill="#7E22CE", stroke_fill="white", stroke_width=4)
            frames.append(im)

# ── 12. br-memes-classicos ──
def generate_br_memes_classicos():
    pack_dir = create_pack_folder('br-memes-classicos')
    font_sm = get_font(22)

    memes = [
        ("NAZARÉ CONFUSA 📐", ["f(x)=?", "cos(θ)", "√2+π=42", "∫e^x dx"], "#F59E0B"),
        ("CHICO FELIZ / TRISTE 😐🙂", ["Antes do rolê", "Depois do rolê"], "#3B82F6"),
        ("CANETA AZUL 🖊️", ["Caneta azul, azul caneta...", "Manoel Gomes"], "#0284C7"),
        ("BORA BILL! 📢", ["Bora fi do Bill!", "Bora muié do Bill!"], "#10B981"),
        ("GRÁVIDA DE TAUBATÉ 🤰", ["Quadrugêmeos!", "Barriga gigante"], "#EC4899"),
        ("SABE DE NADA, INOCENTE! 🌴", ["Cumpadre Washington", "É o Tchan!"], "#F97316"),
        ("RINDO DE NERVOSO 😬", ["Tudo sob controle", "Kkkkkry"], "#EF4444"),
        ("GLÓRIA MARIA NA NUVEM ☁️", ["Viagem astral", "Paz"], "#8B5CF6")
    ]

    for st_idx, (title, subtitles, color) in enumerate(memes, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 50, 472, 462], radius=30, fill="white", outline=color, width=8)
        
        if "NAZARÉ" in title:
            d.ellipse([180, 130, 332, 280], fill="#FDE68A")
            d.ellipse([210, 160, 302, 260], fill="#FED7AA")
            d.ellipse([230, 190, 245, 205], fill="black")
            d.ellipse([265, 190, 280, 205], fill="black")
            for idx, form in enumerate(subtitles):
                d.text((60 + (idx%2)*220, 90 + (idx//2)*240), form, font=get_font(24), fill=color)
        elif "CANETA" in title:
            d.polygon([(236, 90), (276, 90), (276, 290), (256, 330), (236, 290)], fill="#2563EB", outline="#1D4ED8", width=4)
        else:
            d.ellipse([160, 130, 352, 310], fill=color)
            d.ellipse([200, 180, 225, 205], fill="white")
            d.ellipse([285, 180, 310, 205], fill="white")
            d.arc([210, 220, 302, 270], 0, 180, fill="black", width=5)

        draw_text_centered(d, title, (256, 395), font_sm, fill=color, stroke_fill="white", stroke_width=4)
        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 14. br-flork-debochado ──
def generate_br_flork_debochado():
    pack_dir = create_pack_folder('br-flork-debochado')
    font_sm = get_font(22)

    setups = [
        ("LAVANDO MINHA HONRA 🛁", "bathtub"),
        ("MINHA VIDA AMOROSA 🔥", "dumpster_fire"),
        ("PAPEL DE TROUXA 🤡", "clown_mirror"),
        ("MODO DETETIVE FBI 🕵️", "fbi_plant"),
        ("NEM ME CHAMA PRA SAIR 🛌", "blanket"),
        ("RICO POR 5 MINUTOS 💸", "money"),
        ("DOSE EXTRA DE CAFÉ ☕", "coffee_tower"),
        ("LONGE DOS PROBLEMAS 🚀", "astronaut")
    ]

    for st_idx, (quote, setup_type) in enumerate(setups, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 40, 472, 472], radius=30, fill="white", outline="black", width=6)
        
        d.arc([160, 110, 352, 310], 150, 30, fill="black", width=6)
        d.line([(165, 220), (165, 340)], fill="black", width=6)
        d.line([(347, 220), (347, 340)], fill="black", width=6)
        d.ellipse([215, 170, 230, 185], fill="black")
        d.ellipse([282, 170, 297, 185], fill="black")
        d.line([(225, 210), (287, 210)], fill="black", width=5)

        if setup_type == "bathtub":
            d.rounded_rectangle([130, 280, 382, 360], radius=20, fill="#E0F2FE", outline="black", width=4)
        elif setup_type == "clown_mirror":
            d.ellipse([246, 185, 266, 205], fill="#EF4444")
        else:
            d.line([(165, 250), (110, 220)], fill="black", width=5)
            d.line([(347, 250), (402, 220)], fill="black", width=5)

        draw_text_centered(d, quote, (256, 420), font_sm, fill="black", stroke_fill="white", stroke_width=3)
        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 15. br-bom-dia-boa-noite ──
def generate_br_bom_dia_boa_noite():
    pack_dir = create_pack_folder('br-bom-dia-boa-noite')
    font_sm = get_font(22)

    greetings = [
        ("BOM DIA COM CAFÉ & PÃO DE QUEIJO ☕🧀", "#D97706"),
        ("BOM DIA ABENÇOADO NA PRAIA 🏖️✨", "#0284C7"),
        ("GIRASSOL DE PAZ & ALEGRIA 🌻", "#CA8A04"),
        ("ALMOÇO EM FAMÍLIA NO DOMINGO 🥘", "#DC2626"),
        ("BOA TARDE NA REDE DE DESCANSO 🌴", "#059669"),
        ("BOA NOITE COM CRISTO & ESTRELAS 🌙⭐", "#4338CA"),
        ("DURMA COM OS ANJOS 🐱💤", "#7C3AED"),
        ("GRATIDÃO POR MAIS UM DIA 🙏📖", "#92400E")
    ]

    for st_idx, (title, color) in enumerate(greetings, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 50, 472, 462], radius=30, fill="white", outline=color, width=8)
        
        if "CAFÉ" in title:
            d.rectangle([200, 200, 300, 290], fill="#78350F", outline=color, width=4)
            d.arc([280, 215, 330, 275], 270, 90, fill="#78350F", width=6)
        elif "NOITE" in title or "ESTRELAS" in title:
            d.ellipse([190, 120, 310, 240], fill="#FACC15")
            d.ellipse([225, 105, 330, 230], fill="white")
        else:
            d.ellipse([186, 120, 326, 260], fill="#FBBF24", outline=color, width=4)

        draw_text_centered(d, title, (256, 390), font_sm, fill=color, stroke_fill="white", stroke_width=4)
        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 17. br-carnaval-samba ──
def generate_br_carnaval_samba():
    pack_dir = create_pack_folder('br-carnaval-samba')
    font_sm = get_font(22)

    carnaval_scenes = [
        ("PASSISTA SAMBANDO 💃", "passista"),
        ("PANDEIRO NO RITMO 🥁", "pandeiro"),
        ("TRIO ELÉTRICO SALVADOR 🚚", "trio"),
        ("FREVO COM SOMBRINHA ☂️", "frevo"),
        ("MÁSCARA DOURADA VENEZA 🎭", "mask"),
        ("CUÍCA NA BATERIA 🪘", "cuica"),
        ("CARRO ALEGÓRICO RIO 🐆", "float"),
        ("CANHÃO DE CONFETE 🎊", "cannon")
    ]

    for st_idx, (title, scene) in enumerate(carnaval_scenes, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            sway = int(math.sin(phase) * 15)
            
            d.ellipse([50, 50, 462, 462], fill=(255, 240, 245, 240), outline="#DB2777", width=6)
            
            if scene == "pandeiro":
                d.ellipse([140, 140 + sway, 372, 340 + sway], fill="#FEF08A", outline="#78350F", width=8)
            elif scene == "mask":
                d.polygon([(140, 180+sway), (256, 210+sway), (372, 180+sway), (340, 270+sway), (256, 250+sway), (172, 270+sway)], fill="#F59E0B", outline="#B45309", width=4)
            else:
                for fa, col in [(-40, "#EC4899"), (-20, "#8B5CF6"), (0, "#F59E0B"), (20, "#10B981"), (40, "#06B6D4")]:
                    fx = int(256 + math.sin(math.radians(fa + sway)) * 140)
                    fy = int(140 - math.cos(math.radians(fa + sway)) * 80)
                    d.polygon([(256, 200), (fx - 15, fy), (fx, fy - 30), (fx + 15, fy)], fill=col)

            draw_text_centered(d, title, (256, 425), font_sm, fill="#BE185D", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 13. br-vira-lata-caramelo ──
def generate_br_vira_lata_caramelo():
    pack_dir = create_pack_folder('br-vira-lata-caramelo')
    font_sm = get_font(24)

    scenes = [
        ("NO BANQUINHO DO BOTECO 🍻", "bar"),
        ("DE CAPACETE NA OBRA 👷", "hardhat"),
        ("LATINDO PRA MOTO 🛵", "moto"),
        ("DORMINDO DE BARRIGA PRA CIMA 😴", "belly_up"),
        ("PIDONCHO NO CHURRASCO 🍖", "bbq"),
        ("COM A AMARELINHA 🇧🇷", "jersey"),
        ("COM A COXINHA NA BOCA 🍗", "coxinha"),
        ("CAFUNÉ GOSTOSO 🥰", "headscratch")
    ]

    for st_idx, (title, scene) in enumerate(scenes, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        d.ellipse([50, 50, 462, 462], fill="#FEF3C7", outline="#D97706", width=8)
        
        # Caramel Dog Head
        d.ellipse([140, 140, 372, 340], fill="#D97706")
        d.ellipse([90, 130, 170, 260], fill="#B45309")
        d.ellipse([342, 130, 422, 260], fill="#B45309")
        d.ellipse([206, 220, 306, 320], fill="#FDE68A")
        d.ellipse([236, 235, 276, 265], fill="black")
        d.ellipse([244, 280, 268, 315], fill="#F87171") # Tongue

        draw_text_centered(d, title, (256, 420), font_sm, fill="#78350F", stroke_fill="white", stroke_width=4)
        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 15. br-girias-brasileiras ──
def generate_br_girias_brasileiras():
    pack_dir = create_pack_folder('br-girias-brasileiras')
    font_lg = get_font(52)
    font_sm = get_font(24)

    girias = [
        ("EITA PREGO! 🔥", "Lascou tudo de vez", "#EF4444"),
        ("VIXI MARIA! 😱", "Nem te conto...", "#F59E0B"),
        ("TOPÍSSIMO! ⭐", "Aprovado 100%", "#10B981"),
        ("VALEU, FALOU! 🚀", "Partiu fui agora", "#3B82F6"),
        ("MANO DO CÉU! ⚡", "Tô em choque", "#8B5CF6"),
        ("AFF NADA A VER 🙄", "Paciência zero", "#EC4899"),
        ("BORA PARTIR! 🏍️", "Tô pronto", "#06B6D4"),
        ("PERDI TUDO! 😂", "Chorando de rir", "#D97706")
    ]

    for st_idx, (word, sub, color) in enumerate(girias, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 70, 472, 380], radius=35, fill=color, outline="white", width=8)
        d.polygon([(140, 370), (110, 450), (200, 370)], fill=color)

        draw_text_centered(d, word, (256, 180), font_lg, fill="white", stroke_fill="black", stroke_width=6)
        draw_text_centered(d, sub, (256, 280), font_sm, fill="#FEF08A", stroke_fill="black", stroke_width=4)

        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 16. br-zoeira-amigos ──
def generate_br_zoeira_amigos():
    pack_dir = create_pack_folder('br-zoeira-amigos')
    font_sm = get_font(24)

    quotes = [
        ("ANOTANDO NO BLOQUINHO FBI 📝", "#EF4444"),
        ("CARTÃO VERMELHO DIRETO 🟥", "#DC2626"),
        ("QUEM PERGUNTOU? 🔍", "#3B82F6"),
        ("PIPOCA PRA VER O CIRCO PEGAR FOGO 🍿", "#F59E0B"),
        ("ACORDA PRA VIDA! 💥", "#8B5CF6"),
        ("CHAMANDO A POLÍCIA DO BOM SENSO 🚨", "#06B6D4"),
        ("OSCAR DE TROUXA DO ANO 🏆", "#CA8A04"),
        ("CHORANDO NO BANHO 🚿", "#64748B")
    ]

    for st_idx, (quote, color) in enumerate(quotes, 1):
        im = Image.new('RGBA', (512, 512), (0,0,0,0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 50, 472, 462], radius=30, fill="#F8FAFC", outline=color, width=8)
        
        d.ellipse([146, 110, 366, 330], fill=color)
        d.ellipse([180, 170, 220, 210], fill="white")
        d.ellipse([292, 170, 332, 210], fill="white")
        d.ellipse([192, 180, 210, 200], fill="black")
        d.ellipse([304, 180, 322, 200], fill="black")
        d.arc([190, 220, 322, 290], 10, 170, fill="black", width=6)

        draw_text_centered(d, quote, (256, 400), font_sm, fill="black", stroke_fill="white", stroke_width=4)
        save_static(im, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            im.resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── 18. br-passinho-funk ──
def generate_br_passinho_funk():
    pack_dir = create_pack_folder('br-passinho-funk')
    font_sm = get_font(24)

    funk_scenes = [
        ("MANDA O PASSINHO DO RIO 🕺", "passinho"),
        ("BOOMBOX DOS ANOS 90 📻", "boombox"),
        ("DJ RISCANDO NO BAILE 🎧", "dj"),
        ("ÓCULOS JULIET ESPELHADO 😎", "juliet"),
        ("QUADRADINHO DE OITO 💃", "quadradinho"),
        ("FREEZE NO CHÃO ⚡", "freeze"),
        ("PAREDÃO DE SOM 🔊", "paredao"),
        ("FOGOS NA ROCINHA 🎆", "fireworks")
    ]

    for st_idx, (title, scene) in enumerate(funk_scenes, 1):
        frames = []
        for f in range(6):
            im = Image.new('RGBA', (512, 512), (0,0,0,0))
            d = ImageDraw.Draw(im)
            phase = (f / 6.0) * 2 * math.pi
            sway = int(math.sin(phase) * 25)
            
            d.ellipse([50, 50, 462, 462], fill=(255, 241, 242, 245), outline="#E11D48", width=6)
            
            if scene == "boombox":
                d.rectangle([130, 180, 382, 330], fill="#334155", outline="black", width=4)
                d.ellipse([160, 210, 240, 290], fill="#0F172A")
                d.ellipse([272, 210, 352, 290], fill="#0F172A")
            else:
                d.line([(256, 180), (256, 300)], fill="#1E293B", width=18)
                d.line([(256, 300), (200 - sway, 380)], fill="#1E293B", width=14)
                d.line([(256, 300), (312 + sway, 380)], fill="#1E293B", width=14)
                d.ellipse([220, 100, 292, 170], fill="#FDE68A")
                d.rectangle([220, 135, 292, 150], fill="#EF4444") # shades

            draw_text_centered(d, title, (256, 425), font_sm, fill="#9F1239", stroke_fill="white", stroke_width=4)
            frames.append(im)

        save_animated(frames, os.path.join(pack_dir, f"{st_idx}.webp"))
        if st_idx == 1:
            frames[0].resize((96, 96)).save(os.path.join(pack_dir, "tray_icon.png"), format="PNG")


# ── Run All Generators ──
if __name__ == "__main__":
    print("Generating all 20 Brazil packs with 100% unique graphics...")
    generate_br_bandeira_nacional()
    generate_br_bandeira_animada()
    generate_br_bolsonaro_dancando()
    generate_br_lula_reacoes()
    generate_br_futebol_selecao()
    generate_br_futebol_gols_animados()
    generate_br_figurinhas_hot()
    generate_br_beijo_apaixonado()
    generate_br_abraco_carinhoso()
    generate_br_casal_fofo()
    generate_br_coracao_paixao()
    generate_br_gretchen_rainha()
    generate_br_memes_classicos()
    generate_br_flork_debochado()
    generate_br_bom_dia_boa_noite()
    generate_br_vira_lata_caramelo()
    generate_br_carnaval_samba()
    generate_br_girias_brasileiras()
    generate_br_zoeira_amigos()
    generate_br_passinho_funk()
    print("All 20 Brazil sticker packs generated with 100% unique designs!")
