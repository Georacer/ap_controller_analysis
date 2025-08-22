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
    "TECS_HGT_OMEGA": np.concatenate(
        (
            [0, 0.25],
            np.linspace(1, 10, 5),
        )
    ),  # Default: 3
    "TECS_INTEG_GAIN": np.concatenate(
        ([0, 0.05], np.linspace(0.1, 2, 10))
    ),  # Default: 0.3
    "TECS_PTCH_DAMP": np.linspace(0, 1.0, 11),  # Default: 0.3
    "TECS_THR_DAMP": np.concatenate(
        (np.linspace(0, 1.0, 5), np.linspace(2, 5, 4))  # Default: 0.5
    ),
    "TECS_SPD_OMEGA": np.concatenate(
        (
            [0, 0.25],
            np.linspace(0.5, 5, 5),  # Default: 2
        )
    ),
    "TECS_TIME_CONST": np.concatenate(([0.5], np.linspace(1, 10, 10))),  # Default: 5
    "TECS_VERT_ACC": np.concatenate(
        (np.linspace(3, 9, 7), np.linspace(10, 50, 5))
    ),  # Default: 7
    "TECS_CLMB_MAX": np.linspace(2, 10, 5),  # Default: 5
    "TECS_SINK_MAX": np.linspace(2, 10, 5),  # Default: 5
    "TRIM_THROTTLE": np.linspace(10, 80, 8),  # Default: 50
}
