#!/usr/bin/env bash
# Build Notes.apk with no Android SDK, no Gradle and no Maven.
#
# Every tool below is obtainable without a package manager that reaches Google:
#
#   AAPT2       PyPI `aapt2`            (a bundled 6 MB native binary)
#   JAVAC_JAR   npm  `dataslope-tools-jar`
#               OpenJDK 8 tools.jar — it contains com.sun.tools.javac.Main, so the
#               compiler itself is a jar you can run on any JVM. It works on a
#               modern JRE as long as -bootclasspath is given explicitly (which it
#               must be anyway: the platform here is android.jar, not rt.jar).
#   JAVA        any JRE 8+  (PyPI `jdk4py` ships one)
#   DX_JAR      AOSP `dx` — built from dalvik/dx sources, see "Dexing without d8"
#               in ../README.md. It turns .class into a classes.dex.
#   ANDROID_JAR Sable/android-platforms  (android.jar, API 34)
#   python3 + cryptography               (tools/mkapk.py signs v1 + v2)
#
#   AAPT2=/path/to/aapt2 \
#   JAVAC_JAR=/path/to/tools.jar DX_JAR=/path/to/dx.jar \
#   ANDROID_JAR=/path/to/android-34/android.jar \
#   ./tools/build-apk.sh
#
# The result is zip-aligned and signed with the committed key in keys/, so a new
# build installs over the previous one instead of demanding an uninstall — which
# for a journal would mean losing everything.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
proj="$(cd "$here/.." && pwd)"
root="$(cd "$proj/.." && pwd)"
out="${OUT:-/tmp/notes-apk-build}"

AAPT2="${AAPT2:-aapt2}"
JAVA="${JAVA:-java}"
JAVAC_JAR="${JAVAC_JAR:?set JAVAC_JAR to a tools.jar containing com.sun.tools.javac.Main}"
DX_JAR="${DX_JAR:?set DX_JAR to a dx.jar (AOSP dalvik/dx, runnable on a desktop JVM)}"
ANDROID_JAR="${ANDROID_JAR:?set ANDROID_JAR to an android.jar (API 34)}"

target="$root/notes/release/Notes-1.0.apk"

echo "== 1/6  sync the web app into assets =="
rm -rf "$out"; mkdir -p "$out"/{compiled,gen,classes,dex,assets/fonts}
for f in index.html styles.css app.js data.js store.js; do
  cp "$root/notes/$f" "$out/assets/"
done
cp "$root/notes/fonts/"*.woff2 "$out/assets/fonts/"
ls -1 "$out/assets" "$out/assets/fonts" | sed 's/^/   /'

echo "== 2/6  compile resources =="
"$AAPT2" compile --dir "$proj/app/src/main/res" -o "$out/compiled/res.zip"

echo "== 3/6  link resources + manifest + assets -> base.apk =="
"$AAPT2" link -o "$out/base.apk" -I "$ANDROID_JAR" \
  --manifest "$here/AndroidManifest.aapt.xml" \
  -A "$out/assets" --java "$out/gen" \
  --min-sdk-version 24 --target-sdk-version 34 \
  --version-code 1 --version-name 1.0 "$out/compiled/res.zip"

echo "== 4/6  compile java =="
srcs="$(find "$proj/app/src/main/java" -name '*.java') $(find "$out/gen" -name 'R.java')"
# shellcheck disable=SC2086
"$JAVA" -cp "$JAVAC_JAR" com.sun.tools.javac.Main \
  -source 8 -target 8 -nowarn -encoding UTF-8 \
  -bootclasspath "$ANDROID_JAR" -d "$out/classes" $srcs
find "$out/classes" -name '*.class' | sed 's|^.*/classes/|   |'

echo "== 5/6  dex =="
# dx (not d8): it is pure Java, so this build needs nothing from the SDK.
"$JAVA" -Xmx2g -cp "$DX_JAR" com.android.dx.command.Main \
  --dex --min-sdk-version=24 --output "$out/dex/classes.dex" "$out/classes"
ls -l "$out/dex"
test -s "$out/dex/classes.dex" || { echo "dexing produced no classes.dex" >&2; exit 1; }

echo "== 6/6  package, zip-align, sign (v1 + v2) =="
mkdir -p "$(dirname "$target")"
python3 "$here/mkapk.py" "$out/base.apk" "$out/dex/classes.dex" "$target" "$proj/keys"

echo
echo "-> $target"
"$AAPT2" dump badging "$target" | head -6
