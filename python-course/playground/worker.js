/*
 * Pyodide worker: runs the Python files of this course completely in the
 * browser. The main thread sends the file contents (so unsaved edits are the
 * code that runs), this worker writes them into a virtual filesystem and then
 * executes the selected file with runpy — exactly like `python3 file.py`.
 */

importScripts("./vendor/pyodide/pyodide.js");

const VIRTUAL_ROOT = "/course";
let pyodidePromise = null;

function post(message) {
  self.postMessage(message);
}

function boot() {
  if (!pyodidePromise) {
    pyodidePromise = loadPyodide({
      indexURL: "./vendor/pyodide/",
      stdout: (text) => post({ type: "boot", text }),
      stderr: (text) => post({ type: "boot", text }),
    });
  }
  return pyodidePromise;
}

async function prepare(pyodide, files) {
  pyodide.FS.mkdirTree(VIRTUAL_ROOT);
  for (const [path, content] of Object.entries(files)) {
    const full = `${VIRTUAL_ROOT}/${path}`;
    const directory = full.split("/").slice(0, -1).join("/");
    if (directory) {
      pyodide.FS.mkdirTree(directory);
    }
    pyodide.FS.writeFile(full, content, { encoding: "utf8" });
  }
}

const BOOTSTRAP = `
import builtins, sys

sys.path.insert(0, "${VIRTUAL_ROOT}")
sys.argv = [SCRIPT_PATH] + ARGUMENTS

_STDIN_LINES = iter(STDIN_TEXT.splitlines())

def _playground_input(prompt=""):
    sys.stdout.write(str(prompt))
    try:
        return next(_STDIN_LINES)
    except StopIteration:
        raise EOFError("no more lines in the stdin box (add more input on the left)")

builtins.input = _playground_input
`;

async function run({ path, files, argv = [], stdin = "" }) {
  const started = performance.now();
  const pyodide = await boot();

  pyodide.setStdout({ batched: (text) => post({ type: "stdout", text }) });
  pyodide.setStderr({ batched: (text) => post({ type: "stderr", text }) });

  post({ type: "status", text: "writing files…" });
  await prepare(pyodide, files);

  const bootstrap = BOOTSTRAP
    .replace("${VIRTUAL_ROOT}", VIRTUAL_ROOT)
    .replace("SCRIPT_PATH", JSON.stringify(path))
    .replace("ARGUMENTS", JSON.stringify(argv))
    .replace("STDIN_TEXT", JSON.stringify(stdin));

  const script = `${bootstrap}\nimport runpy\nrunpy.run_path(SCRIPT_PATH, run_name="__main__")\n`;

  post({ type: "status", text: "running…" });
  try {
    await pyodide.runPythonAsync(script);
    post({
      type: "done",
      elapsed: ((performance.now() - started) / 1000).toFixed(2),
    });
  } catch (error) {
    post({
      type: "traceback",
      text: error && error.message ? error.message : String(error),
      elapsed: ((performance.now() - started) / 1000).toFixed(2),
    });
  }
}

self.onmessage = async (event) => {
  const { id, action, payload } = event.data || {};
  if (action === "run") {
    try {
      await run(payload);
    } catch (error) {
      post({ type: "traceback", text: String(error), elapsed: "?" });
    }
    post({ type: "finished", id });
  }
};
