import asyncio
import signal
from concurrent.futures import ThreadPoolExecutor
from subprocess import PIPE, Popen
from threading import Thread
import os

from flask import current_app as app

from src.log import logger
from src.notifier import Notifier, Status
from src.runner import Runner

from io import TextIOWrapper


class SimulationRunner(Runner):
    executable: str
    notifier: Notifier
    _running = True
    process = None

    def __init__(self, executable: str, notifier: Notifier):
        self.executable = executable
        self.notifier = notifier

    def run(self, cwd: str, model_file: str):
        self._execute_process(cwd, model_file)

    def _notify_line(self, status: Status, line: str):
        line = line.strip()
        if len(line) > 0:
            self.notifier.send(status, line)

    def is_running(self) -> bool:
        if self.process is not None:
            return self.process.poll() is None
        return False

    def stop(self):
        if self.process is not None and self.is_running():
            self.process.send_signal(signal.SIGTERM)

    def wait(self):
        if self.process is not None:
            self.process.wait()

    def _execute_process(self, cwd: str, model_file: str):
        logger.debug('Start simulation process')
        with Popen(args=[self.executable, '--xml', model_file],
                   cwd=cwd, text=True, universal_newlines=True,
                   stdout=PIPE, stderr=PIPE) as process:
            self.process = process
            stdout, stderr = process.stdout, process.stderr

            os.set_blocking(stdout.fileno(), False)
            os.set_blocking(stderr.fileno(), False)

            while process.poll() is None:
                if stdout.readable():
                    self._notify_line(Status.LOG, stdout.readline())

                # BUG: stderr blocks execution
                # if stderr.readable():
                #     from_stderr = stderr.read()
                #     self._notify_line(Status.ERROR, from_stderr)

            for last_out in stdout.readlines():
                self._notify_line(Status.LOG, last_out)

            for last_err in stderr.readlines():
                self._notify_line(Status.ERROR, last_err)

            return_code = process.wait()
            if return_code != 0:
                err = f'Simulation ended with return code {return_code}'
                logger.error(err)
                self.notifier.send(Status.ERROR, err)
