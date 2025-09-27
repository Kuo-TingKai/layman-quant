"""
Notification service for trading alerts
交易通知服務
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
from datetime import datetime
from twilio.rest import Client
import logging

class NotificationService:
    """Notification service for trading alerts"""
    
    def __init__(self, config: Dict):
        """
        Initialize notification service
        
        Args:
            config: Notification configuration
        """
        self.config = config
        self.email_enabled = config.get('email_enabled', False)
        self.sms_enabled = config.get('sms_enabled', False)
        
        # Email configuration
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.email_username = config.get('email_username', '')
        self.email_password = config.get('email_password', '')
        self.email_recipient = config.get('email_recipient', '')
        
        # SMS configuration
        self.twilio_account_sid = config.get('twilio_account_sid', '')
        self.twilio_auth_token = config.get('twilio_auth_token', '')
        self.twilio_phone_number = config.get('twilio_phone_number', '')
        self.sms_recipient = config.get('sms_recipient', '')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def send_trade_alert(self, trade_info: Dict) -> bool:
        """
        Send trade alert notification
        
        Args:
            trade_info: Dictionary with trade information
            
        Returns:
            True if notification sent successfully
        """
        message = self._format_trade_message(trade_info)
        
        success = True
        
        # Send email notification
        if self.email_enabled:
            if not self._send_email("交易提醒", message):
                success = False
        
        # Send SMS notification
        if self.sms_enabled:
            if not self._send_sms(message):
                success = False
        
        return success
    
    def send_portfolio_alert(self, portfolio_info: Dict) -> bool:
        """
        Send portfolio status alert
        
        Args:
            portfolio_info: Dictionary with portfolio information
            
        Returns:
            True if notification sent successfully
        """
        message = self._format_portfolio_message(portfolio_info)
        
        success = True
        
        # Send email notification
        if self.email_enabled:
            if not self._send_email("投資組合狀態", message):
                success = False
        
        # Send SMS notification (only for critical alerts)
        if self.sms_enabled and portfolio_info.get('alert_level') == 'critical':
            if not self._send_sms(message):
                success = False
        
        return success
    
    def send_error_alert(self, error_info: Dict) -> bool:
        """
        Send error alert notification
        
        Args:
            error_info: Dictionary with error information
            
        Returns:
            True if notification sent successfully
        """
        message = self._format_error_message(error_info)
        
        success = True
        
        # Send email notification
        if self.email_enabled:
            if not self._send_email("系統錯誤", message):
                success = False
        
        # Send SMS notification for critical errors
        if self.sms_enabled and error_info.get('severity') == 'critical':
            if not self._send_sms(message):
                success = False
        
        return success
    
    def send_backtest_results(self, backtest_info: Dict) -> bool:
        """
        Send backtest results notification
        
        Args:
            backtest_info: Dictionary with backtest results
            
        Returns:
            True if notification sent successfully
        """
        message = self._format_backtest_message(backtest_info)
        
        success = True
        
        # Send email notification
        if self.email_enabled:
            subject = f"回測結果 - {backtest_info.get('strategy_name', '量化策略')}"
            if not self._send_email(subject, message):
                success = False
        
        # Send SMS notification for significant results
        if self.sms_enabled and self._should_send_sms_for_backtest(backtest_info):
            if not self._send_sms(message):
                success = False
        
        return success
    
    def _format_trade_message(self, trade_info: Dict) -> str:
        """Format trade information into message"""
        symbol = trade_info.get('symbol', 'N/A')
        action = trade_info.get('action', 'N/A')
        shares = trade_info.get('shares', 0)
        price = trade_info.get('price', 0.0)
        value = trade_info.get('value', 0.0)
        timestamp = trade_info.get('timestamp', datetime.now())
        
        message = f"""
交易提醒 - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

股票代碼: {symbol}
交易動作: {action}
股數: {shares}
價格: ${price:.2f}
交易金額: ${value:.2f}

---
量化交易系統
        """
        
        return message.strip()
    
    def _format_portfolio_message(self, portfolio_info: Dict) -> str:
        """Format portfolio information into message"""
        total_value = portfolio_info.get('total_value', 0.0)
        total_pnl = portfolio_info.get('total_pnl', 0.0)
        pnl_pct = portfolio_info.get('pnl_pct', 0.0)
        positions = portfolio_info.get('positions', [])
        alert_level = portfolio_info.get('alert_level', 'normal')
        
        message = f"""
投資組合狀態 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

總價值: ${total_value:.2f}
總損益: ${total_pnl:.2f} ({pnl_pct:.2f}%)
警報等級: {alert_level}

持倉:
"""
        
        for pos in positions:
            symbol = pos.get('symbol', 'N/A')
            shares = pos.get('shares', 0)
            price = pos.get('price', 0.0)
            pnl = pos.get('pnl', 0.0)
            message += f"  {symbol}: {shares}股 @ ${price:.2f} (損益: ${pnl:.2f})\n"
        
        message += "\n---\n量化交易系統"
        
        return message.strip()
    
    def _format_error_message(self, error_info: Dict) -> str:
        """Format error information into message"""
        error_type = error_info.get('error_type', 'Unknown')
        error_message = error_info.get('error_message', 'No details')
        severity = error_info.get('severity', 'normal')
        timestamp = error_info.get('timestamp', datetime.now())
        
        message = f"""
系統錯誤 - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

錯誤類型: {error_type}
嚴重程度: {severity}
錯誤訊息: {error_message}

---
量化交易系統
        """
        
        return message.strip()
    
    def _format_backtest_message(self, backtest_info: Dict) -> str:
        """Format backtest results into message"""
        strategy_name = backtest_info.get('strategy_name', '量化策略')
        symbols = backtest_info.get('symbols', [])
        period = backtest_info.get('period', 'N/A')
        total_return = backtest_info.get('total_return', 0)
        annualized_return = backtest_info.get('annualized_return', 0)
        sharpe_ratio = backtest_info.get('sharpe_ratio', 0)
        max_drawdown = backtest_info.get('max_drawdown', 0)
        total_trades = backtest_info.get('total_trades', 0)
        win_rate = backtest_info.get('win_rate', 0)
        final_value = backtest_info.get('final_portfolio_value', 0)
        initial_capital = backtest_info.get('initial_capital', 10000)
        timestamp = backtest_info.get('timestamp', datetime.now())
        
        # Performance evaluation
        performance_status = "良好" if total_return > 0.1 else "一般" if total_return > 0 else "需改善"
        risk_status = "低風險" if abs(max_drawdown) < 0.1 else "中等風險" if abs(max_drawdown) < 0.2 else "高風險"
        
        message = f"""
回測結果通知 - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

策略名稱: {strategy_name}
測試標的: {', '.join(symbols)}
回測期間: {period}

📊 績效摘要:
💰 初始資金: ${initial_capital:,.0f}
💰 最終價值: ${final_value:,.0f}
📈 總報酬率: {total_return:.2%}
📊 年化報酬率: {annualized_return:.2%}
⚖️ 夏普比率: {sharpe_ratio:.2f}
📉 最大回撤: {max_drawdown:.2%}

🔄 交易統計:
📋 總交易次數: {total_trades}
🎯 勝率: {win_rate:.2%}

📈 績效評估:
• 報酬表現: {performance_status}
• 風險等級: {risk_status}

💡 建議:
{self._get_backtest_suggestions(total_return, sharpe_ratio, max_drawdown, total_trades)}

---
量化交易系統
        """
        
        return message.strip()
    
    def _get_backtest_suggestions(self, total_return: float, sharpe_ratio: float, 
                                 max_drawdown: float, total_trades: int) -> str:
        """Generate suggestions based on backtest results"""
        suggestions = []
        
        if total_return < 0:
            suggestions.append("• 考慮調整策略參數或更換標的")
        elif total_return < 0.05:
            suggestions.append("• 可嘗試更積極的策略參數")
        
        if sharpe_ratio < 0.5:
            suggestions.append("• 建議優化風險調整後報酬")
        elif sharpe_ratio > 1.5:
            suggestions.append("• 策略表現優異，可考慮增加資金")
        
        if abs(max_drawdown) > 0.15:
            suggestions.append("• 建議加強風險控制機制")
        
        if total_trades < 5:
            suggestions.append("• 策略信號較少，可調整參數增加交易頻率")
        elif total_trades > 50:
            suggestions.append("• 交易頻率較高，注意手續費影響")
        
        if not suggestions:
            suggestions.append("• 策略表現穩定，可繼續觀察")
        
        return '\n'.join(suggestions)
    
    def _should_send_sms_for_backtest(self, backtest_info: Dict) -> bool:
        """Determine if SMS should be sent for backtest results"""
        total_return = backtest_info.get('total_return', 0)
        max_drawdown = backtest_info.get('max_drawdown', 0)
        
        # Send SMS for significant results
        return (total_return > 0.2 or total_return < -0.1 or 
                abs(max_drawdown) > 0.2)
    
    def _send_email(self, subject: str, message: str) -> bool:
        """Send email notification"""
        try:
            if not all([self.email_username, self.email_password, self.email_recipient]):
                self.logger.warning("Email configuration incomplete")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = self.email_recipient
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # Create SMTP session
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_username, self.email_password)
                server.send_message(msg)
            
            self.logger.info("Email notification sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def _send_sms(self, message: str) -> bool:
        """Send SMS notification"""
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, 
                       self.twilio_phone_number, self.sms_recipient]):
                self.logger.warning("SMS configuration incomplete")
                return False
            
            # Create Twilio client
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            # Send SMS
            message_obj = client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=self.sms_recipient
            )
            
            self.logger.info(f"SMS notification sent successfully: {message_obj.sid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def test_notifications(self) -> Dict:
        """Test notification services"""
        results = {
            'email': False,
            'sms': False
        }
        
        # Test email
        if self.email_enabled:
            test_message = "這是一封測試郵件，確認通知系統正常運作。"
            results['email'] = self._send_email("測試郵件", test_message)
        
        # Test SMS
        if self.sms_enabled:
            test_message = "測試簡訊：通知系統正常運作。"
            results['sms'] = self._send_sms(test_message)
        
        return results
