import os
import asyncio
from utilities.job import PausedJob
from utilities.file_management import (
    list_folders,
    list_img,
    list_processed_img,
    assert_folder,
    run_in_folder,
    image_extensions,
)


class DeflateImageJob(PausedJob):
    """Deflate images to high quality webp format, given a folder
    it search all images and turn them into webp images that are more
    size efficient.
    """

    destination_pref = "_mn"
    image_quality = "80"

    def parse_args(self):
        super().parse_args()
        self.parser.add_argument("target", help="absolute path to target folder")
        self.parser.add_argument(
            "--mode",
            help="describe where are files, folder if images are in target folder, root if images are in first depth of target folder",
            default="root",
            choices=("root", "folder"),
        )
        self.args = self.parser.parse_args()

    async def run(self):
        self.parse_args()
        if self.args.mode == "root":
            await self.root_folder(self.args.target)
        elif self.args.mode == "folder":
            await self.single_folder(self.args.target)

    async def single_folder(self, target: str):
        """Compress image files inside a folder (target argument)"""
        target = target[:-1] if target.endswith(os.path.sep) else target
        root_folder = os.path.dirname(target)
        with run_in_folder(root_folder):
            source_dir = target
            target_dir = os.path.join(
                root_folder, f"{os.path.basename(target)}_{self.destination_pref}"
            )
            assert_folder(target_dir)

            await self.copy_processed(source_dir, target_dir)
            await self.compress_img(source_dir, target_dir)
            await self.copy_processed(source_dir, target_dir)

    async def root_folder(self, target: str):
        """Compress image files of folders located in root
        folder (target argument), first depth level
        in folder tree.
        """
        folders = list_folders(target)

        with run_in_folder(target):
            _ = [
                assert_folder(os.path.join(target, f"{a}_{self.destination_pref}"))
                for a in folders
            ]
            copy_job = [
                self.copy_processed(
                    os.path.join(target, a),
                    os.path.join(target, f"{a}_{self.destination_pref}"),
                )
                for a in folders
            ]
            await asyncio.gather(*copy_job)

            compress_job = [
                self.compress_img(
                    os.path.join(target, a),
                    os.path.join(target, f"{a}_{self.destination_pref}"),
                )
                for a in folders
            ]
            print(compress_job)
            await asyncio.gather(*compress_job)

            copy_job = [
                self.copy_processed(
                    os.path.join(target, a),
                    os.path.join(target, f"{a}_{self.destination_pref}"),
                )
                for a in folders
            ]
            await asyncio.gather(*copy_job)

    async def copy_processed(self, source, target):
        resources = list_processed_img(source)
        lp = asyncio.get_event_loop()
        pool = []
        for item in resources:
            info = self.run_cmd(["mv", f"{source}/{item}", target])
            pool.append(info)
        return await asyncio.gather(*pool)

    async def compress_img(self, source, target):
        resources = list_img(source)

        with run_in_folder(source):
            process_pool = []
            lp = asyncio.get_event_loop()
            for img in resources:
                order = [
                    "cwebp",
                    "-quiet",
                    "-q",
                    self.image_quality,
                    os.path.join(source, img),
                    "-o",
                    os.path.join(target, self.webp_replace(img)),
                ]
                process_pool.append(self.run_cmd(order))
            resp = await asyncio.gather(*process_pool)

        return resp

    @staticmethod
    def webp_replace(self, img: str):
        for xts in image_extensions:
            if img.endswith(xts):
                return img.replace(xts, ".webp")


if __name__ == "__main__":
    bk = DeflateImageJob()
    lp = asyncio.get_event_loop()
    lp.run_until_complete(bk.run())
