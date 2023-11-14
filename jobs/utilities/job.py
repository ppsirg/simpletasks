import asyncio
import argparse
from time import time
from functools import partial
from subprocess import run
from concurrent.futures import ThreadPoolExecutor


class CommandLineJob:
    """
    This code defines a class called CommandLineJob in Python.
    It includes various methods for executing command line commands,
    sending notifications, and parsing command line arguments.

    """

    DEBUG = False
    pool = []
    parser = None
    args = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs) -> None:
        self.px = ThreadPoolExecutor(max_workers=5)

    @staticmethod
    def _wrp_run_cmd(command):
        """The class has a static method called _wrp_run_cmd()
        which takes a command as input and executes it using the 'run' function.
        If an exception occurs during the execution,
        the error is printed and None is returned."""
        try:
            rsp = run(command, check=True)
        except Exception as err:
            print(err)
            rsp = None
        finally:
            return rsp

    @staticmethod
    def print_by_lines(items):
        for item in items:
            print(f"- {item}")

    def notify(self, msg):
        """The notify() method sends a desktop notification using the
        'notify-send' command and also prints the message."""
        order = ["notify-send", msg]
        run(order)
        print(f"-->> {msg}")

    def notify_resume(self, msg, success=[], failure=[]):
        """that takes in a message, a list of successful items,
        and a list of failed items. It then prints the message
        and lists the successful and failed items if they are provided.
        """
        self.notify("job finished")
        print(msg)
        if success:
            print("succeded:\n")
            self.print_by_lines(success)
        if failure:
            print("failed:\n")
            self.print_by_lines(failure)

    def parse_args(self):
        """The parse_args() method initializes the argument
        parser for command line arguments.
        """
        self.parser = argparse.ArgumentParser(description=self.__doc__)

    async def run(self):
        """The run() method is an asynchronous method that
        calls the parse_args() method."""
        self.parse_args()


class PausedJob(CommandLineJob):
    max_time = 10 * 60
    start_time = None
    stop_time = 60

    def __init__(self, *args, **kwargs) -> None:
        self.start_time = time()
        super().__init__(*args, **kwargs)

    @property
    def is_elapsed(self):
        tm = time()
        return (tm - self.start_time) > self.max_time

    async def run_cmd(self, command):
        lp = asyncio.get_event_loop()
        if self.is_elapsed:
            self.notify("start waiting to save disk")
            await asyncio.sleep(self.stop_time)
            self.notify("resume job")
            self.start_time = time()
        rs = await lp.run_in_executor(self.px, self._wrp_run_cmd, command)
        return rs
