#!/usr/bin/env python3
"""
Custom strategy example
自訂策略範例
"""

import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.base_strategy import BaseStrategy
from main import TradingSystem
import ta

class MACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy
    簡單移動平均交叉策略
    """
    
    def __init__(self, config):
        super().__init__("MA_Crossover_Strategy", config)
        self.fast_ma = config.get('fast_ma', 10)
        self.slow_ma = config.get('slow_ma', 30)
        self.max_position_size = config.get('max_position_size', 0.1)
    
    def generate_signals(self, data):
        """Generate trading signals based on MA crossover"""
        df = data.copy()
        
        # Calculate moving averages
        df['ma_fast'] = ta.trend.SMAIndicator(df['close'], window=self.fast_ma).sma_indicator()
        df['ma_slow'] = ta.trend.SMAIndicator(df['close'], window=self.slow_ma).sma_indicator()
        
        # Initialize signals
        df['signal'] = 0
        
        # Buy signal: fast MA crosses above slow MA
        df.loc[df['ma_fast'] > df['ma_slow'], 'signal'] = 1
        df.loc[df['ma_fast'] <= df['ma_slow'], 'signal'] = -1
        
        # Only signal on crossover
        df['signal'] = df['signal'].diff()
        df['signal'] = df['signal'].fillna(0)
        
        return df
    
    def calculate_position_size(self, signal, price, available_capital):
        """Calculate position size"""
        if signal == 0:
            return 0
        
        position_value = available_capital * self.max_position_size
        position_size = position_value / price
        return int(position_size)

def main():
    """Run backtest with custom strategy"""
    print("量化交易系統 - 自訂策略範例")
    print("=" * 40)
    
    # Initialize trading system
    trading_system = TradingSystem()
    
    # Define test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    # Define custom strategy parameters
    strategy_config = {
        'fast_ma': 10,
        'slow_ma': 30,
        'max_position_size': 0.15,  # 15% per position
        'stop_loss_pct': 0.03,      # 3% stop loss
        'take_profit_pct': 0.12     # 12% take profit
    }
    
    print(f"測試標的: {symbols}")
    print(f"策略: 移動平均交叉策略")
    print(f"策略參數: {strategy_config}")
    print("\n開始回測...")
    
    # Create custom strategy
    custom_strategy = MACrossoverStrategy(strategy_config)
    
    # Get market data
    data = trading_system.data_provider.get_multiple_stocks_data(symbols, period="1y")
    
    if data.empty:
        print("無法獲取數據")
        return
    
    # Run backtest with custom strategy
    from backtesting import BacktestEngine
    backtest_engine = BacktestEngine(initial_capital=10000, commission_rate=0.001)
    results = backtest_engine.run_backtest(data, custom_strategy, symbols)
    
    if results:
        print("\n回測結果:")
        print("-" * 40)
        print(f"總報酬率: {results.get('total_return', 0):.2%}")
        print(f"年化報酬率: {results.get('annualized_return', 0):.2%}")
        print(f"波動率: {results.get('volatility', 0):.2%}")
        print(f"夏普比率: {results.get('sharpe_ratio', 0):.2f}")
        print(f"最大回撤: {results.get('max_drawdown', 0):.2%}")
        print(f"總交易次數: {results.get('total_trades', 0)}")
        print(f"勝率: {results.get('win_rate', 0):.2%}")
        
        # Generate plot
        backtest_engine.plot_results(results, save_path='custom_strategy_results.png')
        print("\n圖表已保存至: custom_strategy_results.png")
    else:
        print("回測失敗")

if __name__ == "__main__":
    main()
