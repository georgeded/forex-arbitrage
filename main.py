import logging
import sys
import threading
import time

from config import API_URL, POLL_INTERVAL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def _run_api() -> None:
    from api.app import app, start_rate_updater
    start_rate_updater()
    app.run(debug=False, port=5000, use_reloader=False)


if __name__ == "__main__":
    api_thread = threading.Thread(target=_run_api, daemon=True)
    api_thread.start()
    logger.info("Forex API started on http://localhost:5000")

    # Give the API a moment to start before the first poll
    time.sleep(2)

    from core.detector import detect_arbitrage_opportunities
    from portfolio.trader import simulated_trading

    while True:
        logger.info("Fetching new Forex rates...")
        opportunities = detect_arbitrage_opportunities(API_URL)
        simulated_trading(opportunities)
        time.sleep(POLL_INTERVAL)
