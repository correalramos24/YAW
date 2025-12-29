#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Enabling environment!"

function ensure_venv ()
{
    # Create virtualenv if missing and activate it
    if [[ ! -d "${PROJECT_ROOT}/.venv" ]]; then
        echo ".venv not found — creating virtualenv..."

        if ! command -v python3 >/dev/null 2>&1; then
            echo "python3 not found in PATH" >&2
            return 1
        fi

        python3 -m venv "${PROJECT_ROOT}/.venv" || {
            echo "Failed to create virtualenv" >&2
            return 1
        }

        "${PROJECT_ROOT}/.venv/bin/python" -m pip install --upgrade pip || {
            echo "Failed to upgrade pip inside virtualenv" >&2
            return 1
        }
        
        # Install my dependencies:
        pip install git+https://github.com/correalramos24/py_utils.git
        
        echo "Virtualenv created at ${PROJECT_ROOT}/.venv"
    fi

    source "${PROJECT_ROOT}/.venv/bin/activate"
}

# Ensure and activate venv
ensure_venv || exit 1