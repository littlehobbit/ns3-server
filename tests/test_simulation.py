import unittest
from unittest.mock import Mock, call
from src.simulation import Simulation
from src.notifier import Status
from src.uploader import UploadError


@unittest.skip('Need to fix simulation running')
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

        # Runner by defult is off
        self.runner.is_running.return_value = False

    def test_simulation_stop(self):
        self.runner.is_running.return_value = True
        self.simulation.stop()
        self.runner.stop.assert_called_once()

    def test_stop_stopped_simulation(self):
        with self.assertRaises(RuntimeError):
            self.simulation.stop()

    def test_simulation_run(self):
        self.uploader.upload.return_value = 'test-result.zip'

        self.simulation.run(self.workdir, self.MODEL)

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
        self.notifier.send.assert_has_calls([
            call(Status.START), call(Status.ERROR, 'error')
        ])
