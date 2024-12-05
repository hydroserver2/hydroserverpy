import logging
from ftplib import FTP
from io import BytesIO
from .base import Extractor


class FTPExtractor(Extractor):
    def __init__(
        self,
        host: str,
        filepath: str,
        username: str = None,
        password: str = None,
        port: int = 21,
    ):
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.filepath = filepath

    def extract(self):
        """
        Downloads the file from the FTP server and returns a file-like object.
        """
        try:
            ftp = FTP()
            ftp.connect(self.host, self.port)
            ftp.login(user=self.username, passwd=self.password)
            logging.info(f"Connected to FTP server: {self.host}:{self.port}")

            data = BytesIO()
            ftp.retrbinary(f"RETR {self.filepath}", data.write)
            logging.info(
                f"Successfully downloaded file '{self.filepath}' from FTP server."
            )
            data.seek(0)
            return data
        except Exception as e:
            logging.error(f"Error retrieving file from FTP server: {e}")
            return None
        finally:
            if ftp:
                ftp.quit()
