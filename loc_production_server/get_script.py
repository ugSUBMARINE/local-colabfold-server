import os

from app_utils import file_path_dict

FILE_PATHS = file_path_dict()

# check if schdule exists
exe_sched_path = f"{FILE_PATHS['loc_prod_path']}/schedule/execution_shedule.txt"
if os.path.isfile(exe_sched_path):
    all_lines = []
    # True if none of the scripts are running
    all_locked = True
    # get all scheduled scripts
    with open(exe_sched_path, "r") as all_scripts:
        for i in all_scripts:
            all_lines.append(i)
            if not i.startswith("LOCKED"):
                all_locked = False
    if all_locked and len(all_lines) > 0:
        first_line = all_lines[0].replace("LOCKED", "")
        print(first_line.strip())
        with open(exe_sched_path, "w+") as new_scripts:
            for ci, i in enumerate(all_lines):
                if ci == 0:
                    new_scripts.write(first_line)
                else:
                    new_scripts.write(i)
    else:
        print("WAIT")
else:
    print("WAIT")
