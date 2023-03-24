import asyncio

from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from subprocess import PIPE, Popen
from signal import SIGSTOP

from src.notifier import Notifier, Status
from src.runner import Runner


class SimulationRunner(Runner):
    executable: str
    notifier: Notifier
    _running = True
    _task: asyncio.Task

    def __init__(self, executable: str, notifier: Notifier):
        self.executable = executable
        self.notifier = notifier

    def run(self, cwd: str, model_file: str):
        self._task = asyncio.get_event_loop().create_task(
            self._execute_process(cwd, model_file))

    def _notify_line(self, status: Status, line: str):
        line = line.strip()
        if len(line) > 0:
            self.notifier.send(status, line)

    def is_running(self) -> bool:
        if self._task is None:
            return False
        else:
            return not self._task.done() and not self._task.cancelled()

    def stop(self):
        if self._task is not None:
            self._task.cancel()

    async def wait(self):
        if self._task is not None:
            await self._task

    async def _execute_process(self, cwd, model_file):
        process = Popen(
            args=[self.executable, '--xml', model_file],
            cwd=cwd,
            text=True,
            universal_newlines=True,
            stdout=PIPE, stderr=PIPE
        )

        try:
            with process as process:
                stdout, stderr = process.stdout, process.stderr

                while process.poll() is None:
                    if stdout.readable():
                        self._notify_line(Status.LOG, stdout.readline())
                    if stderr.readable():
                        self._notify_line(Status.ERROR, stderr.readline())

                for last_out in stdout.readlines():
                    self._notify_line(Status.LOG, last_out)
                for last_err in stderr.readlines():
                    self._notify_line(Status.LOG, last_err)

                return_code = process.wait()
                if return_code != 0:
                    self.notifier.send(
                        Status.ERROR, f'simulation ended with return code {return_code}')
        except asyncio.CancelledError as cancel:
            if process.poll() is None:
                process.send_signal(SIGSTOP)

# def _loop():
#     loop = asyncio.new_event_loop()
#     loop.run_forever()

# thread = Thread(target=_loop)

# try:
#     thread.run()
# except (KeyboardInterrupt, SystemExit):
#     # Stop Thread when CTRL + C is pressed or when program is exited
#     thread.join()
