# src/message_parser.py

import ast
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class OrderBookMessage:
    """Structured message data"""
    timestamp: float
    symbol: str
    bids: List[Tuple[float, float]]  # [(price, qty), ...]
    asks: List[Tuple[float, float]]
    is_snapshot: bool


class MessageParser:
    """Parse orderbook CSV messages"""

    @staticmethod
    def parse_price_levels(price_str: str) -> List[Tuple[float, float]]:
        """
        Convert string like "[['100.5', '1.5'], ['100.4', '2.0']]"
        to list of tuples [(100.5, 1.5), (100.4, 2.0)]
        """
        if price_str == "[]":
            return []

        # Use ast.literal_eval to safely parse the string
        raw_list = ast.literal_eval(price_str)

        # Convert strings to floats
        return [(float(price), float(qty)) for price, qty in raw_list]

    @staticmethod
    def is_snapshot(bids: List, asks: List) -> bool:
        """
        Snapshot = both bids and asks have data (typically 10 levels)
        Update = one or both might be empty or have fewer entries
        """
        # First message or both sides have full depth is snapshot
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
