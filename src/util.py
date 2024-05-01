from datetime import datetime
import logging

from westpay_access import Transactions


def prompt_iso_date(prompt: str) -> datetime:
    while True:
        try:
            return datetime.fromisoformat(input(prompt))
        except ValueError:
            logging.warning("Invalid format. Please enter the date in ISO format (YYYY-MM-DDTHH:MM)")


def display_transactions(transactions: Transactions) -> None:
    print('|'.join((
        f"{"Terminal ID": ^16}",
        f"{"Serial number": ^16}",
        f"{"Date and time": ^24}",
        f"{"Amount": ^12}",
        f"{"Currency": ^12}",
        f"{"Masked PAN": ^12}",
        f"{"Response": ^32}",
        f"{"Response code": ^16}",
        f"{"Card brand": ^24}",
        f"{"Card issuer": ^64}"
    )))
    for transaction in transactions:
        print('|'.join((
            f"{transaction.terminal_id: ^16}",
            f"{transaction.serial_number if transaction.serial_number is not None else "n/a": ^16}",
            f"{transaction.time.isoformat(): ^24}",
            f"{transaction.amount: ^12.2f}",
            f"{transaction.currency if transaction.currency else "n/a": ^12}",
            f"{f"****{transaction.masked_pan}" if transaction.masked_pan is not None else "n/a": ^12}",
            f"{transaction.response: ^32}",
            f"{transaction.response_code: ^16}",
            f"{transaction.card_brand if transaction.card_brand is not None else "n/a": ^24}",
            f"{transaction.card_issuer if transaction.card_issuer is not None else "n/a": ^64}",
        )))


def pause() -> None:
    input("Press <ENTER> to continue ...")
