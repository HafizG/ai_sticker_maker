# Fetching Categories & Packs — Complete Guide

### How Your Android App Consumes the Sticker CDN

---

## Table of Contents

1. [The Big Picture — 2 Requests, 1 Country Code](#1-the-big-picture)
2. [Request #1: Fetch index.json](#2-request-1-fetch-indexjson)
3. [Resolve Country Code to Region File](#3-resolve-country-code-to-region-file)
4. [Request #2: Fetch Region JSON](#4-request-2-fetch-region-json)
5. [Filter Packs by Category (Tabs)](#5-filter-packs-by-category-tabs)
6. [Build Image URLs](#6-build-image-urls)
7. [Complete Flow — Every Scenario](#7-complete-flow--every-scenario)
8. [Caching Strategy](#8-caching-strategy)
9. [Offline Mode](#9-offline-mode)
10. [Data Models (Kotlin)](#10-data-models-kotlin)
11. [Full Implementation — Step by Step](#11-full-implementation--step-by-step)
12. [Edge Cases & Error Handling](#12-edge-cases--error-handling)

---

## 1. The Big Picture

```
Your app needs exactly:
  1 country code  (detected from device)
  2 HTTP requests (index.json + region.json)

That gives you:
  ✓ All categories (tabs)
  ✓ All packs for that user's region
  ✓ All sticker counts
  ✓ Base URL for all images
  ✓ Version for cache invalidation
```

### Visual Flow

```
┌──────────────┐     GET /index.json      ┌──────────────┐
│              │ ──────────────────────→   │              │
│  Android App │                           │  GitHub CDN  │
│              │  ←─────────────────────   │              │
│              │   categories, regions,    │              │
│              │   zones, baseUrl, v       │              │
│              │                           │              │
│  detect      │                           │              │
│  country="PK"│                           │              │
│              │     GET /regions/PK.json  │              │
│              │ ──────────────────────→   │              │
│              │                           │              │
│              │  ←─────────────────────   │              │
│              │   packs[] with count      │              │
└──────────────┘                           └──────────────┘
        │
        ↓
  Show tabs + packs
  Images: {baseUrl}/packs/{id}/tray_icon.webp
```

---

## 2. Request #1: Fetch index.json

### URL
```
https://hafizg.github.io/ai_sticker_maker/index.json
```

### Response
```json
{
  "v": 1,
  "baseUrl": "https://hafizg.github.io/ai_sticker_maker",
  "categories": [
    { "id": "funny",      "name": "Funny"     },
    { "id": "greetings",  "name": "Greetings" },
    { "id": "sports",     "name": "Sports"    },
    { "id": "emotions",   "name": "Emotions"  },
    { "id": "religious",  "name": "Religious"  },
    { "id": "festivals",  "name": "Festivals"  },
    { "id": "love",       "name": "Love"       },
    { "id": "trending",   "name": "Trending"   },
    { "id": "extra",      "name": "Extra ★"    }
  ],
  "regions": {
    "PK": 1,
    "IN": 1,
    "SA": 1,
    "AE": 1,
    "ID": 1,
    "BD": 1,
    "TR": 1,
    "EG": 1
  },
  "zones": {
    "_arab": {
      "v": 1,
      "countries": ["LB", "SY", "LY", "SD", "YE", "PS", "MR"]
    },
    "_south-asia": {
      "v": 1,
      "countries": ["LK", "NP", "AF", "MV", "MM"]
    },
    "_southeast-asia": {
      "v": 1,
      "countries": ["TH", "VN", "KH", "LA", "SG", "BN"]
    },
    "_africa": {
      "v": 1,
      "countries": ["KE", "GH", "ZA", "TZ", "UG", "ET", "CM", "SN"]
    },
    "_eu": {
      "v": 1,
      "countries": ["DE", "FR", "GB", "ES", "IT", "NL", "US", "CA", "AU"]
    },
    "_latam": {
      "v": 1,
      "countries": ["BR", "MX", "AR", "CO", "CL", "PE", "VE"]
    }
  },
  "defaultRegion": "_default"
}
```

### What You Extract

| Field | What It Is | How You Use It |
|---|---|---|
| `v` | Version number | Compare with cached version. Same → skip re-fetch |
| `baseUrl` | CDN root URL | Prefix for ALL image/data URLs |
| `categories` | Tab definitions | Render horizontal scrollable tabs |
| `regions` | Countries with dedicated files | Check if user's country has its own file |
| `zones` | Fallback groups | If country not in regions, find its zone |
| `defaultRegion` | Final fallback | If country not in any zone either |

---

## 3. Resolve Country Code to Region File

This is the core logic. One country code → one region file.

### Step-by-Step Resolution

```
Input: countryCode = "PK" (detected from device)

Step 1: Is "PK" a key in index.regions?
        regions = { "PK": 1, "IN": 1, "SA": 1, ... }
        → YES! "PK" exists
        → regionFile = "PK"
        → Fetch: {baseUrl}/regions/PK.json
        → DONE ✅

─────────────────────────────────────────────────

Input: countryCode = "LB" (Lebanon)

Step 1: Is "LB" a key in index.regions?
        → NO

Step 2: Is "LB" in any zone's countries array?
        zones._arab.countries = ["LB", "SY", "LY", "SD", "YE", "PS", "MR"]
        → YES! "LB" is in _arab
        → regionFile = "_arab"
        → Fetch: {baseUrl}/regions/_arab.json
        → DONE ✅

─────────────────────────────────────────────────

Input: countryCode = "JP" (Japan)

Step 1: Is "JP" a key in index.regions?
        → NO

Step 2: Is "JP" in any zone's countries array?
        → NO (not in _arab, _south-asia, _southeast-asia, _africa, _eu, _latam)

Step 3: Use defaultRegion
        → regionFile = "_default"
        → Fetch: {baseUrl}/regions/_default.json
        → DONE ✅
```

### The Resolution Function (Kotlin)

```kotlin
fun resolveRegionFile(
    countryCode: String,
    index: IndexResponse
): String {
    // Step 1: Direct region match
    if (countryCode in index.regions) {
        return countryCode   // "PK" → "PK"
    }

    // Step 2: Zone match
    for ((zoneId, zone) in index.zones) {
        if (countryCode in zone.countries) {
            return zoneId    // "LB" → "_arab"
        }
    }

    // Step 3: Default fallback
    return index.defaultRegion   // "_default"
}
```

### Every Country → Its Region File

| User Country | Step 1 (regions?) | Step 2 (zones?) | Result | File |
|---|---|---|---|---|
| PK (Pakistan) | ✅ YES | — | Direct | `PK.json` |
| IN (India) | ✅ YES | — | Direct | `IN.json` |
| SA (Saudi) | ✅ YES | — | Direct | `SA.json` |
| AE (UAE) | ✅ YES | — | Direct | `AE.json` |
| ID (Indonesia) | ✅ YES | — | Direct | `ID.json` |
| BD (Bangladesh) | ✅ YES | — | Direct | `BD.json` |
| TR (Turkey) | ✅ YES | — | Direct | `TR.json` |
| EG (Egypt) | ✅ YES | — | Direct | `EG.json` |
| LB (Lebanon) | ❌ | ✅ `_arab` | Zone | `_arab.json` |
| SY (Syria) | ❌ | ✅ `_arab` | Zone | `_arab.json` |
| PS (Palestine) | ❌ | ✅ `_arab` | Zone | `_arab.json` |
| LK (Sri Lanka) | ❌ | ✅ `_south-asia` | Zone | `_south-asia.json` |
| NP (Nepal) | ❌ | ✅ `_south-asia` | Zone | `_south-asia.json` |
| TH (Thailand) | ❌ | ✅ `_southeast-asia` | Zone | `_southeast-asia.json` |
| VN (Vietnam) | ❌ | ✅ `_southeast-asia` | Zone | `_southeast-asia.json` |
| KE (Kenya) | ❌ | ✅ `_africa` | Zone | `_africa.json` |
| ZA (South Africa) | ❌ | ✅ `_africa` | Zone | `_africa.json` |
| US (United States) | ❌ | ✅ `_eu` | Zone | `_eu.json` |
| GB (United Kingdom) | ❌ | ✅ `_eu` | Zone | `_eu.json` |
| DE (Germany) | ❌ | ✅ `_eu` | Zone | `_eu.json` |
| BR (Brazil) | ❌ | ✅ `_latam` | Zone | `_latam.json` |
| MX (Mexico) | ❌ | ✅ `_latam` | Zone | `_latam.json` |
| JP (Japan) | ❌ | ❌ | Default | `_default.json` |
| KR (Korea) | ❌ | ❌ | Default | `_default.json` |
| CN (China) | ❌ | ❌ | Default | `_default.json` |

**No user ever sees an empty app.** `_default.json` always has global packs.

---

## 4. Request #2: Fetch Region JSON

### URL Pattern
```
{baseUrl}/regions/{regionFile}.json
```

### Example: PK.json
```
GET https://hafizg.github.io/ai_sticker_maker/regions/PK.json
```

### Response
```json
{
  "v": 1,
  "packs": [
    {
      "id": "pk-funny-urdu",
      "name": "Funny Urdu Stickers",
      "cat": ["funny"],
      "count": 3
    },
    {
      "id": "pk-cricket-fans",
      "name": "Cricket Fans PK",
      "cat": ["sports"],
      "count": 2
    },
    {
      "id": "pk-ramadan-memes",
      "name": "Funny Ramadan Memes",
      "cat": ["funny", "religious"],
      "count": 8
    },
    {
      "id": "arab-ramadan-eid",
      "name": "Ramadan & Eid",
      "cat": ["religious", "festivals"],
      "count": 20
    },
    {
      "id": "global-emoji-remix",
      "name": "Emoji Remix",
      "cat": ["funny", "emotions"],
      "count": 15
    },
    {
      "id": "global-reactions",
      "name": "Reaction Stickers",
      "cat": ["funny"],
      "count": 18
    },
    {
      "id": "global-love-hearts",
      "name": "Love & Hearts",
      "cat": ["love"],
      "count": 12
    },
    {
      "id": "extra-vintage-pack",
      "name": "Vintage Collection",
      "cat": ["extra"],
      "count": 10
    },
    {
      "id": "extra-pk-independence",
      "name": "14 August Special",
      "cat": ["extra"],
      "count": 6
    }
  ]
}
```

### What You Get

This is ALL the data you need. Every pack available to a Pakistani user:
- 3 PK-specific packs
- 1 Arab multi-region pack (also targets PK)
- 3 global packs (target `"*"`)
- 2 extra packs (1 global, 1 PK-specific)

**Total: 9 packs, 94 stickers**

### Example: _default.json (for Japan, Korea, etc.)

```json
{
  "v": 1,
  "packs": [
    {
      "id": "global-emoji-remix",
      "name": "Emoji Remix",
      "cat": ["funny", "emotions"],
      "count": 15
    },
    {
      "id": "global-reactions",
      "name": "Reaction Stickers",
      "cat": ["funny"],
      "count": 18
    },
    {
      "id": "global-love-hearts",
      "name": "Love & Hearts",
      "cat": ["love"],
      "count": 12
    },
    {
      "id": "extra-vintage-pack",
      "name": "Vintage Collection",
      "cat": ["extra"],
      "count": 10
    }
  ]
}
```

Only global packs. Still a useful app — never empty.

---

## 5. Filter Packs by Category (Tabs)

You have `categories` from index.json and `packs` from region.json.
ALL filtering is **client-side**. No extra API calls.

### The Core Logic

```kotlin
// You already have these from the 2 requests:
val categories = index.categories    // from index.json
val allPacks = region.packs          // from region.json (e.g. PK.json)

// ─── Show only categories that have packs ─────────────
val visibleCategories = categories.filter { category ->
    allPacks.any { pack -> category.id in pack.cat }
}

// ─── Filter packs for selected tab ────────────────────
fun packsForCategory(categoryId: String): List<Pack> {
    return allPacks.filter { categoryId in it.cat }
}
```

### What Each Tab Shows (PK User)

```
All packs from PK.json:
  pk-funny-urdu         → cat: ["funny"]
  pk-cricket-fans       → cat: ["sports"]
  pk-ramadan-memes      → cat: ["funny", "religious"]
  arab-ramadan-eid      → cat: ["religious", "festivals"]
  global-emoji-remix    → cat: ["funny", "emotions"]
  global-reactions      → cat: ["funny"]
  global-love-hearts    → cat: ["love"]
  extra-vintage-pack    → cat: ["extra"]
  extra-pk-independence → cat: ["extra"]
```

#### Tab: Funny (filter where "funny" in cat)
```
  ✓ pk-funny-urdu         → "funny" ✅
  ✗ pk-cricket-fans       → "sports" only
  ✓ pk-ramadan-memes      → "funny" ✅ (also "religious")
  ✗ arab-ramadan-eid      → "religious", "festivals"
  ✓ global-emoji-remix    → "funny" ✅ (also "emotions")
  ✓ global-reactions      → "funny" ✅
  ✗ global-love-hearts    → "love" only
  ✗ extra-vintage-pack    → "extra" only
  ✗ extra-pk-independence → "extra" only

  Result: 4 packs shown
```

#### Tab: Religious (filter where "religious" in cat)
```
  ✓ pk-ramadan-memes      → "religious" ✅ (also "funny")
  ✓ arab-ramadan-eid      → "religious" ✅ (also "festivals")

  Result: 2 packs shown
```

#### Tab: Sports
```
  ✓ pk-cricket-fans       → "sports" ✅

  Result: 1 pack shown
```

#### Tab: Emotions
```
  ✓ global-emoji-remix    → "emotions" ✅ (also "funny")

  Result: 1 pack shown
```

#### Tab: Love
```
  ✓ global-love-hearts    → "love" ✅

  Result: 1 pack shown
```

#### Tab: Festivals
```
  ✓ arab-ramadan-eid      → "festivals" ✅ (also "religious")

  Result: 1 pack shown
```

#### Tab: Extra ★
```
  ✓ extra-vintage-pack    → "extra" ✅
  ✓ extra-pk-independence → "extra" ✅

  Result: 2 packs shown
```

#### Tab: Greetings
```
  (no pack has "greetings" in cat for PK region)

  Result: 0 packs → HIDE THIS TAB
```

#### Tab: Trending
```
  (no pack has "trending" in cat for PK region)

  Result: 0 packs → HIDE THIS TAB
```

### Final Visible Tabs for PK User

```
[Funny (4)] [Religious (2)] [Sports (1)] [Emotions (1)] [Love (1)] [Festivals (1)] [Extra ★ (2)]

Hidden: Greetings, Trending (no packs)
```

### Multi-Category Packs

A pack can appear in MULTIPLE tabs:

```
pk-ramadan-memes → cat: ["funny", "religious"]

  Shows in Funny tab     ✅
  Shows in Religious tab ✅
  It's the SAME pack — same ID
  Download it from Funny → it shows "Downloaded ✅" in Religious too
```

---

## 6. Build Image URLs

**Zero URLs are stored in JSON.** All URLs are derived from patterns:

### Tray Icon (pack thumbnail)

```
{baseUrl}/packs/{pack.id}/tray_icon.webp
```

```
Examples:
https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/tray_icon.webp
https://hafizg.github.io/ai_sticker_maker/packs/global-emoji-remix/tray_icon.webp
https://hafizg.github.io/ai_sticker_maker/packs/extra-vintage-pack/tray_icon.webp
```

### Individual Sticker

```
{baseUrl}/packs/{pack.id}/{n}.webp     where n = 1, 2, 3, ... count
```

```
Pack: pk-funny-urdu (count: 3)

Sticker 1: https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/1.webp
Sticker 2: https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/2.webp
Sticker 3: https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/3.webp

Pack: arab-ramadan-eid (count: 20)

Sticker 1:  .../packs/arab-ramadan-eid/1.webp
Sticker 2:  .../packs/arab-ramadan-eid/2.webp
...
Sticker 20: .../packs/arab-ramadan-eid/20.webp
```

### Kotlin Helper Functions

```kotlin
fun trayIconUrl(baseUrl: String, packId: String): String {
    return "$baseUrl/packs/$packId/tray_icon.webp"
}

fun stickerUrl(baseUrl: String, packId: String, number: Int): String {
    return "$baseUrl/packs/$packId/$number.webp"
}

fun allStickerUrls(baseUrl: String, packId: String, count: Int): List<String> {
    return (1..count).map { n -> "$baseUrl/packs/$packId/$n.webp" }
}

// Usage:
val baseUrl = index.baseUrl
val pack = region.packs[0]  // pk-funny-urdu, count=3

val tray = trayIconUrl(baseUrl, pack.id)
// → "https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/tray_icon.webp"

val stickers = allStickerUrls(baseUrl, pack.id, pack.count)
// → ["...pk-funny-urdu/1.webp", "...pk-funny-urdu/2.webp", "...pk-funny-urdu/3.webp"]
```

---

## 7. Complete Flow — Every Scenario

### Scenario 1: First Launch (PK User, Online)

```
1. App opens
   │
2. Detect country code
   │  TelephonyManager → "PK"
   │
3. GET https://hafizg.github.io/ai_sticker_maker/index.json
   │  ← Response: categories, regions, zones, baseUrl, v=1
   │  → Cache to: filesDir/cache/index.json
   │  → Save to DataStore: cached_index_v = 1
   │
4. Resolve: "PK" in regions? → YES → regionFile = "PK"
   │
5. GET https://hafizg.github.io/ai_sticker_maker/regions/PK.json
   │  ← Response: 9 packs with counts
   │  → Cache to: filesDir/cache/region_PK.json
   │  → Save to DataStore: cached_region = "PK", cached_region_v = 1
   │
6. Filter categories: hide empty tabs
   │  Visible: Funny(4), Religious(2), Sports(1), Emotions(1),
   │           Love(1), Festivals(1), Extra★(2)
   │
7. Show UI: tabs + pack grid
   │  Tray icons loaded via Coil: {baseUrl}/packs/{id}/tray_icon.webp
   │
8. Network cost: ~3KB + ~5KB = ~8KB total
```

### Scenario 2: Return Visit (Same Version, Online)

```
1. App opens
   │
2. Detect country: "PK" (or read from DataStore)
   │
3. GET index.json
   │  ← v=1
   │  Compare: cached_index_v == 1? → YES, same version
   │
4. Resolve: "PK", cached_region_v == 1? → YES, same version
   │  → Skip fetching PK.json entirely
   │  → Read from: filesDir/cache/region_PK.json
   │
5. Show UI immediately from cache
   │
6. Network cost: ~3KB (just index.json check)
```

### Scenario 3: Return Visit (New Version, Online)

```
1. App opens → Detect: "PK"
   │
2. GET index.json
   │  ← v=2 (you bumped the version!)
   │  Compare: cached_index_v == 1, new == 2 → DIFFERENT
   │
3. Cache new index.json
   │  Save: cached_index_v = 2
   │  Update categories if changed
   │
4. Resolve: "PK" → regions["PK"] = 2, cached_region_v = 1 → DIFFERENT
   │
5. GET regions/PK.json
   │  ← New packs list (maybe new packs added!)
   │  Cache new region file
   │  Save: cached_region_v = 2
   │
6. Show updated UI with new packs
   │
7. Network cost: ~3KB + ~5KB = ~8KB
```

### Scenario 4: Offline (Cached)

```
1. App opens → No network
   │
2. Read index.json from: filesDir/cache/index.json
   │  Found? → YES, use it
   │
3. Read region from DataStore: cached_region = "PK"
   │  Read: filesDir/cache/region_PK.json
   │  Found? → YES, use it
   │
4. Show UI from cache ✅
   │
5. Network cost: 0KB
```

### Scenario 5: Offline (Nothing Cached — First Ever Launch)

```
1. App opens → No network → No cache
   │
2. Show: "Connect to internet to load stickers"
   │  Or: show a bundled minimal pack (optional)
   │
3. When network returns → fetch as Scenario 1
```

### Scenario 6: Lebanon User (Zone Fallback)

```
1. Detect country: "LB"
   │
2. GET index.json
   │
3. Resolve:
   │  "LB" in regions? → NO (regions has PK,IN,SA,AE,ID,BD,TR,EG)
   │  "LB" in any zone? → YES, _arab.countries contains "LB"
   │  → regionFile = "_arab"
   │
4. GET regions/_arab.json
   │  ← Packs targeting _arab + global packs
   │
5. Show UI with Arab + global content
```

### Scenario 7: Japan User (Default Fallback)

```
1. Detect country: "JP"
   │
2. GET index.json
   │
3. Resolve:
   │  "JP" in regions? → NO
   │  "JP" in any zone? → NO
   │  → regionFile = "_default"
   │
4. GET regions/_default.json
   │  ← Only global packs (regions: ["*"])
   │
5. Show UI with global content (still useful, never empty)
```

---

## 8. Caching Strategy

### What to Cache Where

```
DataStore (key-value, tiny):
  ┌──────────────────────────┬───────────┐
  │ Key                      │ Example   │
  ├──────────────────────────┼───────────┤
  │ cached_index_v           │ 1         │
  │ cached_region            │ "PK"      │
  │ cached_region_v          │ 1         │
  │ detected_country         │ "PK"      │
  │ downloaded_packs         │ "pk-funny-urdu,global-emoji-remix" │
  └──────────────────────────┴───────────┘

Internal Storage (JSON files):
  filesDir/cache/
  ├── index.json              ← Full index response
  └── region_PK.json          ← Full region response

Coil Disk Cache (automatic):
  Tray icon images (auto-managed, LRU eviction)

Internal Storage (downloaded packs):
  filesDir/stickers/
  ├── pk-funny-urdu/
  │   ├── tray_icon.webp
  │   ├── 1.webp
  │   ├── 2.webp
  │   └── 3.webp
  └── global-emoji-remix/
      ├── tray_icon.webp
      ├── 1.webp
      └── ...
```

### Cache Decision Logic

```kotlin
suspend fun loadData(): AppData {
    val cachedIndexV = dataStore.get(CACHED_INDEX_V) ?: -1
    val cachedRegion = dataStore.get(CACHED_REGION)
    val cachedRegionV = dataStore.get(CACHED_REGION_V) ?: -1

    // 1. Try to fetch fresh index
    val index = try {
        val fresh = api.fetchIndex()
        // Cache it
        cacheFile("index.json", fresh.raw)
        dataStore.set(CACHED_INDEX_V, fresh.v)
        fresh
    } catch (e: Exception) {
        // Offline → read from cache
        readCacheFile("index.json")?.parseAsIndex()
            ?: throw NoDataException("No cached index")
    }

    // 2. Resolve region
    val country = detectCountry()
    val regionFile = resolveRegionFile(country, index)

    // 3. Decide: fetch region or use cache?
    val needsFetch = regionFile != cachedRegion
        || index.regionVersion(regionFile) != cachedRegionV

    val region = if (needsFetch) {
        try {
            val fresh = api.fetchRegion(regionFile)
            cacheFile("region_$regionFile.json", fresh.raw)
            dataStore.set(CACHED_REGION, regionFile)
            dataStore.set(CACHED_REGION_V, fresh.v)
            fresh
        } catch (e: Exception) {
            readCacheFile("region_$regionFile.json")?.parseAsRegion()
                ?: throw NoDataException("No cached region")
        }
    } else {
        readCacheFile("region_$regionFile.json")!!.parseAsRegion()
    }

    return AppData(index, region, country)
}
```

---

## 9. Offline Mode

### Three Levels of Offline

```
Level 1: Online (normal)
  → Fetch fresh data
  → Cache it
  → Show fresh UI

Level 2: Offline with Cache
  → Can't fetch → use cached index + region
  → Show UI from cache
  → Already-downloaded packs work perfectly
  → Tray icons may show from Coil cache

Level 3: Offline, No Cache (cold start, no internet)
  → Show error / retry button
  → OR: bundle a minimal _default.json in assets/
```

### Bundled Fallback (Optional but Recommended)

```
Include in your APK:
  assets/
    fallback_index.json     ← Copy of index.json at build time
    fallback_default.json   ← Copy of _default.json at build time

Code:
  if (no cache && no network) {
      val index = assets.open("fallback_index.json").parseAsIndex()
      val region = assets.open("fallback_default.json").parseAsRegion()
      // Shows global packs at minimum
  }
```

---

## 10. Data Models (Kotlin)

```kotlin
import kotlinx.serialization.Serializable

// ─── index.json ───────────────────────────────────────

@Serializable
data class IndexResponse(
    val v: Int,
    val baseUrl: String,
    val categories: List<Category>,
    val regions: Map<String, Int>,            // "PK" → 1 (version)
    val zones: Map<String, Zone>,             // "_arab" → Zone(...)
    val defaultRegion: String                 // "_default"
)

@Serializable
data class Category(
    val id: String,      // "funny"
    val name: String     // "Funny"
)

@Serializable
data class Zone(
    val v: Int,
    val countries: List<String>   // ["LB", "SY", "LY", ...]
)

// ─── regions/{code}.json ──────────────────────────────

@Serializable
data class RegionResponse(
    val v: Int,
    val packs: List<Pack>
)

@Serializable
data class Pack(
    val id: String,            // "pk-funny-urdu"
    val name: String,          // "Funny Urdu Stickers"
    val cat: List<String>,     // ["funny"]
    val count: Int             // 3
)
```

---

## 11. Full Implementation — Step by Step

### Step 1: Detect Country Code

```kotlin
import android.content.Context
import android.telephony.TelephonyManager
import java.util.Locale

fun detectCountryCode(context: Context): String {
    // Priority 1: SIM country (most reliable, works without internet)
    val tm = context.getSystemService(Context.TELEPHONY_SERVICE) as? TelephonyManager
    val simCountry = tm?.simCountryIso?.uppercase()
    if (!simCountry.isNullOrBlank() && simCountry.length == 2) {
        return simCountry   // "PK"
    }

    // Priority 2: Network country (needs cellular connection)
    val networkCountry = tm?.networkCountryIso?.uppercase()
    if (!networkCountry.isNullOrBlank() && networkCountry.length == 2) {
        return networkCountry
    }

    // Priority 3: Device locale (user setting)
    val localeCountry = Locale.getDefault().country.uppercase()
    if (localeCountry.length == 2) {
        return localeCountry
    }

    // Priority 4: Hardcoded fallback
    return "US"
}
```

### Step 2: Fetch Index

```kotlin
// Using Ktor:
suspend fun fetchIndex(baseUrl: String): IndexResponse {
    val url = "$baseUrl/index.json"
    return httpClient.get(url).body<IndexResponse>()
}

// Or using simple HttpURLConnection:
suspend fun fetchIndex(baseUrl: String): IndexResponse = withContext(Dispatchers.IO) {
    val url = URL("$baseUrl/index.json")
    val json = url.readText()
    Json.decodeFromString<IndexResponse>(json)
}
```

### Step 3: Resolve Region

```kotlin
fun resolveRegionFile(countryCode: String, index: IndexResponse): String {
    // Direct region match
    if (countryCode in index.regions) return countryCode

    // Zone match
    for ((zoneId, zone) in index.zones) {
        if (countryCode in zone.countries) return zoneId
    }

    // Default
    return index.defaultRegion
}
```

### Step 4: Fetch Region

```kotlin
suspend fun fetchRegion(baseUrl: String, regionFile: String): RegionResponse {
    val url = "$baseUrl/regions/$regionFile.json"
    return httpClient.get(url).body<RegionResponse>()
}
```

### Step 5: Filter for UI

```kotlin
class StickerRepository(
    private val index: IndexResponse,
    private val region: RegionResponse
) {
    val baseUrl: String get() = index.baseUrl
    val allPacks: List<Pack> get() = region.packs

    // Categories that have at least 1 pack
    val visibleCategories: List<Category>
        get() = index.categories.filter { cat ->
            allPacks.any { cat.id in it.cat }
        }

    // Packs for a specific category tab
    fun packsFor(categoryId: String): List<Pack> {
        return allPacks.filter { categoryId in it.cat }
    }

    // Tray icon URL for a pack
    fun trayIconUrl(pack: Pack): String {
        return "${baseUrl}/packs/${pack.id}/tray_icon.webp"
    }

    // All sticker URLs for a pack
    fun stickerUrls(pack: Pack): List<String> {
        return (1..pack.count).map { n ->
            "${baseUrl}/packs/${pack.id}/$n.webp"
        }
    }

    // Single sticker URL
    fun stickerUrl(packId: String, number: Int): String {
        return "${baseUrl}/packs/$packId/$number.webp"
    }

    // Search packs by name
    fun searchPacks(query: String): List<Pack> {
        return allPacks.filter { it.name.contains(query, ignoreCase = true) }
    }

    // All unique category IDs a pack belongs to
    fun categoriesForPack(pack: Pack): List<Category> {
        return index.categories.filter { it.id in pack.cat }
    }

    // Check if pack is downloaded
    fun isDownloaded(packId: String, downloadedPacks: Set<String>): Boolean {
        return packId in downloadedPacks
    }

    // Pack count per category (for badges)
    fun packCountPerCategory(): Map<String, Int> {
        return visibleCategories.associate { cat ->
            cat.id to allPacks.count { cat.id in it.cat }
        }
    }

    // Total stickers across all packs
    val totalStickers: Int
        get() = allPacks.sumOf { it.count }
}
```

### Step 6: Use in Compose UI

```kotlin
// ─── ViewModel ────────────────────────────────────────

@HiltViewModel
class StickerViewModel @Inject constructor(
    private val repository: StickerRepository
) : ViewModel() {

    val categories = repository.visibleCategories
    val selectedCategory = mutableStateOf(categories.firstOrNull())

    val currentPacks: List<Pack>
        get() = selectedCategory.value?.let {
            repository.packsFor(it.id)
        } ?: emptyList()

    fun selectCategory(category: Category) {
        selectedCategory.value = category
    }

    fun trayUrl(pack: Pack) = repository.trayIconUrl(pack)
    fun stickerUrls(pack: Pack) = repository.stickerUrls(pack)
}

// ─── UI ───────────────────────────────────────────────

@Composable
fun StickerScreen(viewModel: StickerViewModel) {
    Column {
        // Scrollable category tabs
        ScrollableTabRow(
            selectedTabIndex = viewModel.categories
                .indexOf(viewModel.selectedCategory.value)
        ) {
            viewModel.categories.forEach { category ->
                Tab(
                    selected = category == viewModel.selectedCategory.value,
                    onClick = { viewModel.selectCategory(category) },
                    text = { Text(category.name) }
                )
            }
        }

        // Pack grid
        LazyVerticalGrid(columns = GridCells.Fixed(2)) {
            items(viewModel.currentPacks) { pack ->
                PackCard(
                    pack = pack,
                    trayUrl = viewModel.trayUrl(pack)
                )
            }
        }
    }
}

@Composable
fun PackCard(pack: Pack, trayUrl: String) {
    Card {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            // Tray icon loaded via Coil
            AsyncImage(
                model = trayUrl,
                contentDescription = pack.name
            )
            Text(pack.name)
            Text("${pack.count} stickers")
        }
    }
}
```

---

## 12. Edge Cases & Error Handling

### Edge Case 1: Country Code Not Detected

```kotlin
val country = detectCountryCode(context)
// If all methods fail → returns "US"
// "US" is in _eu zone → gets _eu.json
// User sees global + EU content (reasonable default)
```

### Edge Case 2: index.json Fetch Fails (First Launch)

```kotlin
try {
    val index = fetchIndex(BASE_INDEX_URL)
} catch (e: Exception) {
    // Option A: Show retry button
    showError("Connect to internet to get started")

    // Option B: Use bundled fallback
    val index = loadBundledIndex()
}
```

### Edge Case 3: Region File Fetch Fails

```kotlin
try {
    val region = fetchRegion(baseUrl, regionFile)
} catch (e: Exception) {
    // Fallback: try _default.json instead
    try {
        val region = fetchRegion(baseUrl, "_default")
    } catch (e2: Exception) {
        // Use cache or bundled fallback
    }
}
```

### Edge Case 4: Category Has Zero Packs

```kotlin
// Already handled by visibleCategories filter:
val visibleCategories = categories.filter { cat ->
    allPacks.any { cat.id in it.cat }
}
// Empty categories are simply not shown as tabs
```

### Edge Case 5: Pack Appears in Multiple Tabs

```kotlin
// pk-ramadan-memes → cat: ["funny", "religious"]
// User downloads from Funny tab
// Goes to Religious tab → same pack.id → shows as downloaded

// The download state is tracked by pack.id, NOT by category
fun isDownloaded(packId: String) = downloadedPacks.contains(packId)
// Works across all tabs automatically
```

### Edge Case 6: User Changes Country (travel / new SIM)

```kotlin
// On each app open:
val currentCountry = detectCountryCode(context)
val savedCountry = dataStore.get(DETECTED_COUNTRY)

if (currentCountry != savedCountry) {
    // Country changed! Re-resolve region
    val newRegionFile = resolveRegionFile(currentCountry, index)
    val savedRegionFile = dataStore.get(CACHED_REGION)

    if (newRegionFile != savedRegionFile) {
        // Need to fetch different region file
        val region = fetchRegion(baseUrl, newRegionFile)
        // Cache it, update DataStore
        // UI will show different packs (new region's content)
    }

    dataStore.set(DETECTED_COUNTRY, currentCountry)
}

// Already-downloaded packs remain accessible!
// User just sees different BROWSING content, not different downloads
```

### Edge Case 7: Version Bumped But Same Region

```kotlin
// index.json v=1 → v=2 but regions.PK still = 1
// This means: categories might have changed, but PK packs haven't

// Check per-region version:
val regionVersion = index.regions[regionFile] ?: index.zones[regionFile]?.v
if (regionVersion == cachedRegionV) {
    // Skip fetching region file → use cache
} else {
    // Fetch fresh region file
}
```

### Error Handling Summary

```
┌─────────────────────┬──────────────────────────────────────┐
│ Failure              │ Fallback                             │
├─────────────────────┼──────────────────────────────────────┤
│ index.json fails    │ Use cached → Use bundled → Show error│
│ region.json fails   │ Try _default → Use cached → Error    │
│ Country detect fails│ Default to "US"                      │
│ Image load fails    │ Coil shows placeholder/error drawable│
│ Pack download fails │ Show retry button per pack           │
│ Zero packs in tab   │ Hide that tab                        │
│ Country changes     │ Re-resolve, keep downloads           │
│ CDN is down         │ Everything works from cache           │
└─────────────────────┴──────────────────────────────────────┘
```

---

## Quick Reference: All URLs

```
Given: baseUrl = "https://hafizg.github.io/ai_sticker_maker"

Bootstrap:
  GET {baseUrl}/index.json

Region data:
  GET {baseUrl}/regions/PK.json
  GET {baseUrl}/regions/_arab.json
  GET {baseUrl}/regions/_default.json

Pack tray icon:
  GET {baseUrl}/packs/pk-funny-urdu/tray_icon.webp

Sticker image:
  GET {baseUrl}/packs/pk-funny-urdu/1.webp
  GET {baseUrl}/packs/pk-funny-urdu/2.webp
  GET {baseUrl}/packs/pk-funny-urdu/3.webp

Formula:
  Index:       {baseUrl}/index.json
  Region:      {baseUrl}/regions/{regionFile}.json
  Tray:        {baseUrl}/packs/{packId}/tray_icon.webp
  Sticker:     {baseUrl}/packs/{packId}/{n}.webp  (n = 1..count)
```

---

## The Complete Picture

```
1 country code
  ↓
2 HTTP requests (index + region)
  ↓
gives you EVERYTHING:
  ✓ categories (tabs)
  ✓ packs (grid items)
  ✓ sticker counts (per pack)
  ✓ image URLs (derived from baseUrl + packId + number)
  ✓ version (for cache invalidation)
  ✓ offline support (cached JSONs + downloaded packs)

Zero extra API calls needed.
All filtering is client-side.
All URLs are computed, not stored.
```

---

*Read time: ~20 minutes. Use as reference when implementing.*
