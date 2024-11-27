import os
import secrets
from datetime import datetime
import re
import json

from flask import flash, escape
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(["fasta", "fa", "json"])


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
            python_path = file_path_dict()["python_path"]
            os.system(f"{python_path} tokenremove.py --token {token_as}")
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


def protein_check(data: dict) -> int:
    """
    check how many amino acids are in a AF3 dict
        :parameter
        - data:
          the dict to check
        :return
        - total_len:
          number of found amino acids
    """
    seq_data = data["sequences"]
    total_len = 0
    for i in seq_data:
        if "protein" in i.keys():
            i_prot_data = i["protein"]
            if "id" in i_prot_data and "sequence" in i_prot_data:
                i_n_chains = len(i_prot_data["id"])
                i_len_seq = len(i_prot_data["sequence"])
                i_total_len = i_n_chains * i_len_seq
                total_len += i_total_len
        elif "ligand" in i.keys():
            i_lig = i["ligand"]
            if "smiles" in i_lig.keys():
                i_smiles = (
                    i_lig["smiles"]
                    .replace("(", "")
                    .replace(")", "")
                    .replace("[", "")
                    .replace("]", "")
                    .replace("_", "")
                    .replace(".", "")
                )
                total_len += len(i_smiles)
    return total_len


def json_check(path: str, max_seqlen: int = 3500, max_protein: int = 3) -> int:
    """
        :parameter
        - path:
          path to the json file
        - max_seqlen:
          maximum number of amino acids in the file
        - max_protein:
          how many protein sequences can be in the fasta file
    :return
        - int
          0 if everything is fine
          1 if json in malformatted
          2 if to many proteins are found
          3 if to many amino acids are found
    """
    with open(path, "r") as jfile:
        try:
            data = json.load(jfile)
        except json.decoder.JSONDecodeError:
            return 1
        if isinstance(data, list):
            valid_all = False
            if len(data) <= max_protein:
                for i in data:
                    valid_all = protein_check(i) <= max_seqlen
                if valid_all:
                    return 0
                else:
                    return 3
            else:
                return 2
        elif isinstance(data, dict):
            if protein_check(data) <= max_seqlen:
                return 0
            else:
                return 3
        else:
            return 1


def remove_token_after_crash(token_in: str) -> None:
    """remove token from in used ones on invalid input
    :parameter
        - token_in:
          the token
    :return
        - None
    """
    python_path = file_path_dict()["python_path"]
    os.system(f"{python_path} tokenremove.py --token {token_in}")


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
    return " " + nmodels_add + amber_rel_add + nrecyles_add


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


def file_path_dict() -> dict:
    """
    :parameter
        - None
    :return
        - path_dict
          dictionary specifying all paths needed
    """
    with open(
        "/home/cfolding/local-colabfold-server/directory_specification.txt"
    ) as dir_file:
        path_dict = {}
        for i in dir_file:
            if not i.startswith("#"):
                i_split = i.strip().split(":")
                if len(i_split[0]) > 0:
                    path_dict[i_split[0]] = ":".join(i_split[1:])
        return path_dict
