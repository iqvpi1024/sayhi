#!/usr/bin/env bash
# Noetide setup for macOS / Linux (source package).
# Unix counterpart of setup-noetide.ps1: chooses a local data directory,
# runs product-init, and records the choice under ~/.noetide/.
# Requires Python 3.12+ on PATH (no third-party packages needed).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$APP_ROOT/src"

SETTINGS_ROOT="${NOETIDE_HOME:-$HOME/.noetide}"
SETTINGS_PATH="$SETTINGS_ROOT/data_dir.txt"
PRIVACY_PATH="$SETTINGS_ROOT/privacy.json"
DEFAULT_DATA_DIR="$SETTINGS_ROOT/data"

DATA_DIRECTORY=""
ASSUME_YES=0

usage() {
    echo "Usage: setup-noetide.sh [--data-dir DIR] [--yes]"
}

step() {
    echo "[Noetide Setup] $1"
}

fail() {
    echo "[Noetide Setup] error: $1" >&2
    exit 1
}

while [ $# -gt 0 ]; do
    case "$1" in
        --data-dir)
            [ $# -ge 2 ] || fail "--data-dir requires a value"
            DATA_DIRECTORY="$2"
            shift 2
            ;;
        --yes|-y)
            ASSUME_YES=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            usage >&2
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

if [ "$ASSUME_YES" -eq 1 ]; then
    if [ -z "$DATA_DIRECTORY" ]; then
        DATA_DIRECTORY="$DEFAULT_DATA_DIR"
    fi
else
    echo "Noetide is local-first: your data stays in the folder you choose unless you"
    echo "explicitly enable remote access. You own the data and can export or back it"
    echo "up at any time."
    printf "Continue with setup? [y/N] "
    read -r answer
    case "$answer" in
        y|Y|yes|YES) ;;
        *) fail "setup cancelled by user" ;;
    esac

    if [ -z "$DATA_DIRECTORY" ]; then
        echo ""
        echo "Choose where your Noetide data lives. You own this folder; uninstalling the"
        echo "app never deletes it."
        printf "Use the default folder? %s [Y/n] " "$DEFAULT_DATA_DIR"
        read -r answer
        case "$answer" in
            n|N|no|NO)
                printf "Enter a local data folder you own: "
                read -r DATA_DIRECTORY
                [ -n "$DATA_DIRECTORY" ] || fail "a local data folder is required"
                ;;
            *)
                DATA_DIRECTORY="$DEFAULT_DATA_DIR"
                ;;
        esac
    fi
fi

RESOLVED_DATA="$("$PYTHON" -c 'import os, sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' "$DATA_DIRECTORY")"
case "$RESOLVED_DATA" in
    "$APP_ROOT"|"$APP_ROOT"/*)
        fail "the data folder must be outside the application folder so upgrades and uninstalls can never touch it"
        ;;
esac

mkdir -p "$RESOLVED_DATA" "$SETTINGS_ROOT"
[ -d "$RESOLVED_DATA" ] && [ -w "$RESOLVED_DATA" ] || fail "data folder is not writable: $RESOLVED_DATA"

if ! "$PYTHON" -m noetide_micro --data-dir "$RESOLVED_DATA" product-init; then
    fail "data initialization failed; the existing folder was not modified - pick an empty folder or restore from a backup"
fi

CHOSEN_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
"$PYTHON" - "$PRIVACY_PATH" "$CHOSEN_AT" "$RESOLVED_DATA" "$ASSUME_YES" <<'PYEOF'
import json
import sys

path, chosen_at, data_dir, assume_yes = sys.argv[1:5]
privacy = {
    "schema_version": "noetide.privacy.v1",
    "chosen_at": chosen_at,
    "data_directory": data_dir,
    "acknowledged_local_only": True,
    "acknowledged_synthetic_only": False,
    "acknowledged_unsigned": False,
    "install_kind": "source",
}
with open(path, "w", encoding="utf-8") as handle:
    json.dump(privacy, handle, indent=2)
    handle.write("\n")
PYEOF
printf '%s' "$RESOLVED_DATA" > "$SETTINGS_PATH"

step "data folder: $RESOLVED_DATA"
step "privacy choices recorded: $PRIVACY_PATH"
# Post-setup health check via the product store. (The plain `status` CLI command
# opens the synthetic demo runtime, which refuses a product-initialized
# database; the product path is the one start-noetide.sh actually serves.)
if ! "$PYTHON" - "$RESOLVED_DATA" <<'PYEOF'
import sys

from noetide_micro.product import NoetideApp

app = NoetideApp(sys.argv[1])
try:
    revision = app.store.current_revision()
finally:
    app.close()
print(f"[Noetide Setup] status check: revision {revision}")
PYEOF
then
    fail "status check failed after setup"
fi
step "setup complete. Run scripts/portable/start-noetide.sh to open the web management UI."
