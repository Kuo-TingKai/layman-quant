# 系統架構說明

## 整體架構

```
量化交易系統
├── 配置層 (Config Layer)
│   └── config.py - 系統配置管理
├── 數據層 (Data Layer)
│   └── data_provider.py - 市場數據獲取
├── 策略層 (Strategy Layer)
│   ├── base_strategy.py - 策略基類
│   └── rsi_ma_strategy.py - RSI+MA策略
├── 回測層 (Backtesting Layer)
│   └── backtest_engine.py - 回測引擎
├── 風險管理層 (Risk Management Layer)
│   └── risk_manager.py - 風險控制
├── 通知層 (Notification Layer)
│   └── notification_service.py - 通知服務
└── 應用層 (Application Layer)
    ├── main.py - 主程式
    ├── run_backtest.py - 回測腳本
    └── run_live.py - 即時交易腳本
```

## 核心組件

### 1. 配置管理 (Config)
- 集中管理所有系統參數
- 支援環境變數配置
- 包含交易參數、風險控制、通知設定等

### 2. 數據提供者 (Data Provider)
- 使用 yfinance 獲取市場數據
- 支援多個股票標的
- 內建數據驗證和快取機制

### 3. 交易策略 (Strategy)
- 基於抽象基類的模組化設計
- 內建 RSI + 移動平均策略
- 易於擴展和自訂

### 4. 回測引擎 (Backtest Engine)
- 完整的回測功能
- 支援多種績效指標計算
- 生成詳細的分析報告和圖表

### 5. 風險管理 (Risk Management)
- 多層風險控制機制
- 持倉限制、停損停利
- 相關性風險控制

### 6. 通知服務 (Notification)
- 支援郵件和簡訊通知
- 可配置的通知條件
- 錯誤警報和交易提醒

## 數據流程

```
市場數據 → 數據提供者 → 策略信號生成 → 風險檢查 → 交易執行 → 通知發送
    ↓
回測引擎 ← 績效分析 ← 交易記錄 ← 持倉管理
```

## 風險控制流程

```
交易信號 → 持倉大小檢查 → 相關性檢查 → 停損停利檢查 → 執行交易
    ↓
風險監控 → 每日虧損檢查 → 回撤檢查 → 緊急平倉
```

## 擴展性設計

### 添加新策略
1. 繼承 `BaseStrategy` 類別
2. 實作 `generate_signals` 方法
3. 實作 `calculate_position_size` 方法

### 添加新數據源
1. 擴展 `DataProvider` 類別
2. 實作新的數據獲取方法
3. 保持相同的數據格式

### 添加新通知方式
1. 擴展 `NotificationService` 類別
2. 實作新的通知方法
3. 更新配置管理

## 安全考量

1. **模擬交易**: 預設為模擬模式，不涉及真實資金
2. **風險限制**: 多層風險控制機制
3. **數據驗證**: 完整的數據品質檢查
4. **錯誤處理**: 完善的異常處理機制

## 效能優化

1. **數據快取**: 避免重複下載相同數據
2. **批次處理**: 支援多個標的同時處理
3. **記憶體管理**: 適當的數據清理機制
4. **非同步處理**: 支援非阻塞的數據獲取
