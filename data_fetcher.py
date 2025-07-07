"""
Data Fetcher Module
Handles all data input and fetching functionality
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import backtrader as bt
from typing import Dict, Optional, Tuple
import ccxt


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
    def fetch_binance_data(symbol: str, interval: str, start: str, end: str) -> pd.DataFrame:
        """Fetch Bitcoin and Ethereum data from Binance"""
        try:
            exchange = ccxt.binance()
            
            # Convert symbol format for Binance (BTC-USD -> BTC/USDT)
            binance_symbol = symbol.replace('-USD', '/USDT')
            
            # Convert dates to timestamps
            since = exchange.parse8601(f"{start}T00:00:00Z")
            until = exchange.parse8601(f"{end}T00:00:00Z")
            
            # Convert interval format for Binance
            interval_map = {
                '1m': '1m',
                '5m': '5m', 
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '4h': '4h',
                '1d': '1d',
                '1wk': '1w',
                '1mo': '1M'
            }
            binance_interval = interval_map.get(interval, '1h')
            
            print(f"Fetching {binance_symbol} data from Binance...")
            
            # Fetching the historical data
            candles = exchange.fetch_ohlcv(binance_symbol, timeframe=binance_interval, since=since, limit=1000)
            
            if not candles:
                print(f"No data returned from Binance for {binance_symbol}")
                return pd.DataFrame()
            
            # Create DataFrame from the data received
            df = pd.DataFrame(candles, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Filter data by end date
            if until:
                end_datetime = pd.to_datetime(end)
                df = df[df.index <= end_datetime]
            
            print(f"✅ Binance data fetched successfully: {len(df)} records")
            print(f"Date range: {df.index.min()} to {df.index.max()}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching from Binance: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def fetch_yahoo_data(symbol: str, interval: str, start: str, end: str) -> pd.DataFrame:
        """Fetch data from Yahoo Finance with error handling and fallbacks"""
        
        # Alternative symbols to try if the original fails
        symbol_alternatives = {
            'BTC-USD': ['BTC-USD', 'BTCUSD=X', 'BTC=F'],
            'ETH-USD': ['ETH-USD', 'ETHUSD=X', 'ETH=F'],
        }
        
        symbols_to_try = symbol_alternatives.get(symbol, [symbol])
        
        for attempt_symbol in symbols_to_try:
            try:
                print(f"Attempting to fetch data for {attempt_symbol}...")
                
                # Try with different parameters
                df = yf.download(
                    attempt_symbol, 
                    start=start, 
                    end=end, 
                    interval=interval,
                    progress=False,
                    threads=False
                )
                
                if df.empty:
                    print(f"No data returned for {attempt_symbol}")
                    continue

                # Handle MultiIndex columns (common with yfinance)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)

                # Clean the data
                df.dropna(inplace=True)
                
                if df.empty:
                    print(f"No data after cleaning for {attempt_symbol}")
                    continue

                # Ensure the index is datetime
                df.index = pd.to_datetime(df.index)

                # Validate columns
                expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                missing_columns = [col for col in expected_columns if col not in df.columns]
                
                if missing_columns:
                    print(f"Missing columns for {attempt_symbol}: {missing_columns}")
                    continue

                print(f"✅ Data fetched successfully for {attempt_symbol}: {len(df)} records")
                print(f"Date range: {df.index.min()} to {df.index.max()}")

                return df
                
            except Exception as e:
                print(f"❌ Error fetching data for {attempt_symbol}: {e}")
                continue
        
        # If all attempts failed, try Binance for crypto symbols
        if symbol.startswith(('BTC', 'ETH', 'CRYPTO')):
            print("Yahoo Finance crypto symbols failed, trying Binance...")
            df = DataFetcher.fetch_binance_data(symbol, interval, start, end)
            if not df.empty:
                return df
        
        # All data sources failed - return empty DataFrame
        print("❌ All external data sources failed (likely due to network restrictions)")
        print("🚫 Unable to fetch market data. Please check your internet connection or try again later.")
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
    
    