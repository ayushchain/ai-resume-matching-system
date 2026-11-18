"""Make the backend `app` package importable wherever pytest is run from."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
