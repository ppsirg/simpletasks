import os
import asyncio

from utilities.job import PausedJob
from utilities.file_management import is_dir, list_folders


class CleanFolderJob(PausedJob):
    """Create a backup of source folder in a target folder.
    This utility is meant to be used to restore files in
    external hard drive, so it check if there is enough
    storage space in external drive and avoid non-safe
    data copy operation. Considering linux problems with
    external drive overload, it has pause time so external
    drive can take some pauses in order to avoid hardware errors
    """

    def parse_args(self):
        super().parse_args()
        self.parser.add_argument(
            "target",
            help="folder to clean",
            type=is_dir,
        )
        self.args = self.parser.parse_args()


    async def run(self):
        self.parse_args()
        folders = list_folders(self.args.target)
        for folder in folders:
            self.pool.append(
                self.run_cmd(["rm", "-rfv", os.path.join(self.args.target, folder)])
            )
        await asyncio.gather(*self.pool)


if __name__ == "__main__":
    bk = CleanFolderJob()
    lp = asyncio.get_event_loop()
    lp.run_until_complete(bk.run())
