import os
import zipfile
import argparse
import warnings
import shutil


def zipping(exclude_dir: str = "_env") -> None:
    """zip directory and remove it afterwards
    :parameter
        - exclude_dir:
          exclude directories with this string in name
    :return
        - None
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-f", "--filepath", type=str, required=True, help="path to directory"
    )
    parser.add_argument(
        "-d",
        "--destination",
        type=str,
        required=True,
        help="path to the zip files destination e.g. mydir.zip",
    )

    # filepath
    args = parser.parse_args()
    path_dir = args.filepath
    path_dest = args.destination
    if not path_dest.endswith(".zip"):
        path_dest = path_dest + ".zip"
    # if file exists
    if os.path.isdir(path_dir):
        # zip the directory
        with zipfile.ZipFile(path_dest, "w") as zipdest:
            for root, dirs, files in os.walk(path_dir, topdown=True):
                dirs[:] = [d for d in dirs if "_env" not in d]
                for f in files:
                    zipdest.write(os.path.join(root, f), f)
        # check for symlinks and remove dir if none exist in this dir
        dir_content = os.scandir(path_dir)
        for i in dir_content:
            if i.is_symlink():
                warnings.warn(
                    "Found a symlink in the directory that should be zippen"
                    "- directory won't be removed"
                )
                return
        shutil.rmtree(path_dir)
    else:
        raise FileNotFoundError(f"File {path_dir} that should be zipped doesn't exist")


if __name__ == "__main__":
    zipping()
