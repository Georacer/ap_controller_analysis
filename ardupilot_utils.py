"""Module with ArduPilot-related helpers."""

import math
from pathlib import Path
from collections import OrderedDict

import numpy as np

from pymavlink import DFReader


class Message:
    """Concrete representation of a message.

    Includes its timestamps and separate iterators for its fields.
    """

    def __init__(self, fmt: DFReader.DFFormat):
        """Class constructor."""
        self.format = fmt
        self.values = dict()  # Supposed to be a dict of lists.
        self.timestamps = list()
        for col in fmt.columns:
            self.values[col] = list()

    def __getitem__(self, item):
        """Dict-like access dunder."""
        return self.values[item]

    def __setitem__(self, item, value):
        """Dict-like access dunder."""
        self.values[item] = value

    def as_numpy(self, item):
        """Convert the values into a numpy array."""
        return np.array(self.timestamps), np.array(self.values[item])


class ArdupilotParser:
    """A parser for Ardupilot logs."""

    log_path = None
    # log = None
    # params = None
    # param_defaults = None
    # topics = None

    def __init__(self, log_path: Path):
        """Class constructor."""
        self.log_path = log_path
        self.log = DFReader.DFReader_binary(str(log_path))
        self.parse_messages()
        self.parse_parameters()

    def parse_messages(self, topic_filter=None):
        """Parse the log and extract the required information.

        This is useful because a DFReader log by default doesn't provide easy
        access to structured log data. Instead one needs to traverse the log
        each time he wants to look something up and process messages one by one.

        Args:
            topic_filter: A list of the form
                TOPICS_OF_INTEREST = [
                    "AETR",  # Normalized pre-mixer control surface outputs.
                    "MODE",  # Vehicle control mode information.
                    "MSG",  # User messages printouts.
                    ...
        """
        self.topics = dict()
        self.log.rewind()
        while True:
            if topic_filter is None:
                m = self.log.recv_match()
            else:
                m = self.log.recv_match(type=topic_filter)
            if m is None:
                break

            msg_name = m.get_type()
            msg_data = m.to_dict()
            del msg_data[
                "mavpackettype"
            ]  # We don't need this and it breaks some assumptions.

            if msg_name not in self.topics.keys():
                self.topics[msg_name] = Message(m.fmt)

            self.topics[msg_name].timestamps.append(m._timestamp)
            for key_name, value in msg_data.items():
                self.topics[msg_name][key_name].append(value)

    def parse_parameters(self):
        """Extract parameter information from stored messages.

        Taken from pymavlink/DFReader.py:L670.
        """
        self.params = OrderedDict()
        self.param_defaults = OrderedDict()

        for name, value, default in zip(
            self.topics["PARM"]["Name"],
            self.topics["PARM"]["Value"],
            self.topics["PARM"]["Default"],
            strict=True,
        ):
            if name is not None:
                self.params[name] = value
                if not math.isnan(default):
                    self.param_defaults[name] = default

        self.params = OrderedDict(sorted(self.params.items()))
        self.param_defaults = OrderedDict(sorted(self.param_defaults.items()))

    def build_log_params(self):
        """Return a list of param dicts."""
        return self.params

    def build_log_param_edits(self):
        """Return a list of parameters changed from default.

        Returns
        -------
        List[str, float, float]
            A list of triplets [param_name, default_value, changed_value]
        """
        try:
            answer = [
                [name, default, self.params[name]]
                for name, default in self.param_defaults.items()
                if default != self.params[name]
            ]
        except KeyError:
            answer = ["N/A", "N/A", "N/A"]
        return answer
