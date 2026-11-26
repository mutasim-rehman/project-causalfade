"""Unified build script for extracting and verifying all dashboard datasets."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR / "extract"))
sys.path.insert(0, str(SCRIPTS_DIR / "verify"))

import extract_all  # type: ignore
import verify_data  # type: ignore


def main() -> None:
    extract_all.main()
    verify_data.main()


if __name__ == "__main__":
    main()
