from .base import Transformer
import logging
import re
import pandas as pd
from datetime import datetime, timezone
from typing import Any, Dict, List


class ByteStreamTransformer(Transformer):
    def __init__(self, datastream_ids):
        self.datastream_ids = datastream_ids

        self.parser_functions = {
            "token": self.parse_token,
            "echo": self.parse_echo,
            "array": self.parse_voltages_array,
            "number": self.parse_number,
            "signed_numbers": self.parse_signed_numbers,
        }

    def transform(self, protocol, byte_response: bytes, address: str, command_str):
        """Decodes and parses a tcp byte response then transforms it into a pandas dataframe.
        Will return the following values:
        [values...] = Successfully transformed data.
        False = The expected pattern couldn't be found.
        None = Successfully matched the pattern but there's no data to return. For echo responses.
        """
        logging.info(f"Raw byte response: {byte_response}")
        self.response = byte_response.decode("utf-8")
        self.protocol = protocol
        self.address = address
        self.command_str = command_str

        response_format = protocol.get("response_format", "signed_numbers")

        try:
            parser = self.parser_functions.get(response_format)
            if parser is None:
                raise ValueError(f"Unsupported response_format: {response_format}")
            return parser()
        except Exception as e:
            logging.error(f"Parse Error: {e}")
            return False

    def parse_echo(self):
        """Check that the response is the same as the command."""
        pattern = rf"{re.escape(self.command_str)}"
        match = re.search(pattern, self.response)
        if not match:
            logging.warning(f"No station echo found in the response.")
            return False
        return None

    def parse_token(self):
        """Parses an SDI-12 response in the atttnn token format where:
        a = station name
        ttt = time in seconds until the sensor will have the measurement(s) ready
        nn = the number of measurements the sensor will make and return in response
        to subsequent D commands.
        """
        token_format = self.protocol.get("token_format")
        time_digits = token_format.count("t")
        measurement_digits = token_format.count("n")
        pattern = rf"{re.escape(self.address)}(\d{{{time_digits}}})(\d{{{measurement_digits}}})"
        match = re.search(pattern, self.response)
        if not match:
            logging.warning(f"No token pattern found in the response.")
            return False

        return [int(match.group(1)), int(match.group(2))]

    def parse_signed_numbers(self):
        """Extracts numbers that begin with a + or - and returns them as a number array.
        For now, assume we only want the first number in the array."""
        pattern = rf"[+-][\d*\.*]+"
        matches = re.findall(pattern, self.response)
        if not matches:
            logging.warning(f"No signed numbers found in the response.")
            return False

        return self.build_observations_map(matches)

    def parse_number(self):
        """Extracts one number immediately after the sensor address."""
        pattern = rf"{re.escape(self.address)}([\d*\.*]+)"
        match = re.search(pattern, self.response)
        if not match:
            logging.warning(f"No number pattern found in the response.")
            return False

        return self.build_observations_map([match.group(1)])

    def parse_voltages_array(
        self,
    ):
        """For a weeder station's single-ended command where we get all 8 input channels at once,
        we expect 8 integers between -4095 and +4095 (millivolts). Then the host (this script)
        is expected to convert those values based on sensor hardware. There are two values we care about:
        match.group(1) = Flow rate
        match.group(8) = Voltage. The FORTRAN scripts assumed two resistors - 1kΩ and 3.32KΩ
                        so we'll use the same conversion factor of 0.00432.
        """
        group_pattern = r"(\d+\s?)"
        pattern = rf"{re.escape(self.address)}\s*{group_pattern * 8}"
        match = re.search(pattern, self.response)
        if not match:
            logging.warning(f"Array of 8 numbers not found in the response.")
            return False

        flow = int(match.group(1))
        battery_voltage = int(match.group(8)) * 0.00432
        return self.build_observations_map([flow, battery_voltage])

    def build_observations_map(self, data: List[Any]):
        measurements = {}
        returns = self.protocol.get("returns", [])
        for name, value in zip(returns, data):
            measurements[name] = float(value)

        unexpected_keys = set(self.datastream_ids.keys()) - set(measurements.keys())
        if unexpected_keys:
            logging.error(f"datastream_ids contains unexpected keys: {unexpected_keys}")
            raise ValueError(
                f"datastream_ids contains keys not present in measurements: {unexpected_keys}"
            )

        current_time = pd.Timestamp(datetime.now(timezone.utc))

        observations_map = {}
        for measurement_name, value in measurements.items():
            datastream_id = self.datastream_ids.get(measurement_name)
            if not datastream_id:
                continue
            df = pd.DataFrame({"timestamp": [current_time], "value": [float(value)]})
            observations_map[datastream_id] = df

        return observations_map
