#!/usr/bin/env python3
"""
Complete backtest demo with mock data
使用模擬數據的完整回測演示
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies import RSIMAStrategy
from backtesting import BacktestEngine

def generate_realistic_data(symbols, days=252):
    """
    Generate realistic mock stock data
    
    Args:
        symbols: List of stock symbols
        days: Number of days of data to generate
        
    Returns:
        DataFrame with realistic OHLCV data
    """
    all_data = []
    
    # Base prices for different symbols
    base_prices = {
        'AAPL': 150.0,
        'MSFT': 300.0,
        'GOOGL': 2500.0,
        'TSLA': 200.0,
        'NVDA': 400.0
    }
    
    for symbol in symbols:
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
        
        # Starting price
        price = base_prices.get(symbol, 100.0)
        
        # Generate price series with trend and volatility
        trend = np.random.uniform(-0.0005, 0.001)  # Daily trend
        volatility = np.random.uniform(0.015, 0.025)  # Daily volatility
        
        prices = [price]
        for i in range(days - 1):
            # Add trend and random walk
            change = np.random.normal(trend, volatility)
            price = price * (1 + change)
            prices.append(max(price, 1))  # Ensure positive prices
        
        # Generate OHLCV data
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             periods=days, freq='D')
        
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Generate realistic OHLC
            daily_vol = np.random.uniform(0.01, 0.03)
            
            high = close * (1 + np.random.uniform(0, daily_vol))
            low = close * (1 - np.random.uniform(0, daily_vol))
            
            # Open price between low and high
            open_price = low + np.random.uniform(0, high - low)
            
            # Ensure OHLC relationships are correct
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            # Generate volume (higher volume on larger price changes)
            price_change = abs(close - prices[i-1]) / prices[i-1] if i > 0 else 0
            base_volume = np.random.randint(1000000, 5000000)
            volume = int(base_volume * (1 + price_change * 2))
            
            data.append({
                'date': date,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume,
                'symbol': symbol
            })
        
        all_data.extend(data)
    
    return pd.DataFrame(all_data)

def run_complete_backtest():
    """Run a complete backtest demonstration"""
    print("🚀 量化交易系統 - 完整回測演示")
    print("=" * 60)
    
    # Generate realistic data
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    print(f"📊 生成模擬數據 - 標的: {symbols}")
    print(f"📅 數據期間: 252 個交易日 (約1年)")
    
    data = generate_realistic_data(symbols, days=252)
    print(f"✅ 生成了 {len(data)} 筆數據記錄")
    
    # Show data summary
    print(f"\n📈 數據摘要:")
    for symbol in symbols:
        symbol_data = data[data['symbol'] == symbol]
        if not symbol_data.empty:
            start_price = symbol_data.iloc[0]['close']
            end_price = symbol_data.iloc[-1]['close']
            change_pct = (end_price - start_price) / start_price * 100
            print(f"  {symbol}: ${start_price:.2f} → ${end_price:.2f} ({change_pct:+.1f}%)")
    
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
    
    print(f"\n🎯 策略配置:")
    print(f"  RSI 週期: {strategy_config['rsi_period']}")
    print(f"  RSI 超賣/超買: {strategy_config['rsi_oversold']}/{strategy_config['rsi_overbought']}")
    print(f"  移動平均線: {strategy_config['ma_short']}/{strategy_config['ma_long']}")
    print(f"  最大持倉: {strategy_config['max_position_size']*100}%")
    print(f"  停損/停利: {strategy_config['stop_loss_pct']*100}%/{strategy_config['take_profit_pct']*100}%")
    
    strategy = RSIMAStrategy(strategy_config)
    print("✅ 策略創建成功")
    
    # Run backtest
    print(f"\n🔄 開始回測...")
    backtest_engine = BacktestEngine(initial_capital=10000, commission_rate=0.001)
    
    results = backtest_engine.run_backtest(data, strategy, symbols)
    
    if results:
        print("✅ 回測完成")
        
        # Display results
        print(f"\n📊 回測結果:")
        print("=" * 60)
        print(f"💰 初始資金: ${10000:,.2f}")
        print(f"💰 最終價值: ${results.get('final_portfolio_value', 0):,.2f}")
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
            print(f"\n📋 交易明細 (前10筆):")
            print("-" * 60)
            print(trades.head(10).to_string(index=False))
            
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
        
        # Generate performance plot
        try:
            plot_file = 'backtest_demo_results.png'
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
        
        return True
    else:
        print("❌ 回測失敗")
        return False

def main():
    """Main function"""
    try:
        success = run_complete_backtest()
        
        if success:
            print(f"\n🎉 演示完成！系統功能正常運作。")
            print(f"\n💡 使用建議:")
            print(f"  1. 調整策略參數以優化績效")
            print(f"  2. 測試不同的股票組合")
            print(f"  3. 配置真實的市場數據源")
            print(f"  4. 設定風險管理參數")
            print(f"  5. 謹慎評估後進行實盤交易")
        else:
            print(f"\n❌ 演示失敗，請檢查系統配置")
        
        return success
        
    except Exception as e:
        print(f"\n❌ 演示過程中發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
