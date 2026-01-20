#!/usr/bin/env bash
set -euo pipefail

echo "This script describes how to place whisper.cpp binary and models locally."
echo "1) Build whisper.cpp and copy the binary to backend/app/models/whisper/main"
echo "2) Download a model, e.g., ggml-base.en.bin to backend/app/models/whisper/ggml-base.en.bin"
echo "3) Optionally set env vars:"
echo "   WHISPER_CPP_BIN=./backend/app/models/whisper/main"
echo "   WHISPER_CPP_MODEL=./backend/app/models/whisper/ggml-base.en.bin"
echo "4) The backend will call the binary with JSON output (-oj) for timestamps."
