import os
import unittest
from ftplib import FTP
from src.ftp_loader import FtpLoader
from src.uploader import Uploader, UploadError


class TestFtpLoader(unittest.TestCase):
    test_dir = os.path.join(os.getcwd(), 'tests')
    address: str = '127.0.0.1'
    user: str = 'test_user'
    password: str = 'test_user_password'
    ftp: FTP

    def assertHasFile(self, file: str):
        files = self.ftp.nlst()
        self.assertIn(file, files)

    def setUp(self) -> None:
        self.loader = FtpLoader(self.address, self.user, self.password)
        self.loader.connect()
        self.ftp = FTP(self.address, self.user, self.password)
        self.cleanRemote()

    def tearDown(self) -> None:
        self.cleanRemote()
        self.loader.close()
        self.ftp.close()
        self.cleanArchives()

    def cleanRemote(self):
        for file in self.ftp.nlst():
            self.ftp.delete(file)

    def cleanArchives(self):
        for file in os.listdir(self.test_dir):
            if file.endswith('tar.gz'):
                os.remove(os.path.join(self.test_dir, file))

    def test_create_ftp_loader(self):
        self.assertTrue(issubclass(FtpLoader, Uploader))
        self.assertEqual(self.loader.address, self.address)
        self.assertEqual(self.loader.user, self.user)
        self.assertEqual(self.loader.password, self.password)

    def test_upload_and_zip_directory(self):
        directory = os.path.join(self.test_dir, 'test_zip_dir')

        result_archive = self.loader.upload(directory)

        self.assertEqual(result_archive, 'test_zip_dir.tar.gz')
        self.assertHasFile(result_archive)

    def test_missed_direcory(self):
        directory = os.path.join(self.test_dir, 'missed_directory')
        with self.assertRaises(UploadError):
            self.loader.upload(directory)

    def test_bad_credentials(self):
        bad_user = 'bad_user'
        bad_password = 'bad_password'
        uploader = FtpLoader(self.address, bad_user, bad_password)
        with self.assertRaises(UploadError):
            uploader.connect()