#!/usr/bin/env python3
"""
Demo script with mock data for the quantitative trading system
使用模擬數據的量化交易系統演示
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
from risk import RiskManager
from notifications import NotificationService

def generate_mock_data(symbols, days=252):
    """
    Generate mock stock data for demonstration
    
    Args:
        symbols: List of stock symbols
        days: Number of days of data to generate
        
    Returns:
        DataFrame with mock OHLCV data
    """
    all_data = []
    
    for symbol in symbols:
        # Generate random walk price data
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
        
        # Starting price
        price = 100 + np.random.uniform(-20, 20)
        
        # Generate price series using random walk
        returns = np.random.normal(0.001, 0.02, days)  # Daily returns
        prices = [price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 1))  # Ensure positive prices
        
        # Generate OHLCV data
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             periods=days, freq='D')
        
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Generate OHLC from close price
            volatility = np.random.uniform(0.01, 0.03)
            high = close * (1 + np.random.uniform(0, volatility))
            low = close * (1 - np.random.uniform(0, volatility))
            open_price = low + np.random.uniform(0, high - low)
            
            # Generate volume
            volume = np.random.randint(1000000, 10000000)
            
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

def demo_backtest():
    """Demonstrate backtesting with mock data"""
    print("量化交易系統演示 - 使用模擬數據")
    print("=" * 50)
    
    # Generate mock data
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    print(f"生成模擬數據 - 標的: {symbols}")
    
    data = generate_mock_data(symbols, days=252)
    print(f"✓ 生成了 {len(data)} 筆數據記錄")
    
    # Create strategy
    strategy_config = {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'ma_short': 20,
        'ma_long': 50,
        'max_position_size': 0.1,
        'stop_loss_pct': 0.05,
        'take_profit_pct': 0.15
    }
    
    strategy = RSIMAStrategy(strategy_config)
    print("✓ 策略創建成功")
    
    # Run backtest
    backtest_engine = BacktestEngine(initial_capital=10000, commission_rate=0.001)
    print("開始回測...")
    
    results = backtest_engine.run_backtest(data, strategy, symbols)
    
    if results:
        print("\n回測結果:")
        print("-" * 50)
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
            print("-" * 50)
            print(trades.head().to_string(index=False))
        
        # Generate plot
        try:
            plot_file = 'demo_backtest_results.png'
            backtest_engine.plot_results(results, save_path=plot_file)
            print(f"\n圖表已保存至: {plot_file}")
        except Exception as e:
            print(f"無法生成圖表: {str(e)}")
        
        return True
    else:
        print("回測失敗")
        return False

def demo_risk_management():
    """Demonstrate risk management features"""
    print("\n風險管理演示:")
    print("-" * 50)
    
    config = {
        'max_position_size': 0.1,
        'stop_loss_pct': 0.05,
        'take_profit_pct': 0.15,
        'max_daily_loss': 0.02,
        'max_drawdown': 0.15
    }
    
    risk_manager = RiskManager(config)
    
    # Test position size calculation
    is_valid, size = risk_manager.check_position_size('AAPL', 150.0, 10000, 1)
    print(f"持倉大小檢查: {'通過' if is_valid else '失敗'} - 建議股數: {size}")
    
    # Test daily loss limit
    current_capital = 9500  # 5% loss
    initial_capital = 10000
    within_limit = risk_manager.check_daily_loss_limit(current_capital, initial_capital)
    print(f"每日虧損限制檢查: {'通過' if within_limit else '超過限制'}")
    
    # Test drawdown limit
    within_drawdown = risk_manager.check_drawdown_limit(current_capital)
    print(f"回撤限制檢查: {'通過' if within_drawdown else '超過限制'}")
    
    return True

def demo_notification():
    """Demonstrate notification features"""
    print("\n通知系統演示:")
    print("-" * 50)
    
    config = {
        'email_enabled': False,  # Disable for demo
        'sms_enabled': False,    # Disable for demo
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'email_username': '',
        'email_password': '',
        'email_recipient': ''
    }
    
    notification_service = NotificationService(config)
    
    # Test trade alert
    trade_info = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'shares': 10,
        'price': 150.0,
        'value': 1500.0,
        'timestamp': datetime.now()
    }
    
    print("模擬交易通知:")
    print(f"股票: {trade_info['symbol']}")
    print(f"動作: {trade_info['action']}")
    print(f"股數: {trade_info['shares']}")
    print(f"價格: ${trade_info['price']:.2f}")
    print(f"金額: ${trade_info['value']:.2f}")
    
    # Test portfolio alert
    portfolio_info = {
        'total_value': 10500.0,
        'total_pnl': 500.0,
        'pnl_pct': 0.05,
        'positions': [
            {'symbol': 'AAPL', 'shares': 10, 'price': 150.0, 'pnl': 100.0},
            {'symbol': 'MSFT', 'shares': 5, 'price': 200.0, 'pnl': 50.0}
        ],
        'alert_level': 'normal'
    }
    
    print(f"\n模擬投資組合狀態:")
    print(f"總價值: ${portfolio_info['total_value']:.2f}")
    print(f"總損益: ${portfolio_info['total_pnl']:.2f} ({portfolio_info['pnl_pct']:.2%})")
    print(f"持倉數量: {len(portfolio_info['positions'])}")
    
    return True

def main():
    """Main demo function"""
    print("🚀 量化交易系統演示")
    print("=" * 50)
    print("此演示使用模擬數據來展示系統功能")
    print("在實際使用中，系統會從真實市場獲取數據")
    print()
    
    # Run demonstrations
    demos = [
        ("回測功能", demo_backtest),
        ("風險管理", demo_risk_management),
        ("通知系統", demo_notification)
    ]
    
    success_count = 0
    total_demos = len(demos)
    
    for name, demo_func in demos:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            if demo_func():
                print(f"✓ {name} 演示成功")
                success_count += 1
            else:
                print(f"✗ {name} 演示失敗")
        except Exception as e:
            print(f"✗ {name} 演示出錯: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"演示結果: {success_count}/{total_demos} 成功")
    
    if success_count == total_demos:
        print("🎉 所有功能演示成功！系統可以正常使用。")
        print("\n下一步:")
        print("1. 配置真實的市場數據源")
        print("2. 設定通知服務（郵件/簡訊）")
        print("3. 調整策略參數以符合您的需求")
        print("4. 開始實際交易（請謹慎評估風險）")
    else:
        print("⚠️ 部分功能需要進一步配置")
    
    return success_count == total_demos

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
