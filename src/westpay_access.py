from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Terminal:
    customer: str
    customer_id: int
    model: str
    operating_mode: str
    pa_version: str
    serial_number: str
    terminal_id: int

    @classmethod
    def from_dict(cls, data: dict) -> Terminal:
        return cls(
            data["CustomerName"],
            data["CustomerId"],
            data["TerminalModel"],
            data["OperatingMode"],
            data["PaVersion"],
            data["SerialNumber"],
            data["TerminalidTerminalId"]
        )


@dataclass(frozen=True)
class Transaction:
    amount: float
    currency: str
    customer: str
    card_brand: str
    card_issuer: str
    masked_pan: str
    method: str
    reference_number: int
    response: str
    response_code: str
    serial_number: str
    terminal_id: int
    time: datetime

    @classmethod
    def from_dict(cls, data: dict) -> Transaction:
        return cls(
            data["Amount"],
            data["Currency"],
            data["CustomerName"],
            data["CardProduct"],
            data["CardIssuer"],
            data["MaskedPan"],
            data["CardEntryMethod"],
            data["RetrievalReferenceNo"],
            data["Response"],
            data["ResponseCode"],
            data["SerialNumber"],
            data["Pid"],
            datetime.fromisoformat(data["Time"])
        )


Terminals = tuple[Terminal, ...]
Transactions = tuple[Transaction, ...]


class WestpayAccess(requests.Session):
    def login(self, username: str, password: str) -> bool:
        login_page = BeautifulSoup(
            self.get("https://access.westpay.se/Account/Login").content,
            "html.parser"
        )
        csrf_token = login_page.find("input", {"name": "__RequestVerificationToken"})["value"]

        data = {
            "UserName": username,
            "Password": password,
            "__RequestVerificationToken": csrf_token
        }

        response = self.post("https://access.westpay.se/Account/login", data)

        return b"Invalid username or password." not in response.content

    def get_terminals(self) -> Terminals:
        params = {
            "filter": "Active"
        }
        response = self.get(
            "https://access.westpay.se/Onboarding/GetMyTerminalidTerminals",
            params=params
        )

        return tuple(map(Terminal.from_dict, response.json()))

    def get_transactions(self, customer_id: int, start: datetime, end: datetime, terminal_id: int = None) -> Transactions:
        data = {
            "customerId": customer_id,
            "fromdate": start.strftime("%Y%m%d"),
            "todate": end.strftime("%Y%m%d"),
            "terminalId": terminal_id,
            "includeSubCustomers": False,
            "pageSize": (1 << 31) - 1
        }

        response = self.post(
            "https://access.westpay.se/api/reports/TransactionsByCustomerAndDate/json",
            data
        )

        return tuple(map(Transaction.from_dict, response.json()["Data"]))
