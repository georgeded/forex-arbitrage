from flask import Flask, jsonify
import random
import threading
import time

app = Flask(__name__)

currency_pairs = {
    "USD/EUR": lambda: round(random.uniform(0.8, 1.2), 4),
    "EUR/GBP": lambda: round(random.uniform(0.7, 0.9), 4),
    "GBP/USD": lambda: round(random.uniform(1.2, 1.4), 4),
    "USD/JPY": lambda: round(random.uniform(100, 150), 2),
    "JPY/EUR": lambda: round(random.uniform(0.007, 0.009), 6),
    "EUR/USD": lambda: round(random.uniform(1.0, 1.5), 4),
    "USD/CHF": lambda: round(random.uniform(0.9, 1.1), 4),
    "CHF/JPY": lambda: round(random.uniform(110, 130), 2),
    "AUD/USD": lambda: round(random.uniform(0.65, 0.75), 4),
    "USD/CAD": lambda: round(random.uniform(1.2, 1.4), 4),
    "NZD/USD": lambda: round(random.uniform(0.6, 0.7), 4),
    "USD/SEK": lambda: round(random.uniform(8.0, 11.0), 2),
    "USD/NOK": lambda: round(random.uniform(9.0, 12.0), 2),
    "USD/ZAR": lambda: round(random.uniform(16.0, 19.0), 2),
    "EUR/AUD": lambda: round(random.uniform(1.4, 1.7), 4),
    "GBP/AUD": lambda: round(random.uniform(1.8, 2.1), 4),
    "USD/INR": lambda: round(random.uniform(70, 85), 2),
    "USD/BRL": lambda: round(random.uniform(4.5, 5.5), 4),
    "EUR/SEK": lambda: round(random.uniform(10.0, 11.5), 2),
    "EUR/NOK": lambda: round(random.uniform(10.5, 12.0), 2),
    "USD/MXN": lambda: round(random.uniform(18.0, 20.0), 2),
    "EUR/ZAR": lambda: round(random.uniform(18.0, 22.0), 2),
    "GBP/JPY": lambda: round(random.uniform(150, 170), 2),
    "USD/SGD": lambda: round(random.uniform(1.3, 1.4), 4),
    "USD/HKD": lambda: round(random.uniform(7.7, 7.9), 4),
}

currencies = set()
for pair in currency_pairs.keys():
    base, quote = pair.split("/")
    currencies.update([base, quote])

global_rates = {pair: func() for pair, func in currency_pairs.items()}

_updater_started = False


def update_rates() -> None:
    global global_rates
    while True:
        global_rates = {pair: func() for pair, func in currency_pairs.items()}
        time.sleep(5)


def start_rate_updater() -> None:
    global _updater_started
    if not _updater_started:
        _updater_started = True
        threading.Thread(target=update_rates, daemon=True).start()


@app.route("/api/rates", methods=["GET"])
def get_forex_rates():
    return jsonify({"currencies": sorted(list(currencies)), "rates": global_rates})


if __name__ == "__main__":
    start_rate_updater()
    app.run(debug=False, port=5000)
