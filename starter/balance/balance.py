# balance.py

from transaction.transaction_category import TransactionCategory


class Balance:
    """Singleton to track the balance."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("No instance exists yet")
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance.balance = 0
        else:
            print("Balance exists")
        return cls._instance

    def __init__(self):
        """Initialize the balance. Prevent direct instantiation."""
        if self._initialized:      # already set up, so don't reset the balance
            return
        self.balance = 0
        self._initialized = True
        self._observers = []

    def reset(self):
        """Reset the net balance to zero."""
        self.balance = 0
        self._observers.clear()

    def add_income(self, amount):
        """Add income to the balance."""
        if amount < 0:
            raise ValueError(f"amount {amount} should not be < 0")
        self.balance += amount

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        if amount < 0:
            raise ValueError(f"amount {amount} should not be < 0")
        self.balance -= amount

    def apply_transaction(self, transaction):
        """
        Apply a Transaction object to update the balance.

        Args:
            transaction (Transaction): The transaction to apply.
        """
        if transaction.category == TransactionCategory.INCOME:
            self.add_income(transaction.amount)
        elif transaction.category == TransactionCategory.EXPENSE:
            self.add_expense(transaction.amount)
        else:
            raise ValueError(
                f"Unknown transaction category: {
                    transaction.category}")
        self.notify(transaction)

    def get_balance(self):
        """Get the current net balance."""
        return self.balance

    def summary(self) -> str:
        return f"Net balance: {self.balance:.2f}"

    def register_observer(self, observer):
        self._observers.append(observer)

    def deregister_observer(self, observer):
        self._observers.remove(observer)

    def notify(self, transaction):
        for observer in self._observers:
            observer.update(self.balance, transaction)

    @classmethod
    def get_instance(cls) -> "Balance":
        return cls()
