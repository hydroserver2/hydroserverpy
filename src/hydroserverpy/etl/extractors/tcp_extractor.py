from .base import Extractor
import logging
import asyncio
from ..protocols.tcp_protocols import TCP_PROTOCOLS
from hydroserverpy.etl.transformers.byte_stream_transformer import ByteStreamTransformer


class TCPSensorExtractor(Extractor):
    def __init__(self, data_source):
        self.host = data_source.host
        self.port = data_source.port
        self.authentication = data_source.authentication
        self.protocol_names = data_source.protocol_names
        self.sensor_address = data_source.sensor_address
        self.retries = data_source.retries

        self.reader = None
        self.writer = None

        self.transformer = ByteStreamTransformer(data_source)

    async def connect(self):
        """Establish a TCP connection"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            logging.info(f"Established TCP connection with {self.host}")
        except Exception as e:
            logging.error(f"Error connecting to {self.host}: {e}")
            await self.disconnect()

    async def extract(self):
        for _ in range(self.retries):
            await self.connect()

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
                    await self.clear_buffer()
                    command = f"{address}{protocol['command']}\r"
                    logging.info(f"sending TCP command: {command}")
                    self.writer.write(command.encode("ascii"))

                    wait = protocol.get("wait", 5)
                    await self.writer.drain()
                    await asyncio.sleep(wait)
                    response = await self.reader.read(4096)

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
                        await asyncio.sleep(seconds_until_ready)
                        continue

                    await self.disconnect()
                    logging.info(f"{protocol_name} parsed response: {parsed_response}")
                    return parsed_response
            except Exception as e:
                logging.error(e)

    async def disconnect(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def clear_buffer(self):
        """Clear all remaining data in the buffer."""
        try:
            await asyncio.wait_for(self.reader.read(4096), timeout=0.1)
        except asyncio.TimeoutError:
            pass  # If a timeout occurs, it means the buffer is now empty
        except Exception as e:
            print("Error clearing buffer:", e)

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
