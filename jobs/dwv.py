import os
import yaml
import asyncio
import pdb

from typing import Dict, List

from yt_dlp import YoutubeDL

from utilities.job import PausedJob
from utilities.file_management import is_dir, is_file, run_in_folder


class DownloadJob(PausedJob):
    """Download videos in a file in folders"""

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
        for target, vid_list in to_download.items():
            with run_in_folder(os.path.join(self.args.target, target)):
                pool = []
                for vid in vid_list:
                    pool.append(self.download_video(vid))
                await asyncio.gather(*pool)

    def load_file(self) -> List:
        with open(self.args.file) as fl:
            try:
                data = yaml.safe_load(fl.read())
            except Exception as err:
                print(type(err), err)
                fl.seek(0)
                data = self.custom_load(fl)
            finally:
                return data

    def custom_load(self, file_descriptor) -> Dict:
        txt = file_descriptor.read()
        lines = (cl for a in txt.split("\n") if len((cl := a.strip())) > 1)
        data = {}
        current_folder = "default"
        for ln in lines:
            if ln.startswith("#"):
                folder_name = ln[1:]
                data[folder_name] = []
                current_folder = folder_name
            else:
                data[current_folder].append(ln)
        return data

    async def download_video(self, vid_url):
        with YoutubeDL() as ydl:
            try:
                ydl.download([vid_url])
            except Exception as err:
                self.notify(f"[{type(err)}] -> {err}")
        # return await self.run_cmd(['poetry', 'run','yt_dlp', vid_url])


if __name__ == "__main__":
    bk = DownloadJob()
    lp = asyncio.get_event_loop()
    lp.run_until_complete(bk.run())
