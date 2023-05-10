#!/usr/bin/python3
from app_utils import file_path_dict
FILE_PATHS = file_path_dict()
prev_time = None
prev_data = None
keep = []
with open(f"{FILE_PATHS['loc_prod_path']}/log_files/ip.log", "r") as oip:
    for ci, i in enumerate(oip):
        i = i.strip().split(",")
        itime = int(i[0].split("_")[-1])
        idata = "".join(i[1:])
        if i == 0:
            prev_time = itime
            prev_data = idata
            keep.append(i)
        else:
            if any(
                [(idata == prev_data and prev_time - itime > 120), idata != prev_data]
            ):
                keep.append(i)
                prev_data = idata
                prev_time = itime

with open(f"{FILE_PATHS['loc_prod_path']}/log_files/ip.log", "w+") as nip:
    for i in keep:
        nip.write(",".join(i) + "\n")

if __name__ == "__main__":
    pass
