import argparse

from tokengenerator import remove_used

parser = argparse.ArgumentParser(description="Remove used token")
parser.add_argument("--token", type=str)
args = parser.parse_args()
to_remove = args.token

remove_used(to_remove)

