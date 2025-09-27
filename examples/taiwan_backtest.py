#!/usr/bin/env python3
"""
Taiwan stock backtest example
台股回測範例
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.taiwan_data_provider import TaiwanDataProvider
from strategies import RSIMAStrategy
from backtesting import BacktestEngine

def main():
    """Run Taiwan stock backtest example"""
    print("台股量化交易系統回測範例")
    print("=" * 50)
    
    # Initialize Taiwan data provider
    taiwan_provider = TaiwanDataProvider()
    
    # Get popular Taiwan stocks
    popular_stocks = taiwan_provider.get_popular_taiwan_stocks()[:5]  # Top 5
    print(f"測試標的: {popular_stocks}")
    print("(台積電、鴻海、聯發科、台塑化、台達電)")
    
    # Get Taiwan stock data
    print("\n下載台股數據...")
    data = taiwan_provider.get_multiple_taiwan_stocks(popular_stocks, period="1y")
    
    if data.empty:
        print("❌ 無法獲取台股數據")
        return
    
    print(f"✅ 成功獲取 {len(data)} 筆台股數據")
    
    # Show data summary
    summary = taiwan_provider.get_data_summary(data)
    print(f"\n數據摘要:")
    print(f"  期間: {summary['date_range']['start'].strftime('%Y-%m-%d')} 至 {summary['date_range']['end'].strftime('%Y-%m-%d')}")
    print(f"  標的: {', '.join(summary['symbols'])}")
    print(f"  平均收盤價: ${summary['price_stats']['avg_close']:.2f}")
    
    # Create strategy
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
    
    strategy = RSIMAStrategy(strategy_config)
    print(f"\n✅ 策略創建成功")
    print(f"  RSI 週期: {strategy_config['rsi_period']}")
    print(f"  RSI 超賣/超買: {strategy_config['rsi_oversold']}/{strategy_config['rsi_overbought']}")
    print(f"  移動平均線: {strategy_config['ma_short']}/{strategy_config['ma_long']}")
    
    # Run backtest
    print(f"\n開始台股回測...")
    backtest_engine = BacktestEngine(initial_capital=100000, commission_rate=0.001425)  # 台股手續費率
    
    results = backtest_engine.run_backtest(data, strategy, popular_stocks)
    
    if results:
        print(f"\n📊 台股回測結果:")
        print("=" * 50)
        print(f"💰 初始資金: ${100000:,.0f}")
        print(f"💰 最終價值: ${results.get('final_portfolio_value', 0):,.0f}")
        print(f"📈 總報酬率: {results.get('total_return', 0):.2%}")
        print(f"📊 年化報酬率: {results.get('annualized_return', 0):.2%}")
        print(f"📉 波動率: {results.get('volatility', 0):.2%}")
        print(f"⚖️ 夏普比率: {results.get('sharpe_ratio', 0):.2f}")
        print(f"📉 最大回撤: {results.get('max_drawdown', 0):.2%}")
        print(f"🔄 總交易次數: {results.get('total_trades', 0)}")
        print(f"🎯 勝率: {results.get('win_rate', 0):.2%}")
        
        # Show trade details
        trades = results.get('trades')
        if not trades.empty:
            print(f"\n📋 交易明細 (前5筆):")
            print("-" * 50)
            print(trades.head().to_string(index=False))
            
            # Calculate trade statistics
            buy_trades = trades[trades['action'] == 'BUY']
            sell_trades = trades[trades['action'] == 'SELL']
            print(f"\n📊 交易統計:")
            print(f"  買入交易: {len(buy_trades)} 筆")
            print(f"  賣出交易: {len(sell_trades)} 筆")
            
            if 'pnl' in sell_trades.columns:
                profitable_trades = sell_trades[sell_trades['pnl'] > 0]
                avg_profit = sell_trades['pnl'].mean()
                print(f"  獲利交易: {len(profitable_trades)} 筆")
                print(f"  平均損益: ${avg_profit:.2f}")
        
        # Generate plot
        try:
            plot_file = 'taiwan_backtest_results.png'
            backtest_engine.plot_results(results, save_path=plot_file)
            print(f"\n📊 績效圖表已保存至: {plot_file}")
        except Exception as e:
            print(f"⚠️ 無法生成圖表: {str(e)}")
        
        # Performance evaluation
        print(f"\n🎯 績效評估:")
        total_return = results.get('total_return', 0)
        sharpe_ratio = results.get('sharpe_ratio', 0)
        max_drawdown = results.get('max_drawdown', 0)
        
        if total_return > 0.1:  # 10% return
            print("  ✅ 總報酬率表現良好")
        elif total_return > 0:
            print("  ⚠️ 總報酬率為正但偏低")
        else:
            print("  ❌ 總報酬率為負")
        
        if sharpe_ratio > 1.0:
            print("  ✅ 夏普比率表現良好")
        elif sharpe_ratio > 0.5:
            print("  ⚠️ 夏普比率中等")
        else:
            print("  ❌ 夏普比率偏低")
        
        if abs(max_drawdown) < 0.1:  # 10% drawdown
            print("  ✅ 回撤控制良好")
        elif abs(max_drawdown) < 0.2:  # 20% drawdown
            print("  ⚠️ 回撤控制中等")
        else:
            print("  ❌ 回撤過大")
        
        print(f"\n🎉 台股回測完成！")
        print(f"💡 建議:")
        print(f"  1. 嘗試不同的策略參數")
        print(f"  2. 測試更多台股標的")
        print(f"  3. 調整風險控制參數")
        print(f"  4. 考慮加入台股特有的技術指標")
        
    else:
        print("❌ 台股回測失敗")

if __name__ == "__main__":
    main()
