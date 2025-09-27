"""
Main trading system application
量化交易系統主程式
"""

import sys
import os
from datetime import datetime
import logging
from typing import Dict, List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data import DataProvider
from strategies import RSIMAStrategy
from backtesting import BacktestEngine
from risk import RiskManager
from notifications import NotificationService

class TradingSystem:
    """Main trading system class"""
    
    def __init__(self, config_file: str = None):
        """
        Initialize trading system
        
        Args:
            config_file: Path to configuration file
        """
        self.config = Config()
        self.setup_logging()
        
        # Initialize components
        self.data_provider = DataProvider()
        self.risk_manager = RiskManager(self.config.__dict__)
        self.notification_service = NotificationService(self.config.__dict__)
        
        # Trading state
        self.portfolio_value = self.config.INITIAL_CAPITAL
        self.positions = {}
        self.trade_history = []
        
        self.logger.info("Trading system initialized successfully")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_backtest(self, symbols: List[str], strategy_config: Dict = None) -> Dict:
        """
        Run backtest on given symbols
        
        Args:
            symbols: List of stock symbols to test
            strategy_config: Strategy configuration parameters
            
        Returns:
            Backtest results
        """
        self.logger.info(f"Starting backtest for symbols: {symbols}")
        
        # Get market data
        data = self.data_provider.get_multiple_stocks_data(symbols, period="1y")
        
        if data.empty:
            self.logger.error("No data available for backtest")
            return {}
        
        # Initialize strategy
        strategy_config = strategy_config or {
            'rsi_period': self.config.RSI_PERIOD,
            'rsi_oversold': self.config.RSI_OVERSOLD,
            'rsi_overbought': self.config.RSI_OVERBOUGHT,
            'ma_short': self.config.MA_SHORT,
            'ma_long': self.config.MA_LONG,
            'max_position_size': self.config.MAX_POSITION_SIZE,
            'stop_loss_pct': self.config.STOP_LOSS_PCT,
            'take_profit_pct': self.config.TAKE_PROFIT_PCT
        }
        
        strategy = RSIMAStrategy(strategy_config)
        
        # Run backtest
        backtest_engine = BacktestEngine(
            initial_capital=self.config.INITIAL_CAPITAL,
            commission_rate=self.config.COMMISSION_RATE
        )
        
        results = backtest_engine.run_backtest(data, strategy, symbols)
        
        # Log results
        self.logger.info(f"Backtest completed. Total return: {results.get('total_return', 0):.2%}")
        
        return results
    
    def run_live_trading(self, symbols: List[str], strategy_config: Dict = None):
        """
        Run live trading (simulation mode)
        
        Args:
            symbols: List of stock symbols to trade
            strategy_config: Strategy configuration parameters
        """
        self.logger.info(f"Starting live trading simulation for symbols: {symbols}")
        
        # Initialize strategy
        strategy_config = strategy_config or {
            'rsi_period': self.config.RSI_PERIOD,
            'rsi_oversold': self.config.RSI_OVERSOLD,
            'rsi_overbought': self.config.RSI_OVERBOUGHT,
            'ma_short': self.config.MA_SHORT,
            'ma_long': self.config.MA_LONG,
            'max_position_size': self.config.MAX_POSITION_SIZE,
            'stop_loss_pct': self.config.STOP_LOSS_PCT,
            'take_profit_pct': self.config.TAKE_PROFIT_PCT
        }
        
        strategy = RSIMAStrategy(strategy_config)
        
        # Main trading loop
        while True:
            try:
                # Get current market data
                data = self.data_provider.get_multiple_stocks_data(symbols, period="5d")
                
                if data.empty:
                    self.logger.warning("No data available, skipping this cycle")
                    continue
                
                # Process each symbol
                for symbol in symbols:
                    symbol_data = data[data['symbol'] == symbol]
                    if symbol_data.empty:
                        continue
                    
                    # Generate signals
                    signals = strategy.generate_signals(symbol_data)
                    latest_signal = signals['signal'].iloc[-1] if not signals.empty else 0
                    current_price = symbol_data['close'].iloc[-1]
                    
                    # Process trading signal
                    if latest_signal != 0:
                        self._process_trading_signal(symbol, latest_signal, current_price, strategy)
                
                # Check risk management
                self._check_risk_limits()
                
                # Update portfolio value
                self._update_portfolio_value()
                
                # Send notifications if needed
                self._send_notifications()
                
                # Wait before next cycle (in real implementation, this would be scheduled)
                import time
                time.sleep(60)  # Wait 1 minute
                
            except KeyboardInterrupt:
                self.logger.info("Trading stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in trading loop: {str(e)}")
                self.notification_service.send_error_alert({
                    'error_type': 'Trading Loop Error',
                    'error_message': str(e),
                    'severity': 'high',
                    'timestamp': datetime.now()
                })
                continue
    
    def _process_trading_signal(self, symbol: str, signal: int, price: float, strategy):
        """Process trading signal"""
        # Check risk limits
        is_valid, position_size = self.risk_manager.check_position_size(
            symbol, price, self.portfolio_value, signal
        )
        
        if not is_valid:
            self.logger.warning(f"Signal for {symbol} rejected by risk manager")
            return
        
        # Execute trade
        if signal == 1 and position_size > 0:  # Buy signal
            self._execute_buy(symbol, position_size, price)
        elif signal == -1:  # Sell signal
            self._execute_sell(symbol, position_size, price)
    
    def _execute_buy(self, symbol: str, shares: int, price: float):
        """Execute buy order"""
        cost = shares * price * (1 + self.config.COMMISSION_RATE)
        
        if cost <= self.portfolio_value:
            self.positions[symbol] = {
                'shares': shares,
                'entry_price': price,
                'entry_time': datetime.now()
            }
            self.portfolio_value -= cost
            
            # Record trade
            trade = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': 'BUY',
                'shares': shares,
                'price': price,
                'value': cost
            }
            self.trade_history.append(trade)
            
            # Update risk manager
            self.risk_manager.update_position(symbol, shares, price, 'BUY', datetime.now())
            
            # Send notification
            self.notification_service.send_trade_alert(trade)
            
            self.logger.info(f"Bought {shares} shares of {symbol} at ${price:.2f}")
    
    def _execute_sell(self, symbol: str, shares: int, price: float):
        """Execute sell order"""
        if symbol in self.positions:
            position = self.positions[symbol]
            actual_shares = min(shares, position['shares'])
            
            proceeds = actual_shares * price * (1 - self.config.COMMISSION_RATE)
            self.portfolio_value += proceeds
            
            # Calculate P&L
            cost = actual_shares * position['entry_price']
            pnl = proceeds - cost
            
            # Update position
            if actual_shares == position['shares']:
                del self.positions[symbol]
            else:
                self.positions[symbol]['shares'] -= actual_shares
            
            # Record trade
            trade = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': 'SELL',
                'shares': actual_shares,
                'price': price,
                'value': proceeds,
                'pnl': pnl
            }
            self.trade_history.append(trade)
            
            # Update risk manager
            self.risk_manager.update_position(symbol, actual_shares, price, 'SELL', datetime.now())
            
            # Send notification
            self.notification_service.send_trade_alert(trade)
            
            self.logger.info(f"Sold {actual_shares} shares of {symbol} at ${price:.2f}, P&L: ${pnl:.2f}")
    
    def _check_risk_limits(self):
        """Check risk management limits"""
        # Check daily loss limit
        if not self.risk_manager.check_daily_loss_limit(self.portfolio_value, self.config.INITIAL_CAPITAL):
            self.logger.warning("Daily loss limit exceeded")
            self._close_all_positions()
        
        # Check drawdown limit
        if not self.risk_manager.check_drawdown_limit(self.portfolio_value):
            self.logger.warning("Maximum drawdown limit exceeded")
            self._close_all_positions()
    
    def _close_all_positions(self):
        """Close all open positions"""
        for symbol in list(self.positions.keys()):
            # Get current price (simplified - in real implementation, get from market)
            current_price = self.positions[symbol]['entry_price']  # Simplified
            self._execute_sell(symbol, self.positions[symbol]['shares'], current_price)
    
    def _update_portfolio_value(self):
        """Update portfolio value"""
        # In real implementation, this would get current market prices
        # For simulation, we'll use entry prices
        total_position_value = sum(
            pos['shares'] * pos['entry_price'] 
            for pos in self.positions.values()
        )
        self.portfolio_value = self.config.INITIAL_CAPITAL - sum(
            trade['value'] for trade in self.trade_history 
            if trade['action'] == 'BUY'
        ) + sum(
            trade['value'] for trade in self.trade_history 
            if trade['action'] == 'SELL'
        )
    
    def _send_notifications(self):
        """Send portfolio notifications"""
        # Calculate portfolio metrics
        total_pnl = sum(trade.get('pnl', 0) for trade in self.trade_history)
        pnl_pct = total_pnl / self.config.INITIAL_CAPITAL if self.config.INITIAL_CAPITAL > 0 else 0
        
        # Determine alert level
        alert_level = 'normal'
        if pnl_pct < -0.1:  # 10% loss
            alert_level = 'critical'
        elif pnl_pct < -0.05:  # 5% loss
            alert_level = 'warning'
        
        # Prepare portfolio info
        portfolio_info = {
            'total_value': self.portfolio_value,
            'total_pnl': total_pnl,
            'pnl_pct': pnl_pct,
            'positions': [
                {
                    'symbol': symbol,
                    'shares': pos['shares'],
                    'price': pos['entry_price'],
                    'pnl': 0  # Simplified
                }
                for symbol, pos in self.positions.items()
            ],
            'alert_level': alert_level
        }
        
        # Send notification if needed
        if alert_level != 'normal':
            self.notification_service.send_portfolio_alert(portfolio_info)
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        total_pnl = sum(trade.get('pnl', 0) for trade in self.trade_history)
        pnl_pct = total_pnl / self.config.INITIAL_CAPITAL if self.config.INITIAL_CAPITAL > 0 else 0
        
        return {
            'portfolio_value': self.portfolio_value,
            'total_pnl': total_pnl,
            'pnl_pct': pnl_pct,
            'positions': self.positions,
            'total_trades': len(self.trade_history),
            'risk_summary': self.risk_manager.get_risk_summary(self.portfolio_value)
        }

def main():
    """Main function"""
    print("量化交易系統啟動中...")
    
    # Initialize trading system
    trading_system = TradingSystem()
    
    # Test symbols (適合散戶的標的)
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    # Run backtest
    print("執行回測...")
    results = trading_system.run_backtest(test_symbols)
    
    if results:
        print(f"回測結果:")
        print(f"總報酬率: {results.get('total_return', 0):.2%}")
        print(f"年化報酬率: {results.get('annualized_return', 0):.2%}")
        print(f"夏普比率: {results.get('sharpe_ratio', 0):.2f}")
        print(f"最大回撤: {results.get('max_drawdown', 0):.2%}")
        print(f"總交易次數: {results.get('total_trades', 0)}")
        print(f"勝率: {results.get('win_rate', 0):.2%}")
        
        # Plot results
        from backtesting import BacktestEngine
        backtest_engine = BacktestEngine()
        backtest_engine.plot_results(results, save_path='backtest_results.png')
    
    # Ask user if they want to run live trading
    user_input = input("\n是否要開始即時交易模擬？(y/n): ")
    if user_input.lower() == 'y':
        print("開始即時交易模擬...")
        trading_system.run_live_trading(test_symbols)

if __name__ == "__main__":
    main()
