# Almari · आलमारी

A personal wardrobe manager. Catalogue your clothes by category, then build outfits from them.

**Zero dependencies. No build step. No backend. Works fully offline** — plain HTML, CSS and
vanilla JS, with photos stored as Blobs in IndexedDB. Nothing ever leaves the device.

```
almari/
├── index.html    structure: header, search, category nav, shelf grid, sheets, tab bar
├── styles.css    design system (paper + indigo + wooden shelves), mobile-first
├── data.js       taxonomy, colour palette, helpers, sample wardrobe
├── store.js      IndexedDB storage (localStorage fallback), image compression, backup
└── app.js        state, filtering, rendering, all UI events
```

## Run it

Any static file server works:

```bash
cd almari
python3 -m http.server 5173 --bind 0.0.0.0
# → http://localhost:5173
```

Opening `index.html` directly also works in most browsers.

## The taxonomy: two axes, not one

The single most important design decision in the app. A flat category list breaks the outfit
builder, because it can't tell what a valid combination is.

| Axis | Purpose | Values |
|---|---|---|
| **Slot** | where it goes on the body → drives the outfit builder | `top` · `bottom` · `outer` · `foot` · `accessory` |
| **Type** | what the garment actually is → drives browsing and filters | `shirt`, `kurta`, `jeans`, `pyjama`, `nehru-jacket`, `kolhapuri`, … 37 in total |

So a **kurta is a `top`**, a **Nehru jacket is `outer`** worn over it, and **pyjama is a
`bottom`**. Occasion (`Casual`, `Office`, `Wedding`, `Festival`, …) and season (`Summer`,
`Monsoon`, `Winter`, `All year`) are multi-select tags, because one white shirt can be both
office and wedding wear.

## Data model

**Item**

```js
{
  id: 'i…',              // Store.uid()
  photoBlob: Blob|null,  // JPEG, downscaled to ≤1000px @ q0.80 (~60–120 KB)
  name: 'Indigo Kurta',  // auto-generated from colour + type if left blank
  slot: 'top',
  type: 'kurta',
  colors:    ['navy'],           // ids from COLORS
  occasions: ['Festival'],
  seasons:   ['Summer','Monsoon'],
  size: 'M', brand: 'Manyavar', fabric: 'Cotton', pattern: 'Solid',
  price: 1299, bought: '2026-08-01',
  notes: 'Dry clean only.',
  laundry: 'clean',              // clean | worn | dirty | cleaning
  worn: 0, lastWorn: null,
  createdAt: 1757…, updatedAt: 1757…
}
```

**Look** — references items by id, never by embedding them, so editing a shirt updates every
look it appears in.

```js
{
  id: 'o…',
  name: 'Office Classic',
  slots: {
    top: 'i…', layer: null, bottom: 'i…',
    outer: null, foot: 'i…', accessory: ['i…', 'i…']
  },
  occasions: ['Office'], seasons: ['All year'],
  rating: 4, notes: 'Monday-to-Thursday rotation.',
  worn: 0, lastWorn: null,
  createdAt: 1757…, updatedAt: 1757…
}
```

Photos live in IndexedDB rather than localStorage on purpose — localStorage caps out around
5 MB, which is roughly 60 photos. IndexedDB comfortably holds hundreds. Looks are in a second
IndexedDB table added at schema version 2; opening a version-1 database upgrades it in place.

If IndexedDB is unavailable (`file://` pages), everything falls back to localStorage with
photos as data URLs. The active backend is shown in the ⋯ menu.

## Built in v1 — the wardrobe

- Category tabs (Everything / Tops / Bottoms / Outerwear / Footwear / Accessories) with live counts
- Type filter chips, multi-select, scoped to the active category
- Search across name, type, colour, brand, fabric, occasion, season and notes (`Ctrl/⌘+K`)
- Shelf grid with photo cards; photo-less items render a colour-wash tile with a hanger
- Add / edit / delete via a bottom sheet (dialog on desktop), camera or gallery capture
- Item detail sheet with every attribute
- Sort by newest, oldest, name or type
- JSON export / import for backups, plus a sample wardrobe for demoing
- Delete and erase use tap-twice-to-confirm instead of native dialogs
- Laundry status, cycled by tapping the badge on a card

## Built in v2 — Outfits

A **Look** is one item per slot. The builder maps each Look slot onto a wardrobe slot via
`LOOK_SLOTS.from`, which is what makes the two-axis taxonomy pay off:

| Look slot | Draws from | Required | Notes |
|---|---|---|---|
| Top | `top` | yes | shirt, tee, kurta |
| Layer | `top` | no | a *second* top — sweater over a shirt |
| Bottom | `bottom` | yes | jeans, chinos, pyjama |
| Outerwear | `outer` | no | jacket, blazer, Nehru jacket |
| Footwear | `foot` | yes | shoes, sandals, Kolhapuri |
| Accessories | `accessory` | no | **multi-select** — watch, belt, cap |

Because `layer` and `top` both draw from the `top` pool, shirt-under-sweater works, while
kurta + Nehru jacket resolves naturally as `top` + `outer`. An item already used in one slot
is disabled in the others, so nothing can appear twice.

- **Live collage preview** — the hero piece left, bottom and footwear stacked right, with a
  `+N` badge for layer/outerwear/accessories
- **Item picker** with search, sorted by compatibility: pieces sharing an occasion with what
  you have already chosen float to the top and get a "Matches" badge
- **Auto-tagging** — occasion and season are inferred as the intersection of the chosen
  pieces, unless you set them yourself
- **Shuffle** — builds a valid random look from wearable items, biased toward the active
  occasion filter, then opens the builder so you can tweak it
- **Combination counter** — "4 tops × 3 bottoms × 3 shoes = 36 possible looks"
- **Wear this** — logs the wear on the look *and* every piece in it, and marks them worn
- **Duplicate**, star rating, notes, and looks that survive item deletion by showing a
  "Needs top" badge instead of breaking

### Laundry state

Items carry `laundry`: `clean` → `worn` → `dirty` → `cleaning`. Tap the badge on a wardrobe
card to cycle it, or set it in the item detail sheet.

The picker offers **clean and worn-once** by default — the clothes you would actually put on
today — and hides dirty and dry-cleaner items behind an "Include dirty" switch. Wearing a
look moves its pieces to `worn`.

## Roadmap

**Feature 3 — the daily hook.** A "Wear today" card driven by Kolhapur weather + occasion +
least-recently-worn, and a wear calendar.

**Later.** Cost-per-wear, neglect alerts ("not worn in 6 months" → donate or sell), wardrobe
colour palette and "missing piece" suggestions, duplicate detection, festival and monsoon
modes, tailor/alteration notes, packing lists, multiple closets, photo snapshots of saved
looks.

## Packaging for Android

Because there is no build step, the whole folder drops into a WebView shell as-is — the same
pipeline used in `../android`. Copy the files into `android/app/src/main/assets/` and load
`index.html`. `capture="environment"` on the photo input opens the camera directly; the
gallery button is a cloned input without it.
