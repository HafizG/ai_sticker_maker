import os
import json
from PIL import Image

PACKS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', 'packs')
MASTER_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', '_master.json')

with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
    master_data = json.load(f)

# Find all existing pack directories
all_dirs = [d for d in os.listdir(PACKS_BASE_DIR) if os.path.isdir(os.path.join(PACKS_BASE_DIR, d))]

valid_packs = {}
br_pack_list = []
global_pack_list = []

# Human-readable names and categories for known packs
pack_metadata_lookup = {
    "br-figurinhas-hot":        { "name": "Figurinhas Quentes & Sexy 🔥",     "cat": ["love", "emotions"],      "animated_sticker_pack": False },
    "br-beijo-apaixonado":      { "name": "Beijos Apaixonados 💋",            "cat": ["love", "emotions"],      "animated_sticker_pack": False },
    "br-abraco-carinhoso":      { "name": "Abraços & Carinho 🤗",             "cat": ["love", "emotions"],      "animated_sticker_pack": False },
    "br-casal-fofo":            { "name": "Casal Fofo & Romântico ❤️",         "cat": ["love"],                  "animated_sticker_pack": False },
    "br-coracao-paixao":        { "name": "Corações & Paixão 💖",              "cat": ["love", "emotions"],      "animated_sticker_pack": False },
    "br-gretchen-rainha":       { "name": "Gretchen Rainha dos Memes 👑",      "cat": ["funny", "trending"],     "animated_sticker_pack": True },
    "br-memes-classicos":       { "name": "Memes Clássicos Brasileiros 😂",    "cat": ["funny"],                "animated_sticker_pack": False },
    "br-bolsonaro-dancando":    { "name": "Bolsonaro Dançando & Memes 🕺",     "cat": ["funny", "trending"],     "animated_sticker_pack": False },
    "br-futebol-selecao":       { "name": "Seleção Brasileira & Craques ⚽",   "cat": ["sports", "trending"],   "animated_sticker_pack": False },
    "br-lula-reacoes":          { "name": "Lula & Política Reações 🚩",        "cat": ["funny"],                "animated_sticker_pack": False },
    "br-bandeira-nacional":     { "name": "Bandeiras do Brasil 🇧🇷",           "cat": ["festivals", "trending"], "animated_sticker_pack": False },
    "br-bandeira-animada":      { "name": "Bandeira do Brasil 2 🇧🇷",          "cat": ["festivals", "trending"], "animated_sticker_pack": False },
    "br-comida-brasileira-1":   { "name": "Comidas do Brasil 1 🍲",           "cat": ["trending", "emotions"], "animated_sticker_pack": False },
    "br-comida-brasileira-2":   { "name": "Comidas do Brasil 2 🥐",           "cat": ["trending", "emotions"], "animated_sticker_pack": False },
    "br-comida-brasileira-3":   { "name": "Comidas do Brasil 3 🍹",           "cat": ["trending", "emotions"], "animated_sticker_pack": False },
    "br-futebol-gols-animados": { "name": "Esportes & Futebol ⚽",            "cat": ["sports", "trending"],   "animated_sticker_pack": False },
    "global-emoji-remix":       { "name": "Funny Faces Reactions",             "cat": ["funny", "emotions"],    "animated_sticker_pack": False },
    "global-reactions":         { "name": "Reaction Stickers",                 "cat": ["funny"],                "animated_sticker_pack": False },
    "global-love-hearts":       { "name": "Animated Faces Reactions",          "cat": ["love"],                 "animated_sticker_pack": True },
    "global-football-bg":       { "name": "Football Backgrounds",              "cat": ["sports"],               "animated_sticker_pack": False },
    "global-football-kicks":    { "name": "Football Kicks",                    "cat": ["sports"],               "animated_sticker_pack": False },
}

for d in all_dirs:
    dir_path = os.path.join(PACKS_BASE_DIR, d)
    webps = [f for f in os.listdir(dir_path) if f.endswith('.webp') and f != 'tray_icon.webp']
    if not webps:
        continue
        
    # Ensure tray_icon.png exists
    tray_path = os.path.join(dir_path, "tray_icon.png")
    if not os.path.exists(tray_path):
        first_webp = os.path.join(dir_path, sorted(webps)[0])
        try:
            im = Image.open(first_webp)
            im.thumbnail((96, 96), Image.Resampling.LANCZOS)
            bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
            bg.paste(im, ((96 - im.width) // 2, (96 - im.height) // 2), im)
            bg.save(tray_path, format="PNG")
        except Exception as e:
            print(f"Error creating tray for {d}: {e}")
            
    meta = pack_metadata_lookup.get(d, {
        "name": d.replace("br-", "").replace("-", " ").title(),
        "cat": ["trending"],
        "animated_sticker_pack": False
    })
    
    valid_packs[d] = {
        "name": meta["name"],
        "cat": meta["cat"],
        "hidden": [],
        "animated_sticker_pack": meta["animated_sticker_pack"]
    }
    
    if d.startswith("br-"):
        br_pack_list.append(d)
    elif d.startswith("global-"):
        global_pack_list.append(d)

master_data["packs"] = valid_packs
master_data["countries"]["BR"]["packs"] = br_pack_list
master_data["countries"]["_default"]["packs"] = global_pack_list

with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=2, ensure_ascii=False)

print(f"Synchronized _master.json with {len(valid_packs)} valid packs ({len(br_pack_list)} BR packs).")
