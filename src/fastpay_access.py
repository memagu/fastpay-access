import sys
import logging

from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem

from credentials import check_credentials, get_cached_credentials, prompt_and_cache_credentials
from westpay_access import WestpayAccess, Transactions
from util import display_transactions, pause, prompt_iso_date


def login() -> WestpayAccess:
    credentials = get_cached_credentials()
    if credentials is None or not check_credentials(*credentials):
        logging.warning("Stored credentials are invalid")
        username, password = prompt_and_cache_credentials()
    else:
        username, password = credentials

    wpa = WestpayAccess()
    wpa.login(username, password)

    return wpa


def fetch_customer_transactions() -> Transactions:
    logging.info("Creating session ...")
    wpa = login()

    serial_number = input("Enter the serial number of a terminal: ")
    start = prompt_iso_date("Enter the start date and time in ISO format (YYYY-MM-DDTHH:MM): ")
    end = prompt_iso_date("Enter the end date and time in ISO format (YYYY-MM-DDTHH:MM): ")

    logging.info("Downloading terminal information ...")
    terminals = wpa.get_terminals()

    logging.info(f"Getting information for S/N: {serial_number} ...")
    terminal = next((terminal for terminal in terminals if terminal.serial_number == serial_number))

    logging.info(f"Fetching transactions for {terminal.customer} between {start.isoformat()} and {end.isoformat()} ...")
    return wpa.get_transactions(terminal.customer_id, start, end)


def fetch_terminal_transactions() -> Transactions:
    logging.info("Creating session ...")
    wpa = login()

    serial_number = input("Enter the serial number of the terminal: ")
    start = prompt_iso_date("Enter the start date and time in ISO format (YYYY-MM-DDTHH:MM): ")
    end = prompt_iso_date("Enter the end date and time in ISO format (YYYY-MM-DDTHH:MM): ")

    logging.info("Downloading terminal information ...")
    terminals = wpa.get_terminals()

    logging.info(f"Getting information for S/N: {serial_number} ...")
    terminal = next((terminal for terminal in terminals if terminal.serial_number == serial_number))

    logging.info(f"Fetching transactions for {serial_number} at {terminal.customer} between {start.isoformat()} and {end.isoformat()} ...")
    transactions = wpa.get_transactions(terminal.customer_id, start, end)
    return tuple(filter(lambda t: t.serial_number == serial_number, transactions))


def main() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)

    menu = ConsoleMenu("Fastpay Access", "A fast CLI alternative to https://access.westpay.se/")
    menu.append_item(FunctionItem("Get customer transactions", lambda: (display_transactions(fetch_customer_transactions()), pause())))
    menu.append_item(FunctionItem("Get terminal transactions", lambda: (display_transactions(fetch_terminal_transactions()), pause())))

    menu.show()


if __name__ == "__main__":
    main()
