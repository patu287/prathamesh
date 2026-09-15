# My Wardrobe — Android

A native Android shell for the offline web app in [`almari/`](../almari/). One
`WebView`, no backend, **zero permissions** — not even `INTERNET`. The whole
wardrobe, its photos and its outfits live in the app's private IndexedDB on the
device.

The finished, signed APK is produced by CI and attached to the workflow run as
a downloadable artifact: **Actions → "Build My Wardrobe APK" → latest run →
Artifacts → `my-wardrobe-apk`** (contains `MyWardrobe-1.0.apk`).

## Installing

1. Download `MyWardrobe-1.0.apk` from the workflow artifact (or build it below).
2. Move it to the phone and tap it. Android will say *“install unknown apps”* —
   allow it for your file manager / browser once, then install.
   (`adb install MyWardrobe-1.0.apk` works too.)
3. Open **My Wardrobe**. Everything is on-device; airplane mode changes nothing.

Updates install in place over the old version, because every build is signed
with the same committed key (see *Signing*).

## What the wrapper does

`app/src/main/java/app/wardrobe/MainActivity.java` is the entire app:

- **Serves `almari/` from a real origin.** Requests to
  `https://appassets.androidplatform.net/assets/…` are answered locally from the
  APK's assets by a `WebViewClient` interceptor. A real origin (not `file://`)
  is what lets IndexedDB and `localStorage` persist the wardrobe and its photos
  across restarts *and* across app updates.
- **Makes photos work.** The `WebChromeClient.onShowFileChooser` hook turns the
  page's `<input type="file">` into a system chooser (`ACTION_GET_CONTENT`,
  `image/*`), which reaches the gallery *and* the camera. Without that override
  a file input in a WebView silently does nothing — that is the bug this wrapper
  exists to avoid. The result URI is handed back through the file_callback,
  including multi-select (`clipData`).
- **Stays offline.** `shouldInterceptRequest` answers only the app's own host;
  anything else simply fails. There is no network code path at all.
- **Looks native.** Window, status and navigation bars are set to the Dusk
  theme's `--bg` (`#131110`) so there is no white flash on launch; back navigates
  web history before exiting; DOM storage, hardware acceleration and the
  lifecycle (`onPause`/`onResume`/`onDestroy`) are wired up.

### Permissions

The manifest declares **none**. Photo picking needs no permission because
`ACTION_GET_CONTENT` grants the app read access to exactly the one URI the user
chose, for that one request. Camera access is delegated to whatever camera app
the chooser offers. Nothing is uploaded anywhere — there is no `INTERNET`
permission to upload with.

## Building it yourself

There is no Gradle wrapper checked in; any Gradle 8.7 + JDK 17 will do.

```bash
# 1. put the web app into assets (CI does this too)
mkdir -p app/src/main/assets
for f in index.html styles.css app.js data.js store.js; do
  cp ../../almari/$f app/src/main/assets/
done

# 2. build the signed release APK
gradle assembleRelease          # or: ./gradlew, if you prefer a wrapper

# → app/build/outputs/apk/release/app-release.apk
```

`minSdk 24` (Android 7.0), `targetSdk 34`. The APK is a few hundred KB: the
wrapper has no dependencies beyond the framework.

GitHub Actions builds it on every push touching `wardrobe-android/**`,
`almari/**` or the workflow itself. The workflow lives at
[`ci/wardrobe-apk.yml`](ci/wardrobe-apk.yml); see *Activating CI* below.

## Activating CI

The account this sandbox pushes with is not allowed to create files under
`.github/workflows/` (GitHub blocks workflow changes from apps without the
`workflows` permission), so the workflow is kept here and activated once, by
you, from a machine that can push workflows:

```bash
git pull
mkdir -p .github/workflows
cp wardrobe-android/ci/wardrobe-apk.yml .github/workflows/
git add .github/workflows/wardrobe-apk.yml
git commit -m "Activate My Wardrobe APK workflow"
git push
```

(Same thing in the GitHub web UI: *Add file → Create new file*, name it
`.github/workflows/wardrobe-apk.yml`, paste the contents of
`wardrobe-android/ci/wardrobe-apk.yml`.) From then on every push that touches
the wrapper or `almari/` produces a fresh `MyWardrobe-1.0.apk` artifact, and the
Actions tab has a *Run workflow* button for building on demand.

## Signing

`keys/wardrobe.keystore` (PKCS#12, alias `wardrobe`, password `wardrobe`) is
**committed on purpose**. A throwaway sideload key kept outside the repo would
mean the next person who builds produces an APK that cannot update yours
(signature mismatch → forced uninstall → the wardrobe inside it gone). With the
key in the repo, every build from anywhere installs cleanly over the last one.

It is *not* a Play Store upload key and grants nothing remote: the APK is signed
locally, the key cannot decrypt anyone's data, and the app talks to no server.
If this ever ships to Play, generate a real upload key there and keep this one
for sideloading only.

Regenerate (only if you accept that older installs must be uninstalled first):

```bash
openssl req -x509 -newkey rsa:2048 -keyout keys/wardrobe.key.pem \
  -out keys/wardrobe.cert.pem -days 10000 -nodes \
  -subj "/CN=My Wardrobe/O=Personal/C=IN"
openssl pkcs12 -export -in keys/wardrobe.cert.pem -inkey keys/wardrobe.key.pem \
  -out keys/wardrobe.keystore -name wardrobe -passout pass:wardrobe
```

## Launcher icon

Adaptive (API 26+): `mipmap-anydpi-v26/ic_launcher*.xml` + the vector hanger in
`drawable/ic_launcher_foreground.xml`, gold on Dusk. Legacy (API 24–25): the
PNGs in `mipmap-*/` are generated, not drawn by hand — rerun
`python3 tools/make_icons.py` after touching the vector to keep them in sync.

## Layout

```
wardrobe-android/
├── settings.gradle / build.gradle / gradle.properties
├── app/
│   ├── build.gradle                     # namespace app.wardrobe, release signing
│   └── src/main/
│       ├── AndroidManifest.xml          # no permissions
│       ├── java/app/wardrobe/MainActivity.java
│       ├── assets/                      # filled from ../../almari at build time
│       └── res/                         # icon, theme, strings
├── keys/                                # committed sideload signing key
└── tools/make_icons.py                  # legacy PNG launcher icons
```
