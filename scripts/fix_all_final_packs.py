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

def make_animated_webp(pil_img, out_path, banner_text="", stroke_color="#15803D"):
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
# 13. br-futebol-gols-animados
# ══════════════════════════════════════════════════
print("Processing Pack 13: br-futebol-gols-animados...")
pack_dir_13 = os.path.join(PACKS_BASE_DIR, 'br-futebol-gols-animados')
os.makedirs(pack_dir_13, exist_ok=True)

gols = [
    ("GOL DE BICICLETA! 🚲⚽", "#15803D"),
    ("NA GAVETA! 🥅💥", "#0284C7"),
    ("DEFESAÇA HISTÓRICA! 🧤", "#DC2626"),
    ("DESLIZANDO NO GRAMADO 🌱", "#16A34A"),
    ("SAMBA NA BANDEIRINHA 🚩", "#F59E0B"),
    ("BOLA GIRANDO NO DEDO ☝️", "#8B5CF6"),
    ("SINALIZADOR & TORCIDA 🎇", "#EA580C"),
    ("CHAMA O VAR! 📺", "#06B6D4"),
]

for idx, (title, color) in enumerate(gols, 1):
    def draw_gol(d, c, col=color):
        d.ellipse([340, 340, 684, 684], fill="white", outline="black", width=14)
        for pent in [(512, 512), (390, 420), (634, 420), (440, 630), (584, 630)]:
            d.polygon([(pent[0], pent[1]-30), (pent[0]+28, pent[1]-10), (pent[0]+18, pent[1]+25), (pent[0]-18, pent[1]+25), (pent[0]-28, pent[1]-10)], fill="black")
    cutout = render_diecut_sticker(draw_gol)
    f = make_animated_webp(cutout, os.path.join(pack_dir_13, f"{idx}.webp"), title, color)
    if idx == 1:
        make_tray(f, os.path.join(pack_dir_13, "tray_icon.png"))
    print(f"Pack 13: Generated {idx}.webp")

# ══════════════════════════════════════════════════
# 14. br-flork-debochado
# ══════════════════════════════════════════════════
print("Processing Pack 14: br-flork-debochado...")
pack_dir_14 = os.path.join(PACKS_BASE_DIR, 'br-flork-debochado')
os.makedirs(pack_dir_14, exist_ok=True)

florks = [
    ("LAVANDO MINHA HONRA 🛁", "bathtub"),
    ("MINHA VIDA AMOROSA 🔥", "fire"),
    ("PAPEL DE TROUXA 🤡", "clown"),
    ("MODO DETETIVE FBI 🕵️", "fbi"),
    ("NEM ME CHAMA PRA SAIR 🛌", "blanket"),
    ("RICO POR 5 MINUTOS 💸", "money"),
    ("DOSE EXTRA DE CAFÉ ☕", "coffee"),
    ("LONGE DOS PROBLEMAS 🚀", "rocket"),
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
    cutout = render_diecut_sticker(draw_flork)
    f = make_static_webp(cutout, os.path.join(pack_dir_14, f"{idx}.webp"), title, "#1E293B")
    if idx == 1:
        make_tray(f, os.path.join(pack_dir_14, "tray_icon.png"))
    print(f"Pack 14: Generated {idx}.webp")

# ══════════════════════════════════════════════════
# 15. br-lula-reacoes
# ══════════════════════════════════════════════════
print("Processing Pack 15: br-lula-reacoes...")
pack_dir_15 = os.path.join(PACKS_BASE_DIR, 'br-lula-reacoes')
os.makedirs(pack_dir_15, exist_ok=True)

lula_scenes = [
    ("FAZ O L! 👆", "faz_o_l"),
    ("VAI TER PICANHA! 🥩🍻", "picanha"),
    ("O BRASIL VOLTOU! 🇧🇷⚡", "voltou"),
    ("COMPANHEIRO! 🍻", "companheiro"),
    ("UNIÃO & RECONSTRUÇÃO ⭐", "uniao"),
    ("O AMOR VENCEU! ❤️", "amor"),
    ("MAIS EDUCAÇÃO! 🎓", "educacao"),
    ("NUNCA NA HISTÓRIA DESSE PAÍS 📢", "historia"),
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
    cutout = render_diecut_sticker(draw_lula)
    f = make_static_webp(cutout, os.path.join(pack_dir_15, f"{idx}.webp"), title, "#DC2626")
    if idx == 1:
        make_tray(f, os.path.join(pack_dir_15, "tray_icon.png"))
    print(f"Pack 15: Generated {idx}.webp")

# ══════════════════════════════════════════════════
# 16. br-carnaval-samba
# ══════════════════════════════════════════════════
print("Processing Pack 16: br-carnaval-samba...")
pack_dir_16 = os.path.join(PACKS_BASE_DIR, 'br-carnaval-samba')
os.makedirs(pack_dir_16, exist_ok=True)

carnaval_items = [
    ("PASSISTA SAMBANDO 💃", "passista"),
    ("PANDEIRO NO RITMO 🥁", "pandeiro"),
    ("TRIO ELÉTRICO SALVADOR 🚚", "trio"),
    ("FREVO COM SOMBRINHA ☂️", "frevo"),
    ("MÁSCARA DOURADA VENEZA 🎭", "mask"),
    ("CUÍCA NA BATERIA 🪘", "cuica"),
    ("CARRO ALEGÓRICO RIO 🐆", "float"),
    ("CANHÃO DE CONFETE 🎊", "cannon"),
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
    cutout = render_diecut_sticker(draw_carnaval)
    f = make_animated_webp(cutout, os.path.join(pack_dir_16, f"{idx}.webp"), title, "#BE185D")
    if idx == 1:
        make_tray(f, os.path.join(pack_dir_16, "tray_icon.png"))
    print(f"Pack 16: Generated {idx}.webp")

# ══════════════════════════════════════════════════
# 17. br-passinho-funk
# ══════════════════════════════════════════════════
print("Processing Pack 17: br-passinho-funk...")
pack_dir_17 = os.path.join(PACKS_BASE_DIR, 'br-passinho-funk')
os.makedirs(pack_dir_17, exist_ok=True)

funk_items = [
    ("MANDA O PASSINHO DO RIO 🕺", "#E11D48"),
    ("BOOMBOX DOS ANOS 90 📻", "#334155"),
    ("DJ RISCANDO NO BAILE 🎧", "#0284C7"),
    ("ÓCULOS JULIET ESPELHADO 😎", "#F59E0B"),
    ("QUADRADINHO DE OITO 💃", "#EC4899"),
    ("FREEZE NO CHÃO ⚡", "#8B5CF6"),
    ("PAREDÃO DE SOM 🔊", "#10B981"),
    ("FOGOS NA ROCINHA 🎆", "#EA580C"),
]

for idx, (title, color) in enumerate(funk_items, 1):
    def draw_funk(d, c, col=color):
        d.line([(512, 360), (512, 640)], fill="#1E293B", width=36)
        d.line([(512, 640), (380, 840)], fill="#1E293B", width=28)
        d.line([(512, 640), (644, 840)], fill="#1E293B", width=28)
        d.ellipse([440, 200, 584, 344], fill="#FDE68A")
        d.rectangle([440, 260, 584, 290], fill=col)
    cutout = render_diecut_sticker(draw_funk)
    f = make_animated_webp(cutout, os.path.join(pack_dir_17, f"{idx}.webp"), title, color)
    if idx == 1:
        make_tray(f, os.path.join(pack_dir_17, "tray_icon.png"))
    print(f"Pack 17: Generated {idx}.webp")

# ══════════════════════════════════════════════════
# 18. br-girias-brasileiras
# ══════════════════════════════════════════════════
print("Processing Pack 18: br-girias-brasileiras...")
pack_dir_18 = os.path.join(PACKS_BASE_DIR, 'br-girias-brasileiras')
os.makedirs(pack_dir_18, exist_ok=True)

girias = [
    ("EITA PREGO! 🔥", "#EF4444"),
    ("VIXI MARIA! 😱", "#F59E0B"),
    ("TOPÍSSIMO! ⭐", "#10B981"),
    ("VALEU, FALOU! 🚀", "#3B82F6"),
    ("MANO DO CÉU! ⚡", "#8B5CF6"),
    ("AFF NADA A VER 🙄", "#EC4899"),
    ("BORA PARTIR! 🏍️", "#06B6D4"),
    ("PERDI TUDO! 😂", "#D97706"),
]

for idx, (word, color) in enumerate(girias, 1):
    def draw_giria(d, c, w=word, col=color):
        d.rounded_rectangle([200, 260, 824, 740], radius=80, fill=col, outline="white", width=14)
        d.polygon([(360, 720), (300, 840), (460, 720)], fill=col)
        draw_text_centered(d, w, (512, 500), get_font(52), fill="white", stroke_fill="black", stroke_width=8)
    cutout = render_diecut_sticker(draw_giria)
    f = make_static_webp(cutout, os.path.join(pack_dir_18, f"{idx}.webp"), "", color)
    if idx == 1:
        make_tray(f, os.path.join(pack_dir_18, "tray_icon.png"))
    print(f"Pack 18: Generated {idx}.webp")

# ══════════════════════════════════════════════════
# 19. br-bandeira-animada
# ══════════════════════════════════════════════════
print("Processing Pack 19: br-bandeira-animada...")
pack_dir_19 = os.path.join(PACKS_BASE_DIR, 'br-bandeira-animada')
os.makedirs(pack_dir_19, exist_ok=True)

anim_flags = [
    ("BANDEIRA ONDULANDO 🇧🇷", "#009C3B"),
    ("FOGOS VERDE & AMARELO 🎆", "#F59E0B"),
    ("CORAÇÃO BRASILEIRO 💖", "#009C3B"),
    ("MOEDA DE OURO 🪙", "#D97706"),
    ("AVIÃO COM FAIXA ✈️", "#0284C7"),
    ("NEON PULSANTE ⚡", "#10B981"),
    ("TAÇA DO MUNDO 🏆", "#F59E0B"),
    ("CHUVA DE CONFETE 🎉", "#002776"),
]

for idx, (title, color) in enumerate(anim_flags, 1):
    def draw_anim_flag(d, c):
        d.rectangle([240, 300, 784, 660], fill="#009C3B", outline="#005A20", width=10)
        d.polygon([(512, 340), (744, 480), (512, 620), (280, 480)], fill="#FFDF00")
        d.ellipse([412, 400, 612, 560], fill="#002776")
        d.arc([412, 430, 612, 530], 190, 350, fill="white", width=10)
    cutout = render_diecut_sticker(draw_anim_flag)
    f = make_animated_webp(cutout, os.path.join(pack_dir_19, f"{idx}.webp"), title, color)
    if idx == 1:
        make_tray(f, os.path.join(pack_dir_19, "tray_icon.png"))
    print(f"Pack 19: Generated {idx}.webp")

# ══════════════════════════════════════════════════
# 20. br-bandeira-nacional
# ══════════════════════════════════════════════════
print("Processing Pack 20: br-bandeira-nacional...")
pack_dir_20 = os.path.join(PACKS_BASE_DIR, 'br-bandeira-nacional')
os.makedirs(pack_dir_20, exist_ok=True)

flag_items = [
    ("BRASIL 🇧🇷", "official"),
    ("PÁTRIA AMADA 💚💛", "map"),
    ("AMOR VERDE & AMARELO 💖", "heart"),
    ("RIO DE JANEIRO 🇧🇷", "rio"),
    ("GIGANTE PELA PRÓPRIA NATUREZA 🛡️", "shield"),
    ("1º LUGAR NO CORAÇÃO 🥇", "medal"),
    ("SOU BRASIL COM ORGULHO ⭐", "star"),
    ("BRASILEIRO COM ORGULHO 🇧🇷", "badge"),
]

for idx, (title, scene_id) in enumerate(flag_items, 1):
    def draw_flag_item(d, c, s=scene_id):
        d.rectangle([240, 300, 784, 660], fill="#009C3B", outline="#005A20", width=10)
        d.polygon([(512, 340), (744, 480), (512, 620), (280, 480)], fill="#FFDF00")
        d.ellipse([412, 400, 612, 560], fill="#002776")
        d.arc([412, 430, 612, 530], 190, 350, fill="white", width=10)
    cutout = render_diecut_sticker(draw_flag_item)
    f = make_static_webp(cutout, os.path.join(pack_dir_20, f"{idx}.webp"), title, "#009C3B")
    if idx == 1:
        make_tray(f, os.path.join(pack_dir_20, "tray_icon.png"))
    print(f"Pack 20: Generated {idx}.webp")

print("\nAll remaining Brazil packs (13 to 20) finished successfully!")
