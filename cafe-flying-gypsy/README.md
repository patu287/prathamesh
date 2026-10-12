# Cafe Flying Gypsy's — website

Static site. **No build step, no dependencies, no backend.** Plain HTML, CSS and vanilla JS.

```
cafe-flying-gypsy/
├── index.html    every section: nav, hero, story, signatures, menu, hours, gallery, reviews, visit
├── styles.css    design system — turquoise / terracotta / amber / cream, responsive, animated
├── app.js        all content data + tabs, filters, lightbox, WhatsApp booking
└── images/       the cafe's own photographs — no stock, no AI-generated imagery
```

## Run it

```bash
cd cafe-flying-gypsy
python3 serve.py 8080
# → http://localhost:8080
```

**Use `serve.py`, not `python3 -m http.server`.** The plain server sends no cache
headers, so after an edit your browser keeps serving the old `styles.css` and
nothing appears to change. `serve.py` sends `Cache-Control: no-store` on every
response, so a normal refresh always shows the current files.

Opening `index.html` directly also works.

> Still seeing an old version? The asset URLs are versioned
> (`styles.css?v=…` and `app.js?v=…` in `index.html`). Bump that string when you
> make a change and every browser is forced to re-fetch. A hard refresh
> (Ctrl/Cmd + Shift + R) also works.

---

## Where everything lives

Everything you'd ever want to change is a plain JavaScript array at the top of `app.js`.
No templates, no build, no framework.

| What | Where in `app.js` |
| --- | --- |
| Phone, WhatsApp, Instagram, email, map coords, reviews link | `CONFIG` |
| The six "Signatures" cards | `SIGNATURES` |
| **The full menu — 113 items in 11 categories** | `MENU` |
| The 24-hour timeline | `HOURS` |
| Gallery photos, captions, categories | `GALLERY` |
| Reviews | `REVIEWS` |

### Editing the menu

```js
{ name:'Masala Maggi', price:99, desc:'The plain-and-perfect original.', tag:'Most loved' }
```

- `price` is a plain number — the site renders `₹99` automatically.
- `tag` is optional. Allowed values: `'Most loved'` (amber), `'Spicy'` (terracotta),
  `'Jain'` (plum), `'Egg'` (amber). Anything else falls back to the green veg pill.
- To add a category, copy a whole `{ id, label, note, items:[…] }` block. The tab,
  the panel and the count all generate themselves.

### Colours and fonts

Every colour is a CSS custom property in `:root` at the top of `styles.css`.
The palette was sampled directly from the cafe's own photographs:

```
--teal #1E9E9C   --teal-deep #0E5F63   --teal-dark #0A4A4E
--terra #B4663A  --amber #E9A33C       --cream #FDF7EC
```

---

## Content sources

Everything on the page is real. Nothing here is invented.

| Content | Source |
| --- | --- |
| Menu items & prices | The cafe's printed card (all 113 items) |
| Address, phone, email, domain | The cafe's own site, `cafeflyinggypsys.online` |
| 24-hour opening, all 7 days | Cafe's own listing + independent review sites |
| Instagram `@cafeflyinggypsys` | Instagram |
| Reviews & 4.5 rating / 1,400+ reviews | Public Google reviews, reproduced as written |
| ₹450 cost for two | magicpin listing |
| ₹250/hour pool table | Google review |
| Pool table, board games, books, resident dogs | Public Google & Reddit reviews |
| 18 photographs | Uploaded by the owner |

---

## Facts hard-coded in the page

- **Address:** 1201-A/4, GH Patil Path, Shivajinagar, Pune 411004
- **Landmarks:** opposite ICICI Bank, behind Ghole Road, near FC Road
- **Hours:** open 24 hours, seven days
- **Phone / WhatsApp:** +91 90111 47147
- **Email:** contact@cafeflyinggypsys.online
- **Map:** 18.5240, 73.8425
- **Serving Pune since:** 2008

If any of those ever change, they live in `CONFIG` (`app.js`) plus the footer and
visit sections of `index.html`, and the `application/ld+json` block at the very
bottom of `index.html`.

---

## Accessibility

- Landmark elements and a skip link; visible focus rings on everything.
- Menu tabs are a proper ARIA tablist — clicking and arrow keys / Home / End all work.
- Gallery opens by mouse, Enter or Space; the lightbox closes on Escape and
  moves with arrow keys or a swipe.
- Every image has a written description; every icon button has an accessible name.
- All motion is disabled under `prefers-reduced-motion`.
- `width` and `height` are set on gallery images so nothing shifts as they load.

## About the photographs

18 photographs, all the owner's own. Each was renamed to something descriptive
(`gypsy-girl-mural.jpg`, `cheesy-loaded-fries.jpg`, …) so the code reads cleanly
and new photos are easy to slot in.

They are **243 px wide at native resolution**, which is the size they arrived in.
The layout is deliberately built around that limit — images are shown as framed
art objects rather than stretched full-bleed. **If higher-resolution originals
exist, drop them into `images/` with the same filenames and the site gets
sharper with zero code changes.**
