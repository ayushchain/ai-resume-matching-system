"""Standalone test runner — no pytest required.

Usage (from backend/):  python tests/run_all.py
Exits 0 when every test passes, 1 otherwise. The same test functions
also run under pytest:  python -m pytest tests/
"""
import importlib
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))          # tests/

MODULES = ["test_skills", "test_parsers", "test_matching", "test_store"]


def main():
    passed = failed = 0
    for name in MODULES:
        module = importlib.import_module(name)
        for attr in sorted(dir(module)):
            if not attr.startswith("test_"):
                continue
            try:
                getattr(module, attr)()
                print(f"PASS {name}.{attr}")
                passed += 1
            except Exception:
                print(f"FAIL {name}.{attr}")
                traceback.print_exc()
                failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
