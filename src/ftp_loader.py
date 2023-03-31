import os
import tarfile
from ftplib import FTP

from src.uploader import Uploader, UploadError


class FtpLoader(Uploader):
    address: str
    user: str
    password: str

    def __init__(self, address: str, user: str, password: str):
        self.address = address
        self.user = user
        self.password = password

    def upload(self, results: str) -> str:
        """ zip & upload result directory """
        try:
            with FTP(self.address, self.user, self.password) as ftp:
                archive_path = self._make_archive(results)
                archive_name = os.path.basename(archive_path)
                with open(archive_path, 'rb') as file:
                    ftp.storbinary(f'STOR {archive_name}', file)
                return archive_name
        except Exception as err:
            raise UploadError(f'Uploading error: {err}')

    def _make_archive(self, path: str) -> str:
        output_filename = path + '.tar.gz'
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(path, arcname=os.path.basename(path))
        return output_filename
