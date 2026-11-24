# transaction.py

from transaction.transaction_category import TransactionCategory

class Transaction:
    """Represents a financial transaction with an amount and category."""

    def __init__(self, amount, category: TransactionCategory):
        self.amount = amount
        self.category = category

    def __str__(self):
        return f"{self.category}: {self.amount}"

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.amount == other.amount and self.category == other.category
