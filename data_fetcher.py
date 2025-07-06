"""
Data Fetcher Module
Handles all data input and fetching functionality
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import backtrader as bt
from typing import Dict, Optional, Tuple


class CustomYahooData(bt.feeds.PandasData):
    """Custom data feed for Yahoo Finance data"""
    params = (
        ('datetime', None),  # Use index as datetime
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
        ('openinterest', -1),
    )


class DataFetcher:
    """Handles data fetching and preprocessing"""
    
    @staticmethod
    def get_default_dates() -> Tuple[str, str]:
        """Get default start and end dates"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    @staticmethod
    def fetch_yahoo_data(symbol: str, interval: str, start: str, end: str) -> pd.DataFrame:
        """Fetch data from Yahoo Finance with error handling"""
        try:
            df = yf.download(symbol, start=start, end=end, interval=interval)
            if df.empty:
                raise ValueError("No data returned from Yahoo Finance")

            # Handle MultiIndex columns (common with yfinance)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)

            # Clean the data
            df.dropna(inplace=True)

            # Ensure the index is datetime
            df.index = pd.to_datetime(df.index)

            # Validate columns
            expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in expected_columns:
                if col not in df.columns:
                    print(f"Warning: Column '{col}' not found in data")

            print(f"Data fetched successfully: {len(df)} records")
            print(f"Date range: {df.index.min()} to {df.index.max()}")

            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_user_config() -> Optional[Dict]:
        """Get user configuration - can be replaced with UI input"""
        default_start, default_end = DataFetcher.get_default_dates()
        
        # Default configuration
        default_config = {
            'symbol': 'BTC-USD',
            'start_date': default_start,
            'end_date': default_end,
            'interval': '1h',
            'initial_capital': 10000,
            'commission': 0.001
        }
        
        return default_config
    
    @staticmethod
    def validate_data(df: pd.DataFrame) -> bool:
        """Validate the fetched data"""
        if df.empty:
            return False
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return all(col in df.columns for col in required_columns)