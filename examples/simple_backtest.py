#!/usr/bin/env python3
"""
Simple backtest example
簡單回測範例
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import TradingSystem

def main():
    """Run a simple backtest example"""
    print("量化交易系統 - 簡單回測範例")
    print("=" * 40)
    
    # Initialize trading system
    trading_system = TradingSystem()
    
    # Define test symbols (適合散戶的標的)
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    # Define strategy parameters
    strategy_config = {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'ma_short': 20,
        'ma_long': 50,
        'max_position_size': 0.1,  # 10% per position
        'stop_loss_pct': 0.05,     # 5% stop loss
        'take_profit_pct': 0.15    # 15% take profit
    }
    
    print(f"測試標的: {symbols}")
    print(f"策略參數: {strategy_config}")
    print("\n開始回測...")
    
    # Run backtest
    results = trading_system.run_backtest(symbols, strategy_config)
    
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
        print(f"最終投資組合價值: ${results.get('final_portfolio_value', 0):.2f}")
        
        # Show some trade details
        trades = results.get('trades')
        if not trades.empty:
            print(f"\n交易明細 (前5筆):")
            print("-" * 40)
            print(trades.head().to_string(index=False))
    else:
        print("回測失敗，請檢查數據和設定")

if __name__ == "__main__":
    main()
