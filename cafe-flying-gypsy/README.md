# Cafe Flying Gypsy's — website

Static site. **No build step, no dependencies, no backend.** Plain HTML, CSS and vanilla JS.

```
cafe-flying-gypsy/
├── index.html    all sections: nav, hero, about, menu, experience, gallery, reviews, visit
├── styles.css    design system (turquoise + terracotta + cream), responsive, animations
├── app.js        menu data, gallery data, reviews, tabs, filters, lightbox, WhatsApp form
└── images/       the cafe's own photographs — no stock, no AI-generated imagery
```

## Run it

```bash
cd cafe-flying-gypsy
python3 -m http.server 8080 --bind 0.0.0.0
# → http://localhost:8080
```

Opening `index.html` directly in a browser also works.

## ⚠️ Updating prices — the one thing left to do

Every menu item lives in the `MENU` array at the top of `app.js`.
Prices that are **real** (taken from the cafe's public Google reviews) already have numbers.
Everything showing a muted `—` on the site is still unknown.

To fill one in, change `null` to a number:

```js
{ name:'Cheese Maggi', price:null, … }   // →  { name:'Cheese Maggi', price:179, … }
```

That is the only edit needed — the site renders `₹179` automatically.

## Other things worth knowing

| What | Where |
| --- | --- |
| Phone / WhatsApp / Instagram / map coords | `CONFIG` object, top of `app.js` |
| Menu categories, items, tags, descriptions | `MENU` array, `app.js` |
| Gallery photos, captions, categories | `GALLERY` array, `app.js` |
| Reviews | `REVIEWS` array, `app.js` |
| Colours, fonts, spacing | CSS custom properties in `:root`, top of `styles.css` |
| Structured data (Google rich results) | `application/ld+json` block at the bottom of `index.html` |

## Facts currently hard-coded in the page

- Address: 1201-A/4, GH Patil Path, Shivajinagar, Pune 411004
- Landmarks: off FC Road, behind Ghole Road, near ICICI Bank, opposite Kiosk Kaffee
- Open 24 hours, every day
- Pure vegetarian · pet-friendly · self-service
- Pool table ₹250/hour, board games, cards, books
- Google rating 4.5 from 1,400+ reviews
- Coordinates 18.5240, 73.8425

## Accessibility & performance notes

- Landmark elements, `aria-*` on all interactive controls, keyboard-operable tabs and lightbox
  (arrows, Home/End, Escape), visible focus rings, skip link.
- Gallery images are lazy-loaded with explicit `width`/`height` to avoid layout shift.
- All animation honours `prefers-reduced-motion`.
- Total page weight of imagery: ~1.2 MB across 18 photos.
