#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH="$SCRIPT_DIR/../../yaw/utils:$SCRIPT_DIR/../..:$PYTHONPATH"