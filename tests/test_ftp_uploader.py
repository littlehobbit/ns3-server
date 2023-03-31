import os
import unittest
from ftplib import FTP
from src.ftp_loader import FtpLoader
from src.uploader import Uploader, UploadError


class TestFtpLoader(unittest.TestCase):
    TEST_DIR = os.path.join(os.getcwd(), 'tests')
    ADDRESS: str = '127.0.0.1'
    USER: str = 'test_user'
    PASSWORD: str = 'test_user_password'
    UPLOAD_DIR: str = 'test_zip_dir'
    ftp: FTP

    def assertHasFile(self, file: str):
        files = self.ftp.nlst()
        self.assertIn(file, files)

    def setUp(self) -> None:
        self.loader = FtpLoader(self.ADDRESS, self.USER, self.PASSWORD)
        self.ftp = FTP(self.ADDRESS, self.USER, self.PASSWORD)
        self.cleanRemote()

    def tearDown(self) -> None:
        self.cleanRemote()
        self.ftp.close()
        self.cleanArchives()

    def cleanRemote(self):
        for file in self.ftp.nlst():
            self.ftp.delete(file)

    def cleanArchives(self):
        for file in os.listdir(self.TEST_DIR):
            if file.endswith('tar.gz'):
                os.remove(os.path.join(self.TEST_DIR, file))

    def test_create_ftp_loader(self):
        self.assertTrue(issubclass(FtpLoader, Uploader))
        self.assertEqual(self.loader.address, self.ADDRESS)
        self.assertEqual(self.loader.user, self.USER)
        self.assertEqual(self.loader.password, self.PASSWORD)

    def test_upload_and_zip_directory(self):
        directory = os.path.join(self.TEST_DIR, self.UPLOAD_DIR)

        result_archive = self.loader.upload(directory)

        self.assertEqual(result_archive, self.UPLOAD_DIR + '.tar.gz')
        self.assertHasFile(result_archive)

    def test_missed_direcory(self):
        directory = os.path.join(self.TEST_DIR, 'missed_directory')
        with self.assertRaises(UploadError):
            self.loader.upload(directory)

    def test_bad_credentials(self):
        BAD_USER = 'bad_user'
        BAD_PASSWORD = 'bad_password'
        uploader = FtpLoader(self.ADDRESS, BAD_USER, BAD_PASSWORD)
        with self.assertRaises(UploadError):
            uploader.upload(self.UPLOAD_DIR)
