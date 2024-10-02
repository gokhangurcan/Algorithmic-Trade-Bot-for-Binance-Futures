import json
import time
import ccxt
import random
import string
import requests
import os

# Configure proxy for requests
proximo_url = os.environ.get('PROXIMO_URL', '')
proxy_dict = {
    "http": proximo_url,
    "https": proximo_url,
}

with open('config.json') as config_file:
    config = json.load(config_file)

api_key = config['exchange']['binance-futures']['API_KEY']
api_secret = config['exchange']['binance-futures']['API_SECRET']

if config['exchange']['binance-futures']['TESTNET']:
    base_url = 'https://testnet.binancefuture.com'
    exchange_url = 'https://testnet.binancefuture.com/fapi/v1'
else:
    base_url = 'https://fapi.binance.com'
    exchange_url = 'https://fapi.binance.com/fapi/v1'

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {
        'defaultType': 'future',
    },
    'urls': {
        'api': {
            'public': exchange_url,
            'private': exchange_url,
        }
    }
})

if config['exchange']['binance-futures']['TESTNET']:
    exchange.set_sandbox_mode(True)

exchange.session.proxies.update(proxy_dict)

try:
    balance = exchange.fetch_balance()
    print("API key is valid. Balance:", balance)
except Exception as e:
    print("API key validation failed:", str(e))


def fetch_position_risk(symbol):
    endpoint = f"{base_url}/fapi/v2/positionRisk"
    headers = {
        'X-MBX-APIKEY': api_key
    }
    params = {
        'symbol': symbol,
        'timestamp': int(time.time() * 1000)
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = ccxt.binance().hmac(query_string.encode(), api_secret.encode())
    params['signature'] = signature

    response = requests.get(endpoint, headers=headers, params=params, proxies=proxy_dict)
    print(f"fetch_position_risk response: {response.json()}")
    return response.json()


class Bot:

    def __init__(self):
        pass

    def create_string(self):
        N = 7
        res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        baseId = 'x-40PTWbMI'
        self.clientId = baseId + str(res)
        return

    def place_limit_order_with_risk(self, symbol, side, qty, price, take_profit_price, stop_loss_price):
        try:
            # Fetch the current price
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']

            # Calculate adjusted prices based on side
            if side == 'Buy':
                limit_price = current_price * (1 - 0.0005)  # %0.3 below current price
            else:
                limit_price = current_price * (1 + 0.0005)  # %0.3 above current price

            limit_price = round(limit_price, 2)

            print(f"Limit Price: {limit_price}")
            print(f"Take Profit Price: {take_profit_price}")
            print(f"Stop Loss Price: {stop_loss_price}")

            # Place the limit order
            limit_order = exchange.create_order(
                symbol=symbol,
                type='LIMIT',
                side=side,
                amount=qty,
                price=limit_price,
                params={'reduceOnly': False, 'timeInForce': 'GTC'}
            )
            print(f"Limit Order Placed: {limit_order}")

            # Place the take profit order if price is set
            if take_profit_price > 0:
                take_profit_order = exchange.create_order(
                    symbol=symbol,
                    type='TAKE_PROFIT_MARKET',
                    side='SELL' if side == 'Buy' else 'BUY',
                    amount=qty,
                    params={
                        'stopPrice': take_profit_price,
                        'reduceOnly': True
                    }
                )
                print(f"Take Profit Order Placed: {take_profit_order}")

            # Place the stop loss order if price is set
            if stop_loss_price > 0:
                stop_loss_order = exchange.create_order(
                    symbol=symbol,
                    type='STOP_MARKET',
                    side='SELL' if side == 'Buy' else 'BUY',
                    amount=qty,
                    params={
                        'stopPrice': stop_loss_price,
                        'reduceOnly': True
                    }
                )
                print(f"Stop Loss Order Placed: {stop_loss_order}")

        except Exception as e:
            print(f"Error placing orders: {e}")

    def close_position(self, symbol):
        position_risk = fetch_position_risk(symbol)
        position = next((pos for pos in position_risk if pos['symbol'] == symbol), None)
        if position:
            self.create_string()
            params = {
                "newClientOrderId": self.clientId,
                'reduceOnly': True
            }
            if float(position['positionAmt']) > 0:
                print("Closing Long Position")
                exchange.create_order(symbol, 'MARKET', 'Sell', float(position['positionAmt']), params=params)
            else:
                print("Closing Short Position")
                exchange.create_order(symbol, 'MARKET', 'Buy', -float(position['positionAmt']), params=params)

    def run(self, data):
        print(data['close_position'])
        if data['close_position'] == 'True':
            print("Closing Position")
            self.close_position(symbol=data['symbol'])
        else:
            if 'cancel_orders' in data:
                print("Cancelling Order")
                exchange.cancel_all_orders(symbol=data['symbol'])
            if 'type' in data:
                print("Placing Order")
                qty = float(data['qty'])
                side = data['side']
                price = float(data.get('price', 0))
                take_profit_percent = float(data.get('take_profit_percent', 0)) / 100
                stop_loss_percent = float(data.get('stop_loss_percent', 0)) / 100
                atr_value = float(data.get('atr_value', 0))

                current_price = exchange.fetch_ticker(data['symbol'])['last']

                if data['order_mode'] == 'Both':
                    if side == 'Buy':
                        take_profit_price = round(float(current_price) + (float(current_price) * take_profit_percent), 2)
                        stop_loss_price = round(float(current_price) - (float(current_price) * stop_loss_percent) - atr_value, 2)
                    else:
                        take_profit_price = round(float(current_price) - (float(current_price) * take_profit_percent), 2)
                        stop_loss_price = round(float(current_price) + (float(current_price) * stop_loss_percent) + atr_value, 2)

                    print("Take Profit Price: " + str(take_profit_price))
                    print("Stop Loss Price: " + str(stop_loss_price))

                    self.create_string()
                    if data['type'] == 'Limit':
                        self.place_limit_order_with_risk(
                            symbol=data['symbol'],
                            side=side,
                            qty=qty,
                            price=price,
                            take_profit_price=take_profit_price,
                            stop_loss_price=stop_loss_price
                        )

                elif data['order_mode'] == 'Profit':
                    if side == 'Buy':
                        take_profit_price = round(float(current_price) + (float(current_price) * take_profit_percent), 2)
                    else:
                        take_profit_price = round(float(current_price) - (float(current_price) * take_profit_percent), 2)

                    print("Take Profit Price: " + str(take_profit_price))

                    self.create_string()
                    if data['type'] == 'Limit':
                        exchange.create_order(
                            symbol=data['symbol'],
                            type='LIMIT',
                            side=side,
                            amount=qty,
                            price=price,
                            params={'reduceOnly': False, 'timeInForce': 'GTC'}
                        )
                        self.place_limit_order_with_risk(
                            symbol=data['symbol'],
                            side=side,
                            qty=qty,
                            price=price,
                            take_profit_price=take_profit_price,
                            stop_loss_price=0  # Stop loss is not set in this case
                        )

                elif data['order_mode'] == 'Stop':
                    stop_loss_price = round(float(current_price) - (float(current_price) * stop_loss_percent) - atr_value, 2) if side == 'Buy' else round(float(current_price) + (float(current_price) * stop_loss_percent) + atr_value, 2)

                    print("Stop Loss Price: " + str(stop_loss_price))

                    self.create_string()
                    if data['type'] == 'Limit':
                        exchange.create_order(
                            symbol=data['symbol'],
                            type='LIMIT',
                            side=side,
                            amount=qty,
                            price=price,
                            params={'reduceOnly': False, 'timeInForce': 'GTC'}
                        )
                        self.place_limit_order_with_risk(
                            symbol=data['symbol'],
                            side=side,
                            qty=qty,
                            price=price,
                            take_profit_price=0,  # Take profit is not set in this case
                            stop_loss_price=stop_loss_price
                        )
