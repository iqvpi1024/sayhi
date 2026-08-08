#!/usr/bin/env bash
# Noetide start for macOS / Linux (source package).
# Unix counterpart of "sayhi Start.cmd": runs setup if needed, then starts
# the local product service on http://127.0.0.1:8765.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$APP_ROOT/src"

SETTINGS_ROOT="${NOETIDE_HOME:-$HOME/.noetide}"
SETTINGS_PATH="$SETTINGS_ROOT/data_dir.txt"

HOST="127.0.0.1"
PORT="8765"

fail() {
    echo "[Noetide Start] error: $1" >&2
    exit 1
}

while [ $# -gt 0 ]; do
    case "$1" in
        --host)
            [ $# -ge 2 ] || fail "--host requires a value"
            HOST="$2"
            shift 2
            ;;
        --port)
            [ $# -ge 2 ] || fail "--port requires a value"
            PORT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: start-noetide.sh [--host HOST] [--port PORT]"
            exit 0
            ;;
        *)
            fail "unknown argument: $1"
            ;;
    esac
done

PYTHON=""
SEEN_VERSION=""
for candidate in python3 python; do
    command -v "$candidate" >/dev/null 2>&1 || continue
    # Skip shims that cannot execute code at all (e.g. the Windows Store stub).
    CANDIDATE_VERSION="$("$candidate" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null)" || continue
    [ -n "$SEEN_VERSION" ] || SEEN_VERSION="$CANDIDATE_VERSION"
    if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    if [ -n "$SEEN_VERSION" ]; then
        fail "Python 3.12 or newer is required; found $SEEN_VERSION. Install a newer Python or point PATH at one."
    fi
    fail "Python was not found on PATH. Install Python 3.12 or newer, then re-run this script."
fi

[ -d "$SRC_DIR/noetide_micro" ] || fail "application sources are missing (expected $SRC_DIR/noetide_micro); re-extract the source package"
export PYTHONPATH="$SRC_DIR${PYTHONPATH:+:$PYTHONPATH}"

if [ ! -f "$SETTINGS_PATH" ]; then
    echo "[Noetide Start] first run: starting setup..."
    "$SCRIPT_DIR/setup-noetide.sh"
fi

DATA_DIRECTORY="$(cat "$SETTINGS_PATH")"
[ -n "$DATA_DIRECTORY" ] || fail "data directory setting is empty ($SETTINGS_PATH); re-run setup-noetide.sh"
[ -d "$DATA_DIRECTORY" ] || fail "data folder no longer exists: $DATA_DIRECTORY (re-run setup-noetide.sh)"

echo "[Noetide Start] data folder: $DATA_DIRECTORY"
echo "[Noetide Start] serving on http://$HOST:$PORT - open this address in your browser."
echo "[Noetide Start] press Ctrl+C to stop."
exec "$PYTHON" -m noetide_micro --data-dir "$DATA_DIRECTORY" product --host "$HOST" --port "$PORT"
