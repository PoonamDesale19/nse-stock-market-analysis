# NSE Stock Market Analysis

##  Project Overview

An automated NSE stock market data pipeline and analytics project that processes daily NSE market data, calculates stock performance indicators, identifies market movers, and presents insights through an interactive Power BI dashboard.

##  Business Objective

The objective of this project is to transform daily NSE market data into actionable insights by identifying:

- Top gaining and losing stocks
- Bullish and bearish market signals
- Market strength and movement
- Stock price performance
- Trading volume and turnover trends
- Stocks to watch for the next trading session

##  Project Architecture

NSE Daily Data
        ↓
Python ETL
        ↓
Azure Blob Storage
        ↓
Data Processing
        ↓
SQL Analysis
        ↓
Power BI Dashboard
        ↓
Business Insights

##  Technologies Used

- Python
- Pandas
- NumPy
- SQL
- Power BI
- DAX
- Power Query
- Azure Blob Storage
- Azure Data Factory
- GitHub

##  Data Pipeline

1. Retrieve daily NSE BhavCopy data
2. Validate and clean the raw data
3. Filter equity securities
4. Calculate daily price movement
5. Calculate market mover scores
6. Calculate price, volume and turnover scores
7. Generate bullish and bearish signals
8. Store processed data in Azure
9. Analyze data using SQL
10. Build interactive Power BI dashboards

##  Key Calculations

### Daily Price Change

Change Percentage is calculated as:

Change % = ((Closing Price - Previous Closing Price) / Previous Closing Price) × 100

### Market Strength Score

Market Strength Score combines:

- Price Score – 50%
- Volume Score – 20%
- Turnover Score – 30%

##  Power BI Dashboard

The dashboard provides:

- Market Movers
- Top 10 Gainers
- Top 10 Losers
- Market Direction
- Stock Signals
- Stock Summary
- Historical Stock Movement
- Open, High, Low and Close prices

##  Project Structure

```text
nse-stock-market-analysis/
│
├── README.md
├── python/
├── sql/
├── powerbi/
├── data/
└── docs/
