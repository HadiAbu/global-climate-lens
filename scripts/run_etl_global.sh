#!/usr/bin/env bash
set -euo pipefail

WORKDIR="$(pwd -W)"

docker run --rm -it \
  -v "$WORKDIR":/work \
  -w /work \
  python:3.12-slim \
  bash -lc "pip install -q pandas && python etl/01_global_etl.py"