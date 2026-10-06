/* ══════════════════════════════════════════════════════════════════
   Notes · end-to-end test — drives the real app in a real DOM against a
   real IndexedDB, exactly the way a thumb would.

   It found a genuine data-loss bug the first time it ran: a key point
   promoted from a sentence was pushed to memory but never written to
   storage, so it showed up in the Aspects view and vanished on reload.
   In-memory assertions cannot catch that. This can.

       cd journal/test && npm install && npm test

   Needs the dev server running (../serve.py), because the page is loaded
   over http — IndexedDB and getUserMedia are not available on file://,
   which is the whole reason the app is served rather than opened.
   ══════════════════════════════════════════════════════════════════ */

import { JSDOM, VirtualConsole } from 'jsdom';
import { indexedDB, IDBKeyRange } from 'fake-indexeddb';
import { webcrypto, randomFillSync } from 'node:crypto';

const ORIGIN = process.env.NOTES_URL || 'http://127.0.0.1:8090';
/* Which page to drive. Default is the app as authored; point it at
   /release/Notes.html to run this exact suite against the built single file —
   the artifact's scripts are inline, so it needs no subresources to load. */
const PAGE = process.env.NOTES_PAGE || '/index.html';
const wait = ms => new Promise(r => setTimeout(r, ms));

let passed = 0, failed = 0;
const step = (name, ok, extra = '') => {
  console.log(`  ${ok ? '✓' : '✗'} ${name}${extra ? '  → ' + extra : ''}`);
  ok ? passed++ : failed++;
};

const problems = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => {
  /* Nothing is fetched any more — fonts are bundled — so a resource failure is
     no longer expected. Report it rather than swallowing it, but keep it
     distinct from a script error, which is what this test exists to catch. */
  if (e.type === 'resource loading') { problems.push('RESOURCE: ' + (e.detail?.message || e.message)); return; }
  const m = e.detail?.message || e.message || String(e.detail);
  if (!/scrollTo|Not implemented/.test(m)) problems.push(`JSDOM ${e.type || ''}: ${m}`);
});
vc.on('error', (...a) => problems.push('CONSOLE.ERROR: ' + a.join(' ')));

/* fake-indexeddb is a module singleton, so a second JSDOM sees the same
   database — which is how the restart test below works. */
async function launch() {
  const dom = await JSDOM.fromURL(`${ORIGIN}${PAGE}`, {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.indexedDB = indexedDB;
      w.IDBKeyRange = IDBKeyRange;
      Object.defineProperty(w, 'crypto', {
        value: { getRandomValues: a => randomFillSync(a), subtle: webcrypto.subtle }, configurable: true
      });
      w.navigator.storage = {
        estimate: async () => ({ usage: 12_400_000, quota: 2_147_483_648 }),
        persist: async () => true, persisted: async () => false
      };
      w.URL.createObjectURL = () => 'blob:stub';
      w.URL.revokeObjectURL = () => {};
      w.HTMLElement.prototype.scrollIntoView = () => {};
    }
  });
  await wait(1100);
  return dom;
}

const dom = await launch();
const w = dom.window, d = w.document;
const $ = s => d.querySelector(s);
const tab = name => [...d.querySelectorAll('.tab')].find(t => t.dataset.view === name);
const type = (el, text) => { el.value = text; el.dispatchEvent(new w.Event('input', { bubbles: true })); };
/* What the user can read. Assertions about copy must not look at <script> text:
   in the built single file the app's own source is inlined into <body>, so a raw
   body.textContent would "find" words that are only in comments. */
const uiText = () => {
  const c = d.body.cloneNode(true);
  c.querySelectorAll('script, style').forEach(n => n.remove());
  return c.textContent;
};
const now = new Date();
const longToday = `${['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][now.getDay()]}, ${now.getDate()} ${
  ['January','February','March','April','May','June','July','August','September','October','November','December'][now.getMonth()]} ${now.getFullYear()}`;

/* ── 1 · boot ───────────────────────────────────────────────────── */
console.log('\nboot');
step('no error banner', $('#errorBanner').classList.contains('hidden'), $('#errorBanner').textContent.slice(0, 160));
step('app visible, PIN gate not shown (it is opt-in)', !$('#app').classList.contains('hidden') && $('#gate').classList.contains('hidden'));
step('eight aspects seeded', d.querySelectorAll('.aspect-card').length === 8, `${d.querySelectorAll('.aspect-card').length}`);
step('consistency grid, and no streak counter anywhere',
     d.querySelectorAll('#todayGrid i').length === 60 && !/\bstreak\b/i.test(uiText()),
     `${d.querySelectorAll('#todayGrid i').length} dots`);
step('date heading reads as a journal, in local time', $('#todayDate').textContent.includes(longToday), $('#todayDate').textContent.slice(0, 34));
step('a prompt is offered', $('#promptText').textContent.length > 10);
step('the empty state invites one honest line', /one honest line/.test($('#todayEntries').textContent));

/* ── 2 · write ──────────────────────────────────────────────────── */
console.log('\nwriting (write-first: the + button is the front door)');
$('#composeBtn').click();
await wait(250);
step('editor opens on a blank page', !$('#sheetEntry').classList.contains('hidden') && d.querySelectorAll('#blocksHost textarea').length === 1);
const firstBox = () => $('#blocksHost textarea');
type(firstBox(), 'Walked to the temple before sunrise.');
await wait(800);
step('autosaves with no Save button', $('#saveState').textContent === 'saved', `state="${$('#saveState').textContent}"`);

firstBox().dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true }));
await wait(300);
step('Enter at the end of a line opens a new block', d.querySelectorAll('#blocksHost textarea').length === 2);
const secondBox = d.querySelectorAll('#blocksHost textarea')[1];
type(secondBox, 'Mornings are the only hours that are actually mine. But I fill them with other people.');
await wait(250);

const chipFor = label => [...d.querySelectorAll('#entryAspects .chip')].find(c => c.textContent.includes(label));
chipFor('Inner life').click();
await wait(700);
step('the entry is filed under an aspect', chipFor('Inner life').classList.contains('on'));

/* ── 3 · the core interaction: highlight → key point ────────────── */
console.log('\nthe loop (this is the whole reason the two halves are one app)');
const SENTENCE = 'Mornings are the only hours that are actually mine.';
secondBox.selectionStart = 0;
secondBox.selectionEnd = SENTENCE.length;
secondBox.dispatchEvent(new w.MouseEvent('mouseup', { bubbles: true }));
await wait(150);
step('highlighting a sentence raises the promote bar', !$('#highlightBar').classList.contains('hidden'));
$('#makeKeyPoint').click();
await wait(900);
step('the sentence is now a quote block inside the entry', !!$('.block-quote'), ($('.block-quote')?.textContent || '').trim().slice(0, 46));
step('and it is marked as a key point', /key point/i.test($('.block-quote .kp-label')?.textContent || ''));
step('the leftover text survives the split', /But I fill them with other people/.test(d.querySelector('#blocksHost').textContent));

$('#entryDone').click();
await wait(450);
step('the entry appears on Today', !!$('#todayEntries .entry-card'));
step('its title is its own first line', /Walked to the temple/.test($('.entry-title')?.textContent || ''));

/* ── 4 · the aspects view shows it back ─────────────────────────── */
console.log('\naspects (a lens over your writing, not a second inbox)');
tab('aspects').click();
await wait(400);
const innerCard = [...d.querySelectorAll('.aspect-card')].find(c => c.textContent.includes('Inner life'));
step('the card says it was touched today', /touched today/.test(innerCard.textContent), innerCard.querySelector('.meta').textContent.trim());
step('the card counts the key point', /1 key point/.test(innerCard.textContent));
innerCard.click();
await wait(400);
step('the aspect detail shows the promoted sentence', /Mornings are the only hours/.test($('#aspectDetail').textContent));
step('and reports real numbers, not decoration', /entries/.test($('#aspectDetail').textContent) && /words/.test($('#aspectDetail').textContent));

/* ── 5 · weekly review ──────────────────────────────────────────── */
console.log('\nweekly review (the habit that keeps key points coming)');
$('#reviewBtn').click();
await wait(300);
step('it asks its three fixed questions', d.querySelectorAll('#reviewBody textarea').length === 3);
$('#rv_next').value = 'Protect the first hour of the morning.';
$('#reviewSave').click();
await wait(700);
step('saving produces a review entry in the timeline', await (async () => {
  tab('timeline').click(); await wait(350);
  const ok = /Weekly review/.test($('#timeline').textContent);
  tab('today').click(); await wait(200);
  return ok;
})());
step('and the third answer becomes a key point', (await w.eval('Store.readAll().then(a => a.keypoints.length)')) >= 2);

/* ── 6 · timeline + search ──────────────────────────────────────── */
console.log('\nfinding things again');
tab('timeline').click();
await wait(350);
step('timeline lists both entries', d.querySelectorAll('#timeline .entry-card').length === 2, `${d.querySelectorAll('#timeline .entry-card').length}`);
step('the review is visually distinct', !!$('#timeline .entry-card.review'));
tab('search').click();
$('#searchInput').value = 'temple';
$('#searchInput').dispatchEvent(new w.Event('input', { bubbles: true }));
await wait(400);
step('search finds an entry by its own words', /Walked to the temple/.test($('#searchResults').textContent));
$('#searchInput').value = 'protect the first hour';
$('#searchInput').dispatchEvent(new w.Event('input', { bubbles: true }));
await wait(400);
step('search finds a key point made during the review', /Protect the first hour/.test($('#searchResults').textContent));

/* ── 7 · storage, and surviving a restart ───────────────────────── */
console.log('\npersistence (a journal you can lose is not a journal)');
const before = JSON.parse(await w.eval(`Store.readAll().then(a => JSON.stringify({
  e: a.entries.length, k: a.keypoints.length,
  texts: a.keypoints.map(x => x.text).sort(),
  linked: a.entries.flatMap(e => e.blocks.filter(b => b.t === 'quote').map(b => b.keyPointId)).filter(Boolean).length
}))`));
step('every key point reached storage, not just the screen', before.k >= 2 && before.texts.length === before.k, JSON.stringify(before));
step('the promoted sentence is still linked to its key point', before.linked >= 1);

const $s = s => d.querySelector(s);
$s('#settingsBtn').click();
await wait(600);
step('storage meter shows real numbers', /of 2\.0+ GB available/.test($s('#storageText').textContent), $s('#storageText').textContent);
step('the persistence state is stated, not hidden', /Persistent storage granted/.test($s('#persistText').textContent));
step('the PIN is opt-in and off by default', $s('#pinToggle').checked === false);
step('the privacy panel admits a PIN is not encryption', /not encryption/.test($s('#sheetSettings').textContent.replace(/\s+/g, ' ')));
dom.window.close();

/* a genuinely new page, sharing only the database — i.e. reopening the app */
const dom2 = await launch();
const d2 = dom2.window.document;
const $2 = s => d2.querySelector(s);
step('after a full restart the entry is still on Today', /Walked to the temple/.test($2('#todayEntries').textContent));
const after = JSON.parse(await dom2.window.eval('Store.readAll().then(a => JSON.stringify({e:a.entries.length,k:a.keypoints.length}))'));
step('and the stored journal matches what was on screen', after.e === before.e && after.k === before.k, JSON.stringify(after));
step('reopening restores the aspect link, not a loose end', (() => {
  [...d2.querySelectorAll('.tab')].find(t => t.dataset.view === 'aspects').click();
  const card = [...d2.querySelectorAll('.aspect-card')].find(c => c.textContent.includes('Inner life'));
  return /touched today/.test(card.textContent);
})());
dom2.window.close();

/* ── overlays: a closed sheet must not swallow taps ───────────────────
   The rule is not "the sheet is invisible" — an invisible full-screen layer
   still eats every tap. It has to leave the hit-testing tree.

   This checks the mechanism rather than a computed display, deliberately:
   jsdom's getComputedStyle ignores !important when the important rule is
   declared *before* a more specific one (verified: `.hidden` sits at the top
   of styles.css, `.sheet.modal` 200 lines below), while browsers honour
   importance over both order and specificity. Asserting the computed value
   here would test jsdom's bug instead of the app. */
console.log('\noverlays (a closed sheet must not swallow taps)');
const dom3 = await launch();
const d3 = dom3.window.document;
const w3 = dom3.window;
const $$ = s => d3.querySelector(s);
const OVERLAYS = ['#gate', '#sheetEntry', '#sheetKey', '#sheetAspect', '#sheetReview',
                  '#sheetRecord', '#sheetSettings', '#viewer'];
const closed = sel => { const el = $$(sel); return !el || el.classList.contains('hidden'); };
step('every overlay starts closed', OVERLAYS.every(closed),
     OVERLAYS.filter(s => !closed(s)).join(' ') || 'all closed');

const cssText = [...d3.querySelectorAll('style')].map(s => s.textContent).join('\n')
  + [...d3.styleSheets].map(sh => { try { return [...sh.cssRules].map(r => r.cssText).join('\n'); } catch (e) { return ''; } }).join('\n');
const hiddenRule = (cssText.match(/\.hidden\s*\{[^}]*\}/) || [''])[0];
step('.hidden removes the element from painting AND hit-testing',
     /display:\s*none\s*!important/.test(hiddenRule) &&
     /pointer-events:\s*none\s*!important/.test(hiddenRule),
     hiddenRule.replace(/\s+/g, ' ').slice(0, 84));

$$('#composeBtn').click();
await wait(400);
const openNow = $$('#sheetEntry');
step('the editor, once opened, is not hidden', !openNow.classList.contains('hidden'));

$$('#sheetEntry [data-close]').click();          // "Cancel" — the app's own path
await wait(400);
step('after Cancel the overlay is closed again, not a transparent lid',
     openNow.classList.contains('hidden'));
step('and no other overlay was left open by the round trip', OVERLAYS.every(closed));
dom3.window.close();

console.log(`\npage errors: ${problems.length ? '\n  ' + problems.join('\n  ') : 'none'}`);
console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed || problems.length ? 1 : 0);
