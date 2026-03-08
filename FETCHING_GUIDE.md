# Fetching Categories & Packs — Complete Guide (v2)

### How Your Android App Consumes the Country-First Sticker CDN

---

## Table of Contents

1. [The Big Picture — 1 Request, 1 Country Code](#1-the-big-picture)
2. [Detect Country Code](#2-detect-country-code)
3. [Fetch Country JSON](#3-fetch-country-json)
4. [Filter Packs by Category (Tabs)](#4-filter-packs-by-category-tabs)
5. [Build Image URLs](#5-build-image-urls)
6. [Complete Flow — Every Scenario](#6-complete-flow--every-scenario)
7. [Caching Strategy](#7-caching-strategy)
8. [Offline Mode](#8-offline-mode)
9. [Data Models (Kotlin)](#9-data-models-kotlin)
10. [Full Implementation — Step by Step](#10-full-implementation--step-by-step)
11. [Edge Cases & Error Handling](#11-edge-cases--error-handling)
12. [v1 → v2 Migration Cheat Sheet](#12-v1--v2-migration-cheat-sheet)

---

## 1. The Big Picture

```
Your app needs exactly:
  1 country code  (detected from device)
  1 HTTP request  (country file — self-contained)

That gives you:
  ✓ All categories (tabs) for that country
  ✓ All packs in display order
  ✓ All sticker filenames per pack
  ✓ Base URL for all images
  ✓ Version for cache invalidation
```

### Visual Flow

```
┌──────────────┐                           ┌──────────────┐
│              │  GET /countries/PK.json    │              │
│  Android App │ ──────────────────────→   │  GitHub CDN  │
│              │                           │              │
│  detect      │  ←─────────────────────   │              │
│  country="PK"│  {                        │              │
│              │    categories,            │              │
│              │    packs (with stickers), │              │
│              │    baseUrl, v             │              │
│              │  }                        │              │
└──────────────┘                           └──────────────┘
        │
        ↓
  Show tabs + packs
  Images: {baseUrl}/packs/{id}/{sticker}
```

**That's it. One request. No fallback chains. No zone resolution.**

---

## 2. Detect Country Code

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

---

## 3. Fetch Country JSON

### The Only Request You Need

```
GET https://hafizg.github.io/ai_sticker_maker/countries/{COUNTRY_CODE}.json
```

### Example: PK.json

```
GET https://hafizg.github.io/ai_sticker_maker/countries/PK.json
```

### Response

```json
{
  "v": 2,
  "baseUrl": "https://hafizg.github.io/ai_sticker_maker",
  "country": "PK",
  "categories": [
    { "id": "funny",     "name": "Funny"     },
    { "id": "greetings", "name": "Greetings" },
    { "id": "sports",    "name": "Sports"    },
    { "id": "emotions",  "name": "Emotions"  },
    { "id": "religious", "name": "Religious"  },
    { "id": "festivals", "name": "Festivals"  },
    { "id": "love",      "name": "Love"       },
    { "id": "trending",  "name": "Trending"   },
    { "id": "extra",     "name": "Extra ★"    }
  ],
  "packs": [
    {
      "id": "pk-funny-urdu",
      "name": "Funny Urdu Stickers",
      "cat": ["funny"],
      "count": 10,
      "tray": "1.webp",
      "stickers": ["1.webp", "2.webp", "3.webp", "4.webp", "5.webp",
                    "6.webp", "7.webp", "8.webp", "9.webp", "10.webp"]
    },
    {
      "id": "pk-cricket-fans",
      "name": "Cricket Fans PK",
      "cat": ["sports"],
      "count": 8,
      "tray": "1.webp",
      "stickers": ["1.webp", "2.webp", "3.webp", "4.webp",
                    "5.webp", "6.webp", "7.webp", "8.webp"]
    },
    {
      "id": "global-emoji-remix",
      "name": "Emoji Remix",
      "cat": ["funny", "emotions"],
      "count": 15,
      "tray": "1.webp",
      "stickers": ["1.webp", "2.webp", "3.webp", ... "15.webp"]
    }
  ]
}
```

### What You Get (Everything In One Response)

| Field | What It Is | How You Use It |
|---|---|---|
| `v` | Version number | Compare with cached version. Same → skip re-fetch |
| `baseUrl` | CDN root URL | Prefix for ALL image URLs |
| `country` | Country code | Confirmation of which country file was served |
| `categories` | Tab definitions (only this country's tabs) | Render horizontal scrollable tabs |
| `packs` | Full pack list with sticker filenames | Render grid, build image URLs |
| `packs[].tray` | First sticker filename | Pack thumbnail |
| `packs[].stickers` | Array of filenames | Exact sticker list (respects `hidden`) |
| `packs[].count` | Number of visible stickers | Display "X stickers" badge |

### Fallback for Unknown Countries

```kotlin
suspend fun fetchCountryData(baseUrl: String, country: String): CountryResponse {
    return try {
        // Try exact country
        httpClient.get("$baseUrl/countries/$country.json").body()
    } catch (e: ClientRequestException) {
        if (e.response.status == HttpStatusCode.NotFound) {
            // Country not in CDN → use _default
            httpClient.get("$baseUrl/countries/_default.json").body()
        } else throw e
    }
}
```

**Only 2 possible outcomes:**
1. Country file exists → use it
2. 404 → fetch `_default.json`

No zones. No resolution chain. No mental gymnastics.

---

## 4. Filter Packs by Category (Tabs)

All filtering is **client-side**. No extra API calls.

### The Core Logic

```kotlin
// You already have everything from 1 request:
val data: CountryResponse = fetchCountryData(baseUrl, "PK")
val categories = data.categories   // tabs for PK
val allPacks = data.packs          // packs for PK

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
  ✓ pk-ramadan-memes      → "funny" ✅ (also "religious")
  ✓ global-emoji-remix    → "funny" ✅ (also "emotions")
  ✓ global-reactions      → "funny" ✅

  Result: 4 packs shown
```

#### Tab: Religious
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

#### Tab: Trending
```
  (no pack has "trending" for PK)

  Result: 0 packs → HIDE THIS TAB
```

### Final Visible Tabs for PK

```
[Funny (4)] [Religious (2)] [Sports (1)] [Emotions (1)] [Love (1)] [Festivals (1)] [Extra ★ (2)]

Hidden: Greetings, Trending (no packs)
```

### Multi-Category Packs

```
pk-ramadan-memes → cat: ["funny", "religious"]

  Shows in Funny tab     ✅
  Shows in Religious tab ✅
  Same pack, same ID
  Download it from Funny → shows "Downloaded ✅" in Religious too
```

### Per-Country Category Control

Notice that **categories are per-country** in v2:

```
PK.json → categories: ["funny", "greetings", "sports", "emotions",
                         "religious", "festivals", "love", "trending", "extra"]

SA.json → categories: ["funny", "greetings", "emotions", "religious",
                         "festivals", "love", "trending", "extra"]
                         ↑ No "sports" tab for Saudi Arabia!
```

This is controlled in `_master.json`:
```json
"SA": {
  "categories": ["funny", "greetings", "emotions", "religious", "festivals", "love", "trending", "extra"],
  "packs": [...]
}
```

---

## 5. Build Image URLs

### v2: Sticker filenames are in the JSON

Unlike v1 where you generated `{n}.webp` from count, v2 gives you the **actual filenames**:

```json
"stickers": ["1.webp", "2.webp", "3.webp", "4.webp", "5.webp"]
```

This means hidden stickers are already excluded. No client-side filtering needed.

### Tray Icon (pack thumbnail)

```
{baseUrl}/packs/{pack.id}/{pack.tray}
```

```
Examples:
https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/1.webp
https://hafizg.github.io/ai_sticker_maker/packs/global-emoji-remix/1.webp
```

### Individual Sticker

```
{baseUrl}/packs/{pack.id}/{sticker}
```

```
Pack: pk-funny-urdu
  stickers: ["1.webp", "2.webp", "3.webp", "4.webp", "5.webp",
             "6.webp", "7.webp", "8.webp", "9.webp", "10.webp"]

Sticker 1:  https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/1.webp
Sticker 2:  https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/2.webp
...
Sticker 10: https://hafizg.github.io/ai_sticker_maker/packs/pk-funny-urdu/10.webp
```

### Why Explicit Filenames Are Better Than Count-Based

| | v1 (count-based) | v2 (explicit filenames) |
|---|---|---|
| How | `count: 10` → generate 1..10 | `stickers: ["1.webp", "2.webp", ...]` |
| Hidden stickers | Not supported | Already excluded from array |
| Non-sequential names | Not possible | Supported (e.g. `"hero.webp"`) |
| Client logic | `(1..count).map { "$it.webp" }` | `stickers.map { it }` — use directly |

### Kotlin Helper Functions

```kotlin
fun trayIconUrl(baseUrl: String, pack: Pack): String {
    return "$baseUrl/packs/${pack.id}/${pack.tray}"
}

fun stickerUrl(baseUrl: String, packId: String, sticker: String): String {
    return "$baseUrl/packs/$packId/$sticker"
}

fun allStickerUrls(baseUrl: String, pack: Pack): List<String> {
    return pack.stickers.map { "$baseUrl/packs/${pack.id}/$it" }
}

// Usage:
val data = fetchCountryData(baseUrl, "PK")
val pack = data.packs[0]  // pk-funny-urdu

val tray = trayIconUrl(data.baseUrl, pack)
// → ".../packs/pk-funny-urdu/1.webp"

val stickers = allStickerUrls(data.baseUrl, pack)
// → [".../pk-funny-urdu/1.webp", ".../pk-funny-urdu/2.webp", ... ]
```

---

## 6. Complete Flow — Every Scenario

### Scenario 1: First Launch (PK User, Online)

```
1. App opens
   │
2. Detect country code
   │  TelephonyManager → "PK"
   │
3. GET https://hafizg.github.io/ai_sticker_maker/countries/PK.json
   │  ← Response: categories, packs (with sticker lists), baseUrl, v=2
   │  → Cache to: filesDir/cache/country_PK.json
   │  → Save to DataStore: cached_country = "PK", cached_v = 2
   │
4. Filter categories: hide empty tabs
   │  Visible: Funny(4), Religious(2), Sports(1), Emotions(1),
   │           Love(1), Festivals(1), Extra★(2)
   │
5. Show UI: tabs + pack grid
   │  Tray icons loaded via Coil: {baseUrl}/packs/{id}/{tray}
   │
6. Network cost: ~8KB (one request)
```

### Scenario 2: Return Visit (Same Version, Online)

```
1. App opens → Detect: "PK"
   │
2. GET countries/PK.json
   │  ← v=2
   │  Compare: cached_v == 2? → YES, same version
   │  → Skip parsing, use cached file
   │
3. Show UI immediately from cache
   │
4. Network cost: ~8KB (could use HTTP 304 Not-Modified for 0 bytes)
```

### Scenario 3: Return Visit (New Version, Online)

```
1. App opens → Detect: "PK"
   │
2. GET countries/PK.json
   │  ← v=3 (version bumped!)
   │  Compare: cached_v == 2, new == 3 → DIFFERENT
   │
3. Cache new file
   │  Save: cached_v = 3
   │  New categories? New packs? All here.
   │
4. Show updated UI
   │
5. Network cost: ~8KB
```

### Scenario 4: Offline (Cached)

```
1. App opens → No network
   │
2. Read from DataStore: cached_country = "PK"
   │  Read: filesDir/cache/country_PK.json
   │  Found? → YES, use it
   │
3. Show UI from cache ✅
   │
4. Network cost: 0KB
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

### Scenario 6: Lebanon User (Alias Country)

```
1. Detect country: "LB"
   │
2. GET countries/LB.json
   │  ← File exists! (CI generated it from "same_as": "AE")
   │  Contains same packs/categories as AE but "country": "LB"
   │
3. Show UI ✅
   │
   No zone resolution needed.
   CDN already has LB.json pre-generated.
```

### Scenario 7: Japan User (Unlisted Country)

```
1. Detect country: "JP"
   │
2. GET countries/JP.json
   │  ← 404 Not Found (JP not in _master.json)
   │
3. Fallback: GET countries/_default.json
   │  ← Global packs (still useful, never empty)
   │
4. Show UI with global content ✅
```

### v1 vs v2 Comparison

| Scenario | v1 | v2 |
|---|---|---|
| PK user | GET index.json → resolve → GET regions/PK.json | GET countries/PK.json |
| Lebanon | GET index.json → find zone "_arab" → GET regions/_arab.json | GET countries/LB.json |
| Japan | GET index.json → not found → GET regions/_default.json | GET countries/JP.json → 404 → GET countries/_default.json |
| Requests | Always 2 (sometimes 3) | Always 1 (sometimes 2 for unknown) |

---

## 7. Caching Strategy

### What to Cache Where

```
DataStore (key-value, tiny):
  ┌──────────────────────────┬───────────┐
  │ Key                      │ Example   │
  ├──────────────────────────┼───────────┤
  │ cached_country           │ "PK"      │
  │ cached_v                 │ 2         │
  │ detected_country         │ "PK"      │
  │ downloaded_packs         │ "pk-funny-urdu,global-emoji-remix" │
  └──────────────────────────┴───────────┘

Internal Storage (JSON file):
  filesDir/cache/
  └── country_PK.json          ← Full country response (one file!)

Coil Disk Cache (automatic):
  Tray icon images (auto-managed, LRU eviction)

Internal Storage (downloaded packs):
  filesDir/stickers/
  ├── pk-funny-urdu/
  │   ├── 1.webp
  │   ├── 2.webp
  │   └── 3.webp
  └── global-emoji-remix/
      ├── 1.webp
      └── ...
```

### Cache Decision Logic

```kotlin
suspend fun loadData(context: Context, baseUrl: String): CountryResponse {
    val country = detectCountryCode(context)
    val cachedCountry = dataStore.get(CACHED_COUNTRY)
    val cachedV = dataStore.get(CACHED_V) ?: -1

    // Try to fetch fresh data
    val data = try {
        val fresh = fetchCountryData(baseUrl, country)

        // Same version as cache? Skip processing
        if (country == cachedCountry && fresh.v == cachedV) {
            return readCacheFile("country_$country.json")!!.parse()
        }

        // New data — cache it
        cacheFile("country_$country.json", fresh.raw)
        dataStore.set(CACHED_COUNTRY, country)
        dataStore.set(CACHED_V, fresh.v)
        dataStore.set(DETECTED_COUNTRY, country)
        fresh
    } catch (e: Exception) {
        // Offline → read from cache
        readCacheFile("country_${cachedCountry ?: country}.json")?.parse()
            ?: throw NoDataException("No cached data")
    }

    return data
}
```

### Smarter: Use HTTP ETags

Since GitHub Pages supports `ETag` headers, you can avoid downloading unchanged data:

```kotlin
suspend fun fetchWithETag(url: String, cachedETag: String?): Pair<String?, String> {
    val response = httpClient.get(url) {
        cachedETag?.let { header("If-None-Match", it) }
    }

    return when (response.status) {
        HttpStatusCode.NotModified -> null to cachedETag!!  // Use cache
        HttpStatusCode.OK -> {
            val body = response.bodyAsText()
            val newETag = response.headers["ETag"] ?: ""
            body to newETag
        }
        else -> throw Exception("Unexpected: ${response.status}")
    }
}
```

---

## 8. Offline Mode

### Three Levels of Offline

```
Level 1: Online (normal)
  → Fetch fresh country JSON
  → Cache it
  → Show fresh UI

Level 2: Offline with Cache
  → Can't fetch → use cached country JSON
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
    fallback_default.json    ← Copy of _default.json at build time

Code:
  if (no cache && no network) {
      val data = assets.open("fallback_default.json").parse<CountryResponse>()
      // Shows global packs at minimum
  }
```

---

## 9. Data Models (Kotlin)

```kotlin
import kotlinx.serialization.Serializable

// ─── countries/{CC}.json ──────────────────────────────

@Serializable
data class CountryResponse(
    val v: Int,                           // 2
    val baseUrl: String,                  // "https://hafizg.github.io/ai_sticker_maker"
    val country: String,                  // "PK"
    val categories: List<Category>,       // tabs for this country
    val packs: List<Pack>                 // packs for this country (display order)
)

@Serializable
data class Category(
    val id: String,      // "funny"
    val name: String     // "Funny"
)

@Serializable
data class Pack(
    val id: String,              // "pk-funny-urdu"
    val name: String,            // "Funny Urdu Stickers"
    val cat: List<String>,       // ["funny"]
    val count: Int,              // 10
    val tray: String,            // "1.webp" (first sticker used as thumbnail)
    val stickers: List<String>   // ["1.webp", "2.webp", ..., "10.webp"]
)
```

### That's It — 3 Data Classes

Compare with v1 which needed 5 data classes:
```
v1: IndexResponse, Category, Zone, RegionResponse, Pack
v2: CountryResponse, Category, Pack  ← simpler
```

---

## 10. Full Implementation — Step by Step

### Step 1: Fetch Country Data

```kotlin
class StickerApi(private val httpClient: HttpClient) {

    suspend fun fetchCountry(baseUrl: String, countryCode: String): CountryResponse {
        return try {
            httpClient.get("$baseUrl/countries/$countryCode.json").body()
        } catch (e: ClientRequestException) {
            if (e.response.status == HttpStatusCode.NotFound) {
                // Unknown country → fallback
                httpClient.get("$baseUrl/countries/_default.json").body()
            } else throw e
        }
    }
}
```

### Step 2: Repository

```kotlin
class StickerRepository(
    private val data: CountryResponse
) {
    val baseUrl: String get() = data.baseUrl
    val country: String get() = data.country
    val allPacks: List<Pack> get() = data.packs

    // Categories that have at least 1 pack
    val visibleCategories: List<Category>
        get() = data.categories.filter { cat ->
            allPacks.any { cat.id in it.cat }
        }

    // Packs for a specific category tab
    fun packsFor(categoryId: String): List<Pack> {
        return allPacks.filter { categoryId in it.cat }
    }

    // Tray icon URL
    fun trayIconUrl(pack: Pack): String {
        return "$baseUrl/packs/${pack.id}/${pack.tray}"
    }

    // All sticker URLs for a pack
    fun stickerUrls(pack: Pack): List<String> {
        return pack.stickers.map { "$baseUrl/packs/${pack.id}/$it" }
    }

    // Single sticker URL
    fun stickerUrl(packId: String, sticker: String): String {
        return "$baseUrl/packs/$packId/$sticker"
    }

    // Search packs by name
    fun searchPacks(query: String): List<Pack> {
        return allPacks.filter { it.name.contains(query, ignoreCase = true) }
    }

    // Pack count per category (for badges)
    fun packCountPerCategory(): Map<String, Int> {
        return visibleCategories.associate { cat ->
            cat.id to allPacks.count { cat.id in it.cat }
        }
    }

    // Total stickers across all packs
    val totalStickers: Int get() = allPacks.sumOf { it.count }
}
```

### Step 3: ViewModel

```kotlin
@HiltViewModel
class StickerViewModel @Inject constructor(
    private val stickerApi: StickerApi,
    private val context: Application
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    private var repository: StickerRepository? = null
    var selectedCategory by mutableStateOf<Category?>(null)
        private set

    val currentPacks: List<Pack>
        get() = selectedCategory?.let { repository?.packsFor(it.id) } ?: emptyList()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val country = detectCountryCode(context)
                val baseUrl = "https://hafizg.github.io/ai_sticker_maker"
                val data = stickerApi.fetchCountry(baseUrl, country)

                repository = StickerRepository(data)
                selectedCategory = repository!!.visibleCategories.firstOrNull()

                _uiState.value = UiState.Success(
                    categories = repository!!.visibleCategories,
                    packs = currentPacks
                )
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Failed to load")
            }
        }
    }

    fun selectCategory(category: Category) {
        selectedCategory = category
        _uiState.value = UiState.Success(
            categories = repository!!.visibleCategories,
            packs = repository!!.packsFor(category.id)
        )
    }

    fun retry() = loadData()
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val categories: List<Category>, val packs: List<Pack>) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Step 4: Compose UI

```kotlin
@Composable
fun StickerScreen(viewModel: StickerViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Error -> ErrorView(state.message, onRetry = viewModel::retry)
        is UiState.Success -> StickerContent(state, viewModel)
    }
}

@Composable
fun StickerContent(state: UiState.Success, viewModel: StickerViewModel) {
    Column {
        // Category tabs
        ScrollableTabRow(
            selectedTabIndex = state.categories
                .indexOf(viewModel.selectedCategory)
                .coerceAtLeast(0)
        ) {
            state.categories.forEach { category ->
                Tab(
                    selected = category == viewModel.selectedCategory,
                    onClick = { viewModel.selectCategory(category) },
                    text = { Text(category.name) }
                )
            }
        }

        // Pack grid
        LazyVerticalGrid(columns = GridCells.Fixed(2)) {
            items(state.packs, key = { it.id }) { pack ->
                PackCard(pack = pack, viewModel = viewModel)
            }
        }
    }
}

@Composable
fun PackCard(pack: Pack, viewModel: StickerViewModel) {
    val repo = viewModel.repository ?: return

    Card(modifier = Modifier.padding(8.dp)) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            // Tray icon via Coil
            AsyncImage(
                model = repo.trayIconUrl(pack),
                contentDescription = pack.name,
                modifier = Modifier.size(96.dp)
            )
            Text(pack.name, style = MaterialTheme.typography.titleSmall)
            Text("${pack.count} stickers", style = MaterialTheme.typography.bodySmall)
        }
    }
}
```

### Step 5: Pack Detail Screen (Sticker Grid)

```kotlin
@Composable
fun PackDetailScreen(pack: Pack, baseUrl: String) {
    Column {
        Text(pack.name, style = MaterialTheme.typography.headlineSmall)
        Text("${pack.count} stickers")

        LazyVerticalGrid(columns = GridCells.Fixed(4)) {
            items(pack.stickers) { sticker ->
                AsyncImage(
                    model = "$baseUrl/packs/${pack.id}/$sticker",
                    contentDescription = sticker,
                    modifier = Modifier
                        .size(80.dp)
                        .padding(4.dp)
                        .clickable { /* share or add to keyboard */ }
                )
            }
        }
    }
}
```

---

## 11. Edge Cases & Error Handling

### Edge Case 1: Country Code Not Detected

```kotlin
val country = detectCountryCode(context)
// If all methods fail → returns "US"
// US.json exists in CDN (generated from "same_as": "_default")
// User sees global content → reasonable default
```

### Edge Case 2: Country File 404

```kotlin
// GET countries/JP.json → 404
// Automatic fallback to _default.json (built into fetchCountry)
```

### Edge Case 3: CDN Completely Down (First Launch)

```kotlin
try {
    val data = stickerApi.fetchCountry(baseUrl, country)
} catch (e: Exception) {
    // Option A: Show retry button
    showError("Connect to internet to get started")

    // Option B: Use bundled fallback from assets/
    val data = loadBundledDefault()
}
```

### Edge Case 4: Category Has Zero Packs

```kotlin
// Already handled by visibleCategories filter:
val visibleCategories = categories.filter { cat ->
    allPacks.any { cat.id in it.cat }
}
// Empty categories simply don't appear as tabs
```

### Edge Case 5: Hidden Stickers

```
_master.json: "pk-funny-urdu": { ..., "hidden": ["5.webp"] }

CI generates PK.json with:
  "stickers": ["1.webp", "2.webp", "3.webp", "4.webp", "6.webp", ...]
              ↑ no "5.webp" — already excluded

App doesn't need to know about hidden stickers.
It just uses the stickers array as-is.
```

### Edge Case 6: User Changes Country (travel / new SIM)

```kotlin
// On each app open:
val currentCountry = detectCountryCode(context)
val savedCountry = dataStore.get(DETECTED_COUNTRY)

if (currentCountry != savedCountry) {
    // Country changed! Fetch new country file
    val data = stickerApi.fetchCountry(baseUrl, currentCountry)
    // Cache it, update DataStore
    // UI shows different packs (new country's content)
    // Already-downloaded packs remain accessible!
    dataStore.set(DETECTED_COUNTRY, currentCountry)
}
```

### Edge Case 7: Pack In Multiple Tabs

```kotlin
// pk-ramadan-memes → cat: ["funny", "religious"]
// User downloads from Funny tab
// Goes to Religious tab → same pack.id → shows as downloaded

// Download state tracked by pack.id (not by category)
fun isDownloaded(packId: String) = downloadedPacks.contains(packId)
// Works across all tabs automatically
```

### Error Handling Summary

```
┌─────────────────────┬──────────────────────────────────────┐
│ Failure              │ Fallback                             │
├─────────────────────┼──────────────────────────────────────┤
│ country.json fails  │ Try _default.json → cache → error    │
│ Country detect fails│ Default to "US"                      │
│ Image load fails    │ Coil shows placeholder/error drawable│
│ Pack download fails │ Show retry button per pack           │
│ Zero packs in tab   │ Hide that tab                        │
│ Country changes     │ Fetch new country file, keep downloads│
│ CDN is down         │ Everything works from cache           │
│ Hidden sticker      │ Not in stickers[] — automatic        │
└─────────────────────┴──────────────────────────────────────┘
```

---

## 12. v1 → v2 Migration Cheat Sheet

If you had v1 code, here's exactly what changes:

### Data Models

```diff
- data class IndexResponse(val v, val baseUrl, val categories, val regions, val zones, val defaultRegion)
- data class Zone(val v, val countries)
- data class RegionResponse(val v, val packs)
- data class Pack(val id, val name, val cat, val count)
+ data class CountryResponse(val v, val baseUrl, val country, val categories, val packs)
+ data class Pack(val id, val name, val cat, val count, val tray, val stickers)
```

### Fetching

```diff
- // 2 requests + resolution
- val index = fetch("$baseUrl/index.json")
- val regionFile = resolveRegionFile(country, index)
- val region = fetch("$baseUrl/regions/$regionFile.json")
+ // 1 request
+ val data = fetch("$baseUrl/countries/$country.json")  // or _default on 404
```

### Image URLs

```diff
- fun trayIconUrl(pack: Pack) = "$baseUrl/packs/${pack.id}/tray_icon.webp"
- fun stickerUrl(pack: Pack, n: Int) = "$baseUrl/packs/${pack.id}/$n.webp"
+ fun trayIconUrl(pack: Pack) = "$baseUrl/packs/${pack.id}/${pack.tray}"
+ fun stickerUrl(pack: Pack, s: String) = "$baseUrl/packs/${pack.id}/$s"
```

### Categories

```diff
- val categories = index.categories  // global, same for all countries
+ val categories = data.categories   // per-country (controlled in _master.json)
```

### Sticker List

```diff
- val stickers = (1..pack.count).map { "$it.webp" }  // generated from count
+ val stickers = pack.stickers  // explicit list, hidden already excluded
```

### Cache Keys

```diff
- DataStore: cached_index_v, cached_region, cached_region_v
+ DataStore: cached_country, cached_v  // simpler!
```

---

## Quick Reference: All URLs

```
Given: baseUrl = "https://hafizg.github.io/ai_sticker_maker"

Country data (the ONLY request you make):
  GET {baseUrl}/countries/PK.json
  GET {baseUrl}/countries/_default.json     ← fallback for unknown countries

Country list (optional, for admin/debug):
  GET {baseUrl}/index.json

Pack tray icon:
  GET {baseUrl}/packs/pk-funny-urdu/1.webp  ← pack.tray value

Sticker image:
  GET {baseUrl}/packs/pk-funny-urdu/1.webp
  GET {baseUrl}/packs/pk-funny-urdu/2.webp
  GET {baseUrl}/packs/pk-funny-urdu/10.webp

Formula:
  Country:     {baseUrl}/countries/{countryCode}.json
  Fallback:    {baseUrl}/countries/_default.json
  Tray:        {baseUrl}/packs/{packId}/{pack.tray}
  Sticker:     {baseUrl}/packs/{packId}/{pack.stickers[n]}
```

---

## The Complete Picture

```
1 country code
  ↓
1 HTTP request (country JSON — self-contained)
  ↓
gives you EVERYTHING:
  ✓ categories (tabs, per-country)
  ✓ packs (grid items, display order)
  ✓ sticker filenames (explicit, hidden excluded)
  ✓ tray icon (first sticker)
  ✓ image URLs (baseUrl + packId + sticker)
  ✓ version (for cache invalidation)
  ✓ offline support (one cached JSON file)

Zero resolution logic.
Zero extra API calls.
All filtering is client-side.
All URLs are computed from 3 values: baseUrl, packId, stickerName.
```

---

*Read time: ~15 minutes. Use as reference when implementing.*
