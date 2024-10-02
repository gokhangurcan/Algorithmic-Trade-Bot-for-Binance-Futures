This is a trading bot that allows you to perform futures trading on the Binance Futures exchange using signals received via webhook from algorithms created on TradingView. The bot is written in Python and utilizes Heroku servers to enable your TradingView strategy to execute trades on your account with your Binance API key.

Unlike the Python library created by Binance for its own futures, this bot has a distinct functional block. To address the issue of constantly changing IPs with the Heroku servers, the Proximo plugin has been utilized. (The cost of using Heroku servers is $7 per month, and the Proximo plugin is $3.)

- **You can reach me via my email address for any inquiries.**

- **You can use this bot with PyCharm or Spyder.**




### **Usage of the Heroku app:**

1.) Create a Heroku account _(https://www.heroku.com/)_

2.) Edit config.json to add your own api keys & secret key.

You need to create new API key and secret key on Binance and give the API required permissions. _(Enable Futures)_

4.) Open terminal.

5.) Install Heroku CLI. _(https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli)_

6.) Enter the following lines into the terminal in order to:

```
git init

heroku login

heroku create <server-name>

git add .

git commit -m "Initial Commit"

git push heroku master
```

When you need to update the code or the API-secret keys, you must ENTER a new build to Heroku on terminal:
```
git add .

git commit -m "Update"

git push heroku master
```



### **Usage of the Proximo for Static IP Provisioning:**

1.) Open Terminal and enter the following lines:

```
heroku addons:create proximo:development

heroku config | grep PROXIMO_URL
```

2.) Your static IP address will be shown when you add the add-on.:
```
heroku addons:create proximo:development
```


### **Send alerts from TradingView or Postman to your new heroku web server**

1.) Before creating a Tradingview signal, you can also try buying and selling via Binance Tesnet by sending test signals via Postman:

- _Create an alert for your Tradingview strategy and enter the webhook url of your Heroku server in the webhook address from the settings:_

![Image](https://github.com/user-attachments/assets/c7963d15-b457-45ae-9faf-19f47b4ea36c)

- _To send alerts via Postman for the testing phases of the bot, edit your workspace as follows:_

![Image](https://github.com/user-attachments/assets/757a8b46-c6f4-476b-8370-ed22d9a54179)

2.) The alarm format should be as follows:
```
{
	"key": 12345,
	"exchange": "binance-futures",
	"symbol": "BTCUSDT",
	"type": "Limit",
	"side": "Buy",
	"qty": "1",
	"price": "50000",
	"close_position": "False",
	"cancel_orders": "True",
	"order_mode": "Both",
	"take_profit_percent": "5",
	"stop_loss_percent": "1.5"
}
```
3.) 

> **key**: _key to acces your webhook server_
> **echange**: _binance-futures only_
> **symbol**: _BTCUSDT, ETHUSDT, etc._
> **type**: _limit or market_
> **side**: _sell or buy_
> **qty**: _total quantity size (pay attention to leverage and size in futures)._
> **price**: _price order required for limit order_
> **close_positions**: _true or false_
> **cancel_orders**: _true or false_
> **order_mode**: _Both (for Stop Loss & Take Profit Orders)_
> **take_profit_percent**: _take profit percentage (be careful to use float lika 3.5)_
> **stop_loss_percent**: _stop loss percentage (be careful to use float lika 1.5)_







