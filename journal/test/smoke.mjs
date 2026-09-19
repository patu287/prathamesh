/* ══════════════════════════════════════════════════════════════════
   Rojni · smoke test
   Runs data.js + store.js in a bare Node context with no DOM and no
   IndexedDB — which means everything goes through the localStorage
   fallback. That is deliberate: it is the path that silently corrupts
   (a Blob cannot be JSON-serialised), and the one nobody exercises.

       node test/smoke.mjs

   The backup test is the important one: export → import → compare.
   A journal you can lose is not a journal.
   ══════════════════════════════════════════════════════════════════ */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');

let passed = 0, failed = 0;
function test(name, fn) {
  try { fn(); console.log(`  ✓ ${name}`); passed++; }
  catch (err) { console.log(`  ✗ ${name}\n      ${err.message}`); failed++; }
}
async function testAsync(name, fn) {
  try { await fn(); console.log(`  ✓ ${name}`); passed++; }
  catch (err) { console.log(`  ✗ ${name}\n      ${err.message}`); failed++; }
}

/* ── the harness ────────────────────────────────────────────────── */
function makeStore() {
  const mem = new Map();
  const localStorage = {
    getItem: k => (mem.has(k) ? mem.get(k) : null),
    setItem: (k, v) => mem.set(k, String(v)),
    removeItem: k => mem.delete(k)
  };
  const window = { crypto: globalThis.crypto };   // no indexedDB on purpose

  /* A working FileReader stub — the localStorage fallback path really does
     depend on it (that is how a Blob becomes a data URL), so stubbing it out
     would make the test pass while the feature was broken. */
  class FileReader {
    readAsDataURL(blob) {
      blob.arrayBuffer().then(buf => {
        const b64 = Buffer.from(new Uint8Array(buf)).toString('base64');
        this.result = `data:${blob.type || 'application/octet-stream'};base64,${b64}`;
        this.onload && this.onload();
      }).catch(err => { this.error = err; this.onerror && this.onerror(); });
    }
  }
  const src = readFileSync(join(root, 'data.js'), 'utf8') + '\n'
            + readFileSync(join(root, 'store.js'), 'utf8') + '\n'
            + 'return { Store, uid, dateKey, todayKey, daysAgo, relDate, fmtLong, fmtShort, fmtClock, fmtSize, entryTitle, blocksText, wordCount, escapeHTML, parseKey };';
  const factory = new Function('window', 'document', 'navigator', 'localStorage',
    'Blob', 'TextEncoder', 'TextDecoder', 'atob', 'btoa', 'URL', 'FileReader', 'indexedDB', src);
  return factory(window, {}, {}, localStorage, Blob, TextEncoder, TextDecoder,
    globalThis.atob, globalThis.btoa, URL, FileReader, undefined);
}

const api = makeStore();
const { Store } = api;

/* ── date handling ──────────────────────────────────────────────── */
console.log('\ndates');
test('dateKey uses the LOCAL day, never a UTC instant', () => {
  const late = new Date(2026, 8, 19, 23, 40);      // 11:40pm local
  assert.equal(api.dateKey(late), '2026-09-19', 'a late-night entry must land on today');
  const early = new Date(2026, 8, 20, 0, 5);
  assert.equal(api.dateKey(early), '2026-09-20');
});
test('dateKey zero-pads', () => assert.equal(api.dateKey(new Date(2026, 0, 3)), '2026-01-03'));
test('parseKey round-trips', () => {
  assert.equal(api.dateKey(api.parseKey('2026-09-19')), '2026-09-19');
});
test('fmtLong reads like a journal', () =>
  assert.equal(api.fmtLong('2026-09-19'), 'Saturday, 19 September 2026'));
test('relDate speaks plainly', () => {
  const today = api.todayKey();
  assert.equal(api.relDate(today), 'today');
  const y = new Date(); y.setDate(y.getDate() - 1);
  assert.equal(api.relDate(api.dateKey(y)), 'yesterday');
  const w = new Date(); w.setDate(w.getDate() - 12);
  assert.equal(api.relDate(api.dateKey(w)), '12 days ago');
  const yr = new Date(); yr.setDate(yr.getDate() - 365);
  assert.equal(api.relDate(api.dateKey(yr)), 'a year ago');
});
test('fmtClock handles minutes and hours', () => {
  assert.equal(api.fmtClock(0), '0:00');
  assert.equal(api.fmtClock(7), '0:07');
  assert.equal(api.fmtClock(412.6), '6:53');
  assert.equal(api.fmtClock(3725), '1:02:05');
});
test('fmtSize', () => {
  assert.equal(api.fmtSize(240 * 1024), '240 KB');
  assert.equal(api.fmtSize(5 * 1048576), '5.0 MB');
});

/* ── entry text ─────────────────────────────────────────────────── */
console.log('\nentries');
test('entryTitle falls back to the first real line', () => {
  const e = { blocks: [{ t: 'text', text: '\n\n  A long day. ' }, { t: 'text', text: 'More.' }] };
  assert.equal(api.entryTitle(e), 'A long day.');
});
test('entryTitle names media-only entries', () => {
  assert.equal(api.entryTitle({ blocks: [{ t: 'audio', media: 'm1' }] }), 'Voice note');
  assert.equal(api.entryTitle({ blocks: [{ t: 'photo', media: 'm2' }] }), 'Photo');
});
test('entryTitle truncates without exploding', () => {
  const t = api.entryTitle({ blocks: [{ t: 'text', text: 'x'.repeat(200) }] });
  assert.ok(t.length <= 94 && t.endsWith('…'));
});
test('entryTitle prefers an explicit title (reviews, prompts)', () =>
  assert.equal(api.entryTitle({ title: 'Weekly review', blocks: [{ t: 'text', text: 'hi' }] }), 'Weekly review'));
test('wordCount counts real words, not empty blocks', () => {
  assert.equal(api.wordCount({ blocks: [{ t: 'text', text: 'one two three' }, { t: 'text', text: '' }] }), 3);
  assert.equal(api.wordCount({ blocks: [{ t: 'photo', media: 'm' }] }), 0);
});
test('escapeHTML neutralises a script tag', () =>
  assert.equal(api.escapeHTML('<img src=x onerror=alert(1)>'), '&lt;img src=x onerror=alert(1)&gt;'));

/* ── storage fallback: the path that silently corrupts ──────────── */
console.log('\nstorage (localStorage fallback — no IndexedDB available)');
const bytes = new Uint8Array([1, 2, 3, 4, 5, 250, 251, 252]);

await testAsync('a Blob survives the round trip (this is the bug it guards)', async () => {
  const blob = new Blob([bytes], { type: 'audio/webm' });
  await Store.put(Store.T.MEDIA, { id: 'm1', entryId: 'e1', type: 'audio', blob, duration: 42.5, mime: 'audio/webm' });
  const back = await Store.readTable(Store.T.MEDIA);
  assert.equal(back.length, 1);
  assert.ok(back[0].blob, 'the blob must come back — a JSON-serialised Blob stringifies to {} and vanishes silently');
  const got = new Uint8Array(await back[0].blob.arrayBuffer());
  assert.deepEqual([...got], [...bytes], 'bytes must be identical');
  assert.equal(back[0].duration, 42.5);
});

await testAsync('entries survive the round trip', async () => {
  const entry = {
    id: 'e1', date: '2026-09-19', createdAt: Date.now(), updatedAt: Date.now(),
    kind: 'day', title: '', mood: 4, energy: 3, aspects: ['health'],
    blocks: [{ t: 'text', text: 'First line.\nSecond line.' }, { t: 'audio', media: 'm1' }]
  };
  await Store.put(Store.T.ENTRIES, entry);
  const back = await Store.readAll();
  assert.equal(back.entries.length, 1);
  assert.equal(back.entries[0].blocks[1].media, 'm1');
  assert.deepEqual(back.entries[0].aspects, ['health']);
});

await testAsync('the meta table is a plain object, not an array of rows', async () => {
  await Store.put(Store.T.META, { key: 'persist', value: 'granted' });
  await Store.put(Store.T.META, { key: 'sessionDays', value: ['2026-09-19'] });
  const { meta } = await Store.readAll();
  assert.equal(meta.persist, 'granted');
  assert.deepEqual(meta.sessionDays, ['2026-09-19']);
});

await testAsync('deleteEntryCascade takes its media with it', async () => {
  await Store.deleteEntryCascade('e1');
  const all = await Store.readAll();
  assert.equal(all.entries.length, 0);
  assert.equal(all.media.length, 0, 'orphaned audio would sit in storage forever');
});

/* ── PIN ────────────────────────────────────────────────────────── */
console.log('\nPIN');
await testAsync('the same PIN and salt always hash the same', async () => {
  const salt = Store.makeSalt();
  const a = await Store.hashPin('4821', salt);
  const b = await Store.hashPin('4821', salt);
  assert.equal(a, b);
  assert.notEqual(a, await Store.hashPin('4822', salt));
  assert.notEqual(a, await Store.hashPin('4821', Store.makeSalt()));
  assert.ok(a.length >= 32);
});

/* ── backup: the whole point ────────────────────────────────────── */
console.log('\nbackup (ZIP write → read → restore)');
const photoBytes = new Uint8Array(2000).map((_, i) => (i * 37) % 256);
const audioBytes = new Uint8Array(5000).map((_, i) => (i * 11) % 256);

await testAsync('export → import restores the journal byte-for-byte', async () => {
  await Store.clearAll();
  const blob1 = new Blob([photoBytes], { type: 'image/jpeg' });
  const blob2 = new Blob([audioBytes], { type: 'audio/webm' });

  await Store.put(Store.T.ENTRIES, {
    id: 'e1', date: '2026-09-18', createdAt: 1, updatedAt: 1, kind: 'day', title: '',
    mood: 5, energy: 2, aspects: ['inner'],
    blocks: [{ t: 'text', text: 'A day worth keeping.' }, { t: 'photo', media: 'm1' }, { t: 'audio', media: 'm2' },
             { t: 'quote', text: 'What I actually meant.', keyPointId: 'k1' }]
  });
  await Store.put(Store.T.MEDIA, { id: 'm1', entryId: 'e1', type: 'image', blob: blob1, thumb: null, mime: 'image/jpeg', width: 1400, height: 900 });
  await Store.put(Store.T.MEDIA, { id: 'm2', entryId: 'e1', type: 'audio', blob: blob2, peaks: [1, 2, 3], mime: 'audio/webm', duration: 132.4 });
  await Store.put(Store.T.KEYS, { id: 'k1', text: 'What I actually meant.', aspects: ['inner'], date: '2026-09-18', sourceEntryId: 'e1', pinned: true, status: 'open' });
  await Store.put(Store.T.ASPECTS, { id: 'inner', name: 'Inner life', glyph: '◐', color: '#7a4a6b', order: 0, bigRock: true, focus: [{ text: 'sit still', done: false }] });

  const out = await Store.exportBackup();
  assert.ok(out.blob.size > 7000, 'the zip should contain the media, not just the manifest');
  assert.match(out.filename, /^rojni-backup-\d{4}-\d{2}-\d{2}\.zip$/);
  assert.deepEqual(out.counts, { entries: 1, media: 2, keypoints: 1 });

  const zip = new Uint8Array(await out.blob.arrayBuffer());
  const names = ['journal.json', 'media/m1.jpg', 'media/m2.webm'];
  names.forEach(n => assert.ok(
    Buffer.from(zip).includes(Buffer.from(n)), `the zip must list ${n} — a backup is real files, not a database dump`));

  await Store.clearAll();
  assert.equal((await Store.readAll()).entries.length, 0, 'a fresh install must really be empty');

  const res = await Store.importBackup(zip.buffer.slice(zip.byteOffset, zip.byteOffset + zip.byteLength));
  assert.deepEqual([res.entries, res.media, res.keypoints, res.missingMedia], [1, 2, 1, 0]);

  const back = await Store.readAll();
  assert.equal(back.entries[0].blocks[0].text, 'A day worth keeping.');
  assert.equal(back.entries[0].blocks[3].keyPointId, 'k1', 'the link from sentence to key point must survive');
  assert.equal(back.keypoints[0].pinned, true);
  assert.equal(back.aspects[0].focus[0].text, 'sit still');

  const gotPhoto = new Uint8Array(await back.media.find(m => m.id === 'm1').blob.arrayBuffer());
  const gotAudio = new Uint8Array(await back.media.find(m => m.id === 'm2').blob.arrayBuffer());
  assert.deepEqual([...gotPhoto], [...photoBytes], 'photo bytes must be identical');
  assert.deepEqual([...gotAudio], [...audioBytes], 'audio bytes must be identical');
  assert.equal(back.media.find(m => m.id === 'm2').duration, 132.4, 'a 2-minute note must not become 0:00');
});

await testAsync('importing junk fails with a sentence a human can act on', async () => {
  const junk = new TextEncoder().encode('this is not a zip file at all, not even close');
  await assert.rejects(
    () => Store.importBackup(junk.buffer.slice(junk.byteOffset, junk.byteOffset + junk.byteLength)),
    (err) => {
      assert.match(err.message, /Rojni backup/);
      return true;
    });
});

await testAsync('import merges rather than wiping', async () => {
  const before = (await Store.readAll()).entries.length;
  await Store.put(Store.T.ENTRIES, {
    id: 'e9', date: '2026-09-19', createdAt: 9, updatedAt: 9, kind: 'day',
    blocks: [{ t: 'text', text: 'Written after the last backup.' }]
  });
  const out = await Store.exportBackup();
  const zip = new Uint8Array(await out.blob.arrayBuffer());
  await Store.importBackup(zip.buffer.slice(zip.byteOffset, zip.byteOffset + zip.byteLength));
  const after = await Store.readAll();
  assert.ok(after.entries.length >= before + 1, 'an import must never delete what is already there');
  assert.ok(after.entries.find(e => e.id === 'e9'), 'the entry written after the backup is still here');
});

/* ── report ─────────────────────────────────────────────────────── */
console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed ? 1 : 0);
