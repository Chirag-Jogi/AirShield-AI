import sys
from pathlib import Path

# Add the project root to sys.path so 'src' can be imported correctly.
sys.path.insert(0, str(Path(__file__).resolve().parent))
