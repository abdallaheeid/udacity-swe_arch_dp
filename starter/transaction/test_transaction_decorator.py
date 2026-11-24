import unittest
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_decorator import TaxDecorator, FeeDecorator
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver

INCOME = TransactionCategory.INCOME
EXPENSE = TransactionCategory.EXPENSE


class TestTaxDecorator(unittest.TestCase):

    def test_tax_reduces_income(self):
        t = TaxDecorator(Transaction(1000, INCOME), rate=0.2)
        self.assertAlmostEqual(t.amount, 800)

    def test_tax_ignores_expense(self):
        t = TaxDecorator(Transaction(100, EXPENSE), rate=0.2)
        self.assertEqual(t.amount, 100)

    def test_category_is_preserved(self):
        t = TaxDecorator(Transaction(100, INCOME), rate=0.1)
        self.assertEqual(t.category, INCOME)

    def test_invalid_rate_raises(self):
        self.assertRaises(
            ValueError,
            TaxDecorator,
            Transaction(100, INCOME),
            rate=1.5,
        )


class TestFeeDecorator(unittest.TestCase):

    def test_fee_increases_expense(self):
        t = FeeDecorator(Transaction(50, EXPENSE), fee=2.5)
        self.assertAlmostEqual(t.amount, 52.5)

    def test_fee_ignores_income(self):
        t = FeeDecorator(Transaction(50, INCOME), fee=2.5)
        self.assertEqual(t.amount, 50)

    def test_negative_fee_raises(self):
        self.assertRaises(
            ValueError,
            FeeDecorator,
            Transaction(50, EXPENSE),
            fee=-1,
        )


class TestDecoratorComposition(unittest.TestCase):

    def test_decorators_can_be_stacked(self):
        t = FeeDecorator(TaxDecorator(Transaction(1000, INCOME), rate=0.2), fee=5)
        self.assertAlmostEqual(t.amount, 800)          # fee doesn't apply to income

        t = FeeDecorator(FeeDecorator(Transaction(100, EXPENSE), fee=1), fee=2)
        self.assertAlmostEqual(t.amount, 103)

    def test_decorated_is_still_a_transaction(self):
        t = TaxDecorator(Transaction(100, INCOME), rate=0.1)
        self.assertIsInstance(t, Transaction)

    def test_original_transaction_is_unchanged(self):
        original = Transaction(1000, INCOME)
        TaxDecorator(original, rate=0.2)
        self.assertEqual(original.amount, 1000)


class TestDecoratorWithBalance(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_balance_uses_decorated_amounts(self):
        self.balance.apply_transaction(TaxDecorator(Transaction(1000, INCOME), rate=0.2))
        self.balance.apply_transaction(FeeDecorator(Transaction(100, EXPENSE), fee=5))
        self.assertAlmostEqual(self.balance.get_balance(), 695)   # 800 - 105

    def test_observers_see_decorated_amounts(self):
        observer = LowBalanceAlertObserver(threshold=100)
        self.balance.register_observer(observer)
        self.balance.apply_transaction(Transaction(100, INCOME))
        self.assertFalse(observer.alert_triggered)
        self.balance.apply_transaction(FeeDecorator(Transaction(0, EXPENSE), fee=1))
        self.assertTrue(observer.alert_triggered)               # 100 - 1 = 99


if __name__ == "__main__":
    unittest.main()