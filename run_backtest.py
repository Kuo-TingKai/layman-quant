#!/usr/bin/env python3
"""
Backtest runner script
回測執行腳本
"""

import sys
import os
import argparse
from datetime import datetime
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import TradingSystem
from config import Config

def run_backtest(symbols, period="1y", strategy_config=None):
    """
    Run backtest with given parameters
    
    Args:
        symbols: List of stock symbols
        period: Data period for backtest
        strategy_config: Strategy configuration
    """
    print(f"開始回測 - 標的: {symbols}, 期間: {period}")
    print("=" * 50)
    
    # Initialize trading system
    trading_system = TradingSystem()
    
    # Run backtest
    results = trading_system.run_backtest(symbols, strategy_config)
    
    if not results:
        print("回測失敗：無法獲取數據或發生錯誤")
        return
    
    # Display results
    print("\n回測結果:")
    print("=" * 50)
    print(f"總報酬率: {results.get('total_return', 0):.2%}")
    print(f"年化報酬率: {results.get('annualized_return', 0):.2%}")
    print(f"波動率: {results.get('volatility', 0):.2%}")
    print(f"夏普比率: {results.get('sharpe_ratio', 0):.2f}")
    print(f"最大回撤: {results.get('max_drawdown', 0):.2%}")
    print(f"總交易次數: {results.get('total_trades', 0)}")
    print(f"勝率: {results.get('win_rate', 0):.2%}")
    print(f"最終投資組合價值: ${results.get('final_portfolio_value', 0):.2f}")
    
    # Display trade details
    trades = results.get('trades', pd.DataFrame())
    if not trades.empty:
        print(f"\n交易明細 (前10筆):")
        print("-" * 50)
        print(trades.head(10).to_string(index=False))
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"backtest_results_{timestamp}.json"
    
    # Convert results to JSON-serializable format
    json_results = {
        'total_return': float(results.get('total_return', 0)),
        'annualized_return': float(results.get('annualized_return', 0)),
        'volatility': float(results.get('volatility', 0)),
        'sharpe_ratio': float(results.get('sharpe_ratio', 0)),
        'max_drawdown': float(results.get('max_drawdown', 0)),
        'total_trades': int(results.get('total_trades', 0)),
        'win_rate': float(results.get('win_rate', 0)),
        'final_portfolio_value': float(results.get('final_portfolio_value', 0)),
        'symbols': symbols,
        'period': period,
        'timestamp': timestamp
    }
    
    import json
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果已保存至: {results_file}")
    
    # Generate plot
    try:
        from backtesting import BacktestEngine
        backtest_engine = BacktestEngine()
        plot_file = f"backtest_plot_{timestamp}.png"
        backtest_engine.plot_results(results, save_path=plot_file)
        print(f"圖表已保存至: {plot_file}")
    except Exception as e:
        print(f"無法生成圖表: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='量化交易系統回測工具')
    parser.add_argument('--symbols', nargs='+', default=['AAPL', 'MSFT', 'GOOGL'],
                       help='股票代碼列表 (預設: AAPL MSFT GOOGL)')
    parser.add_argument('--period', default='1y',
                       choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y'],
                       help='回測期間 (預設: 1y)')
    parser.add_argument('--rsi-period', type=int, default=14,
                       help='RSI 週期 (預設: 14)')
    parser.add_argument('--rsi-oversold', type=int, default=30,
                       help='RSI 超賣線 (預設: 30)')
    parser.add_argument('--rsi-overbought', type=int, default=70,
                       help='RSI 超買線 (預設: 70)')
    parser.add_argument('--ma-short', type=int, default=20,
                       help='短期移動平均線 (預設: 20)')
    parser.add_argument('--ma-long', type=int, default=50,
                       help='長期移動平均線 (預設: 50)')
    parser.add_argument('--max-position', type=float, default=0.1,
                       help='最大持倉比例 (預設: 0.1)')
    
    args = parser.parse_args()
    
    # Prepare strategy configuration
    strategy_config = {
        'rsi_period': args.rsi_period,
        'rsi_oversold': args.rsi_oversold,
        'rsi_overbought': args.rsi_overbought,
        'ma_short': args.ma_short,
        'ma_long': args.ma_long,
        'max_position_size': args.max_position,
        'stop_loss_pct': 0.05,
        'take_profit_pct': 0.15
    }
    
    # Run backtest
    run_backtest(args.symbols, args.period, strategy_config)

if __name__ == "__main__":
    main()
