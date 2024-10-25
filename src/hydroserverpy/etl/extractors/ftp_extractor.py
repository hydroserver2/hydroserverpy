import logging
from ftplib import FTP
from io import BytesIO


class FTPExtractor:
    def __init__(self, host: str, username: str, password: str, filepath: str):
        self.host = host
        self.username = username
        self.password = password
        self.filepath = filepath

    async def extract(self):
        """
        Downloads the file from the FTP server and returns a file-like object.
        """
        try:
            ftp = FTP(self.host)
            ftp.login(self.username, self.password)
            logging.info(f"Connected to FTP server: {self.host}")

            data = BytesIO()

            ftp.retrbinary(f"RETR {self.filepath}", data.write)
            ftp.quit()

            data.seek(0)
            logging.info(
                f"Successfully downloaded file '{self.filepath}' from FTP server."
            )
            return data
        except Exception as e:
            logging.error(f"Error retrieving file from FTP server: {e}")
            return None
