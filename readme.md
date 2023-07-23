# CANDLEBOT Backtesting Bot

Project to retrieve historical crypto data from CEX (Centralized Exchanges) like Binance and use this data to run backtesting strategies to validate if a trading strategy is worth it to use in real investment or not. For some of the CEX is needed to have a valid key like for example Binance.

Some of the features included in this project:

- crawl Binance [candlesticks](https://en.wikipedia.org/wiki/Candlestick_chart) and store them in a DB
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

![candlebot_backfill](https://github.com/oalfonso-o/candlebot/assets/9935204/61224e09-b335-4206-b4ff-6d841e86abee)

Here we are downloading candles from Binance:

- since 2000: first candle starts in 2017
- until 2023
- candles intervals of 1 day
- symbol ETHUSDT

And we see we retrieved 2167 candles

And now we can test our strategies:

### Testing a strategy and visualize it in the chart

Also from the dashboard, in this case an example with ADAUSDT (in the backfill step we backfilled ETHUSDT, you can select the symbol in the form), this helps to define our strategy:

![candlebot_backtesting_ada](https://github.com/oalfonso-o/candlebot/assets/9935204/8f78bd52-296b-44e6-a67c-e9cefe588991)

In this example we select since 2000 up to 2023 for ADAUSDT symbol with intervals of 1d and strategy "fractal_and_engulfing" (you have to define in code your own strategies, this is a random strategy being tested). The first candle is from January 2021 and the last from July 2023. In the chart we can see all the indicators needed for this strategy which helps to debug the decisions we put in this strategy on when to open and when to close position. We can also see the candles where we open and where we close the position. In the lower section we see a legend with a summary, showing the number of "winner" operations which in this case is 4 and the % of amount at the end of this period using this strategy. We see it's only close to 0.1% of win (100.099) which doesn't look very promising in 2 years and a half.

The good thing of this is the level of detail and having the charts to validate what would happen with your strategy with the past data.

To define your own strategy you need to add a new strategy in `backend.candlebot.strategist.Strategist.strategies`, you can use other strategies as a reference to create your own.

It's pending to add also more details about the current wallet being used, as the strategy simulates a wallet and a fictional amount used to open and close positions.

### Backtesting

Once we have our trategy tested with the charts and we see it's something it can make sense and be a "winner" option to put it to work automatic it's time to validate this doing backtesting using more time periods and more symbols, as we can think our strategy can beat any market but only backtesting can prove that it is true. For that there's also a friendly view in the dashboard to run our strategy against many options. Depending on the number of options that you select this can take a lot of time, it's better to start backtesting with less periods and currencies. The output of the backtest is a summary of stats to be able to view the top most efficient strategies with their symbols, intervals and stats.

An example running 2 backtests with ADAUSDT and ETHUSDT for 1 day interval with the strategy we saw previously:

![candlebot_backtesting_ada_eth_1d](https://github.com/oalfonso-o/candlebot/assets/9935204/1eb9a6e1-763e-427c-8596-ee7844bd3a8a)

After running the test we see 2 lines, one per each symbol but we could select all the symbols (we need them backfilled first) and add also 1m period (but think that 1m candlesticks are too many candlesticks to process in a normal laptop, 1 year of daily candlesticks are only 365 candles, 1 year of candles with 1m interval are 525600 candles, and also multiply this per the number of symbols so better start the backtesting with less number of permutations and bigger intervals).

In each line we see these details:

- Strategy: fractal_and_engulfing
- Symbol: ADAUSDT and ETHUSDT
- Interval: 1d
- % won: the table is sorted by this value, so we see the best strategy for this backtest
- Balance Origin Start: the amount of fake currency present in the wallet before starting
- Balance Origin End: the amount of take currency present in the wallet after the test -> in this case the real win amount is very sad TBH
- Open amount: which is 100, this can be configured in the strategy, to open positions with a different amount
- Balance Long: the final balance in open positions in long, it's 0 because all the open positions have been closed
- Opened Position Long: number of total operations opened in long
- Closed Positions Long: number of total operations closed in long
- Fee: total amount paid in fees (in Binance you pay a fixed fee for each operation, we need to take this into account too)
- Date From, Date To and the Date of the test


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
