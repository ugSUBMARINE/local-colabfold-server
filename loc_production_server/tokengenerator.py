import string
import random
from app_utils import file_path_dict

FILE_PATHS = file_path_dict()


TOKEN_BASE_PATH = f"{FILE_PATHS['loc_prod_path']}/tokens/"


def gen_token(num_token: int) -> None:
    """generate new registered_tokens
    :parameter
        - num_token:
          Number of tokens to create
    :return
        - None
    """
    alphabet = list(string.ascii_uppercase)
    alphabet = [i for i in alphabet if i != "O"]
    tokens = []
    for i in range(num_token):
        tokens.append("".join(random.choices(alphabet, k=10)))
    with open(f"{TOKEN_BASE_PATH}registered_tokens.txt", "a+") as tok_file:
        for i in tokens:
            tok_file.write(i + "\n")


def add_used(token: str) -> None:
    """add a used token to the list of currently used tokens
    :parameter
        - token:
          the token to check
    :return
        - None
    """
    with open(f"{TOKEN_BASE_PATH}used_tokens.txt", "a") as running:
        running.write(token + "\n")


def remove_used(token: str) -> None:
    """remove the used token when job is finished
    :parameter
        - token:
          the token to check
    :return
        - None
    """
    all_tokens = []
    found_token = False
    with open(f"{TOKEN_BASE_PATH}used_tokens.txt", "r") as running:
        for i in running:
            if token == i.strip() and not found_token:
                found_token = True
            else:
                all_tokens.append(i)
    with open(f"{TOKEN_BASE_PATH}used_tokens.txt", "w+") as readd:
        for i in all_tokens:
            readd.write(i)


def check_used_token(token: str, max_runs: int = 2) -> bool:
    """check how often the token is currently used
    :parameter
        - token:
          the token to check
        - max_runs:
          how often a token can be used at the same time
    :return
        - whether the token is already used as many times as allowed
    """
    cur_used = sum(
        1 for i in open(f"{TOKEN_BASE_PATH}used_tokens.txt", "r") if token == i.strip()
    )
    if cur_used > max_runs:
        return False
    else:
        return True


def check_token_valid(token: str) -> bool:
    """check if a entered token is an existing one
    :parameter
        - token:
          the token to check
    :return
        - whether the token is a registered valid token
    """
    registered_tokens = []
    reg_pass = False
    with open(f"{TOKEN_BASE_PATH}registered_tokens.txt", "r") as reg_tokens:
        for i in reg_tokens:
            if token == i.strip():
                reg_pass = True
                break
    return reg_pass


if __name__ == "__main__":
    pass
    # gen_token(5)
    remove_used("2a")
    print(check_used_token("2a", 1))
    print(check_token_valid("2a"))
