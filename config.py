"""
Configuration management for the quantitative trading system
適合散戶的量化交易系統配置
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class for the trading system"""
    
    # Trading parameters
    INITIAL_CAPITAL = 10000  # 初始資金 (適合散戶的金額)
    MAX_POSITION_SIZE = 0.1  # 單一持倉最大比例 (10%)
    STOP_LOSS_PCT = 0.05     # 停損比例 (5%)
    TAKE_PROFIT_PCT = 0.15   # 停利比例 (15%)
    COMMISSION_RATE = 0.001  # 手續費率 (0.1%)
    
    # Data settings
    DATA_SOURCE = 'yfinance'  # 數據來源
    TIMEFRAME = '1d'          # 時間框架
    LOOKBACK_DAYS = 252       # 回測天數 (一年)
    
    # Strategy parameters
    RSI_PERIOD = 14           # RSI 週期
    RSI_OVERSOLD = 30         # RSI 超賣線
    RSI_OVERBOUGHT = 70       # RSI 超買線
    MA_SHORT = 20             # 短期移動平均線
    MA_LONG = 50              # 長期移動平均線
    
    # Risk management
    MAX_DAILY_LOSS = 0.02     # 每日最大虧損 (2%)
    MAX_DRAWDOWN = 0.15       # 最大回撤 (15%)
    
    # Notification settings
    EMAIL_ENABLED = True
    SMS_ENABLED = False       # 預設關閉，避免額外費用
    
    # Email configuration (需要設定環境變數)
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', '')
    
    # SMS configuration (需要設定環境變數)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    SMS_RECIPIENT = os.getenv('SMS_RECIPIENT', '')
    
    # Database settings
    DATABASE_URL = 'sqlite:///trading_system.db'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'trading_system.log'
