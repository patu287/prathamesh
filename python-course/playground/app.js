/*
 * Python Playground — front end.
 *
 * Loads the course files over HTTP, shows them in a small editor, and runs them
 * in a Pyodide web worker (see worker.js). Progress is kept in localStorage so
 * you can close the tab and come back later.
 */

// ---------------------------------------------------------------------------
// the course file list (paths are relative to python-course/)
// ---------------------------------------------------------------------------
const SECTIONS = [
  {
    title: "Start here",
    files: [
      { path: "README.md", label: "README" },
      { path: "CHEATSHEET.md", label: "CHEATSHEET", hint: "keep this open while you code" },
    ],
  },
  {
    title: "Lessons · read and run",
    files: [
      "lessons/lesson_01_hello.py",
      "lessons/lesson_02_variables.py",
      "lessons/lesson_03_operators.py",
      "lessons/lesson_04_strings.py",
      "lessons/lesson_05_conditions.py",
      "lessons/lesson_06_loops.py",
      "lessons/lesson_07_lists.py",
      "lessons/lesson_08_tuples_sets.py",
      "lessons/lesson_09_dicts.py",
      "lessons/lesson_10_functions.py",
      "lessons/lesson_11_errors_files.py",
      "lessons/lesson_12_comprehensions_generators.py",
      "lessons/lesson_13_modules_venv.py",
      "lessons/lesson_14_classes_oop.py",
      "lessons/lesson_15_lambdas_decorators.py",
      "lessons/lesson_16_big_o.py",
    ].map((path) => ({
      path,
      label: path.split("/")[1].replace(/^lesson_/, "").replace(/\.py$/, "").replace(/_/g, " "),
      desktopOnly: path.includes("modules_venv"),
      hint: path.includes("modules_venv")
        ? "This lesson uses subprocess and a virtualenv — run it in a real terminal. Everything else works here."
        : undefined,
    })),
  },
  {
    title: "Exercises · your turn",
    files: [
      "ex_01_basics", "ex_02_variables", "ex_03_operators", "ex_04_strings",
      "ex_05_conditions", "ex_06_loops", "ex_07_lists", "ex_08_tuples_sets",
      "ex_09_dicts", "ex_10_functions", "ex_11_errors_files", "ex_12_comprehensions",
      "ex_13_modules", "ex_14_classes", "ex_15_lambdas", "ex_16_big_o",
    ].map((name) => ({
      path: `exercises/${name}.py`,
      label: name.replace(/^ex_/, "").replace(/_/g, " "),
      graded: true,
      solution: true,
    })),
  },
  {
    title: "DSA topics · read and run",
    files: [
      "dsa_01_arrays", "dsa_02_strings", "dsa_03_hashmaps", "dsa_04_sorting",
      "dsa_05_binary_search", "dsa_06_recursion", "dsa_07_stacks_queues",
      "dsa_08_linked_lists", "dsa_09_trees", "dsa_10_heaps", "dsa_11_graphs",
      "dsa_12_dp",
    ].map((name) => ({
      path: `dsa/${name}.py`,
      label: name.replace(/^dsa_/, "").replace(/_/g, " "),
    })),
  },
  {
    title: "Problems · graded",
    files: Array.from({ length: 21 }, (_, index) => {
      const id = `p${String(index).padStart(2, "0")}`;
      return id;
    }).map((id) => ({
      path: `problems/${id}`,
      label: id,
      graded: true,
      solution: true,
      prefix: true,
    })),
  },
];

const PROBLEM_NAMES = [
  "warmup", "fizzbuzz", "strings_basics", "two_sum", "array_basics", "frequency",
  "anagrams", "dedupe", "partition", "prefix_sums", "binary_search", "merge_sorted",
  "stacks", "fibonacci", "recursion", "subsets", "permutations", "two_pointers",
  "sliding_window", "linked_list", "monotonic",
];

// Resolve the problem section into real file names.
SECTIONS[4].files = PROBLEM_NAMES.map((name, index) => ({
  path: `problems/p${String(index).padStart(2, "0")}_${name}.py`,
  label: `p${String(index).padStart(2, "0")} · ${name.replace(/_/g, " ")}`,
  graded: true,
  solution: true,
}));

const ALL_FILES = SECTIONS.flatMap((section) => section.files);
const FILE_BY_PATH = new Map(ALL_FILES.map((file) => [file.path, file]));

// ---------------------------------------------------------------------------
// state
// ---------------------------------------------------------------------------
const state = {
  files: new Map(),          // path -> original content
  progress: {},             // path -> { passed, failed, skipped }
  current: null,
  dirty: false,
  workerReady: false,
  running: false,
};

const STORAGE_PROGRESS = "python-course-progress-v1";
const STORAGE_EDITS = "python-course-edits-v1";
const STORAGE_SPLIT = "python-course-split-v1";
const STORAGE_TEXT = "python-course-text-size-v1";

const $ = (id) => document.getElementById(id);
const statusEl = $("status");
const statusText = $("status-text");
const consoleEl = $("console");
const editor = $("editor");
const gutter = $("gutter");

// ---------------------------------------------------------------------------
// storage
// ---------------------------------------------------------------------------
function loadStored() {
  try {
    state.progress = JSON.parse(localStorage.getItem(STORAGE_PROGRESS) || "{}");
  } catch {
    state.progress = {};
  }
}

function saveProgress() {
  try {
    localStorage.setItem(STORAGE_PROGRESS, JSON.stringify(state.progress));
  } catch { /* storage full or blocked — ignore */ }
}

function loadEdits() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_EDITS) || "{}");
  } catch {
    return {};
  }
}

function saveEdit(path, content) {
  try {
    const edits = loadEdits();
    if (content === state.files.get(path)) {
      delete edits[path];
    } else {
      edits[path] = content;
    }
    localStorage.setItem(STORAGE_EDITS, JSON.stringify(edits));
  } catch { /* ignore */ }
}

// ---------------------------------------------------------------------------
// panel sizes — how much of the screen the lesson panel gets
// ---------------------------------------------------------------------------
const splitEl = $("split");
const splitterEl = $("splitter");
const DEFAULT_SPLIT = { editor: 70, output: 30 };

function applySplit({ editor: ed, output: out }) {
  splitEl.style.setProperty("--editor-grow", String(ed));
  splitEl.style.setProperty("--output-grow", String(out));
  splitterEl.setAttribute("aria-valuenow", String(Math.round((ed / (ed + out)) * 100)));
}

function currentSplit() {
  const style = getComputedStyle(splitEl);
  const ed = parseFloat(style.getPropertyValue("--editor-grow"));
  const out = parseFloat(style.getPropertyValue("--output-grow"));
  return {
    editor: Number.isFinite(ed) && ed > 0 ? ed : DEFAULT_SPLIT.editor,
    output: Number.isFinite(out) && out > 0 ? out : DEFAULT_SPLIT.output,
  };
}

function saveSplit(values) {
  try {
    localStorage.setItem(STORAGE_SPLIT, JSON.stringify(values));
  } catch { /* ignore */ }
}

function loadSplit() {
  let saved = null;
  try {
    saved = JSON.parse(localStorage.getItem(STORAGE_SPLIT) || "null");
  } catch { saved = null; }
  const usable = saved
    && Number.isFinite(saved.editor) && Number.isFinite(saved.output)
    && saved.editor > 0 && saved.output > 0;
  applySplit(usable ? saved : { ...DEFAULT_SPLIT });
}

function resetSplit() {
  applySplit({ ...DEFAULT_SPLIT });
  saveSplit({ ...DEFAULT_SPLIT });
}

// ---------------------------------------------------------------------------
// code text size (A− / A+) — for long lessons and small screens
// ---------------------------------------------------------------------------
const TEXT_STEPS = [0.85, 1, 1.15, 1.3];
let textStep = 1;

function applyTextScale(step) {
  textStep = Math.min(TEXT_STEPS.length - 1, Math.max(0, step));
  const scale = TEXT_STEPS[textStep];
  const percent = `${Math.round(scale * 100)}%`;
  document.documentElement.style.setProperty("--text-scale", String(scale));
  $("text-smaller").disabled = textStep === 0;
  $("text-bigger").disabled = textStep === TEXT_STEPS.length - 1;
  $("text-smaller").title = `smaller code (now ${percent})`;
  $("text-bigger").title = `bigger code (now ${percent})`;
  try {
    localStorage.setItem(STORAGE_TEXT, String(textStep));
  } catch { /* ignore */ }
}

function loadTextScale() {
  let stored = null;
  try {
    stored = Number.parseInt(localStorage.getItem(STORAGE_TEXT) ?? "", 10);
  } catch { stored = null; }
  applyTextScale(Number.isInteger(stored) && stored >= 0 && stored < TEXT_STEPS.length ? stored : 1);
}

// ---------------------------------------------------------------------------
// rendering helpers
// ---------------------------------------------------------------------------
function write(text, className = "stdout") {
  const span = document.createElement("span");
  span.className = className;
  span.textContent = text.endsWith("\n") ? text : `${text}\n`;
  consoleEl.appendChild(span);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function clearConsole() {
  consoleEl.innerHTML = "";
  $("elapsed").textContent = "";
}

function updateGutter() {
  const lines = editor.value.split("\n").length;
  let text = "";
  for (let i = 1; i <= lines; i += 1) {
    text += `${i}\n`;
  }
  gutter.textContent = text;
  gutter.scrollTop = editor.scrollTop;
}

function badgeFor(path, file) {
  const record = state.progress[path];
  if (file.desktopOnly) return "💻";
  if (record) {
    if (record.failed > 0) return "❌";
    if (record.skipped > 0) return "⏳";
    if (record.passed > 0) return "✅";
    return "▫️";
  }
  return file.graded ? "▫️" : "•";
}

function renderFileList(filter = "") {
  const list = $("file-list");
  const needle = filter.trim().toLowerCase();
  list.innerHTML = "";
  for (const section of SECTIONS) {
    const files = section.files.filter((file) => {
      if (!needle) return true;
      return `${file.label} ${file.path}`.toLowerCase().includes(needle);
    });
    if (!files.length) continue;
    const title = document.createElement("div");
    title.className = "group-title";
    title.textContent = section.title;
    list.appendChild(title);
    for (const file of files) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "file-button";
      if (file.path === state.current) button.classList.add("active");
      if (file.desktopOnly) button.classList.add("desktop-only");
      const name = document.createElement("span");
      name.className = "name";
      name.textContent = file.label;
      const badge = document.createElement("span");
      badge.className = "badge";
      badge.textContent = badgeFor(file.path, file);
      button.append(name, badge);
      button.addEventListener("click", () => openFile(file.path));
      list.appendChild(button);
    }
  }
}

function renderProgress() {
  const graded = ALL_FILES.filter((file) => file.graded);
  const done = graded.filter((file) => {
    const record = state.progress[file.path];
    return record && record.failed === 0 && record.skipped === 0 && record.passed > 0;
  }).length;
  $("progress-bar").style.width = `${graded.length ? (done / graded.length) * 100 : 0}%`;
  $("progress-text").textContent = `${done} / ${graded.length} done`;
}

// ---------------------------------------------------------------------------
// file loading
// ---------------------------------------------------------------------------
async function loadAllFiles() {
  const edits = loadEdits();
  const filePaths = [...ALL_FILES.map((f) => f.path), "tools/harness.py"];
  let failCount = 0;
  const results = await Promise.all(filePaths.map(async (path) => {
    try {
      const response = await fetch(`../${path}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return [path, await response.text()];
    } catch (err) {
      failCount++;
      console.warn(`Could not load ${path}:`, err);
      return [path, `# ${path}\n\n# Note: This file could not be loaded (${err.message}).\n`];
    }
  }));
  for (const [path, text] of results) {
    state.files.set(path, text);
  }
  // Apply locally saved edits on top.
  for (const [path, content] of Object.entries(edits)) {
    if (state.files.has(path)) state.files.set(path, content);
  }
  if (failCount > 0 && failCount === filePaths.length) {
    throw new Error("All course files failed to load");
  }
}

function openFile(path) {
  if (state.dirty) saveEdit(state.current, editor.value);
  const file = FILE_BY_PATH.get(path);
  state.current = path;
  const content = state.files.get(path) ?? "";
  editor.value = content;
  $("file-title").textContent = file ? file.label : path;
  $("file-path").textContent = `python-course/${path}`;
  $("run-solution").disabled = !(file && file.solution);
  $("hint").classList.toggle("hidden", !(file && file.hint));
  if (file && file.hint) $("hint").textContent = file.hint;
  state.dirty = false;
  updateGutter();
  renderFileList($("filter").value);
  clearConsole();
  if (window.innerWidth <= 860) editor.scrollIntoView({ block: "nearest" });
}

// ---------------------------------------------------------------------------
// running
// ---------------------------------------------------------------------------
const WORKER_URL = "worker.js";
let worker = null;
let runId = 0;
let pending = null;

function startWorker() {
  worker = new Worker(WORKER_URL);
  worker.onmessage = (event) => {
    const message = event.data || {};
    if (message.type === "boot") {
      const text = String(message.text || "").trim();
      if (text) setStatus(text, "loading");
      return;
    }
    if (message.type === "stdout") {
      write(message.text, "stdout");
      captureSummary(message.text);
      return;
    }
    if (message.type === "stderr") {
      write(message.text, "stderr");
      return;
    }
    if (message.type === "traceback") {
      write(message.text, "stderr");
      if (pending) finishRun(pending.path, pending.solution, false);
      return;
    }
    if (message.type === "done") {
      write(`\n── finished in ${message.elapsed}s`, "info");
      if (pending) finishRun(pending.path, pending.solution, true);
      return;
    }
    if (message.type === "status") {
      setStatus(message.text, "loading");
    }
    if (message.type === "finished") {
      state.running = false;
      updateRunButtons();
    }
  };
}

function setStatus(text, mode = "loading") {
  statusText.textContent = text;
  statusEl.classList.toggle("ready", mode === "ready");
  statusEl.classList.toggle("error", mode === "error");
}

let summaryBuffer = "";

function captureSummary(text) {
  if (!pending) return;
  summaryBuffer += text;
  const match = summaryBuffer.match(/(\d+) passed\s+(\d+) failed\s+(\d+) skipped/);
  if (match && pending.path) {
    const [, passed, failed, skipped] = match;
    state.progress[pending.path] = {
      passed: Number(passed),
      failed: Number(failed),
      skipped: Number(skipped),
      at: Date.now(),
    };
    saveProgress();
    summaryBuffer = "";
  }
}

function finishRun(path, solution, success) {
  if (path) {
    const record = state.progress[path];
    if (record && !solution) {
      if (record.failed > 0) {
        write(`\n${record.failed} test(s) failing — read the ❌ lines above and fix them.`, "warn");
      } else if (record.skipped > 0) {
        write(`\n${record.skipped} test(s) still unimplemented (NotImplementedError).`, "warn");
      } else if (record.passed > 0) {
        write(`\n🎉 all ${record.passed} tests passed!`, "ok");
      }
    }
    if (!solution) renderProgress();
    renderFileList($("filter").value);
  }
  pending = null;
  state.running = false;
  updateRunButtons();
  setStatus(success ? "ready" : "error", success ? "ready" : "error");
}

function updateRunButtons() {
  $("run").disabled = state.running;
  $("run").textContent = state.running ? "⏳ Running" : "▶ Run";
  $("run-solution").disabled = state.running || !(FILE_BY_PATH.get(state.current)?.solution);
}

function run({ solution = false } = {}) {
  if (!state.current) return;
  saveEdit(state.current, editor.value);
  state.files.set(state.current, editor.value);
  clearConsole();
  // if the output was hidden to enlarge the lesson, bring it back for the results
  if (splitEl.classList.contains("output-collapsed")) setOutputCollapsed(false);
  summaryBuffer = "";
  const files = {};
  for (const [path, content] of state.files) {
    files[path] = content;
  }
  pending = { path: state.current, solution };
  state.running = true;
  updateRunButtons();
  write(`▶ ${state.current}${solution ? "   (reference solution, --solution)" : ""}\n`, "info");
  worker.postMessage({
    id: ++runId,
    action: "run",
    payload: {
      path: `/course/${state.current}`,
      files,
      argv: solution ? ["--solution"] : [],
      stdin: $("stdin").value,
    },
  });
}

// ---------------------------------------------------------------------------
// events
// ---------------------------------------------------------------------------
editor.addEventListener("input", () => {
  state.dirty = true;
  updateGutter();
  if (state.current) saveEdit(state.current, editor.value);
});
editor.addEventListener("scroll", () => {
  gutter.scrollTop = editor.scrollTop;
});
editor.addEventListener("keydown", (event) => {
  if (event.key === "Tab") {
    event.preventDefault();
    const { selectionStart, selectionEnd, value } = editor;
    const indent = "    ";
    if (selectionStart === selectionEnd) {
      editor.value = value.slice(0, selectionStart) + indent + value.slice(selectionEnd);
      editor.selectionStart = editor.selectionEnd = selectionStart + indent.length;
    } else {
      const lineStart = value.lastIndexOf("\n", selectionStart - 1) + 1;
      const block = value.slice(lineStart, selectionEnd);
      const shifted = event.shiftKey
        ? block.replace(/^ {1,4}/gm, "")
        : block.replace(/^/gm, indent);
      editor.value = value.slice(0, lineStart) + shifted + value.slice(selectionEnd);
      editor.selectionStart = lineStart;
      editor.selectionEnd = lineStart + shifted.length;
    }
    updateGutter();
  }
});
editor.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    if (!state.running) run();
  }
});

$("run").addEventListener("click", () => run());
$("run-solution").addEventListener("click", () => run({ solution: true }));
$("clear").addEventListener("click", clearConsole);
$("reset-file").addEventListener("click", async () => {
  if (!state.current) return;
  const response = await fetch(`../${state.current}`);
  const original = await response.text();
  state.files.set(state.current, original);
  editor.value = original;
  saveEdit(state.current, original);
  state.dirty = false;
  updateGutter();
  clearConsole();
  write(`↺ ${state.current} restored to the original file\n`, "info");
});
$("filter").addEventListener("input", (event) => renderFileList(event.target.value));

// ------------------------------------------------- the lesson ⇕ output divider
let drag = null;

splitterEl.addEventListener("pointerdown", (event) => {
  if (splitEl.classList.contains("output-collapsed")) return;
  drag = {
    y: event.clientY,
    height: Math.max(splitEl.getBoundingClientRect().height, 1),
    ...currentSplit(),
  };
  splitterEl.setPointerCapture(event.pointerId);
  splitterEl.classList.add("dragging");
  document.body.classList.add("resizing");
  event.preventDefault();
});

splitterEl.addEventListener("pointermove", (event) => {
  if (!drag) return;
  const total = drag.editor + drag.output;
  const share = (event.clientY - drag.y) / drag.height;   // fraction of the split height
  let editor = drag.editor + share * total;
  editor = Math.min(total * 0.9, Math.max(total * 0.1, editor));
  applySplit({ editor, output: total - editor });
});

function endDrag() {
  if (!drag) return;
  drag = null;
  splitterEl.classList.remove("dragging");
  document.body.classList.remove("resizing");
  saveSplit(currentSplit());
}
splitterEl.addEventListener("pointerup", endDrag);
splitterEl.addEventListener("pointercancel", endDrag);

splitterEl.addEventListener("dblclick", resetSplit);

splitterEl.addEventListener("keydown", (event) => {
  if (event.key === "Home") {
    event.preventDefault();
    resetSplit();
    return;
  }
  const step = event.key === "ArrowUp" ? -3 : event.key === "ArrowDown" ? 3 : 0;
  if (!step) return;
  event.preventDefault();
  const { editor, output } = currentSplit();
  const total = editor + output;
  const next = Math.min(total * 0.9, Math.max(total * 0.1, editor + step));
  applySplit({ editor: next, output: total - next });
  saveSplit({ editor: next, output: total - next });
});

// ------------------------------------------------- show/hide the file list
$("toggle-sidebar").addEventListener("click", () => {
  const hidden = $("layout").classList.toggle("sidebar-hidden");
  const button = $("toggle-sidebar");
  button.classList.toggle("on", hidden);
  button.textContent = hidden ? "☰ Files ▸" : "☰ Files";
  button.title = hidden ? "show the file list" : "hide the file list for a wider page";
});

// ------------------------------------------------- "⤢ Big page" mode
function setOutputCollapsed(collapsed) {
  splitEl.classList.toggle("output-collapsed", collapsed);
  const button = $("toggle-output");
  button.classList.toggle("on", collapsed);
  button.textContent = collapsed ? "⤡ Show output" : "⤢ Big page";
  button.title = collapsed
    ? "show the output panel again"
    : "hide the output panel and give the lesson the whole screen";
}

$("toggle-output").addEventListener("click", () => {
  setOutputCollapsed(!splitEl.classList.contains("output-collapsed"));
});

// ------------------------------------------------- code text size
$("text-smaller").addEventListener("click", () => applyTextScale(textStep - 1));
$("text-bigger").addEventListener("click", () => applyTextScale(textStep + 1));

$("reset-progress").addEventListener("click", () => {
  state.progress = {};
  saveProgress();
  renderProgress();
  renderFileList($("filter").value);
  write("progress cleared\n", "info");
});

// ---------------------------------------------------------------------------
// boot
// ---------------------------------------------------------------------------
(async function main() {
  loadStored();
  loadSplit();
  loadTextScale();
  try {
    await loadAllFiles();
  } catch (error) {
    setStatus("could not load the course files", "error");
    write(`Failed to load files: ${error.message}\n` +
      "Start the bundled server (python3 serve.py) or open the page over HTTP " +
      "— browsers block file:// reads.\n", "stderr");
    return;
  }
  renderFileList();
  renderProgress();
  startWorker();
  openFile("README.md");
  const initialPath = new URLSearchParams(location.search).get("file");
  if (initialPath && state.files.has(initialPath)) openFile(initialPath);
  write("Python is starting up in your browser (Pyodide + WebAssembly).\n" +
    "The first load takes a few seconds; after that everything is instant.\n\n", "info");
})();
