# 量化交易系統 (Quantitative Trading System)

一個專為有限預算散戶設計的量化交易系統，包含策略開發、回測、風險管理和通知功能。

## 系統特色

- 🎯 **適合散戶**: 專為小額投資者設計，初始資金僅需 $10,000
- 📊 **多種策略**: 內建 RSI + 移動平均策略，易於擴展
- 🔄 **完整回測**: 提供詳細的回測分析和視覺化圖表
- 🛡️ **風險管理**: 內建停損、停利、持倉限制等風險控制
- 📧 **即時通知**: 支援郵件和簡訊通知（可選）
- 💰 **低成本**: 使用免費的 yfinance 數據源

## 系統架構

```
quant/
├── config.py                 # 系統配置
├── main.py                   # 主程式
├── requirements.txt          # 依賴套件
├── run_backtest.py          # 回測執行腳本
├── run_live.py              # 即時交易腳本
├── strategies/              # 交易策略
│   ├── __init__.py
│   ├── base_strategy.py     # 策略基類
│   └── rsi_ma_strategy.py   # RSI+MA策略
├── backtesting/             # 回測引擎
│   ├── __init__.py
│   └── backtest_engine.py
├── data/                    # 數據處理
│   ├── __init__.py
│   └── data_provider.py
├── risk/                    # 風險管理
│   ├── __init__.py
│   └── risk_manager.py
└── notifications/           # 通知系統
    ├── __init__.py
    └── notification_service.py
```

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數（可選）

複製 `env_example.txt` 為 `.env` 並填入您的通知設定：

```bash
cp env_example.txt .env
```

編輯 `.env` 檔案，填入您的郵件和簡訊設定。

### 3. 執行回測

```bash
# 使用預設參數回測
python run_backtest.py

# 自訂參數回測
python run_backtest.py --symbols AAPL MSFT GOOGL TSLA --period 1y --rsi-period 14
```

### 4. 執行即時交易模擬

```bash
# 使用預設參數
python run_live.py

# 自訂參數
python run_live.py --symbols AAPL MSFT --interval 30 --rsi-period 14
```

## 使用說明

### 回測功能

回測腳本支援以下參數：

- `--symbols`: 股票代碼列表（預設：AAPL MSFT GOOGL）
- `--period`: 回測期間（1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y）
- `--rsi-period`: RSI 週期（預設：14）
- `--rsi-oversold`: RSI 超賣線（預設：30）
- `--rsi-overbought`: RSI 超買線（預設：70）
- `--ma-short`: 短期移動平均線（預設：20）
- `--ma-long`: 長期移動平均線（預設：50）
- `--max-position`: 最大持倉比例（預設：0.1）

### 即時交易功能

即時交易腳本支援以下參數：

- `--symbols`: 股票代碼列表
- `--interval`: 交易間隔（分鐘）
- 其他策略參數與回測相同

### 策略說明

#### RSI + 移動平均策略

- **買入信號**: RSI < 30 且短期移動平均線向上穿越長期移動平均線
- **賣出信號**: RSI > 70 且短期移動平均線向下穿越長期移動平均線
- **風險控制**: 停損 5%，停利 15%，最大持倉 10%

## 風險管理

系統內建多層風險控制：

1. **持倉限制**: 單一標的最大持倉 10%
2. **停損停利**: 自動停損 5%，停利 15%
3. **每日虧損限制**: 每日最大虧損 2%
4. **最大回撤限制**: 最大回撤 15%
5. **相關性控制**: 限制同類股持倉數量

## 通知功能

### 郵件通知

設定 Gmail 應用程式密碼：

1. 開啟 Google 帳戶設定
2. 啟用兩步驟驗證
3. 生成應用程式密碼
4. 在 `.env` 檔案中設定

### 簡訊通知（可選）

使用 Twilio 服務：

1. 註冊 Twilio 帳戶
2. 獲取 Account SID 和 Auth Token
3. 在 `.env` 檔案中設定

## 自訂策略

您可以輕鬆創建自訂策略：

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__("MyStrategy", config)
    
    def generate_signals(self, data):
        # 實作您的信號生成邏輯
        pass
    
    def calculate_position_size(self, signal, price, available_capital):
        # 實作您的倉位計算邏輯
        pass
```

## 注意事項

1. **僅供學習**: 此系統僅供學習和研究使用
2. **模擬交易**: 預設為模擬交易，不涉及真實資金
3. **數據延遲**: 使用免費數據源可能有延遲
4. **風險警告**: 投資有風險，請謹慎評估

## 故障排除

### 常見問題

1. **數據下載失敗**: 檢查網路連線和股票代碼
2. **郵件發送失敗**: 檢查 Gmail 應用程式密碼設定
3. **依賴套件錯誤**: 執行 `pip install -r requirements.txt`

### 日誌檔案

系統會生成 `trading_system.log` 日誌檔案，包含詳細的執行記錄。

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善系統。

## 授權

MIT License

## 免責聲明

本系統僅供教育和研究目的使用。投資有風險，使用者需自行承擔投資風險。作者不對任何投資損失負責。
