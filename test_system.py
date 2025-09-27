#!/usr/bin/env python3
"""
Test script for the quantitative trading system
量化交易系統測試腳本
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("測試模組導入...")
    
    try:
        from config import Config
        print("✓ Config module imported successfully")
    except Exception as e:
        print(f"✗ Config module import failed: {e}")
        return False
    
    try:
        from data import DataProvider
        print("✓ DataProvider module imported successfully")
    except Exception as e:
        print(f"✗ DataProvider module import failed: {e}")
        return False
    
    try:
        from strategies import RSIMAStrategy
        print("✓ RSIMAStrategy module imported successfully")
    except Exception as e:
        print(f"✗ RSIMAStrategy module import failed: {e}")
        return False
    
    try:
        from backtesting import BacktestEngine
        print("✓ BacktestEngine module imported successfully")
    except Exception as e:
        print(f"✗ BacktestEngine module import failed: {e}")
        return False
    
    try:
        from risk import RiskManager
        print("✓ RiskManager module imported successfully")
    except Exception as e:
        print(f"✗ RiskManager module import failed: {e}")
        return False
    
    try:
        from notifications import NotificationService
        print("✓ NotificationService module imported successfully")
    except Exception as e:
        print(f"✗ NotificationService module import failed: {e}")
        return False
    
    return True

def test_data_provider():
    """Test data provider functionality"""
    print("\n測試數據提供者...")
    
    try:
        from data import DataProvider
        provider = DataProvider()
        
        # Test getting data for a single symbol
        data = provider.get_stock_data('AAPL', period='5d')
        
        if data.empty:
            print("✗ No data retrieved for AAPL")
            return False
        
        print(f"✓ Retrieved {len(data)} records for AAPL")
        print(f"  Date range: {data['date'].min()} to {data['date'].max()}")
        print(f"  Columns: {list(data.columns)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data provider test failed: {e}")
        return False

def test_strategy():
    """Test strategy functionality"""
    print("\n測試交易策略...")
    
    try:
        from strategies import RSIMAStrategy
        from data import DataProvider
        
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
        print("✓ Strategy created successfully")
        
        # Get test data
        provider = DataProvider()
        data = provider.get_stock_data('AAPL', period='1mo')
        
        if data.empty:
            print("✗ No data available for strategy test")
            return False
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        if 'signal' not in signals.columns:
            print("✗ No signals generated")
            return False
        
        signal_count = (signals['signal'] != 0).sum()
        print(f"✓ Generated {signal_count} trading signals")
        
        return True
        
    except Exception as e:
        print(f"✗ Strategy test failed: {e}")
        return False

def test_risk_manager():
    """Test risk manager functionality"""
    print("\n測試風險管理...")
    
    try:
        from risk import RiskManager
        
        config = {
            'max_position_size': 0.1,
            'stop_loss_pct': 0.05,
            'take_profit_pct': 0.15,
            'max_daily_loss': 0.02,
            'max_drawdown': 0.15
        }
        
        risk_manager = RiskManager(config)
        print("✓ Risk manager created successfully")
        
        # Test position size calculation
        is_valid, size = risk_manager.check_position_size('AAPL', 150.0, 10000, 1)
        
        if not is_valid:
            print("✗ Position size validation failed")
            return False
        
        print(f"✓ Position size validation passed: {size} shares")
        
        return True
        
    except Exception as e:
        print(f"✗ Risk manager test failed: {e}")
        return False

def test_backtest_engine():
    """Test backtest engine functionality"""
    print("\n測試回測引擎...")
    
    try:
        from backtesting import BacktestEngine
        from strategies import RSIMAStrategy
        from data import DataProvider
        
        # Create components
        engine = BacktestEngine(initial_capital=10000, commission_rate=0.001)
        
        config = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'ma_short': 20,
            'ma_long': 50,
            'max_position_size': 0.1
        }
        
        strategy = RSIMAStrategy(config)
        provider = DataProvider()
        
        # Get test data
        data = provider.get_multiple_stocks_data(['AAPL'], period='1mo')
        
        if data.empty:
            print("✗ No data available for backtest")
            return False
        
        # Run backtest
        results = engine.run_backtest(data, strategy, ['AAPL'])
        
        if not results:
            print("✗ Backtest failed to produce results")
            return False
        
        print("✓ Backtest completed successfully")
        print(f"  Total return: {results.get('total_return', 0):.2%}")
        print(f"  Total trades: {results.get('total_trades', 0)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Backtest engine test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("量化交易系統測試")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_data_provider,
        test_strategy,
        test_risk_manager,
        test_backtest_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("測試結果:")
    print("=" * 40)
    print(f"通過: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有測試通過！系統可以正常使用。")
    else:
        print("✗ 部分測試失敗，請檢查錯誤訊息。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
