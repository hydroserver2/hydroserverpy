from .base import Extractor
import logging
import asyncio


class TCPExtractor(Extractor):
    def __init__(self, host, port, authentication=None):
        self.host = host
        self.port = port
        self.authentication = authentication
        self.reader = None
        self.writer = None

    async def connect(self):
        """Establish a TCP connection"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            logging.info(f"Established TCP connection with {self.host}")
        except Exception as e:
            logging.error(f"Error connecting to {self.host}: {e}")
            self.disconnect()

    async def extract(self, command, wait):
        await self.clear_buffer()

        logging.info(f"sending TCP command: {command}")
        self.writer.write(command.encode("ascii"))

        await self.writer.drain()
        await asyncio.sleep(wait)
        return await self.reader.read(4096)

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
