/**
 * generate.js — CI Build Script (v2 — Country-first)
 *
 * Reads _master.json + scans pack folders → generates:
 *   - sticker-cdn/countries/{CC}.json   (one per country)
 *   - sticker-cdn/countries/_default.json
 *   - sticker-cdn/index.json            (country list + metadata)
 *
 * New v2 concepts:
 *   - No regions/zones/wildcards
 *   - Countries declare their own packs + categories
 *   - "same_as" pointer for countries that share config
 *   - "hidden" array per pack to exclude individual stickers
 *   - Each country file is self-contained (1 request from app)
 *
 * Usage: node scripts/generate.js
 * Exit code 1 on validation failure → blocks CI deploy.
 */

const fs = require('fs');
const path = require('path');

// ─── Config ────────────────────────────────────────────────────────────
const CDN_DIR = path.join(__dirname, '..', 'sticker-cdn');
const MASTER_PATH = path.join(CDN_DIR, '_master.json');
const PACKS_DIR = path.join(CDN_DIR, 'packs');
const COUNTRIES_DIR = path.join(CDN_DIR, 'countries');
const MAX_STICKERS = 30;

// ─── Load master ───────────────────────────────────────────────────────
if (!fs.existsSync(MASTER_PATH)) {
  console.error('ERROR: _master.json not found at', MASTER_PATH);
  process.exit(1);
}

const master = JSON.parse(fs.readFileSync(MASTER_PATH, 'utf8'));
const errors = [];
const warnings = [];

// ─── Step 1: Validate master structure ─────────────────────────────────
if (typeof master.v !== 'number' || master.v < 1) {
  errors.push('"v" must be a positive integer');
}

if (!master.baseUrl || typeof master.baseUrl !== 'string') {
  errors.push('"baseUrl" must be a non-empty string');
}

if (!master.categories || typeof master.categories !== 'object' || Array.isArray(master.categories)) {
  errors.push('"categories" must be an object { id: "Display Name" }');
}

if (!master.packs || typeof master.packs !== 'object' || Array.isArray(master.packs)) {
  errors.push('"packs" must be an object { packId: { name, cat, hidden } }');
}

if (!master.countries || typeof master.countries !== 'object' || Array.isArray(master.countries)) {
  errors.push('"countries" must be an object');
}

// Bail early on structural errors
if (errors.length > 0) {
  console.error('\n❌ Structural validation failed:\n');
  errors.forEach(e => console.error('  • ' + e));
  process.exit(1);
}

// ─── Step 2: Validate categories ───────────────────────────────────────
const catIds = new Set(Object.keys(master.categories));

if (catIds.size === 0) {
  errors.push('No categories defined');
}

for (const [id, name] of Object.entries(master.categories)) {
  if (typeof name !== 'string' || name.trim() === '') {
    errors.push(`Category "${id}" must have a non-empty string name`);
  }
}

// ─── Step 3: Validate packs ───────────────────────────────────────────
const packIds = new Set(Object.keys(master.packs));

if (packIds.size === 0) {
  errors.push('No packs defined');
}

for (const [id, pack] of Object.entries(master.packs)) {
  if (!pack.name || typeof pack.name !== 'string') {
    errors.push(`Pack "${id}" must have a "name" string`);
  }
  if (!Array.isArray(pack.cat) || pack.cat.length === 0) {
    errors.push(`Pack "${id}" must have at least one category in "cat"`);
  } else {
    for (const cat of pack.cat) {
      if (!catIds.has(cat)) {
        errors.push(`Pack "${id}" references unknown category "${cat}"`);
      }
    }
  }
  if (pack.hidden !== undefined && !Array.isArray(pack.hidden)) {
    errors.push(`Pack "${id}" "hidden" must be an array (or omit it)`);
  }
}

// ─── Step 4: Validate countries + same_as pointers ─────────────────────
if (!master.countries._default) {
  errors.push('"countries._default" is required as fallback');
}

// Resolve same_as with circular detection
function resolveCountry(code, visited = new Set()) {
  const entry = master.countries[code];
  if (!entry) return null;
  if (!entry.same_as) return entry;

  if (visited.has(code)) {
    errors.push(`Circular same_as detected: ${[...visited, code].join(' → ')}`);
    return null;
  }
  visited.add(code);

  const target = master.countries[entry.same_as];
  if (!target) {
    errors.push(`Country "${code}" same_as "${entry.same_as}" — target not found`);
    return null;
  }
  return resolveCountry(entry.same_as, visited);
}

for (const [code, entry] of Object.entries(master.countries)) {
  if (entry.same_as) {
    // Validate same_as target exists
    resolveCountry(code);
    continue;
  }

  // Full country entry — validate fields
  if (!Array.isArray(entry.categories) || entry.categories.length === 0) {
    errors.push(`Country "${code}" must have a non-empty "categories" array`);
  } else {
    for (const cat of entry.categories) {
      if (!catIds.has(cat)) {
        errors.push(`Country "${code}" references unknown category "${cat}"`);
      }
    }
  }

  if (!Array.isArray(entry.packs) || entry.packs.length === 0) {
    errors.push(`Country "${code}" must have a non-empty "packs" array`);
  } else {
    for (const packId of entry.packs) {
      if (!packIds.has(packId)) {
        errors.push(`Country "${code}" references unknown pack "${packId}"`);
      }
    }
  }
}

// ─── Step 5: Scan pack folders ─────────────────────────────────────────
const packStickers = {}; // packId → [sorted sticker filenames]

for (const [id, pack] of Object.entries(master.packs)) {
  const packPath = path.join(PACKS_DIR, id);
  if (!fs.existsSync(packPath)) {
    errors.push(`Missing folder: packs/${id}/`);
    continue;
  }

  const allFiles = fs.readdirSync(packPath);
  const hidden = new Set(pack.hidden || []);

  // All .webp files except tray_icon
  const stickerFiles = allFiles
    .filter(f => f.endsWith('.webp') && f !== 'tray_icon.webp' && !hidden.has(f))
    .sort((a, b) => {
      // Numeric sort: 1.webp, 2.webp, ... 10.webp
      const numA = parseInt(a, 10);
      const numB = parseInt(b, 10);
      if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
      return a.localeCompare(b);
    });

  if (stickerFiles.length === 0) {
    errors.push(`No visible stickers in packs/${id}/ (${hidden.size} hidden)`);
    continue;
  }

  if (stickerFiles.length > MAX_STICKERS) {
    errors.push(`Too many stickers in packs/${id}/ (${stickerFiles.length}, max ${MAX_STICKERS})`);
  }

  // Validate hidden entries reference real files
  for (const h of hidden) {
    if (!allFiles.includes(h)) {
      warnings.push(`Pack "${id}" hides "${h}" but file doesn't exist`);
    }
  }

  // Warn about non-webp files
  const nonWebp = allFiles.filter(
    f => !f.endsWith('.webp') && f !== '.DS_Store' && f !== 'Thumbs.db'
  );
  if (nonWebp.length > 0) {
    warnings.push(`Unexpected files in packs/${id}/: ${nonWebp.join(', ')}`);
  }

  packStickers[id] = stickerFiles;
}

// ─── Abort on errors ───────────────────────────────────────────────────
if (warnings.length > 0) {
  console.warn('\n⚠️  Warnings:\n');
  warnings.forEach(w => console.warn('  • ' + w));
}

if (errors.length > 0) {
  console.error('\n❌ Validation failed:\n');
  errors.forEach(e => console.error('  • ' + e));
  console.error(`\n${errors.length} error(s) found. Fix them and retry.\n`);
  process.exit(1);
}

// ─── Step 6: Clean old output ──────────────────────────────────────────
// Remove old regions/ folder if it exists (v1 artifact)
const OLD_REGIONS_DIR = path.join(CDN_DIR, 'regions');
if (fs.existsSync(OLD_REGIONS_DIR)) {
  fs.rmSync(OLD_REGIONS_DIR, { recursive: true, force: true });
  console.log('  🗑️  Removed old regions/ folder (v1 artifact)');
}

// Create or clean countries/ folder
if (fs.existsSync(COUNTRIES_DIR)) {
  for (const f of fs.readdirSync(COUNTRIES_DIR)) {
    fs.unlinkSync(path.join(COUNTRIES_DIR, f));
  }
} else {
  fs.mkdirSync(COUNTRIES_DIR, { recursive: true });
}

// ─── Step 7: Generate country JSON files ───────────────────────────────
const countryCodes = Object.keys(master.countries);
let filesGenerated = 0;

for (const code of countryCodes) {
  const config = resolveCountry(code);
  if (!config) continue; // Error already logged

  // Build categories array (preserves order from country definition)
  const categories = config.categories
    .filter(catId => catIds.has(catId))
    .map(catId => ({ id: catId, name: master.categories[catId] }));

  // Build packs array (preserves order from country definition)
  const packs = config.packs
    .filter(packId => packStickers[packId]) // only packs with stickers
    .map(packId => {
      const pack = master.packs[packId];
      const stickers = packStickers[packId];
      return {
        id: packId,
        name: pack.name,
        cat: pack.cat,
        count: stickers.length,
        tray: stickers[0], // first sticker as tray icon
        stickers
      };
    });

  const output = {
    v: master.v,
    baseUrl: master.baseUrl,
    country: code,
    categories,
    packs
  };

  fs.writeFileSync(
    path.join(COUNTRIES_DIR, `${code}.json`),
    JSON.stringify(output, null, 2)
  );
  filesGenerated++;
}

// ─── Step 8: Generate index.json ───────────────────────────────────────
const indexData = {
  v: master.v,
  baseUrl: master.baseUrl,
  countries: countryCodes.filter(c => c !== '_default')
};

fs.writeFileSync(
  path.join(CDN_DIR, 'index.json'),
  JSON.stringify(indexData, null, 2)
);

// ─── Summary ───────────────────────────────────────────────────────────
const mainCountries = countryCodes.filter(c => c !== '_default' && !master.countries[c].same_as);
const aliasCountries = countryCodes.filter(c => master.countries[c].same_as);
const totalStickers = Object.values(packStickers).reduce((sum, arr) => sum + arr.length, 0);

console.log(`\n✅ v${master.v} generated successfully!\n`);
console.log(`  🌍 ${filesGenerated} country files created:`);
console.log(`     • ${mainCountries.length} main: ${mainCountries.join(', ')}`);
console.log(`     • ${aliasCountries.length} aliases (same_as): ${aliasCountries.join(', ')}`);
console.log(`     • 1 _default fallback`);
console.log(`  📦 ${packIds.size} packs validated (${totalStickers} visible stickers)`);
console.log(`  📄 index.json created`);
console.log(`  🌐 Base URL: ${master.baseUrl}`);
console.log('');
