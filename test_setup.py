"""
Quick test to verify setup is working
"""

from sortedcontainers import SortedDict

def test_sorted_dict():
    """Test SortedDict works for our use case"""
    
    # Test bids (reverse sorted - highest first)
    bids = SortedDict(lambda x: -x)
    bids[100.5] = 1.5
    bids[99.0] = 2.0
    bids[101.0] = 1.0
    
    print("Bids (highest price first):")
    for price, qty in list(bids.items())[:3]:
        print(f"  ${price}: {qty} BTC")
    
    # Verify order is correct
    prices = list(bids.keys())
    assert prices[0] == 101.0, "Highest bid should be first"
    assert prices[1] == 100.5
    assert prices[2] == 99.0
    
    # Test asks (normal sorted - lowest first)
    asks = SortedDict()
    asks[100.5] = 1.5
    asks[99.0] = 2.0
    asks[101.0] = 1.0
    
    print("\nAsks (lowest price first):")
    for price, qty in list(asks.items())[:3]:
        print(f"  ${price}: {qty} BTC")
    
    # Verify order is correct
    prices = list(asks.keys())
    assert prices[0] == 99.0, "Lowest ask should be first"
    assert prices[1] == 100.5
    assert prices[2] == 101.0
    
    print("\n✓ SortedDict working correctly for order book!")
    
    # Test operations we'll need
    print("\nTesting key operations:")
    
    # Access top N
    top_3_bids = list(bids.items())[:3]
    print(f"  Top 3 bids: {top_3_bids}")
    
    # Update
    bids[100.5] = 2.5
    print(f"  Updated bid at 100.5: {bids[100.5]}")
    
    # Delete
    del bids[99.0]
    print(f"  Deleted bid at 99.0, remaining: {len(bids)}")
    
    # Check if price exists
    if 101.0 in bids:
        print(f"  Price 101.0 exists with quantity: {bids[101.0]}")
    
    print("\n✓ All operations working!")

if __name__ == '__main__':
    test_sorted_dict()
