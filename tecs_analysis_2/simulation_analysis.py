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
    ah.plot(x, y, label=segment)
    ah.set_xlim(x.min(), x.max())
    ah.set_ylabel(quantity)


# For each parameter:
for parameter in parameter_names:

    data_per_param = [
        data["data"] for data in all_data if data["log_name"].startswith(parameter)
    ]

    fig, axs = plt.subplots(6, 1)
    fig.set_size_inches(12, 12)
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

        for idx, quantity in enumerate(
            [
                "airspeed_frequency",
                "airspeed_amplitude",
                "altitude_frequency",
                "altitude_amplitude",
                "altitude_rise_time",
                "altitude_overshoot",
            ]
        ):

            data = np.array([data[segment][quantity] for data in data_per_param])[
                sort_idx
            ]
            draw_axis(axs[idx], x, data, quantity, segment)

        # airspeed_freq = np.array(
        #     [data[segment]["airspeed_frequency"] for data in data_per_param]
        # )[sort_idx]
        # draw_axis(axs[0], x, airspeed_freq, parameter, segment)

        # airspeed_amplitude = np.array(
        #     [data[segment]["airspeed_amplitude"] for data in data_per_param]
        # )[sort_idx]
        # draw_axis(axs[1], x, airspeed_amplitude, parameter, segment)

        # altitude_freq = np.array(
        #     [data[segment]["altitude_frequency"] for data in data_per_param]
        # )[sort_idx]
        # draw_axis(axs[2], x, altitude_freq, parameter, segment)

        # altitude_amplitude = np.array(
        #     [data[segment]["altitude_amplitude"] for data in data_per_param]
        # )[sort_idx]
        # draw_axis(axs[3], x, altitude_amplitude, parameter, segment)

        # altitude_rise_time = np.array(
        #     [data[segment]["altitude_rise_time"] for data in data_per_param]
        # )[sort_idx]
        # axs[4].plot(x, altitude_rise_time, label=segment)

        # altitude_overshoot = np.array(
        #     [data[segment]["altitude_overshoot"] for data in data_per_param]
        # )[sort_idx]
        # axs[5].plot(x, altitude_overshoot, label=segment)
        axs[5].set_xlabel("Parameter value")

    axs[0].legend(loc="upper left")

    # Save each plot into a .png.
    fig.savefig(f"artifacts/{parameter}.png")
