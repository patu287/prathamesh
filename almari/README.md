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
  worn: 0, lastWorn: null,       // reserved for feature 3
  createdAt: 1757…, updatedAt: 1757…
}
```

Photos live in IndexedDB rather than localStorage on purpose — localStorage caps out around
5 MB, which is roughly 60 photos. IndexedDB comfortably holds hundreds.

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

## Roadmap

**Feature 2 — Outfits.** Build a "Look" from one item per slot, validate the pairing with the
slot axis, save and rate looks, then a wear calendar.

**Feature 3 — the daily hook.** Laundry state (`clean` / `worn once` / `dirty` / at the
dry-cleaner) so the builder only offers clean clothes, and a "Wear today" card driven by
Kolhapur weather + occasion + least-recently-worn.

**Later.** Cost-per-wear, neglect alerts ("not worn in 6 months" → donate or sell), wardrobe
colour palette and "missing piece" suggestions, duplicate detection, festival and monsoon
modes, tailor/alteration notes, packing lists, multiple closets.

## Packaging for Android

Because there is no build step, the whole folder drops into a WebView shell as-is — the same
pipeline used in `../android`. Copy the files into `android/app/src/main/assets/` and load
`index.html`. `capture="environment"` on the photo input opens the camera directly; the
gallery button is a cloned input without it.
