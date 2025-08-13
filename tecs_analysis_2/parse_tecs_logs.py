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
from dataclasses import dataclass, asdict
from typing import Tuple
import sys
import random

import numpy as np
from pymavlink import DFReader
from rich.pretty import pprint
from rich.progress import Progress
import scipy as scp
import matplotlib.pyplot as plt
from tinydb import TinyDB, Query

import common

sys.path.append("..")
import ardupilot_utils as apu

LOGS_DIR = "~/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2/temp_dir/logs"
RAD2DEG = 180 / np.pi
DEG2RAD = 1 / RAD2DEG

# A dictionary with the start and end waypoint numbers of each segment.
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
    airspeed_target: Tuple[np.ndarray, np.ndarray]
    altitude: Tuple[np.ndarray, np.ndarray]
    altitude_target: Tuple[np.ndarray, np.ndarray]
    pitch_target: Tuple[np.ndarray, np.ndarray]
    parameters: dict


@dataclass
class SegmentMetadata:
    """Class containing the metadata of a segment."""

    airspeed_frequency: float | None  # Hz
    airspeed_amplitude: float | None  # m/s
    airspeed_overshoot: float | None  # m/s
    airspeed_undershoot: float | None  # m/s
    altitude_frequency: float | None  # Hz
    altitude_amplitude: float | None  # m
    altitude_overshoot: float | None  # %
    altitude_rise_time: float | None  # %
    pitch_target_frequency: float | None  # Hz
    pitch_target_amplitude: float | None  # deg
    parameters: dict


def do_fft(
    timeseries: Tuple[np.ndarray, np.ndarray], height_threshold=None, freq_threshold=0.1
):
    """Carry out Fourier analysis on the passed timeseries.

    Args:
        timeseries:
            A length-2 iterable with the series timestamps and the series values.

    Returns:
        The biggest peak frequency and amplitude.
    """

    peaks = np.absolute(
        np.fft.rfft(timeseries[1] - timeseries[1].mean()) / len(timeseries[0]) * 2
    )  # Remove the signal DC value and convert to real units.
    freqs = np.fft.rfftfreq(len(timeseries[0]), d=np.average(np.diff(timeseries[0])))
    prominence = (
        peaks.max() * 0.05
    )  # Find peaks that stand out at least that much from their baseline.
    peaks_idx, properties = scp.signal.find_peaks(
        peaks, height=(None, None), prominence=prominence
    )

    # Sort by peak amplitude.
    sort_idx = peaks_idx[np.flip(np.argsort(properties["peak_heights"]))]

    peak = None
    freq = None

    for peak_idx in sort_idx:

        if (
            freqs[peak_idx] < freq_threshold
        ):  # We've probably captured the transient sine.
            continue

        if height_threshold and (peaks[peak_idx] < height_threshold):
            # Not a very significant peak
            continue

        freq = freqs[peak_idx]
        peak = peaks[peak_idx]
        break

    return freq, peak


def calc_regulation_stats(
    timeseries: Tuple[np.ndarray, np.ndarray], target: Tuple[np.ndarray, np.ndarray]
):
    """Find the maximum and minimum error.

    Assumes the input response and demand are for a regulation problem.

    Args:
        timeseries:
            A length-2 iterable with the series timestamps and the series values.
        target:
            A length-2 iterable with the target value timestamps and the series values.

    Returns:
        maximum positive error: How much higher the response got from the target. Positive value.
        maximum negative error: How much lower the response got from the target. Positive value.
    """

    # Interpolate the target.
    target_timestamps = target[0]
    target_values = target[1]
    if (timeseries[0] != target[0]).all():
        target_timestamps = timeseries[0]
        target_values = np.interp(timeseries[0], target_timestamps, target_values)

    error = timeseries[1] - target_values

    return error.max(), -error.min()


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

    airspeed_frequency, airspeed_amplitude = do_fft(
        raw_data.airspeed, height_threshold=0.25
    )
    airspeed_overshoot, airspeed_undershoot = calc_regulation_stats(
        raw_data.airspeed, raw_data.airspeed_target
    )
    altitude_frequency, altitude_amplitude = do_fft(
        raw_data.altitude, height_threshold=0.5
    )
    altitude_overshoot, altitude_rise_time = calc_rise_stats(
        raw_data.altitude, raw_data.altitude_target
    )
    pitch_target_frequency, pitch_target_amplitude = do_fft(
        raw_data.pitch_target, height_threshold=1 * DEG2RAD
    )

    return SegmentMetadata(
        airspeed_frequency=airspeed_frequency,
        airspeed_amplitude=airspeed_amplitude,
        airspeed_overshoot=airspeed_overshoot,
        airspeed_undershoot=airspeed_undershoot,
        altitude_frequency=altitude_frequency,
        altitude_amplitude=altitude_amplitude,
        altitude_overshoot=altitude_overshoot,
        altitude_rise_time=altitude_rise_time,
        pitch_target_frequency=pitch_target_frequency,
        pitch_target_amplitude=(
            None if pitch_target_amplitude is None else pitch_target_amplitude * RAD2DEG
        ),
        parameters=raw_data.parameters,
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
    topic_filter = ["CTUN", "TECS", "MISE", "PARM"]

    data = dict()
    parameters = dict()

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

        # Capture the parameters.
        # Make sure the full dictionary of common.parameter_matrix is uncommented, to capture all of the parameters.
        if msg_name == "PARM" and (msg_data["Name"] in common.parameter_matrix.keys()):
            parameters[msg_data["Name"]] = msg_data["Value"]

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
                        airspeed=topics["TECS"].as_numpy("sp"),
                        airspeed_target=topics["TECS"].as_numpy("spdem"),
                        altitude=topics["TECS"].as_numpy("h"),
                        altitude_target=topics["TECS"].as_numpy("hin"),
                        pitch_target=topics["TECS"].as_numpy("ph"),
                        parameters=parameters,
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


def convert_data_to_dict(data):
    """Convert the result of parse_log() into a pure dict."""

    return {segment_name: asdict(metadata) for segment_name, metadata in data.items()}


def add_to_db(data):
    """Add this script's data to the database.

    This will overwrite older data.
    """
    db = TinyDB("performance_results.json", sort_keys=True, indent=4)
    logdata = Query()

    for log_data in data:
        db.upsert(log_data, logdata.log_name == log_data["log_name"])


if __name__ == "__main__":
    logs_dir = Path(LOGS_DIR).expanduser()
    logs_paths = list(Path(common.ARTIFACTS_PATH).glob("*.BIN"))

    all_data = []

    with Progress() as progress:

        task1 = progress.add_task("Parsing logs...", total=len(logs_paths))
        for log_path in logs_paths:
            progress.update(task1, advance=1)
            data_one_log = {}
            data_one_log["data"] = convert_data_to_dict(parse_log(log_path))
            data_one_log["log_name"] = log_path.name
            all_data.append(data_one_log)
        # pprint(all_data)
        add_to_db(all_data)
