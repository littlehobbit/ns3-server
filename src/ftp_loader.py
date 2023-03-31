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
            with FTP() as ftp:
                self._connect(ftp)
                path, name = self._make_archive(results)
                with open(path, 'rb') as file:
                    ftp.storbinary(f'STOR {name}', file)
                return name
        except Exception as err:
            raise UploadError(f'Uploading error: {err}')

    def _connect(self, ftp):
        ftp.connect(self.address)
        ftp.login(self.user, self.password)

    def _make_archive(self, path: str) -> str:
        archive_path = path + '.tar.gz'
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(path, arcname=os.path.basename(path))
        return archive_path, os.path.basename(archive_path)

