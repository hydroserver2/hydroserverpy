from .base import Extractor
import logging
import socket
import time
from ..protocols.tcp_protocols import TCP_PROTOCOLS
from hydroserverpy.etl.transformers.byte_stream_transformer import ByteStreamTransformer


class TCPSensorExtractor(Extractor):
    def __init__(
        self,
        host: str,
        port: int,
        authentication: dict,
        sensor_address: str,
        retries: int,
        protocol_names: list,
        datastream_ids: dict,
    ):
        self.host = host
        self.port = port
        self.authentication = authentication

        self.sensor_address = sensor_address
        self.retries = retries
        self.protocol_names = protocol_names
        self.datastream_ids = datastream_ids

        self.sock = None

        self.transformer = ByteStreamTransformer(datastream_ids)

    def connect(self):
        """Establish a TCP connection"""
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=10)
            logging.info(f"Established TCP connection with {self.host}")
        except socket.error as e:
            logging.error(f"Error connecting to {self.host}: {e}")
            self.disconnect()

    def extract(self):
        for _ in range(self.retries):
            self.connect()
            if not self.sock:
                continue

            try:
                # TODO: We'll need a way for the user to add their own protocols
                for protocol_name in self.protocol_names:
                    protocol = TCP_PROTOCOLS.get(protocol_name)
                    if not protocol:
                        logging.error(
                            f'"{protocol_name}" not found in TCP_PROTOCOLS list.'
                        )
                        break

                    address = self.derive_station_address(
                        self.sensor_address, protocol.get("type", None)
                    )

                    # Extract
                    self.clear_buffer()
                    command = f"{address}{protocol['command']}\r"
                    logging.info(f"sending TCP command: {command}")
                    self.sock.sendall(command.encode("ascii"))

                    time.sleep(protocol.get("wait", 5))
                    response = self.sock.recv(4096)

                    # Transform
                    parsed_response = self.transformer.transform(
                        protocol, response, address, command
                    )
                    if parsed_response is None:
                        logging.info(
                            f"{protocol_name} received echo: {parsed_response}"
                        )
                        continue
                    elif parsed_response is False:
                        raise ValueError(f"Expected response not found")

                    response_format = protocol.get("response_format")
                    if response_format == "token":
                        # Token responses say how much time they need to prepare a measurement.
                        # Therefore sleep for that amount of time then move on to the next protocol,
                        # which should have a D command.
                        seconds_until_ready = parsed_response[0]
                        logging.info(
                            f"Waiting {seconds_until_ready} seconds for sensor {self.sensor_address} to prepare a measurement..."
                        )
                        time.sleep(seconds_until_ready)
                        continue

                    logging.info(f"{protocol_name} parsed response: {parsed_response}")
                    self.disconnect()
                    return parsed_response
            except Exception as e:
                logging.error(e)

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
                logging.info(f"Closed TCP connection with {self.host}:{self.port}")
            except socket.error as e:
                logging.error(f"Error closing socket: {e}")
            finally:
                self.sock = None

    def clear_buffer(self):
        """Clear all remaining data in the buffer."""
        try:
            # Set socket to non-blocking to clear the buffer
            self.sock.setblocking(False)
            while True:
                try:
                    data = self.sock.recv(4096)
                    if not data:
                        break
                except BlockingIOError:
                    break
        except socket.error as e:
            logging.error(f"Error clearing buffer: {e}")

    def convert_to_voltage_address(station_name):
        """Converts the last character of a given station name between '0' and '9'
        to a character between 'a' and 'j' by shifting ASCII values.
        This character represents a voltage level.
        """
        volt_num = station_name[-1]
        new_char = chr(ord(volt_num) + 49)
        return station_name[:-1] + new_char

    def derive_station_address(self, station_name, command_type):
        return (
            self.convert_to_voltage_address(station_name)
            if command_type == "voltage_address"
            else station_name
        )
