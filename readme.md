# CANDLEBOT AUTO TRADER
This project has few features to:
- crawl Binance candles and store them in a DB
- show charts of these values
- backtesting strategies
- automatically trade with a little % of profit

## Install
1. Create a virtualenv with python 3.8
2. Install this repo inside with pip
3. Copy .env.example to .env and customize vars
4. Run a mongod
5. Run the desired command with run.py

## To crawl data:
```
python run.py crawl -s SYMBOL
```

## To auto-trade:
```
python run.py trade -s SYMBOL
```

## List of Symbols
You can check them in `candlebot.constants`

## Interesting trading documentation
- https://www.youtube.com/watch?v=L7G0OfJUON8
- https://www.youtube.com/watch?v=9h3lByx59ns&t=1s
- https://www.youtube.com/channel/UCkDiQC3OeMnHBcSWgBy2plQ/videos