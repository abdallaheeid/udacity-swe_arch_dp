# Reflection

This project is a small personal finance tracker. Transactions (income and expenses) are applied to a balance, observers react to balance changes, and income from an external freelance platform is integrated. Four design patterns shape its structure.

## 1. Singleton: `Balance`

**What it does:** `Balance` makes sure there is exactly one balance object in the application. Every call to `Balance()` or `Balance.get_instance()` returns the same instance.

**How it improved the design:** The whole app reads and updates a single source of truth. There is no risk of two parts of the program working on different balances, and no need to pass the balance object through every function.

**Trade-offs:**

- **Hidden global state.** The balance persists across unit tests, so the tests had to call `reset()` in `setUp()`. `reset()` also had to clear registered observers, because otherwise observers from one test kept firing in the next.
- **`__init__` runs on every call.** Python calls `__init__` even when `__new__` returns the existing instance. Without an `_initialized` guard, each `Balance()` call would silently reset the balance to 0. This bug was not obvious.
- **Harder to extend.** Supporting several accounts later would mean removing the singleton.

## 2. Observer: `IBalanceObserver`, `PrintObserver`, `LowBalanceAlertObserver`

**What it does:** Observers register with `Balance` and are notified after each transaction is applied.

**How it improved the design:** `Balance` only updates the number and notifies. It doesn't know about printing or alerts. New reactions, such as logging to a file or sending an email, can be added as new observer classes without touching `Balance`. Each observer can be tested on its own.

**Trade-offs:**

- **Fixed interface.** Every observer receives `(balance, transaction)`, even if it only needs one of them. Changing the signature would affect all observers.
- **Synchronous and ordered.** Observers run one after another in registration order. A slow or failing observer blocks or breaks the transaction flow.
- **State semantics had to be decided.** The tests required `alert_triggered` to reflect the _current_ balance, not stay `True` once it was triggered. That is a design decision, not something the pattern dictates.

## 3. Adapter: `TransactionAdapter`

**What it does:** It converts an `ExternalFreelanceIncome` from a third-party platform (with its own fields such as `invoice_id` and a string `typ = "income"`) into the app's own `Transaction`.

**How it improved the design:** The rest of the app only ever deals with `Transaction`. External formats stay at the edge of the system, and supporting a new platform means writing a new adapter. `Balance` and the observers stay unchanged.

**Trade-offs:**

- **Type mapping is the real work.** The external type is a string (`"income"`), while the app uses the `TransactionCategory` enum. Passing the string through unchanged broke `apply_transaction`, so the adapter has to map values explicitly and reject unknown ones.
- **Information is lost.** `invoice_id` and `description` are not part of `Transaction`, so they are dropped during conversion.
- **One more class** for a single conversion. It's worth it once more external sources are added.

## 4. Decorator: `TaxDecorator`, `FeeDecorator` (own choice)

**What it does:** Decorators wrap a `Transaction` and change its effective amount. `TaxDecorator` deducts a percentage from income, and `FeeDecorator` adds a fixed fee to expenses. Decorators can be stacked.

**How it improved the design:** Rules like tax and fees are added without changing `Transaction`, `Balance` or the adapter, which follows the open/closed principle. Rules can be combined freely, e.g. `FeeDecorator(TaxDecorator(t, 0.25), 2)`, without creating a subclass for every combination. Each decorator is small and easy to unit test, and the original transaction is never mutated.

**Trade-offs:**

- **Interface must match exactly.** Decorators expose `amount` and `category` as read-only properties and deliberately skip `Transaction.__init__`. This works, but it is easy to get wrong when `Transaction` gains new attributes.
- **Equality and debugging.** `__eq__` compares the decorated amount, and in deep stacks it is less obvious where a final amount comes from. Descriptive `__str__` methods help with this.
- **Floating-point amounts.** Percentages produce floats (e.g. `0.1 * 3`), so the tests use `assertAlmostEqual`. A real finance app should use `Decimal`.

## Summary

| Pattern   | Main benefit                                     | Main trade-off                               |
| --------- | ------------------------------------------------ | -------------------------------------------- |
| Singleton | One shared source of truth for the balance       | Global state leaks between tests             |
| Observer  | Balance is decoupled from reactions              | Synchronous, fixed `update` signature        |
| Adapter   | External formats isolated at the system boundary | Explicit type mapping, extra fields are lost |
| Decorator | Composable rules without new subclasses          | Interface must be mirrored, harder to trace  |

Overall, the patterns made the code easier to extend: new observers, external sources and transaction rules can be added without modifying existing classes. The main cost was the shared state of the singleton, which needed extra care in testing.
