"""
Taiwan stock data provider
台股數據提供者
"""

import yfinance as yf
import pandas as pd
import requests
import json
from typing import List, Dict
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

class TaiwanDataProvider:
    """Taiwan stock data provider using multiple sources"""
    
    def __init__(self):
        """Initialize Taiwan data provider"""
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
    def get_taiwan_stock_data(self, symbol: str, period: str = "1y", 
                             interval: str = "1d") -> pd.DataFrame:
        """
        Get Taiwan stock data using yfinance with .TW suffix
        
        Args:
            symbol: Taiwan stock symbol (e.g., '2330' for TSMC)
            period: Data period
            interval: Data interval
            
        Returns:
            DataFrame with OHLCV data
        """
        # Add .TW suffix for Taiwan stocks
        if not symbol.endswith('.TW'):
            symbol = f"{symbol}.TW"
        
        cache_key = f"taiwan_{symbol}_{period}_{interval}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if current_time - cache_time < self.cache_duration:
                return cached_data.copy()
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"Warning: No data found for Taiwan stock {symbol}")
                return pd.DataFrame()
            
            # Clean and format data
            data = data.reset_index()
            data.columns = data.columns.str.lower()
            
            # Add symbol column (remove .TW suffix for display)
            display_symbol = symbol.replace('.TW', '')
            data['symbol'] = display_symbol
            
            # Rename columns
            column_mapping = {
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            data = data.rename(columns=column_mapping)
            
            # Select required columns
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'symbol']
            data = data[required_columns]
            
            # Cache the data
            self.cache[cache_key] = (data.copy(), current_time)
            
            return data
            
        except Exception as e:
            print(f"Error downloading Taiwan stock data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_twse_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get Taiwan stock data from TWSE official API
        
        Args:
            symbol: Taiwan stock symbol (e.g., '2330')
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            
        Returns:
            DataFrame with OHLCV data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            # TWSE API endpoint
            url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY"
            params = {
                'response': 'json',
                'date': end_date,
                'stockNo': symbol
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('stat') != 'OK':
                print(f"TWSE API error: {data.get('message', 'Unknown error')}")
                return pd.DataFrame()
            
            # Parse the data
            fields = data['fields']
            records = data['data']
            
            # Convert to DataFrame
            df = pd.DataFrame(records, columns=fields)
            
            # Clean and format data
            df['date'] = pd.to_datetime(df['日期'], format='%Y%m%d')
            df['open'] = pd.to_numeric(df['開盤價'].str.replace(',', ''), errors='coerce')
            df['high'] = pd.to_numeric(df['最高價'].str.replace(',', ''), errors='coerce')
            df['low'] = pd.to_numeric(df['最低價'].str.replace(',', ''), errors='coerce')
            df['close'] = pd.to_numeric(df['收盤價'].str.replace(',', ''), errors='coerce')
            df['volume'] = pd.to_numeric(df['成交股數'].str.replace(',', ''), errors='coerce')
            df['symbol'] = symbol
            
            # Select required columns
            result = df[['date', 'open', 'high', 'low', 'close', 'volume', 'symbol']].copy()
            
            return result
            
        except Exception as e:
            print(f"Error getting TWSE data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_multiple_taiwan_stocks(self, symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """
        Get data for multiple Taiwan stocks
        
        Args:
            symbols: List of Taiwan stock symbols
            period: Data period
            
        Returns:
            Combined DataFrame with data for all symbols
        """
        all_data = []
        
        for symbol in symbols:
            print(f"Downloading Taiwan stock data for {symbol}...")
            data = self.get_taiwan_stock_data(symbol, period)
            if not data.empty:
                all_data.append(data)
            time.sleep(0.5)  # Rate limiting
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            return combined_data
        else:
            return pd.DataFrame()
    
    def get_popular_taiwan_stocks(self) -> List[str]:
        """
        Get list of popular Taiwan stock symbols
        
        Returns:
            List of popular Taiwan stock symbols
        """
        return [
            '2330',  # 台積電
            '2317',  # 鴻海
            '2454',  # 聯發科
            '6505',  # 台塑化
            '2308',  # 台達電
            '2881',  # 富邦金
            '2882',  # 國泰金
            '2303',  # 聯電
            '3711',  # 日月光投控
            '2412',  # 中華電
            '2891',  # 中信金
            '2886',  # 兆豐金
            '2382',  # 廣達
            '2474',  # 可成
            '2327',  # 國巨
            '2884',  # 玉山金
            '2885',  # 元大金
            '2880',  # 華南金
            '2883',  # 開發金
            '2887',  # 台新金
        ]
    
    def get_taiwan_index_data(self, index_symbol: str = "TWII", period: str = "1y") -> pd.DataFrame:
        """
        Get Taiwan stock index data
        
        Args:
            index_symbol: Index symbol (default: TWII for Taiwan Weighted Index)
            period: Data period
            
        Returns:
            DataFrame with index data
        """
        # Add .TW suffix for Taiwan index
        if not index_symbol.endswith('.TW'):
            index_symbol = f"{index_symbol}.TW"
        
        return self.get_taiwan_stock_data(index_symbol, period)
    
    def validate_taiwan_data(self, data: pd.DataFrame) -> bool:
        """
        Validate Taiwan stock data quality
        
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
        
        return True
    
    def get_data_summary(self, data: pd.DataFrame) -> Dict:
        """
        Get summary statistics for Taiwan stock data
        
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
