#!/usr/bin/env python3
"""
Taiwan stock backtest runner script
台股回測執行腳本
"""

import sys
import os
import argparse
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.taiwan_data_provider import TaiwanDataProvider
from strategies import RSIMAStrategy
from backtesting import BacktestEngine

def run_taiwan_backtest(symbols, period="1y", strategy_config=None):
    """
    Run Taiwan stock backtest
    
    Args:
        symbols: List of Taiwan stock symbols
        period: Data period for backtest
        strategy_config: Strategy configuration
    """
    print(f"開始台股回測 - 標的: {symbols}, 期間: {period}")
    print("=" * 60)
    
    # Initialize Taiwan data provider
    taiwan_provider = TaiwanDataProvider()
    
    # Get Taiwan stock data
    print("下載台股數據...")
    data = taiwan_provider.get_multiple_taiwan_stocks(symbols, period)
    
    if data.empty:
        print("❌ 無法獲取台股數據，請檢查股票代碼和網路連線")
        return
    
    print(f"✅ 成功獲取 {len(data)} 筆台股數據")
    
    # Show data summary
    summary = taiwan_provider.get_data_summary(data)
    print(f"\n📊 數據摘要:")
    print(f"  期間: {summary['date_range']['start'].strftime('%Y-%m-%d')} 至 {summary['date_range']['end'].strftime('%Y-%m-%d')}")
    print(f"  標的: {', '.join(summary['symbols'])}")
    print(f"  平均收盤價: ${summary['price_stats']['avg_close']:.2f}")
    
    # Create strategy
    strategy = RSIMAStrategy(strategy_config)
    print(f"\n✅ 策略創建成功")
    
    # Run backtest
    print(f"\n🔄 開始回測...")
    backtest_engine = BacktestEngine(initial_capital=100000, commission_rate=0.001425)  # 台股手續費率
    
    results = backtest_engine.run_backtest(data, strategy, symbols)
    
    if not results:
        print("❌ 回測失敗")
        return
    
    # Display results
    print(f"\n📊 台股回測結果:")
    print("=" * 60)
    print(f"💰 初始資金: ${100000:,.0f}")
    print(f"💰 最終價值: ${results.get('final_portfolio_value', 0):,.0f}")
    print(f"📈 總報酬率: {results.get('total_return', 0):.2%}")
    print(f"📊 年化報酬率: {results.get('annualized_return', 0):.2%}")
    print(f"📉 波動率: {results.get('volatility', 0):.2%}")
    print(f"⚖️ 夏普比率: {results.get('sharpe_ratio', 0):.2f}")
    print(f"📉 最大回撤: {results.get('max_drawdown', 0):.2%}")
    print(f"🔄 總交易次數: {results.get('total_trades', 0)}")
    print(f"🎯 勝率: {results.get('win_rate', 0):.2%}")
    
    # Display trade details
    trades = results.get('trades')
    if not trades.empty:
        print(f"\n📋 交易明細 (前10筆):")
        print("-" * 60)
        print(trades.head(10).to_string(index=False))
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"taiwan_backtest_results_{timestamp}.json"
    
    # Convert results to JSON-serializable format
    import json
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
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 結果已保存至: {results_file}")
    
    # Generate plot
    try:
        plot_file = f"taiwan_backtest_plot_{timestamp}.png"
        backtest_engine.plot_results(results, save_path=plot_file)
        print(f"📊 圖表已保存至: {plot_file}")
    except Exception as e:
        print(f"⚠️ 無法生成圖表: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='台股量化交易系統回測工具')
    parser.add_argument('--symbols', nargs='+', default=['2330', '2317', '2454'],
                       help='台股代碼列表 (預設: 2330 2317 2454)')
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
    
    # Run Taiwan stock backtest
    run_taiwan_backtest(args.symbols, args.period, strategy_config)

if __name__ == "__main__":
    main()
