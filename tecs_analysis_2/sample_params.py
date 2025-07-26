#!/usr/bin/env python

"""Sample the parameter space and generate a response

This script will sample a set of TECS parameters. For each sample, it will run
the same mission and store the flight logs using a specific naming scheme.

To be used with `ardupilot/apdevcon2025` branch.
"""

import shutil
import subprocess
import numpy as np
from pathlib import Path
import os

import common

# Create the sampling space.
parameter_matrix = {
    # "TECS_HDEM_TCONST": np.linspace(0.5, 5, 5),
    # "TECS_HGT_OMEGA": np.linspace(1, 10, 5),
    # "TECS_INTEG_GAIN": np.linspace(0.1, 1, 5),
    "TECS_PTCH_DAMP": np.linspace(0.1, 1.0, 5),
    # "TECS_SPD_OMEGA": np.linspace(0.5, 5, 5),
    # "TECS_TIME_CONST": np.linspace(1, 10, 5),
    # "TECS_VERT_ACC": np.linspace(3, 10, 5),
}
combinations = []
for parameter, values in parameter_matrix.items():
    for value in values:
        combinations.append((parameter, value))

try:
    os.makedirs(common.SITL_RUN_DIR)
except FileExistsError:
    pass
try:
    os.makedirs(common.ARTIFACTS_PATH)
except FileExistsError:
    pass

for sample_point in combinations:
    # Generate a temporary parameter file.
    param_name = sample_point[0]
    param_value = sample_point[1]
    with open(common.SAMPLE_PARAM_FILE, "w") as f:
        f.write(f"{param_name} {param_value}")

    # Run the autotest.
    print(f"*** Running test for sample: {param_name}={param_value}")
    subprocess.run(
        f"{common.SITL_PYTHON} /home/george/projects_no_dropbox/ardupilot/Tools/autotest/autotest.py test.Plane.fly_tecs_test",
        cwd=common.SITL_RUN_DIR,
        shell=True,
        check=True,
    )

    # Find the flight log, it should be the biggest one.
    log_files = [str(path) for path in Path(common.LOGS_PATH).glob("*.BIN")]
    flight_log = max(log_files, key=os.path.getsize)

    # Copy and rename it.
    shutil.copyfile(
        flight_log, str(Path(common.ARTIFACTS_PATH) / f"{param_name}_{param_value}.BIN")
    )
