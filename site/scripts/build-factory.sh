#!/bin/sh
set -eu
PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UNITY_EDITOR=${UNITY_EDITOR:-/Applications/Unity/Hub/Editor/6000.3.22f1/Unity.app/Contents/MacOS/Unity}
mkdir -p "$PROJECT_ROOT/tmp"
"$UNITY_EDITOR" -batchmode -projectPath "$PROJECT_ROOT/OchakovoFactoryWorld" -buildTarget WebGL -executeMethod FactoryBuilder.BuildWeb -quit -logFile "$PROJECT_ROOT/tmp/factory-webgl.log"

mkdir -p "$PROJECT_ROOT/web/public/unity"
cp -R "$PROJECT_ROOT/OchakovoFactoryWorld/Builds/WebGL/." "$PROJECT_ROOT/web/public/unity/"
