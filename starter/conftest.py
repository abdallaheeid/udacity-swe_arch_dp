"""Shared pytest fixtures."""
import pytest

from balance.balance import Balance


@pytest.fixture(autouse=True)
def reset_balance():
    """Reset the Balance singleton so tests stay independent."""
    Balance.get_instance().reset()
    yield
    Balance.get_instance().reset()
