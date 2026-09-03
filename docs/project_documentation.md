# NSE Stock Market Analysis — Project Documentation

## 1. Project Overview

This project processes daily NSE BhavCopy market data and transforms it into useful stock-market insights.

The project combines Python, Azure Blob Storage, and Power BI to create an automated data-processing and visualization workflow.

## 2. Objective

The main objectives are:

- Process daily NSE equity market data
- Identify top gainers and losers
- Calculate stock price movement
- Analyze trading volume and turnover
- Generate bullish and bearish stock signals
- Track stock performance across trading days
- Present insights through an interactive Power BI dashboard

## 3. Data Source

The project uses NSE BhavCopy as the daily market-data source.

The dataset contains information such as:

- Trading Date
- Stock Symbol
- Open Price
- High Price
- Low Price
- Close Price
- Previous Close Price
- Trading Volume
- Turnover
- Number of Trades

## 4. Data Pipeline

```text
NSE BhavCopy
     ↓
Python
     ↓
Data Cleaning & Transformation
     ↓
Market Calculations
     ↓
Azure Blob Storage
     ↓
Power BI
     ↓
Interactive Dashboard
