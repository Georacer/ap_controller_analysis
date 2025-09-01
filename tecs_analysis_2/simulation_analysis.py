#!/usr/bin/env python

"""Parse the results found in performance_results.json database."""

import matplotlib.pyplot as plt
from tinydb import TinyDB, Query
import numpy as np
from rich.pretty import pprint
import copy

import common

PLOT_ROWS = 4


def draw_axis(ah, x, y, quantity, segment):
    """Draw one axis."""
    ah.plot(x, y, label=segment, marker="x")
    ah.set_xlim(x.min(), x.max())
    ah.set_ylabel(quantity)
    ah.ticklabel_format(style="plain", axis="y", useOffset=False)


# Open the database.
db = TinyDB("performance_results.json", access_mode="r")

# Extract all the different parameter names/sweeps.
log = Query()
all_data = db.all()

# Find the list of cases which merit their own figure.
sweeps = dict()

# Generate the graph cases as combinations of the secondary parameters.
for experiment in common.parameter_matrix:

    # Convert numpy arrays to lists, in order to hash them.
    for key in experiment.keys():
        experiment[key] = np.array(experiment[key]).tolist()

    primary_param_name = list(experiment.keys())[0]

    # Copy the experiments dictionary.
    secondary_params = copy.copy(experiment)
    # Delete the primary parameter.
    del secondary_params[primary_param_name]
    # Generate the remaining combinations.
    flat_secondary_params = common.generate_combinations([secondary_params])
    for case in flat_secondary_params:
        # Re-convert the values into lists.
        case = {key: [value] for key, value in case.items()}
        # Add back the primary parameter sweep.
        # Create the entry in the sweeps dictionary.
        sweeps[f"{primary_param_name}_{common.generate_hash(case, 2)}"] = {
            primary_param_name: experiment[primary_param_name]
        } | case

# Use the latest entry to build the segment names.
# Others might not be up to date with all the parameters.
max_id = max([entry.doc_id for entry in all_data])
last_entry = db.get(doc_id=max_id)
segment_names = list(last_entry["data"].keys())  # type: ignore This entry is sure to exist in the db.
# parameter_names = list(last_entry["data"][segment_names[0]]["parameters"].keys())  # type: ignore

# For each parameter:
for image_name, case in sweeps.items():

    combinations = common.generate_combinations([case])
    primary_param_name = list(case.keys())[0]
    log_names = [f"{common.generate_name(sample)}.BIN" for sample in combinations]

    data_per_case = [
        entry["data"] for entry in all_data if entry["log_name"] in log_names
    ]

    quantities = [
        "airspeed_frequency",
        "airspeed_amplitude",
        "airspeed_overshoot",
        "airspeed_undershoot",
        "altitude_frequency",
        "altitude_amplitude",
        "altitude_rise_time",
        "altitude_overshoot",
        "pitch_target_frequency",
        "pitch_target_amplitude",
        "climb_rate_rmse",
    ]
    div_res, mod_res = divmod(len(quantities), PLOT_ROWS)

    fig, axs = plt.subplots(PLOT_ROWS, div_res + 1)
    fig.set_size_inches(20, 12)

    title = None
    for name, value in case.items():
        # Assumes secondary parameters have a single value.
        if title is None:
            title = f"{name} influence\n"
        else:
            title = title + f"{name}={value[0]}\n"

    fig.suptitle(title)

    # For each segment:
    for segment in segment_names:

        # Skip for now as it distorts results.
        if segment == "level":
            continue

        # Create the plot:
        x = np.array(
            [data[segment]["parameters"][primary_param_name] for data in data_per_case]
        )
        sort_idx = np.argsort(x)
        x.sort()

        for index, quantity in enumerate(quantities):

            # Plot climb rate only in specific segments.
            if quantity == "climb_rate_rmse" and segment not in ["climb", "sink"]:
                continue

            data = np.array([data[segment][quantity] for data in data_per_case])[
                sort_idx
            ]
            idy, idx = divmod(index, PLOT_ROWS)
            draw_axis(axs[idx, idy], x, data, quantity, segment)
            if idx == PLOT_ROWS - 1:
                axs[idx, idy].set_xlabel("Parameter value")

    axs[0, 0].legend(loc="upper left")

    # Save each plot into a .png.
    fig.savefig(f"artifacts/{image_name}.png")
