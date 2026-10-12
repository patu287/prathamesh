# KERN Coffee & Bakery — Warm Organic Minimalism (Aesop) edition

A static site with the same content, photos and interactions as the Swiss edition in `../cafe/`, restyled in a warm, earthy, organic direction.

## Design notes
- **Palette:** linen `#F1E9DA`, paper `#F7F1E6`, sand `#E4D5BC`, clay `#CDB99A`, cream `#FBF7EF`, ink `#2B2119`, espresso `#3B2A1E`, brown `#6E5240`, terra `#B5593A`, olive `#5E6134`, sage `#A9AC8C`.
- **Type:** Cormorant Garamond (display, italics for accents) with Inter (body, small caps labels).
- **Texture:** a fixed SVG noise overlay gives a paper/linen grain across the page.
- **Photography:** arch-topped frames with a grain overlay and a soft sepia grade, for a film-like feel.
- **Illustration:** hand-drawn line doodles (cup, bean, leaf) as stroke-draw SVG paths.
- **Layout:** generous whitespace and asymmetric columns. Breakpoints at 1100, 880 and 560px. Reduced-motion preferences are respected.

## Run locally
Serve the folder with any static server, for example:

```
python3 -m http.server 8083 --bind 0.0.0.0
```

Then open http://localhost:8083.
