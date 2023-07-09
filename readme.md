# CANDLEBOT Backtesting Bot

Project to retrieve historical crypto data from CEX (Centralized Exchanges) like Binance and use this data to run backtesting strategies to validate if a trading strategy is worth it to use in real investment or not. For some of the CEX is needed to have a valid key like for example Binance.

Some of the features included in this project:

- crawl Binance candles and store them in a DB
- show charts of these values
- define custom backtesting strategies, run them against real historical data and see the charts with all the forecasted operations
- put this strategy to run automatically with the Binance API (WIP)

## Install
- Install TA-Lib: https://github.com/TA-Lib/ta-lib-python
- Create a virtualenv with python 3.8
- Install `backend` and `frontend` with pip
- Run a mongod
- Copy .env.example to .env and customize vars
- For a complete list of commands we have backend/run.py


## Dashboard

To make it easy to work with this data there's a dashboard, we need to run the front and the backend:

```
make back
```
and
```
make front
```
(With mongod running)

And now we can also run the commands of `run.py` but more friendly.

### Backfilling

We can do it from a form:

[backfill_btc_usdt_1d.webm](https://github.com/oalfonso-o/candlebot/assets/9935204/c349f2b9-9e2e-4d30-a182-0a1182c2213f)


And now we can test our strategies:

### Testing an strategy (backtesting)

Also from the dashboard:

[testing_strategy.webm](https://github.com/oalfonso-o/candlebot/assets/9935204/b2e0af64-578d-4980-8b23-6be845ca2856)

This example shows a minimum win of 0.04% from Jan 01 2022 to Jul 07 2023, this strategy is not worth it. And I couldn't find one that was really a winning strategy. But this project allows you defining your own strategy, when to buy, when to sell, take into account the fees for each operation and see if with a rigic logic you could find a method that it always returns profit.

The good thing of this is the level of detail and having the charts to validate what would happen with your strategy with the past data.

To define your own strategy you need to add a new strategy in `backend.candlebot.strategist.Strategist.strategies`, you can use other strategies as a reference to create your own.


## Usage: backend/run.py

With this script we can run the main actions of this project, let's take a look at the help of the script:

```
$ python backend/run.py --help
usage: run.py [-h]
              [-s {ADAUSDT,BTCUSDT,ETHUSDT,LTCUSDT,BNBUSDT,DOGEUSDT,XRPUSDT,DOTUSDT,UNIUSDT,BCHUSDT,LTCUSDT,LINKUSDT,VETUSDT,SOLUSDT,XLMUSDT,THETAUSDT,FILUSDT,TRXUSDT,NEOUSDT,XMRUSDT,LUNAUSDT,CAKEUSDT,EOSUSDT,IOTAUSDT,1INCHUSDT,HOTUSDT,CHZUSDT,SXPUSDT,TLMUSDT,ETCUSDT}]
              [-i INTERVAL] [--fill-date-from FILL_DATE_FROM] [--bt-test-id BT_TEST_ID]
              [--chart-no-show]
              {crawl,fill,fill_all,backtesting,market}

positional arguments:
  {crawl,fill,fill_all,backtesting,market}

options:
  -h, --help            show this help message and exit
  -s {ADAUSDT,BTCUSDT,ETHUSDT,LTCUSDT,BNBUSDT,DOGEUSDT,XRPUSDT,DOTUSDT,UNIUSDT,BCHUSDT,LTCUSDT,LINKUSDT,VETUSDT,SOLUSDT,XLMUSDT,THETAUSDT,FILUSDT,TRXUSDT,NEOUSDT,XMRUSDT,LUNAUSDT,CAKEUSDT,EOSUSDT,IOTAUSDT,1INCHUSDT,HOTUSDT,CHZUSDT,SXPUSDT,TLMUSDT,ETCUSDT}, --symbol {ADAUSDT,BTCUSDT,ETHUSDT,LTCUSDT,BNBUSDT,DOGEUSDT,XRPUSDT,DOTUSDT,UNIUSDT,BCHUSDT,LTCUSDT,LINKUSDT,VETUSDT,SOLUSDT,XLMUSDT,THETAUSDT,FILUSDT,TRXUSDT,NEOUSDT,XMRUSDT,LUNAUSDT,CAKEUSDT,EOSUSDT,IOTAUSDT,1INCHUSDT,HOTUSDT,CHZUSDT,SXPUSDT,TLMUSDT,ETCUSDT}
  -i INTERVAL, --interval INTERVAL
                        Str Binance candlesticks interval
  --fill-date-from FILL_DATE_FROM
                        Date YYYYMMDD. Used when command is fill as date from to query Binance API and
                        perform an initial filling of the DB.
  --bt-test-id BT_TEST_ID
                        Test ID to run with backtesting
  --chart-no-show
```

### 1. Fill All
Backfilling: Same as `2. Fill` but without filters, it fills all the intervals and currency pairs in `candlebot.constants.TRADING_SYMBOLS` and `candlebot.constants.INTERVALS`. The idea of having "Fill" and "Fill All" is to be able to populate the whole db fast with this "Fill All" and then later use only "Fill" to fill the gaps.

```
python backend/run.py fill_all
```

Take into account that this can take very long, as it have many currencies, feel free to edit the constants to reduce the number of pairs. Also there's risk of getting banned if the CEX APIs decide to do it.

### 2. Fill
Same as Fil All but only foran specific pair of crypto currencies to allow us doing backtesting with them

This is better to fill only the data needed for your tests, for example ADA USDT for 1 day candles since Jan 01 2021:

```
python backend/run.py fill --symbol ADAUSDT --interval 1d --fill-date-from 20210101
```

### 3. Crawl
Keep a loop running that will collect the latest candles in the specified interval in real time for an specified currency pair

```
python backend/run.py crawl -s BTCUSDT
```

We have the pairs choices in the help message of `run.py`.

### 4. Backtesting
Run the backtesting strategy which will store the results of the win/loses in the database

### 5. Market Arbitrage
Retrieve current prices of multiple CEX and check if there's enough difference between any of them to make it worth to buy cheaper in one CEX, transfer it to the other and sell there getting profit.




## List of Symbols
You can check them in `backend.candlebot.constants`

## Interesting documentation
- https://www.youtube.com/watch?v=L7G0OfJUON8
- https://www.youtube.com/watch?v=9h3lByx59ns&t=1s
- https://www.youtube.com/channel/UCkDiQC3OeMnHBcSWgBy2plQ/videos
- https://jsfiddle.net/trior/q3kt6psb/3/ -> pin charts
- https://jsfiddle.net/q3u2khzt/ -> show volume
