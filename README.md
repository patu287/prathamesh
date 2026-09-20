# prathamesh

Two things live in this repository:

| | What | Where |
|---|------|-------|
| 🐍 | **Python course: zero → intermediate → basic DSA** — 16 lessons, 16 exercise sets, 12 DSA topics and 21 auto-graded problems, plus a browser playground that runs Python offline (Pyodide/WebAssembly) | [`python-course/`](python-course/README.md) |
| 🛍️ | **Vendora** — a local-marketplace prototype (Vite + vanilla JS) with an Android wrapper | [`index.html`](index.html), [`app.js`](app.js), [`android/`](android/) |

## Start the Python course

```bash
# option A — the playground (no installation, runs Python in the browser)
cd python-course && python3 serve.py
#   → http://localhost:8080/python-course/playground/index.html

# option B — real files in a real terminal
python3 python-course/lessons/lesson_01_hello.py
python3 python-course/exercises/ex_01_basics.py
python3 python-course/tools/grade.py            # score all exercises + problems
```

Full guide, curriculum and study plan: **[python-course/README.md](python-course/README.md)**
One-page syntax reference: **python-course/CHEATSHEET.md**

## Vendora (web + Android)

```bash
npm install
npm run dev        # http://localhost:5173
```

The Android sources and build tooling are under `android/`, `wardrobe-android/`
and `reset/`.
