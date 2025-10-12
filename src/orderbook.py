# src/orderbook.py

from sortedcontainers import SortedDict
from typing import Dict, List, Tuple, Optional


class OrderBook:
    """Efficient orderbook using SortedDict"""

    def __init__(self, symbol: str, depth: int = 10):
        self.symbol = symbol
        self.depth = depth

        # Bids: highest price first (reverse sort)
        self.bids = SortedDict(lambda x: -x)

        # Asks: lowest price first (normal sort)
        self.asks = SortedDict()

        self.last_update_time = None
        self.is_initialized = False

    def process_snapshot(self, bids: List[Tuple[float, float]],
                         asks: List[Tuple[float, float]],
                         timestamp: float) -> None:
        """Initialize orderbook from snapshot"""
        # Clear existing data
        self.bids.clear()
        self.asks.clear()

        # Load bids
        for price, qty in bids:
            self.bids[price] = qty

        # Load asks
        for price, qty in asks:
            self.asks[price] = qty

        self.last_update_time = timestamp
        self.is_initialized = True

    def process_update(self, bids: List[Tuple[float, float]],
                       asks: List[Tuple[float, float]],
                       timestamp: float) -> None:
        """Process incremental updates"""
        if not self.is_initialized:
            # First message should be snapshot
            self.process_snapshot(bids, asks, timestamp)
            return

        # Update bids
        for price, qty in bids:
            if qty == 0.0:
                # Delete price level
                if price in self.bids:
                    del self.bids[price]
            else:
                # Update or insert
                self.bids[price] = qty

        # Update asks
        for price, qty in asks:
            if qty == 0.0:
                # Delete price level
                if price in self.asks:
                    del self.asks[price]
            else:
                # Update or insert
                self.asks[price] = qty

        # Trim to depth (keep only top N)
        self._trim_to_depth()

        self.last_update_time = timestamp

    def _trim_to_depth(self) -> None:
        """Keep only top N levels per side"""
        # Keep first 'depth' items (already sorted)
        if len(self.bids) > self.depth:
            # Get keys to delete
            keys_to_delete = list(self.bids.keys())[self.depth:]
            for key in keys_to_delete:
                del self.bids[key]

        if len(self.asks) > self.depth:
            keys_to_delete = list(self.asks.keys())[self.depth:]
            for key in keys_to_delete:
                del self.asks[key]

    def get_top_n(self, n: int = 10) -> Dict[str, List[Tuple[float, float]]]:
        """Get top N bids and asks"""
        return {
            'bids': list(self.bids.items())[:n],
            'asks': list(self.asks.items())[:n]
        }