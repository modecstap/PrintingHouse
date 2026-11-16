#!/usr/bin/env bash
# Run backend lint gates: pylint (score 10/10), then isort/black check, then mypy.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-$ROOT}"

RCFILE="${ROOT}/.pylintrc"
TEST_DISABLE=(
  missing-module-docstring
  missing-function-docstring
  missing-class-docstring
  protected-access
  too-many-public-methods
)
TEST_DISABLE_CSV="$(IFS=,; echo "${TEST_DISABLE[*]}")"

echo "==> pylint (backend, excluding tests)"
pylint --rcfile="${RCFILE}" \
  --ignore-paths='^backend/test/' \
  backend

echo "==> pylint (backend/test, relaxed)"
pylint --rcfile="${RCFILE}" \
  --disable="${TEST_DISABLE_CSV}" \
  backend/test

echo "==> isort check"
isort --check-only --diff backend

echo "==> black check"
black --check backend

echo "==> mypy"
mypy backend

echo "All backend lint checks passed."
