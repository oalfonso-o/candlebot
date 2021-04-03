import logging
import argparse
from dotenv import load_dotenv

from crypto.crawler import Crawler
from crypto import constants

load_dotenv()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(name)8.8s  %(levelname)7s  %(message)s',
        force=True,
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        '--symbol',
        required=True,
        choices=[
            constants.SYMBOL_CARDANO_EURO,
            constants.SYMBOL_BITCOIN_EURO,
            constants.SYMBOL_ETHEREUM_EURO,
        ],
    )
    args = parser.parse_args()
    crawler = Crawler()
    data = crawler.get_data(args.symbol)
    logging.info(data)
