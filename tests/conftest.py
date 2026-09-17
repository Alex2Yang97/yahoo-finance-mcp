import sys
from pathlib import Path

# Add the project root to the Python path so tests can import from server.py
sys.path.insert(0, str(Path(__file__).parent.parent))
