import os
import math
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PACKS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', 'packs')
MASTER_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', '_master.json')
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

def convert_pack_to_static(pack_name, banner_color="#BE123C"):
    pack_dir = os.path.join(PACKS_BASE_DIR, pack_name)
    if not os.path.exists(pack_dir):
        return
    webps = [f for f in os.listdir(pack_dir) if f.endswith('.webp') and f != 'tray_icon.webp']
    for w_file in sorted(webps, key=lambda x: int(x.split('.')[0])):
        w_path = os.path.join(pack_dir, w_file)
        im = Image.open(w_path)
        im.seek(0)
        frame0 = im.copy().convert('RGBA')
        frame0.save(w_path, format="WEBP", lossless=True)
    print(f"Converted {pack_name} to static WebP stickers.")

# ══════════════════════════════════════════════════
# 1. MAKE PREVIOUS 5 PACKS STATIC
# ══════════════════════════════════════════════════
static_packs = [
    "br-figurinhas-hot",
    "br-beijo-apaixonado",
    "br-abraco-carinhoso",
    "br-casal-fofo",
    "br-coracao-paixao",
]

for p in static_packs:
    convert_pack_to_static(p)

# Update _master.json animated flags for previous 5 packs
with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
    master_data = json.load(f)

for p in static_packs:
    if p in master_data["packs"]:
        master_data["packs"][p]["animated_sticker_pack"] = False

master_data["packs"]["br-gretchen-rainha"]["animated_sticker_pack"] = True

with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=2, ensure_ascii=False)

print("Updated _master.json flags for static packs and animated Gretchen.")

# ══════════════════════════════════════════════════
# 2. BUILD 10 ANIMATED STICKERS FOR br-gretchen-rainha
# ══════════════════════════════════════════════════
print("Building 10 Animated Stickers for br-gretchen-rainha...")
pack_dir_6 = os.path.join(PACKS_BASE_DIR, 'br-gretchen-rainha')
os.makedirs(pack_dir_6, exist_ok=True)

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

def make_tray(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((88, 88), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

# 1. Gretchen Laughing Photo (Animated Laugh Bounce)
p1 = os.path.join(ARTIFACT_DIR, "gretchen_laughing_1786903694400.jpg")
c1 = extract_pure_transparent_sticker(p1)
frames_1 = []
for f in range(6):
    phase = (f / 6.0) * 2 * math.pi
    canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    # Bouncing laugh movement
    dy = int(math.sin(phase) * 12)
    c1_c = c1.copy()
    c1_c.thumbnail((450, 410), Image.Resampling.LANCZOS)
    canvas.paste(c1_c, ((512 - c1_c.width)//2, (410 - c1_c.height)//2 + 15 + dy), c1_c)
    d = ImageDraw.Draw(canvas)
    draw_text_centered(d, "GRETCHEN RINDO 😂", (256, 475), get_font(26), fill="#FEF08A", stroke_fill="#7E22CE", stroke_width=5)
    # Ha ha ha laugh text popping
    if f % 2 == 0:
        d.text((360, 60), "HA!", font=get_font(32), fill="#FDE047", stroke_fill="black", stroke_width=4)
    else:
        d.text((80, 80), "HAHA!", font=get_font(32), fill="#FDE047", stroke_fill="black", stroke_width=4)
    frames_1.append(canvas)

frames_1[0].save(os.path.join(pack_dir_6, "1.webp"), format="WEBP", save_all=True, append_images=frames_1[1:], duration=120, loop=0, lossless=False, quality=90)
make_tray(frames_1[0], os.path.join(pack_dir_6, "tray_icon.png"))
print("Pack 6: Generated 1.webp")

# Gretchen animated scenes definitions
gretchen_anim_scenes = [
    ("TOMANDO CAFÉ NA PAZ ☕", "coffee"),
    ("REVIRANDO OS OLHOS 🙄", "eyeball"),
    ("CONGA CONGA CONGA 💃", "conga"),
    ("CHORANDO COM ÓCULOS 😭", "cry"),
    ("DIGITANDO NERVOSA 💻", "keyboard"),
    ("ESPIANDO NA CORTINA 👀", "curtain"),
    ("DROP THE MIC 🎤", "mic"),
    ("DEUSA DA INTERNET 🌟", "queen"),
    ("CHAMA NO DEBOCHE 💅", "sassy"),
]

for idx, (title, scene_id) in enumerate(gretchen_anim_scenes, 2):
    frames = []
    for f in range(6):
        phase = (f / 6.0) * 2 * math.pi
        
        def draw_gretchen_frame(d, c, s=scene_id, fr=f, ph=phase):
            # Sway/movement
            sway = int(math.sin(ph) * 15)
            # Body & Sequins Dress
            d.ellipse([260 + sway, 480, 764 + sway, 940], fill="#E11D48")
            # Voluminous black hair
            d.ellipse([320 + sway, 180, 704 + sway, 680], fill="#1C1917")
            # Face
            d.ellipse([360 + sway, 260, 664 + sway, 600], fill="#FCD34D")
            
            if s == "coffee":
                # Steaming cup moves up to mouth
                cup_y = 520 - int(abs(math.sin(ph)) * 30)
                d.rectangle([560 + sway, cup_y, 700 + sway, cup_y + 140], fill="#78350F", outline="#B45309", width=6)
                d.arc([660 + sway, cup_y + 20, 740 + sway, cup_y + 120], 270, 90, fill="#B45309", width=10)
                # Animated steam
                d.line([(600 + sway, cup_y - 20 - fr*4), (620 + sway, cup_y - 40 - fr*4)], fill="#E2E8F0", width=4)
                d.rectangle([400 + sway, 370, 490 + sway, 430], fill="#0F172A")
                d.rectangle([534 + sway, 370, 624 + sway, 430], fill="#0F172A")
            elif s == "eyeball":
                # Animated rolling eyeballs
                d.ellipse([420 + sway, 360, 480 + sway, 420], fill="white")
                d.ellipse([544 + sway, 360, 604 + sway, 420], fill="white")
                pupil_y = int(370 + math.cos(ph) * 15)
                d.ellipse([440 + sway, pupil_y, 465 + sway, pupil_y + 20], fill="black")
                d.ellipse([564 + sway, pupil_y, 589 + sway, pupil_y + 20], fill="black")
            elif s == "conga":
                # Side to side conga dance
                d.rectangle([400 + sway, 370, 490 + sway, 430], fill="#0F172A")
                d.rectangle([534 + sway, 370, 624 + sway, 430], fill="#0F172A")
                # Music notes moving
                ny = 140 - fr * 12
                d.text((700, ny), "🎵", font=get_font(42), fill="#EC4899")
            elif s == "cry":
                d.rectangle([400 + sway, 370, 490 + sway, 430], fill="#0F172A", outline="#E2E8F0", width=4)
                d.rectangle([534 + sway, 370, 624 + sway, 430], fill="#0F172A", outline="#E2E8F0", width=4)
                d.line([(490 + sway, 395), (534 + sway, 395)], fill="#0F172A", width=6)
                # Falling tears
                tear_y = 440 + (fr * 18) % 100
                d.ellipse([435 + sway, tear_y, 455 + sway, tear_y + 30], fill="#38BDF8")
                d.ellipse([569 + sway, tear_y, 589 + sway, tear_y + 30], fill="#38BDF8")
            elif s == "keyboard":
                # Furious typing hands moving up and down
                d.polygon([(300, 680), (724, 680), (800, 840), (224, 840)], fill="#94A3B8", outline="#334155", width=6)
                hand_l = 660 if fr % 2 == 0 else 640
                hand_r = 640 if fr % 2 == 0 else 660
                d.ellipse([340, hand_l, 440, hand_l + 80], fill="#FCD34D")
                d.ellipse([584, hand_r, 684, hand_r + 80], fill="#FCD34D")
                d.rectangle([400 + sway, 370, 490 + sway, 430], fill="#0F172A")
                d.rectangle([534 + sway, 370, 624 + sway, 430], fill="#0F172A")
            elif s == "curtain":
                # Curtain sliding back and forth
                curt_w = int(240 + math.sin(ph) * 40)
                d.rectangle([140, 200, 140 + curt_w, 900], fill="#BE123C", outline="#881337", width=8)
                d.rectangle([884 - curt_w, 200, 884, 900], fill="#BE123C", outline="#881337", width=8)
                d.rectangle([400 + sway, 370, 490 + sway, 430], fill="#0F172A")
                d.rectangle([534 + sway, 370, 624 + sway, 430], fill="#0F172A")
            elif s == "mic":
                # Dropping mic downwards
                mic_y = 520 + fr * 25
                d.rectangle([500, mic_y, 524, mic_y + 120], fill="#475569")
                d.ellipse([480, mic_y - 30, 544, mic_y + 40], fill="#94A3B8")
                d.rectangle([400 + sway, 370, 490 + sway, 430], fill="#0F172A")
                d.rectangle([534 + sway, 370, 624 + sway, 430], fill="#0F172A")
            elif s == "queen":
                # Golden crown with pulsating glowing stars
                d.polygon([(360+sway, 240), (420+sway, 120), (512+sway, 200), (604+sway, 120), (664+sway, 240)], fill="#F59E0B", outline="#B45309", width=6)
                d.rectangle([400 + sway, 370, 490 + sway, 430], fill="#0F172A")
                d.rectangle([534 + sway, 370, 624 + sway, 430], fill="#0F172A")
                # Pulsating sparkle star
                star_sz = 15 + (fr % 3) * 12
                sx, sy = 512 + sway, 100
                d.polygon([(sx, sy-star_sz), (sx+5, sy-5), (sx+star_sz, sy), (sx+5, sy+5), (sx, sy+star_sz), (sx-5, sy+5), (sx-star_sz, sy), (sx-5, sy-5)], fill="#FEF08A")
            else: # sassy
                d.rectangle([400 + sway, 370, 490 + sway, 430], fill="#0F172A")
                d.rectangle([534 + sway, 370, 624 + sway, 430], fill="#0F172A")
                # Sparkling nail polish hand waving
                hand_y = 460 - (fr * 10) % 40
                d.ellipse([640 + sway, hand_y, 740 + sway, hand_y + 80], fill="#FCD34D")
                # Polish sparkles
                d.ellipse([720 + sway, hand_y - 10, 740 + sway, hand_y + 10], fill="#EC4899")
                
            d.ellipse([450 + sway, 480, 574 + sway, 530], fill="#BE123C") # Red lips
            
        stk_frame = render_diecut_sticker(draw_gretchen_frame)
        canvas_f = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        stk_frame.thumbnail((450, 410), Image.Resampling.LANCZOS)
        canvas_f.paste(stk_frame, ((512 - stk_frame.width)//2, (410 - stk_frame.height)//2 + 15), stk_frame)
        d_f = ImageDraw.Draw(canvas_f)
        draw_text_centered(d_f, title, (256, 475), get_font(26), fill="#FEF08A", stroke_fill="#7E22CE", stroke_width=5)
        frames.append(canvas_f)
        
    out_webp = os.path.join(pack_dir_6, f"{idx}.webp")
    frames[0].save(out_webp, format="WEBP", save_all=True, append_images=frames[1:], duration=120, loop=0, lossless=False, quality=90)
    print(f"Pack 6: Generated Animated {idx}.webp")

print("Pack 6 (br-gretchen-rainha) finished successfully with 10 animated stickers!")
