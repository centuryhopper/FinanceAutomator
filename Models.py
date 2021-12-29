import datetime


def transaction_from_json(json):
    return Transaction(
        json["name"],
        json["amount"],
        json["date"],
        json["account_number"],
    )

class Transaction:
    def __init__(self, description, transactionType, amount, date, account_number):
        self.description = description
        self.transactionType = transactionType
        self.amount = amount
        self.date = date
        self.account_number = account_number
    def serialize(self):
        return {
            "description": self.description,
            "transaction_type": self.transactionType,
            "amount": self.amount,
            "date": str(self.date),
            "account_number": self.account_number,
        }
    def __str__(self):
        return f'{self.description}, {self.transactionType}, {self.amount}, {self.date}, {self.account_number}'

