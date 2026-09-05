# Reset — Android app

A ~35 KB WebView wrapper around `reset/index.html`. No permissions (not even
INTERNET), no dependencies, no analytics. The page is served from the virtual
origin `https://appassets.androidplatform.net/assets/index.html`, which is
intercepted locally by `MainActivity`, so the page gets a stable web origin and
`localStorage` keeps your messages, sessions and streak forever.

| | |
|---|---|
| Package | `app.reset` |
| min SDK | 24 (Android 7.0) |
| target SDK | 33 |
| Signature | v1 (JAR) + v2 (APK Signature Scheme v2), self-signed |
| Prebuilt | [`../reset/Reset-1.0.apk`](../reset/Reset-1.0.apk) |

## Install the prebuilt APK

1. Copy `reset/Reset-1.0.apk` to the phone (USB, Drive, Telegram to yourself…).
2. Tap it. Android will ask to allow installs from that app — allow it once.
3. "Install anyway" on the Play Protect warning (it's just an unknown signer).

## Rebuilding

**With Android Studio / Gradle** (normal path):

```bash
cd android
cp ../reset/index.html app/src/main/assets/index.html   # keep assets in sync
gradle assembleDebug      # or: open the android/ folder in Android Studio and Run
```

**With CI**: copy `ci/android-apk.yml` to `.github/workflows/android-apk.yml`,
push, and download the `reset-apk` artifact from the Actions run.

**Without the Android SDK** (how `Reset-1.0.apk` was actually produced):
`tools/mkapk.py` takes an `aapt2 link` output plus a `classes.dex` and produces a
zip-aligned, v1+v2-signed APK using only Python (`cryptography`). See the header
of that file. Re-signing with the key in `keys/` is what lets a new build install
*over* an existing one.

## Signing key

`keys/reset.key.pem` + `keys/reset.cert.pem` are a throwaway self-signed
sideloading key, committed on purpose so future builds can update the installed
app in place. It is **not** a Play Store upload key — if this app ever goes to a
store, generate a fresh key and keep it out of Git.
