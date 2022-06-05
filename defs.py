# Project Definitions

import os
from pathlib import Path

PROJECT_PATH: Path = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR_PATH: Path = PROJECT_PATH.joinpath("data")
