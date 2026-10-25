#!/bin/sh
set -eu
PUBLISH_FACTORY=false
case "${1:-}" in
  "") ;;
  --publish) PUBLISH_FACTORY=true ;;
  *) echo "Usage: $0 [--publish]" >&2; exit 2 ;;
esac
PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UNITY_EDITOR=${UNITY_EDITOR:-/Applications/Unity/Hub/Editor/6000.3.22f1/Unity.app/Contents/MacOS/Unity}
mkdir -p "$PROJECT_ROOT/tmp"
"$UNITY_EDITOR" -batchmode -projectPath "$PROJECT_ROOT/OchakovoFactoryWorld" -buildTarget WebGL -executeMethod FactoryBuilder.BuildWeb -quit -logFile "$PROJECT_ROOT/tmp/factory-webgl.log"

if [ "$PUBLISH_FACTORY" = true ]; then
  mkdir -p "$PROJECT_ROOT/web/public/unity"
  cp -R "$PROJECT_ROOT/OchakovoFactoryWorld/Builds/WebGL/." "$PROJECT_ROOT/web/public/unity/"
fi
