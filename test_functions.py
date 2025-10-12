# test_functions_cli.py

"""
Test required functions with real orderbook data
"""

from src.processor import OrderBookProcessor


def test_with_real_orderbook():
    """Test functions with actual market data"""

    data_file = "data/raw/orderbooks-10.csv"

    # Load real orderbook
    processor = OrderBookProcessor()
    ob = processor.process_file(data_file, "BTC/USD", 1755864237.5, depth=10)

    if not ob:
        print("Error: Could not load orderbook")
        return

    print("=" * 70)
    print("TESTING WITH REAL BTC/USD ORDERBOOK")
    print("=" * 70)

    # Show current state
    top = ob.get_top_n(5)
    print("\nCurrent Order Book (Top 5):")
    print("-" * 70)
    print("BIDS:")
    for price, qty in top['bids']:
        print(f"  ${price:>12.2f}  |  {qty:>10.8f} BTC")

    print("\nASKS:")
    for price, qty in top['asks']:
        print(f"  ${price:>12.2f}  |  {qty:>10.8f} BTC")

    # Test NotionalAhead
    print("\n" + "=" * 70)
    print("TEST 1: NotionalAhead")
    print("=" * 70)

    best_bid = top['bids'][0][0]
    best_ask = top['asks'][0][0]

    bid_notional = ob.notional_ahead('bid', best_bid)
    print(f"\nNotional ahead of best bid (${best_bid:,.2f}):")
    print(f"  ${bid_notional:,.2f}")

    ask_notional = ob.notional_ahead('ask', best_ask)
    print(f"\nNotional ahead of best ask (${best_ask:,.2f}):")
    print(f"  ${ask_notional:,.2f}")

    # Test at different price levels
    mid_price = (best_bid + best_ask) / 2
    bid_notional_mid = ob.notional_ahead('bid', mid_price)
    ask_notional_mid = ob.notional_ahead('ask', mid_price)

    print(f"\nNotional ahead of mid price (${mid_price:,.2f}):")
    print(f"  Bids: ${bid_notional_mid:,.2f}")
    print(f"  Asks: ${ask_notional_mid:,.2f}")

    # Test PlaceLimitOrder
    print("\n" + "=" * 70)
    print("TEST 2: PlaceLimitOrder")
    print("=" * 70)

    # Make a copy for testing (don't modify original)
    from copy import deepcopy
    test_ob = deepcopy(ob)

    # Aggressive buy order (crosses spread)
    order_price = best_ask + 10  # Well above best ask
    order_qty = top['asks'][0][1] * 0.5  # Half of best ask quantity

    print(f"\nPlacing BUY order:")
    print(f"  Price: ${order_price:,.2f}")
    print(f"  Quantity: {order_qty:.8f} BTC")
    print(f"  (This will match against asks)")

    result = test_ob.place_limit_order('buy', order_price, order_qty)

    print("\nOrder Book After Execution:")
    print("-" * 70)
    print("BIDS:")
    for price, qty in result['bids'][:5]:
        print(f"  ${price:>12.2f}  |  {qty:>10.8f} BTC")

    print("\nASKS:")
    for price, qty in result['asks'][:5]:
        print(f"  ${price:>12.2f}  |  {qty:>10.8f} BTC")

    # Passive sell order (doesn't cross spread)
    print("\n" + "-" * 70)

    passive_price = best_bid - 10  # Below best bid
    passive_qty = 1.0

    print(f"\nPlacing SELL order (passive):")
    print(f"  Price: ${passive_price:,.2f}")
    print(f"  Quantity: {passive_qty:.8f} BTC")
    print(f"  (This will NOT match, joins ask side)")

    result2 = test_ob.place_limit_order('sell', passive_price, passive_qty)

    print("\nOrder Book After Passive Order:")
    print("-" * 70)
    print("Top 3 Asks:")
    for price, qty in result2['asks'][:3]:
        print(f"  ${price:>12.2f}  |  {qty:>10.8f} BTC")

    print("\n" + "=" * 70)
    print("✓ REAL DATA TESTS COMPLETED")
    print("=" * 70)


if __name__ == '__main__':
    test_with_real_orderbook()