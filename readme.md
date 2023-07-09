# CANDLEBOT AUTO TRADER
This project has few features to:
- crawl Binance candles and store them in a DB
- show charts of these values
- backtesting strategies
- automatically trade with a little % of profit

## Install
- Install TA-Lib: https://github.com/TA-Lib/ta-lib-python
- Create a virtualenv with python 3.8
- Install `backend` and `frontend` with pip
- Run a mongod
- Copy .env.example to .env and customize vars
- Run backend with make back
- Run frontend with make front
- For more commands check backend/run.py

## To crawl data:
```
python run.py crawl -s SYMBOL
```

## To auto-trade:
```
python run.py trade -s SYMBOL
```

## List of Symbols
You can check them in `backend.candlebot.constants`

## Interesting documentation
- https://www.youtube.com/watch?v=L7G0OfJUON8
- https://www.youtube.com/watch?v=9h3lByx59ns&t=1s
- https://www.youtube.com/channel/UCkDiQC3OeMnHBcSWgBy2plQ/videos
- https://jsfiddle.net/trior/q3kt6psb/3/ -> pin charts
- https://jsfiddle.net/q3u2khzt/ -> show volume