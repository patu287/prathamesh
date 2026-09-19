# Notes — Android app

A single-Activity WebView wrapper around [`../notes`](../notes). No dependencies beyond
one androidx class, no analytics, no network code — and **no `INTERNET` permission at
all**, so the app cannot phone home even if a future edit told it to.

The page is served from the virtual origin
`https://appassets.androidplatform.net/assets/index.html`, intercepted locally by
`MainActivity`, rather than from `file://`. That is not a nicety: a `file://` page gets no
IndexedDB, no Web Crypto, and data that the system treats as a cache and evicts. The
virtual HTTPS origin is what makes the journal persistent.

| | |
|---|---|
| Package | `app.notes` |
| Label | Notes |
| min SDK | 24 (Android 7.0) |
| target SDK | 34 |
| Permissions | `RECORD_AUDIO` — **one**, and only that |
| Signature | v1 (JAR) + v2, self-signed with the committed key in `keys/` |
| APK | [`../notes/release/Notes-1.0.apk`](../notes/release/) |

## Install

1. Get `Notes-1.0.apk` onto the phone (USB, Drive, Telegram to yourself…). The committed
   build is `notes/release/Notes-1.0.apk` — 257 KB, signed, installable as-is.
2. Tap it. Android will ask to allow installs from that app — allow it once.
3. "Install anyway" on the Play Protect warning. That warning is about the unknown
   signer, not about the app.

Because the signing key is committed, later builds install **over** the existing one.
That matters more here than anywhere else in this repo: uninstalling to fix a signature
mismatch would take the journal with it.

## The permission, stated honestly

`RECORD_AUDIO` is the only one. Voice notes are a first-class kind of entry in Notes, not
an attachment, so there is no version of this app that works without it — but note what is
*absent*:

| Not requested | Why it isn't needed |
|---|---|
| `INTERNET` | The app never talks to anything. Not "does not" — cannot. |
| `CAMERA` | Taking a photo delegates to the system camera app via `ACTION_IMAGE_CAPTURE`. Declaring `CAMERA` would make it *mandatory*; the camera app already holds it. |
| `WRITE_EXTERNAL_STORAGE` / `READ_MEDIA_IMAGES` | Photos come in through `ACTION_GET_CONTENT`, where the system grants read access to the single file the user picked. Backups go out through a save dialog the user points at a folder. Neither needs a broad grant. |

This is a real tradeoff against [`../android`](../android), whose Reset app proudly declares
zero permissions. Notes cannot — so it says so on the tin instead of hiding it.

## Three things that fail silently in a WebView

Every one of these produces *no error, no prompt, no log* — just a button that does
nothing, which is indistinguishable from a bug in the page. All three are handled here
because there is no way to notice them from the outside.

**1 · File choosers** — an `<input type="file">` does nothing at all when tapped unless
`WebChromeClient.onShowFileChooser` is implemented. That is why the wardrobe app has one,
and why this one does too. Two details worth keeping:

- A pending `ValueCallback` must **always** be answered, including with `null`. If it is
  dropped, the page's input stays locked and *every later tap is ignored too*.
- `capture="environment"` sets `FileChooserParams.isCaptureEnabled()`, which is how the
  page asks for "take a photo now" rather than "pick a file". That path goes through
  `ACTION_IMAGE_CAPTURE` with a `FileProvider` URI — a `file://` URI throws
  `FileUriExposedException` on every version this app supports — and silently falls back
  to the picker if the phone has no camera app.

**2 · The microphone** — `getUserMedia` is refused with no prompt and no error unless
`onPermissionRequest` is implemented *and* the app holds `RECORD_AUDIO`. So the request is
held open while the Android permission dialog runs, then granted or denied honestly, and a
denial gets a visible explanation instead of a dead record button. (`onPermissionRequest`
is never called on a `file://` page at all — another reason for the virtual origin.)

**3 · Saving a backup** — `<a download>` is **ignored for `blob:` URLs** in a WebView. The
export would appear to work and write nothing, which for a journal is the worst possible
bug: you would find out the day you needed the file. So when the app is running inside the
shell, `#exportBtn` hands the finished bytes to `NotesNative.saveFile()` over a
`@JavascriptInterface` bridge, and the shell opens a system save dialog
(`ACTION_CREATE_DOCUMENT`) — which also means no storage permission, on any Android
version, and the user chooses the folder.

`<a download>` on an `http(s)` URL *does* work, but the page is offline by design, so
there is nothing to point it at.

## Rebuilding

The APK that ships with this repo (`notes/release/Notes-1.0.apk`) was built **without the
Android SDK, without Gradle and without Maven** — every input is either Python, a jar from
npm/PyPI, or a git clone. `tools/build-apk.sh` does all six stages:

```bash
cd notes-android
AAPT2=/path/to/aapt2 \
JAVAC_JAR=/path/to/tools.jar \
DX_JAR=/path/to/dx.jar \
ANDROID_JAR=/path/to/android-34/android.jar \
JAVA=/path/to/jre/bin/java \
./tools/build-apk.sh          # -> ../notes/release/Notes-1.0.apk
```

| Stage | Tool | Where it comes from |
| --- | --- | --- |
| 1 | shell | copies `../notes/{index.html,styles.css,app.js,data.js,store.js}` + `fonts/` into `assets/` |
| 2 | `aapt2 compile` | PyPI `aapt2` (a bundled 6 MB native binary) |
| 3 | `aapt2 link` | same binary; links `tools/AndroidManifest.aapt.xml` + `assets/` + `res/` |
| 4 | `com.sun.tools.javac.Main` | npm `dataslope-tools-jar` (OpenJDK 8 `tools.jar`, 17.5 MB) |
| 5 | `com.android.dx.command.Main` | AOSP `dalvik/dx` sources, compiled with the same javac — see below |
| 6 | `tools/mkapk.py` | pure Python + `cryptography`: zips, aligns, signs v1 **and** v2 |

A JRE is only needed as a runner (`jdk4py` on PyPI ships one), and `android.jar` can be
cloned from `Sable/android-platforms`: `git clone --depth 1 --filter=blob:none --sparse`,
then `git sparse-checkout set android-34`.

### Dexing without d8

The Android SDK's `d8.jar` was not available here — and npm's `d8-termux`, despite its
name, is a *dalvik* `classes.dex` masquerading as a jar, so it cannot run on a desktop JVM
(`Could not find or load main class com.android.tools.r8.D8`). The way out is `dx`, the
dexer d8 replaced: it is pure Java, self-contained, and its source is in the AOSP mirror.

```bash
git clone --depth 1 --branch pie-qpr3-release --filter=blob:none --sparse \
    https://github.com/aosp-mirror/platform_dalvik /tmp/dalvik
cd /tmp/dalvik && git sparse-checkout set dx
find "$PWD/dx/src" -name '*.java' > /tmp/dx-srcs.txt
java -cp tools.jar com.sun.tools.javac.Main -nowarn -source 7 -target 7 \
  -bootclasspath android.jar -d /tmp/dx-classes @/tmp/dx-srcs.txt   # 609 classes
java -cp tools.jar sun.tools.jar.Main cf dx.jar -C /tmp/dx-classes .
```

`-source 7` is not cosmetic: with `-source 8` this javac build (1.8.0_131) dies on
`annotationType(): unrecognized Attribute name MODULE` while reading `android.jar`. dx is
Java 7 code, so targeting 7 is honest *and* it sidesteps the crash. dx then emits dex
format 037, which needs minSdk 24 — exactly what the manifest declares.

### Verifying the result

`tools/verify-apk.py` re-derives both signatures from their specs (it shares no code with
the signer, so a bug there cannot hide):

```bash
python3 tools/verify-apk.py ../notes/release/Notes-1.0.apk keys/notes.cert.pem
```

It checks the v1 digests chain (`MANIFEST.MF` → entries, `CERT.SF` → manifest, PKCS#7
signature), the v2 content digest over the three sections, the embedded certificate, the
4-byte DATA alignment of every STORED entry, and that the dex carries `MainActivity`, the
appassets start URL, and no leaked `com/android/dx` classes.

**With Android Studio / Gradle:** the Gradle project is still here and still valid —

```bash
cd notes-android
mkdir -p app/src/main/assets/fonts
cp ../notes/{index.html,styles.css,app.js,data.js,store.js} app/src/main/assets/   # keep assets in sync
cp ../notes/fonts/*.woff2 app/src/main/assets/fonts/
gradle assembleRelease
```

**With CI:** `ci/notes-apk.yml` is the Gradle workflow (ubuntu-latest), kept out
of `.github/workflows/` on purpose — the GitHub account that maintains this repo has no
`workflows` permission, so pushing that path is rejected. To use it, copy the file to
`.github/workflows/notes-apk.yml` from the GitHub web UI (uploading through the browser
works where `git push` does not).

## Launcher icon

`tools/make_icons.py` rasterises the five legacy mipmap densities with no image tooling —
the glyph is drawn directly as shape coverage, supersampled 3×3 per pixel. A page with two
indigo lines and one amber line: the sentence that got promoted to a key point. API 26+
uses the adaptive icon in `mipmap-anydpi-v26` with the matching vector foreground.

```bash
python3 tools/make_icons.py
```

The colours live in both the Python and the vector drawable. Change one, change both.

## Signing key

`keys/notes.keystore` (PKCS12, password `notes`, alias `notes`) is a throwaway
self-signed sideloading key, committed **on purpose** so future builds can update the
installed app in place rather than forcing an uninstall that would destroy the journal.
It is not a Play Store upload key — if this app ever goes to a store, generate a fresh key
and keep it out of Git.
