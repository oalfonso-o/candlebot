from binance import ThreadedWebsocketManager

from candlebot.settings import Settings


def main():

    symbol = 'ADAUSDT'

    twm = ThreadedWebsocketManager(
        api_key=Settings.API_KEY,
        api_secret=Settings.SECRET_KEY
    )
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        print(f"message type: {msg['e']}")
        print(msg)

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    streams = [f'{symbol}@miniTicker', f'{symbol}@bookTicker']
    twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)


if __name__ == "__main__":
    main()
