# Data

This project uses daily NSE market data (BhavCopy) as the primary data source.

## Data Flow

NSE Daily Market Data
→ Python Processing
→ Azure Blob Storage
→ Power BI

## Data Storage

- Raw data is stored in the Azure Blob Storage `raw` container.
- Processed data is stored in the Azure Blob Storage `process` container.
- Large/raw CSV files are not stored directly in this GitHub repository.

## Data Processing

Python is used to clean, transform and calculate stock performance metrics including:

- Change Percentage
- Price Score
- Volume Score
- Turnover Score
- Market Mover Score
- Bullish/Bearish signals
