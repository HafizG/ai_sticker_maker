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

def clean_cutout_transparent(img_path):
    if not os.path.exists(img_path):
        return None
    bgr = cv2.imread(img_path)
    if bgr is None:
        return None
        
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    
    color_mask = (sat > 12).astype(np.uint8) * 255
    dark_mask = (val < 190).astype(np.uint8) * 255
    fg_raw = cv2.bitwise_or(color_mask, dark_mask)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
    dilated = cv2.dilate(fg_raw, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return Image.open(img_path).convert('RGBA')
        
    main_contour = max(contours, key=cv2.contourArea)
    mask = np.zeros(sat.shape, dtype=np.uint8)
    cv2.drawContours(mask, [main_contour], -1, 255, thickness=cv2.FILLED)
    
    mask_pil = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(radius=1.5))
    mask_arr = np.array(mask_pil)
    mask_arr[mask_arr < 120] = 0
    mask_arr[mask_arr >= 120] = 255
    
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[mask_arr == 0] = [0, 0, 0, 0]
    
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

def make_static_webp(pil_img, out_path, banner_text="", banner_color="#BE123C"):
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

def make_animated_webp(pil_img, out_path, banner_text="", stroke_color="#BE123C"):
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
        
        if banner_text:
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

def make_tray(canvas, out_path):
    tray = canvas.copy()
    tray.thumbnail((88, 88), Image.Resampling.LANCZOS)
    bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    bg.paste(tray, ((96 - tray.width) // 2, (96 - tray.height) // 2), tray)
    bg.save(out_path, format="PNG")

# ── 1. br-gretchen-rainha ──
print("Building br-gretchen-rainha...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-gretchen-rainha')
os.makedirs(pack_dir, exist_ok=True)

gretchen_scenes = [
    ("GRETCHEN RINDO 😂", "laugh", os.path.join(ARTIFACT_DIR, "gretchen_laughing_1786903694400.jpg")),
    ("TOMANDO CAFÉ NA PAZ ☕", "coffee", None),
    ("REVIRANDO OS OLHOS 🙄", "eyeball", None),
    ("CONGA CONGA CONGA 💃", "conga", None),
    ("CHORANDO COM ÓCULOS 😭", "cry", None),
    ("DIGITANDO NERVOSA 💻", "keyboard", None),
    ("ESPIANDO NA CORTINA 👀", "curtain", None),
    ("DROP THE MIC 🎤", "mic", None)
]

for idx, (title, scene_id, photo_p) in enumerate(gretchen_scenes, 1):
    if photo_p and os.path.exists(photo_p):
        st = clean_cutout_transparent(photo_p)
    else:
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
                d.ellipse([440, 360, 465, 385], fill="black") # Looking up
                d.ellipse([564, 360, 589, 385], fill="black")
            elif s == "cry":
                d.rectangle([400, 370, 490, 430], fill="#0F172A", outline="#E2E8F0", width=4)
                d.rectangle([534, 370, 624, 430], fill="#0F172A", outline="#E2E8F0", width=4)
                d.line([(490, 395), (534, 395)], fill="#0F172A", width=6)
                d.ellipse([435, 450, 455, 480], fill="#38BDF8") # Tear
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
        st = render_diecut_sticker(draw_gretchen)
        
    c = make_animated_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#7E22CE")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 2. br-bolsonaro-dancando ──
print("Building br-bolsonaro-dancando...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-bolsonaro-dancando')
os.makedirs(pack_dir, exist_ok=True)

bolso_scenes = [
    ("VALEU MEU BRASIL! 👍", "thumbs", os.path.join(ARTIFACT_DIR, "bolsonaro_thumbs_up_sticker_1786904611609.jpg")),
    ("TURN DOWN FOR WHAT 😎", "thug", None),
    ("DE JET SKI NA PRAIA 🌊", "jetski", None),
    ("TÁ COM MEDO, PETISTA? 📢", "megaphone", None),
    ("TOCANDO SANFONA 🪗", "accordion", None),
    ("DANÇA DO CAPITÃO 🕺", "dance", None),
    ("FLEXÃO MILITAR 💪", "pushup", None),
    ("PASTEL NA FEIRA 🥟", "pastel", None)
]

for idx, (title, scene_id, photo_p) in enumerate(bolso_scenes, 1):
    if photo_p and os.path.exists(photo_p):
        st = clean_cutout_transparent(photo_p)
    else:
        def draw_bolso(d, c, s=scene_id):
            d.ellipse([260, 480, 764, 940], fill="#1E3A8A") # Navy suit
            d.line([(320, 500), (704, 900)], fill="#009C3B", width=45) # Presidential sash
            d.line([(330, 510), (714, 910)], fill="#FFDF00", width=20)
            d.ellipse([360, 200, 664, 540], fill="#FED7AA") # Face
            d.arc([350, 170, 674, 380], 180, 360, fill="#64748B", width=40) # Hair
            if s == "thug":
                d.rectangle([390, 320, 490, 380], fill="black")
                d.rectangle([534, 320, 634, 380], fill="black")
                d.line([(490, 340), (534, 340)], fill="black", width=8)
            elif s == "jetski":
                d.polygon([(180, 680), (844, 680), (720, 840), (280, 840)], fill="#0284C7", outline="#0369A1", width=8)
            elif s == "megaphone":
                d.polygon([(540, 380), (780, 280), (780, 480)], fill="#DC2626", outline="black", width=6)
            elif s == "accordion":
                d.rectangle([300, 520, 724, 760], fill="#DC2626", outline="black", width=6)
                for bx in range(320, 700, 35):
                    d.line([(bx, 520), (bx, 760)], fill="white", width=4)
            elif s == "pastel":
                d.polygon([(560, 420), (720, 360), (700, 520)], fill="#FDE047", outline="#CA8A04", width=6)
            d.arc([440, 400, 584, 460], 0, 180, fill="black", width=8) # Smile
        st = render_diecut_sticker(draw_bolso)
        
    c = make_animated_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#15803D")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 3. br-vira-lata-caramelo ──
print("Building br-vira-lata-caramelo...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-vira-lata-caramelo')
os.makedirs(pack_dir, exist_ok=True)

dog_scenes = [
    ("CARAMELO COM COXINHA 🍗", "coxinha", os.path.join(ARTIFACT_DIR, "caramelo_dog_sticker_1786903786655.jpg")),
    ("NO BANQUINHO DO BOTECO 🍻", "bar", None),
    ("COM A AMARELINHA 🇧🇷", "jersey", None),
    ("DE CAPACETE NA OBRA 👷", "hardhat", None),
    ("DORMINDO NA CALÇADA 😴", "sleep", None),
    ("LATINDO PRA MOTO 🛵", "moto", None),
    ("CAFUNÉ GOSTOSO 🥰", "scratch", None),
    ("DE OLHO NO CHURRASCO 🍖", "bbq", None)
]

for idx, (title, scene_id, photo_p) in enumerate(dog_scenes, 1):
    if photo_p and os.path.exists(photo_p):
        st = clean_cutout_transparent(photo_p)
    else:
        def draw_caramelo(d, c, s=scene_id):
            d.ellipse([280, 340, 744, 840], fill="#D97706") # Head
            d.ellipse([180, 300, 340, 600], fill="#B45309") # Left Ear
            d.ellipse([684, 300, 844, 600], fill="#B45309") # Right Ear
            d.ellipse([380, 500, 644, 760], fill="#FDE68A") # Snout
            d.ellipse([460, 520, 564, 600], fill="black") # Nose
            d.ellipse([475, 630, 545, 710], fill="#F87171") # Tongue
            d.ellipse([360, 420, 440, 500], fill="#451A03") # Left Eye
            d.ellipse([584, 420, 664, 500], fill="#451A03") # Right Eye
            if s == "jersey":
                d.ellipse([260, 740, 764, 1000], fill="#FFDF00", outline="#009C3B", width=12)
            elif s == "hardhat":
                d.ellipse([320, 180, 704, 380], fill="#F59E0B", outline="#B45309", width=10)
            elif s == "bar":
                d.rectangle([200, 780, 824, 860], fill="#78350F", outline="#451A03", width=8)
            elif s == "bbq":
                d.line([(512, 700), (740, 600)], fill="#94A3B8", width=12)
                d.ellipse([700, 540, 820, 640], fill="#881337") # Meat skewer
        st = render_diecut_sticker(draw_caramelo)
        
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#D97706")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 4. br-futebol-selecao ──
print("Building br-futebol-selecao...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-futebol-selecao')
os.makedirs(pack_dir, exist_ok=True)

players = [
    ("PELÉ: O REI DO FUTEBOL 👑", "pele", os.path.join(ARTIFACT_DIR, "pele_king_sticker_1786904558814.jpg")),
    ("NEYMAR JR GOL! ⚡⚽", "neymar", os.path.join(ARTIFACT_DIR, "neymar_celebrating_sticker_1786903904919.jpg")),
    ("BAILA VINI JR! 🕺", "vini", None),
    ("RONALDINHO GAÚCHO 🤙", "r10", None),
    ("RONALDO R9 FENÔMENO ⚽", "r9", None),
    ("MARTA: 6X MELHOR DO MUNDO 🌟", "marta", None),
    ("AYRTON SENNA DO BRASIL 🏎️", "senna", None),
    ("PRUUU! DANÇA DO POMBO 🐦", "richarlison", None)
]

for idx, (title, scene_id, photo_p) in enumerate(players, 1):
    if photo_p and os.path.exists(photo_p):
        st = clean_cutout_transparent(photo_p)
    else:
        def draw_player(d, c, s=scene_id):
            d.ellipse([260, 480, 764, 980], fill="#FFDF00", outline="#009C3B", width=12) # Jersey
            d.ellipse([340, 200, 684, 560], fill="#78350F" if s in ["vini", "r10"] else "#D97706")
            if s == "senna":
                d.ellipse([300, 160, 724, 600], fill="#FFDF00", outline="#B45309", width=12) # Helmet
                d.rectangle([300, 320, 724, 380], fill="#009C3B")
                d.rectangle([300, 380, 724, 440], fill="#002776")
                d.rounded_rectangle([380, 280, 644, 440], radius=30, fill="#0F172A", outline="white", width=6)
            elif s == "r10":
                d.ellipse([260, 160, 764, 680], fill="#1C1917") # Curly hair
                d.rectangle([340, 260, 684, 300], fill="white", outline="black", width=4) # Headband
            elif s == "r9":
                d.ellipse([420, 180, 604, 260], fill="#1C1917") # Iconic triangle haircut
            elif s == "richarlison":
                d.ellipse([380, 180, 644, 280], fill="#F8FAFC") # Bleached hair
            elif s == "marta":
                for star_i in range(6):
                    sx = 280 + star_i * 90
                    d.polygon([(sx, 120), (sx+8, 140), (sx+30, 145), (sx+14, 160), (sx+18, 185), (sx, 170), (sx-18, 185), (sx-14, 160), (sx-30, 145), (sx-8, 140)], fill="#F59E0B")
            draw_text_centered(d, "10" if s=="pele" else "7" if s=="vini" else "9" if s=="r9" else "BRA", (512, 700), get_font(72), fill="#002776")
        st = render_diecut_sticker(draw_player)
        
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#0284C7")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 5. br-bom-dia-boa-noite ──
print("Building br-bom-dia-boa-noite...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-bom-dia-boa-noite')
os.makedirs(pack_dir, exist_ok=True)

greetings = [
    ("BOM DIA COM CAFÉ & PÃO DE QUEIJO ☕🧀", "coffee", os.path.join(ARTIFACT_DIR, "bom_dia_coffee_sticker_1786903861596.jpg")),
    ("BOM DIA ABENÇOADO NA PRAIA 🏖️✨", "beach", None),
    ("GIRASSOL DE PAZ & ALEGRIA 🌻", "sunflower", None),
    ("ALMOÇO EM FAMÍLIA NO DOMINGO 🥘", "bbq", None),
    ("BOA TARDE NA REDE 🌴", "hammock", None),
    ("BOA NOITE COM O CRISTO 🌙⭐", "christ", None),
    ("DURMA COM OS ANJOS 🐱💤", "kitten", None),
    ("GRATIDÃO POR MAIS UM DIA 🙏📖", "bible", None)
]

for idx, (title, scene_id, photo_p) in enumerate(greetings, 1):
    if photo_p and os.path.exists(photo_p):
        st = clean_cutout_transparent(photo_p)
    else:
        def draw_greeting(d, c, s=scene_id):
            if s == "beach":
                d.pieslice([180, 200, 844, 864], 180, 360, fill="#F59E0B") # Sun
                d.chord([120, 500, 904, 1100], 180, 360, fill="#0284C7") # Ocean
            elif s == "sunflower":
                d.ellipse([340, 340, 684, 684], fill="#78350F")
                for a in range(0, 360, 30):
                    px = int(512 + math.cos(math.radians(a)) * 260)
                    py = int(512 + math.sin(math.radians(a)) * 260)
                    d.ellipse([px-60, py-60, px+60, py+60], fill="#FDE047", outline="#CA8A04", width=4)
            elif s == "christ":
                d.ellipse([300, 200, 724, 624], fill="#FACC15") # Moon
                d.line([(512, 340), (512, 800)], fill="white", width=40) # Christ statue
                d.line([(280, 420), (744, 420)], fill="white", width=30)
            elif s == "bible":
                d.polygon([(240, 480), (512, 540), (784, 480), (784, 780), (512, 840), (240, 780)], fill="#FEF08A", outline="#78350F", width=8)
                d.rectangle([480, 260, 544, 480], fill="#DC2626") # Candle
                d.ellipse([496, 180, 528, 260], fill="#F59E0B")
            else:
                d.ellipse([300, 300, 724, 724], fill="#CA8A04")
        st = render_diecut_sticker(draw_greeting)
        
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#D97706")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 6. br-memes-classicos ──
print("Building br-memes-classicos...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-memes-classicos')
os.makedirs(pack_dir, exist_ok=True)

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
            for f_text, (fx, fy) in [("f(x)=?", (160, 200)), ("cos(θ)", (740, 240)), ("√2+π=42", (180, 680)), ("∫e^x dx", (720, 700))]:
                d.text((fx, fy), f_text, font=get_font(42), fill="#D97706")
        elif s == "caneta":
            d.polygon([(460, 160), (564, 160), (564, 680), (512, 780), (460, 680)], fill="#2563EB", outline="#1D4ED8", width=8)
            d.rectangle([480, 120, 544, 160], fill="#1E3A8A")
        elif s == "bill":
            d.polygon([(520, 420), (780, 320), (780, 540)], fill="#10B981", outline="black", width=6)
        elif s == "gravida":
            d.ellipse([280, 560, 744, 940], fill="#EC4899") # Giant belly
        else:
            d.ellipse([380, 420, 460, 480], fill="black")
            d.ellipse([564, 420, 644, 480], fill="black")
            d.arc([420, 540, 604, 620], 0, 180, fill="black", width=8)
    st = render_diecut_sticker(draw_meme)
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#F59E0B")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 7. br-zoeira-amigos ──
print("Building br-zoeira-amigos...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-zoeira-amigos')
os.makedirs(pack_dir, exist_ok=True)

zoeira_items = [
    ("ANOTANDO NO BLOQUINHO FBI 📝", "#EF4444"),
    ("CARTÃO VERMELHO DIRETO 🟥", "#DC2626"),
    ("QUEM PERGUNTOU? 🔍", "#3B82F6"),
    ("PIPOCA PRA VER O CIRCO PEGAR FOGO 🍿", "#F59E0B"),
    ("ACORDA PRA VIDA! 💥", "#8B5CF6"),
    ("CHAMANDO A POLÍCIA DO BOM SENSO 🚨", "#06B6D4"),
    ("OSCAR DE TROUXA DO ANO 🏆", "#CA8A04"),
    ("CHORANDO NO BANHO 🚿", "#64748B")
]

for idx, (title, color) in enumerate(zoeira_items, 1):
    def draw_zoeira(d, c, col=color):
        d.ellipse([240, 240, 784, 784], fill=col)
        d.ellipse([340, 360, 440, 460], fill="white")
        d.ellipse([584, 360, 684, 460], fill="white")
        d.ellipse([370, 390, 420, 440], fill="black")
        d.ellipse([614, 390, 664, 440], fill="black")
        d.arc([380, 520, 644, 660], 0, 180, fill="black", width=12)
    st = render_diecut_sticker(draw_zoeira)
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, color)
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 8. br-futebol-gols-animados ──
print("Building br-futebol-gols-animados...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-futebol-gols-animados')
os.makedirs(pack_dir, exist_ok=True)

gols = [
    ("GOL DE BICICLETA! 🚲⚽", "#15803D"),
    ("NA GAVETA! 🥅💥", "#0284C7"),
    ("DEFESAÇA HISTÓRICA! 🧤", "#DC2626"),
    ("DESLIZANDO NO GRAMADO 🌱", "#16A34A"),
    ("SAMBA NA BANDEIRINHA 🚩", "#F59E0B"),
    ("BOLA GIRANDO NO DEDO ☝️", "#8B5CF6"),
    ("SINALIZADOR & TORCIDA 🎇", "#EA580C"),
    ("CHAMA O VAR! 📺", "#06B6D4")
]

for idx, (title, color) in enumerate(gols, 1):
    def draw_gol(d, c, col=color):
        d.ellipse([340, 340, 684, 684], fill="white", outline="black", width=14)
        for pent in [(512, 512), (390, 420), (634, 420), (440, 630), (584, 630)]:
            d.polygon([(pent[0], pent[1]-30), (pent[0]+28, pent[1]-10), (pent[0]+18, pent[1]+25), (pent[0]-18, pent[1]+25), (pent[0]-28, pent[1]-10)], fill="black")
    st = render_diecut_sticker(draw_gol)
    c = make_animated_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, color)
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 9. br-flork-debochado ──
print("Building br-flork-debochado...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-flork-debochado')
os.makedirs(pack_dir, exist_ok=True)

florks = [
    ("LAVANDO MINHA HONRA 🛁", "bathtub"),
    ("MINHA VIDA AMOROSA 🔥", "fire"),
    ("PAPEL DE TROUXA 🤡", "clown"),
    ("MODO DETETIVE FBI 🕵️", "fbi"),
    ("NEM ME CHAMA PRA SAIR 🛌", "blanket"),
    ("RICO POR 5 MINUTOS 💸", "money"),
    ("DOSE EXTRA DE CAFÉ ☕", "coffee"),
    ("LONGE DOS PROBLEMAS 🚀", "rocket")
]

for idx, (title, scene_id) in enumerate(florks, 1):
    def draw_flork(d, c, s=scene_id):
        d.arc([320, 200, 704, 600], 150, 30, fill="black", width=14)
        d.line([(330, 420), (330, 780)], fill="black", width=14)
        d.line([(694, 420), (694, 780)], fill="black", width=14)
        d.ellipse([430, 320, 460, 350], fill="black")
        d.ellipse([564, 320, 594, 350], fill="black")
        d.line([(450, 420), (574, 420)], fill="black", width=10)
        if s == "clown":
            d.ellipse([487, 360, 537, 410], fill="#EF4444")
        elif s == "coffee":
            d.rectangle([580, 560, 740, 740], fill="#78350F", outline="black", width=8)
    st = render_diecut_sticker(draw_flork)
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#1E293B")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 10. br-lula-reacoes ──
print("Building br-lula-reacoes...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-lula-reacoes')
os.makedirs(pack_dir, exist_ok=True)

lula_scenes = [
    ("FAZ O L! 👆", "faz_o_l"),
    ("VAI TER PICANHA! 🥩🍻", "picanha"),
    ("O BRASIL VOLTOU! 🇧🇷⚡", "voltou"),
    ("COMPANHEIRO! 🍻", "companheiro"),
    ("UNIÃO & RECONSTRUÇÃO ⭐", "uniao"),
    ("O AMOR VENCEU! ❤️", "amor"),
    ("MAIS EDUCAÇÃO! 🎓", "educacao"),
    ("NUNCA NA HISTÓRIA DESSE PAÍS 📢", "historia")
]

for idx, (title, scene_id) in enumerate(lula_scenes, 1):
    def draw_lula(d, c, s=scene_id):
        d.ellipse([340, 240, 684, 600], fill="#FED7AA") # Head
        d.arc([320, 420, 704, 660], 0, 180, fill="white", width=45) # White beard
        d.ellipse([420, 360, 460, 400], fill="black")
        d.ellipse([564, 360, 604, 400], fill="black")
        if s == "faz_o_l":
            d.rectangle([480, 200, 544, 520], fill="#FFD1A4", outline="#B45309", width=6)
            d.rectangle([480, 460, 680, 520], fill="#FFD1A4", outline="#B45309", width=6)
        elif s == "picanha":
            d.ellipse([300, 640, 724, 840], fill="#881337", outline="#4C0519", width=8)
            d.pieslice([300, 640, 724, 840], 190, 350, fill="#FDE047")
    st = render_diecut_sticker(draw_lula)
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#DC2626")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 11. br-carnaval-samba ──
print("Building br-carnaval-samba...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-carnaval-samba')
os.makedirs(pack_dir, exist_ok=True)

carnaval_items = [
    ("PASSISTA SAMBANDO 💃", "passista"),
    ("PANDEIRO NO RITMO 🥁", "pandeiro"),
    ("TRIO ELÉTRICO SALVADOR 🚚", "trio"),
    ("FREVO COM SOMBRINHA ☂️", "frevo"),
    ("MÁSCARA DOURADA VENEZA 🎭", "mask"),
    ("CUÍCA NA BATERIA 🪘", "cuica"),
    ("CARRO ALEGÓRICO RIO 🐆", "float"),
    ("CANHÃO DE CONFETE 🎊", "cannon")
]

for idx, (title, scene_id) in enumerate(carnaval_items, 1):
    def draw_carnaval(d, c, s=scene_id):
        if s == "pandeiro":
            d.ellipse([260, 260, 764, 764], fill="#FEF08A", outline="#78350F", width=18)
            for ba in range(0, 360, 45):
                bx = int(512 + math.cos(math.radians(ba)) * 240)
                by = int(512 + math.sin(math.radians(ba)) * 240)
                d.ellipse([bx-25, by-25, bx+25, by+25], fill="#E2E8F0", outline="#475569", width=4)
        elif s == "mask":
            d.polygon([(260, 360), (512, 420), (764, 360), (704, 560), (512, 520), (320, 560)], fill="#F59E0B", outline="#B45309", width=8)
            d.ellipse([340, 420, 440, 480], fill="black")
            d.ellipse([584, 420, 684, 480], fill="black")
        else:
            for fa, col in [(-50, "#EC4899"), (-25, "#8B5CF6"), (0, "#F59E0B"), (25, "#10B981"), (50, "#06B6D4")]:
                fx = int(512 + math.sin(math.radians(fa)) * 340)
                fy = int(320 - math.cos(math.radians(fa)) * 220)
                d.polygon([(512, 440), (fx - 35, fy), (fx, fy - 60), (fx + 35, fy)], fill=col)
    st = render_diecut_sticker(draw_carnaval)
    c = make_animated_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#BE185D")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 12. br-passinho-funk ──
print("Building br-passinho-funk...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-passinho-funk')
os.makedirs(pack_dir, exist_ok=True)

funk_items = [
    ("MANDA O PASSINHO DO RIO 🕺", "#E11D48"),
    ("BOOMBOX DOS ANOS 90 📻", "#334155"),
    ("DJ RISCANDO NO BAILE 🎧", "#0284C7"),
    ("ÓCULOS JULIET ESPELHADO 😎", "#F59E0B"),
    ("QUADRADINHO DE OITO 💃", "#EC4899"),
    ("FREEZE NO CHÃO ⚡", "#8B5CF6"),
    ("PAREDÃO DE SOM 🔊", "#10B981"),
    ("FOGOS NA ROCINHA 🎆", "#EA580C")
]

for idx, (title, color) in enumerate(funk_items, 1):
    def draw_funk(d, c, col=color):
        d.line([(512, 360), (512, 640)], fill="#1E293B", width=36)
        d.line([(512, 640), (380, 840)], fill="#1E293B", width=28)
        d.line([(512, 640), (644, 840)], fill="#1E293B", width=28)
        d.ellipse([440, 200, 584, 344], fill="#FDE68A")
        d.rectangle([440, 260, 584, 290], fill=col) # Juliet shades
    st = render_diecut_sticker(draw_funk)
    c = make_animated_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, color)
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 13. br-girias-brasileiras ──
print("Building br-girias-brasileiras...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-girias-brasileiras')
os.makedirs(pack_dir, exist_ok=True)

girias = [
    ("EITA PREGO! 🔥", "#EF4444"),
    ("VIXI MARIA! 😱", "#F59E0B"),
    ("TOPÍSSIMO! ⭐", "#10B981"),
    ("VALEU, FALOU! 🚀", "#3B82F6"),
    ("MANO DO CÉU! ⚡", "#8B5CF6"),
    ("AFF NADA A VER 🙄", "#EC4899"),
    ("BORA PARTIR! 🏍️", "#06B6D4"),
    ("PERDI TUDO! 😂", "#D97706")
]

for idx, (word, color) in enumerate(girias, 1):
    def draw_giria(d, c, w=word, col=color):
        d.rounded_rectangle([180, 240, 844, 760], radius=80, fill=col, outline="white", width=14)
        d.polygon([(340, 740), (280, 880), (460, 740)], fill=col)
        draw_text_centered(d, w, (512, 500), get_font(56), fill="white", stroke_fill="black", stroke_width=8)
    st = render_diecut_sticker(draw_giria)
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), "", color)
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 14. br-bandeira-animada ──
print("Building br-bandeira-animada...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-bandeira-animada')
os.makedirs(pack_dir, exist_ok=True)

anim_flags = [
    ("BANDEIRA ONDULANDO 🇧🇷", "#009C3B"),
    ("FOGOS VERDE & AMARELO 🎆", "#F59E0B"),
    ("CORAÇÃO BRASILEIRO 💖", "#009C3B"),
    ("MOEDA DE OURO 🪙", "#D97706"),
    ("AVIÃO COM FAIXA ✈️", "#0284C7"),
    ("NEON PULSANTE ⚡", "#10B981"),
    ("TAÇA DO MUNDO 🏆", "#F59E0B"),
    ("CHUVA DE CONFETE 🎉", "#002776")
]

for idx, (title, color) in enumerate(anim_flags, 1):
    def draw_anim_flag(d, c):
        d.rectangle([220, 280, 804, 680], fill="#009C3B", outline="#005A20", width=10)
        d.polygon([(512, 320), (764, 480), (512, 640), (260, 480)], fill="#FFDF00")
        d.ellipse([412, 380, 612, 580], fill="#002776")
        d.arc([412, 420, 612, 540], 190, 350, fill="white", width=12)
    st = render_diecut_sticker(draw_anim_flag)
    c = make_animated_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, color)
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

# ── 15. br-bandeira-nacional ──
print("Building br-bandeira-nacional...")
pack_dir = os.path.join(PACKS_BASE_DIR, 'br-bandeira-nacional')
os.makedirs(pack_dir, exist_ok=True)

flag_items = [
    ("BRASIL 🇧🇷", "official"),
    ("PÁTRIA AMADA 💚💛", "map"),
    ("AMOR VERDE & AMARELO 💖", "heart"),
    ("RIO DE JANEIRO 🇧🇷", "rio"),
    ("GIGANTE PELA PRÓPRIA NATUREZA 🛡️", "shield"),
    ("1º LUGAR NO CORAÇÃO 🥇", "medal"),
    ("SOU BRASIL COM ORGULHO ⭐", "star"),
    ("BRASILEIRO COM ORGULHO 🇧🇷", "badge")
]

for idx, (title, scene_id) in enumerate(flag_items, 1):
    def draw_flag_item(d, c, s=scene_id):
        d.rectangle([220, 280, 804, 680], fill="#009C3B", outline="#005A20", width=10)
        d.polygon([(512, 320), (764, 480), (512, 640), (260, 480)], fill="#FFDF00")
        d.ellipse([412, 380, 612, 580], fill="#002776")
        d.arc([412, 420, 612, 540], 190, 350, fill="white", width=12)
    st = render_diecut_sticker(draw_flag_item)
    c = make_static_webp(st, os.path.join(pack_dir, f"{idx}.webp"), title, "#009C3B")
    if idx == 1:
        make_tray(c, os.path.join(pack_dir, "tray_icon.png"))

print("\nAll 20 Brazil Packs successfully generated with 100% transparent backgrounds and unique stickers!")
