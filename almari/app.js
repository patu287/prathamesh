/* ══════════════════════════════════════════════════════════════════
   My Wardrobe · app.js
   Two views — Wardrobe (items) and Outfits (looks) — sharing one app
   shell, one search box and one storage layer.
   ══════════════════════════════════════════════════════════════════ */

/* Surface every runtime error instead of failing silently. A click handler
   that throws otherwise looks exactly like a click that does nothing. */
function showErr(msg) {
  const bar = document.getElementById('errbar');
  if (!bar) return;
  bar.hidden = false;
  bar.textContent = '⚠ ' + msg;
  bar.title = 'Tap to dismiss';
  bar.onclick = () => { bar.hidden = true; };
}
window.addEventListener('error', e => showErr(e.message || 'Script error'));
window.addEventListener('unhandledrejection', e => showErr('Async error: ' + (e.reason && e.reason.message || e.reason)));

const el = id => document.getElementById(id);

const state = {
  view: 'wardrobe',
  items: [],
  looks: [],
  itemMap: new Map(),

  /* wardrobe */
  slot: 'all',
  types: new Set(),
  query: '',
  sort: 'new',
  editingId: null,
  detailId: null,
  form: blankForm(),

  /* outfits */
  lookOccasion: 'all',
  lookSort: 'new',
  editingLookId: null,
  lookDetailId: null,
  builder: blankBuilder(),
  pickerFor: null,
  pickerQuery: '',
  pickerShowAll: false
};

let previewURL = null;   // object URL for the form's photo preview

function blankForm() {
  return { photoBlob: null, name: '', slot: 'top', type: 'shirt', occasions: [], laundry: 'clean' };
}

function blankBuilder(seed) {
  const base = {
    slots: { top: null, layer: null, bottom: null, outer: null, foot: null, accessory: [] },
    name: '', occasions: [], rating: 0
  };
  return seed
    ? Object.assign(base, seed, { slots: Object.assign(base.slots, seed.slots || {}) })
    : base;
}

const HANGER_SVG = `<svg viewBox="0 0 48 34" aria-hidden="true">
  <path d="M24 8.5c0-3 4.6-3 4.6 0 0 2.2-2.4 2.9-4.6 4v2.1"/>
  <path d="M24 14.6 4.6 24.4c-1.6.8-1.4 3.1.4 3.6L24 32.6l19-4.6c1.8-.5 2-2.8.4-3.6L24 14.6z"/>
</svg>`;

const PLUS_SVG = `<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>`;

/* With colour tagging gone, a photo-less item still needs to be visually
   distinct on the shelf. The tone is hashed from the name so it is stable
   across renders, and it resolves to a CSS variable so both themes supply
   their own six tones. */
const TILE_TONE_COUNT = 6;

function tileTone(item) {
  const key = ((item && item.name) || '') + ((item && item.type) || '') + ((item && item.id) || '');
  let h = 0;
  for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) >>> 0;
  return 'var(--tone-' + ((h % TILE_TONE_COUNT) + 1) + ')';
}

/* ─────────────────────────  theme  ───────────────────────── */
const THEME_KEY = 'mywardrobe.theme';
const THEME_META = { dusk: '#131110', light: '#FAF8F5' };

const currentTheme = () => document.documentElement.getAttribute('data-theme') || 'dusk';

function applyTheme(t) {
  const theme = t === 'light' ? 'light' : 'dusk';
  document.documentElement.setAttribute('data-theme', theme);
  try { localStorage.setItem(THEME_KEY, theme); } catch (err) { /* private mode */ }
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', THEME_META[theme]);
  const seg = el('themeSeg');
  if (seg) Array.from(seg.children).forEach(b => {
    const on = b.dataset.themePick === theme;
    b.classList.toggle('on', on);
    b.setAttribute('aria-checked', on);
  });
}

/* ─────────────────────────  boot  ───────────────────────── */
(async function init() {
  try {
    applyTheme(currentTheme());
    buildFormControls();
    buildBuilderControls();
    wireEvents();
    await reload();
    setView('wardrobe');
  } catch (err) {
    showErr('Startup failed: ' + (err && err.message ? err.message : err));
    throw err;
  }
})();

async function reload() {
  const [items, looks] = await Promise.all([Store.all(), Store.allLooks()]);
  state.items = items;
  state.looks = looks;
  state.itemMap = new Map(items.map(i => [i.id, i]));
  renderAll();
}

function renderAll() {
  renderHeader();
  renderSlots(); renderTypes(); renderGrid();
  renderLookOccasions(); renderLooks();
}

const itemById = id => (id ? state.itemMap.get(id) || null : null);

/* ─────────────────────  shared thumbnail  ───────────────── */
function cellInner(item) {
  if (!item) return '';
  const url = Store.photoURL(item);
  if (url) return `<img src="${url}" alt="${escapeAttr(autoName(item))}" loading="lazy" />`;
  return `<span class="tile" style="background:${tileTone(item)}" aria-hidden="true">
            <span class="hanger">${HANGER_SVG}</span>
            <span class="tile-label">${escapeHTML(typeById(item.type).label)}</span>
          </span>`;
}

/* ─────────────────────  header + counts  ────────────────── */
function renderHeader() {
  const n = state.items.length;
  const line = el('countLine');

  if (state.view === 'outfits') {
    line.textContent = n === 0 ? 'No items yet'
      : `${state.looks.length} look${state.looks.length === 1 ? '' : 's'} · ${n} item${n === 1 ? '' : 's'}`;
  } else if (n === 0) {
    line.textContent = 'No items yet';
  } else {
    const tops = state.items.filter(i => i.slot === 'top').length;
    const bottoms = state.items.filter(i => i.slot === 'bottom').length;
    line.textContent = `${n} item${n === 1 ? '' : 's'} · ${tops} tops · ${bottoms} bottoms`;
  }

  const stats = el('menuStats');
  if (stats) {
    const rows = SLOTS.map(s =>
      `<div class="stat"><b>${state.items.filter(i => i.slot === s.id).length}</b><span>${s.label}</span></div>`).join('');
    const dirty = state.items.filter(i => i.laundry === 'dirty' || i.laundry === 'cleaning').length;
    stats.innerHTML = `
      <div class="stat big"><b>${n}</b><span>items · ${state.looks.length} looks</span></div>
      ${rows}
      <div class="stat"><b>${state.items.filter(i => i.photoBlob).length}</b><span>with photo</span></div>
      <div class="stat"><b>${dirty}</b><span>in the wash</span></div>`;
  }

  const sl = el('storageLine');
  if (sl) {
    sl.textContent = Store.backend() === 'IndexedDB'
      ? 'Storage: IndexedDB (unlimited photos)'
      : 'Storage: localStorage (photo space limited — serve over http)';
  }
}

/* ───────────────────────  view switch  ──────────────────── */
function setView(v) {
  state.view = v;
  const w = v === 'wardrobe';

  ['slots', 'types', 'toolbar', 'stage'].forEach(id => { el(id).hidden = !w; });
  ['lookOccasions', 'lookToolbar', 'stageOutfits'].forEach(id => { el(id).hidden = w; });

  el('fabLabel').textContent = w ? 'Add' : 'New look';
  el('fab').setAttribute('aria-label', w ? 'Add an item' : 'Build a look');
  el('search').placeholder = w ? 'Search clothes…' : 'Search looks…';

  document.querySelectorAll('.tab').forEach(t => {
    const on = t.dataset.tab === v;
    t.classList.toggle('active', on);
    if (on) t.setAttribute('aria-current', 'page'); else t.removeAttribute('aria-current');
  });

  renderAll();
}

/* ═══════════════════════  WARDROBE VIEW  ══════════════════ */

function renderSlots() {
  const tabs = [{ id: 'all', label: 'Everything' }].concat(SLOTS);
  el('slots').innerHTML = tabs.map(s => {
    const count = s.id === 'all' ? state.items.length : state.items.filter(i => i.slot === s.id).length;
    return `<button class="slot ${state.slot === s.id ? 'on' : ''}" data-slot="${s.id}" aria-pressed="${state.slot === s.id}">
      <span>${s.label}</span><em>${count}</em></button>`;
  }).join('');
}

function renderTypes() {
  const wrap = el('types');
  if (state.view !== 'wardrobe') { wrap.hidden = true; return; }

  const list = state.slot === 'all' ? TYPES : typesIn(state.slot);
  const used = new Set(state.items.map(i => i.type));
  const relevant = list.filter(t => used.has(t.id) || state.types.has(t.id));
  if (!relevant.length) { wrap.innerHTML = ''; wrap.hidden = true; return; }

  wrap.hidden = false;
  wrap.innerHTML = `<button class="chip ${state.types.size === 0 ? 'on' : ''}" data-type="">All</button>` +
    relevant.map(t => {
      const n = state.items.filter(i => i.type === t.id).length;
      return `<button class="chip ${state.types.has(t.id) ? 'on' : ''}" data-type="${t.id}">${t.label}<em>${n}</em></button>`;
    }).join('');
}

function visibleItems() {
  const q = state.query.trim().toLowerCase();
  const list = state.items.filter(item => {
    if (state.slot !== 'all' && item.slot !== state.slot) return false;
    if (state.types.size && !state.types.has(item.type)) return false;
    if (q && !haystack(item).includes(q)) return false;
    return true;
  });
  const by = {
    new:  (a, b) => (b.createdAt || 0) - (a.createdAt || 0),
    old:  (a, b) => (a.createdAt || 0) - (b.createdAt || 0),
    name: (a, b) => autoName(a).localeCompare(autoName(b)),
    type: (a, b) => typeById(a.type).label.localeCompare(typeById(b.type).label) ||
                    autoName(a).localeCompare(autoName(b))
  }[state.sort];
  return list.sort(by);
}

function renderGrid() {
  const list = visibleItems();
  const grid = el('grid');
  const nothingAtAll = state.items.length === 0;

  el('emptyFirst').hidden = !nothingAtAll;
  el('emptyFilter').hidden = nothingAtAll || list.length > 0;
  grid.hidden = list.length === 0;

  el('resultCount').textContent = nothingAtAll ? '' :
    `${list.length} ${list.length === 1 ? 'item' : 'items'}${state.slot === 'all' ? '' : ' in ' + slotById(state.slot).label.toLowerCase()}`;

  if (!list.length) return;
  grid.innerHTML = list.map(cardHTML).join('');

  if (!el('emptyFilter').hidden) {
    el('emptyFilterMsg').textContent = state.query
      ? `Nothing matches “${state.query}”.`
      : 'No items in this category yet.';
  }
}

function cardHTML(item) {
  const name = autoName(item);
  const type = typeById(item.type);
  const tags = (item.occasions || []).slice(0, 2).map(o => `<span class="tag">${escapeHTML(o)}</span>`).join('');

  const st = item.laundry && item.laundry !== 'clean' ? item.laundry : null;
  const badge = st
    ? `<span class="laundry-badge ${st}" data-cycle="${item.id}" role="button" tabindex="0"
         title="Tap to change laundry status">${laundryById(st).short}</span>`
    : '';

  return `<article class="card" data-id="${item.id}" tabindex="0" role="button" aria-label="${escapeAttr(name)}">
    <div class="thumb">${cellInner(item)}${badge}</div>
    <div class="card-body">
      <h3>${escapeHTML(name)}</h3>
      <p class="card-meta">${escapeHTML(type.label)}</p>
      ${tags ? `<div class="card-foot">${tags}</div>` : ''}
    </div>
  </article>`;
}

/* ─────────────────────  item detail  ────────────────────── */
function openDetail(id) {
  const item = itemById(id);
  if (!item) return;
  state.detailId = id;
  el('detailTitle').textContent = autoName(item);

  const url = Store.photoURL(item);
  const hero = url
    ? `<img class="hero" src="${url}" alt="${escapeAttr(autoName(item))}" />`
    : `<div class="hero tile" style="background:${tileTone(item)}"><span class="hanger">${HANGER_SVG}</span>
         <span class="tile-label">${escapeHTML(typeById(item.type).label)}</span></div>`;

  const row = (k, v) => v ? `<div class="drow"><span>${k}</span><b>${escapeHTML(String(v))}</b></div>` : '';
  const chipLine = list => (list || []).map(x => `<span class="tag">${escapeHTML(x)}</span>`).join('');
  const st = item.laundry || 'clean';
  const inLooks = state.looks.filter(l => lookItemIds(l).includes(id));

  el('detailBody').innerHTML = `
    ${hero}
    <div class="field">
      <span class="field-label">Laundry status</span>
      <div class="segmented laundry-row" id="laundryRow">
        ${LAUNDRY.map(l => `<button type="button" class="seg ${l.id === st ? 'on' : ''}" data-laundry="${l.id}">${l.short}</button>`).join('')}
      </div>
    </div>
    <div class="detail-rows">
      ${row('Category', slotById(item.slot).label)}
      ${row('Type', typeById(item.type).label)}
      ${row('Added', fmtDate(new Date(item.createdAt || Date.now()).toISOString().slice(0, 10)))}
      ${item.worn ? row('Worn', `${item.worn} time${item.worn === 1 ? '' : 's'}${item.lastWorn ? ' · last ' + fmtDate(new Date(item.lastWorn).toISOString().slice(0, 10)) : ''}`) : ''}
      ${chipLine(item.occasions) ? `<div class="drow col"><span>Occasions</span><div class="tagrow">${chipLine(item.occasions)}</div></div>` : ''}
      ${inLooks.length ? `<div class="drow col"><span>In ${inLooks.length} look${inLooks.length === 1 ? '' : 's'}</span><div class="tagrow">${inLooks.map(l => `<span class="tag">${escapeHTML(l.name || autoLookName(l, state.items))}</span>`).join('')}</div></div>` : ''}
    </div>`;

  el('detailDelete').innerHTML = 'Delete';
  el('detailDelete').classList.remove('armed');
  openSheet('detail');
}

async function setLaundry(id, status) {
  const item = itemById(id);
  if (!item) return;
  item.laundry = status;
  item.updatedAt = Date.now();
  await Store.put(item);
  renderAll();
  toast(`${autoName(item)} → ${laundryById(status).label}`);
}

/* ─────────────────────  add / edit item  ────────────────── */
function buildFormControls() {
  el('fSlot').innerHTML = SLOTS.map(s =>
    `<button type="button" class="seg" data-fslot="${s.id}" role="radio" aria-checked="false">${s.short}</button>`).join('');

  el('fLaundry').innerHTML = LAUNDRY.map(l =>
    `<button type="button" class="seg" data-flaundry="${l.id}" role="radio" aria-checked="false" title="${l.label}">${l.short}</button>`).join('');

  el('fOccasions').innerHTML = OCCASIONS.map(o => `<button type="button" class="chip" data-occ="${o}">${o}</button>`).join('');

  renderFormTypes();
  syncFormUI();
}

function renderFormTypes() {
  const list = typesIn(state.form.slot);
  if (!list.some(t => t.id === state.form.type)) state.form.type = list[0].id;
  el('fType').innerHTML = list.map(t =>
    `<button type="button" class="chip ${t.id === state.form.type ? 'on' : ''}" data-ftype="${t.id}">${t.label}</button>`).join('');
}

function syncFormUI() {
  const f = state.form;
  el('fName').value = f.name;
  markGroup('fSlot', b => b.dataset.fslot === f.slot);
  markGroup('fLaundry', b => b.dataset.flaundry === f.laundry);
  markGroup('fOccasions', b => f.occasions.includes(b.dataset.occ));
  renderFormTypes();

  const img = el('photoPreview');
  if (previewURL) { URL.revokeObjectURL(previewURL); previewURL = null; }
  if (f.photoBlob) {
    previewURL = URL.createObjectURL(f.photoBlob);
    img.src = previewURL;
    img.hidden = false;
    el('photoEmpty').hidden = true;
    el('photoRemove').hidden = false;
  } else {
    img.removeAttribute('src');
    img.hidden = true;
    el('photoEmpty').hidden = false;
    el('photoRemove').hidden = true;
  }
  el('formTitle').textContent = state.editingId ? 'Edit item' : 'Add an item';
  el('formSave').textContent = state.editingId ? 'Save changes' : 'Add to wardrobe';
}

function markGroup(id, pred) {
  const box = el(id);
  if (!box) return;
  Array.from(box.children).forEach(b => {
    const on = pred(b);
    b.classList.toggle('on', on);
    if (b.getAttribute('role') === 'radio') b.setAttribute('aria-checked', on);
  });
}

function openAdd() {
  state.editingId = null;
  state.form = blankForm();
  syncFormUI();
  openSheet('form');
  setTimeout(() => { const n = el('fName'); if (n) n.focus({ preventScroll: true }); }, 260);
}

function openEdit(id) {
  const item = itemById(id);
  if (!item) return;
  state.editingId = id;
  state.form = {
    photoBlob: item.photoBlob || null,
    name: item.name || '',
    slot: item.slot || 'top',
    type: item.type || 'shirt',
    occasions: (item.occasions || []).slice(),
    laundry: item.laundry || 'clean'
  };
  syncFormUI();
  closeSheet('detail');
  openSheet('form');
}

async function saveForm() {
  const f = state.form;
  if (!f.slot || !f.type) return toast('Pick a category and type');

  const base = state.editingId ? itemById(state.editingId) : null;
  // Object.assign onto `base` keeps any legacy fields from older backups intact.
  const item = Object.assign({}, base || {}, {
    id: base ? base.id : Store.uid('i'),
    photoBlob: f.photoBlob || null,
    name: el('fName').value.trim(),
    slot: f.slot,
    type: f.type,
    occasions: f.occasions.slice(),
    laundry: f.laundry || 'clean',
    worn: base ? (base.worn || 0) : 0,
    lastWorn: base ? (base.lastWorn || null) : null,
    createdAt: base ? base.createdAt : Date.now(),
    updatedAt: Date.now()
  });
  if (!item.name) item.name = autoName(item);

  try {
    if (base) Store.forgetPhoto(base.id);
    await Store.put(item);
    closeSheet('form');
    await reload();
    toast(base ? 'Changes saved' : `Added “${item.name}”`);
    if (state.pickerFor) renderPicker();
    flashCard(item.id);
  } catch (err) {
    toast(err && err.message ? err.message : 'Could not save that item');
  }
}

function flashCard(id) {
  const card = document.querySelector(`.card[data-id="${id}"]`);
  if (!card) return;
  card.classList.add('flash');
  card.scrollIntoView({ behavior: 'smooth', block: 'center' });
  setTimeout(() => card.classList.remove('flash'), 1400);
}

/* ─────────────────────  photo capture  ──────────────────── */
async function handlePhotoFile(file) {
  if (!file) return;
  const drop = el('photoDrop');
  drop.classList.add('busy');
  try {
    state.form.photoBlob = await Store.compressImage(file);
    syncFormUI();
    toast('Photo added');
  } catch (err) {
    toast(err && err.message ? err.message : 'Could not read that photo');
  } finally {
    drop.classList.remove('busy');
  }
}

/* ═══════════════════════  OUTFITS VIEW  ═══════════════════ */

function lookItemIds(look) {
  const s = (look && look.slots) || {};
  return LOOK_SLOTS.reduce((acc, sl) => {
    const v = s[sl.id];
    if (sl.multi) return acc.concat((v || []).filter(Boolean));
    return v ? acc.concat(v) : acc;
  }, []);
}

const lookItems = look => lookItemIds(look).map(itemById).filter(Boolean);

function renderLookOccasions() {
  const wrap = el('lookOccasions');
  const used = new Set();
  state.looks.forEach(l => (l.occasions || []).forEach(o => used.add(o)));
  if (state.lookOccasion !== 'all') used.add(state.lookOccasion);

  if (!used.size) { wrap.innerHTML = ''; return; }
  wrap.innerHTML = `<button class="chip ${state.lookOccasion === 'all' ? 'on' : ''}" data-locc="">All occasions</button>` +
    Array.from(used).map(o => {
      const n = state.looks.filter(l => (l.occasions || []).includes(o)).length;
      return `<button class="chip ${state.lookOccasion === o ? 'on' : ''}" data-locc="${escapeAttr(o)}">${escapeHTML(o)}<em>${n}</em></button>`;
    }).join('');
}

function visibleLooks() {
  const q = state.query.trim().toLowerCase();
  const list = state.looks.filter(look => {
    if (state.lookOccasion !== 'all' && !(look.occasions || []).includes(state.lookOccasion)) return false;
    if (!q) return true;
    const words = [look.name, autoLookName(look, state.items),
      (look.occasions || []).join(' '),
      lookItems(look).map(i => autoName(i)).join(' ')];
    return words.filter(Boolean).join(' ').toLowerCase().includes(q);
  });
  const by = {
    new:    (a, b) => (b.createdAt || 0) - (a.createdAt || 0),
    name:   (a, b) => (a.name || '').localeCompare(b.name || ''),
    worn:   (a, b) => (b.worn || 0) - (a.worn || 0),
    rating: (a, b) => (b.rating || 0) - (a.rating || 0)
  }[state.lookSort];
  return list.sort(by);
}

function renderLooks() {
  const list = visibleLooks();
  const grid = el('lookGrid');
  const none = state.looks.length === 0;

  el('emptyLooks').hidden = !none;
  el('emptyLookFilter').hidden = none || list.length > 0;
  grid.hidden = list.length === 0;

  const c = combinations(state.items);
  el('comboLine').textContent = state.items.length < 3
    ? 'Add a top, a bottom and footwear to start'
    : `${c.tops} tops × ${c.bottoms} bottoms × ${c.shoes} shoes = ${c.total.toLocaleString('en-IN')} possible looks`;

  if (none) {
    el('emptyLooksMsg').textContent = state.items.length < 3
      ? 'You need at least a top, a bottom and a pair of shoes in the wardrobe first.'
      : `Your wardrobe can already make ${c.total.toLocaleString('en-IN')} combinations. Save the ones you actually wear.`;
    return;
  }
  if (!list.length) {
    el('emptyLookFilterMsg').textContent = state.query
      ? `No look matches “${state.query}”.`
      : 'No look is tagged with that occasion.';
    return;
  }
  grid.innerHTML = list.map(lookCardHTML).join('');
}

function collageHTML(slots, opts) {
  const o = opts || {};
  const s = slots || {};
  const top = itemById(s.top), bottom = itemById(s.bottom), foot = itemById(s.foot);
  const extras = [itemById(s.layer), itemById(s.outer)]
    .filter(Boolean)
    .concat((s.accessory || []).map(itemById).filter(Boolean));

  const cell = (item, cls, label) => item
    ? `<div class="c-cell ${cls}">${cellInner(item)}</div>`
    : `<div class="c-cell ${cls} void">${o.labelVoid ? escapeHTML(label) : ''}</div>`;

  return `<div class="collage">
      ${cell(top, 'main', 'Top')}
      ${cell(bottom, '', 'Bottom')}
      ${cell(foot, '', 'Footwear')}
      ${extras.length ? `<span class="c-more">+${extras.length}</span>` : ''}
    </div>`;
}

function starsHTML(rating) {
  const r = rating || 0;
  return `<span class="stars-sm" aria-label="${r} out of 5">` +
    [1, 2, 3, 4, 5].map(i => i <= r ? '★' : '<span class="off">★</span>').join('') + '</span>';
}

function lookCardHTML(look) {
  const name = look.name || autoLookName(look, state.items);
  const missing = requiredMissing(look.slots);
  const tags = (look.occasions || []).slice(0, 2).map(o => `<span class="tag">${escapeHTML(o)}</span>`).join('');

  return `<article class="card look ${missing.length ? 'incomplete' : ''}" data-look="${look.id}" tabindex="0" role="button" aria-label="${escapeAttr(name)}">
    <div class="thumb">
      ${collageHTML(look.slots)}
      ${missing.length ? `<span class="c-incomplete">Needs ${escapeHTML(missing[0].toLowerCase())}</span>` : ''}
    </div>
    <div class="look-body">
      <h3>${escapeHTML(name)}</h3>
      <div class="look-meta">
        ${look.rating ? starsHTML(look.rating) : ''}
        ${look.worn ? `<span class="worn">worn ${look.worn}×</span>` : ''}
        ${!look.rating && !look.worn ? '<span>Not worn yet</span>' : ''}
      </div>
      ${tags ? `<div class="card-foot">${tags}</div>` : ''}
    </div>
  </article>`;
}

/* ───────────────────────  builder  ──────────────────────── */
function buildBuilderControls() {
  el('lOccasions').innerHTML = OCCASIONS.map(o => `<button type="button" class="chip" data-locc2="${o}">${o}</button>`).join('');
  el('lStars').innerHTML = [1, 2, 3, 4, 5].map(i =>
    `<button type="button" data-star="${i}" role="radio" aria-checked="false" aria-label="${i} star${i === 1 ? '' : 's'}">★</button>`).join('');
}

const requiredMissing = slots => LOOK_SLOTS.filter(sl => sl.required && !(slots || {})[sl.id]).map(sl => sl.label);

function openBuilder(look) {
  state.editingLookId = look ? look.id : null;
  state.builder = look
    ? blankBuilder({
        slots: {
          top: look.slots.top || null, layer: look.slots.layer || null,
          bottom: look.slots.bottom || null, outer: look.slots.outer || null,
          foot: look.slots.foot || null, accessory: (look.slots.accessory || []).slice()
        },
        name: look.name || '',
        occasions: (look.occasions || []).slice(),
        rating: look.rating || 0
      })
    : blankBuilder();
  el('builderTitle').textContent = look ? 'Edit look' : 'Build a look';
  el('builderSave').textContent = look ? 'Save changes' : 'Save look';
  syncBuilderUI();
  openSheet('builder');
}

function syncBuilderUI() {
  const b = state.builder;
  el('lName').value = b.name;
  markGroup('lOccasions', x => b.occasions.includes(x.dataset.locc2));

  Array.from(el('lStars').children).forEach(x => {
    const on = Number(x.dataset.star) <= (b.rating || 0);
    x.classList.toggle('on', on);
    x.setAttribute('aria-checked', Number(x.dataset.star) === (b.rating || 0));
  });

  renderBuilderSlots();
  renderBuilderPreview();
}

function renderBuilderPreview() {
  el('builderPreview').innerHTML = collageHTML(state.builder.slots, { labelVoid: true });
  const missing = requiredMissing(state.builder.slots);
  el('builderHint').textContent = missing.length
    ? `Still need: ${missing.join(', ')}`
    : 'Complete — save it, or keep tweaking';
  el('builderSave').disabled = missing.length > 0;
}

function renderBuilderSlots() {
  const b = state.builder;
  el('builderSlots').innerHTML = LOOK_SLOTS.map(sl => {
    if (sl.multi) {
      const chosen = (b.slots.accessory || []).map(itemById).filter(Boolean);
      return `<div class="slotrow ${chosen.length ? '' : 'empty'}" data-slotrow="${sl.id}" role="button" tabindex="0">
          <span class="slotrow-thumb void">${PLUS_SVG}</span>
          <span class="slotrow-text">
            <b>${sl.label}</b>
            <em class="${chosen.length ? '' : 'ph'}">${chosen.length ? `${chosen.length} chosen — tap to add more` : sl.hint}</em>
          </span>
          <span class="slotrow-act">Add</span>
        </div>
        ${chosen.length ? `<div class="acc-chips">${chosen.map(it => `
          <span class="acc-chip">${cellInner(it)}${escapeHTML(autoName(it))}
            <button type="button" data-unacc="${it.id}" aria-label="Remove ${escapeAttr(autoName(it))}">&times;</button>
          </span>`).join('')}</div>` : ''}`;
    }

    const item = itemById(b.slots[sl.id]);
    if (!item) {
      return `<div class="slotrow empty ${sl.required ? 'required' : ''}" data-slotrow="${sl.id}" role="button" tabindex="0">
        <span class="slotrow-thumb void">${PLUS_SVG}</span>
        <span class="slotrow-text"><b>${sl.label}${sl.required ? ' ·' : ''}</b><em class="ph">${sl.hint}</em></span>
        <span class="slotrow-act">Choose</span>
      </div>`;
    }
    return `<div class="slotrow" data-slotrow="${sl.id}" role="button" tabindex="0">
      <span class="slotrow-thumb">${cellInner(item)}</span>
      <span class="slotrow-text">
        <b>${sl.label}</b>
        <em>${escapeHTML(autoName(item))}</em>
        ${item.laundry && item.laundry !== 'clean' ? `<small>${laundryById(item.laundry).label}</small>` : ''}
      </span>
      <button type="button" class="x" data-clearslot="${sl.id}" aria-label="Remove ${sl.label}">&times;</button>
    </div>`;
  }).join('');

  wireBuilderRows();
}

/* Listeners are bound straight onto the fresh nodes rather than delegated.
   innerHTML replaced them, so the old listeners go with the old nodes. */
function wireBuilderRows() {
  const box = el('builderSlots');

  box.querySelectorAll('[data-clearslot]').forEach(btn => {
    btn.addEventListener('click', ev => {
      ev.stopPropagation();
      state.builder.slots[btn.dataset.clearslot] = null;
      syncBuilderUI();
    });
  });

  box.querySelectorAll('[data-unacc]').forEach(btn => {
    btn.addEventListener('click', ev => {
      ev.stopPropagation();
      const arr = state.builder.slots.accessory || [];
      const i = arr.indexOf(btn.dataset.unacc);
      if (i >= 0) arr.splice(i, 1);
      syncBuilderUI();
    });
  });

  box.querySelectorAll('[data-slotrow]').forEach(row => {
    const go = () => openPicker(row.dataset.slotrow);
    row.addEventListener('click', ev => {
      if (ev.target.closest('[data-clearslot]') || ev.target.closest('[data-unacc]')) return;
      go();
    });
    row.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); go(); }
    });
  });
}

async function saveLook() {
  const b = state.builder;
  const missing = requiredMissing(b.slots);
  if (missing.length) return toast(`Still need: ${missing.join(', ')}`);

  const base = state.editingLookId ? state.looks.find(l => l.id === state.editingLookId) : null;
  const look = Object.assign({}, base || {}, {
    id: base ? base.id : Store.uid('o'),
    name: el('lName').value.trim(),
    slots: {
      top: b.slots.top, layer: b.slots.layer, bottom: b.slots.bottom,
      outer: b.slots.outer, foot: b.slots.foot,
      accessory: (b.slots.accessory || []).slice()
    },
    occasions: b.occasions.slice(),
    rating: b.rating || 0,
    worn: base ? (base.worn || 0) : 0,
    lastWorn: base ? (base.lastWorn || null) : null,
    createdAt: base ? base.createdAt : Date.now(),
    updatedAt: Date.now()
  });
  if (!look.name) look.name = autoLookName(look, state.items);

  try {
    await Store.putLook(look);
    closeSheet('builder');
    await reload();
    if (state.view !== 'outfits') setView('outfits'); else renderAll();
    toast(base ? 'Look updated' : `Saved “${look.name}”`);
    flashLook(look.id);
  } catch (err) {
    toast(err && err.message ? err.message : 'Could not save that look');
  }
}

function flashLook(id) {
  const card = document.querySelector(`.look[data-look="${id}"]`);
  if (!card) return;
  card.classList.add('flash');
  card.scrollIntoView({ behavior: 'smooth', block: 'center' });
  setTimeout(() => card.classList.remove('flash'), 1400);
}

/* ───────────────────────  picker  ───────────────────────── */
function builderChosenItems(exceptSlot) {
  const b = state.builder;
  const out = [];
  LOOK_SLOTS.forEach(sl => {
    if (sl.id === exceptSlot) return;
    const v = b.slots[sl.id];
    if (sl.multi) (v || []).forEach(id => { const it = itemById(id); if (it) out.push(it); });
    else { const it = itemById(v); if (it) out.push(it); }
  });
  return out;
}

function takenIds(exceptSlot) {
  const ids = new Set();
  LOOK_SLOTS.forEach(sl => {
    if (sl.id === exceptSlot) return;
    const v = state.builder.slots[sl.id];
    if (sl.multi) (v || []).forEach(id => ids.add(id));
    else if (v) ids.add(v);
  });
  return ids;
}

function openPicker(slotId) {
  const sl = lookSlotById(slotId);
  if (!sl) return showErr('Unknown slot: ' + slotId);

  if (!state.items.length) {
    toast('Add some clothes first');
    setView('wardrobe');
    return openAdd();
  }

  state.pickerFor = slotId;
  state.pickerQuery = '';
  el('pickerSearch').value = '';
  el('pickerTitle').textContent = sl.multi
    ? 'Add an accessory'
    : `Choose ${sl.label === 'Outerwear' ? 'outerwear' : 'a ' + sl.label.toLowerCase()}`;
  el('pickerShowAll').checked = state.pickerShowAll;
  el('pickerClear').textContent = sl.required ? 'Cancel' : 'Leave this empty';
  renderPicker();
  openSheet('picker');
  setTimeout(() => el('pickerSearch').focus({ preventScroll: true }), 280);
}

function renderPicker() {
  const sl = lookSlotById(state.pickerFor);
  if (!sl) return;
  const grid = el('pickerGrid');
  const empty = el('pickerEmpty');
  const taken = takenIds(sl.id);
  const chosenNow = sl.multi ? (state.builder.slots.accessory || []) : [state.builder.slots[sl.id]];
  const seeds = builderChosenItems(sl.id);

  const all = state.items.filter(i => i.slot === sl.from);
  let pool = state.pickerShowAll ? all : all.filter(isWearable);

  const q = state.pickerQuery.trim().toLowerCase();
  if (q) pool = pool.filter(i => haystack(i).includes(q));

  pool = pool.slice().sort((a, b) => {
    const d = matchScore(b, seeds).total - matchScore(a, seeds).total;
    if (d) return d;
    return autoName(a).localeCompare(autoName(b));
  });

  if (!pool.length) {
    grid.innerHTML = '';
    grid.hidden = true;
    empty.hidden = false;
    el('pickerEmptyTitle').textContent = all.length ? 'None available' : 'Nothing to pick';
    el('pickerEmptyMsg').textContent = !all.length
      ? `You have no ${sl.label.toLowerCase()} in the wardrobe yet. Add one and it will appear here.`
      : (q ? `Nothing matches “${q}”.`
           : `All your ${sl.label.toLowerCase()} are dirty or at the cleaner. Flip “Include dirty” above to pick one anyway.`);
    return;
  }
  empty.hidden = true;
  grid.hidden = false;

  grid.innerHTML = pool.map((item, i) => {
    const isTaken = taken.has(item.id);
    const isOn = chosenNow.includes(item.id);
    const score = matchScore(item, seeds);
    const st = item.laundry && item.laundry !== 'clean' ? item.laundry : null;
    const blocked = isTaken && !sl.multi;
    return `<button type="button" class="pick ${isOn ? 'on' : ''} ${blocked ? 'dim' : ''}"
        data-pick="${item.id}" ${blocked ? 'disabled' : ''} style="animation-delay:${Math.min(i * 12, 220)}ms"
        title="${escapeAttr(autoName(item))}">
      <span class="pthumb">${cellInner(item)}
        ${score.occ > 0 && !isOn ? '<span class="match">Matches</span>' : ''}
        ${blocked ? '<span class="taken">Used</span>' : ''}
        ${st ? `<i class="stat-dot ${st}" title="${laundryById(st).label}"></i>` : ''}
      </span>
      <span class="pname">${escapeHTML(autoName(item))}</span>
    </button>`;
  }).join('');

  grid.querySelectorAll('[data-pick]').forEach(btn => {
    btn.addEventListener('click', () => { if (!btn.disabled) choosePick(btn.dataset.pick); });
  });
}

function choosePick(itemId) {
  const sl = lookSlotById(state.pickerFor);
  if (!sl) return;
  if (sl.multi) {
    const arr = state.builder.slots.accessory || (state.builder.slots.accessory = []);
    const i = arr.indexOf(itemId);
    if (i >= 0) arr.splice(i, 1); else arr.push(itemId);
    syncBuilderUI();
    renderPicker();
    return;                       // stay open — accessories are additive
  }
  state.builder.slots[sl.id] = itemId;
  autoFillLookTags();
  syncBuilderUI();
  closeSheet('picker');
}

/** Guess the occasion for the look from the pieces chosen so far. */
function autoFillLookTags() {
  const b = state.builder;
  if (b.occasions.length) return;                 // respect what the user set
  const chosen = builderChosenItems(null);
  if (chosen.length < 2) return;
  const shared = chosen.reduce((acc, it) =>
    acc.filter(v => (it.occasions || []).includes(v)), (chosen[0].occasions || []).slice());
  if (shared.length) b.occasions = shared.slice(0, 2);
}

/* ─────────────────────  look detail  ────────────────────── */
function openLookDetail(id) {
  const look = state.looks.find(l => l.id === id);
  if (!look) return;
  state.lookDetailId = id;
  const name = look.name || autoLookName(look, state.items);
  el('lookTitle').textContent = name;

  const chipLine = list => (list || []).map(x => `<span class="tag">${escapeHTML(x)}</span>`).join('');
  const row = (k, v) => v ? `<div class="drow"><span>${k}</span><b>${v}</b></div>` : '';

  const pieces = LOOK_SLOTS.map(sl => {
    if (sl.multi) {
      return (look.slots.accessory || []).map(itemById).filter(Boolean)
        .map(it => pieceHTML(sl.label, it)).join('');
    }
    const it = itemById(look.slots[sl.id]);
    if (!it) return sl.required
      ? `<div class="piece missing"><span class="slotrow-thumb void">${PLUS_SVG}</span>
           <span class="piece-text"><b>${sl.label}</b><em>Missing — this item was deleted</em></span></div>`
      : '';
    return pieceHTML(sl.label, it);
  }).join('');

  el('lookBody').innerHTML = `
    <div class="builder-preview">${collageHTML(look.slots)}</div>
    <div class="detail-rows">
      ${chipLine(look.occasions) ? `<div class="drow col"><span>Occasions</span><div class="tagrow">${chipLine(look.occasions)}</div></div>` : ''}
      ${row('Rating', look.rating ? starsHTML(look.rating) : '')}
      ${row('Worn', look.worn ? `${look.worn} time${look.worn === 1 ? '' : 's'}` : '')}
      ${row('Last worn', look.lastWorn ? fmtDate(new Date(look.lastWorn).toISOString().slice(0, 10)) : '')}
    </div>
    <div class="field" style="margin-top:18px">
      <span class="field-label">Pieces</span>
      <div class="piece-list">${pieces}</div>
    </div>`;

  el('lookBody').querySelectorAll('[data-piece]').forEach(btn => {
    btn.addEventListener('click', () => openDetail(btn.dataset.piece));   // stacks on top
  });

  el('lookDelete').innerHTML = 'Delete';
  el('lookDelete').classList.remove('armed');
  openSheet('look');
}

function pieceHTML(label, item) {
  return `<button type="button" class="piece" data-piece="${item.id}">
    <span class="slotrow-thumb">${cellInner(item)}</span>
    <span class="piece-text"><b>${escapeHTML(label)}</b><em>${escapeHTML(autoName(item))}</em></span>
    <span class="go" aria-hidden="true">›</span>
  </button>`;
}

async function wearLook(id) {
  const look = state.looks.find(l => l.id === id);
  if (!look) return;
  const now = Date.now();
  const touched = [];
  lookItems(look).forEach(item => {
    item.worn = (item.worn || 0) + 1;
    item.lastWorn = now;
    item.laundry = 'worn';
    item.updatedAt = now;
    touched.push(item);
  });
  look.worn = (look.worn || 0) + 1;
  look.lastWorn = now;
  look.updatedAt = now;

  try {
    await Promise.all(touched.map(i => Store.put(i)));
    await Store.putLook(look);
    await reload();
    closeSheet('look');
    toast(`Logged — ${look.name || 'look'} worn ${look.worn}×`);
    flashLook(look.id);
  } catch (err) {
    toast('Could not log that wear');
  }
}

async function duplicateLook(id) {
  const look = state.looks.find(l => l.id === id);
  if (!look) return;
  const copy = Object.assign({}, look, {
    id: Store.uid('o'),
    name: (look.name || 'Look') + ' copy',
    slots: Object.assign({}, look.slots, { accessory: (look.slots.accessory || []).slice() }),
    worn: 0, lastWorn: null, createdAt: Date.now(), updatedAt: Date.now()
  });
  await Store.putLook(copy);
  await reload();
  closeSheet('look');
  toast('Duplicated');
  flashLook(copy.id);
}

/* ───────────────────────  shuffle  ──────────────────────── */
function shuffleLook() {
  const pool = state.items.filter(isWearable);
  const bySlot = s => pool.filter(i => i.slot === s);
  const tops = bySlot('top'), bottoms = bySlot('bottom'), feet = bySlot('foot');

  if (!tops.length || !bottoms.length || !feet.length) {
    return toast('You need at least one clean top, bottom and pair of shoes');
  }

  const occ = state.lookOccasion !== 'all' ? state.lookOccasion : null;
  const prefer = arr => {
    const m = occ ? arr.filter(i => (i.occasions || []).includes(occ)) : arr;
    return m.length ? m : arr;
  };
  const rand = arr => arr[Math.floor(Math.random() * arr.length)];
  const best = (arr, seeds) => {
    const scored = arr.map(i => ({ i, s: matchScore(i, seeds).total }));
    const good = scored.filter(x => x.s > 0);
    return rand(good.length ? good : scored).i;
  };

  const top = rand(prefer(tops));
  const bottom = best(prefer(bottoms), [top]);
  const foot = best(prefer(feet), [top, bottom]);

  const outerPool = bySlot('outer').filter(i => matchScore(i, [top, bottom, foot]).total > 0);
  const outer = outerPool.length && Math.random() < 0.6 ? rand(outerPool) : null;

  const accPool = bySlot('accessory').filter(i => matchScore(i, [top, bottom, foot]).total > 0);
  const accessory = accPool.slice(0, 6).filter(() => Math.random() < 0.45).slice(0, 2);

  const chosen = [top, bottom, foot].concat(outer ? [outer] : [], accessory);
  const shared = chosen.reduce((acc, it) =>
    acc.filter(v => (it.occasions || []).includes(v)), (chosen[0].occasions || []).slice());

  state.editingLookId = null;
  state.builder = blankBuilder({
    slots: { top: top.id, layer: null, bottom: bottom.id, outer: outer ? outer.id : null, foot: foot.id, accessory },
    name: '',
    occasions: (occ ? [occ] : shared.slice(0, 2)),
    rating: 0
  });
  el('builderTitle').textContent = 'Shuffled look';
  el('builderSave').textContent = 'Save look';
  syncBuilderUI();
  openSheet('builder');
  toast('Shuffled — tweak it or save it');
}

/* ─────────────────────  sheets / scrims  ────────────────── */
const sheetStack = [];

function openSheet(key) {
  const sheet = el(key + 'Sheet');
  const scrim = el(key + 'Scrim');
  if (!sheet || !scrim) return showErr('Missing sheet: ' + key);

  // Stacked sheets (the picker opens over the builder) must each sit above
  // the one below — a flat z-index would let the lower sheet paint on top.
  const depth = sheetStack.includes(key) ? sheetStack.indexOf(key) : sheetStack.length;
  scrim.style.zIndex = String(60 + depth * 10);
  sheet.style.zIndex = String(61 + depth * 10);

  sheet.hidden = false;
  scrim.hidden = false;
  document.body.classList.add('locked');
  requestAnimationFrame(() => {
    sheet.classList.add('open');
    scrim.classList.add('open');
  });
  if (!sheetStack.includes(key)) sheetStack.push(key);
}

function closeSheet(key) {
  const sheet = el(key + 'Sheet');
  const scrim = el(key + 'Scrim');
  if (!sheet || !scrim) return;
  sheet.classList.remove('open');
  scrim.classList.remove('open');
  const i = sheetStack.indexOf(key);
  if (i >= 0) sheetStack.splice(i, 1);
  setTimeout(() => {
    sheet.hidden = true;
    scrim.hidden = true;
    if (!sheetStack.length) document.body.classList.remove('locked');
  }, 240);
}

function closeTopSheet() {
  if (sheetStack.length) closeSheet(sheetStack[sheetStack.length - 1]);
}

/* ───────────────────────  toast  ────────────────────────── */
let toastTimer = null;
function toast(msg) {
  const t = el('toast');
  if (!t) return;
  t.textContent = msg;
  t.hidden = false;
  requestAnimationFrame(() => t.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    t.classList.remove('show');
    setTimeout(() => { t.hidden = true; }, 260);
  }, 2400);
}

/* ───────────────────────  events  ───────────────────────── */
function wireEvents() {
  /* tabs + FAB */
  document.querySelector('.tabbar').addEventListener('click', e => {
    const tab = e.target.closest('.tab');
    if (!tab) return;
    setView(tab.dataset.tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  el('fab').addEventListener('click', () => {
    if (state.view === 'outfits') openBuilder(null); else openAdd();
  });

  /* shared search */
  const search = el('search');
  search.addEventListener('input', () => {
    state.query = search.value;
    el('clearSearch').hidden = !search.value;
    if (state.view === 'outfits') renderLooks(); else renderGrid();
  });
  el('clearSearch').addEventListener('click', () => {
    search.value = ''; state.query = ''; el('clearSearch').hidden = true;
    if (state.view === 'outfits') renderLooks(); else renderGrid();
    search.focus();
  });
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); el('search').focus(); }
    if (e.key === 'Escape') closeTopSheet();
  });

  /* ── wardrobe chrome ── */
  el('slots').addEventListener('click', e => {
    const b = e.target.closest('[data-slot]');
    if (!b) return;
    state.slot = b.dataset.slot;
    state.types.clear();
    renderSlots(); renderTypes(); renderGrid();
  });
  el('types').addEventListener('click', e => {
    const b = e.target.closest('[data-type]');
    if (!b) return;
    const id = b.dataset.type;
    if (!id) state.types.clear();
    else if (state.types.has(id)) state.types.delete(id);
    else state.types.add(id);
    renderTypes(); renderGrid();
  });
  el('sort').addEventListener('change', e => { state.sort = e.target.value; renderGrid(); });

  /* grid: laundry badge cycles, card opens detail */
  el('grid').addEventListener('click', async e => {
    const cyc = e.target.closest('[data-cycle]');
    if (cyc) {
      e.stopPropagation();
      const item = itemById(cyc.dataset.cycle);
      if (item) await setLaundry(item.id, nextLaundry(item.laundry || 'clean'));
      return;
    }
    const card = e.target.closest('.card');
    if (card) openDetail(card.dataset.id);
  });
  el('grid').addEventListener('keydown', async e => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const cyc = e.target.closest('[data-cycle]');
    if (cyc) {
      e.preventDefault();
      const item = itemById(cyc.dataset.cycle);
      if (item) await setLaundry(item.id, nextLaundry(item.laundry || 'clean'));
      return;
    }
    const card = e.target.closest('.card');
    if (card) { e.preventDefault(); openDetail(card.dataset.id); }
  });

  el('emptyAdd').addEventListener('click', openAdd);
  el('emptySample').addEventListener('click', loadSamples);
  el('clearFilters').addEventListener('click', clearFilters);

  /* ── outfit chrome ── */
  el('lookOccasions').addEventListener('click', e => {
    const b = e.target.closest('[data-locc]');
    if (!b) return;
    state.lookOccasion = b.dataset.locc || 'all';
    renderLookOccasions(); renderLooks();
  });
  el('lookSort').addEventListener('change', e => { state.lookSort = e.target.value; renderLooks(); });
  el('shuffleBtn').addEventListener('click', shuffleLook);
  el('emptyNewLook').addEventListener('click', () => openBuilder(null));
  el('emptyShuffle').addEventListener('click', shuffleLook);
  el('clearLookFilters').addEventListener('click', () => {
    state.lookOccasion = 'all'; state.query = '';
    el('search').value = ''; el('clearSearch').hidden = true;
    renderLookOccasions(); renderLooks();
  });

  el('lookGrid').addEventListener('click', e => {
    const card = e.target.closest('[data-look]');
    if (card) openLookDetail(card.dataset.look);
  });
  el('lookGrid').addEventListener('keydown', e => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const card = e.target.closest('[data-look]');
    if (card) { e.preventDefault(); openLookDetail(card.dataset.look); }
  });

  /* ── item form sheet ── */
  el('formClose').addEventListener('click', () => closeSheet('form'));
  el('formCancel').addEventListener('click', () => closeSheet('form'));
  el('formScrim').addEventListener('click', () => closeSheet('form'));
  el('formSave').addEventListener('click', saveForm);

  el('fSlot').addEventListener('click', e => {
    const b = e.target.closest('[data-fslot]');
    if (!b) return;
    state.form.slot = b.dataset.fslot;
    syncFormUI();
  });
  el('fLaundry').addEventListener('click', e => {
    const b = e.target.closest('[data-flaundry]');
    if (!b) return;
    state.form.laundry = b.dataset.flaundry;
    markGroup('fLaundry', x => x.dataset.flaundry === state.form.laundry);
  });
  el('fType').addEventListener('click', e => {
    const b = e.target.closest('[data-ftype]');
    if (!b) return;
    state.form.type = b.dataset.ftype;
    renderFormTypes();
  });
  el('fOccasions').addEventListener('click', e => {
    const b = e.target.closest('[data-occ]');
    if (!b) return;
    toggleIn(state.form.occasions, b.dataset.occ);
    b.classList.toggle('on');
  });

  /* Photo inputs are triggered by <label for> in the markup — no script.
     A sandboxed preview iframe can block a programmatic input.click(),
     but it cannot block a label activating its own control. */
  el('photoInput').addEventListener('change', e => { handlePhotoFile(e.target.files[0]); e.target.value = ''; });
  el('galleryInput').addEventListener('change', e => { handlePhotoFile(e.target.files[0]); e.target.value = ''; });
  el('photoRemove').addEventListener('click', () => { state.form.photoBlob = null; syncFormUI(); });

  /* ── item detail sheet ── */
  el('detailClose').addEventListener('click', () => closeSheet('detail'));
  el('detailScrim').addEventListener('click', () => closeSheet('detail'));
  el('detailEdit').addEventListener('click', () => openEdit(state.detailId));
  el('detailBody').addEventListener('click', e => {
    const b = e.target.closest('[data-laundry]');
    if (b && state.detailId) setLaundry(state.detailId, b.dataset.laundry);
  });
  el('detailDelete').addEventListener('click', async () => {
    const btn = el('detailDelete');
    const id = state.detailId;
    await tapTwice(btn, 'Tap again to delete', 'Delete', async () => {
      await Store.remove(id);
      closeSheet('detail');
      await reload();
      toast('Item deleted');
    });
  });

  /* ── builder sheet ── */
  el('builderClose').addEventListener('click', () => closeSheet('builder'));
  el('builderCancel').addEventListener('click', () => closeSheet('builder'));
  el('builderScrim').addEventListener('click', () => closeSheet('builder'));
  el('builderSave').addEventListener('click', saveLook);

  el('lOccasions').addEventListener('click', e => {
    const b = e.target.closest('[data-locc2]');
    if (!b) return;
    toggleIn(state.builder.occasions, b.dataset.locc2);
    b.classList.toggle('on');
  });
  el('lStars').addEventListener('click', e => {
    const b = e.target.closest('[data-star]');
    if (!b) return;
    const v = Number(b.dataset.star);
    state.builder.rating = state.builder.rating === v ? 0 : v;   // tap again to clear
    syncBuilderUI();
  });

  /* ── picker sheet ── */
  el('pickerClose').addEventListener('click', () => closeSheet('picker'));
  el('pickerScrim').addEventListener('click', () => closeSheet('picker'));
  el('pickerSearch').addEventListener('input', e => { state.pickerQuery = e.target.value; renderPicker(); });
  el('pickerShowAll').addEventListener('change', e => { state.pickerShowAll = e.target.checked; renderPicker(); });
  el('pickerClear').addEventListener('click', () => {
    const sl = lookSlotById(state.pickerFor);
    if (sl && !sl.required) {
      state.builder.slots[sl.id] = sl.multi ? [] : null;
      syncBuilderUI();
    }
    closeSheet('picker');
  });
  el('pickerAddItem').addEventListener('click', () => { closeSheet('picker'); openAdd(); });

  /* ── look detail sheet ── */
  el('lookClose').addEventListener('click', () => closeSheet('look'));
  el('lookScrim').addEventListener('click', () => closeSheet('look'));
  el('lookEdit').addEventListener('click', () => {
    const look = state.looks.find(l => l.id === state.lookDetailId);
    closeSheet('look');
    if (look) setTimeout(() => openBuilder(look), 200);
  });
  el('lookWear').addEventListener('click', () => wearLook(state.lookDetailId));
  el('lookDuplicate').addEventListener('click', () => duplicateLook(state.lookDetailId));
  el('lookDelete').addEventListener('click', async () => {
    const btn = el('lookDelete');
    const id = state.lookDetailId;
    await tapTwice(btn, 'Tap again', 'Delete', async () => {
      await Store.removeLook(id);
      closeSheet('look');
      await reload();
      toast('Look deleted');
    });
  });

  /* ── menu sheet ── */
  el('themeSeg').addEventListener('click', e => {
    const b = e.target.closest('[data-theme-pick]');
    if (b) applyTheme(b.dataset.themePick);
  });
  el('menuBtn').addEventListener('click', () => { renderHeader(); openSheet('menu'); });
  el('menuClose').addEventListener('click', () => closeSheet('menu'));
  el('menuScrim').addEventListener('click', () => closeSheet('menu'));
  el('mExport').addEventListener('click', doExport);
  el('mImport').addEventListener('click', () => el('importInput').click());

  const SAMPLE_HTML = '<span>Load sample clothes</span><em>Demo data, no photos</em>';
  el('mSample').addEventListener('click', () => tapTwice(el('mSample'),
    '<span>Tap again to load</span><em>Replaces your current items and looks</em>',
    SAMPLE_HTML, loadSamples));

  const RESET_HTML = '<span>Erase everything</span><em>Cannot be undone</em>';
  el('mReset').addEventListener('click', () => tapTwice(el('mReset'),
    '<span>Tap again to erase</span><em>All items and looks will be gone</em>',
    RESET_HTML, async () => {
      await Store.replaceAll([]);
      await Store.replaceAllLooks([]);
      closeSheet('menu');
      await reload();
      toast('Wardrobe and looks erased');
    }));

  el('importInput').addEventListener('change', async e => {
    const file = e.target.files[0];
    e.target.value = '';
    if (!file) return;
    try {
      const data = await Store.importJSON(await file.text());
      closeSheet('menu');
      await reload();
      toast(`Imported ${data.items.length} items, ${data.looks.length} looks`);
    } catch (err) {
      toast(err && err.message ? err.message : 'Import failed');
    }
  });
}

/* ─────────────────────  menu actions  ───────────────────── */
/**
 * In-app tap-twice confirmation. `window.confirm` is blocked outright in a
 * sandboxed preview iframe, where it silently returns false — so anything
 * guarded by it simply never happens.
 */
function tapTwice(node, armedHTML, normalHTML, onConfirm) {
  if (node.dataset.armed === '1') {
    delete node.dataset.armed;
    clearTimeout(node._armTimer);
    node.classList.remove('armed');
    node.innerHTML = normalHTML;
    return onConfirm();
  }
  node.dataset.armed = '1';
  node.classList.add('armed');
  node.innerHTML = armedHTML;
  node._armTimer = setTimeout(() => {
    delete node.dataset.armed;
    node.classList.remove('armed');
    node.innerHTML = normalHTML;
  }, 3200);
}

async function loadSamples() {
  const seed = Store.seedSamples();
  await Store.replaceAll(seed.items);
  await Store.replaceAllLooks(seed.looks);
  closeSheet('menu');
  await reload();
  toast(`${seed.items.length} items and ${seed.looks.length} looks loaded`);
}

async function doExport() {
  try {
    const json = await Store.exportJSON(state.items, state.looks);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `my-wardrobe-backup-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
    toast('Backup downloaded');
  } catch (err) {
    toast('Export failed');
  }
}

function clearFilters() {
  state.slot = 'all';
  state.types.clear();
  state.query = '';
  el('search').value = '';
  el('clearSearch').hidden = true;
  renderAll();
}

/* ─────────────────────  small utils  ────────────────────── */
function toggleIn(arr, val) {
  const i = arr.indexOf(val);
  if (i >= 0) arr.splice(i, 1); else arr.push(val);
}

function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso.length <= 10 ? iso + 'T00:00:00' : iso);
  if (isNaN(d)) return '';
  return new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }).format(d);
}

function escapeHTML(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
const escapeAttr = escapeHTML;
