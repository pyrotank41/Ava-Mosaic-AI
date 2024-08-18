import sys
import os
from pathlib import Path

# Get the parent directory of the directory containing this file
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to sys.path
sys.path.insert(0, str(parent_dir))
