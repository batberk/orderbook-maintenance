# Case Study 1: Order Book Maintenance

## Overview

This program maintains an accurate order book by processing messages from a CSV file. It handles both snapshots (complete order book state) and incremental updates, then displays the top 10 bids and asks at a specified timestamp.

## File Structure

Your directory should look like this:

```
Case Study 1/
├── main.py
├── src/
│   ├── orderbook.py
│   ├── message_parser.py
│   └── processor.py
├── requirements.txt
├── README.md
└── orderbooks.csv          # Place your data file here
```

The CSV data file should be in the same directory as `main.py`.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The main dependency is `sortedcontainers`, which provides the `SortedDict` data structure used for efficient order book operations.

## Usage

```bash
python main.py <data_file> <timestamp> <symbol> [--depth DEPTH]
```

### Examples

```bash
python main.py orderbooks.csv 1634567890.5 BTC/USD
python main.py orderbooks.csv 1634567890.5 ETH/USD --depth 1000
```

The program processes all messages for the specified symbol until reaching the target timestamp, then displays the order book state at that moment.

## Output

```
Processing BTC/USD until timestamp 1634567890.5
Data file: orderbooks.csv
Depth: 10

Top 10 Bids (Buy Orders - Highest to Lowest):
--------------------------------------------------
  $ 50125.50000000  |        2.45000000
  $ 50125.00000000  |        1.20000000
  ...

Top 10 Asks (Sell Orders - Lowest to Highest):
--------------------------------------------------
  $ 50126.00000000  |        1.80000000
  $ 50126.50000000  |        3.20000000
  ...

Last update: 1634567890.5
```

## Key Functions

### NotionalAhead(side, price)

Calculates the total notional value (price × quantity) of all orders ahead of a given price level.

- **For bids**: sums all levels with price ≥ target (higher prices are better)
- **For asks**: sums all levels with price ≤ target (lower prices are better)

Usage example:
```python
orderbook = processor.process_file('orderbooks.csv', 'BTC/USD', 1634567890.5)
notional = orderbook.notional_ahead('bid', 50000.0)
```

### PlaceLimitOrder(side, price, quantity)

Simulates placing a limit order with realistic matching engine behavior.

- **Buy orders** match against asks at or below the limit price
- **Sell orders** match against bids at or above the limit price
- Unmatched quantity joins the book at the specified price
- Returns updated top 10 bids and asks after execution

Usage example:
```python
result = orderbook.place_limit_order('buy', 50000.0, 1.5)
print(result['bids'])
print(result['asks'])
```

## Design Decisions

### SortedDict Data Structure

The implementation uses `SortedDict` for maintaining price levels because it provides O(log n) time complexity for insertions, deletions, and updates while automatically maintaining sorted order. This is significantly faster than repeatedly sorting a regular dictionary after each update.

### Bid and Ask Ordering

The order book maintains different sort orders for each side:
- **Bids**: descending order (highest price first) using `SortedDict(lambda x: -x)`
- **Asks**: ascending order (lowest price first) using `SortedDict()`

This matches standard market conventions where better prices appear first.

### Memory Management

The implementation automatically trims the order book to the specified depth after each update. This keeps memory usage bounded and maintains performance even when processing large datasets.

## Performance

The code is designed to process the entire order book file in under 60 seconds per symbol. Key optimizations include:

- O(log n) operations using SortedDict
- Early loop termination when conditions are met
- In-place updates without unnecessary data copying
- Efficient depth trimming using `islice`

Typical processing time: 2-5 seconds for ~100,000 messages.

## Code Structure

- **`main.py`**: Entry point and command-line interface
- **`src/orderbook.py`**: Core order book maintenance logic
- **`src/message_parser.py`**: CSV parsing and message structure
- **`src/processor.py`**: File processing and message routing
- **`requirements.txt`**: Python dependencies

## Testing

The implementation can be tested with different depth parameters to verify both accuracy and performance across various configurations.