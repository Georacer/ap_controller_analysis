"""Common utilities for tecs_analysis_2"""

from pathlib import Path

SITL_PYTHON = "/usr/bin/python"
PROJECT_DIR = "/home/george/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2"
SITL_RUN_DIR = str(Path(PROJECT_DIR) / "temp_dir")
SAMPLE_PARAM_FILE = str(Path(SITL_RUN_DIR) / "sample_point.parm")
LOGS_PATH = str(Path(SITL_RUN_DIR) / "logs")
ARTIFACTS_PATH = str(Path(PROJECT_DIR) / "artifacts")
