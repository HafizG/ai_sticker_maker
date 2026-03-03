/**
 * generate.js — CI Build Script
 *
 * Reads _master.json + scans pack folders → generates:
 *   - sticker-cdn/index.json
 *   - sticker-cdn/regions/{REGION}.json  (one per region)
 *   - sticker-cdn/regions/{ZONE}.json    (one per zone)
 *   - sticker-cdn/regions/_default.json
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
const REGIONS_DIR = path.join(CDN_DIR, 'regions');
const MAX_STICKERS = 30;

// ─── Load master ───────────────────────────────────────────────────────
if (!fs.existsSync(MASTER_PATH)) {
  console.error('ERROR: _master.json not found at', MASTER_PATH);
  process.exit(1);
}

const master = JSON.parse(fs.readFileSync(MASTER_PATH, 'utf8'));
const errors = [];
const warnings = [];

// ─── Validate master structure ─────────────────────────────────────────
if (typeof master.v !== 'number' || master.v < 1) {
  errors.push('"v" must be a positive integer');
}

if (!master.baseUrl || typeof master.baseUrl !== 'string') {
  errors.push('"baseUrl" must be a non-empty string (e.g. "https://hafizg.github.io/ai_sticker_maker")');
}

if (!Array.isArray(master.categories) || master.categories.length === 0) {
  errors.push('"categories" must be a non-empty array');
}

if (!Array.isArray(master.regions)) {
  errors.push('"regions" must be an array');
}

if (!Array.isArray(master.zones)) {
  errors.push('"zones" must be an array');
}

if (!Array.isArray(master.packs) || master.packs.length === 0) {
  errors.push('"packs" must be a non-empty array');
}

// Bail early on structural errors
if (errors.length > 0) {
  console.error('\n❌ Structural validation failed:\n');
  errors.forEach(e => console.error('  • ' + e));
  process.exit(1);
}

// ─── Build lookup sets ─────────────────────────────────────────────────
const catIds = new Set(master.categories.map(c => c.id));
const regionCodes = new Set(master.regions);
const zoneIds = new Set(master.zones.map(z => z.id));

// Check for duplicate category IDs
const catIdList = master.categories.map(c => c.id);
const dupCats = catIdList.filter((id, i) => catIdList.indexOf(id) !== i);
if (dupCats.length > 0) {
  errors.push(`Duplicate category IDs: ${[...new Set(dupCats)].join(', ')}`);
}

// Check for duplicate pack IDs
const packIdList = master.packs.map(p => p.id);
const dupPacks = packIdList.filter((id, i) => packIdList.indexOf(id) !== i);
if (dupPacks.length > 0) {
  errors.push(`Duplicate pack IDs: ${[...new Set(dupPacks)].join(', ')}`);
}

// Check for duplicate zone IDs
const zoneIdList = master.zones.map(z => z.id);
const dupZones = zoneIdList.filter((id, i) => zoneIdList.indexOf(id) !== i);
if (dupZones.length > 0) {
  errors.push(`Duplicate zone IDs: ${[...new Set(dupZones)].join(', ')}`);
}

// Validate zone format
for (const zone of master.zones) {
  if (!zone.id.startsWith('_')) {
    errors.push(`Zone ID "${zone.id}" must start with "_"`);
  }
  if (!Array.isArray(zone.countries) || zone.countries.length === 0) {
    errors.push(`Zone "${zone.id}" must have a non-empty countries array`);
  }
}

// ─── Step 1: Scan pack folders & validate ──────────────────────────────
if (!fs.existsSync(REGIONS_DIR)) {
  fs.mkdirSync(REGIONS_DIR, { recursive: true });
}

const packCounts = {};

for (const pack of master.packs) {
  // Validate required fields
  if (!pack.id || typeof pack.id !== 'string') {
    errors.push(`Pack missing valid "id": ${JSON.stringify(pack)}`);
    continue;
  }
  if (!pack.name || typeof pack.name !== 'string') {
    errors.push(`Pack "${pack.id}" missing valid "name"`);
  }
  if (!Array.isArray(pack.cat) || pack.cat.length === 0) {
    errors.push(`Pack "${pack.id}" must have at least one category in "cat"`);
  }
  if (!Array.isArray(pack.regions) || pack.regions.length === 0) {
    errors.push(`Pack "${pack.id}" must have at least one entry in "regions"`);
  }

  // Validate category IDs exist
  if (Array.isArray(pack.cat)) {
    for (const cat of pack.cat) {
      if (!catIds.has(cat)) {
        errors.push(`Unknown category "${cat}" in pack "${pack.id}"`);
      }
    }
  }

  // Validate region references
  if (Array.isArray(pack.regions)) {
    for (const r of pack.regions) {
      if (r !== '*' && r !== '_default' && !regionCodes.has(r) && !zoneIds.has(r)) {
        errors.push(`Unknown region/zone "${r}" in pack "${pack.id}"`);
      }
    }
  }

  // Validate folder exists
  const packPath = path.join(PACKS_DIR, pack.id);
  if (!fs.existsSync(packPath)) {
    errors.push(`Missing folder: packs/${pack.id}/`);
    continue;
  }

  // Validate tray icon
  if (!fs.existsSync(path.join(packPath, 'tray_icon.webp'))) {
    errors.push(`Missing tray_icon.webp in packs/${pack.id}/`);
  }

  // Count stickers
  const allFiles = fs.readdirSync(packPath);
  const stickerFiles = allFiles.filter(
    f => f !== 'tray_icon.webp' && f.endsWith('.webp')
  );
  const stickerCount = stickerFiles.length;

  if (stickerCount === 0) {
    errors.push(`No stickers in packs/${pack.id}/`);
    continue;
  }

  if (stickerCount > MAX_STICKERS) {
    errors.push(
      `Too many stickers in packs/${pack.id}/ (${stickerCount}, max ${MAX_STICKERS})`
    );
  }

  // Validate sequential naming: 1.webp, 2.webp, ...
  for (let i = 1; i <= stickerCount; i++) {
    if (!fs.existsSync(path.join(packPath, `${i}.webp`))) {
      errors.push(`Missing ${i}.webp in packs/${pack.id}/ (gap in sequence)`);
    }
  }

  // Warn about extra non-webp files
  const nonWebp = allFiles.filter(
    f => !f.endsWith('.webp') && f !== '.DS_Store' && f !== 'Thumbs.db'
  );
  if (nonWebp.length > 0) {
    warnings.push(
      `Unexpected files in packs/${pack.id}/: ${nonWebp.join(', ')}`
    );
  }

  packCounts[pack.id] = stickerCount;
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

// ─── Step 2: Build target list ─────────────────────────────────────────
const targets = [
  ...master.regions.map(code => ({ id: code, type: 'region' })),
  ...master.zones.map(z => ({ id: z.id, type: 'zone' })),
  { id: '_default', type: 'default' }
];

// ─── Step 3: Generate region/zone JSON files ───────────────────────────
for (const target of targets) {
  const filtered = master.packs
    .filter(p => p.regions.includes(target.id) || p.regions.includes('*'))
    .filter(p => packCounts[p.id] > 0)
    .map(p => ({
      id: p.id,
      name: p.name,
      cat: p.cat,
      count: packCounts[p.id]
    }));

  const regionData = {
    v: master.v,
    packs: filtered
  };

  fs.writeFileSync(
    path.join(REGIONS_DIR, `${target.id}.json`),
    JSON.stringify(regionData, null, 2)
  );
}

// ─── Step 4: Generate index.json ───────────────────────────────────────
const regionsMap = {};
master.regions.forEach(code => {
  regionsMap[code] = master.v;
});

const zonesMap = {};
master.zones.forEach(z => {
  zonesMap[z.id] = { v: master.v, countries: z.countries };
});

const indexData = {
  v: master.v,
  baseUrl: master.baseUrl,
  categories: master.categories,
  regions: regionsMap,
  zones: zonesMap,
  defaultRegion: '_default'
};

fs.writeFileSync(
  path.join(CDN_DIR, 'index.json'),
  JSON.stringify(indexData, null, 2)
);

// ─── Summary ───────────────────────────────────────────────────────────
const regionCount = master.regions.length;
const zoneCount = master.zones.length;
const totalTargets = targets.length;

console.log(`\n✅ v${master.v} generated successfully!\n`);
console.log(`  📁 ${totalTargets} region/zone files created:`);
console.log(`     • ${regionCount} regions: ${master.regions.join(', ')}`);
console.log(`     • ${zoneCount} zones: ${master.zones.map(z => z.id).join(', ')}`);
console.log(`     • 1 default fallback`);
console.log(`  📦 ${master.packs.length} packs validated (${Object.values(packCounts).reduce((a, b) => a + b, 0)} total stickers)`);
console.log(`  📄 index.json created`);
console.log(`  🌐 Base URL: ${master.baseUrl}`);
console.log('');
