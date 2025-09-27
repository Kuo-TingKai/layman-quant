"""
Data provider for market data
市場數據提供者
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict
import time
import warnings
warnings.filterwarnings('ignore')

class DataProvider:
    """Data provider for market data using yfinance"""
    
    def __init__(self):
        """Initialize data provider"""
        self.cache = {}  # Simple cache for data
        self.cache_duration = 300  # Cache duration in seconds (5 minutes)
    
    def get_stock_data(self, symbol: str, period: str = "1y", 
                      interval: str = "1d") -> pd.DataFrame:
        """
        Get stock data for given symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"{symbol}_{period}_{interval}"
        current_time = time.time()
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if current_time - cache_time < self.cache_duration:
                return cached_data.copy()
        
        try:
            # Download data using yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"Warning: No data found for symbol {symbol}")
                return pd.DataFrame()
            
            # Clean and format data
            data = data.reset_index()
            data.columns = data.columns.str.lower()
            
            # Add symbol column
            data['symbol'] = symbol
            
            # Rename columns to standard format
            column_mapping = {
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            data = data.rename(columns=column_mapping)
            
            # Select only required columns
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'symbol']
            data = data[required_columns]
            
            # Cache the data
            self.cache[cache_key] = (data.copy(), current_time)
            
            return data
            
        except Exception as e:
            print(f"Error downloading data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_multiple_stocks_data(self, symbols: List[str], period: str = "1y", 
                                interval: str = "1d") -> pd.DataFrame:
        """
        Get data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            period: Data period
            interval: Data interval
            
        Returns:
            Combined DataFrame with data for all symbols
        """
        all_data = []
        
        for symbol in symbols:
            print(f"Downloading data for {symbol}...")
            data = self.get_stock_data(symbol, period, interval)
            if not data.empty:
                all_data.append(data)
            time.sleep(0.1)  # Small delay to avoid rate limiting
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            return combined_data
        else:
            return pd.DataFrame()
    
    def get_taiwan_stocks_data(self, symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """
        Get data for Taiwan stocks (add .TW suffix)
        
        Args:
            symbols: List of Taiwan stock symbols
            period: Data period
            
        Returns:
            DataFrame with Taiwan stock data
        """
        taiwan_symbols = [f"{symbol}.TW" for symbol in symbols]
        return self.get_multiple_stocks_data(taiwan_symbols, period)
    
    def get_etf_data(self, symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """
        Get data for ETFs
        
        Args:
            symbols: List of ETF symbols
            period: Data period
            
        Returns:
            DataFrame with ETF data
        """
        return self.get_multiple_stocks_data(symbols, period)
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate data quality
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if data is valid
        """
        if data.empty:
            return False
        
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            return False
        
        # Check for missing values
        if data[required_columns].isnull().any().any():
            return False
        
        # Check for negative prices
        price_columns = ['open', 'high', 'low', 'close']
        if (data[price_columns] <= 0).any().any():
            return False
        
        # Check for negative volume
        if (data['volume'] < 0).any():
            return False
        
        return True
    
    def get_data_summary(self, data: pd.DataFrame) -> Dict:
        """
        Get summary statistics for the data
        
        Args:
            data: DataFrame with market data
            
        Returns:
            Dictionary with summary statistics
        """
        if data.empty:
            return {}
        
        summary = {
            'total_records': len(data),
            'date_range': {
                'start': data['date'].min(),
                'end': data['date'].max()
            },
            'symbols': data['symbol'].unique().tolist(),
            'price_stats': {
                'min_close': data['close'].min(),
                'max_close': data['close'].max(),
                'avg_close': data['close'].mean(),
                'std_close': data['close'].std()
            },
            'volume_stats': {
                'min_volume': data['volume'].min(),
                'max_volume': data['volume'].max(),
                'avg_volume': data['volume'].mean(),
                'std_volume': data['volume'].std()
            }
        }
        
        return summary
