# main.py

import argparse
from src.processor import OrderBookProcessor


def main():
    parser = argparse.ArgumentParser(
        description='Order Book Maintenance System'
    )
    parser.add_argument('data_file', help='Path to CSV data file')
    parser.add_argument('timestamp', type=float, help='Target timestamp')
    parser.add_argument('symbol', help='Trading symbol (e.g., BTC/USD)')
    parser.add_argument('--depth', type=int, default=10,
                        help='Order book depth (default: 10)')

    args = parser.parse_args()

    print(f"Processing {args.symbol} until timestamp {args.timestamp}")
    print(f"Data file: {args.data_file}")
    print(f"Depth: {args.depth}\n")

    # Process file
    processor = OrderBookProcessor()
    orderbook = processor.process_file(
        args.data_file,
        args.symbol,
        args.timestamp,
        args.depth
    )

    if orderbook is None:
        print(f"Error: Symbol {args.symbol} not found in data")
        return

    # Get and display top 10
    top_10 = orderbook.get_top_n(10)

    print("Top 10 Bids (Buy Orders - Highest to Lowest):")
    print("-" * 50)
    for price, qty in top_10['bids']:
        print(f"  ${price:>12.8f}  |  {qty:>15.8f}")

    print("\nTop 10 Asks (Sell Orders - Lowest to Highest):")
    print("-" * 50)
    for price, qty in top_10['asks']:
        print(f"  ${price:>12.8f}  |  {qty:>15.8f}")

    print(f"\nLast update: {orderbook.last_update_time}")


if __name__ == '__main__':
    main()