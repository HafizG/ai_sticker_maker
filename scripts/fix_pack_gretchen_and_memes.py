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

def make_animated_webp(pil_img, out_path, banner_text, stroke_color="#7E22CE"):
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

def make_static_webp(pil_img, out_path, banner_text, banner_color="#D97706"):
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
# 1. FIX PACK 6: br-gretchen-rainha
# ══════════════════════════════════════════════════
print("Processing Pack 6: br-gretchen-rainha...")
pack_dir_6 = os.path.join(PACKS_BASE_DIR, 'br-gretchen-rainha')
os.makedirs(pack_dir_6, exist_ok=True)

gretchen_p1 = os.path.join(ARTIFACT_DIR, "gretchen_laughing_1786903694400.jpg")
c1 = extract_pure_transparent_sticker(gretchen_p1)
f1 = make_animated_webp(c1, os.path.join(pack_dir_6, "1.webp"), "GRETCHEN RINDO 😂", "#7E22CE")
make_tray(f1, os.path.join(pack_dir_6, "tray_icon.png"))
print("Pack 6: Generated 1.webp")

gretchen_scenes = [
    ("TOMANDO CAFÉ NA PAZ ☕", "coffee"),
    ("REVIRANDO OS OLHOS 🙄", "eyeball"),
    ("CONGA CONGA CONGA 💃", "conga"),
    ("CHORANDO COM ÓCULOS 😭", "cry"),
    ("DIGITANDO NERVOSA 💻", "keyboard"),
    ("ESPIANDO NA CORTINA 👀", "curtain"),
    ("DROP THE MIC 🎤", "mic"),
]

for idx, (title, scene_id) in enumerate(gretchen_scenes, 2):
    def draw_gretchen(d, c, s=scene_id):
        d.ellipse([260, 480, 764, 940], fill="#E11D48") # Red sequins
        d.ellipse([320, 180, 704, 680], fill="#1C1917") # Black hair
        d.ellipse([360, 260, 664, 600], fill="#FCD34D") # Face
        if s == "coffee":
            d.rectangle([580, 480, 720, 640], fill="#78350F", outline="#B45309", width=6)
            d.arc([680, 500, 760, 620], 270, 90, fill="#B45309", width=12)
        elif s == "eyeball":
            d.ellipse([420, 360, 480, 420], fill="white")
            d.ellipse([544, 360, 604, 420], fill="white")
            d.ellipse([440, 360, 465, 385], fill="black")
            d.ellipse([564, 360, 589, 385], fill="black")
        elif s == "cry":
            d.rectangle([400, 370, 490, 430], fill="#0F172A", outline="#E2E8F0", width=4)
            d.rectangle([534, 370, 624, 430], fill="#0F172A", outline="#E2E8F0", width=4)
            d.line([(490, 395), (534, 395)], fill="#0F172A", width=6)
            d.ellipse([435, 450, 455, 480], fill="#38BDF8")
            d.ellipse([569, 450, 589, 480], fill="#38BDF8")
        elif s == "keyboard":
            d.polygon([(300, 680), (724, 680), (800, 840), (224, 840)], fill="#94A3B8", outline="#334155", width=6)
        elif s == "mic":
            d.rectangle([500, 540, 524, 720], fill="#475569")
            d.ellipse([480, 460, 544, 550], fill="#94A3B8")
        else:
            d.rectangle([400, 370, 490, 430], fill="#0F172A")
            d.rectangle([534, 370, 624, 430], fill="#0F172A")
        d.ellipse([450, 480, 574, 530], fill="#BE123C") # Red lips
    cutout = render_diecut_sticker(draw_gretchen)
    make_animated_webp(cutout, os.path.join(pack_dir_6, f"{idx}.webp"), title, "#7E22CE")
    print(f"Pack 6: Generated {idx}.webp")

print("Pack 6 (br-gretchen-rainha) finished successfully!\n")

# ══════════════════════════════════════════════════
# 2. FIX PACK 7: br-memes-classicos
# ══════════════════════════════════════════════════
print("Processing Pack 7: br-memes-classicos...")
pack_dir_7 = os.path.join(PACKS_BASE_DIR, 'br-memes-classicos')
os.makedirs(pack_dir_7, exist_ok=True)

memes = [
    ("NAZARÉ CONFUSA 📐", "nazare"),
    ("CHICO FELIZ / TRISTE 😐🙂", "chico"),
    ("CANETA AZUL 🖊️", "caneta"),
    ("BORA BILL! 📢", "bill"),
    ("GRÁVIDA DE TAUBATÉ 🤰", "gravida"),
    ("SABE DE NADA, INOCENTE! 🌴", "inocente"),
    ("RINDO DE NERVOSO 😬", "nervoso"),
    ("GLÓRIA MARIA NA NUVEM ☁️", "gloria")
]

for idx, (title, scene_id) in enumerate(memes, 1):
    def draw_meme(d, c, s=scene_id):
        d.ellipse([260, 320, 764, 820], fill="#FED7AA") # Face
        if s == "nazare":
            d.ellipse([240, 240, 784, 720], fill="#FDE047") # Blond hair
            for f_text, (fx, fy) in [("f(x)=?", (260, 280)), ("cos(θ)", (660, 300)), ("√2+π", (260, 600)), ("∫e^x", (660, 600))]:
                d.text((fx, fy), f_text, font=get_font(36), fill="#D97706")
        elif s == "caneta":
            d.polygon([(460, 160), (564, 160), (564, 680), (512, 780), (460, 680)], fill="#2563EB", outline="#1D4ED8", width=8)
            d.rectangle([480, 120, 544, 160], fill="#1E3A8A")
        elif s == "bill":
            d.polygon([(520, 420), (780, 320), (780, 540)], fill="#10B981", outline="black", width=6)
        elif s == "gravida":
            d.ellipse([280, 560, 744, 940], fill="#EC4899")
        else:
            d.ellipse([380, 420, 460, 480], fill="black")
            d.ellipse([564, 420, 644, 480], fill="black")
            d.arc([420, 540, 604, 620], 0, 180, fill="black", width=8)
    cutout = render_diecut_sticker(draw_meme)
    out_webp = os.path.join(pack_dir_7, f"{idx}.webp")
    f_res = make_static_webp(cutout, out_webp, title, "#F59E0B")
    if idx == 1:
        make_tray(f_res, os.path.join(pack_dir_7, "tray_icon.png"))
    print(f"Pack 7: Generated {idx}.webp")

print("Pack 7 (br-memes-classicos) finished successfully!")
