#!/usr/bin/env python

"""Parse the results found in performance_results.json database."""

import matplotlib.pyplot as plt
from tinydb import TinyDB, Query
import numpy as np

# Open the database.
db = TinyDB("performance_results.json", access_mode="r")

# Extract all the different parameter names/sweeps.
log = Query()
all_data = db.all()

# Initialize the data structures.
segment_names = list(all_data[0]["data"].keys())
parameter_names = list(all_data[0]["data"][segment_names[0]]["parameters"].keys())


def draw_axis(ah, x, y, quantity, segment):
    """Draw one axis."""
    ah.plot(x, y, label=segment, marker="x")
    ah.set_xlim(x.min(), x.max())
    ah.set_ylabel(quantity)


# For each parameter:
for parameter in parameter_names:

    data_per_param = [
        data["data"] for data in all_data if data["log_name"].startswith(parameter)
    ]

    fig, axs = plt.subplots(4, 2)
    fig.set_size_inches(16, 12)
    fig.suptitle(f"{parameter} influence")

    # For each segment:
    for segment in segment_names:

        # Skip for now as it distorts results.
        if segment == "level":
            continue

        # Create the plot:
        x = np.array(
            [data[segment]["parameters"][parameter] for data in data_per_param]
        )
        sort_idx = np.argsort(x)
        x.sort()

        quantities = [
            "airspeed_frequency",
            "airspeed_amplitude",
            "airspeed_overshoot",
            "airspeed_undershoot",
            "altitude_frequency",
            "altitude_amplitude",
            "altitude_rise_time",
            "altitude_overshoot",
        ]

        for index, quantity in enumerate(quantities):

            data = np.array([data[segment][quantity] for data in data_per_param])[
                sort_idx
            ]
            idy, idx = divmod(index, int(np.ceil(len(quantities) / 2)))
            draw_axis(axs[idx, idy], x, data, quantity, segment)

        axs[3, 0].set_xlabel("Parameter value")
        axs[3, 1].set_xlabel("Parameter value")

    axs[0, 0].legend(loc="upper left")

    # Save each plot into a .png.
    fig.savefig(f"artifacts/{parameter}.png")
