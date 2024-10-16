import asyncio
import logging
from ..extractors.tcp_extractor import TCPExtractor
from ..protocols.tcp_protocols import TCP_PROTOCOLS
from ..transformers.byte_stream_transformer import ByteStreamTransformer


class ByteStreamDataSource:
    def __init__(self, host, port, sensor_address, protocol_names, authentication=None):
        self.protocol_names = protocol_names
        self.sensor_address = sensor_address

        self.extractor = TCPExtractor(host, port, authentication)
        self.transformer = ByteStreamTransformer()

    async def get_data(self):
        # TODO: Pass in a retry amount
        # TODO: If connection is lost, try to reestablish it gracefully
        await self.extractor.connect()

        # TODO: We'll need a way for the user to add their own protocols
        for protocol_name in self.protocol_names:
            protocol = TCP_PROTOCOLS.get(protocol_name)
            if not protocol:
                logging.error(f'"{protocol_name}" not found in TCP_PROTOCOLS list.')
                break

            address = self.derive_station_address(
                self.sensor_address, protocol.get("type", None)
            )

            # Extract
            command = f"{address}{protocol['command']}\r"
            wait = protocol.get("wait", 5)
            response = await self.extractor.extract(command, wait)

            # Transform
            parsed_response = self.transformer.transform(
                protocol, response, address, command
            )
            if parsed_response is None:
                logging.info(f"{protocol_name} received echo: {parsed_response}")
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
                await asyncio.sleep(seconds_until_ready)
                continue

            logging.info(f"{protocol_name} parsed response: {parsed_response}")
            return parsed_response

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
