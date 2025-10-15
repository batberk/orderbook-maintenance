import json
import pandas as pd
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class OrderBookMessage:
    """Structured message data"""
    timestamp: float
    symbol: str
    bids: List[Tuple[float, float]]
    asks: List[Tuple[float, float]]
    is_snapshot: bool


class MessageParser:
    """Parse orderbook CSV messages"""

    @staticmethod
    def parse_price_levels(price_str: str) -> List[Tuple[float, float]]:
        """Convert string representation of price levels to list of tuples"""
        if not price_str or price_str == "[]":
            return []

        try:
            # Normalize single quotes to double quotes for valid JSON
            if "'" in price_str and '"' not in price_str:
                price_str = price_str.replace("'", '"')

            raw_list = json.loads(price_str)
        except json.JSONDecodeError:
            raw_list = json.loads(price_str.replace("'", '"'))

        # Convert all string pairs to floats
        return [(float(price), float(qty)) for price, qty in raw_list]

    @staticmethod
    def is_snapshot(bids: List, asks: List) -> bool:
        """
        Snapshot = both bids and asks have data ( 10 levels)
        Update = one or both might be empty or have fewer entries
        """
        return len(bids) >= 10 and len(asks) >= 10

    def parse_message(self, row: pd.Series) -> OrderBookMessage:
        """Parse a single CSV row into structured message"""
        bids = self.parse_price_levels(row['bids'])
        asks = self.parse_price_levels(row['asks'])

        return OrderBookMessage(
            timestamp=float(row['time']),
            symbol=row['symbol'],
            bids=bids,
            asks=asks,
            is_snapshot=self.is_snapshot(bids, asks)
        )
