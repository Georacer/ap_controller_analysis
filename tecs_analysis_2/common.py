"""Common utilities for tecs_analysis_2"""

from pathlib import Path

import numpy as np

SITL_PYTHON = "/usr/bin/python"
PROJECT_DIR = "/home/george/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2"
SITL_RUN_DIR = str(Path(PROJECT_DIR) / "temp_dir")
SAMPLE_PARAM_FILE = str(Path(SITL_RUN_DIR) / "sample_point.parm")
LOGS_PATH = str(Path(SITL_RUN_DIR) / "logs")
ARTIFACTS_PATH = str(Path(PROJECT_DIR) / "artifacts")

parameter_matrix = {
    "TECS_HDEM_TCONST": np.linspace(0.5, 5, 5),  # Default: 3
    "TECS_HGT_OMEGA": np.linspace(1, 10, 5),  # Default: 3
    "TECS_INTEG_GAIN": np.linspace(0.1, 1, 5),  # Default: 0.3
    "TECS_PTCH_DAMP": np.linspace(0.1, 1.0, 5),  # Default: 0.3
    "TECS_SPD_OMEGA": np.linspace(0.5, 5, 5),  # Default: 2
    "TECS_TIME_CONST": np.linspace(1, 10, 5),  # Default: 5
    "TECS_VERT_ACC": np.linspace(3, 50, 5),  # Default: 7
}
