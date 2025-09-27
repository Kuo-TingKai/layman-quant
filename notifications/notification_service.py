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
