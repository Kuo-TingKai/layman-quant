#!/usr/bin/env python3
"""
Live trading runner script
即時交易執行腳本
"""

import sys
import os
import argparse
import time
import schedule
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import TradingSystem
from config import Config

def run_live_trading(symbols, strategy_config=None, interval_minutes=60):
    """
    Run live trading simulation
    
    Args:
        symbols: List of stock symbols
        strategy_config: Strategy configuration
        interval_minutes: Trading interval in minutes
    """
    print(f"開始即時交易模擬 - 標的: {symbols}")
    print(f"交易間隔: {interval_minutes} 分鐘")
    print("=" * 50)
    
    # Initialize trading system
    trading_system = TradingSystem()
    
    # Schedule trading
    def trading_job():
        print(f"\n執行交易檢查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            # Get current portfolio summary
            portfolio = trading_system.get_portfolio_summary()
            print(f"投資組合價值: ${portfolio['portfolio_value']:.2f}")
            print(f"總損益: ${portfolio['total_pnl']:.2f} ({portfolio['pnl_pct']:.2%})")
            print(f"持倉數量: {len(portfolio['positions'])}")
            
            # Run one trading cycle
            trading_system.run_live_trading(symbols, strategy_config)
            
        except Exception as e:
            print(f"交易執行錯誤: {str(e)}")
            trading_system.notification_service.send_error_alert({
                'error_type': 'Live Trading Error',
                'error_message': str(e),
                'severity': 'high',
                'timestamp': datetime.now()
            })
    
    # Schedule the job
    schedule.every(interval_minutes).minutes.do(trading_job)
    
    # Run initial check
    trading_job()
    
    # Main loop
    print(f"\n即時交易已啟動，每 {interval_minutes} 分鐘執行一次")
    print("按 Ctrl+C 停止交易")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n交易已停止")
        
        # Final portfolio summary
        portfolio = trading_system.get_portfolio_summary()
        print("\n最終投資組合摘要:")
        print("=" * 50)
        print(f"投資組合價值: ${portfolio['portfolio_value']:.2f}")
        print(f"總損益: ${portfolio['total_pnl']:.2f} ({portfolio['pnl_pct']:.2%})")
        print(f"總交易次數: {portfolio['total_trades']}")
        print(f"持倉數量: {len(portfolio['positions'])}")
        
        if portfolio['positions']:
            print("\n當前持倉:")
            for symbol, pos in portfolio['positions'].items():
                print(f"  {symbol}: {pos['shares']}股 @ ${pos['entry_price']:.2f}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='量化交易系統即時交易')
    parser.add_argument('--symbols', nargs='+', default=['AAPL', 'MSFT', 'GOOGL'],
                       help='股票代碼列表 (預設: AAPL MSFT GOOGL)')
    parser.add_argument('--interval', type=int, default=60,
                       help='交易間隔（分鐘） (預設: 60)')
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
    
    # Run live trading
    run_live_trading(args.symbols, strategy_config, args.interval)

if __name__ == "__main__":
    main()
