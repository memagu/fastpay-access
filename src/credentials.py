import logging
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values

from westpay_access import WestpayAccess

DOTENV_PATH = Path("./.env")


def get_cached_credentials() -> Optional[tuple[str, str]]:
    credentials = dotenv_values()

    if not credentials:
        return

    username = credentials["WESTPAY_USERNAME"]
    password = credentials["WESTPAY_PASSWORD"]

    if username and password:
        return username, password


def check_credentials(username: str, password: str) -> bool:
    wpa = WestpayAccess()
    return wpa.login(username, password)


def save_credentials(username: str, password: str, file: Path) -> None:
    if not file.parent.exists():
        file.parent.mkdir(parents=True)

    file.write_text('\n'.join((f"WESTPAY_USERNAME={username}", f"WESTPAY_PASSWORD={password}")))


def prompt_and_cache_credentials() -> tuple[str, str]:
    while True:
        username, password = input("Enter username: "), input("Enter password: ")
        if check_credentials(username, password):
            save_credentials(username, password, DOTENV_PATH)
            return username, password

        logging.warning("Invalid username or password. Try again!")
