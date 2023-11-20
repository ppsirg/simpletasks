import os
import shutil
from subprocess import run
from contextlib import contextmanager



image_extensions = (".jpg", ".jpeg", ".png")



@contextmanager
def run_in_folder(folder):
    base_dir = os.getcwd()
    assert_folder(folder)
    os.chdir(folder)
    yield
    os.chdir(base_dir)


def is_img(res: str) -> bool:
    is_file = os.path.isfile(res)
    is_img = any([res.endswith(a) for a in image_extensions])
    return is_img and is_file


def list_img(source) -> list:
    return (a for a in os.listdir(source) if is_img(os.path.join(source, a)))


def list_processed_img(source) -> list:
    return (a for a in os.listdir(source) if a.endswith(".webp"))


def list_folders(target: str):
    return (
        a.strip()
        for a in os.listdir(target)
        if os.path.isdir(os.path.join(target, a.strip()))
    )


def can_backup(filepath: str, target_device: str):
    file_size = get_folder_size(filepath)
    available_space = shutil.disk_usage(target_device).free
    return file_size < available_space


def get_folder_size(filepath: str):
    size = 0
    if os.path.isdir(filepath):
        for path, dirs, files in os.walk(filepath):
            for f in files:
                abs_f = os.path.join(path, f)
                size += os.path.getsize(abs_f)
    else:
        size = os.path.getsize(filepath)
    return size


def assert_folder(path: str) -> str:
    components = (a for a in path.split("/") if a)
    partial = None
    for comp in components:
        if partial:
            partial = os.path.join(partial, comp)
        else:
            partial = f"/{comp}/"
        if not os.path.exists(partial):
            os.mkdir(partial)
    return path


def is_dir(path: str):
    if not os.path.isdir(path):
        raise NotADirectoryError
    else:
        return path
    

def is_file(path: str):
    if not os.path.isfile(path):
        raise NotADirectoryError
    else:
        return path



def move_content(content: str, target: str):
    order = ["cp", "-vr", content, target]
    run(order, check=True)
