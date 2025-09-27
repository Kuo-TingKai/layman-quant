"""
Base strategy class for quantitative trading
量化交易策略基類
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str, config: Dict):
        """
        Initialize the strategy
        
        Args:
            name: Strategy name
            config: Configuration parameters
        """
        self.name = name
        self.config = config
        self.positions = {}  # Current positions
        self.trades = []     # Trade history
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on market data
        
        Args:
            data: Market data with OHLCV columns
            
        Returns:
            DataFrame with signals (1: buy, -1: sell, 0: hold)
        """
        pass
    
    @abstractmethod
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
        pass
    
    def should_exit_position(self, symbol: str, current_price: float, 
                           entry_price: float, entry_time: pd.Timestamp) -> bool:
        """
        Check if position should be exited based on stop loss/take profit
        
        Args:
            symbol: Stock symbol
            current_price: Current market price
            entry_price: Entry price of the position
            entry_time: Entry time of the position
            
        Returns:
            True if position should be exited
        """
        # Calculate return percentage
        return_pct = (current_price - entry_price) / entry_price
        
        # Check stop loss
        if return_pct <= -self.config.get('stop_loss_pct', 0.05):
            return True
            
        # Check take profit
        if return_pct >= self.config.get('take_profit_pct', 0.15):
            return True
            
        return False
    
    def get_strategy_info(self) -> Dict:
        """Get strategy information"""
        return {
            'name': self.name,
            'config': self.config,
            'positions': self.positions,
            'total_trades': len(self.trades)
        }
