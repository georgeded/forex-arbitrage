import logging
import random

from config import STARTING_BALANCE

logger = logging.getLogger(__name__)

portfolio_balance: dict[str, float] = {
    "USD": STARTING_BALANCE,
    "EUR": STARTING_BALANCE,
    "GBP": STARTING_BALANCE,
    "JPY": STARTING_BALANCE,
    "CHF": STARTING_BALANCE,
    "AUD": STARTING_BALANCE,
    "CAD": STARTING_BALANCE,
    "NZD": STARTING_BALANCE,
    "SEK": STARTING_BALANCE,
    "NOK": STARTING_BALANCE,
    "ZAR": STARTING_BALANCE,
    "INR": STARTING_BALANCE,
    "BRL": STARTING_BALANCE,
    "MXN": STARTING_BALANCE,
    "SGD": STARTING_BALANCE,
    "HKD": STARTING_BALANCE,
}


def get_balance(currency: str) -> float:
    return portfolio_balance.get(currency, float("inf"))


def pick_best_cycle(cycles: list[tuple[str, ...]]) -> tuple[str, ...] | None:
    if not cycles:
        return None
    max_balance = -float("inf")
    best_cycle: tuple[str, ...] | None = None
    for cycle in cycles:
        start_currency = cycle[0]
        balance = get_balance(start_currency)
        if balance > max_balance:
            max_balance = balance
            best_cycle = cycle
        elif balance == max_balance:
            best_cycle = random.choice([best_cycle, cycle])
    return best_cycle


def simulated_trading(opportunities: dict[tuple[str, ...], dict]) -> None:
    try:
        if not opportunities:
            logger.info("No arbitrage cycle detected.")
            return

        best_cycle = pick_best_cycle(list(opportunities.keys()))
        if best_cycle is None:
            return

        profitability = opportunities[best_cycle]["percentage_profit"]
        cycle_weight = opportunities[best_cycle]["total_weight"]

        if cycle_weight > 0 and profitability < 0:
            logger.info("Cycle weight is positive and profit is negative. Trade not executed.")
            return

        for currency in best_cycle[:-1]:
            if currency in portfolio_balance:
                portfolio_balance[currency] *= 1 + profitability / 100

        cycle_str = "->".join(best_cycle)
        logger.info(
            "Full cycle trade execution | profit: %.2f%% | weight: %.4f | cycle: %s",
            profitability,
            cycle_weight,
            cycle_str,
        )
        balance_str = " | ".join(
            f"{c}: {b:.4f}" for c, b in portfolio_balance.items()
        )
        logger.info("Portfolio: %s", balance_str)

    except Exception as e:
        logger.error("Error during simulated trading: %s", e)
