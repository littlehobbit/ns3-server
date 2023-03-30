from src.runner import Runner
from src.uploader import Uploader
from src.notifier import Notifier, Status


class Simulation:
    """ This class has responsobility to running requested simulation and providing results to client """
    runner: Runner
    uploader: Uploader
    notifier: Notifier

    def __init__(self, runner: Runner, uploader: Uploader, notifier: Notifier):
        self.runner = runner
        self.uploader = uploader
        self.notifier = notifier

    async def run(self, workdir: str, file_name: str):
        self.notifier.send(Status.START)

        try:
            self.runner.run(workdir, file_name)
            await self.runner.wait()
            resulted_zip = self.uploader.upload(workdir)
        except Exception as err:
            self.notifier.send(Status.ERROR, str(err))
            return

        self.notifier.send(Status.UPLOADED, resulted_zip)
        self.notifier.send(Status.END)

    def stop(self):
        if self.is_stoped():
            raise RuntimeError()
        self.runner.stop()

    def is_stoped(self):
        return not self.runner.is_running()
