#!/usr/bin/env python

# Checkout georacer/ardupilot/apdevcon2025 .
# Run plane test mission.
# $ clear; /home/george/projects_no_dropbox/ardupilot/Tools/autotest/autotest.py test.Plane.fly_tecs_test
# Load the parameter value to sample.
# Wait for the mission to finish.

# Parse the log and extract the segments.
# Perform FFT on each segment. Collect velocity and altitude peaks.
# Store the information in a lightweight database.

from pathlib import Path
from dataclasses import dataclass
from typing import Tuple
import sys

import numpy as np
from pymavlink import DFReader
from rich.pretty import pprint
import matplotlib.pyplot as plt

sys.path.append("..")
import ardupilot_utils as apu

RAD2HZ = 1 / np.pi
LOGS_DIR = "~/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2/temp_dir/logs"

segments = {
    "level": (4, 5),
    "step_up": (5, 6),
    "step_down": (6, 7),
    "climb": (7, 8),
    "sink": (9, 10),
}


@dataclass
class SegmentRawData:
    """Class containing parsed data from a flight segment."""

    airspeed: Tuple[np.ndarray, np.ndarray]
    altitude: Tuple[np.ndarray, np.ndarray]
    altitude_target: Tuple[np.ndarray, np.ndarray]


@dataclass
class SegmentMetadata:
    """Class containing the metadata of a segment."""

    airspeed_frequency: float | None
    airspeed_amplitude: float | None
    altitude_frequency: float | None
    altitude_amplitude: float | None
    altitude_overshoot: float | None
    altitude_rise_time: float | None


def do_fft(timeseries: Tuple[np.ndarray, np.ndarray]):
    """Carry out Fourier analysis on the passed timeseries.

    Args:
        timeseries:
            A length-2 iterable with the series timestamps and the series values.

    Returns:
        The biggest peak frequency and amplitude.
    """

    peaks = np.fft.rfft(timeseries[1])
    freqs = (
        np.fft.fftfreq(len(timeseries[0])) * np.average(np.diff(timeseries[0])) * RAD2HZ
    )
    peak_idx = np.argmax(peaks)

    freq = freqs[peak_idx]
    peak = peaks[peak_idx]

    if freq < 0.1:
        return None, None
    else:
        return freq, peak


def calc_rise_stats(
    timeseries: Tuple[np.ndarray, np.ndarray], target: Tuple[np.ndarray, np.ndarray]
):
    """Find the rise time and overshoot of a response.

    Args:
        timeseries:
            A length-2 iterable with the series timestamps and the series values.
        target:
            A length-2 iterable with the target value timestamps and the series values.

    Returns:
        overshoot, in % of target value.
        rise time, in seconds to reach 95% of target.
    """

    # Interpolate the target.
    target_timestamps = target[0]
    target_values = target[1]
    if (timeseries[0] != target[0]).all():
        target_timestamps = timeseries[0]
        target_values = np.interp(timeseries[0], target_timestamps, target_values)

    error = timeseries[1] - target_values

    # Do a linear fit to see the general trend of the response (upwards, downards)
    response_coeffs = np.polyfit(timeseries[0], timeseries[1], deg=1)
    # Check if this is an ascending or descending response.
    if response_coeffs[0] < 0:
        # Flip to an ascending response.
        error = -error

    # Normalize to a unit step.
    error_normalized = error / (np.abs(error.min())) + 1
    print(f"Error stats: max: {error.max()}, min: {error.min()}")
    print(
        f"Normalized error stats: max: {error_normalized.max()}, min: {error_normalized.min()}"
    )

    overshoot = (error_normalized.max() - 1) * 100
    rise_time = timeseries[0][np.argmax(error_normalized > 0.95)] - timeseries[0][0]

    # If the error never converged to a ramp response, then don't bother.
    if error_normalized[-1] < error_normalized[0]:
        overshoot = None
        rise_time = None

    return overshoot, rise_time


def extract_metadata(raw_data: SegmentRawData):
    """Extract the metadata of interest from raw log data.

    Args:
        log_data: SegmentRawData

    Returns:
        An instance of SegmentMetadata.
    """

    airspeed_frequency, airspeed_amplitude = do_fft(raw_data.airspeed)
    altitude_frequency, altitude_amplitude = do_fft(raw_data.altitude)
    altitude_overshoot, altitude_rise_time = calc_rise_stats(
        raw_data.altitude, raw_data.altitude_target
    )

    return SegmentMetadata(
        airspeed_frequency=airspeed_frequency,
        airspeed_amplitude=airspeed_amplitude,
        altitude_frequency=altitude_frequency,
        altitude_amplitude=altitude_amplitude,
        altitude_overshoot=altitude_overshoot,
        altitude_rise_time=altitude_rise_time,
    )


def parse_log(log_path):
    """Parse a log file and extract raw data.

    Returns:
        A dictionary with the same keys as `segments`. Its values are SegmentRawData.
    """
    # Open the log.

    log = DFReader.DFReader_binary(str(log_path))
    log.rewind()

    topics = dict()
    topic_filter = [
        "CTUN",
        "TECS",
        "MISE",
    ]

    data = dict()

    segment_idx = 0
    segment_start = list(segments.values())[segment_idx][0]
    segment_end = list(segments.values())[segment_idx][1]
    started_segmenting = False

    while True:
        if topic_filter is None:
            m = log.recv_match()
        else:
            m = log.recv_match(type=topic_filter)
        if m is None:
            break

        msg_name = m.get_type()
        msg_data = m.to_dict()

        # Split the segments.
        if msg_name == "MISE":
            if msg_data["CNum"] == segment_start:
                started_segmenting = True
            if msg_data["CNum"] == segment_end:
                if not started_segmenting:
                    raise RuntimeError(f"Did not find start of segment {segment_idx}")
                else:
                    # Consume airspeed and altitude messages and put them in SegmentRawData.
                    data[list(segments.keys())[segment_idx]] = SegmentRawData(
                        airspeed=topics["CTUN"].as_numpy("As"),
                        altitude=topics["TECS"].as_numpy("h"),
                        altitude_target=topics["TECS"].as_numpy("hin"),
                    )

                    # Reset the topic ledger.
                    topics = dict()
                    segment_idx = segment_idx + 1

                    if segment_idx == len(segments):
                        break

                    segment_start = list(segments.values())[segment_idx][0]

                    # Check if we are about to examine back-to-back segments.
                    if segment_start == segment_end:
                        started_segmenting = True
                    else:
                        started_segmenting = False

                    segment_end = list(segments.values())[segment_idx][1]

        del msg_data[
            "mavpackettype"
        ]  # We don't need this and it breaks some assumptions.

        if started_segmenting:
            if msg_name not in topics.keys():
                topics[msg_name] = apu.Message(m.fmt)

            topics[msg_name].timestamps.append(m._timestamp)
            for key_name, value in msg_data.items():
                topics[msg_name][key_name].append(value)

    # fig, ax = plt.subplots()
    # for raw_data in data.values():
    #     ax.plot(raw_data.altitude[0], raw_data.altitude[1])
    # ax.grid()
    # fig.savefig("altitude.png")

    return {
        segment_name: extract_metadata(raw_data)
        for segment_name, raw_data in data.items()
    }


if __name__ == "__main__":
    logs_dir = Path(LOGS_DIR).expanduser()
    log_path = logs_dir / "00000002.BIN"
    data = parse_log(log_path)
    pprint(data)
