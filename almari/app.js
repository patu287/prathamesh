/* ══════════════════════════════════════════════════════════════════
   Almari · app.js
   Wardrobe screen: categories, filters, search, the shelf grid,
   add/edit item sheet and item detail sheet.
   ══════════════════════════════════════════════════════════════════ */

const el = id => document.getElementById(id);

const state = {
  items: [],
  slot: 'all',
  types: new Set(),
  query: '',
  sort: 'new',
  editingId: null,
  detailId: null,
  form: blankForm()
};

let previewURL = null;   // object URL for the form's photo preview

function blankForm() {
  return {
    photoBlob: null,
    name: '', slot: 'top', type: 'shirt',
    colors: [], occasions: [], seasons: [],
    size: '', brand: '', fabric: '', pattern: '',
    price: '', bought: '', notes: ''
  };
}

const HANGER_SVG = `<svg viewBox="0 0 48 34" aria-hidden="true">
  <path d="M24 8.5c0-3 4.6-3 4.6 0 0 2.2-2.4 2.9-4.6 4v2.1"/>
  <path d="M24 14.6 4.6 24.4c-1.6.8-1.4 3.1.4 3.6L24 32.6l19-4.6c1.8-.5 2-2.8.4-3.6L24 14.6z"/>
</svg>`;

/* ─────────────────────────  boot  ───────────────────────── */
(async function init() {
  buildFormControls();
  wireEvents();
  await reload();
})();

async function reload() {
  state.items = await Store.all();
  renderAll();
}

function renderAll() {
  renderSlots();
  renderTypes();
  renderGrid();
  renderHeader();
}

/* ─────────────────────  header + counts  ────────────────── */
function renderHeader() {
  const n = state.items.length;
  const withPhoto = state.items.filter(i => i.photoBlob).length;
  if (n === 0) {
    el('countLine').textContent = 'No items yet';
  } else {
    const tops = state.items.filter(i => i.slot === 'top').length;
    const bottoms = state.items.filter(i => i.slot === 'bottom').length;
    el('countLine').textContent = `${n} item${n === 1 ? '' : 's'} · ${tops} tops · ${bottoms} bottoms`;
  }
  const stats = el('menuStats');
  if (stats) {
    const rows = SLOTS.map(s => `<div class="stat"><b>${state.items.filter(i => i.slot === s.id).length}</b><span>${s.label}</span></div>`).join('');
    stats.innerHTML = `
      <div class="stat big"><b>${n}</b><span>total items</span></div>
      ${rows}
      <div class="stat"><b>${withPhoto}</b><span>with photo</span></div>`;
  }
}

/* ─────────────────────  category tabs  ──────────────────── */
function renderSlots() {
  const tabs = [{ id: 'all', label: 'Everything' }].concat(SLOTS);
  el('slots').innerHTML = tabs.map(s => {
    const count = s.id === 'all' ? state.items.length : state.items.filter(i => i.slot === s.id).length;
    return `<button class="slot ${state.slot === s.id ? 'on' : ''}" data-slot="${s.id}" aria-pressed="${state.slot === s.id}">
      <span>${s.label}</span><em>${count}</em></button>`;
  }).join('');
}

/* ─────────────────────  type filter chips  ──────────────── */
function renderTypes() {
  const list = state.slot === 'all' ? TYPES : typesIn(state.slot);
  const used = new Set(state.items.map(i => i.type));
  const relevant = list.filter(t => used.has(t.id) || state.types.has(t.id));
  const wrap = el('types');
  if (!relevant.length) { wrap.innerHTML = ''; wrap.hidden = true; return; }
  wrap.hidden = false;
  const allOn = state.types.size === 0;
  wrap.innerHTML = `<button class="chip ${allOn ? 'on' : ''}" data-type="">All</button>` +
    relevant.map(t => {
      const n = state.items.filter(i => i.type === t.id).length;
      return `<button class="chip ${state.types.has(t.id) ? 'on' : ''}" data-type="${t.id}">${t.label}<em>${n}</em></button>`;
    }).join('');
}

/* ─────────────────────  filtering + sorting  ────────────── */
function visibleItems() {
  const q = state.query.trim().toLowerCase();
  let list = state.items.filter(item => {
    if (state.slot !== 'all' && item.slot !== state.slot) return false;
    if (state.types.size && !state.types.has(item.type)) return false;
    if (q && !haystack(item).includes(q)) return false;
    return true;
  });
  const by = {
    new:  (a, b) => (b.createdAt || 0) - (a.createdAt || 0),
    old:  (a, b) => (a.createdAt || 0) - (b.createdAt || 0),
    name: (a, b) => (a.name || autoName(a)).localeCompare(b.name || autoName(b)),
    type: (a, b) => typeById(a.type).label.localeCompare(typeById(b.type).label) ||
                    (a.name || '').localeCompare(b.name || '')
  }[state.sort];
  return list.sort(by);
}

/* ─────────────────────  the shelf grid  ─────────────────── */
function renderGrid() {
  const list = visibleItems();
  const grid = el('grid');
  const firstEmpty = el('emptyFirst');
  const filterEmpty = el('emptyFilter');

  const nothingAtAll = state.items.length === 0;
  firstEmpty.hidden = !nothingAtAll;
  filterEmpty.hidden = nothingAtAll || list.length > 0;
  grid.hidden = list.length === 0;

  el('resultCount').textContent = nothingAtAll ? '' :
    `${list.length} ${list.length === 1 ? 'item' : 'items'}${state.slot === 'all' ? '' : ' in ' + slotById(state.slot).label.toLowerCase()}`;

  if (!list.length) return;
  grid.innerHTML = list.map(cardHTML).join('');

  if (filterEmpty.hidden === false) {
    el('emptyFilterMsg').textContent = state.query
      ? `Nothing matches “${state.query}”.`
      : 'No items in this category yet.';
  }
}

function cardHTML(item) {
  const name = item.name || autoName(item);
  const type = typeById(item.type);
  const url = Store.photoURL(item);
  const colors = (item.colors || []).map(id => colorById(id)).filter(Boolean);
  const bg = colors.length
    ? `background:linear-gradient(140deg, ${colors.map(c => c.hex).join(', ')})`
    : 'background:linear-gradient(140deg,#E7DECF,#D6C7B1)';

  const thumb = url
    ? `<img src="${url}" alt="${escapeAttr(name)}" loading="lazy" />`
    : `<span class="tile" style="${bg}" aria-hidden="true">
         <span class="hanger">${HANGER_SVG}</span>
         <span class="tile-label">${type.label}</span>
       </span>`;

  const meta = [type.label, item.size && `Size ${item.size}`].filter(Boolean).join(' · ');
  const dots = colors.slice(0, 4).map(c =>
    `<i class="dot" style="background:${c.hex}" title="${c.label}"></i>`).join('');
  const tags = (item.occasions || []).slice(0, 2)
    .map(o => `<span class="tag">${o}</span>`).join('');

  return `<article class="card" data-id="${item.id}" tabindex="0" role="button" aria-label="${escapeAttr(name)}">
    <div class="thumb">${thumb}</div>
    <div class="card-body">
      <h3>${escapeHTML(name)}</h3>
      <p class="card-meta">${escapeHTML(meta)}</p>
      <div class="card-foot">${dots ? `<span class="dots">${dots}</span>` : ''}${tags}</div>
    </div>
  </article>`;
}

/* ─────────────────────  item detail  ────────────────────── */
function openDetail(id) {
  const item = state.items.find(i => i.id === id);
  if (!item) return;
  state.detailId = id;
  el('detailTitle').textContent = item.name || autoName(item);

  const url = Store.photoURL(item);
  const colors = (item.colors || []).map(c => colorById(c)).filter(Boolean);
  const hero = url
    ? `<img class="hero" src="${url}" alt="${escapeAttr(item.name || autoName(item))}" />`
    : `<div class="hero tile" style="${colors.length ? `background:linear-gradient(140deg,${colors.map(c => c.hex).join(',')})` : 'background:linear-gradient(140deg,#E7DECF,#D6C7B1)'}">
         <span class="hanger">${HANGER_SVG}</span><span class="tile-label">${typeById(item.type).label}</span></div>`;

  const row = (k, v) => v ? `<div class="drow"><span>${k}</span><b>${escapeHTML(String(v))}</b></div>` : '';
  const chipLine = list => (list || []).map(x => `<span class="tag">${escapeHTML(x)}</span>`).join('');

  el('detailBody').innerHTML = `
    ${hero}
    <div class="detail-rows">
      ${row('Category', slotById(item.slot).label)}
      ${row('Type', typeById(item.type).label)}
      ${row('Size', item.size)}
      ${row('Brand', item.brand)}
      ${row('Fabric', item.fabric)}
      ${row('Pattern', item.pattern)}
      ${row('Price paid', item.price ? '₹' + Number(item.price).toLocaleString('en-IN') : '')}
      ${row('Bought on', item.bought ? fmtDate(item.bought) : '')}
      ${row('Added', fmtDate(new Date(item.createdAt || Date.now()).toISOString().slice(0, 10)))}
      ${(colors.length) ? `<div class="drow"><span>Colours</span><b class="colorline"><span class="dots">${colors.map(c => `<i class="dot" style="background:${c.hex}" title="${c.label}"></i>`).join('')}</span>${escapeHTML(colors.map(c => c.label).join(', '))}</b></div>` : ''}
      ${chipLine(item.occasions) ? `<div class="drow col"><span>Occasions</span><div class="tagrow">${chipLine(item.occasions)}</div></div>` : ''}
      ${chipLine(item.seasons) ? `<div class="drow col"><span>Seasons</span><div class="tagrow">${chipLine(item.seasons)}</div></div>` : ''}
      ${item.notes ? `<div class="drow col"><span>Notes</span><p class="notes">${escapeHTML(item.notes)}</p></div>` : ''}
    </div>`;

  const del = el('detailDelete');
  del.textContent = 'Delete';
  del.classList.remove('armed');
  openSheet('detail');
}

/* ─────────────────────  add / edit form  ────────────────── */
function buildFormControls() {
  el('fSlot').innerHTML = SLOTS.map(s =>
    `<button type="button" class="seg" data-slot="${s.id}" role="radio" aria-checked="false">${s.short}</button>`).join('');

  el('fColors').innerHTML = COLORS.map(c =>
    `<button type="button" class="swatch" data-color="${c.id}" style="--sw:${c.hex}" title="${c.label}" aria-label="${c.label}">
       <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true"><path d="M3 8.4l3.2 3.2L13 4.8"/></svg>
     </button>`).join('');

  el('fOccasions').innerHTML = OCCASIONS.map(o => `<button type="button" class="chip" data-occ="${o}">${o}</button>`).join('');
  el('fSeasons').innerHTML = SEASONS.map(s => `<button type="button" class="chip" data-sea="${s}">${s}</button>`).join('');
  fillSelect('fFabric', FABRICS, 'Not specified');
  fillSelect('fPattern', PATTERNS, 'Not specified');
  renderFormTypes();
  syncFormUI();
}

function fillSelect(id, values, placeholder) {
  el(id).innerHTML = `<option value="">${placeholder}</option>` +
    values.map(v => `<option value="${v}">${v}</option>`).join('');
}

function renderFormTypes() {
  const list = typesIn(state.form.slot);
  if (!list.some(t => t.id === state.form.type)) state.form.type = list[0].id;
  el('fType').innerHTML = list.map(t =>
    `<button type="button" class="chip ${t.id === state.form.type ? 'on' : ''}" data-ftype="${t.id}">${t.label}</button>`).join('');
}

function syncFormUI() {
  const f = state.form;
  Array.from(el('fSlot').children).forEach(b => {
    const on = b.dataset.slot === f.slot;
    b.classList.toggle('on', on);
    b.setAttribute('aria-checked', on);
  });
  renderFormTypes();
  Array.from(el('fColors').children).forEach(b => b.classList.toggle('on', f.colors.includes(b.dataset.color)));
  Array.from(el('fOccasions').children).forEach(b => b.classList.toggle('on', f.occasions.includes(b.dataset.occ)));
  Array.from(el('fSeasons').children).forEach(b => b.classList.toggle('on', f.seasons.includes(b.dataset.sea)));

  el('fName').value = f.name;
  el('fSize').value = f.size;
  el('fBrand').value = f.brand;
  el('fFabric').value = f.fabric;
  el('fPattern').value = f.pattern;
  el('fPrice').value = f.price;
  el('fBought').value = f.bought;
  el('fNotes').value = f.notes;

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

function openAdd() {
  state.editingId = null;
  state.form = blankForm();
  syncFormUI();
  openSheet('form');
  setTimeout(() => el('fName').focus({ preventScroll: true }), 260);
}

function openEdit(id) {
  const item = state.items.find(i => i.id === id);
  if (!item) return;
  state.editingId = id;
  state.form = Object.assign(blankForm(), {
    photoBlob: item.photoBlob || null,
    name: item.name || '',
    slot: item.slot || 'top',
    type: item.type || 'shirt',
    colors: (item.colors || []).slice(),
    occasions: (item.occasions || []).slice(),
    seasons: (item.seasons || []).slice(),
    size: item.size || '', brand: item.brand || '',
    fabric: item.fabric || '', pattern: item.pattern || '',
    price: item.price || '', bought: item.bought || '', notes: item.notes || ''
  });
  syncFormUI();
  closeSheet('detail');
  openSheet('form');
}

async function saveForm() {
  const f = state.form;
  if (!f.slot || !f.type) return toast('Pick a category and type');

  const base = state.editingId ? state.items.find(i => i.id === state.editingId) : null;
  const item = {
    id: base ? base.id : Store.uid(),
    photoBlob: f.photoBlob || null,
    name: (el('fName').value || '').trim(),
    slot: f.slot,
    type: f.type,
    colors: f.colors.slice(),
    occasions: f.occasions.slice(),
    seasons: f.seasons.slice(),
    size: el('fSize').value.trim(),
    brand: el('fBrand').value.trim(),
    fabric: el('fFabric').value,
    pattern: el('fPattern').value,
    price: el('fPrice').value ? Number(el('fPrice').value) : null,
    bought: el('fBought').value || '',
    notes: el('fNotes').value.trim(),
    worn: base ? (base.worn || 0) : 0,
    lastWorn: base ? (base.lastWorn || null) : null,
    createdAt: base ? base.createdAt : Date.now(),
    updatedAt: Date.now()
  };
  if (!item.name) item.name = autoName(item);

  try {
    if (base) Store.forgetPhoto(base.id);
    await Store.put(item);
    closeSheet('form');
    await reload();
    toast(base ? 'Changes saved' : `Added “${item.name}”`);
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
let galleryInput = null;

async function handlePhotoFile(file) {
  if (!file) return;
  const drop = el('photoDrop');
  drop.classList.add('busy');
  try {
    state.form.photoBlob = await Store.compressImage(file);
    syncFormUI();
  } catch (err) {
    toast(err && err.message ? err.message : 'Could not read that photo');
  } finally {
    drop.classList.remove('busy');
  }
}

/* ─────────────────────  sheets / scrims  ────────────────── */
const SHEETS = { form: 'form', detail: 'detail', menu: 'menu', outfit: 'outfit' };
const sheetStack = [];

function openSheet(key) {
  const sheet = el(key + 'Sheet');
  const scrim = el(key + 'Scrim');
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

/* ─────────────────────  toast  ──────────────────────────── */
let toastTimer = null;
function toast(msg) {
  const t = el('toast');
  t.textContent = msg;
  t.hidden = false;
  requestAnimationFrame(() => t.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    t.classList.remove('show');
    setTimeout(() => { t.hidden = true; }, 260);
  }, 2400);
}

/* ─────────────────────  events  ─────────────────────────── */
function wireEvents() {
  /* category tabs */
  el('slots').addEventListener('click', e => {
    const b = e.target.closest('[data-slot]');
    if (!b) return;
    state.slot = b.dataset.slot;
    state.types.clear();
    renderTypes(); renderGrid(); renderSlots();
  });

  /* type chips */
  el('types').addEventListener('click', e => {
    const b = e.target.closest('[data-type]');
    if (!b) return;
    const id = b.dataset.type;
    if (!id) state.types.clear();
    else if (state.types.has(id)) state.types.delete(id);
    else state.types.add(id);
    renderTypes(); renderGrid();
  });

  /* search */
  const search = el('search');
  search.addEventListener('input', () => {
    state.query = search.value;
    el('clearSearch').hidden = !search.value;
    renderGrid();
  });
  el('clearSearch').addEventListener('click', () => {
    search.value = ''; state.query = ''; el('clearSearch').hidden = true; renderGrid(); search.focus();
  });

  /* sort */
  el('sort').addEventListener('change', e => { state.sort = e.target.value; renderGrid(); });

  /* grid → detail */
  el('grid').addEventListener('click', e => {
    const card = e.target.closest('.card');
    if (card) openDetail(card.dataset.id);
  });
  el('grid').addEventListener('keydown', e => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const card = e.target.closest('.card');
    if (card) { e.preventDefault(); openDetail(card.dataset.id); }
  });

  /* empty states */
  el('emptyAdd').addEventListener('click', openAdd);
  el('emptySample').addEventListener('click', loadSamples);
  el('clearFilters').addEventListener('click', clearFilters);

  /* FAB + tabs */
  el('fab').addEventListener('click', openAdd);
  document.querySelector('.tabbar').addEventListener('click', e => {
    const tab = e.target.closest('.tab');
    if (!tab) return;
    if (tab.dataset.tab === 'outfits') openSheet('outfit');
    else { closeSheet('outfit'); window.scrollTo({ top: 0, behavior: 'smooth' }); }
  });
  el('outfitGo').addEventListener('click', () => closeSheet('outfit'));
  el('outfitClose').addEventListener('click', () => closeSheet('outfit'));
  el('outfitScrim').addEventListener('click', () => closeSheet('outfit'));

  /* ── form sheet ── */
  el('formClose').addEventListener('click', () => closeSheet('form'));
  el('formCancel').addEventListener('click', () => closeSheet('form'));
  el('formScrim').addEventListener('click', () => closeSheet('form'));
  el('formSave').addEventListener('click', saveForm);

  el('fSlot').addEventListener('click', e => {
    const b = e.target.closest('[data-slot]');
    if (!b) return;
    state.form.slot = b.dataset.slot;
    syncFormUI();
  });
  el('fType').addEventListener('click', e => {
    const b = e.target.closest('[data-ftype]');
    if (!b) return;
    state.form.type = b.dataset.ftype;
    renderFormTypes();
  });
  el('fColors').addEventListener('click', e => {
    const b = e.target.closest('[data-color]');
    if (!b) return;
    toggleIn(state.form.colors, b.dataset.color);
    b.classList.toggle('on');
  });
  el('fOccasions').addEventListener('click', e => {
    const b = e.target.closest('[data-occ]');
    if (!b) return;
    toggleIn(state.form.occasions, b.dataset.occ);
    b.classList.toggle('on');
  });
  el('fSeasons').addEventListener('click', e => {
    const b = e.target.closest('[data-sea]');
    if (!b) return;
    toggleIn(state.form.seasons, b.dataset.sea);
    b.classList.toggle('on');
  });

  /* photo */
  const photoInput = el('photoInput');
  galleryInput = photoInput.cloneNode(true);
  galleryInput.removeAttribute('capture');
  galleryInput.id = 'galleryInput';
  document.body.appendChild(galleryInput);

  photoInput.addEventListener('change', e => { handlePhotoFile(e.target.files[0]); e.target.value = ''; });
  galleryInput.addEventListener('change', e => { handlePhotoFile(e.target.files[0]); e.target.value = ''; });
  el('photoDrop').addEventListener('click', () => photoInput.click());
  el('photoPick').addEventListener('click', () => galleryInput.click());
  el('photoRemove').addEventListener('click', () => {
    state.form.photoBlob = null;
    syncFormUI();
  });

  /* ── detail sheet ── */
  el('detailClose').addEventListener('click', () => closeSheet('detail'));
  el('detailScrim').addEventListener('click', () => closeSheet('detail'));
  el('detailEdit').addEventListener('click', () => openEdit(state.detailId));
  el('detailDelete').addEventListener('click', async () => {
    const btn = el('detailDelete');
    if (!btn.classList.contains('armed')) {
      btn.classList.add('armed');
      btn.textContent = 'Tap again to delete';
      setTimeout(() => { btn.classList.remove('armed'); btn.textContent = 'Delete'; }, 3200);
      return;
    }
    const id = state.detailId;
    await Store.remove(id);
    closeSheet('detail');
    await reload();
    toast('Item deleted');
  });

  /* ── menu sheet ── */
  el('menuBtn').addEventListener('click', () => { renderHeader(); openSheet('menu'); });
  el('menuClose').addEventListener('click', () => closeSheet('menu'));
  el('menuScrim').addEventListener('click', () => closeSheet('menu'));
  el('mSample').addEventListener('click', loadSamples);
  el('mExport').addEventListener('click', doExport);
  el('mImport').addEventListener('click', () => el('importInput').click());
  el('mReset').addEventListener('click', async () => {
    const btn = el('mReset');
    if (!btn.classList.contains('armed')) {
      btn.classList.add('armed');
      btn.querySelector('span').textContent = 'Tap again to erase';
      setTimeout(() => { btn.classList.remove('armed'); btn.querySelector('span').textContent = 'Erase everything'; }, 3200);
      return;
    }
    await Store.replaceAll([]);
    state.items = [];
    closeSheet('menu');
    renderAll();
    toast('Wardrobe erased');
  });
  el('importInput').addEventListener('change', async e => {
    const file = e.target.files[0];
    e.target.value = '';
    if (!file) return;
    try {
      const items = await Store.importJSON(await file.text());
      state.items = items;
      closeSheet('menu');
      renderAll();
      toast(`Imported ${items.length} items`);
    } catch (err) {
      toast(err && err.message ? err.message : 'Import failed');
    }
  });

  /* keyboard */
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeTopSheet();
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); el('search').focus(); }
  });
}

/* ─────────────────────  menu actions  ───────────────────── */
async function loadSamples() {
  if (state.items.length && !window.confirm('Replace your current wardrobe with the sample data?')) return;
  await Store.replaceAll(Store.seedSamples());
  closeSheet('menu');
  await reload();
  toast('Sample wardrobe loaded');
}

async function doExport() {
  try {
    const json = await Store.exportJSON(state.items);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `almari-backup-${new Date().toISOString().slice(0, 10)}.json`;
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
