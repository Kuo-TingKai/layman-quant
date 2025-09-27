# 快速開始指南

## 1. 安裝系統

```bash
# 安裝依賴套件
pip install -r requirements.txt

# 測試系統是否正常運作
python test_system.py
```

## 2. 執行回測

```bash
# 使用預設參數回測
python run_backtest.py

# 自訂參數回測
python run_backtest.py --symbols AAPL MSFT GOOGL --period 1y --rsi-period 14
```

## 3. 執行即時交易模擬

```bash
# 使用預設參數
python run_live.py

# 自訂參數
python run_live.py --symbols AAPL MSFT --interval 30
```

## 4. 查看範例

```bash
# 簡單回測範例
python examples/simple_backtest.py

# 自訂策略範例
python examples/custom_strategy.py
```

## 5. 配置通知（可選）

1. 複製環境變數範例檔案：
```bash
cp env_example.txt .env
```

2. 編輯 `.env` 檔案，填入您的通知設定：
```
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=recipient@gmail.com
```

## 常見問題

### Q: 如何修改交易策略參數？
A: 在執行腳本時使用命令列參數，或直接修改 `config.py` 檔案。

### Q: 如何添加新的交易策略？
A: 參考 `examples/custom_strategy.py` 範例，繼承 `BaseStrategy` 類別。

### Q: 如何查看詳細的交易記錄？
A: 系統會生成 `trading_system.log` 日誌檔案，包含所有交易記錄。

### Q: 如何調整風險控制參數？
A: 修改 `config.py` 中的風險管理參數，如 `MAX_POSITION_SIZE`、`STOP_LOSS_PCT` 等。

## 注意事項

- 此系統僅供學習和研究使用
- 預設為模擬交易，不涉及真實資金
- 投資有風險，請謹慎評估
