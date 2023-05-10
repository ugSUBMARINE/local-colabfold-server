from datetime import datetime
import string
import random
import os

from app_utils import file_path_dict
FILE_PATHS = file_path_dict()


def make_bash_file(name: str, lines: list[str]):
    """
    generate bash scripts that should be executed
    :parameter
        - name:
          name of the script that should be generated
        - lines:
          lines of the bash script
    :return
        - None
    """
    # path where schedule is stored
    base_path = f"{FILE_PATHS['loc_prod_path']}/schedule/"
    # create needed directories if they are not present
    if not os.path.isdir(base_path):
        os.mkdir(base_path)
    if not os.path.isdir(base_path + "exe_scripts"):
        os.mkdir(base_path + "exe_scripts")

    # name of the script to execute
    new_name = f"{base_path}exe_scripts/{name.split('.')[0]}.sh"
    
    # create the bash script
    with open(new_name, "w+") as bashfile:
        bashfile.write("#!/bin/bash\n")
        for i in lines:
            bashfile.write(str(i) + "\n")
    # add bash script to queue
    exe_shed_path = f"{base_path}execution_shedule.txt"
    if not os.path.isfile(exe_shed_path):
        with open(exe_shed_path, "a+") as ef:
            pass
        os.system(f"chmod +rw {exe_shed_path}")
        os.system(f"chmod o+w {exe_shed_path}")
    with open(exe_shed_path, "a+") as exe_shed:
        exe_shed.write("LOCKED " + new_name + "\n")


if __name__ == "__main__":
    pass
    make_bash_file("test2.sh", ["/bin/bash /home/cfolding/local-colabfold-server/loc_production_server/test.sh"])
