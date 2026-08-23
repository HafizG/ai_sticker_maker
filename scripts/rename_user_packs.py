import os
import shutil
import json
from PIL import Image

PACKS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', 'packs')
MASTER_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sticker-cdn', '_master.json')

folder_mapping = {
    'brazil flags': 'br-bandeira-nacional',
    'brazil flags2': 'br-bandeira-animada',
    'brazil food 1': 'br-comida-brasileira-1',
    'brazil food 2': 'br-comida-brasileira-2',
    'brazil food 3': 'br-comida-brasileira-3',
    'brazil sports': 'br-futebol-gols-animados',
}

for src_name, dst_name in folder_mapping.items():
    src_dir = os.path.join(PACKS_BASE_DIR, src_name)
    dst_dir = os.path.join(PACKS_BASE_DIR, dst_name)
    
    if not os.path.exists(src_dir):
        print(f"Source dir {src_name} not found, skipping.")
        continue
        
    # Temporary rename src_dir if dst_dir already exists
    temp_dir = os.path.join(PACKS_BASE_DIR, dst_name + "_temp")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.rename(src_dir, temp_dir)
    
    # Clean up dst_dir if it exists
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir, exist_ok=True)
    
    # Process files
    all_files = sorted(os.listdir(temp_dir))
    webp_files = [f for f in all_files if f.lower().endswith('.webp')]
    png_files = [f for f in all_files if f.lower().endswith('.png')]
    
    # Move and rename webps to 1.webp, 2.webp...
    for idx, w in enumerate(webp_files, 1):
        old_w_path = os.path.join(temp_dir, w)
        new_w_path = os.path.join(dst_dir, f"{idx}.webp")
        shutil.move(old_w_path, new_w_path)
        
    # Process tray icon
    tray_dst = os.path.join(dst_dir, "tray_icon.png")
    if png_files:
        png_src = os.path.join(temp_dir, png_files[0])
        try:
            im = Image.open(png_src)
            im.thumbnail((96, 96), Image.Resampling.LANCZOS)
            bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
            bg.paste(im, ((96 - im.width) // 2, (96 - im.height) // 2), im)
            bg.save(tray_dst, format="PNG")
        except Exception as e:
            print(f"Error processing tray for {dst_name}: {e}")
            shutil.copy(png_src, tray_dst)
    else:
        # Generate tray from 1.webp
        first_webp = os.path.join(dst_dir, "1.webp")
        if os.path.exists(first_webp):
            im = Image.open(first_webp)
            im.thumbnail((96, 96), Image.Resampling.LANCZOS)
            bg = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
            bg.paste(im, ((96 - im.width) // 2, (96 - im.height) // 2), im)
            bg.save(tray_dst, format="PNG")
            
    # Clean up temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"Renamed and standardized pack: {src_name} -> {dst_name} ({len(webp_files)} stickers)")

# ══════════════════════════════════════════════════
# UPDATE _master.json
# ══════════════════════════════════════════════════
with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
    master_data = json.load(f)

# Ensure food packs are registered
food_packs_meta = {
    "br-comida-brasileira-1": { "name": "Comidas do Brasil 1 🍲", "cat": ["trending", "emotions"], "hidden": [], "animated_sticker_pack": False },
    "br-comida-brasileira-2": { "name": "Comidas do Brasil 2 🥐", "cat": ["trending", "emotions"], "hidden": [], "animated_sticker_pack": False },
    "br-comida-brasileira-3": { "name": "Comidas do Brasil 3 🍹", "cat": ["trending", "emotions"], "hidden": [], "animated_sticker_pack": False },
    "br-bandeira-nacional":   { "name": "Bandeiras do Brasil 🇧🇷", "cat": ["festivals", "trending"], "hidden": [], "animated_sticker_pack": False },
    "br-bandeira-animada":    { "name": "Bandeira do Brasil 2 🇧🇷", "cat": ["festivals", "trending"], "hidden": [], "animated_sticker_pack": False },
    "br-futebol-gols-animados":{ "name": "Esportes & Futebol ⚽", "cat": ["sports", "trending"], "hidden": [], "animated_sticker_pack": False },
}

for pid, pdata in food_packs_meta.items():
    master_data["packs"][pid] = pdata
    if pid not in master_data["countries"]["BR"]["packs"]:
        master_data["countries"]["BR"]["packs"].append(pid)

with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=2, ensure_ascii=False)

print("\nUpdated _master.json successfully!")
