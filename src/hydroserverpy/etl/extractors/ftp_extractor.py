from .base import Extractor
import logging
import aioftp


class FTPExtractor(Extractor):
    def __init__(self, host, port=21, authentication=None, delimiter=","):
        self.host = host
        self.port = port
        self.authentication = authentication or {}
        self.client = None
        self.delimiter = delimiter

    async def connect(self):
        """Establish an FTP connection"""
        self.client = aioftp.Client()
        try:
            username = self.authentication.get("username", "anonymous")
            password = self.authentication.get("password", "")
            await self.client.connect(self.host, self.port)
            await self.client.login(username, password)
            logging.info(f"Connected to FTP server {self.host}:{self.port}")
        except Exception as e:
            logging.error(
                f"Failed to connect to FTP server {self.host}:{self.port} - {e}"
            )
            self.client = None
            raise

    async def extract(self):
        # TODO: extract data from host
        data = None

    async def disconnect(self):
        """Close the FTP connection"""
        if self.client:
            try:
                await self.client.quit()
                logging.info("FTP connection closed.")
            except Exception as e:
                logging.error(f"Error while disconnecting from FTP server: {e}")
            finally:
                self.client = None
