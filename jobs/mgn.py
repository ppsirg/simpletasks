import os
import yaml
import asyncio
import pdb

from typing import Dict, List

from utilities.job import PausedJob
from utilities.file_management import is_dir, is_file, run_in_folder


class MagnetHelperJob(PausedJob):
    """Help open multiple magnets"""

    def parse_args(self):
        super().parse_args()
        self.parser.add_argument(
            "file",
            help="file to search",
            type=is_file,
        )
        self.parser.add_argument(
            "target",
            help="folder to clean",
            type=is_dir,
        )
        self.args = self.parser.parse_args()

    async def run(self):
        self.parse_args()
        to_download = self.load_file()
        for magnet in to_download:
            await self.run_cmd(
                ["transmission-cli", "-w", self.args.target, "-v", magnet], px=None
            )
            # await self.run_cmd(['transmission-gtk', magnet])
            self.notify(f"descargando {magnet[-10:]}")
            await asyncio.sleep(5)
            print("---")

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
