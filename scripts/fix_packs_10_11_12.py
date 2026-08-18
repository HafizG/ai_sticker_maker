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

def extract_pure_transparent_sticker(img_path):
    bgr = cv2.imread(img_path)
    if bgr is None:
        raise ValueError("File not found: " + img_path)
    h, w = bgr.shape[:2]
    
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    
    bg_candidates = (sat < 15)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bg_candidates.astype(np.uint8) * 255)
    
    outer_bg = np.zeros((h, w), dtype=bool)
    for label in range(1, num_labels):
        x, y, comp_w, comp_h, area = stats[label]
        if x == 0 or y == 0 or (x + comp_w >= w) or (y + comp_h >= h):
            outer_bg |= (labels == label)
            
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilated_bg = cv2.dilate(outer_bg.astype(np.uint8), kernel)
    
    alpha = np.ones((h, w), dtype=np.uint8) * 255
    alpha[dilated_bg > 0] = 0
    
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[alpha == 0] = [0, 0, 0, 0]
    
    pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    return pil_img

def render_diecut_sticker(draw_func):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    draw_func(d, canvas)
    
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

def make_static_webp(pil_img, out_path, banner_text="", banner_color="#0284C7"):
    canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    pil_img_c = pil_img.copy()
    pil_img_c.thumbnail((470, 440), Image.Resampling.LANCZOS)
    
    ox = (512 - pil_img_c.width) // 2
    oy = (440 - pil_img_c.height) // 2 + 10
    canvas.paste(pil_img_c, (ox, oy), pil_img_c)
    
    if banner_text:
        d = ImageDraw.Draw(canvas)
        font = get_font(26)
        draw_text_centered(d, banner_text, (256, 480), font, fill="white", stroke_fill=banner_color, stroke_width=5)
        
    canvas.save(out_path, format="WEBP", lossless=True)
    return canvas

def make_tray(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((88, 88), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

# ══════════════════════════════════════════════════
# 1. FIX PACK 10: br-futebol-selecao
# ══════════════════════════════════════════════════
print("Processing Pack 10: br-futebol-selecao...")
pack_dir_10 = os.path.join(PACKS_BASE_DIR, 'br-futebol-selecao')
os.makedirs(pack_dir_10, exist_ok=True)

# 1. Pelé
pele_p = os.path.join(ARTIFACT_DIR, "pele_king_sticker_1786904558814.jpg")
c_pele = extract_pure_transparent_sticker(pele_p)
f10 = make_static_webp(c_pele, os.path.join(pack_dir_10, "1.webp"), "PELÉ: O REI DO FUTEBOL 👑", "#0284C7")
make_tray(f10, os.path.join(pack_dir_10, "tray_icon.png"))
print("Pack 10: Generated 1.webp")

# 2. Neymar
neymar_p = os.path.join(ARTIFACT_DIR, "neymar_celebrating_sticker_1786903904919.jpg")
c_neymar = extract_pure_transparent_sticker(neymar_p)
make_static_webp(c_neymar, os.path.join(pack_dir_10, "2.webp"), "NEYMAR JR GOL! ⚡⚽", "#0284C7")
print("Pack 10: Generated 2.webp")

players_rest = [
    ("BAILA VINI JR! 🕺", "vini"),
    ("RONALDINHO GAÚCHO 🤙", "r10"),
    ("RONALDO R9 FENÔMENO ⚽", "r9"),
    ("MARTA: 6X MELHOR DO MUNDO 🌟", "marta"),
    ("AYRTON SENNA DO BRASIL 🏎️", "senna"),
    ("PRUUU! DANÇA DO POMBO 🐦", "richarlison"),
]

for idx, (title, scene_id) in enumerate(players_rest, 3):
    def draw_player(d, c, s=scene_id):
        d.ellipse([260, 480, 764, 980], fill="#FFDF00", outline="#009C3B", width=12) # Jersey
        d.ellipse([340, 200, 684, 560], fill="#78350F" if s in ["vini", "r10"] else "#D97706")
        if s == "senna":
            d.ellipse([300, 160, 724, 600], fill="#FFDF00", outline="#B45309", width=12)
            d.rectangle([300, 320, 724, 380], fill="#009C3B")
            d.rectangle([300, 380, 724, 440], fill="#002776")
            d.rounded_rectangle([380, 280, 644, 440], radius=30, fill="#0F172A", outline="white", width=6)
        elif s == "r10":
            d.ellipse([260, 160, 764, 680], fill="#1C1917")
            d.rectangle([340, 260, 684, 300], fill="white", outline="black", width=4)
        elif s == "r9":
            d.ellipse([420, 180, 604, 260], fill="#1C1917")
        elif s == "richarlison":
            d.ellipse([380, 180, 644, 280], fill="#F8FAFC")
        elif s == "marta":
            for star_i in range(6):
                sx = 280 + star_i * 90
                d.polygon([(sx, 120), (sx+8, 140), (sx+30, 145), (sx+14, 160), (sx+18, 185), (sx, 170), (sx-18, 185), (sx-14, 160), (sx-30, 145), (sx-8, 140)], fill="#F59E0B")
        draw_text_centered(d, "7" if s=="vini" else "10" if s=="r10" else "9" if s=="r9" else "BRA", (512, 700), get_font(72), fill="#002776")
    cutout = render_diecut_sticker(draw_player)
    make_static_webp(cutout, os.path.join(pack_dir_10, f"{idx}.webp"), title, "#0284C7")
    print(f"Pack 10: Generated {idx}.webp")

print("Pack 10 (br-futebol-selecao) finished successfully!\n")

# ══════════════════════════════════════════════════
# 2. FIX PACK 11: br-bom-dia-boa-noite
# ══════════════════════════════════════════════════
print("Processing Pack 11: br-bom-dia-boa-noite...")
pack_dir_11 = os.path.join(PACKS_BASE_DIR, 'br-bom-dia-boa-noite')
os.makedirs(pack_dir_11, exist_ok=True)

coffee_p = os.path.join(ARTIFACT_DIR, "bom_dia_coffee_sticker_1786903861596.jpg")
c_coffee = extract_pure_transparent_sticker(coffee_p)
f11 = make_static_webp(c_coffee, os.path.join(pack_dir_11, "1.webp"), "BOM DIA COM CAFÉ & PÃO DE QUEIJO ☕🧀", "#D97706")
make_tray(f11, os.path.join(pack_dir_11, "tray_icon.png"))
print("Pack 11: Generated 1.webp")

greetings_rest = [
    ("BOM DIA ABENÇOADO NA PRAIA 🏖️✨", "beach"),
    ("GIRASSOL DE PAZ & ALEGRIA 🌻", "sunflower"),
    ("ALMOÇO EM FAMÍLIA NO DOMINGO 🥘", "bbq"),
    ("BOA TARDE NA REDE 🌴", "hammock"),
    ("BOA NOITE COM O CRISTO 🌙⭐", "christ"),
    ("DURMA COM OS ANJOS 🐱💤", "kitten"),
    ("GRATIDÃO POR MAIS UM DIA 🙏📖", "bible"),
]

for idx, (title, scene_id) in enumerate(greetings_rest, 2):
    def draw_greeting(d, c, s=scene_id):
        if s == "beach":
            d.pieslice([180, 200, 844, 864], 180, 360, fill="#F59E0B")
            d.chord([120, 500, 904, 1100], 180, 360, fill="#0284C7")
        elif s == "sunflower":
            d.ellipse([340, 340, 684, 684], fill="#78350F")
            for a in range(0, 360, 30):
                px = int(512 + math.cos(math.radians(a)) * 260)
                py = int(512 + math.sin(math.radians(a)) * 260)
                d.ellipse([px-60, py-60, px+60, py+60], fill="#FDE047", outline="#CA8A04", width=4)
        elif s == "christ":
            d.ellipse([300, 200, 724, 624], fill="#FACC15")
            d.line([(512, 340), (512, 800)], fill="white", width=40)
            d.line([(280, 420), (744, 420)], fill="white", width=30)
        elif s == "bible":
            d.polygon([(240, 480), (512, 540), (784, 480), (784, 780), (512, 840), (240, 780)], fill="#FEF08A", outline="#78350F", width=8)
            d.rectangle([480, 260, 544, 480], fill="#DC2626")
            d.ellipse([496, 180, 528, 260], fill="#F59E0B")
        else:
            d.ellipse([300, 300, 724, 724], fill="#CA8A04")
    cutout = render_diecut_sticker(draw_greeting)
    make_static_webp(cutout, os.path.join(pack_dir_11, f"{idx}.webp"), title, "#D97706")
    print(f"Pack 11: Generated {idx}.webp")

print("Pack 11 (br-bom-dia-boa-noite) finished successfully!\n")

# ══════════════════════════════════════════════════
# 3. FIX PACK 12: br-zoeira-amigos
# ══════════════════════════════════════════════════
print("Processing Pack 12: br-zoeira-amigos...")
pack_dir_12 = os.path.join(PACKS_BASE_DIR, 'br-zoeira-amigos')
os.makedirs(pack_dir_12, exist_ok=True)

zoeira_items = [
    ("ANOTANDO NO BLOQUINHO FBI 📝", "#EF4444"),
    ("CARTÃO VERMELHO DIRETO 🟥", "#DC2626"),
    ("QUEM PERGUNTOU? 🔍", "#3B82F6"),
    ("PIPOCA PRA VER O CIRCO PEGAR FOGO 🍿", "#F59E0B"),
    ("ACORDA PRA VIDA! 💥", "#8B5CF6"),
    ("CHAMANDO A POLÍCIA DO BOM SENSO 🚨", "#06B6D4"),
    ("OSCAR DE TROUXA DO ANO 🏆", "#CA8A04"),
    ("CHORANDO NO BANHO 🚿", "#64748B"),
]

for idx, (title, color) in enumerate(zoeira_items, 1):
    def draw_zoeira(d, c, col=color):
        d.ellipse([240, 240, 784, 784], fill=col)
        d.ellipse([340, 360, 440, 460], fill="white")
        d.ellipse([584, 360, 684, 460], fill="white")
        d.ellipse([370, 390, 420, 440], fill="black")
        d.ellipse([614, 390, 664, 440], fill="black")
        d.arc([380, 520, 644, 660], 0, 180, fill="black", width=12)
    cutout = render_diecut_sticker(draw_zoeira)
    out_webp = os.path.join(pack_dir_12, f"{idx}.webp")
    f_res = make_static_webp(cutout, out_webp, title, color)
    if idx == 1:
        make_tray(f_res, os.path.join(pack_dir_12, "tray_icon.png"))
    print(f"Pack 12: Generated {idx}.webp")

print("Pack 12 (br-zoeira-amigos) finished successfully!")
