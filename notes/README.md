# Notes — the day, kept

A private, offline, local-first journal. Write the day, record the days you can't
write, keep photos, and distil the few **key points** that matter across the aspects
of your life.

**Nothing ever leaves the device.** No account, no server, no analytics, no network
calls at runtime. Same architecture as [`../almari`](../almari): plain HTML/CSS/vanilla
JS, no build step, IndexedDB for records and media Blobs. It drops into a WebView shell
as-is, the same way [`../android`](../android) wraps the Reset app.

> The app is called **Notes**; the folder is `notes/`, the Android shell is
> `notes-android/`, and the APK lands in `notes/release/`.
>
> The IndexedDB database is still named `rojni` internally — this app's original name —
> exactly the way `almari`'s database is still called `almari`. Renaming the thing that
> holds your data would orphan every entry already on a device, so only the parts a human
> reads were renamed. Backups exported under the old name still import; the format is
> identical and both labels are accepted.

## Run it

```bash
cd notes
python3 serve.py 8090           # threaded, HTTP/1.1, cache-disabled — best for iterating
python3 serve.py 8081 release   # the built artifacts: Notes.html and the APK
# → http://localhost:8090
```

Fonts are bundled in `fonts/` (SIL OFL) rather than fetched from a CDN, because the
Android build has no `INTERNET` permission — a Google Fonts link could only ever fail
there. Side effect: the app now makes **no external requests at all**, in any context,
which is what the rest of this file already claimed.

Serve it over http when you mean to record. On `file://` there is no IndexedDB (media
falls back to localStorage and fills up almost immediately) and no
`navigator.mediaDevices` — the mic button then does nothing at all, silently. Where a
browser blocks storage *entirely*, the app now keeps working in memory and says so in
Settings rather than failing to open; that was a real boot failure until the single-file
test below caught it.

### One file

```bash
python3 tools/build-single.py    # → release/Notes.html   (~380 KB)
```

Folds the whole app into one self-contained HTML file: the stylesheet, `data.js`,
`store.js`, `app.js` and all eight woff2 fonts are inlined, so the result has **no
subresources and makes no network requests at all**. Nothing is minified — the file stays
readable. The script refuses to write if any `src`/`href`/`@import`/`url(fonts/…)` escapes
inlining, and refuses if any of the shipped JavaScript so much as mentions a URL.

That file is what you open from a phone's Downloads folder. Text and photos work; audio
recording needs a real origin, so serve the folder (or use the APK) when you want to talk
instead of type.

### Tests

```bash
cd notes/test && npm install && npm test
```

Three suites, kept out of the app folder because the app itself has no dependencies and
should stay that way:

| Suite | What it covers |
|---|---|
| `test/smoke.mjs` | Pure logic in a bare Node context with **no DOM and no IndexedDB** — so everything runs through the localStorage fallback, the path that silently corrupts because a Blob JSON-serialises to `{}`. Includes the backup round trip, verified byte-for-byte. |
| `test/dom.mjs` | Drives the real app in jsdom against a real IndexedDB: writes an entry, promotes a sentence to a key point, files it under an aspect, runs the weekly review, searches, then **restarts the app and checks the journal is still there**. Point it at the built artifact with `NOTES_PAGE=/release/Notes.html` to run the same 37 checks against the single file. |
| `test/single.mjs` | Builds `release/Notes.html`, asserts it is genuinely self-contained, then opens it the way a phone would — as a **local file, with no IndexedDB and no network** — and checks the app still boots and tells the truth about storage. |

`test/dom.mjs` paid for itself immediately. It found a data-loss bug on its first run:
a key point promoted from a sentence was pushed to memory but never written to storage,
so it appeared in the Aspects view and vanished on reload. No in-memory assertion could
have caught that — only a restart could.

The ZIP writer is also verified by an external tool, not just by its own reader:

```bash
unzip -t notes-backup-2026-09-19.zip     # → No errors detected
unzip -l notes-backup-2026-09-19.zip     # → journal.json, media/m1.jpg, media/m2.webm
```

---

## What's built

**Your two features, joined into one loop**

- **Daily journal** — the day is a *container*, not a page. Several entries per day
  (morning pages, a mid-afternoon voice memo, a 9pm note), each a block stack under a
  date heading. A block is text, a quote, a photo or a voice note, in any order.
  Autosave, no Save button, zero required fields. `Enter` at the end of a line opens a
  new block; mid-line it makes a paragraph.
- **Key points across life aspects** — the Aspects tab is a *lens over your own writing*,
  not a second inbox you have to feed. The headline interaction: **highlight a sentence
  in an entry → "→ Key point"**. It becomes a labelled quote block in the entry *and* a
  key point filed under that entry's aspects. Also writable directly from an aspect page,
  and the third answer of every weekly review becomes one automatically.
- **Aspect scorecards** whose most useful number is not a chart: *"Health — last touched
  12 days ago."* Plus entries / words / key points / average mood, a 12-month attention
  bar, and a **Big Rocks** flag. Today then opens with the honest comparison: *"you're
  spending your words on Work, and Health is a big rock that's been 12 days."*

**Capture**

- **Voice notes as a first-class entry kind**, not an attachment — record in one tap, live
  level meter, waveform drawn from peaks decoded at save time, playback speed control, and
  **playback position remembered** (a 40-minute memo is unusable otherwise). Audio and text
  can sit on the same entry, so you can listen and write your own summary later.
- **Photos** — camera or gallery, multi-select, downscaled to ≤1400px JPEG q0.80 at save
  time with a 320px thumbnail. EXIF capture date is read *before* the re-encode and offered
  as the entry date; the re-encode then strips EXIF entirely, GPS included.
- **Prompts** — 50 offline prompts, another one on tap, and "write on this" turns the
  question into the entry's heading.
- **Mood + energy** — two optional taps, no keyboard. They are what makes "your mood when
  writing about Health: 3.1/5" possible a year later.

**Read it back**

- **Today** — heading, a quiet 60-day consistency grid, **on this day** (a month / three
  months / six months / a year / two years ago), today's entries, a prompt, and the big-rock note.
- **Timeline** — everything, grouped by day, filterable by aspect and by voice / photos /
  key points / reviews.
- **Search** — entries, key points, aspect names, month names, raw dates. Debounced full
  scan; no inverted index, because a few thousand records scan in single-digit milliseconds.
- **Weekly review** — the week's entries as cards, three fixed questions
  (*what mattered · what drained me · one thing for next week*). Saves as a `review` entry.
  This is the habit that keeps key points coming; without it they accumulate once and die.
- **Random old page** — one button, one old entry.

**Keeping it**

- **Export** → a real ZIP: `journal.json` beside a `media/` folder of actual `.webm` and
  `.jpg` files. Store-only, hand-rolled, ~80 lines, no dependency. Not a database dump —
  formats that will still be readable in twenty years, by something that isn't this app.
- **Import** merges rather than wipes, and reports what it couldn't find.
- `navigator.storage.persist()` is requested on the first saved entry, not when storage is
  already full. Storage meter and persistence state are shown in plain words, including the
  bad news.
- **PIN gate** (off by default). The UI says plainly that it is a *gate, not a lockbox*: it
  stops someone who picks up your unlocked phone and nothing more.
- **Android app** — [`notes-android/`](../notes-android): a single-WebView shell that serves
  the page from `https://appassets.androidplatform.net` (intercepted locally, never the
  network), holds **exactly one permission** — the microphone, so voice notes exist — and
  declares no `INTERNET` at all. See its README for the three things that fail *silently*
  in a WebView without explicit handling: file choosers, microphone grants, and
  `<a download>` on a blob URL.

## What's not built

Honest list, roughly in the order I'd do them:

1. **Encryption.** AES-GCM + passphrase. Deliberately not rushed into v1: lose the
   passphrase and the journal is gone forever, which is a real commitment, not a checkbox.
2. **Audio transcription.** Reliable on-device STT does not exist in a WebView without a
   backend. The v1 answer is the honest one — audio *and* text on the same entry. Cloud
   transcription would mean uploading your journal, which breaks the entire premise.
3. **People tags** (`Mom`, `Rahul`). Journals are mostly about people. A third axis, so it
   earns its place after v1 rather than crowding it.
4. **Native quick capture** and an Android share-sheet target.
5. Cost-per-attention charts, chapters, printable year book. Fun, not load-bearing.

---

# Why it's designed this way

The rest of this file is the reasoning. It is the part worth arguing with.

## The one opinion that matters

**You described two features. Do not build two features.**

If the daily journal and the life-aspects grid are separate screens with separate data,
you will use one of them and abandon the other. Guaranteed. Two silos in one app is just
two apps. What works is a single loop:

```
   write the day ──▶ highlight a sentence ──▶ it becomes a Key Point
        ▲                                          │
        │                                          ▼
        └──── the Aspects view shows it back ◀─────┘
              ("Health: last touched 12 days ago")
```

The entry is the raw material; the aspect view is derived from it.

## The second: friction is the only competitor that matters

Not Day One, not Notion, not Apple Journal — apathy and the phone lock screen. The app you
actually keep is the one you can use one-handed in 20 seconds, lights off, half-asleep.
Hence: one big `+`, zero required fields, no Save button, a one-line day is enough, a voice
memo is enough, voice is an entry kind rather than an attachment, and never a form.

## The third: streaks are a trap for journals

A streak counter is a guilt machine: it produces fake entries, then a broken streak, then
abandonment. You cannot be honest in a place that is disappointed in you. So: a quiet month
grid showing days written / with audio / with a photo, and an *attention* read per aspect.
Nudge on substance, never on compliance. (There is a test asserting the word "streak"
appears nowhere in the UI.)

## The fourth: a journal you can lose is not a journal

Whatever else gets cut, export and persistence do not. That is why they are in v1 and
tested rather than on a roadmap.

---

## Data model

```js
/* Entry — one thought, one voice memo, one photo dump. Several per day. */
{
  id: 'e…', date: '2026-09-19',      // LOCAL date key, never a UTC timestamp
  createdAt: 1757…, updatedAt: 1757…,
  kind: 'day' | 'review',
  title: '',                          // optional; reviews and prompts set it
  blocks: [                           // ordered — this is what makes it feel like paper
    { t: 'text',  text: '…' },
    { t: 'photo', media: 'm…' },
    { t: 'audio', media: 'm…' },
    { t: 'quote', text: '…', keyPointId: 'k…' }   // the promoted sentence
  ],
  mood: 3, energy: 4,                 // 1–5, both optional
  aspects: ['health', 'work'],
  place: ''
}

/* Media — its own table, so a 40 MB recording is never loaded to render a date. */
{
  id: 'm…', entryId: 'e…', type: 'audio' | 'image',
  blob: Blob,
  mime: 'audio/webm;codecs=opus',
  duration: 412.6,        // seconds — TIMED while recording, never read off the blob
  thumb: Blob | null,     // ~320px JPEG, images only
  peaks: [0…255, …],      // 64 buckets, decoded once at save, drawn forever
  width, height, origDate, createdAt
}

/* KeyPoint — the payload of the second feature. Outlives the entry that made it. */
{
  id: 'k…', text: 'I write badly when I write at midnight.',
  aspects: ['work', 'inner'], date: '2026-09-19',
  sourceEntryId: 'e…' | null, pinned: false, status: 'open' | 'done' | 'dropped'
}

/* Aspect */
{ id: 'health', name: 'Health', glyph: '◍', color: '#4c7a63', order: 0,
  bigRock: true, focus: [{ text: 'walk daily', done: false, addedAt: 1757… }], archived: false }

/* Meta — { key, value } rows, normalised to a plain object on read */
{ key: 'pin' | 'persist' | 'sessionDays' | 'lastBackup', value: … }
```

Default aspects live in one array at the top of `data.js`:
**Health · Work · Money · Relationships · Learning · Inner life · Home · Play.**
Edit that list to your own life. Rename, reorder, add and archive inside the app too.

### Three model decisions worth defending

**`date` is a local-date string, never a timestamp.** An 11:40pm entry must land on today,
not tomorrow. Deriving the day key from a UTC instant is a bug class that shows up in every
journal app on earth and stays invisible until someone in IST writes at midnight. There is
a test for exactly that.

**Media is its own table.** Blobs inside the entry record means every timeline render pulls
40 MB through structured clone. `thumb` and `peaks` exist for the same reason: decode once
at save, render forever from the small copy.

**`kind` is tiny, and there is no `tags` field.** The only distinction that changes
behaviour is day entry vs. weekly review. Anything else is a filter, and filters are search.

---

## Audio: the parts that bite

- **`MediaRecorder` blob duration is often `Infinity`.** Chrome's WebM output frequently
  omits the duration from the header. So the app runs its own timer while recording and
  stores the elapsed seconds — waveform scaling, the progress bar and position memory all
  depend on that number being right.
- **Never hardcode a MIME type.** `MediaRecorder.isTypeSupported()` is probed in order:
  `audio/webm;codecs=opus` → `audio/webm` → `audio/ogg;codecs=opus` → `audio/mp4`.
  Android Chrome gives webm/opus, Safari gives mp4. Both are stored and played back through
  `URL.createObjectURL`.
- **Record small on purpose.** `audioBitsPerSecond: 32000`, mono, echo cancellation and
  noise suppression on: ~4 KB/s ≈ 240 KB per minute, and for speech it is indistinguishable.
- **Revoke every object URL.** A long timeline that leaks hundreds of decoded audio blobs is
  a memory leak you only notice on a phone, three months in — `UrlCache` exists for that.
- **In a WebView, `getUserMedia` fails silently.** `MainActivity` must implement
  `WebChromeClient.onPermissionRequest` and grant `RESOURCE_AUDIO_CAPTURE`, or you get no
  prompt, no error, just a dead button. The recorder surfaces that case in words rather than
  doing nothing.

## Photos

Downscale to ≤1400px and re-encode to JPEG q0.80 at save time (~150–300 KB), plus a 320px
thumbnail. One step that also strips EXIF — GPS included — so privacy is a side effect of
performance work rather than an extra feature. `DateTimeOriginal` is read from the original
file *before* the strip and offered as the entry date.

---

## Screens

Four tabs. Not five, not six.

| Tab | Job |
|---|---|
| **Today** | write. On-this-day card, prompt shuffle, the one big `+` |
| **Timeline** | read. Reverse-chronological, grouped by day, filterable by aspect and media |
| **Aspects** | the loop. Scorecards, big rocks pinned, key points and focus items per aspect |
| **Search** | find. Text, aspect names, dates |

## Hardening (borrowed from `almari`, all still true)

Three things exist because a preview iframe is a hostile environment and each failure is
*silent* — indistinguishable from a dead button:

- **Capture uses `<label for="…">`, never `input.click()`** — a sandboxed iframe can block a
  scripted file-dialog open; it cannot block a label activating its own control. Both
  `#photoInput` (with `capture="environment"`, so it opens the camera) and `#galleryInput`
  are wired this way, as is backup import.
- **Confirmations are in-app tap-twice, never `window.confirm`** — sandboxed iframes return
  `false` without asking, so anything guarded by it simply never runs.
- **Every runtime error is surfaced in a red banner** via `window.onerror` and
  `unhandledrejection`, and boot is wrapped in try/catch.

Added for this app, because both fail quietly by nature: `navigator.storage.persist()` and
`getUserMedia` each get a visible state in the UI and a sentence explaining what happened.

## Decisions, as taken

| Question | Answer |
|---|---|
| Build pattern | Same local-first, zero-build app + WebView APK as `almari` and `android` |
| Voice or writing first | **Write-first.** The `+` opens the editor; the mic is one tap away inside it |
| Privacy lock | **PIN gate**, labelled honestly as a gate rather than encryption. Encryption is a deliberate v1.5 |
| Aspects | The eight defaults above, to be edited in `data.js` — the app opens onto domains that have to be *yours* or the second feature is dead on arrival |
| Packaging | An installable APK in `notes/release/Notes-1.0.apk`, built from `notes-android/` by `notes-apk.yml` |
