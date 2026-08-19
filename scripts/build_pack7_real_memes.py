import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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

def make_static_webp(pil_img, out_path, banner_text, banner_color="#D97706"):
    canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    pil_img_c = pil_img.copy()
    pil_img_c.thumbnail((470, 430), Image.Resampling.LANCZOS)
    
    ox = (512 - pil_img_c.width) // 2
    oy = (430 - pil_img_c.height) // 2 + 10
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
# BUILD 10 REAL PHOTOREALISTIC BRAZILIAN MEME STICKERS
# ══════════════════════════════════════════════════
print("Building 10 Real Photorealistic Brazilian Meme Stickers for Pack 7...")
pack_dir_7 = os.path.join(PACKS_BASE_DIR, 'br-memes-classicos')
os.makedirs(pack_dir_7, exist_ok=True)

meme_files = [
    ("meme_nazare_confusa_1787149933746.jpg", "NAZARÉ CONFUSA 🤔📐", "#D97706"),
    ("meme_chico_buarque_1787149976771.jpg", "CHICO FELIZ / TRISTE 🎭", "#0284C7"),
    ("meme_caneta_azul_1787150033288.jpg", "CANETA AZUL, AZUL CANETA 🖊️", "#2563EB"),
    ("meme_bora_bill_1787150092527.jpg", "BORA BILL! 📢⚽", "#DC2626"),
    ("meme_gravida_taubate_1787150199257.jpg", "GRÁVIDA DE TAUBATÉ 🤰👗", "#059669"),
    ("meme_compadre_washington_1787150259979.jpg", "SABE DE NADA, INOCENTE! ☝️", "#D97706"),
    ("meme_rindo_nervoso_1787150321117.jpg", "RINDO DE NERVOSO 😅", "#475569"),
    ("meme_gloria_maria_1787150390049.jpg", "GLÓRIA MARIA EM CHOQUE 😱🎢", "#047857"),
    ("meme_faustao_1787150456657.jpg", "Ô LOCO MEU! ERROU! 🎙️", "#1E3A8A"),
    ("meme_ines_brasil_1787150517831.jpg", "GRAÇAS A DEUS! 🙌✨", "#BE185D"),
]

for idx, (fname, title, color) in enumerate(meme_files, 1):
    fpath = os.path.join(ARTIFACT_DIR, fname)
    cutout = extract_pure_transparent_sticker(fpath)
    out_webp = os.path.join(pack_dir_7, f"{idx}.webp")
    f_res = make_static_webp(cutout, out_webp, title, color)
    if idx == 1:
        make_tray(f_res, os.path.join(pack_dir_7, "tray_icon.png"))
    print(f"Pack 7: Generated Real Photo Meme {idx}.webp -> {fname}")

print("\nPack 7 (br-memes-classicos) finished successfully with 10 REAL PHOTOREALISTIC meme stickers!")
