# KERN — Coffee & Bakery (website)

A static, dependency-free one-page website for a fictional specialty café in Zürich.
Swiss / International Typographic Style: 12-column grid, flush-left type, one signal red, paper and ink palette, hairline rules and numbered labels.

## Run locally
    cd cafe
    python3 -m http.server 8080
Then open http://localhost:8080

## Files
- `index.html` — structure and content (menu, roasts, visit, reservation form)
- `styles.css` — design tokens, layout, animations, responsive and reduced-motion rules
- `script.js` — live open/closed status (Zürich time), menu tabs, count-up stats, scroll reveals, parallax, form validation
- `assets/` — generated photography

Fonts load from Google Fonts (Inter Tight, Inter, JetBrains Mono) with Helvetica/Arial fallbacks.
All café details (name, address, prices, phone) are placeholders.
