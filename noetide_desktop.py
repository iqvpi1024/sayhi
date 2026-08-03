"""Noetide desktop launcher for the complete local product.

Run:
    python noetide_desktop.py

The first launch creates an empty local database under the chosen data directory
and opens the local web UI at http://127.0.0.1:8765.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Noetide desktop")
    parser.add_argument("--data-dir", default=None, help="data directory (default: ~/.noetide/data)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    data_dir = args.data_dir or (Path.home() / ".noetide" / "data")
    from noetide_micro.product_server import serve_product

    return serve_product(data_dir, host=args.host, port=args.port)


if __name__ == "__main__":
    raise SystemExit(main())
