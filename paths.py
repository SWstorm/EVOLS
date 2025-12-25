
import os


def get_data_dir() -> str:
    base = os.environ.get("EVOLS_DATA_DIR")
    if not base:
        home = os.path.expanduser("~")
        base = os.path.join(home, ".evols_vault")
    os.makedirs(base, exist_ok=True)
    return base


def db_path() -> str:
    return os.path.join(get_data_dir(), "passwords.db")


def salt_path() -> str:
    return os.path.join(get_data_dir(), "vault.salt")


def twofa_path() -> str:
    return os.path.join(get_data_dir(), "2fa_secret.key")
