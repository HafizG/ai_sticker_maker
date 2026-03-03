/**
 * create-dummy-webps.js
 * 
 * Generates tiny valid 1x1 pixel WebP placeholder files for all packs
 * defined in _master.json. Run this ONCE to bootstrap the structure.
 * Replace these with real sticker images before publishing.
 *
 * Usage: node scripts/create-dummy-webps.js
 */

const fs = require('fs');
const path = require('path');

const master = JSON.parse(
  fs.readFileSync(path.join(__dirname, '..', 'sticker-cdn', '_master.json'), 'utf8')
);
const packsDir = path.join(__dirname, '..', 'sticker-cdn', 'packs');

// Minimal valid 1x1 WebP file (lossy, 44 bytes)
// RIFF header + WEBP + VP8 chunk with 1x1 pixel data
const MINI_WEBP = Buffer.from([
  0x52, 0x49, 0x46, 0x46, // RIFF
  0x24, 0x00, 0x00, 0x00, // file size - 8
  0x57, 0x45, 0x42, 0x50, // WEBP
  0x56, 0x50, 0x38, 0x20, // VP8 (lossy)
  0x18, 0x00, 0x00, 0x00, // chunk size
  0x30, 0x01, 0x00, 0x9D, // VP8 bitstream
  0x01, 0x2A, 0x01, 0x00, // width=1
  0x01, 0x00, 0x01, 0x40, // height=1
  0x25, 0xA4, 0x00, 0x03,
  0x70, 0x00, 0xFE, 0xFB,
  0x94, 0x00, 0x00
]);

// How many stickers per pack (for demo purposes)
const STICKER_COUNTS = {
  'pk-funny-urdu': 3,
  'pk-cricket-fans': 2,
  'pk-ramadan-memes': 8,
  'sa-arabic-greetings': 5,
  'arab-ramadan-eid': 20,
  'global-emoji-remix': 15,
  'global-reactions': 18,
  'global-love-hearts': 12,
  'extra-vintage-pack': 10,
  'extra-pk-independence': 6,
  'extra-sa-national-day': 4
};

let created = 0;

for (const pack of master.packs) {
  const packPath = path.join(packsDir, pack.id);

  if (!fs.existsSync(packPath)) {
    fs.mkdirSync(packPath, { recursive: true });
  }

  // tray_icon.webp
  const trayPath = path.join(packPath, 'tray_icon.webp');
  if (!fs.existsSync(trayPath)) {
    fs.writeFileSync(trayPath, MINI_WEBP);
    created++;
  }

  // numbered stickers
  const count = STICKER_COUNTS[pack.id] || 3;
  for (let i = 1; i <= count; i++) {
    const stickerPath = path.join(packPath, `${i}.webp`);
    if (!fs.existsSync(stickerPath)) {
      fs.writeFileSync(stickerPath, MINI_WEBP);
      created++;
    }
  }
}

console.log(`\nCreated ${created} dummy WebP files across ${master.packs.length} packs.`);
console.log('Replace these with real sticker images before publishing.\n');
