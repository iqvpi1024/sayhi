#!/usr/bin/env bash
# Build the Noetide macOS / Linux source package: sayhi-<version>-src.tar.gz.
#
# The Windows beta (scripts/build-d2-beta.ps1) embeds a Python runtime, which
# cannot be produced for macOS/Linux from a Windows machine. This script ships
# the sources plus Unix launchers instead; the target machine only needs
# Python 3.12+ (zero third-party dependencies).
#
# Usage:
#   scripts/build-unix-source.sh [--ref <git-ref>] [--worktree] [--output-dir DIR]
#
#   --ref REF      package sources from a git ref (tag/branch/commit, default HEAD)
#   --worktree     package the working tree as-is instead of a git ref
#   --output-dir   output directory (default: <repo>/dist)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

REF="HEAD"
USE_WORKTREE=0
OUTPUT_DIR=""

fail() {
    echo "[build-unix-source] error: $1" >&2
    exit 1
}

while [ $# -gt 0 ]; do
    case "$1" in
        --ref)
            [ $# -ge 2 ] || fail "--ref requires a value"
            REF="$2"
            shift 2
            ;;
        --worktree)
            USE_WORKTREE=1
            shift
            ;;
        --output-dir)
            [ $# -ge 2 ] || fail "--output-dir requires a value"
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help|-h)
            sed -n '2,15p' "$0"
            exit 0
            ;;
        *)
            fail "unknown argument: $1"
            ;;
    esac
done

[ -n "$OUTPUT_DIR" ] || OUTPUT_DIR="$REPO_ROOT/dist"

VERSION="$(sed -n 's/^version = "\([^"]*\)".*/\1/p' "$REPO_ROOT/pyproject.toml" | head -n 1)"
[ -n "$VERSION" ] || fail "could not read version from $REPO_ROOT/pyproject.toml"

BUNDLE_NAME="sayhi-$VERSION-src"
STAGE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/noetide-src-build-XXXXXXXX")"
trap 'rm -rf "$STAGE_ROOT"' EXIT

BUNDLE_ROOT="$STAGE_ROOT/$BUNDLE_NAME"
mkdir -p "$BUNDLE_ROOT"

# Paths shipped in the source package (matches the Windows bundle contents,
# plus the desktop launcher). Windows portable scripts are not included;
# the Unix launchers under scripts/portable are added separately below.
INCLUDE_PATHS=(
    "src"
    "noetide_desktop.py"
    "start.py"
    "README.md"
    "LICENSE"
    "SUPPORT.md"
    "pyproject.toml"
)

if [ "$USE_WORKTREE" -eq 1 ]; then
    echo "[build-unix-source] packaging working tree"
    for path in "${INCLUDE_PATHS[@]}"; do
        [ -e "$REPO_ROOT/$path" ] || fail "missing required path in working tree: $path"
        mkdir -p "$BUNDLE_ROOT/$(dirname "$path")"
        cp -R "$REPO_ROOT/$path" "$BUNDLE_ROOT/$path"
    done
    SOURCE_REF="worktree"
else
    command -v git >/dev/null 2>&1 || fail "git is required (or use --worktree)"
    echo "[build-unix-source] packaging git ref: $REF"
    git -C "$REPO_ROOT" archive --format=tar --output="$STAGE_ROOT/source.tar" "$REF" -- "${INCLUDE_PATHS[@]}" \
        || fail "git archive failed for ref $REF"
    tar -xf "$STAGE_ROOT/source.tar" -C "$BUNDLE_ROOT"
    SOURCE_REF="$(git -C "$REPO_ROOT" rev-parse "$REF" 2>/dev/null || echo "$REF")"
fi

# The Unix launchers may be newer than the archived ref; always ship the
# working-tree copies so the package is never missing them.
mkdir -p "$BUNDLE_ROOT/scripts/portable"
for launcher in setup-noetide.sh start-noetide.sh; do
    [ -f "$REPO_ROOT/scripts/portable/$launcher" ] || fail "missing Unix launcher: scripts/portable/$launcher"
    cp "$REPO_ROOT/scripts/portable/$launcher" "$BUNDLE_ROOT/scripts/portable/$launcher"
    chmod +x "$BUNDLE_ROOT/scripts/portable/$launcher"
done

# Never ship caches, tests, or local artifacts regardless of the source mode.
find "$BUNDLE_ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$BUNDLE_ROOT" -type f -name '*.pyc' -delete

cat > "$BUNDLE_ROOT/SOURCE_PACKAGE_MANIFEST.json" <<EOF
{
  "schema_version": "noetide.source-package.v1",
  "name": "$BUNDLE_NAME",
  "version": "$VERSION",
  "source_ref": "$SOURCE_REF",
  "platforms": ["macos", "linux"],
  "requires": "Python 3.12+ (standard library only)",
  "setup": "scripts/portable/setup-noetide.sh",
  "start": "scripts/portable/start-noetide.sh",
  "code_signed": false
}
EOF

mkdir -p "$OUTPUT_DIR"
ARCHIVE_PATH="$OUTPUT_DIR/$BUNDLE_NAME.tar.gz"
rm -f "$ARCHIVE_PATH"
tar -czf "$ARCHIVE_PATH" -C "$STAGE_ROOT" "$BUNDLE_NAME"

if command -v sha256sum >/dev/null 2>&1; then
    ARCHIVE_HASH="$(sha256sum "$ARCHIVE_PATH" | cut -d ' ' -f 1)"
elif command -v shasum >/dev/null 2>&1; then
    ARCHIVE_HASH="$(shasum -a 256 "$ARCHIVE_PATH" | cut -d ' ' -f 1)"
else
    fail "neither sha256sum nor shasum is available"
fi
printf '%s  %s\n' "$ARCHIVE_HASH" "$BUNDLE_NAME.tar.gz" > "$OUTPUT_DIR/SHA256SUMS-$VERSION-src.txt"

echo "[build-unix-source] built: $ARCHIVE_PATH"
echo "[build-unix-source] SHA-256: $ARCHIVE_HASH"
echo "[build-unix-source] checksums: $OUTPUT_DIR/SHA256SUMS-$VERSION-src.txt"
