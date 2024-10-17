from .base import Transformer
import logging
import re


# TODO: Update this to return a pandas dataframe that can be uploaded to HydroServer
class ByteStreamTransformer(Transformer):
    def __init__(self):
        pass

    def transform(self, protocol, byte_response: bytes, address: str, command_str):
        """Decodes and parses a tcp byte response then transforms it into a pandas dataframe.
        Will return the following values:
        [values...] = Successfully transformed data.
        False = The expected pattern couldn't be found.
        None = Successfully matched the pattern but there's no data to return. For echo responses.
        """
        logging.info(f"Raw byte response: {byte_response}")
        response = byte_response.decode("utf-8")
        response_format = protocol.get("response_format", "signed_numbers")

        parser_functions = {
            "token": lambda: self.parse_token(
                response, address, protocol.get("token_format")
            ),
            # "identification": lambda: parse_identification_token(response, address),
            "echo": lambda: self.parse_echo(response, command_str),
            "array": lambda: self.parse_voltages_array(response, address),
            "number": lambda: self.parse_number(response, address),
            "signed_numbers": lambda: self.parse_signed_numbers(response),
        }

        try:
            parser = parser_functions.get(response_format)
            if parser is None:
                raise ValueError(f"Unsupported response_format: {response_format}")
            return parser()
        except Exception as e:
            logging.error(f"Parse Error: {e}")
            return False

    def parse_echo(self, response: str, sensor_command):
        """Check that the response is the same as the command."""
        pattern = rf"{re.escape(sensor_command)}"
        match = re.search(pattern, response)
        if not match:
            logging.warning(f"No station echo found in the response.")
            return False
        return None

    def parse_token(self, response: str, address, token_format):
        """Parses an SDI-12 response in the atttnn token format where:
        a = station name
        ttt = time in seconds until the sensor will have the measurement(s) ready
        nn = the number of measurements the sensor will make and return in response
        to subsequent D commands.
        """
        time_digits = token_format.count("t")
        measurement_digits = token_format.count("n")
        pattern = (
            rf"{re.escape(address)}(\d{{{time_digits}}})(\d{{{measurement_digits}}})"
        )
        match = re.search(pattern, response)
        if not match:
            logging.warning(f"No token pattern found in the response.")
            return False

        return [int(match.group(1)), int(match.group(2))]

    def parse_signed_numbers(self, response: str):
        """Extracts numbers that begin with a + or - and returns them as a number array."""
        pattern = rf"[+-][\d*\.*]+"
        matches = re.findall(pattern, response)
        if not matches:
            logging.warning(f"No signed numbers found in the response.")
            return False

        return [float(num) for num in matches]

    def parse_number(self, response: str, address):
        """Extracts one number immediately after the sensor address."""
        pattern = rf"{re.escape(address)}([\d*\.*]+)"
        match = re.search(pattern, response)
        if not match:
            logging.warning(f"No number pattern found in the response.")
            return False

        return [float(match.group(1))]

    def parse_voltages_array(self, response: str, address):
        """For a weeder station's single-ended command where we get all 8 input channels at once,
        we expect 8 integers between -4095 and +4095 (millivolts). Then the host (this script)
        is expected to convert those values based on sensor hardware. There are two values we care about:
        match.group(1) = Flow rate
        match.group(8) = Voltage. The FORTRAN scripts assumed two resistors - 1kΩ and 3.32KΩ
                        so we'll use the same conversion factor of 0.00432.
        """
        group_pattern = r"(\d+\s?)"
        pattern = rf"{re.escape(address)}\s*{group_pattern * 8}"
        match = re.search(pattern, response)
        if not match:
            logging.warning(f"Array of 8 numbers not found in the response.")
            return False

        flow = int(match.group(1))
        battery_voltage = int(match.group(8)) * 0.00432
        return [flow, battery_voltage]

    # def parse_identification_token(self, response: str, address):
    #     """Parses an SDI-12 response in the allccccccccmmmmmmvvvxx..xx token format where:
    #     a = station name
    #     l = 2 character SDI-12 version number (for example 12 is version 1.2)
    #     c = 8 character vendor ID
    #     m = 6 character sensor model number
    #     v = 3 character sensor version
    #     x = Optional field of up to 13 characters to be used for serial number or sensor
    #         specific information
    #     """
    #     identification_pattern = r"(\d{2})([^\\r]{8})([^\\r]{6})([^\\r]{3})([^\\r]{0,13})"
    #     pattern = rf"{re.escape(address)}{identification_pattern}"
    #     match = re.search(pattern, response)
    #     if not match:
    #         logging.warning("No identification pattern found in the response.")
    #         return False

    #     version = match.group(1)
    #     vendor_id = match.group(2)
    #     model_number = match.group(3)
    #     sensor_version = match.group(4)
    #     optional_info = match.group(5)

    #     return {
    #         "version_number": version,
    #         "vendor_id": vendor_id,
    #         "model_number": model_number,
    #         "sensor_version": sensor_version,
    #         "optional_info": optional_info,
    #     }
