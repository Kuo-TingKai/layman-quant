"""
RSI + Moving Average Strategy for retail traders
適合散戶的RSI移動平均策略
"""

import pandas as pd
from typing import Dict
from .base_strategy import BaseStrategy
import ta

class RSIMAStrategy(BaseStrategy):
    """
    RSI + Moving Average crossover strategy
    Combines RSI momentum indicator with moving average trend following
    """
    
    def __init__(self, config: Dict):
        """
        Initialize RSI + MA strategy
        
        Args:
            config: Strategy configuration parameters
        """
        super().__init__("RSI_MA_Strategy", config)
        
        # Strategy parameters
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.ma_short = config.get('ma_short', 20)
        self.ma_long = config.get('ma_long', 50)
        self.max_position_size = config.get('max_position_size', 0.1)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals using RSI and Moving Average
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with signals
        """
        df = data.copy()
        
        # Calculate RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=self.rsi_period).rsi()
        
        # Calculate moving averages
        df['ma_short'] = ta.trend.SMAIndicator(df['close'], window=self.ma_short).sma_indicator()
        df['ma_long'] = ta.trend.SMAIndicator(df['close'], window=self.ma_long).sma_indicator()
        
        # Initialize signals
        df['signal'] = 0
        
        # Buy signals: RSI oversold + MA short > MA long
        buy_condition = (
            (df['rsi'] < self.rsi_oversold) & 
            (df['ma_short'] > df['ma_long']) &
            (df['ma_short'].shift(1) <= df['ma_long'].shift(1))  # MA crossover
        )
        df.loc[buy_condition, 'signal'] = 1
        
        # Sell signals: RSI overbought + MA short < MA long
        sell_condition = (
            (df['rsi'] > self.rsi_overbought) & 
            (df['ma_short'] < df['ma_long']) &
            (df['ma_short'].shift(1) >= df['ma_long'].shift(1))  # MA crossover
        )
        df.loc[sell_condition, 'signal'] = -1
        
        return df
    
    def calculate_position_size(self, signal: int, price: float, 
                              available_capital: float) -> float:
        """
        Calculate position size based on signal and available capital
        
        Args:
            signal: Trading signal (1, -1, or 0)
            price: Current price
            available_capital: Available capital for trading
            
        Returns:
            Position size (number of shares)
        """
        if signal == 0:
            return 0
            
        # Calculate position size as percentage of available capital
        position_value = available_capital * self.max_position_size
        position_size = position_value / price
        
        # Round down to whole shares
        return int(position_size)
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        return f"""
        RSI + Moving Average Strategy:
        - RSI Period: {self.rsi_period}
        - RSI Oversold: {self.rsi_oversold}
        - RSI Overbought: {self.rsi_overbought}
        - Short MA: {self.ma_short}
        - Long MA: {self.ma_long}
        - Max Position Size: {self.max_position_size * 100}%
        
        Buy Signal: RSI < {self.rsi_oversold} AND Short MA crosses above Long MA
        Sell Signal: RSI > {self.rsi_overbought} AND Short MA crosses below Long MA
        """
