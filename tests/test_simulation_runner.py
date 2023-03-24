import os
import tempfile
import unittest
from unittest.mock import Mock, call

import asyncio
from src.simulation_runner import SimulationRunner
from src.notifier import Status


class SimulationRunnerTest(unittest.IsolatedAsyncioTestCase):
    EXECUTABLE: str = '/media/gataullin/FLASHKA/Project/simulation-core/build/simulation'
    MODEL_FILE: str = 'model.xml'

    temp_test_dir: str
    runner: SimulationRunner
    notifier: Mock = Mock()

    def setUp(self):
        self.temp_test_dir = os.path.join(os.getcwd(), 'tests')
        self.runner = SimulationRunner(self.EXECUTABLE, self.notifier)

    async def test_run(self):
        self.runner.run(self.temp_test_dir, self.MODEL_FILE)
        self.assertTrue(self.runner.is_running())

        await self.runner.wait()

        self.assertFalse(self.runner.is_running())

        # assert has logs
        self.assertGreater(self.getNotifiedCount(Status.LOG), 0)
        # assert no errors
        self.assertEqual(self.getNotifiedCount(Status.ERROR), 0)

    async def test_stop_after_run(self):
        self.runner.run(self.temp_test_dir, self.MODEL_FILE)
        self.assertTrue(self.runner.is_running())
        self.runner.stop()

        with self.assertRaises(asyncio.CancelledError):
            await self.runner.wait()
        self.assertFalse(self.runner.is_running())

    def getNotifiedCount(self, status: Status) -> int:
        args_list = self.notifier.send.call_args_list
        return len(
            [1 for first_arg, _ in args_list if first_arg[0] == status]
        )
