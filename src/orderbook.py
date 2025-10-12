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
        """Keep only top N levels per side using efficient slicing"""
        if len(self.bids) > self.depth:
            for key in list(self.bids.islice(self.depth, None)):
                del self.bids[key]
        if len(self.asks) > self.depth:
            for key in list(self.asks.islice(self.depth, None)):
                del self.asks[key]

    def get_top_n(self, n: int = 10) -> Dict[str, List[Tuple[float, float]]]:
        """Get top N bids and asks"""
        return {
            'bids': list(self.bids.items())[:n],
            'asks': list(self.asks.items())[:n]
        }

    def notional_ahead(self, side: str, price: float) -> float:
        """
        Calculate total notional value ahead of given price

        Notional = price * quantity for each level
        "Ahead" means:
        - For bids: all prices >= given price (higher or equal)
        - For asks: all prices <= given price (lower or equal)

        Args:
            side: 'bid' or 'ask'
            price: Price level to calculate from

        Returns:
            Total notional value (sum of price * quantity)

        Example:
            Bids: [100->2.0, 99->3.0, 98->1.0]
            notional_ahead('bid', 99) = (100*2.0) + (99*3.0) = 200 + 297 = 497
        """
        book = self.bids if side == 'bid' else self.asks
        total_notional = 0.0

        if side == 'bid':
            # For bids: better prices are HIGHER
            # Sum all levels with price >= given price
            for p, q in book.items():
                if p >= price:
                    total_notional += p * q
                else:
                    # SortedDict is ordered, we can break early
                    # (bids go from high to low)
                    break
        else:  # ask
            # For asks: better prices are LOWER
            # Sum all levels with price <= given price
            for p, q in book.items():
                if p <= price:
                    total_notional += p * q
                else:
                    # SortedDict is ordered, we can break early
                    # (asks go from low to high)
                    break

        return total_notional

    def place_limit_order(self, order_side: str, price: float,
                          quantity: float) -> Dict[str, List[Tuple[float, float]]]:
        """
        Simulate placing a limit order with matching engine logic

        Limit Order Behavior:
        - BUY order: Will match against asks at or below limit price
        - SELL order: Will match against bids at or above limit price
        - Unmatched quantity joins the book on appropriate side

        Args:
            order_side: 'buy' or 'sell'
            price: Limit price for the order
            quantity: Order quantity

        Returns:
            Updated top 10 bids and asks after order execution
        """
        remaining_qty = quantity

        if order_side == 'buy':
            # Buy order matches against asks (removes liquidity from ask side)
            # Can match at prices <= our limit price

            # Get all ask prices (sorted low to high)
            ask_prices = list(self.asks.keys())

            for ask_price in ask_prices:
                if remaining_qty <= 0:
                    break

                # Can only match if ask price <= our limit price
                if ask_price > price:
                    break  # No more matching possible

                available_qty = self.asks[ask_price]

                if available_qty <= remaining_qty:
                    # Fully consume this ask level
                    remaining_qty -= available_qty
                    del self.asks[ask_price]
                else:
                    # Partially consume this ask level
                    self.asks[ask_price] -= remaining_qty
                    remaining_qty = 0

            # If we have remaining quantity, add it to bid side
            if remaining_qty > 0:
                if price in self.bids:
                    self.bids[price] += remaining_qty
                else:
                    self.bids[price] = remaining_qty

                # Trim to depth
                self._trim_to_depth()

        else:  # sell order
            # Sell order matches against bids (removes liquidity from bid side)
            # Can match at prices >= our limit price

            # Get all bid prices (sorted high to low due to our reverse sort)
            bid_prices = list(self.bids.keys())

            for bid_price in bid_prices:
                if remaining_qty <= 0:
                    break

                # Can only match if bid price >= our limit price
                if bid_price < price:
                    break  # No more matching possible

                available_qty = self.bids[bid_price]

                if available_qty <= remaining_qty:
                    # Fully consume this bid level
                    remaining_qty -= available_qty
                    del self.bids[bid_price]
                else:
                    # Partially consume this bid level
                    self.bids[bid_price] -= remaining_qty
                    remaining_qty = 0

            # If we have remaining quantity, add it to ask side
            if remaining_qty > 0:
                if price in self.asks:
                    self.asks[price] += remaining_qty
                else:
                    self.asks[price] = remaining_qty

                # Trim to depth
                self._trim_to_depth()

        # Return updated top 10
        return self.get_top_n(10)