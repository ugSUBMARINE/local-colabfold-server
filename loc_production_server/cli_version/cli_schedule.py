import os
import sys
import argparse
from datetime import datetime
sys.path.append((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from make_bash import make_bash_file
                                                                                   
parser = argparse.ArgumentParser(description="Add bash commands")
parser.add_argument(                                                                
"-n", "--name", type=str, required=True, help="name of the generated script"           
)                                                                                   
parser.add_argument(                                                                
"-c", "--commands", type=str, required=True, help="',' seperated bash commands that should be added in a script"           
)                                                                                   
args = parser.parse_args()
make_bash_file(f"{args.name}.sh", args.commands.split(","))
