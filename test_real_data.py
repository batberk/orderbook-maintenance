# test_real_data.py

"""
Test with actual CSV data
"""

from src.processor import OrderBookProcessor
import os


def test_with_real_data():
    """Test processing real CSV file"""

    # Update this path to your actual CSV file
    data_file = "data/raw/orderbooks-1000.csv"  # Adjust filename

    if not os.path.exists(data_file):
        print(f"Error: Data file not found at {data_file}")
        print("Please update the path in test_real_data.py")
        return

    print(f"Testing with real data from: {data_file}\n")

    # Use a timestamp from your data
    # Looking at your sample, first timestamp is around 1755864237.347009
    target_timestamp = 1755866982.8128388  # Process first ~0.2 seconds
    target_symbol = "BTC/USD"

    print(f"Processing {target_symbol} until timestamp {target_timestamp}")
    print("This should process the first few messages...\n")

    processor = OrderBookProcessor()

    try:
        orderbook = processor.process_file(
            data_file,
            target_symbol,
            target_timestamp,
            depth=1000
        )

        if orderbook is None:
            print(f"Error: {target_symbol} not found in data")
            return

        # Get top 10
        top_10 = orderbook.get_top_n(10)

        print("=" * 60)
        print(f"Order Book for {target_symbol}")
        print("=" * 60)

        print("\nTop 10 Bids (Highest to Lowest):")
        print("-" * 60)
        for i, (price, qty) in enumerate(top_10['bids'], 1):
            print(f"  {i:2d}. ${price:>15.8f}  |  {qty:>18.8f}")

        print("\nTop 10 Asks (Lowest to Highest):")
        print("-" * 60)
        for i, (price, qty) in enumerate(top_10['asks'], 1):
            print(f"  {i:2d}. ${price:>15.8f}  |  {qty:>18.8f}")

        print(f"\nLast Update: {orderbook.last_update_time}")
        print(f"Total Bid Levels: {len(orderbook.bids)}")
        print(f"Total Ask Levels: {len(orderbook.asks)}")

        print("\n✓ Real data test completed successfully!")

    except Exception as e:
        print(f"✗ Error processing data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_with_real_data()