import os
import secrets
from datetime import datetime
import re

from flask import flash, escape
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(["fasta", "fa"])


def gen_key(dir_name: str = "log_files") -> None:
    """generate secret key and store it in file
    :parameter
        - dir_name:
          path to directory where key should be stored
    :return
        - None
    """
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
    skey_path = os.path.join(dir_name, "skey.txt")
    if not os.path.isfile(skey_path):
        with open(skey_path, "w+") as key_file:
            key_file.write(secrets.token_urlsafe(24))


def get_key(dir_name: str = "log_files") -> str:
    """read secret key file and return key in b''
    :parameter
        - dir_name:
          path to directory where the key is stored
    :return
        - secret key
    """
    with open(os.path.join(dir_name, "skey.txt"), "r") as key_file:
        return key_file.readline().strip().encode()


def allowed_file(filename: str) -> bool:
    """which file extension is allowed as set in ALLOWED_EXTENSIONS
    :parameter
        - filename:
          file to be checked
    :return
        - bool
          whether file is valid or not
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_string(
    in_string: str, info: str, token_as: str = None, remove_token: bool = False
):
    """check if string is operating system safe
    :parameter
        - in_string:
          string to be checked
        - info:
          the info that should be flashed on the site if input is wrong
        - token_as:
          which token supplied this string
        - remove_token:
          whether the token should be removed
    :return
        - bool
          true if the input was valid
        - filename
          None if input was invalid or secure version if it was valid
    """
    if in_string is None:
        info = "Input is None"
        return False, None
    else:
        in_string = str(in_string)
        check = bool(re.match("^[A-Za-z0-9_-]+[A-Za-z0-9_.-]*$", in_string))
    if not check:
        flash(info)
        if remove_token:
            os.system(f"python3 tokenremove.py --token {token_as}")
        return False, None
    else:
        return True, secure_filename(escape(in_string))


def fasta_check(fasta_path: str, max_protein: int = 3, max_seqlen=2500) -> int:
    """check fasta file for number of sequences and amino acids
    :parameter
        - fasta_path:
          path to the fasta file
        - max_protein:
          how many protein sequences can be in the fasta file
        - max_seqlen:
          maximum number of amino acids in the file
    :return
        - int
          0 if everything is fine
          1 if no fasta header was foung
          2 if to many headers (sequences) were found
          3 if to many amino acids were found
    """
    header_count = 0
    seq_len = 0
    with open(fasta_path, "r") as fasta:
        for i in fasta:
            if i.startswith(">"):
                header_count += 1
            else:
                seq_len += len(i.strip())
                if seq_len > max_seqlen:
                    return 3
            if header_count > max_protein:
                return 2
    if header_count == 0:
        return 1
    elif header_count > max_protein:
        return 2
    return 0


def remove_token_after_crash(token_in: str) -> None:
    """remove token from in used ones on invalid input
    :parameter
        - token_in:
          the token
    :return
        - None
    """
    os.system(f"python3 tokenremove.py --token {token_in}")


def add_string(nmodels: str, amber_rel: str, nrecyles: str):
    """get additional setting in the colabfold call string
    :parameter
        - nmodels:
          number of models that should be generated
        - amber_rel:
          if amber realax should be used
        - nrecyles:
          number of recycles
    :return
        - str
          string containing the additional parameters
    """
    nmodels_add = f"--num-models {nmodels}"
    amber_rel_add = ""
    if amber_rel == "amber_relax":
        amber_rel_add = " --amber --use-gpu-relax"
    nrecyles_add = ""
    if nrecyles != "auto":
        nrecyles_add = f" --num-recycle {nrecyles}"
    return " " + nmodels_add + amber_rel_add + nrecyles_add + " --zip"


def ip_log(req, access: str, fpath: str = "log_files"):
    """log the ip addresses that access the sites
    :parameter
        - req:
          the request body
        - access:
          name of the site htat was accessed
        - fapth:
          filepath where the log is stored
    :return
        - func1return
          description
    """
    ip_addr = req.environ.get("HTTP_X_FORWARDED_FOR", req.remote_addr)
    with open(os.path.join(fpath, "ip.log"), "a+") as iplog:
        ip_string = f"{datetime.now().strftime('%d%m%y_%H%M%S')},{ip_addr},{access}\n"
        iplog.write(ip_string)


# append_queue("test2")
# os.system("tail -n +2 log_files/queued.txt")