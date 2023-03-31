import unittest
from time import sleep
from unittest.mock import Mock, call

from src.notifier import Status
from src.simulation import Simulation
from src.uploader import UploadError


class SimulationTest(unittest.TestCase):
    MODEL = 'model.xml'

    def setUp(self):
        self.uploader = Mock()
        self.runner = Mock()
        self.notifier = Mock()
        self.workdir = '/path/to/workdir'

        self.simulation = Simulation(
            uploader=self.uploader,
            runner=self.runner,
            notifier=self.notifier
        )

    def test_simulation_stop(self):
        def side_effect(*args):
            sleep(1)
        self.runner.run.side_effect = side_effect

        self.simulation.run(self.workdir, self.MODEL)
        self.assertFalse(self.simulation.is_stoped())

        self.simulation.stop()
        self.simulation.wait()

        self.assertTrue(self.simulation.is_stoped())
        self.runner.stop.assert_called_once()

    def test_stop_stopped_simulation(self):
        with self.assertRaises(RuntimeError):
            self.simulation.stop()

    def test_simulation_run(self):
        self.uploader.upload.return_value = 'test-result.zip'

        self.simulation.run(self.workdir, self.MODEL)
        self.simulation.wait()

        self.runner.run.assert_called_once_with(self.workdir, self.MODEL)

        self.uploader.upload.assert_called_once_with(self.workdir)

        self.notifier.send.assert_has_calls(
            [
                call(Status.START),
                call(Status.UPLOADED, 'test-result.zip'),
                call(Status.END)
            ]
        )

    def test_runner_raise_error(self):
        self.runner.run.side_effect = RuntimeError('error')

        self.simulation.run(self.workdir, self.MODEL)
        self.simulation.wait()

        self.notifier.send.assert_has_calls(
            [
                call(Status.START),
                call(Status.ERROR, 'error')
            ]
        )
        self.uploader.upload.assert_not_called()

    def test_notify_error_on_failed_upload(self):
        self.uploader.upload.side_effect = UploadError('error')
        self.simulation.run(self.workdir, self.MODEL)
        self.simulation.wait()
        self.notifier.send.assert_has_calls([
            call(Status.START), call(Status.ERROR, 'error')
        ])
