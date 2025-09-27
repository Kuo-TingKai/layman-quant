"""
Risk management system for quantitative trading
量化交易風險管理系統
"""

from typing import Dict, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class RiskManager:
    """Risk management system for trading strategies"""
    
    def __init__(self, config: Dict):
        """
        Initialize risk manager
        
        Args:
            config: Risk management configuration
        """
        self.config = config
        self.max_position_size = config.get('max_position_size', 0.1)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.05)
        self.take_profit_pct = config.get('take_profit_pct', 0.15)
        self.max_daily_loss = config.get('max_daily_loss', 0.02)
        self.max_drawdown = config.get('max_drawdown', 0.15)
        self.max_correlation = config.get('max_correlation', 0.7)
        
        # Risk tracking
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.peak_capital = 0.0
        self.current_drawdown = 0.0
        self.positions = {}
        self.trade_history = []
        
    def check_position_size(self, symbol: str, price: float, 
                          available_capital: float, signal: int) -> Tuple[bool, float]:
        """
        Check if position size is within risk limits
        
        Args:
            symbol: Stock symbol
            price: Current price
            available_capital: Available capital
            signal: Trading signal (1: buy, -1: sell, 0: hold)
            
        Returns:
            Tuple of (is_valid, recommended_position_size)
        """
        if signal == 0:
            return True, 0
        
        # Calculate maximum position value
        max_position_value = available_capital * self.max_position_size
        
        # Calculate position size
        position_size = max_position_value / price
        
        # Check if we already have a position in this symbol
        if symbol in self.positions:
            current_position = self.positions[symbol]['shares']
            if signal == 1:  # Buy signal
                # Check if adding to position exceeds limits
                total_value = (current_position + position_size) * price
                if total_value > available_capital * self.max_position_size * 2:  # Allow 2x for averaging down
                    return False, 0
            elif signal == -1:  # Sell signal
                # Can only sell what we have
                return True, min(position_size, current_position)
        else:
            if signal == -1:  # Can't sell what we don't have
                return False, 0
        
        return True, position_size
    
    def check_daily_loss_limit(self, current_capital: float, 
                              initial_capital: float) -> bool:
        """
        Check if daily loss limit is exceeded
        
        Args:
            current_capital: Current portfolio value
            initial_capital: Initial capital
            
        Returns:
            True if within daily loss limit
        """
        daily_loss = (initial_capital - current_capital) / initial_capital
        return daily_loss <= self.max_daily_loss
    
    def check_drawdown_limit(self, current_capital: float) -> bool:
        """
        Check if maximum drawdown limit is exceeded
        
        Args:
            current_capital: Current portfolio value
            
        Returns:
            True if within drawdown limit
        """
        # Update peak capital
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
        
        # Calculate current drawdown
        if self.peak_capital > 0:
            self.current_drawdown = (self.peak_capital - current_capital) / self.peak_capital
            return self.current_drawdown <= self.max_drawdown
        
        return True
    
    def check_correlation_risk(self, new_symbol: str, 
                              existing_positions: Dict) -> bool:
        """
        Check correlation risk for new position
        
        Args:
            new_symbol: New symbol to add
            existing_positions: Current positions
            
        Returns:
            True if correlation risk is acceptable
        """
        if not existing_positions:
            return True
        
        # Simple correlation check based on sector/industry
        # In a real implementation, you would calculate actual correlation
        # For now, we'll use a simple rule: max 3 positions in same sector
        sector_positions = {}
        for symbol, position in existing_positions.items():
            # Simplified sector classification
            sector = self._get_sector(symbol)
            sector_positions[sector] = sector_positions.get(sector, 0) + 1
        
        new_sector = self._get_sector(new_symbol)
        if sector_positions.get(new_sector, 0) >= 3:
            return False
        
        return True
    
    def _get_sector(self, symbol: str) -> str:
        """
        Get sector for symbol (simplified classification)
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Sector name
        """
        # Simplified sector classification
        # In real implementation, you would use actual sector data
        tech_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'INTC']
        finance_symbols = ['JPM', 'BAC', 'WFC', 'GS', 'MS']
        healthcare_symbols = ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK']
        
        if symbol in tech_symbols:
            return 'Technology'
        elif symbol in finance_symbols:
            return 'Financial'
        elif symbol in healthcare_symbols:
            return 'Healthcare'
        else:
            return 'Other'
    
    def calculate_position_risk(self, symbol: str, price: float, 
                               shares: int, portfolio_value: float) -> Dict:
        """
        Calculate risk metrics for a position
        
        Args:
            symbol: Stock symbol
            price: Current price
            shares: Number of shares
            portfolio_value: Total portfolio value
            
        Returns:
            Dictionary with risk metrics
        """
        position_value = shares * price
        position_weight = position_value / portfolio_value if portfolio_value > 0 else 0
        
        # Calculate stop loss and take profit levels
        stop_loss_price = price * (1 - self.stop_loss_pct)
        take_profit_price = price * (1 + self.take_profit_pct)
        
        # Calculate potential loss and gain
        potential_loss = position_value * self.stop_loss_pct
        potential_gain = position_value * self.take_profit_pct
        
        return {
            'symbol': symbol,
            'position_value': position_value,
            'position_weight': position_weight,
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price,
            'potential_loss': potential_loss,
            'potential_gain': potential_gain,
            'risk_reward_ratio': potential_gain / potential_loss if potential_loss > 0 else 0
        }
    
    def update_position(self, symbol: str, shares: int, price: float, 
                       action: str, timestamp: datetime):
        """
        Update position tracking
        
        Args:
            symbol: Stock symbol
            shares: Number of shares
            price: Transaction price
            action: 'BUY' or 'SELL'
            timestamp: Transaction timestamp
        """
        if action == 'BUY':
            if symbol in self.positions:
                # Average down/up
                current_shares = self.positions[symbol]['shares']
                current_price = self.positions[symbol]['price']
                total_shares = current_shares + shares
                total_value = (current_shares * current_price) + (shares * price)
                avg_price = total_value / total_shares
                
                self.positions[symbol] = {
                    'shares': total_shares,
                    'price': avg_price,
                    'timestamp': timestamp
                }
            else:
                self.positions[symbol] = {
                    'shares': shares,
                    'price': price,
                    'timestamp': timestamp
                }
        
        elif action == 'SELL':
            if symbol in self.positions:
                current_shares = self.positions[symbol]['shares']
                remaining_shares = current_shares - shares
                
                if remaining_shares <= 0:
                    del self.positions[symbol]
                else:
                    self.positions[symbol]['shares'] = remaining_shares
        
        # Record trade
        self.trade_history.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'action': action,
            'shares': shares,
            'price': price
        })
    
    def get_risk_summary(self, portfolio_value: float) -> Dict:
        """
        Get current risk summary
        
        Args:
            portfolio_value: Current portfolio value
            
        Returns:
            Dictionary with risk summary
        """
        total_position_value = sum(pos['shares'] * pos['price'] 
                                 for pos in self.positions.values())
        
        return {
            'total_positions': len(self.positions),
            'total_position_value': total_position_value,
            'position_weight': total_position_value / portfolio_value if portfolio_value > 0 else 0,
            'current_drawdown': self.current_drawdown,
            'max_drawdown_limit': self.max_drawdown,
            'daily_pnl': self.daily_pnl,
            'total_pnl': self.total_pnl,
            'risk_limits': {
                'max_position_size': self.max_position_size,
                'stop_loss_pct': self.stop_loss_pct,
                'take_profit_pct': self.take_profit_pct,
                'max_daily_loss': self.max_daily_loss
            }
        }
    
    def should_exit_position(self, symbol: str, current_price: float) -> bool:
        """
        Check if position should be exited based on risk rules
        
        Args:
            symbol: Stock symbol
            current_price: Current market price
            
        Returns:
            True if position should be exited
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        entry_price = position['price']
        
        # Check stop loss
        if current_price <= entry_price * (1 - self.stop_loss_pct):
            return True
        
        # Check take profit
        if current_price >= entry_price * (1 + self.take_profit_pct):
            return True
        
        return False
