import argparse
from subprocess import PIPE, Popen
from app_utils import file_path_dict


def af_commit_to_log():
    parser = argparse.ArgumentParser(description="Get commit hash AF3")
    parser.add_argument("--log_path", type=str, help="Path to log file")
    parser.add_argument(
        "--git_path",
        type=str,
        default="git_path",
        required=False,
        help="Path to git repository",
    )
    parser.add_argument(
        "--af_version",
        type=str,
        default="Alphafold3",
        required=False,
        help="Alphafold version",
    )
    args = parser.parse_args()
    logfile_path = args.log_path
    try:
        af_version = "Alphafold3"
        p = Popen(
            ["git", "-C", file_path_dict()[args.git_path], "rev-parse", "HEAD"],
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = p.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        if len(stderr) == 0:
            with open(logfile_path, "a+") as lfile:
                lfile.write(f"{af_version} is running on commit: {stdout.strip()}\n")
        else:
            with open(logfile_path, "a+") as lfile:
                lfile.write(
                    f"Error while retrieving {af_version} commit: {stderr.strip()}\n"
                )
    except Exception as e:
        with open(logfile_path, "a+") as lfile:
            lfile.write(f"Error while retrieving {af_version} commit: {e}\n")


if __name__ == "__main__":
    af_commit_to_log()
