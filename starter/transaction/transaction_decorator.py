"""Decorator pattern: add behaviour (tax, fees, ...) to transactions
without modifying them."""
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TransactionDecorator(Transaction):
    """Base decorator. Wraps a Transaction and exposes the same interface."""

    def __init__(self, transaction: Transaction):
        # Intentionally no super().__init__():
        # state comes from the wrapped transaction.
        self._wrapped = transaction

    @property
    def amount(self):
        return self._wrapped.amount

    @property
    def category(self):
        return self._wrapped.category

    def __str__(self):
        return str(self._wrapped)


class TaxDecorator(TransactionDecorator):
    """Deducts a percentage tax from INCOME transactions.

    Expenses pass through unchanged.
    """

    def __init__(self, transaction: Transaction, rate: float):
        if not 0 <= rate <= 1:
            raise ValueError(
                f"Tax rate must be between 0 and 1, got {rate}"
            )
        super().__init__(transaction)
        self.rate = rate

    @property
    def amount(self):
        base = self._wrapped.amount
        if self.category == TransactionCategory.INCOME:
            return base * (1 - self.rate)
        return base

    def __str__(self):
        return (
            f"{self._wrapped} "
            f"(after {self.rate:.0%} tax: {self.amount:.2f})"
        )


class FeeDecorator(TransactionDecorator):
    """Adds a fixed fee to EXPENSE transactions.

    Income passes through unchanged.
    """

    def __init__(self, transaction: Transaction, fee: float):
        if fee < 0:
            raise ValueError(f"Fee must be non-negative, got {fee}")
        super().__init__(transaction)
        self.fee = fee

    @property
    def amount(self):
        base = self._wrapped.amount
        if self.category == TransactionCategory.EXPENSE:
            return base + self.fee
        return base

    def __str__(self):
        return (
            f"{self._wrapped} "
            f"(+ fee {self.fee:.2f} = {self.amount:.2f})"
        )
