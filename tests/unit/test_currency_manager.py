import pytest
from unittest.mock import patch
from app.services.currency_manager import CurrencyManager

@patch("app.services.currency_manager.settings")
def test_register_client_initializes_balance(mock_settings):
    mock_settings.STARTING_TOKENS = 10
    cm = CurrencyManager()
    cm.register_client("client1")
    assert cm.get_balance("client1") == 10

def test_get_balance_returns_zero_for_unregistered_client():
    cm = CurrencyManager()
    assert cm.get_balance("ghost") == 0

@patch("app.services.currency_manager.settings")
def test_calculate_cost_various_lengths(mock_settings):
    mock_settings.COST_MODIFIER = 2
    cm = CurrencyManager()

    assert cm.calculate_cost(0) == 0
    # queue_length=1 → steps=0 → modifier=2 → cost=1+2=3
    assert cm.calculate_cost(1) == 3
    # queue_length=6 → steps=1 → modifier=4 → cost=6+4=10
    assert cm.calculate_cost(6) == 10

@patch("app.services.currency_manager.settings")
def test_try_spend_success_and_failure(mock_settings):
    mock_settings.STARTING_TOKENS = 20
    mock_settings.COST_MODIFIER = 2
    cm = CurrencyManager()
    cm.register_client("client1")

    # queue_length=1 → cost=3, balance=20 → success
    success, new_balance = cm.try_spend("client1", 1)
    assert success is True
    assert new_balance == 17

    # queue_length=100 → cost huge, balance=17 → fail
    success, new_balance = cm.try_spend("client1", 100)
    assert success is False
    assert new_balance == 17

def test_reward_for_popular_track_custom_tokens():
    cm = CurrencyManager()
    cm._balances["client1"] = 10

    new_balance = cm.reward_for_popular_track("client1", tokens=5)
    assert new_balance == 15

    # unregistered owner → returns 0
    assert cm.reward_for_popular_track("ghost", tokens=5) == 0


def test_add_tokens_existing_client():
    cm = CurrencyManager()
    cm._balances["client1"] = 10
    cm.add_tokens("client1", 5)
    assert cm.get_balance("client1") == 15

def test_add_tokens_nonexistent_client():
    cm = CurrencyManager()
    cm.add_tokens("ghost", 5)
    assert cm.get_balance("ghost") == 0