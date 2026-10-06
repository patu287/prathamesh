/* ══════════════════════════════════════════════════════════════════
   Notes · single-file artifact test

   The other two suites cover the app; this one covers release/Notes.html —
   the way a phone meets it: opened straight from a Downloads folder, with no
   server, no network and, because file:// is an opaque origin, no IndexedDB.

   It builds the artifact first (python3 tools/build-single.py) so it can never
   pass against a stale file that no longer matches the sources.

       node test/single.mjs          # runs from notes/test
   ══════════════════════════════════════════════════════════════════ */

import { execFileSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { JSDOM, VirtualConsole } from 'jsdom';
import { webcrypto, randomFillSync } from 'node:crypto';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const artifact = join(root, 'release', 'Notes.html');

let passed = 0, failed = 0;
const step = (name, ok, extra = '') => {
  console.log(`  ${ok ? '✓' : '✗'} ${name}${extra ? '  → ' + extra : ''}`);
  ok ? passed++ : failed++;
};

/* ── build it, so what is tested is what the sources say today ──────── */
let built = '';
try {
  built = execFileSync('python3', [join(root, 'tools', 'build-single.py')], { encoding: 'utf8' }).trim();
  step('the build script runs', true, built.split('\n').pop());
} catch (err) {
  step('the build script runs', false, String(err.stdout || err.message).slice(0, 200));
}
step('release/Notes.html exists', existsSync(artifact));

const html = existsSync(artifact) ? readFileSync(artifact, 'utf8') : '';

/* ── static promises: nothing to fetch, fonts included ──────────────── */
console.log('\nthe file promises to be self-contained');
const markup = html.replace(/<script>[\s\S]*?<\/script>/g, '').replace(/<style>[\s\S]*?<\/style>/g, '');
const subresources = markup.match(/(?:src|href)="(?!#|data:)[^"]+"/g) || [];
step('no subresource in the markup', subresources.length === 0, subresources.slice(0, 2).join(' '));
step('all 8 fonts inlined as data URIs', (html.match(/data:font\/woff2;base64,/g) || []).length === 8);
step('the three scripts are inline, not linked', (html.match(/<script>/g) || []).length === 3
     && !/<script[^>]+src=/.test(html));
step('no @import and no url(fonts/…) left', !/@import/.test(html) && !/url\((?!data:)/.test(html));
step('no URL at all in the shipped JavaScript',
     !/https?:\/\//.test(html), 'nothing in the file can phone home');

/* ── now open it the way a phone would: as a local file ─────────────── */
console.log('\nopened from the filesystem (no server, no IndexedDB, no mic)');
const problems = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => {
  const m = e.detail?.message || e.message || String(e.detail);
  if (!/scrollTo|Not implemented/.test(m)) problems.push(`${e.type || 'jsdomError'}: ${m}`);
});
vc.on('error', (...a) => problems.push('CONSOLE.ERROR: ' + a.join(' ')));

let dom = null;
try {
  dom = await JSDOM.fromFile(artifact, {
    runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      /* Deliberately NOT injecting fake-indexeddb: this is the file:// path,
         where the browser withholds it, and the app has to cope. */
      Object.defineProperty(w, 'crypto', {
        value: { getRandomValues: a => randomFillSync(a), subtle: webcrypto.subtle }, configurable: true
      });
      w.navigator.storage = {
        estimate: async () => ({ usage: 0, quota: 0 }),
        persist: async () => false, persisted: async () => false
      };
      w.URL.createObjectURL = () => 'blob:stub';
      w.URL.revokeObjectURL = () => {};
      w.HTMLElement.prototype.scrollIntoView = () => {};
    }
  });
} catch (err) {
  step('jsdom can open the file', false, String(err).slice(0, 200));
}

if (dom) {
  await new Promise(r => setTimeout(r, 900));
  const d = dom.window.document;
  const $ = s => d.querySelector(s);
  step('jsdom opens a file:// page', true, dom.window.location.protocol);
  step('the app boots', !$('#app').classList.contains('hidden'));
  step('eight aspects seeded', d.querySelectorAll('.aspect-card').length === 8);
  step('no error banner', $('#errorBanner').classList.contains('hidden'),
       $('#errorBanner').textContent.slice(0, 120));
  step('the consistency grid still renders', d.querySelectorAll('#todayGrid i').length === 60);
  step('the empty state invites one honest line', /one honest line/.test($('#todayEntries').textContent));
  step('the app admits storage is blocked instead of pretending',
       /blocked by this browser/.test($('#backendText').textContent),
       $('#backendText').textContent.slice(0, 90));
  step('nothing tried to load from the network',
       !problems.some(p => /RESOURCE|resource loading/i.test(p)), problems.slice(0, 2).join(' | '));
  step('no script errors on the degraded path', problems.length === 0, problems.slice(0, 2).join(' | '));
}

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed ? 1 : 0);
