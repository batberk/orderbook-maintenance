# test_basic.py

"""
Basic tests to verify setup is working
"""

from src.orderbook import OrderBook


def test_snapshot():
    """Test snapshot loading"""
    print("Testing snapshot loading...")

    ob = OrderBook("TEST/USD", depth=10)

    bids = [(100.0, 1.0), (99.0, 2.0), (98.0, 3.0)]
    asks = [(101.0, 1.5), (102.0, 2.5), (103.0, 3.5)]

    ob.process_snapshot(bids, asks, 123456.0)

    top = ob.get_top_n(10)

    print(f"  Top bid: {top['bids'][0]}")
    print(f"  Top ask: {top['asks'][0]}")

    # Verify highest bid is first
    assert top['bids'][0] == (100.0, 1.0), "Highest bid should be first"
    assert top['asks'][0] == (101.0, 1.5), "Lowest ask should be first"

    print("  ✓ Snapshot test passed!\n")


def test_update():
    """Test update processing"""
    print("Testing updates...")

    ob = OrderBook("TEST/USD", depth=10)

    # Initialize with snapshot
    ob.process_snapshot([(100.0, 1.0)], [(101.0, 1.5)], 1.0)

    # Add new bid at higher price
    ob.process_update([(100.5, 2.0)], [], 2.0)

    top = ob.get_top_n(10)

    print(f"  After update, top bid: {top['bids'][0]}")

    assert top['bids'][0] == (100.5, 2.0), "New bid should be at top"

    print("  ✓ Update test passed!\n")


def test_deletion():
    """Test price level deletion"""
    print("Testing deletions...")

    ob = OrderBook("TEST/USD", depth=10)

    # Initialize
    bids = [(100.0, 1.0), (99.0, 2.0), (98.0, 3.0)]
    ob.process_snapshot(bids, [(101.0, 1.5)], 1.0)

    print(f"  Before deletion - top 3 bids: {ob.get_top_n(3)['bids']}")

    # Delete top bid (quantity = 0)
    ob.process_update([(100.0, 0.0)], [], 2.0)

    top = ob.get_top_n(10)

    print(f"  After deletion - top bid: {top['bids'][0]}")

    assert top['bids'][0] == (99.0, 2.0), "After deletion, 99.0 should be top"
    assert 100.0 not in ob.bids, "Deleted price should not exist"

    print("  ✓ Deletion test passed!\n")


def test_parser():
    """Test message parser"""
    print("Testing message parser...")

    from src.message_parser import MessageParser

    parser = MessageParser()

    # Test parsing price levels string
    price_str = "[['100.5', '1.5'], ['100.4', '2.0']]"
    parsed = parser.parse_price_levels(price_str)

    print(f"  Parsed: {parsed}")

    assert parsed == [(100.5, 1.5), (100.4, 2.0)], "Parser should convert strings to floats"

    # Test empty list
    empty = parser.parse_price_levels("[]")
    assert empty == [], "Empty list should parse correctly"

    print("  ✓ Parser test passed!\n")


if __name__ == '__main__':
    print("=" * 50)
    print("Running Basic Tests")
    print("=" * 50 + "\n")

    try:
        test_parser()
        test_snapshot()
        test_update()
        test_deletion()

        print("=" * 50)
        print("✓ ALL TESTS PASSED!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()