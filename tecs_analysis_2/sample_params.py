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

from rich.pretty import pprint

import common

# Create the sampling space.
# combinations is a list of lists.
# Each list item is a dictionary of parameters to alter.
combinations = common.generate_combinations(common.parameter_matrix)

try:
    os.makedirs(common.SITL_RUN_DIR)
except FileExistsError:
    pass
try:
    os.makedirs(common.ARTIFACTS_PATH)
except FileExistsError:
    pass

for sample in combinations:
    # Generate a temporary parameter file.
    with open(common.SAMPLE_PARAM_FILE, "w") as f:
        for name, value in sample.items():
            f.write(f"{name} {value}\n")

    # Run the autotest.
    print(f"*** Running test for sample: {sample}")
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
        flight_log,
        str(Path(common.ARTIFACTS_PATH) / f"{common.generate_name(sample)}.BIN"),
    )
