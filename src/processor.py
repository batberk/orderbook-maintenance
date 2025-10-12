# src/processor.py

import pandas as pd
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
        """
        Process CSV file until target timestamp for target symbol

        Args:
            filename: Path to CSV file
            target_symbol: Symbol to process (e.g., 'BTC/USD')
            target_timestamp: Stop processing at this timestamp
            depth: Orderbook depth (10 or 1000)

        Returns:
            OrderBook for target symbol at target timestamp
        """
        # Read CSV in chunks for memory efficiency
        chunk_size = 10000

        for chunk in pd.read_csv(filename, chunksize=chunk_size):
            for _, row in chunk.iterrows():
                # Check timestamp first (early exit)
                if row['time'] > target_timestamp:
                    break

                # Filter by symbol (only process target symbol)
                if row['symbol'] != target_symbol:
                    continue

                # Parse message
                message = self.parser.parse_message(row)

                # Get or create orderbook for this symbol
                if message.symbol not in self.orderbooks:
                    self.orderbooks[message.symbol] = OrderBook(
                        message.symbol, depth
                    )

                orderbook = self.orderbooks[message.symbol]

                # Process message
                if message.is_snapshot:
                    orderbook.process_snapshot(
                        message.bids, message.asks, message.timestamp
                    )
                else:
                    orderbook.process_update(
                        message.bids, message.asks, message.timestamp
                    )

            # Check if we've passed target timestamp
            if chunk['time'].min() > target_timestamp:
                break

        return self.orderbooks.get(target_symbol)