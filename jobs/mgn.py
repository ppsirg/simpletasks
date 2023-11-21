import os
import yaml
import asyncio
import pdb

from typing import Dict, List
from subprocess import run

from utilities.job import PausedJob
from utilities.file_management import is_dir, is_file, run_in_folder


class MagnetHelperJob(PausedJob):
    """Help open multiple magnets"""

    def parse_args(self):
        super().parse_args()
        self.parser.add_argument(
            "file",
            help="file with magnet links",
            type=is_file,
        )
        self.args = self.parser.parse_args()

    async def run(self):
        self.parse_args()
        to_download = self.load_file()
        lp = asyncio.get_event_loop()
        for magnet in to_download:
            self.pool.append(
                lp.run_in_executor(None, run, ["transmission-gtk", magnet])
            )
        await asyncio.gather(*self.pool)

    def load_file(self) -> List:
        with open(self.args.file) as fl:
            data = self.custom_load(fl)
            return data

    def custom_load(self, file_descriptor) -> Dict:
        txt = file_descriptor.read()
        lines = (cl for a in txt.split("\n") if len((cl := a.strip())) > 1)
        return lines


if __name__ == "__main__":
    bk = MagnetHelperJob()
    lp = asyncio.get_event_loop()
    lp.run_until_complete(bk.run())
