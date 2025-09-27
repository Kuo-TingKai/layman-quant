"""
Backtesting engine for quantitative trading strategies
量化交易策略回測引擎
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class BacktestEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, initial_capital: float = 10000, commission_rate: float = 0.001):
        """
        Initialize backtesting engine
        
        Args:
            initial_capital: Starting capital
            commission_rate: Commission rate per trade
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.reset()
    
    def reset(self):
        """Reset backtesting state"""
        self.capital = self.initial_capital
        self.positions = {}  # {symbol: {'shares': int, 'entry_price': float, 'entry_time': datetime}}
        self.trades = []
        self.portfolio_values = []
        self.dates = []
        self.returns = []
        
    def run_backtest(self, data: pd.DataFrame, strategy, symbols: List[str]) -> Dict:
        """
        Run backtest on given data and strategy
        
        Args:
            data: Market data with OHLCV columns
            strategy: Trading strategy instance
            symbols: List of symbols to trade
            
        Returns:
            Backtest results dictionary
        """
        self.reset()
        
        # Generate signals for each symbol
        signals_data = {}
        for symbol in symbols:
            symbol_data = data[data['symbol'] == symbol].copy()
            if len(symbol_data) > 0:
                signals_data[symbol] = strategy.generate_signals(symbol_data)
        
        # Process each trading day
        all_dates = sorted(set(data['date']))
        
        for date in all_dates:
            daily_data = data[data['date'] == date]
            
            for _, row in daily_data.iterrows():
                symbol = row['symbol']
                price = row['close']
                
                if symbol in signals_data:
                    symbol_signals = signals_data[symbol]
                    date_signals = symbol_signals[symbol_signals.index == date]
                    
                    if not date_signals.empty:
                        signal = date_signals['signal'].iloc[0]
                        self._process_signal(symbol, price, signal, date, strategy)
            
            # Update portfolio value
            self._update_portfolio_value(date)
        
        # Calculate performance metrics
        results = self._calculate_performance_metrics()
        return results
    
    def _process_signal(self, symbol: str, price: float, signal: int, 
                       date: pd.Timestamp, strategy):
        """Process trading signal"""
        current_position = self.positions.get(symbol, {'shares': 0})
        
        if signal == 1 and current_position['shares'] == 0:  # Buy signal
            position_size = strategy.calculate_position_size(signal, price, self.capital)
            if position_size > 0:
                cost = position_size * price * (1 + self.commission_rate)
                if cost <= self.capital:
                    self.positions[symbol] = {
                        'shares': position_size,
                        'entry_price': price,
                        'entry_time': date
                    }
                    self.capital -= cost
                    self.trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'BUY',
                        'shares': position_size,
                        'price': price,
                        'value': cost
                    })
        
        elif signal == -1 and current_position['shares'] > 0:  # Sell signal
            self._close_position(symbol, price, date)
    
    def _close_position(self, symbol: str, price: float, date: pd.Timestamp):
        """Close position for given symbol"""
        if symbol in self.positions:
            position = self.positions[symbol]
            proceeds = position['shares'] * price * (1 - self.commission_rate)
            self.capital += proceeds
            
            # Calculate P&L
            cost = position['shares'] * position['entry_price']
            pnl = proceeds - cost
            
            self.trades.append({
                'date': date,
                'symbol': symbol,
                'action': 'SELL',
                'shares': position['shares'],
                'price': price,
                'value': proceeds,
                'pnl': pnl
            })
            
            del self.positions[symbol]
    
    def _update_portfolio_value(self, date: pd.Timestamp):
        """Update portfolio value for given date"""
        portfolio_value = self.capital
        
        # Add value of current positions
        for symbol, position in self.positions.items():
            # For simplicity, assume current price equals entry price
            # In real implementation, you'd get current market price
            position_value = position['shares'] * position['entry_price']
            portfolio_value += position_value
        
        self.portfolio_values.append(portfolio_value)
        self.dates.append(date)
        
        # Calculate daily return
        if len(self.portfolio_values) > 1:
            daily_return = (portfolio_value - self.portfolio_values[-2]) / self.portfolio_values[-2]
            self.returns.append(daily_return)
        else:
            self.returns.append(0)
    
    def _calculate_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.portfolio_values:
            return {}
        
        portfolio_series = pd.Series(self.portfolio_values, index=self.dates)
        
        # Ensure returns and dates have matching lengths
        if len(self.returns) > 0:
            # Truncate returns to match available dates
            max_returns = len(self.dates) - 1
            returns_to_use = self.returns[:max_returns]
            returns_series = pd.Series(returns_to_use, index=self.dates[1:len(returns_to_use)+1])
        else:
            returns_series = pd.Series([], dtype=float)
        
        # Basic metrics
        total_return = (portfolio_series.iloc[-1] - self.initial_capital) / self.initial_capital
        annualized_return = (1 + total_return) ** (252 / len(portfolio_series)) - 1
        
        # Risk metrics
        volatility = returns_series.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Drawdown
        peak = portfolio_series.expanding().max()
        drawdown = (portfolio_series - peak) / peak
        max_drawdown = drawdown.min()
        
        # Trade statistics
        trade_df = pd.DataFrame(self.trades)
        total_trades = len(trade_df)
        if 'pnl' in trade_df.columns:
            winning_trades = len(trade_df[trade_df['pnl'] > 0])
        else:
            winning_trades = 0
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'final_portfolio_value': portfolio_series.iloc[-1],
            'portfolio_series': portfolio_series,
            'returns_series': returns_series,
            'trades': trade_df
        }
    
    def plot_results(self, results: Dict, save_path: Optional[str] = None):
        """Plot backtest results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Portfolio value over time
        portfolio_series = results['portfolio_series']
        axes[0, 0].plot(portfolio_series.index, portfolio_series.values)
        axes[0, 0].set_title('Portfolio Value Over Time')
        axes[0, 0].set_ylabel('Portfolio Value ($)')
        axes[0, 0].grid(True)
        
        # Drawdown
        peak = portfolio_series.expanding().max()
        drawdown = (portfolio_series - peak) / peak
        axes[0, 1].fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
        axes[0, 1].set_title('Drawdown')
        axes[0, 1].set_ylabel('Drawdown (%)')
        axes[0, 1].grid(True)
        
        # Daily returns distribution
        returns_series = results['returns_series']
        axes[1, 0].hist(returns_series.values, bins=50, alpha=0.7)
        axes[1, 0].set_title('Daily Returns Distribution')
        axes[1, 0].set_xlabel('Daily Return')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True)
        
        # Performance metrics table
        metrics_text = f"""
        Total Return: {results['total_return']:.2%}
        Annualized Return: {results['annualized_return']:.2%}
        Volatility: {results['volatility']:.2%}
        Sharpe Ratio: {results['sharpe_ratio']:.2f}
        Max Drawdown: {results['max_drawdown']:.2%}
        Total Trades: {results['total_trades']}
        Win Rate: {results['win_rate']:.2%}
        """
        axes[1, 1].text(0.1, 0.5, metrics_text, transform=axes[1, 1].transAxes, 
                        fontsize=10, verticalalignment='center')
        axes[1, 1].set_title('Performance Metrics')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
