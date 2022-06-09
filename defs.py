# Project Definitions

import os
from pathlib import Path

# Project Path
PROJECT_PATH: Path = Path(os.path.dirname(os.path.abspath(__file__)))

# Common Directories
DATA_DIR_PATH: Path = PROJECT_PATH.joinpath("data")
LOG_DIR_PATH: Path = PROJECT_PATH.joinpath("logs")
