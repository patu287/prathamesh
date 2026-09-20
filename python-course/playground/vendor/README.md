# Vendored Pyodide

These files are the [Pyodide](https://pyodide.org) runtime that lets the
`playground/` run **Python 3.12 in the browser**, with no installation and no
internet connection.

| File                | Size    | What it is |
|---------------------|---------|------------|
| `pyodide.js`        | 15 KB   | loader (defines `loadPyodide`) |
| `pyodide.asm.js`    | 1.2 MB  | glue code for the WebAssembly module |
| `pyodide.asm.wasm`  | 9.7 MB  | CPython 3.12 compiled to WebAssembly |
| `python_stdlib.zip` | 2.3 MB  | the Python standard library |
| `pyodide-lock.json` | 104 KB  | package metadata (309 packages available) |

* **Version:** Pyodide 0.26.2 (CPython 3.12.1)
* **Where it came from:** `npm pack pyodide@0.26.2` (the files are copied
  verbatim from the published npm package)
* **Licence:** Pyodide is distributed under the **MPL-2.0** licence; CPython and
  the bundled standard library are under the **PSF Licence**. See
  <https://pyodide.org/en/stable/project/license.html>.

## Why vendor it instead of using a CDN?

The playground must work offline (on a train, in a lab with no wifi) and on
localhost with `python3 serve.py`. Copying the runtime into the repository costs
~14 MB once and removes every network dependency.

## Updating it

```bash
mkdir -p /tmp/pyodide && cd /tmp/pyodide
npm pack pyodide@0.26.2        # or a newer version
tar xzf pyodide-*.tgz
cp package/{pyodide.js,pyodide.asm.js,pyodide.asm.wasm,python_stdlib.zip,pyodide-lock.json} \
   <repo>/python-course/playground/vendor/pyodide/
```

Then reload the playground — `python-course/playground/worker.js` is the only
file that knows about the runtime.
