# Source this from anywhere in the repo:  . tools/env.sh
# Everything it points at lives under .tools/ and is safe to delete.
TVOS_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)

export JAVA_HOME="$TVOS_ROOT/.tools/jdk-17/Contents/Home"
export ANDROID_HOME="$TVOS_ROOT/.tools/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export ANDROID_USER_HOME="$TVOS_ROOT/.tools/android-home"
export ANDROID_AVD_HOME="$TVOS_ROOT/.tools/avd"
export ANDROID_EMULATOR_HOME="$TVOS_ROOT/.tools/android-home"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

mkdir -p "$ANDROID_USER_HOME" "$ANDROID_AVD_HOME"

if [ ! -x "$JAVA_HOME/bin/java" ] || [ ! -x "$ANDROID_HOME/platform-tools/adb" ]; then
  echo "Local toolchain missing. Expected .tools/jdk-17 and .tools/android-sdk; see GUIDE.md." >&2
fi
