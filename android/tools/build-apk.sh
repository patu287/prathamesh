#!/usr/bin/env bash
# Build Reset.apk without Gradle / Android Studio.
#
# Needs, on PATH or pointed at by the vars below:
#   AAPT2      android build-tools aapt2
#   ANDROID_JAR android.jar for API 33 (platforms/android-33/android.jar)
#   D8_JAR     d8.jar (build-tools/lib/d8.jar) or r8.jar
#   JAVAC_JAR  ecj.jar (Eclipse compiler) — or set JAVAC=javac to use a real JDK
#   JAVA       a JRE 8+
#   python3 with the `cryptography` package (for tools/mkapk.py)
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
out="${OUT:-$root/build-apk}"

AAPT2="${AAPT2:-aapt2}"
JAVA="${JAVA:-java}"
ANDROID_JAR="${ANDROID_JAR:?set ANDROID_JAR to an android.jar}"
D8_JAR="${D8_JAR:?set D8_JAR to d8.jar/r8.jar}"
JAVAC_JAR="${JAVAC_JAR:-}"

rm -rf "$out"; mkdir -p "$out"/{compiled,gen,classes,dex,assets}
cp "$root/reset/index.html" "$out/assets/index.html"

# 1. resources
"$AAPT2" compile --dir "$root/android/app/src/main/res" -o "$out/compiled/res.zip"

# 2. manifest + resources + assets -> base.apk (+ generated R.java)
"$AAPT2" link -o "$out/base.apk" -I "$ANDROID_JAR" \
  --manifest "$here/AndroidManifest.aapt.xml" \
  -A "$out/assets" --java "$out/gen" \
  --min-sdk-version 24 --target-sdk-version 33 \
  --version-code 1 --version-name 1.0 "$out/compiled/res.zip"

# 3. java -> classes
srcs="$root/android/app/src/main/java/app/reset/MainActivity.java $out/gen/app/reset/R.java"
if [ -n "$JAVAC_JAR" ]; then
  "$JAVA" -jar "$JAVAC_JAR" -source 1.7 -target 1.7 -nowarn \
      -bootclasspath "$ANDROID_JAR" -d "$out/classes" $srcs
else
  "${JAVAC:-javac}" -source 8 -target 8 -bootclasspath "$ANDROID_JAR" -d "$out/classes" $srcs
fi

# 4. classes -> dex
"$JAVA" -cp "$D8_JAR" com.android.tools.r8.D8 --release --min-api 24 \
  --lib "$ANDROID_JAR" --output "$out/dex" $(find "$out/classes" -name '*.class')

# 5. package + zip-align + sign (v1 + v2)
python3 "$here/mkapk.py" "$out/base.apk" "$out/dex/classes.dex" \
  "$root/reset/Reset-1.0.apk" "$root/android/keys"

echo "-> $root/reset/Reset-1.0.apk"
