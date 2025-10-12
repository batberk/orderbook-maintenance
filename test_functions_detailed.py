# test_functions_detailed.py

"""
Detailed tests with clear verification
"""

from src.processor import OrderBookProcessor
from copy import deepcopy


def test_buy_order_matching():
    """Test buy order clearly consumes asks"""

    print("=" * 70)
    print("TEST: Buy Order Should Consume Asks")
    print("=" * 70)

    # Load real orderbook
    processor = OrderBookProcessor()
    ob = processor.process_file(
        "data/raw/orderbooks-10.csv",
        "BTC/USD",
        1755864237.5,
        depth=10
    )

    # Show initial state
    initial_asks = list(ob.asks.items())[:3]
    print("\n📊 BEFORE ORDER:")
    print("Top 3 Asks:")
    for price, qty in initial_asks:
        print(f"  ${price:>12.2f}  |  {qty:.8f} BTC")

    best_ask_price = initial_asks[0][0]
    best_ask_qty = initial_asks[0][1]

    # Place aggressive buy order that should match
    buy_price = best_ask_price + 100  # Well above best ask
    buy_qty = best_ask_qty * 0.5  # Buy half of best ask

    print(f"\n🔵 PLACING BUY ORDER:")
    print(f"  Price: ${buy_price:,.2f} (above best ask)")
    print(f"  Quantity: {buy_qty:.8f} BTC (half of best ask)")
    print(f"  Expected: Should consume from ask at ${best_ask_price:.2f}")

    # Execute
    result = ob.place_limit_order('buy', buy_price, buy_qty)

    # Show results
    print(f"\n📊 AFTER ORDER:")
    print("Top 3 Asks:")
    for price, qty in result['asks'][:3]:
        print(f"  ${price:>12.2f}  |  {qty:.8f} BTC")

    # Verify
    remaining_qty = result['asks'][0][1]
    expected_remaining = best_ask_qty - buy_qty

    print(f"\n✓ VERIFICATION:")
    print(f"  Original quantity at ${best_ask_price:.2f}: {best_ask_qty:.8f}")
    print(f"  Buy quantity: {buy_qty:.8f}")
    print(f"  Expected remaining: {expected_remaining:.8f}")
    print(f"  Actual remaining: {remaining_qty:.8f}")

    if abs(remaining_qty - expected_remaining) < 0.00000001:
        print(f"  ✅ PASS: Order matched correctly!")
    else:
        print(f"  ❌ FAIL: Quantities don't match!")

    print()


def test_sell_order_matching():
    """Test sell order clearly consumes bids"""

    print("=" * 70)
    print("TEST: Sell Order Should Consume Bids")
    print("=" * 70)

    # Load real orderbook
    processor = OrderBookProcessor()
    ob = processor.process_file(
        "data/raw/orderbooks-10.csv",
        "BTC/USD",
        1755864237.5,
        depth=10
    )

    # Show initial state
    initial_bids = list(ob.bids.items())[:3]
    print("\n📊 BEFORE ORDER:")
    print("Top 3 Bids:")
    for price, qty in initial_bids:
        print(f"  ${price:>12.2f}  |  {qty:.8f} BTC")

    best_bid_price = initial_bids[0][0]
    best_bid_qty = initial_bids[0][1]

    # Place aggressive sell order that should match
    sell_price = best_bid_price - 100  # Well below best bid
    sell_qty = best_bid_qty * 0.3  # Sell 30% of best bid

    print(f"\n🔴 PLACING SELL ORDER:")
    print(f"  Price: ${sell_price:,.2f} (below best bid)")
    print(f"  Quantity: {sell_qty:.8f} BTC (30% of best bid)")
    print(f"  Expected: Should consume from bid at ${best_bid_price:.2f}")

    # Execute
    result = ob.place_limit_order('sell', sell_price, sell_qty)

    # Show results
    print(f"\n📊 AFTER ORDER:")
    print("Top 3 Bids:")
    for price, qty in result['bids'][:3]:
        print(f"  ${price:>12.2f}  |  {qty:.8f} BTC")

    # Verify
    remaining_qty = result['bids'][0][1]
    expected_remaining = best_bid_qty - sell_qty

    print(f"\n✓ VERIFICATION:")
    print(f"  Original quantity at ${best_bid_price:.2f}: {best_bid_qty:.8f}")
    print(f"  Sell quantity: {sell_qty:.8f}")
    print(f"  Expected remaining: {expected_remaining:.8f}")
    print(f"  Actual remaining: {remaining_qty:.8f}")

    if abs(remaining_qty - expected_remaining) < 0.00000001:
        print(f"  ✅ PASS: Order matched correctly!")
    else:
        print(f"  ❌ FAIL: Quantities don't match!")

    print()


def test_passive_order():
    """Test order that doesn't match (joins book)"""

    print("=" * 70)
    print("TEST: Passive Order Should Join Book")
    print("=" * 70)

    # Load real orderbook
    processor = OrderBookProcessor()
    ob = processor.process_file(
        "data/raw/orderbooks-10.csv",
        "BTC/USD",
        1755864237.5,
        depth=10
    )

    best_bid = list(ob.bids.items())[0][0]
    best_ask = list(ob.asks.items())[0][0]

    print(f"\n📊 CURRENT SPREAD:")
    print(f"  Best Bid: ${best_bid:,.2f}")
    print(f"  Best Ask: ${best_ask:,.2f}")
    print(f"  Spread: ${best_ask - best_bid:.2f}")

    # Place passive sell order in the middle
    passive_price = (best_bid + best_ask) / 2
    passive_qty = 0.5

    print(f"\n🟡 PLACING PASSIVE SELL ORDER:")
    print(f"  Price: ${passive_price:,.2f} (in the spread)")
    print(f"  Quantity: {passive_qty:.8f} BTC")
    print(f"  Expected: Should join ask side (no matching)")

    # Execute
    result = ob.place_limit_order('sell', passive_price, passive_qty)

    # Show results
    print(f"\n📊 AFTER ORDER:")
    print("Top 5 Asks:")
    for price, qty in result['asks'][:5]:
        marker = " ← NEW" if abs(price - passive_price) < 0.01 else ""
        print(f"  ${price:>12.2f}  |  {qty:.8f} BTC{marker}")

    # Verify
    if passive_price in ob.asks:
        print(f"\n  ✅ PASS: Order added to ask side at ${passive_price:.2f}!")
    else:
        print(f"\n  ❌ FAIL: Order not found in ask side!")

    print()


def test_notional_calculation():
    """Test notional calculation with clear examples"""

    print("=" * 70)
    print("TEST: Notional Calculation")
    print("=" * 70)

    # Load real orderbook
    processor = OrderBookProcessor()
    ob = processor.process_file(
        "data/raw/orderbooks-10.csv",
        "BTC/USD",
        1755864237.5,
        depth=10
    )

    # Get top levels
    top_bids = list(ob.bids.items())[:3]
    top_asks = list(ob.asks.items())[:3]

    print("\n📊 TOP 3 LEVELS:")
    print("\nBids:")
    for price, qty in top_bids:
        notional = price * qty
        print(f"  ${price:>12.2f} × {qty:.8f} = ${notional:>15.2f}")

    print("\nAsks:")
    for price, qty in top_asks:
        notional = price * qty
        print(f"  ${price:>12.2f} × {qty:.8f} = ${notional:>15.2f}")

    # Calculate notional at best bid
    best_bid = top_bids[0][0]
    bid_notional = ob.notional_ahead('bid', best_bid)

    # Manual calculation
    manual_bid_notional = sum(p * q for p, q in top_bids if p >= best_bid)

    print(f"\n💰 NOTIONAL AT BEST BID (${best_bid:,.2f}):")
    print(f"  Calculated: ${bid_notional:,.2f}")
    print(f"  Manual: ${manual_bid_notional:,.2f}")

    if abs(bid_notional - manual_bid_notional) < 0.01:
        print(f"  ✅ PASS: Notional calculation correct!")
    else:
        print(f"  ❌ FAIL: Notional mismatch!")

    print()


if __name__ == '__main__':
    test_notional_calculation()
    test_buy_order_matching()
    test_sell_order_matching()
    test_passive_order()

    print("=" * 70)
    print("✓ ALL DETAILED TESTS COMPLETED")
    print("=" * 70)