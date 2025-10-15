import csv
from typing import Dict
from .orderbook import OrderBook
from .message_parser import MessageParser


class OrderBookProcessor:
    """Process orderbook data from CSV file"""

    def __init__(self):
        self.orderbooks: Dict[str, OrderBook] = {}
        self.parser = MessageParser()

    def process_file(self, filename: str, target_symbol: str,
                     target_timestamp: float, depth: int = 10) -> OrderBook:
        """Process CSV until target timestamp for target symbol"""
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                t = float(row['time'])
                if t > target_timestamp:
                    break
                if row['symbol'] != target_symbol:
                    continue

                # Parse message (row is already dict-like)
                message = self.parser.parse_message(row)

                orderbook = self.orderbooks.setdefault(
                    message.symbol, OrderBook(message.symbol, depth)
                )

                if message.is_snapshot:
                    orderbook.process_snapshot(message.bids, message.asks, t)
                else:
                    orderbook.process_update(message.bids, message.asks, t)

        return self.orderbooks.get(target_symbol)
