#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ADAPTER_DIR="$ROOT_DIR/app/backend/solvers/cpp_adapters"
OUT_DIR="$ROOT_DIR/app/backend/solvers/cpp_executables"
CPP_REPO_DIR="$ROOT_DIR/app/cpp_solver"

# Runtime adapters expect this directory layout.
mkdir -p "$OUT_DIR/Database"

CXX=${CXX:-g++}
CXXFLAGS=(-std=c++17 -O2 -pipe)

"$CXX" "${CXXFLAGS[@]}" "$ADAPTER_DIR/bfs_main.cpp" -o "$OUT_DIR/bfs_solver"
"$CXX" "${CXXFLAGS[@]}" "$ADAPTER_DIR/dfs_main.cpp" -o "$OUT_DIR/dfs_solver"
"$CXX" "${CXXFLAGS[@]}" "$ADAPTER_DIR/iddfs_main.cpp" -o "$OUT_DIR/iddfs_solver"
"$CXX" "${CXXFLAGS[@]}" "$ADAPTER_DIR/idastar_main.cpp" -o "$OUT_DIR/idastar_solver"

# IDA* depends on a precomputed corner PDB file.
if [[ -f "$CPP_REPO_DIR/Database/cornerDepth5V1.txt" ]]; then
  cp "$CPP_REPO_DIR/Database/cornerDepth5V1.txt" "$OUT_DIR/Database/cornerDepth5V1.txt"
else
  echo "Pattern DB file not found at $CPP_REPO_DIR/Database/cornerDepth5V1.txt" >&2
  exit 1
fi

echo "Built C++ solver adapters into $OUT_DIR"
