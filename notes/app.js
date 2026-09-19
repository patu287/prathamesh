/* ══════════════════════════════════════════════════════════════════
   Notes · app.js
   State, rendering, every UI event. No framework, no build step.

   The one loop this app exists to serve:
     write the day → promote a sentence → it becomes a key point
       → the aspects view shows it back to you
   ══════════════════════════════════════════════════════════════════ */

/* ── state ──────────────────────────────────────────────────────── */
const S = {
  entries: [], media: [], keypoints: [], aspects: [],
  meta: {},
  view: 'today',
  entry: null,            // entry open in the editor
  entryMedia: [],         // media rows for the open entry
  isNew: false,
  keyDraft: null,
  aspectDraft: null,
  activeAspect: null,
  filters: { aspects: new Set(), kinds: new Set() },
  search: '',
  searchFilter: 'all',
  prompt: '',
  timelineLimit: 30,
  recorder: null,
  dirty: false
};

const $  = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const mediaById = id => S.media.find(m => m.id === id);
const aspectName = id => (S.aspects.find(a => a.id === id) || {}).name || id;

/* URL cache for Blobs. Every object URL is tracked so it can be revoked —
   a timeline that leaks hundreds of decoded audio blobs is a memory leak
   you only notice on a phone, three months in. */
const UrlCache = (() => {
  const cache = new Map();
  return {
    get(id) {
      const m = mediaById(id);
      if (!m || !m.blob) return null;
      if (!cache.has(id)) cache.set(id, URL.createObjectURL(m.blob));
      return cache.get(id);
    },
    release(id) {
      if (cache.has(id)) { URL.revokeObjectURL(cache.get(id)); cache.delete(id); }
    }
  };
})();

function fail(err) {
  const banner = $('#errorBanner');
  banner.textContent = `Notes hit an error — this is a bug, not something you did:\n\n${err && err.stack ? err.stack : err}`;
  banner.classList.remove('hidden');
}
window.onerror = (msg, src, line, col, err) => fail(err || `${msg} (${src}:${line}:${col})`);
window.addEventListener('unhandledrejection', e => fail(e.reason));

/* ── tap-twice confirmation ───────────────────────────────────────
   Never window.confirm(): a sandboxed iframe blocks the native modal and
   returns false without asking, so anything guarded by it never runs. */
let armed = null;
function confirmAction(btn, message, action) {
  if (armed === btn) {
    clearTimeout(btn._t);
    armed = null;
    btn.classList.remove('danger-armed');
    toast('');
    action();
    return;
  }
  if (armed) { clearTimeout(armed._t); armed.classList.remove('danger-armed'); }
  armed = btn;
  btn.classList.add('danger-armed');
  toast(message, 'armed');
  btn._t = setTimeout(() => { armed = null; btn.classList.remove('danger-armed'); toast(''); }, 4000);
}
let toastTimer = null;
function toast(msg, kind = '') {
  const t = $('#toast');
  if (!msg) { t.classList.add('hidden'); return; }
  t.textContent = msg;
  t.className = `toast ${kind}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add('hidden'), 3200);
}

/* ── boot ───────────────────────────────────────────────────────── */
async function boot() {
  const first = !localStorage.getItem('rojni.seen');
  const all = await Store.readAll();
  S.entries = all.entries;
  S.media = all.media;
  S.keypoints = all.keypoints;
  S.aspects = all.aspects;
  S.meta = all.meta || {};

  if (!S.aspects.length) {
    S.aspects = DEFAULT_ASPECTS.map((a, i) => Object.assign({ order: i, bigRock: i < 2, focus: [], archived: false }, a));
    await Store.putMany(Store.T.ASPECTS, S.aspects);
  }
  S.prompt = PROMPTS[Math.floor(Math.random() * PROMPTS.length)];

  await applyTheme();
  if (S.meta.pin) { showGate(); } else { startApp(); }
  if (first) localStorage.setItem('rojni.seen', '1');
}

function startApp() {
  $('#gate').classList.add('hidden');
  $('#app').classList.remove('hidden');
  renderAll();
}

async function applyTheme() {
  const theme = S.meta.theme || {};
  if (theme.accent) document.documentElement.style.setProperty('--indigo', theme.accent);
}

/* ── navigation ─────────────────────────────────────────────────── */
function nav(view) {
  S.view = view;
  ['today', 'timeline', 'aspects', 'search'].forEach(v => {
    $(`#view${v[0].toUpperCase()}${v.slice(1)}`).classList.toggle('hidden', v !== view);
  });
  $$('.tab').forEach(t => t.classList.toggle('active', t.dataset.view === view));
  window.scrollTo({ top: 0 });
  if (view === 'timeline') renderTimeline();
  if (view === 'aspects') renderAspects();
  if (view === 'search') { renderSearch(); setTimeout(() => $('#searchInput').focus(), 60); }
  if (view === 'today') renderToday();
}

function renderAll() {
  renderToday();
  renderTimeline();
  renderAspects();
  renderSearch();
  renderSettings();
}

/* ══════════════════════════════════════════════════════════════════
   TODAY
   ══════════════════════════════════════════════════════════════════ */
function renderToday() {
  const key = todayKey();
  $('#todayDate').innerHTML =
    `<h1>${fmtLong(key)}</h1><div class="sub">${S.entries.filter(e => e.date === key).length} entr${S.entries.filter(e => e.date === key).length === 1 ? 'y' : 'ies'} today · ${S.entries.length} in all</div>`;

  /* Quiet consistency grid — dots, not a streak. A journal is a place to be
     honest, and you cannot be honest somewhere that is disappointed in you. */
  const days = S.meta.sessionDays || [];
  const grid = [];
  for (let i = 59; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i);
    const k = dateKey(d);
    const due = S.entries.filter(e => e.date === k);
    const hasAudio = due.some(e => (e.blocks || []).some(b => b.t === 'audio'));
    const hasPhoto = due.some(e => (e.blocks || []).some(b => b.t === 'photo'));
    const cls = [due.length ? 'written' : '', hasAudio ? 'audio' : '', hasPhoto ? 'photo' : '', k === key ? 'today' : ''].filter(Boolean).join(' ');
    grid.push(`<i class="${cls}" title="${fmtShort(k)}"></i>`);
  }
  $('#todayGrid').innerHTML = grid.join('');

  /* On this day — the retention engine of every journal that ever lasted. */
  const otd = onThisDay();
  $('#onThisDay').innerHTML = otd ? `
    <div class="otd" data-open="${otd.entry.id}">
      <span class="eyebrow">${otd.label}</span>
      <p>${escapeHTML(entryTitle(otd.entry))}</p>
      ${otd.thumb ? `<img class="otd-img" src="${otd.thumb}" alt="">` : ''}
    </div>` : '';

  /* Today's entries */
  const todays = S.entries.filter(e => e.date === key).sort((a, b) => b.createdAt - a.createdAt);
  $('#todayEntries').innerHTML = todays.length
    ? todays.map(entryCard).join('')
    : `<div class="empty">Nothing written today yet.<br>Tap <b>+</b> and write one honest line.</div>`;

  $('#promptText').textContent = S.prompt;

  /* Big rocks: the honest comparison between what you say matters and where
     your words actually went. */
  const rocks = S.aspects.filter(a => a.bigRock && !a.archived);
  if (rocks.length) {
    const lines = rocks.map(a => {
      const last = lastTouched(a.id);
      const d = last ? daysAgo(last) : null;
      if (d === null) return `<b>${escapeHTML(a.name)}</b> has nothing yet`;
      if (d > 7) return `<b>${escapeHTML(a.name)}</b> — <span class="stale">${relDate(last)}</span>`;
      return null;
    }).filter(Boolean);
    $('#bigRockNote').innerHTML = lines.length
      ? `<div class="panel" style="margin-top:22px"><div class="panel-head"><b>Big rocks</b><span class="muted small">what you said matters</span></div><p class="small" style="margin:0">${lines.join(' · ')}</p></div>`
      : '';
  } else $('#bigRockNote').innerHTML = '';
}

function onThisDay() {
  const today = new Date();
  for (const back of [30, 90, 182, 365, 730]) {
    const d = new Date(today); d.setDate(d.getDate() - back);
    const k = dateKey(d);
    const hit = S.entries.filter(e => e.date === k).sort((a, b) => a.createdAt - b.createdAt)[0];
    if (hit) {
      const photoBlock = (hit.blocks || []).find(b => b.t === 'photo');
      return {
        entry: hit,
        label: back === 30 ? 'A month ago' : back === 90 ? 'Three months ago' : back === 182 ? 'Six months ago' : back === 365 ? 'A year ago today' : 'Two years ago today',
        thumb: photoBlock ? UrlCache.get(photoBlock.media) : null
      };
    }
  }
  return null;
}

function entryCard(e) {
  const photos = (e.blocks || []).filter(b => b.t === 'photo').slice(0, 4);
  const audio = (e.blocks || []).filter(b => b.t === 'audio');
  const quote = (e.blocks || []).find(b => b.t === 'quote');
  const text = blocksText(e);
  const preview = text.split('\n').slice(1).join(' ').slice(0, 220);
  const isReview = e.kind === 'review';
  return `
  <article class="entry-card ${isReview ? 'review' : ''}" data-open="${e.id}">
    ${isReview ? '<span class="eyebrow tiny" style="color:var(--amber)">Weekly review</span>' : ''}
    <h3 class="entry-title">${escapeHTML(entryTitle(e))}</h3>
    ${preview ? `<p class="entry-preview">${escapeHTML(preview)}</p>` : ''}
    ${quote ? `<div class="entry-quote">${escapeHTML(quote.text.slice(0, 180))}</div>` : ''}
    ${photos.length ? `<div class="entry-thumbs">${photos.map(p => UrlCache.get(p.media) ? `<img src="${UrlCache.get(p.media)}" alt="">` : '').join('')}</div>` : ''}
    <div class="entry-foot">
      <span>${fmtMedium(e.date)}</span>
      ${audio.length ? `<span class="tag pill-audio">◍ ${audio.map(a => fmtClock((mediaById(a.media) || {}).duration)).join(', ')}</span>` : ''}
      ${photos.length ? `<span class="tag">▣ ${photos.length}</span>` : ''}
      ${e.mood ? `<span class="tag">mood ${e.mood}/5</span>` : ''}
      ${(e.aspects || []).map(a => {
        const asp = S.aspects.find(x => x.id === a);
        return asp ? `<span class="tag" style="border-color:${asp.color}44;color:${asp.color}">${asp.glyph} ${escapeHTML(asp.name)}</span>` : '';
      }).join('')}
    </div>
  </article>`;
}

/* ══════════════════════════════════════════════════════════════════
   TIMELINE
   ══════════════════════════════════════════════════════════════════ */
function filteredEntries() {
  let list = [...S.entries].sort((a, b) => (b.date.localeCompare(a.date)) || (b.createdAt - a.createdAt));
  const { aspects, kinds } = S.filters;
  if (aspects.size) list = list.filter(e => (e.aspects || []).some(a => aspects.has(a)));
  if (kinds.size) {
    list = list.filter(e => {
      const b = e.blocks || [];
      if (kinds.has('audio')    && b.some(x => x.t === 'audio'))    return true;
      if (kinds.has('photo')    && b.some(x => x.t === 'photo'))    return true;
      if (kinds.has('quote')    && b.some(x => x.t === 'quote'))    return true;
      if (kinds.has('review')   && e.kind === 'review')             return true;
      if (kinds.has('text')     && b.some(x => x.t === 'text'))     return true;
      return false;
    });
  }
  return list;
}

function renderTimeline() {
  const chips = [
    ...S.aspects.filter(a => !a.archived).map(a => ({ id: 'k:' + a.id, label: `${a.glyph} ${a.name}`, on: S.filters.aspects.has(a.id) })),
    { id: 'm:audio', label: '◍ Voice', on: S.filters.kinds.has('audio') },
    { id: 'm:photo', label: '▣ Photos', on: S.filters.kinds.has('photo') },
    { id: 'm:quote', label: '❝ Key points', on: S.filters.kinds.has('quote') },
    { id: 'm:review', label: '≋ Reviews', on: S.filters.kinds.has('review') }
  ];
  $('#timelineFilters').innerHTML = chips.map(c =>
    `<button class="chip ${c.on ? 'on' : ''}" data-chip="${c.id}">${escapeHTML(c.label)}</button>`).join('');

  const list = filteredEntries();
  const slice = list.slice(0, S.timelineLimit);
  $('#timelineCount').textContent = `${list.length} entr${list.length === 1 ? 'y' : 'ies'}`;
  $('#timeline').innerHTML = slice.length ? groupByDay(slice) : `<div class="empty">Nothing here yet.</div>`;
  $('#randomPage').classList.toggle('hidden', list.length < 8);
  $('#loadMore').classList.toggle('hidden', list.length <= S.timelineLimit);
}

function groupByDay(list) {
  let out = '';
  let current = null;
  for (const e of list) {
    if (e.date !== current) {
      if (current) out += '</div>';
      current = e.date;
      out += `<div class="day-group"><div class="day-group-label"><b>${fmtMedium(e.date)}</b><span>${relDate(e.date)}</span></div>`;
    }
    out += entryCard(e);
  }
  return out + '</div>';
}

/* ══════════════════════════════════════════════════════════════════
   ASPECTS — the lens over your own writing
   ══════════════════════════════════════════════════════════════════ */
function lastTouched(aspectId) {
  const dates = [];
  S.entries.forEach(e => { if ((e.aspects || []).includes(aspectId)) dates.push(e.date); });
  S.keypoints.forEach(k => { if ((k.aspects || []).includes(aspectId)) dates.push(k.date); });
  return dates.sort().pop() || null;
}

function aspectWords(aspectId, monthsBack = 12) {
  const buckets = new Array(monthsBack).fill(0);
  const now = new Date();
  S.entries.forEach(e => {
    if (!(e.aspects || []).includes(aspectId)) return;
    const d = parseKey(e.date);
    const diff = (now.getFullYear() - d.getFullYear()) * 12 + (now.getMonth() - d.getMonth());
    if (diff >= 0 && diff < monthsBack) buckets[monthsBack - 1 - diff] += wordCount(e);
  });
  return buckets;
}

function aspectMood(aspectId) {
  const moods = S.entries.filter(e => (e.aspects || []).includes(aspectId) && e.mood).map(e => Number(e.mood));
  if (!moods.length) return null;
  return (moods.reduce((a, b) => a + b, 0) / moods.length).toFixed(1);
}

function renderAspects() {
  const live = S.aspects.filter(a => !a.archived).sort((a, b) => a.order - b.order);
  $('#aspectGrid').innerHTML = live.map(a => {
    const last = lastTouched(a.id);
    const d = last ? daysAgo(last) : null;
    const kpCount = S.keypoints.filter(k => (k.aspects || []).includes(a.id)).length;
    const openCount = S.keypoints.filter(k => (k.aspects || []).includes(a.id) && k.status === 'open').length;
    const buckets = aspectWords(a.id);
    const max = Math.max(1, ...buckets);
    const bars = buckets.map(v => `<i class="${v ? 'has' : ''}" style="height:${Math.max(2, Math.round(v / max * 18))}px"></i>`).join('');
    return `
    <article class="aspect-card ${a.bigRock ? 'big-rock' : ''}" data-aspect="${a.id}">
      <span class="accent" style="background:${a.color}"></span>
      ${a.bigRock ? '<span class="rock-badge">Big rock</span>' : ''}
      <span class="glyph" style="color:${a.color}">${a.glyph}</span>
      <span class="name">${escapeHTML(a.name)}</span>
      <div class="attention">${bars}</div>
      <span class="meta">${d === null ? 'nothing yet' : d === 0 ? 'touched today' : `<span class="${d > 7 ? 'stale' : ''}">${relDate(last)}</span>`} · ${kpCount} key point${kpCount === 1 ? '' : 's'}${openCount ? ` · ${openCount} open` : ''}</span>
    </article>`;
  }).join('');

  renderAspectDetail();
}

function renderAspectDetail() {
  const host = $('#aspectDetail');
  if (!S.activeAspect) { host.innerHTML = ''; return; }
  const a = S.aspects.find(x => x.id === S.activeAspect);
  if (!a) { S.activeAspect = null; host.innerHTML = ''; return; }

  const kps = S.keypoints.filter(k => (k.aspects || []).includes(a.id))
    .sort((x, y) => (y.pinned - x.pinned) || y.date.localeCompare(x.date));
  const entries = S.entries.filter(e => (e.aspects || []).includes(a.id)).length;
  const words = S.entries.filter(e => (e.aspects || []).includes(a.id)).reduce((n, e) => n + wordCount(e), 0);
  const mood = aspectMood(a.id);
  const last = lastTouched(a.id);

  host.innerHTML = `
    <div class="aspect-detail">
      <div class="row spread">
        <h3 style="color:${a.color}">${a.glyph} ${escapeHTML(a.name)}</h3>
        <button class="text-btn" id="editAspect" data-id="${a.id}">Edit</button>
      </div>
      <p class="muted small" style="margin:0">${last ? `Last touched ${relDate(last)}.` : 'Nothing written about this yet.'}</p>

      <div class="stat-row">
        <div class="stat"><b>${entries}</b><span>entries</span></div>
        <div class="stat"><b>${words}</b><span>words</span></div>
        <div class="stat"><b>${kps.length}</b><span>key points</span></div>
        <div class="stat"><b>${mood || '–'}</b><span>avg mood${mood ? '/5' : ''}</span></div>
      </div>

      <div class="row gap" style="margin-bottom:16px">
        <button class="primary" id="writeAspect" data-id="${a.id}">Write about this</button>
        <button class="ghost" id="keyAspect" data-id="${a.id}">+ Key point</button>
      </div>

      <span class="eyebrow">Focus</span>
      <div id="focusList">${(a.focus || []).length ? a.focus.map((f, i) => `
        <label class="focus-item ${f.done ? 'done' : ''}">
          <input type="checkbox" data-focus="${i}" ${f.done ? 'checked' : ''} />
          <span>${escapeHTML(f.text)}</span>
          <button class="icon-btn-sm danger" data-unfocus="${i}" style="margin-left:auto">×</button>
        </label>`).join('')
        : '<p class="muted small">Nothing yet. What are you actually working on here?</p>'}
      </div>
      <div class="row gap" style="margin-top:8px">
        <input class="mini-input" id="focusInput" placeholder="walk daily…" style="flex:1;width:auto" />
        <button class="ghost" id="focusAdd">Add</button>
      </div>

      <div style="margin-top:20px"><span class="eyebrow">Key points</span></div>
      <div>${kps.length ? kps.map(k => `
        <div class="kp-item ${k.pinned ? 'pinned' : ''} ${k.status !== 'open' ? 'done' : ''}">
          <div class="kp-text">
            ${k.pinned ? '★ ' : ''}${escapeHTML(k.text)}
            <div class="kp-src">${fmtShort(k.date)} · ${k.status}${k.sourceEntryId ? ' · from an entry' : ''}</div>
          </div>
          <button class="icon-btn-sm" data-keydone="${k.id}" title="Cycle status">${k.status === 'open' ? '○' : k.status === 'done' ? '●' : '◌'}</button>
          <button class="icon-btn-sm danger" data-keydel="${k.id}">×</button>
        </div>`).join('')
        : '<p class="muted small">No key points yet. The fastest way to make one: open an entry and highlight the sentence that matters.</p>'}
      </div>
    </div>`;
}

/* ══════════════════════════════════════════════════════════════════
   SEARCH
   ══════════════════════════════════════════════════════════════════ */
let searchTimer = null;
function renderSearch() {
  const filters = [
    { id: 'all', label: 'Everything' }, { id: 'entries', label: 'Entries' },
    { id: 'keys', label: 'Key points' }, { id: 'audio', label: 'Voice' },
    { id: 'photo', label: 'Photos' }, { id: 'review', label: 'Reviews' }
  ];
  $('#searchFilters').innerHTML = filters.map(f =>
    `<button class="chip ${S.searchFilter === f.id ? 'on' : ''}" data-sfilter="${f.id}">${f.label}</button>`).join('');

  const q = S.search.trim().toLowerCase();
  if (!q) {
    $('#searchResults').innerHTML = `<div class="empty">Search your own writing.<br><span class="small">Words, aspect names, a date like <code>august</code> or <code>2026-08</code>.</span></div>`;
    return;
  }

  const out = [];
  const wantEntries = ['all', 'entries', 'audio', 'photo', 'review'].includes(S.searchFilter);
  if (wantEntries) {
    let list = S.entries.filter(e => {
      const hay = `${fullText(e)} ${e.date} ${fmtLong(e.date)} ${(e.aspects || []).map(aspectName).join(' ')}`.toLowerCase();
      if (!hay.includes(q)) return false;
      const b = e.blocks || [];
      if (S.searchFilter === 'audio'  && !b.some(x => x.t === 'audio')) return false;
      if (S.searchFilter === 'photo'  && !b.some(x => x.t === 'photo')) return false;
      if (S.searchFilter === 'review' && e.kind !== 'review')           return false;
      return true;
    }).sort((a, b) => b.date.localeCompare(a.date));
    out.push(...list.map(entryCard));
  }
  if (['all', 'keys'].includes(S.searchFilter)) {
    const kps = S.keypoints.filter(k => `${k.text} ${(k.aspects || []).map(aspectName).join(' ')} ${k.date}`.toLowerCase().includes(q));
    if (kps.length) {
      out.push(`<span class="eyebrow" style="margin-top:10px">Key points</span>`);
      out.push(...kps.map(k => `<article class="entry-card"><div class="entry-title">${escapeHTML(k.text)}</div>
        <div class="entry-foot"><span>${fmtShort(k.date)}</span>${(k.aspects || []).map(a => `<span class="tag">${escapeHTML(aspectName(a))}</span>`).join('')}</div></article>`));
    }
  }
  $('#searchResults').innerHTML = out.length ? out.join('') : `<div class="empty">Nothing matches “${escapeHTML(S.search)}”.</div>`;
}

/* ══════════════════════════════════════════════════════════════════
   ENTRY EDITOR
   ══════════════════════════════════════════════════════════════════ */
function blankEntry(date) {
  return {
    id: uid('e'), date: date || todayKey(), createdAt: Date.now(), updatedAt: Date.now(),
    kind: 'day', title: '', blocks: [{ t: 'text', text: '' }],
    mood: '', energy: '', aspects: [], place: ''
  };
}

async function openEntry(id) {
  const found = S.entries.find(e => e.id === id);
  S.isNew = !found;
  S.entry = found ? JSON.parse(JSON.stringify(found)) : blankEntry();
  S.entryMedia = found ? await Store.mediaFor(id) : [];
  drawEditor();
  $('#sheetEntry').classList.remove('hidden');
  setTimeout(() => {
    const last = $$('#blocksHost textarea').pop();
    if (S.isNew && last) last.focus();
  }, 120);
}

function openNewEntry(date) {
  S.isNew = true;
  S.entry = blankEntry(date);
  S.entryMedia = [];
  drawEditor();
  $('#sheetEntry').classList.remove('hidden');
  setTimeout(() => {
    const box = $('#blocksHost textarea');
    if (box) box.focus();
  }, 120);
}

function drawEditor() {
  const e = S.entry;
  $('#entryDate').value = e.date;
  $('#entryMood').value = e.mood || '';
  $('#entryEnergy').value = e.energy || '';
  $('#entryMeta').textContent = S.isNew ? 'new entry' : `edited ${relTime(e.updatedAt)}`;
  $('#entryDelete').textContent = S.isNew ? 'Discard' : 'Delete';
  const toggleAspect = id => {
    e.aspects = (e.aspects || []).includes(id) ? e.aspects.filter(x => x !== id) : [...(e.aspects || []), id];
    paintEntryAspects();
    patch();
  };
  const paintEntryAspects = () => drawAspectChips($('#entryAspects'), e.aspects || [], toggleAspect);
  paintEntryAspects();
  drawBlocks();
}

function relTime(ts) {
  const mins = Math.round((Date.now() - ts) / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
}

function drawAspectChips(host, selected, onToggle) {
  host.innerHTML = S.aspects.filter(a => !a.archived).map(a => {
    const on = selected.includes(a.id);
    return `<button class="chip ${on ? 'on aspect-on' : ''}" style="${on ? `background:${a.color}` : ''}" data-aid="${a.id}">${a.glyph} ${escapeHTML(a.name)}</button>`;
  }).join('');
  host.onclick = ev => {
    const b = ev.target.closest('[data-aid]');
    if (b) onToggle(b.dataset.aid);
  };
}

function drawBlocks() {
  const host = $('#blocksHost');
  host.innerHTML = `<div class="blocks">${S.entry.blocks.map((b, i) => blockHTML(b, i)).join('')}</div>`;
  $$('#blocksHost textarea').forEach(t => { autoGrow(t); bindTextarea(t); });
  $$('#blocksHost [data-mediaclick]').forEach(el => {
    el.onclick = () => openViewer(el.dataset.mediaclick);
  });
  $$('#blocksHost [data-delblock]').forEach(el => {
    el.onclick = () => removeBlock(Number(el.dataset.delblock));
  });
  bindAudioPlayers();
}

function blockHTML(b, i) {
  if (b.t === 'text') {
    return `<div class="block"><textarea class="block-text" data-bi="${i}" rows="1" placeholder="${i === 0 ? 'What happened today…' : 'Keep going…'}">${escapeHTML(b.text)}</textarea></div>`;
  }
  if (b.t === 'quote') {
    return `<div class="block"><div class="block-quote">${escapeHTML(b.text)}
      <span class="kp-label">${b.keyPointId ? '★ key point' : 'quote'}</span>
      <button class="icon-btn-sm danger" data-delblock="${i}" style="float:right;margin-top:-4px">×</button></div></div>`;
  }
  const m = mediaById(b.media) || S.entryMedia.find(x => x.id === b.media);
  if (!m) return `<div class="block"><div class="block-media"><div class="media-main"><div class="media-name">Missing media</div><div class="media-sub">This file is not in storage.</div></div><button class="icon-btn-sm danger" data-delblock="${i}">×</button></div></div>`;

  if (b.t === 'photo') {
    const src = UrlCache.get(m.id);
    return `<div class="block"><div class="block-media">
      ${src ? `<img src="${src}" alt="" data-mediaclick="${m.id}" />` : '<div class="media-name">Photo</div>'}
      <div class="media-main">
        <div class="media-name">Photo</div>
        <div class="media-sub">${m.width ? `${m.width}×${m.height} · ` : ''}${fmtSize(m.blob ? m.blob.size : 0)}${m.origDate ? ' · captured ' + fmtShort(m.origDate) : ''}</div>
      </div>
      <button class="icon-btn-sm" data-mediaclick="${m.id}">↗</button>
      <button class="icon-btn-sm danger" data-delblock="${i}">×</button>
    </div></div>`;
  }

  const peaks = m.peaks || new Array(48).fill(60);
  return `<div class="block"><div class="block-media" style="align-items:stretch;flex-direction:column">
    <div class="row spread" style="width:100%">
      <span class="media-name">◍ Voice note · ${fmtClock(m.duration)}</span>
      <span class="row" style="gap:2px">
        <button class="icon-btn-sm" data-mediaclick="${m.id}">↗</button>
        <button class="icon-btn-sm danger" data-delblock="${i}">×</button>
      </span>
    </div>
    <div class="wave" data-wave="${m.id}">${peaks.slice(0, 48).map(p => `<i style="height:${Math.max(2, Math.round(p / 255 * 22))}px"></i>`).join('')}</div>
    <audio class="media-player" controls preload="metadata" data-audio="${m.id}" src="${UrlCache.get(m.id) || ''}"></audio>
  </div></div>`;
}

function autoGrow(el) {
  el.style.height = 'auto';
  el.style.height = (el.scrollHeight + 2) + 'px';
}

function bindTextarea(el) {
  const i = Number(el.dataset.bi);
  el.addEventListener('input', () => {
    S.entry.blocks[i].text = el.value;
    autoGrow(el);
    patch();
  });
  el.addEventListener('keydown', ev => {
    if (ev.key === 'Enter' && !ev.shiftKey) {
      const atEnd = el.selectionStart === el.value.length && el.selectionEnd === el.value.length;
      if (atEnd) {
        ev.preventDefault();
        S.entry.blocks[i].text = el.value;
        S.entry.blocks.splice(i + 1, 0, { t: 'text', text: '' });
        drawBlocks();
        const next = $(`#blocksHost textarea[data-bi="${i + 1}"]`);
        if (next) next.focus();
        patch(true);
      }
    }
  });
  /* Highlight → key point. Selection inside a textarea is invisible to the
     DOM, so the bar is positioned from the block rather than a Range. */
  const showBar = () => {
    const sel = el.value.slice(el.selectionStart, el.selectionEnd).trim();
    if (sel.length < 3) { hideHighlightBar(); return; }
    const r = el.getBoundingClientRect();
    showHighlightBar(sel, r);
  };
  el.addEventListener('mouseup', showBar);
  el.addEventListener('keyup', ev => { if (ev.shiftKey) showBar(); });
  el.addEventListener('blur', () => setTimeout(hideHighlightBar, 220));
}

function bindAudioPlayers() {
  $$('#blocksHost audio[data-audio]').forEach(a => {
    const id = a.dataset.audio;
    const wave = $(`[data-wave="${id}"]`);
    const bars = wave ? [...wave.children] : [];
    const posKey = 'rojni.pos.' + id;
    a.addEventListener('loadedmetadata', () => {
      const saved = Number(localStorage.getItem(posKey) || 0);
      /* MediaRecorder blobs frequently report duration: Infinity, so trust the
         duration we timed ourselves and only use the element's if it's sane. */
      if (saved > 1 && isFinite(a.duration) && saved < a.duration - 2) a.currentTime = saved;
    });
    a.addEventListener('timeupdate', () => {
      if (isFinite(a.duration) && a.duration > 0) {
        const pct = a.currentTime / a.duration;
        bars.forEach((bar, i) => bar.classList.toggle('on', i / bars.length <= pct));
      }
      if (Math.round(a.currentTime) % 3 === 0) {
        try { localStorage.setItem(posKey, String(Math.floor(a.currentTime))); } catch (e) {}
      }
    });
  });
}

/* ── the highlight bar ──────────────────────────────────────────── */
let pendingSelection = null;
function showHighlightBar(text, rect) {
  pendingSelection = text;
  const bar = $('#highlightBar');
  /* keep focus in the textarea — otherwise the selection is gone by the time
     the button's click event fires */
  bar.onmousedown = ev => ev.preventDefault();
  bar.classList.remove('hidden');
  const top = rect.top - 56;
  bar.style.bottom = 'auto';
  bar.style.top = `${Math.max(10, top)}px`;
}
function hideHighlightBar() {
  $('#highlightBar').classList.add('hidden');
  pendingSelection = null;
}

async function promoteSelection(asQuote) {
  const text = pendingSelection;
  const active = document.activeElement;
  if (!text || !active || !active.dataset || active.dataset.bi === undefined) return;
  const i = Number(active.dataset.bi);
  const box = active;
  const start = box.selectionStart, end = box.selectionEnd;
  const before = box.value.slice(0, start);
  const after = box.value.slice(end);

  const quote = { t: 'quote', text: text.trim() };
  const replacement = [];
  if (before.trim()) replacement.push({ t: 'text', text: before.replace(/\n+$/, '') });
  let kpId = null;
  if (!asQuote) {
    const kp = {
      id: uid('k'), text: text.trim(), aspects: [...(S.entry.aspects || [])],
      date: S.entry.date, sourceEntryId: S.entry.id, pinned: false, status: 'open'
    };
    S.keypoints.push(kp);
    kpId = kp.id;
    quote.keyPointId = kpId;
    await Store.put(Store.T.KEYS, kp);   // persist now — a key point that exists
                                         // only in memory disappears on reload
  }
  replacement.push(quote);
  if (after.trim()) replacement.push({ t: 'text', text: after.replace(/^\n+/, '') });

  S.entry.blocks.splice(i, 1, ...replacement);
  hideHighlightBar();
  drawBlocks();
  await saveEntry();
  toast(asQuote ? 'Kept as a quote.' : `Key point saved${S.entry.aspects.length ? '' : ' — tap an aspect to file it'}.`);
}

/* ── media: photos ──────────────────────────────────────────────── */
async function addPhotos(files) {
  if (!files || !files.length) return;
  toast('Adding photos…');
  for (const file of files) {
    try {
      const origDate = await Store.exifDate(file);
      const { blob, width, height } = await Store.compressImage(file);
      const thumb = await Store.thumbnail(blob);
      const rec = {
        id: uid('m'), entryId: S.entry.id, type: 'image', blob, thumb: thumb || null,
        width, height, mime: 'image/jpeg', origDate: origDate || null, createdAt: Date.now()
      };
      S.entryMedia.push(rec);
      S.media.push(rec);
      S.entry.blocks.push({ t: 'photo', media: rec.id });
    } catch (err) {
      fail(err);
    }
  }
  if (S.entry.blocks.length === 1 && S.entry.blocks[0].t === 'text' && !S.entry.blocks[0].text) S.entry.blocks.shift();
  drawBlocks();
  await saveEntry();
  toast('');
}

/* ── media: audio ───────────────────────────────────────────────── */
function openRecorder() {
  $('#recError').textContent = '';
  $('#recTime').textContent = '0:00';
  $('#recToggle').textContent = 'Record';
  $('#sheetRecord').classList.remove('hidden');
}

async function startRecording() {
  const errBox = $('#recError');
  errBox.textContent = '';
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
    errBox.textContent = 'This browser cannot record audio. In the Android app this means MainActivity is missing WebChromeClient.onPermissionRequest — the failure is silent by design, which is why this message exists.';
    return;
  }
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true }
    });
  } catch (err) {
    errBox.textContent = err && err.name === 'NotAllowedError'
      ? 'Microphone permission was refused. Nothing was recorded.'
      : `Could not start the microphone (${err && err.name}).`;
    return;
  }

  const mime = Store.pickAudioMime();
  const rec = new MediaRecorder(stream, mime ? { mimeType: mime, audioBitsPerSecond: 32000 } : { audioBitsPerSecond: 32000 });
  const chunks = [];
  const startedAt = Date.now();
  rec.ondataavailable = ev => { if (ev.data && ev.data.size) chunks.push(ev.data); };

  /* Live level meter */
  const canvas = $('#recCanvas');
  const ctx = canvas.getContext('2d');
  const Ctx = window.AudioContext || window.webkitAudioContext;
  let analyser = null, audioCtx = null, drawId = null;
  try {
    audioCtx = new Ctx();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 512;
    source.connect(analyser);
    const data = new Uint8Array(analyser.frequencyBinCount);
    const draw = () => {
      analyser.getByteFrequencyData(data);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const bars = 48, step = Math.floor(data.length / bars);
      for (let i = 0; i < bars; i++) {
        const v = data[i * step] / 255;
        const h = Math.max(3, v * canvas.height);
        ctx.fillStyle = '#47578f';
        ctx.fillRect(i * (canvas.width / bars), (canvas.height - h) / 2, canvas.width / bars - 3, h);
      }
      drawId = requestAnimationFrame(draw);
    };
    draw();
  } catch (err) { /* a meter is a luxury; recording is not */ }

  const tick = setInterval(() => {
    $('#recTime').innerHTML = `<span class="rec-dot"></span>${fmtClock((Date.now() - startedAt) / 1000)}`;
  }, 200);

  S.recorder = {
    rec, stream, chunks, startedAt,
    stopMaster() {
      clearInterval(tick);
      if (drawId) cancelAnimationFrame(drawId);
      if (audioCtx) { try { audioCtx.close(); } catch (e) {} }
      stream.getTracks().forEach(t => t.stop());
    }
  };

  rec.onstop = async () => {
    const duration = (Date.now() - startedAt) / 1000;
    const blob = new Blob(chunks, { type: rec.mimeType || 'audio/webm' });
    S.recorder.stopMaster();
    S.recorder = null;
    $('#sheetRecord').classList.add('hidden');

    if (duration < 0.6 || !blob.size) { toast('Nothing recorded.'); return; }
    toast('Saving voice note…');
    const peaks = await Store.waveform(blob);
    const rec2 = {
      id: uid('m'), entryId: S.entry.id, type: 'audio', blob,
      mime: blob.type, duration, peaks: peaks || null, createdAt: Date.now()
    };
    S.entryMedia.push(rec2);
    S.media.push(rec2);
    S.entry.blocks.push({ t: 'audio', media: rec2.id });
    if (S.entry.blocks.length === 1 && S.entry.blocks[0].t === 'text' && !S.entry.blocks[0].text) S.entry.blocks.shift();
    drawBlocks();
    await saveEntry();
    toast('');
  };

  rec.start(1000);
  $('#recToggle').textContent = 'Stop & keep';
}

function stopRecording() {
  if (!S.recorder) return;
  $('#recToggle').textContent = 'Record';
  S.recorder.rec.stop();
}

/* ── saving ─────────────────────────────────────────────────────── */
let patchTimer = null;
function patch(structural = false) {
  S.dirty = true;
  setSaveState('saving…', '');
  clearTimeout(patchTimer);
  patchTimer = setTimeout(() => saveEntry(), structural ? 80 : 500);
}

function setSaveState(text, cls) {
  const el = $('#saveState');
  el.textContent = text;
  el.className = 'save-state muted small ' + (cls || '');
}

async function saveEntry() {
  if (!S.entry) return;
  const e = S.entry;
  if (e.kind !== 'review' && isEntryEmpty(e)) { setSaveState(''); return; }   // never persist blank pages
  e.updatedAt = Date.now();
  if (!S.entries.find(x => x.id === e.id)) S.entries.push(e);
  else S.entries = S.entries.map(x => x.id === e.id ? e : x);

  try {
    await Store.put(Store.T.ENTRIES, e);
    if (S.entryMedia.length) await Store.putMany(Store.T.MEDIA, S.entryMedia);
    S.isNew = false;
    S.dirty = false;
    setSaveState('saved', 'saved');
    /* Ask for persistent storage on the first real entry — not when it's full.
       Without it the browser may evict this origin, silently. */
    if (!S.meta.askedPersist) {
      S.meta.askedPersist = true;
      S.meta.persist = await Store.requestPersist();
      await Store.put(Store.T.META, { key: 'persist', value: S.meta.persist });
      renderSettings();
    }
    trackSession();
  } catch (err) {
    setSaveState('not saved', '');
    fail(err);
  }
}

function trackSession() {
  const k = todayKey();
  const days = S.meta.sessionDays || [];
  if (!days.includes(k)) {
    days.push(k);
    S.meta.sessionDays = days.slice(-400);
    Store.put(Store.T.META, { key: 'sessionDays', value: S.meta.sessionDays });
  }
}

function isEntryEmpty(e) {
  const hasText = (e.blocks || []).some(b => b.text && b.text.trim());
  const hasMedia = (e.blocks || []).some(b => b.t === 'photo' || b.t === 'audio');
  return !hasText && !hasMedia && !e.title;
}

function closeEntry() {
  clearTimeout(patchTimer);
  if (S.isNew && isEntryEmpty(S.entry)) {
    /* a blank page the user backed out of — throw it away, don't litter */
    S.entryMedia.forEach(m => { S.media = S.media.filter(x => x.id !== m.id); UrlCache.release(m.id); });
    S.entry.blocks.filter(b => b.t === 'quote' && b.keyPointId).forEach(b => {
      S.keypoints = S.keypoints.filter(k => k.id !== b.keyPointId);
      Store.remove(Store.T.KEYS, b.keyPointId);   // don't leave it orphaned on disk
    });
  }
  S.entry = null;
  S.entryMedia = [];
  $('#sheetEntry').classList.add('hidden');
  hideHighlightBar();
  renderAll();
}

async function deleteBlock(i) {
  const b = S.entry.blocks[i];
  if (b && (b.t === 'photo' || b.t === 'audio')) {
    const m = S.entryMedia.find(x => x.id === b.media);
    if (m) {
      UrlCache.release(m.id);
      S.entryMedia = S.entryMedia.filter(x => x.id !== m.id);
      S.media = S.media.filter(x => x.id !== m.id);
      await Store.remove(Store.T.MEDIA, m.id);
    }
  }
  S.entry.blocks.splice(i, 1);
  if (!S.entry.blocks.length) S.entry.blocks.push({ t: 'text', text: '' });
  drawBlocks();
  patch(true);
}

/* ── media viewer ───────────────────────────────────────────────── */
function openViewer(mediaId) {
  const m = mediaById(mediaId);
  if (!m) return;
  const url = UrlCache.get(mediaId);
  const body = $('#viewerBody');
  $('#viewer').classList.remove('hidden');
  if (m.type === 'image') {
    body.innerHTML = `<img src="${url}" alt="">`;
    $('#viewerCaption').textContent = `${m.width}×${m.height} · ${fmtSize(m.blob.size)}`;
  } else {
    body.innerHTML = `<audio controls autoplay src="${url}"></audio>`;
    $('#viewerCaption').textContent = `Voice note · ${fmtClock(m.duration)}`;
  }
}
function closeViewer() {
  $('#viewer').classList.add('hidden');
  $('#viewerBody').innerHTML = '';
}

/* ══════════════════════════════════════════════════════════════════
   KEY POINTS
   ══════════════════════════════════════════════════════════════════ */
function openKeySheet(draft) {
  S.keyDraft = draft;
  $('#keyText').value = draft.text || '';
  $('#keyPinned').checked = !!draft.pinned;
  $('#keyStatus').value = draft.status || 'open';
  $('#keySource').textContent = draft.sourceEntryId
    ? 'Promoted from an entry. File it under the aspects it belongs to.'
    : 'A decision, a commitment, a pattern worth keeping.';
  const paint = () => drawAspectChips($('#keyAspects'), draft.aspects || [], toggle);
  const toggle = id => {
    draft.aspects = (draft.aspects || []).includes(id) ? draft.aspects.filter(x => x !== id) : [...(draft.aspects || []), id];
    paint();
  };
  paint();
  $('#sheetKey').classList.remove('hidden');
  setTimeout(() => $('#keyText').focus(), 120);
}

async function saveKey() {
  const text = $('#keyText').value.trim();
  if (!text) { $('#sheetKey').classList.add('hidden'); return; }
  const k = Object.assign(S.keyDraft, {
    text,
    pinned: $('#keyPinned').checked,
    status: $('#keyStatus').value
  });
  if (!S.keypoints.find(x => x.id === k.id)) S.keypoints.push(k);
  else S.keypoints = S.keypoints.map(x => x.id === k.id ? k : x);

  /* if it came from a quote block, link the two so the entry shows what you kept */
  if (k.sourceEntryId && S.entry && S.entry.id === k.sourceEntryId) {
    const q = S.entry.blocks.find(b => b.t === 'quote' && !b.keyPointId);
    if (q) q.keyPointId = k.id;
  }
  await Store.put(Store.T.KEYS, k);
  $('#sheetKey').classList.add('hidden');
  if (S.entry) drawBlocks();
  renderAll();
  toast('Key point saved.');
}

/* ══════════════════════════════════════════════════════════════════
   ASPECTS edit
   ══════════════════════════════════════════════════════════════════ */
function openAspectSheet(id) {
  const existing = id ? S.aspects.find(a => a.id === id) : null;
  S.aspectDraft = existing
    ? JSON.parse(JSON.stringify(existing))
    : { id: uid('a'), name: '', glyph: '◇', color: ASPECT_COLORS[S.aspects.length % ASPECT_COLORS.length], order: S.aspects.length, bigRock: false, focus: [], archived: false };
  $('#aspectSheetTitle').textContent = existing ? 'Edit aspect' : 'New aspect';
  $('#aspectName').value = S.aspectDraft.name;
  $('#aspectGlyph').value = S.aspectDraft.glyph;
  $('#aspectBigRock').checked = !!S.aspectDraft.bigRock;
  $('#aspectArchive').textContent = existing ? 'Archive this aspect' : '';
  $('#aspectArchive').style.display = existing ? '' : 'none';
  $('#aspectColors').innerHTML = ASPECT_COLORS.map(c =>
    `<button class="swatch ${c === S.aspectDraft.color ? 'on' : ''}" style="background:${c}" data-color="${c}"></button>`).join('');
  $('#aspectColors').onclick = ev => {
    const b = ev.target.closest('[data-color]');
    if (!b) return;
    S.aspectDraft.color = b.dataset.color;
    $$('#aspectColors .swatch').forEach(s => s.classList.toggle('on', s.dataset.color === b.dataset.color));
  };
  $('#sheetAspect').classList.remove('hidden');
}

async function saveAspect() {
  const a = S.aspectDraft;
  a.name = $('#aspectName').value.trim() || a.name || 'Untitled';
  a.glyph = $('#aspectGlyph').value.trim() || a.glyph;
  a.bigRock = $('#aspectBigRock').checked;
  if (!S.aspects.find(x => x.id === a.id)) S.aspects.push(a);
  else S.aspects = S.aspects.map(x => x.id === a.id ? a : x);
  await Store.put(Store.T.ASPECTS, a);
  $('#sheetAspect').classList.add('hidden');
  renderAll();
}

/* ══════════════════════════════════════════════════════════════════
   WEEKLY REVIEW
   ══════════════════════════════════════════════════════════════════ */
function openReview() {
  const now = new Date();
  const week = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now); d.setDate(d.getDate() - i);
    const k = dateKey(d);
    const es = S.entries.filter(e => e.date === k);
    if (es.length) week.push(`<div class="focus-item"><span><b>${fmtMedium(k)}</b><br><span class="muted small">${escapeHTML(entryTitle(es[0]))}</span></span></div>`);
  }
  $('#reviewBody').innerHTML = `
    <div class="panel"><div class="panel-head"><b>This week</b><span class="muted small">${week.length} day${week.length === 1 ? '' : 's'} written</span></div>
      ${week.join('') || '<p class="muted small">Nothing written this week. The review still works — it just has less to work with.</p>'}
    </div>
    ${WEEK_QUESTIONS.map(q => `
      <div class="field">
        <span class="eyebrow">${escapeHTML(q.label)}</span>
        <p class="muted tiny" style="margin:2px 0 6px">${escapeHTML(q.hint)}</p>
        <textarea id="rv_${q.id}" rows="3" placeholder="…" style="width:100%;border:1px solid var(--line-2);border-radius:10px;padding:10px 12px;font-family:var(--serif);font-size:15.5px;background:var(--paper-2)"></textarea>
      </div>`).join('')}`;
  $('#sheetReview').classList.remove('hidden');
}

async function saveReview() {
  const answers = WEEK_QUESTIONS.map(q => ({ q, a: ($(`#rv_${q.id}`) || {}).value || '' }));
  if (!answers.some(x => x.a.trim())) { $('#sheetReview').classList.add('hidden'); return; }

  const blocks = [];
  answers.forEach(({ q, a }) => {
    if (!a.trim()) return;
    blocks.push({ t: 'text', text: `${q.label}\n${a.trim()}` });
  });
  const entry = {
    id: uid('e'), date: todayKey(), createdAt: Date.now(), updatedAt: Date.now(),
    kind: 'review', title: `Weekly review · ${fmtShort(todayKey())}`,
    blocks, mood: '', energy: '', aspects: [], place: ''
  };
  S.entries.push(entry);
  await Store.put(Store.T.ENTRIES, entry);

  /* The third answer becomes a key point. This is the mechanism that keeps the
     aspects view alive — without it, key points accumulate once and die. */
  const next = answers.find(x => x.q.id === 'next');
  if (next && next.a.trim()) {
    const kp = {
      id: uid('k'), text: next.a.trim(), aspects: [], date: todayKey(),
      sourceEntryId: entry.id, pinned: false, status: 'open'
    };
    S.keypoints.push(kp);
    await Store.put(Store.T.KEYS, kp);
  }
  $('#sheetReview').classList.add('hidden');
  renderAll();
  toast('Review saved. Tap the key point to file it under an aspect.');
}

/* ══════════════════════════════════════════════════════════════════
   SETTINGS · storage · backup · PIN
   ══════════════════════════════════════════════════════════════════ */
async function renderSettings() {
  const est = await Store.estimate();
  const bar = $('#storageBar');
  if (est && est.quota) {
    const pct = Math.min(100, (est.usage / est.quota) * 100);
    bar.style.width = Math.max(1.5, pct).toFixed(2) + '%';
    $('#storageText').textContent = `${fmtSize(est.usage)} of ${fmtSize(est.quota)} available (${pct < 1 ? '<1' : pct.toFixed(1)}% used)`;
    $('#storageState').textContent = pct > 80 ? 'getting full' : 'healthy';
  } else {
    $('#storageText').textContent = 'This browser does not report storage estimates.';
  }
  const p = S.meta.persist;
  $('#persistText').innerHTML = p === 'granted'
    ? '✓ Persistent storage granted — the browser will not evict this journal to reclaim space.'
    : p === 'denied'
      ? '⚠ Persistent storage was refused. Export a backup regularly; the browser could evict this data under storage pressure.'
      : p === 'unsupported'
        ? '⚠ This browser cannot request persistent storage. Export a backup regularly.'
        : 'Persistent storage has not been requested yet — it is asked for on your first saved entry.';
  $('#lastBackup').textContent = S.meta.lastBackup ? `Last backup: ${relTime(S.meta.lastBackup)}` : 'No backup taken yet.';
  $('#pinToggle').checked = !!S.meta.pin;
  $('#pinSetRow').classList.toggle('hidden', !S.meta.pin);
  $('#backendText').textContent = `Storage backend: ${Store.usingFallback ? 'localStorage fallback (media space is very limited — serve over http)' : 'IndexedDB'}${nativeShell() ? ', inside the Android app' : ''}. ${S.entries.length} entries · ${S.keypoints.length} key points · ${S.media.length} media files.`;
}

/* ── the Android bridge ───────────────────────────────────────────
   Inside the app's WebView, `<a download>` is silently ignored for blob:
   URLs — the export would look like it worked and write nothing. So when
   the shell is present, the finished bytes are handed to it instead and it
   asks the user where to put the file. Blob bytes are converted in chunks
   because String.fromCharCode.apply on a few megabytes overflows the stack. */
function nativeShell() {
  const n = window.NotesNative;
  try { return (n && typeof n.available === 'function' && n.available()) ? n : null; }
  catch (err) { return null; }
}
function blobToBase64(blob) {
  return blob.arrayBuffer().then(buf => {
    const bytes = new Uint8Array(buf);
    let out = '';
    const CHUNK = 0x8000;
    for (let i = 0; i < bytes.length; i += CHUNK) {
      out += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK));
    }
    return btoa(out);
  });
}

async function doExport() {
  try {
    toast('Building your backup…');
    const out = await Store.exportBackup();
    const shell = nativeShell();
    if (shell) {
      shell.saveFile(out.filename, await blobToBase64(out.blob));
      toast('Backup ready — choose where to save it.');
    } else {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(out.blob);
      a.download = out.filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 30000);
    }
    S.meta.lastBackup = Date.now();
    await Store.put(Store.T.META, { key: 'lastBackup', value: S.meta.lastBackup });
    renderSettings();
    toast(`Backup: ${out.counts.entries} entries, ${out.counts.media} media files (${fmtSize(out.bytes)}).`);
  } catch (err) {
    fail(err);
    toast('The export failed — see the red bar for the reason.');
  }
}

async function doImport(file) {
  try {
    toast('Importing…');
    const res = await Store.importBackup(await file.arrayBuffer());
    const all = await Store.readAll();
    S.entries = all.entries; S.media = all.media; S.keypoints = all.keypoints; S.aspects = all.aspects;
    renderAll();
    toast(`Imported ${res.entries} entries and ${res.media} media files.${res.missingMedia ? ` ${res.missingMedia} media entries had no file in the zip.` : ''}`);
  } catch (err) {
    fail(err);
    toast(String(err.message || err));
  }
}

/* ── PIN gate ───────────────────────────────────────────────────── */
let pinEntry = '';
let gateMode = 'unlock';
function showGate(mode = 'unlock') {
  gateMode = mode;
  pinEntry = '';
  $('#gate').classList.remove('hidden');
  $('#app').classList.add('hidden');
  $('#gateTitle').textContent = mode === 'unlock' ? 'Enter your PIN' : 'Choose a PIN';
  $('#gateSub').textContent = 'A gate, not a lockbox — it keeps a passer-by out, not a technician.';
  const keys = ['1','2','3','4','5','6','7','8','9','⌫','0','✓'];
  $('#keypad').innerHTML = keys.map(k => `<button data-key="${k}">${k}</button>`).join('');
  drawPinDots();
}
function drawPinDots() {
  $('#pinDots').innerHTML = Array.from({ length: 6 }, (_, i) => `<i class="${i < pinEntry.length ? 'on' : ''}"></i>`).join('');
}
async function pinKey(k) {
  if (k === '⌫') { pinEntry = pinEntry.slice(0, -1); drawPinDots(); return; }
  if (k === '✓') { await submitPin(); return; }
  if (pinEntry.length >= 6) return;
  pinEntry += k;
  drawPinDots();
  if (pinEntry.length === 4) await submitPin();   // most PINs are 4 digits
}
async function submitPin() {
  if (pinEntry.length < 4) return;
  const pin = S.meta.pin;
  const hash = await Store.hashPin(pinEntry, pin.salt);
  if (hash === pin.hash) {
    pinEntry = '';
    startApp();
  } else {
    $('#gate').classList.add('shake');
    setTimeout(() => $('#gate').classList.remove('shake'), 400);
    pinEntry = '';
    drawPinDots();
    $('#gateSub').textContent = 'That is not it.';
  }
}

/* ══════════════════════════════════════════════════════════════════
   EVENTS
   ══════════════════════════════════════════════════════════════════ */
function wire() {
  /* tabs */
  $$('.tab').forEach(t => t.onclick = () => nav(t.dataset.view));
  $('#composeBtn').onclick = () => openNewEntry(todayKey());

  /* global click delegation for entry cards + aspect cards */
  document.addEventListener('click', ev => {
    const open = ev.target.closest('[data-open]');
    if (open) {
      const e = S.entries.find(x => x.id === open.dataset.open);
      if (e) openEntry(e.id);
      return;
    }
    const asp = ev.target.closest('[data-aspect]');
    if (asp && !ev.target.closest('[data-keydone],[data-keydel],[data-unfocus],[data-focus]')) {
      S.activeAspect = S.activeAspect === asp.dataset.aspect ? null : asp.dataset.aspect;
      renderAspects();
      if (S.activeAspect) setTimeout(() => $('#aspectDetail').scrollIntoView({ behavior: 'smooth', block: 'start' }), 60);
      return;
    }
    const chip = ev.target.closest('[data-chip]');
    if (chip) {
      const [kind, id] = chip.dataset.chip.split(':');
      const set = kind === 'k' ? S.filters.aspects : S.filters.kinds;
      set.has(id) ? set.delete(id) : set.add(id);
      renderTimeline();
      return;
    }
    const sf = ev.target.closest('[data-sfilter]');
    if (sf) { S.searchFilter = sf.dataset.sfilter; renderSearch(); return; }

    const done = ev.target.closest('[data-keydone]');
    if (done) { cycleKey(done.dataset.keydone); return; }
    const del = ev.target.closest('[data-keydel]');
    if (del) { confirmAction(del, 'Tap again to delete this key point', () => deleteKey(del.dataset.keydel)); return; }
  });

  /* today */
  $('#promptShuffle').onclick = () => { S.prompt = PROMPTS[Math.floor(Math.random() * PROMPTS.length)]; renderToday(); };
  $('#promptUse').onclick = () => {
    const prompt = S.prompt;
    openNewEntry(todayKey());
    setTimeout(() => {
      if (!S.entry) return;
      S.entry.title = prompt;      // the question becomes the entry's heading
      drawEditor();
      const box = $('#blocksHost textarea');
      if (box) box.focus();
      patch(true);
    }, 90);
  };

  /* editor */
  $('#entryDone').onclick = () => closeEntry();
  $$('#sheetEntry [data-close]').forEach(b => b.onclick = () => closeEntry());
  $('#entryDate').onchange = ev => { S.entry.date = ev.target.value || todayKey(); patch(true); };
  $('#entryMood').onchange = ev => { S.entry.mood = ev.target.value; patch(true); };
  $('#entryEnergy').onchange = ev => { S.entry.energy = ev.target.value; patch(true); };
  $('#addText').onclick = () => { S.entry.blocks.push({ t: 'text', text: '' }); drawBlocks(); patch(true); $$('#blocksHost textarea').pop().focus(); };
  $('#addAudio').onclick = openRecorder;
  $('#entryDelete').onclick = ev => confirmAction(ev.target, S.isNew ? 'Tap again to discard this entry' : 'Tap again to delete this entry forever', async () => {
    if (!S.isNew) await Store.deleteEntryCascade(S.entry.id);
    S.entries = S.entries.filter(x => x.id !== S.entry.id);
    S.entry = null;
    $('#sheetEntry').classList.add('hidden');
    renderAll();
    toast('Deleted.');
  });

  $('#photoInput').onchange = ev => { addPhotos(ev.target.files); ev.target.value = ''; };
  $('#galleryInput').onchange = ev => { addPhotos(ev.target.files); ev.target.value = ''; };

  $('#makeKeyPoint').onclick = () => promoteSelection(false);
  $('#quoteIt').onclick = () => promoteSelection(true);
  $('#dismissBar').onclick = hideHighlightBar;
  document.addEventListener('scroll', hideHighlightBar, { passive: true });

  /* key point sheet */
  $$('#sheetKey [data-close]').forEach(b => b.onclick = () => { $('#sheetKey').classList.add('hidden'); });
  $('#keySave').onclick = saveKey;

  /* aspect detail actions */
  document.addEventListener('click', ev => {
    const write = ev.target.closest('#writeAspect');
    if (write) { const id = write.dataset.id; openNewEntry(todayKey()); setTimeout(() => { if (S.entry) { S.entry.aspects = [id]; drawEditor(); } }, 90); return; }
    const keyBtn = ev.target.closest('#keyAspect');
    if (keyBtn) { openKeySheet({ id: uid('k'), text: '', aspects: [keyBtn.dataset.id], date: todayKey(), sourceEntryId: null, pinned: false, status: 'open' }); return; }
    const edit = ev.target.closest('#editAspect');
    if (edit) { openAspectSheet(edit.dataset.id); return; }
    const cb = ev.target.closest('[data-focus]');
    if (cb) {
      const a = S.aspects.find(x => x.id === S.activeAspect);
      a.focus[Number(cb.dataset.focus)].done = cb.checked;
      Store.put(Store.T.ASPECTS, a).then(renderAspects);
      return;
    }
    const un = ev.target.closest('[data-unfocus]');
    if (un) {
      const a = S.aspects.find(x => x.id === S.activeAspect);
      a.focus.splice(Number(un.dataset.unfocus), 1);
      Store.put(Store.T.ASPECTS, a).then(renderAspects);
      return;
    }
    if (ev.target.id === 'focusAdd') {
      const input = $('#focusInput');
      const text = input.value.trim();
      if (!text) return;
      const a = S.aspects.find(x => x.id === S.activeAspect);
      a.focus = a.focus || [];
      a.focus.push({ text, done: false, addedAt: Date.now() });
      input.value = '';
      Store.put(Store.T.ASPECTS, a).then(renderAspects);
      return;
    }
  });

  document.addEventListener('keydown', ev => { if (ev.key === 'Enter' && ev.target.id === 'focusInput') $('#focusAdd').click(); });

  /* aspect sheet */
  $('#addAspect').onclick = () => openAspectSheet(null);
  $$('#sheetAspect [data-close]').forEach(b => b.onclick = () => $('#sheetAspect').classList.add('hidden'));
  $('#aspectSave').onclick = saveAspect;
  $('#aspectArchive').onclick = ev => confirmAction(ev.target, 'Tap again to archive this aspect', async () => {
    S.aspectDraft.archived = true;
    if (!S.aspects.find(x => x.id === S.aspectDraft.id)) S.aspects.push(S.aspectDraft);
    else S.aspects = S.aspects.map(x => x.id === S.aspectDraft.id ? S.aspectDraft : x);
    await Store.put(Store.T.ASPECTS, S.aspectDraft);
    $('#sheetAspect').classList.add('hidden');
    S.activeAspect = null;
    renderAll();
  });

  /* review */
  $('#reviewBtn').onclick = openReview;
  $('#reviewSave').onclick = saveReview;
  $$('#sheetReview [data-close]').forEach(b => b.onclick = () => $('#sheetReview').classList.add('hidden'));

  /* recorder */
  $$('#sheetRecord [data-close]').forEach(b => b.onclick = () => {
    if (S.recorder) { S.recorder.rec.onstop = null; S.recorder.rec.stop(); S.recorder.stopMaster(); S.recorder = null; }
    $('#sheetRecord').classList.add('hidden');
  });
  $('#recToggle').onclick = () => (S.recorder ? stopRecording() : startRecording());
  $('#recDiscard').onclick = () => {
    if (S.recorder) { S.recorder.rec.onstop = null; S.recorder.rec.stop(); S.recorder.stopMaster(); S.recorder = null; }
    $('#recToggle').textContent = 'Record';
    $('#sheetRecord').classList.add('hidden');
  };

  /* viewer */
  $('#viewerClose').onclick = closeViewer;
  $('#viewer').onclick = ev => { if (ev.target.id === 'viewer') closeViewer(); };

  /* settings */
  $('#settingsBtn').onclick = () => { renderSettings(); $('#sheetSettings').classList.remove('hidden'); };
  $$('#sheetSettings [data-close]').forEach(b => b.onclick = () => $('#sheetSettings').classList.add('hidden'));
  $('#exportBtn').onclick = doExport;
  $('#importInput').onchange = ev => { if (ev.target.files[0]) doImport(ev.target.files[0]); ev.target.value = ''; };
  $('#pinToggle').onchange = async ev => {
    if (ev.target.checked) { $('#pinSetRow').classList.remove('hidden'); return; }
    delete S.meta.pin;
    await Store.remove(Store.T.META, 'pin');
    $('#pinSetRow').classList.add('hidden');
    toast('PIN removed.');
  };
  $('#pinSave').onclick = async () => {
    const a = $('#pinA').value.trim(), b = $('#pinB').value.trim();
    if (a.length < 4 || a !== b) { toast('PINs must match and be at least 4 digits.'); return; }
    const salt = Store.makeSalt();
    S.meta.pin = { salt, hash: await Store.hashPin(a, salt) };
    await Store.put(Store.T.META, { key: 'pin', value: S.meta.pin });
    $('#pinA').value = ''; $('#pinB').value = '';
    $('#pinToggle').checked = true;
    toast('PIN set. It will be asked for next time the app opens.');
  };
  $('#wipeBtn').onclick = ev => confirmAction(ev.target, 'Tap again to erase EVERYTHING', async () => {
    await Store.clearAll();
    S.entries = []; S.media = []; S.keypoints = []; S.aspects = []; S.meta = {};
    location.reload();
  });

  /* search */
  $('#searchInput').oninput = ev => {
    S.search = ev.target.value;
    clearTimeout(searchTimer);
    searchTimer = setTimeout(renderSearch, 140);
  };

  /* timeline */
  $('#randomPage').onclick = () => {
    const old = S.entries.filter(e => daysAgo(e.date) > 14);
    const pool = old.length ? old : S.entries;
    if (!pool.length) return;
    openEntry(pool[Math.floor(Math.random() * pool.length)].id);
  };
  $('#loadMore').onclick = () => { S.timelineLimit += 30; renderTimeline(); };

  /* gate */
  $('#keypad').onclick = ev => { const b = ev.target.closest('[data-key]'); if (b) pinKey(b.dataset.key); };
  $('#gateForget').onclick = ev => confirmAction(ev.target, 'Tap again to remove the PIN', async () => {
    delete S.meta.pin;
    await Store.remove(Store.T.META, 'pin');
    toast('PIN removed. The journal is unchanged.');
    startApp();
  });
  document.addEventListener('keydown', ev => {
    if ($('#gate').classList.contains('hidden')) return;
    if (/^[0-9]$/.test(ev.key)) pinKey(ev.key);
    if (ev.key === 'Backspace') pinKey('⌫');
    if (ev.key === 'Enter') pinKey('✓');
  });
}

async function cycleKey(id) {
  const k = S.keypoints.find(x => x.id === id);
  if (!k) return;
  k.status = k.status === 'open' ? 'done' : k.status === 'done' ? 'dropped' : 'open';
  await Store.put(Store.T.KEYS, k);
  renderAspects();
}
async function deleteKey(id) {
  await Store.remove(Store.T.KEYS, id);
  S.keypoints = S.keypoints.filter(k => k.id !== id);
  renderAspects();
  toast('Deleted.');
}

/* ── go ─────────────────────────────────────────────────────────── */
wire();
boot().catch(fail);
