#!/usr/bin/env python3
"""
Simple demo for the quantitative trading system
量化交易系統簡單演示
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies import RSIMAStrategy
from risk import RiskManager
from notifications import NotificationService

def generate_simple_data(symbol, days=100):
    """Generate simple mock data for one symbol"""
    np.random.seed(42)  # Fixed seed for reproducible results
    
    # Generate price series
    price = 100
    prices = [price]
    
    for i in range(days - 1):
        change = np.random.normal(0, 0.02)  # 2% daily volatility
        price = price * (1 + change)
        prices.append(max(price, 1))
    
    # Generate OHLCV data
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                         periods=days, freq='D')
    
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        high = close * (1 + abs(np.random.normal(0, 0.01)))
        low = close * (1 - abs(np.random.normal(0, 0.01)))
        open_price = low + np.random.uniform(0, high - low)
        volume = np.random.randint(1000000, 5000000)
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'symbol': symbol
        })
    
    return pd.DataFrame(data)

def demo_strategy():
    """Demonstrate strategy functionality"""
    print("📊 交易策略演示")
    print("-" * 40)
    
    # Generate data
    data = generate_simple_data('AAPL', days=100)
    print(f"✓ 生成了 {len(data)} 天的模擬數據")
    
    # Create strategy
    config = {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'ma_short': 20,
        'ma_long': 50,
        'max_position_size': 0.1
    }
    
    strategy = RSIMAStrategy(config)
    print("✓ RSI + 移動平均策略創建成功")
    
    # Generate signals
    signals = strategy.generate_signals(data)
    signal_count = (signals['signal'] != 0).sum()
    print(f"✓ 生成了 {signal_count} 個交易信號")
    
    # Show signal details
    buy_signals = signals[signals['signal'] == 1]
    sell_signals = signals[signals['signal'] == -1]
    
    print(f"  - 買入信號: {len(buy_signals)} 個")
    print(f"  - 賣出信號: {len(sell_signals)} 個")
    
    if len(buy_signals) > 0:
        print(f"  - 最新買入信號: {buy_signals.iloc[-1]['date'].strftime('%Y-%m-%d')}")
    if len(sell_signals) > 0:
        print(f"  - 最新賣出信號: {sell_signals.iloc[-1]['date'].strftime('%Y-%m-%d')}")
    
    return True

def demo_risk_management():
    """Demonstrate risk management"""
    print("\n🛡️ 風險管理演示")
    print("-" * 40)
    
    config = {
        'max_position_size': 0.1,  # 10% per position
        'stop_loss_pct': 0.05,     # 5% stop loss
        'take_profit_pct': 0.15,   # 15% take profit
        'max_daily_loss': 0.02,    # 2% daily loss limit
        'max_drawdown': 0.15       # 15% max drawdown
    }
    
    risk_manager = RiskManager(config)
    print("✓ 風險管理器創建成功")
    
    # Test scenarios
    scenarios = [
        ("正常交易", 'AAPL', 150.0, 10000, 1),
        ("高價股票", 'GOOGL', 2500.0, 10000, 1),
        ("低價股票", 'PENNY', 0.5, 10000, 1),
        ("賣出信號", 'AAPL', 160.0, 10000, -1)
    ]
    
    for name, symbol, price, capital, signal in scenarios:
        is_valid, size = risk_manager.check_position_size(symbol, price, capital, signal)
        status = "✓ 通過" if is_valid else "✗ 拒絕"
        print(f"  {name}: {status} - 建議股數: {size}")
    
    # Test risk limits
    print("\n風險限制檢查:")
    print(f"  - 最大持倉比例: {config['max_position_size']*100}%")
    print(f"  - 停損比例: {config['stop_loss_pct']*100}%")
    print(f"  - 停利比例: {config['take_profit_pct']*100}%")
    print(f"  - 每日最大虧損: {config['max_daily_loss']*100}%")
    print(f"  - 最大回撤: {config['max_drawdown']*100}%")
    
    return True

def demo_notifications():
    """Demonstrate notification system"""
    print("\n📧 通知系統演示")
    print("-" * 40)
    
    config = {
        'email_enabled': False,  # Disabled for demo
        'sms_enabled': False,    # Disabled for demo
    }
    
    notification_service = NotificationService(config)
    print("✓ 通知服務創建成功")
    
    # Simulate trade notifications
    trades = [
        {
            'symbol': 'AAPL',
            'action': 'BUY',
            'shares': 10,
            'price': 150.0,
            'value': 1500.0,
            'timestamp': datetime.now()
        },
        {
            'symbol': 'MSFT',
            'action': 'SELL',
            'shares': 5,
            'price': 200.0,
            'value': 1000.0,
            'pnl': 100.0,
            'timestamp': datetime.now()
        }
    ]
    
    print("模擬交易通知:")
    for trade in trades:
        print(f"  📈 {trade['symbol']} {trade['action']} {trade['shares']}股 @ ${trade['price']:.2f}")
        if 'pnl' in trade:
            print(f"     損益: ${trade['pnl']:.2f}")
    
    # Simulate portfolio alert
    portfolio_info = {
        'total_value': 10500.0,
        'total_pnl': 500.0,
        'pnl_pct': 0.05,
        'positions': 2,
        'alert_level': 'normal'
    }
    
    print(f"\n投資組合狀態:")
    print(f"  💰 總價值: ${portfolio_info['total_value']:.2f}")
    print(f"  📊 總損益: ${portfolio_info['total_pnl']:.2f} ({portfolio_info['pnl_pct']:.1%})")
    print(f"  📈 持倉數量: {portfolio_info['positions']}")
    print(f"  ⚠️ 警報等級: {portfolio_info['alert_level']}")
    
    return True

def demo_system_overview():
    """Show system overview"""
    print("🎯 量化交易系統概覽")
    print("=" * 50)
    print("專為有限預算散戶設計的量化交易系統")
    print()
    print("核心功能:")
    print("  📊 交易策略 - RSI + 移動平均策略")
    print("  🔄 回測引擎 - 完整的績效分析")
    print("  🛡️ 風險管理 - 多層風險控制")
    print("  📧 通知系統 - 郵件和簡訊提醒")
    print("  📈 數據處理 - 自動獲取市場數據")
    print()
    print("適合散戶的特色:")
    print("  💰 初始資金: $10,000")
    print("  📉 最大持倉: 10% per position")
    print("  🛑 停損停利: 5% / 15%")
    print("  ⚠️ 風險控制: 每日最大虧損 2%")
    print()

def main():
    """Main demo function"""
    demo_system_overview()
    
    demos = [
        ("交易策略", demo_strategy),
        ("風險管理", demo_risk_management),
        ("通知系統", demo_notifications)
    ]
    
    success_count = 0
    for name, demo_func in demos:
        try:
            if demo_func():
                success_count += 1
        except Exception as e:
            print(f"✗ {name} 演示出錯: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"演示結果: {success_count}/{len(demos)} 成功")
    
    if success_count == len(demos):
        print("🎉 系統演示完成！所有核心功能正常運作。")
        print("\n下一步操作:")
        print("1. 配置真實的市場數據源")
        print("2. 設定郵件/簡訊通知")
        print("3. 調整策略參數")
        print("4. 開始模擬交易")
        print("5. 謹慎評估後進行實盤交易")
    else:
        print("⚠️ 部分功能需要進一步配置")
    
    return success_count == len(demos)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
