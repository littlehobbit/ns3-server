import os
import tempfile
from datetime import datetime
from threading import Thread

import xmltodict

from src.log import logger
from src.notifier import Notifier, Status
from src.runner import Runner
from src.uploader import Uploader


class Simulation:
    """ This class has responsobility to running requested simulation and providing results to client """
    runner: Runner
    uploader: Uploader
    notifier: Notifier
    _thread: Thread = None

    def __init__(self, runner: Runner, uploader: Uploader, notifier: Notifier):
        self.runner = runner
        self.uploader = uploader
        self.notifier = notifier

    def run_model_xml(self, xml: str):
        model_name = self.get_model_name(xml)

        workdir = self.create_model_directory(model_name)
        logger.info(f'Create workdir {workdir}')

        config = self.write_xml_model(workdir, xml)
        logger.info(f'Write xml configuration to {config}')

        logger.info(f'Start new simulation "{model_name}"')
        self.run(workdir, config)

    def get_model_name(self, xml: str) -> str:
        xml = xmltodict.parse(xml)
        return xml['model']['@name']

    def create_model_directory(self, model_name: str) -> str:
        return tempfile.mkdtemp(
            prefix=model_name + '-',
            suffix='-{date:%Y-%m-%d_%H:%M:%S}'.format(date=datetime.now())
        )

    def write_xml_model(self, dir: str, xml: str) -> str:
        config = os.path.join(dir, 'model.xml')
        with open(config, 'wb') as config_file:
            config_file.write(xml)
        return config

    def run(self, workdir: str, file_name: str):
        if self.is_running():
            raise RuntimeError('Attempt to start running simulation')

        self._thread = Thread(target=self._do_run,
                              args=[workdir, file_name])
        self._thread.start()

    def _do_run(self, workdir: str, file_name: str):
        try:
            self.notifier.send(Status.START)
            self.runner.run(workdir, file_name)
            resulted_zip = self.uploader.upload(workdir)
            self.notifier.send(Status.UPLOADED, resulted_zip)
            self.notifier.send(Status.END)
        except Exception as err:
            logger.exception('Simulation error')
            self.notifier.send(Status.ERROR, str(err))
    


    def stop(self):
        if self.is_stoped():
            raise RuntimeError('Can not stop: no simulation is running')
        self.runner.stop()

    def wait(self):
        if self._thread is not None:
            self._thread.join()

    def is_stoped(self) -> bool:
        return self._thread is None or not self._thread.is_alive()

    def is_running(self) -> bool:
        return not self.is_stoped()
