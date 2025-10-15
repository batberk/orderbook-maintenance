from sortedcontainers import SortedDict
from typing import Dict, List, Tuple


class OrderBook:
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
        Calculate total notional value ahead of given price level
        Args:
            side: 'bid' or 'ask'
            price: Price level to calculate from

        Returns:
            Total notional value (sum of price * quantity)
        """
        book = self.bids if side == 'bid' else self.asks
        total_notional = 0.0

        if side == 'bid':
            # Sum all levels with price >= given price
            for p, q in book.items():
                if p >= price:
                    total_notional += p * q
                else:
                    # SortedDict is ordered, we can break early
                    break
        else:  # ask
            # Sum all levels with price <= given price
            for p, q in book.items():
                if p <= price:
                    total_notional += p * q
                else:
                    # SortedDict is ordered, we can break early
                    break

        return total_notional

    def place_limit_order(self, order_side: str, price: float,
                          quantity: float) -> Dict[str, List[Tuple[float, float]]]:
        """
        Simulate placing a limit order with matching engine logic

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
            to_delete = []

            for ask_price, available_qty in self.asks.items():
                if remaining_qty <= 0:
                    break
                if ask_price > price:
                    break

                if available_qty <= remaining_qty:
                    remaining_qty -= available_qty
                    to_delete.append(ask_price)
                else:
                    self.asks[ask_price] = available_qty - remaining_qty
                    remaining_qty = 0
                    break

            for ask_price in to_delete:
                del self.asks[ask_price]

            if remaining_qty > 0:
                if price in self.bids:
                    self.bids[price] += remaining_qty
                else:
                    self.bids[price] = remaining_qty
                self._trim_to_depth()

        else:  # sell order
            # Sell order matches against bids (removes liquidity from bid side)
            # Can match at prices >= our limit price
            to_delete = []

            for bid_price, available_qty in self.bids.items():
                if remaining_qty <= 0:
                    break
                if bid_price < price:
                    break

                if available_qty <= remaining_qty:
                    remaining_qty -= available_qty
                    to_delete.append(bid_price)
                else:
                    self.bids[bid_price] = available_qty - remaining_qty
                    remaining_qty = 0
                    break

            for bid_price in to_delete:
                del self.bids[bid_price]

            if remaining_qty > 0:
                if price in self.asks:
                    self.asks[price] += remaining_qty
                else:
                    self.asks[price] = remaining_qty
                self._trim_to_depth()

        return self.get_top_n(10)
