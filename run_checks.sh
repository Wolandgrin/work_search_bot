#!/usr/bin/env bash
# Wrapper - delegates to run_checks.py (runs all checks, reports summary)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec "${PYTHON:-python3}" "$SCRIPT_DIR/run_checks.py" "$@"
