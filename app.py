import json
from flask import Flask, request, jsonify
import ccxt
import os
import requests

# Configure proxy for requests
proximo_url = os.environ.get('PROXIMO_URL', '')
proxy_dict = {
    "http": proximo_url,
    "https": proximo_url,
}


def validate_binance_api_key(exchange):
    try:
        result = exchange.fetch_balance()
        print("Binance API key is valid. Balance:", result)
        return True
    except Exception as e:
        print("Binance API key validation failed:", str(e))
        return False


app = Flask(__name__)

# Load config.json
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
    print("Config Loaded:", config)
except Exception as e:
    print("Failed to load config:", str(e))

use_binance_futures = False
if 'binance-futures' in config.get('exchange', {}):
    if config['exchange']['binance-futures'].get('ENABLED', False):
        print("Binance Futures is enabled!")
        use_binance_futures = True

        api_key = config['exchange']['binance-futures']['API_KEY']
        api_secret = config['exchange']['binance-futures']['API_SECRET']
        print("API Key:", api_key)
        print("API Secret:", api_secret)

        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {
                'defaultType': 'future',
            },
            'urls': {
                'api': {
                    'public': 'https://fapi.binance.com/fapi/v1',
                    'private': 'https://fapi.binance.com/fapi/v1',
                }
            }
        })

        if config['exchange']['binance-futures'].get('TESTNET', False):
            exchange.urls['api']['public'] = 'https://testnet.binancefuture.com/fapi/v1'
            exchange.urls['api']['private'] = 'https://testnet.binancefuture.com/fapi/v1'
            exchange.set_sandbox_mode(True)

        # Apply proxy settings to exchange
        exchange.session.proxies.update(proxy_dict)
        print("Exchange initialized with URLs:", exchange.urls)
    else:
        print("Binance Futures is not enabled in config.")
else:
    print("Binance Futures is not found in the exchange config.")

# Validate Binance Futures API key
if use_binance_futures:
    if not validate_binance_api_key(exchange):
        print("Invalid Binance Futures API key.")
        use_binance_futures = False
else:
    print("Binance Futures is not enabled or config loading failed.")


@app.route('/')
def index():
    return jsonify({'message': 'Server is running!'})


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("Hook Received!")
        data = json.loads(request.data)
        print("Received data:", data)

        if int(data['key']) != config['KEY']:
            print("Invalid Key, Please Try Again!")
            return jsonify({
                "status": "error",
                "message": "Invalid Key, Please Try Again!"
            }), 400

        if data['exchange'] == 'binance-futures':
            print("Exchange recognized as binance-futures")
            if use_binance_futures:
                from Futures import Bot
                bot = Bot()
                bot.run(data)
                return jsonify({
                    "status": "success",
                    "message": "Binance Futures Webhook Received!"
                }), 200
            else:
                print("Binance Futures is not enabled or API key is invalid.")
                return jsonify({
                    "status": "error",
                    "message": "Invalid Exchange, Please Try Again!"
                }), 400

        return jsonify({"status": "error", "message": "Invalid Exchange"}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)