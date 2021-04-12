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
4. Copy web/js/.env.example.js to web/js/.env.js and customize vars (if needed)
5. Run a mongod
6. Copy the nginx site of web/candlebot.conf in an nginx sites-enabled dir
7. Run api with make api
8. Go to localhost:1234
9. For more commands check candlebot/run.py

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

## Interesting documentation
- https://www.youtube.com/watch?v=L7G0OfJUON8
- https://www.youtube.com/watch?v=9h3lByx59ns&t=1s
- https://www.youtube.com/channel/UCkDiQC3OeMnHBcSWgBy2plQ/videos
- https://jsfiddle.net/trior/q3kt6psb/3/ -> pin charts
- https://jsfiddle.net/q3u2khzt/ -> show volume