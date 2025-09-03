"""Common utilities for tecs_analysis_2"""

from pathlib import Path
import itertools
import hashlib
import json

import numpy as np

SITL_PYTHON = "/usr/bin/python"
PROJECT_DIR = "/home/george/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2"
SITL_RUN_DIR = str(Path(PROJECT_DIR) / "temp_dir")
SAMPLE_PARAM_FILE = str(Path(SITL_RUN_DIR) / "sample_point.parm")
LOGS_PATH = str(Path(SITL_RUN_DIR) / "logs")
ARTIFACTS_PATH = str(Path(PROJECT_DIR) / "artifacts")

parameter_matrix = [
    {"TECS_HDEM_TCONST": np.linspace(0.5, 5, 5)},  # Default: 3
    {
        "TECS_HGT_OMEGA": np.concatenate(([0, 0.25], np.linspace(1, 10, 5)))
    },  # Default: 3
    {
        "TECS_INTEG_GAIN": np.concatenate(([0, 0.05], np.linspace(0.1, 1.9, 10)))
    },  # Default: 0.3
    {"TECS_PTCH_DAMP": np.linspace(0, 1.0, 11)},  # Default: 0.3
    {
        "TECS_THR_DAMP": np.concatenate(
            (np.linspace(0, 1.0, 5), np.linspace(2, 5, 4))
        )  # Default: 0.5
    },
    {
        "TECS_SPD_OMEGA": np.concatenate(
            ([0, 0.25], np.linspace(0.5, 5, 5))  # Default: 2
        )
    },
    {"TECS_TIME_CONST": np.concatenate(([0.5], np.linspace(1, 10, 10)))},  # Default: 5
    {
        "TECS_VERT_ACC": np.concatenate((np.linspace(3, 9, 7), np.linspace(10, 50, 5)))
    },  # Default: 7
    {"TECS_CLMB_MAX": np.linspace(2, 10, 5)},  # Default: 5
    {"TECS_SINK_MAX": np.linspace(2, 10, 5)},  # Default: 5
    {"TRIM_THROTTLE": np.linspace(10, 80, 8)},  # Default: 50
    {"PTCH_LIM_MAX_DEG": np.linspace(5, 50, 10), "TECS_PITCH_MAX": [0]},  # Default: 15
    {
        "PTCH_LIM_MAX_DEG": np.linspace(5, 50, 10),
        "TECS_PITCH_MAX": [0],
        "TECS_CLMB_MAX": [20],
    },
    {"AIRSPEED_CRUISE": np.linspace(6, 30, 5)},  # Default: 22
    #########################################################################
    # Runs to evaluate influence of pitch control loop.
    #########################################################################
    {
        "PTCH2SRV_TCONST": np.concatenate(
            (np.linspace(0.1, 1, 5), np.linspace(1.4, 3, 5))
        )
    },  # Default: 0.25
    {"PTCH_RATE_P": [0.05, 0.1, 0.15, 0.25, 0.5, 0.75, 1.0]},  # Default: 0.15
    {
        "PTCH2SRV_RMAX_UP": [
            1.0,
            2.0,
            5.0,
            10.0,
            15.0,
            20.0,
            30.0,
            40.0,
            50.0,
            70.0,
            90.0,
        ]
    },  # Default: 90
    {
        "TECS_TIME_CONST": np.linspace(1, 10, 10),
        "PTCH2SRV_RMAX_UP": [2],
    },
    {
        "TECS_HDEM_TCONST": np.linspace(1, 10, 10),  # Default: 3
        "PTCH2SRV_RMAX_UP": [2],  # Default: 90
    },
    {
        "TECS_PTCH_DAMP": np.linspace(0.1, 1, 10),  # Default: 0.3
        "TECS_TIME_CONST": [12],  # Default: 5
        "TECS_HDEM_TCONST": [6],  # Default: 3
        "PTCH2SRV_RMAX_UP": [2],  # Default: 90
    },
    {
        "TECS_TIME_CONST": np.linspace(1, 10, 10),  # Default: 5
        "PTCH2SRV_TCONST": [0.25, 0.5, 1.0, 2.0, 2.6, 3.0],  # Default: 0.25
    },
    ##########################################################################
]


def get_parameter_names(matrix):
    """Generate a list of all parameters referenced in the parameter_matrix."""

    parameter_names = set()

    for case in matrix:
        parameter_names = parameter_names.union(set(list(case.keys())))

    return parameter_names


def generate_combinations(matrix):
    """Generate parameter combinations.

    Args:
        matrix: A list containing dictionaries.
            Each dictionary has AP parameters as keys and lists of values to sweep.

    Returns:
        A flat list of dictionaries, with AP parameters as keys and a single value assigned to each.
    """
    combinations = []

    for case in matrix:
        param_names = list(case.keys())
        param_values = list(case.values())

        flat_values = list(itertools.product(*param_values))
        for combo_values in flat_values:
            combinations.append(dict(zip(param_names, combo_values)))

    return combinations


def generate_hash(dictionary, length=None):
    "Generate a has given a dictionary."
    encoded = json.dumps(dictionary).encode()
    if length is None:
        dhash = hashlib.md5()
        dhash.update(encoded)
        return dhash.hexdigest()
    else:
        dhash = hashlib.shake_128()
        dhash.update(encoded)
        return dhash.hexdigest(length)


def generate_name(sample):
    """Generate a filename for a given parameter sample.

    Assumption: The first parameter passed is the one that is primarily sweeped for.

    Args:
        sample: A dictionary with AP parameter names as keys and their values.

    Returns:
        A string for filename, without an extension.
    """

    primary_parameter = list(sample.items())[0]
    primary_name = primary_parameter[0]
    primary_value = primary_parameter[1]

    return f"{primary_name}_{primary_value:.3}_{generate_hash(sample)}"
