"""
Telegram Bot Manager
"""
import frappe
import requests
import json

class TelegramBotManager:
    def __init__(self):
        settings = frappe.get_doc("Telegram Settings")
        self.token = settings.get_password("bot_token")
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def process_update(self, update):
        if "message" in update:
            self.handle_message(update["message"])
        elif "callback_query" in update:
            self.handle_callback(update["callback_query"])
    
    def handle_message(self, message):
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user = message["from"]
        
        if text.startswith("/start"):
            self.cmd_start(chat_id, user)
        elif text.startswith("/status"):
            self.cmd_status(chat_id)
        elif text.startswith("/batch"):
            self.cmd_batch(chat_id, text)
        elif text.startswith("/product"):
            self.cmd_product(chat_id)
        elif text.startswith("/help"):
            self.cmd_help(chat_id)
        else:
            self.handle_state(chat_id, text, user, message.get("message_id"))
    
    def handle_callback(self, callback):
        chat_id = callback["message"]["chat"]["id"]
        data = callback["data"]
        
        if data.startswith("product:"):
            product_id = data.split(":")[1]
            self.send_message(chat_id, f"Product selected: {product_id}")
    
    def cmd_start(self, chat_id, user):
        message = """🏭 *TITAN RFID System*

Welcome! Please configure your device:

1️⃣ Enter ERP URL
2️⃣ Enter Device ID  
3️⃣ Enter API Token

Your session will be secured."""
        self.send_message(chat_id, message, parse_mode="Markdown")
        self.set_user_state(chat_id, "awaiting_erp_url")
    
    def cmd_status(self, chat_id):
        device = self.get_device_by_chat(chat_id)
        if not device:
            self.send_message(chat_id, "❌ No device registered. Use /start")
            return
        
        message = f"""📊 *Device Status*

Device: `{device.device_id}`
Status: {device.status}
Warehouse: {device.warehouse or "Not set"}"""
        self.send_message(chat_id, message, parse_mode="Markdown")
    
    def cmd_batch(self, chat_id, text):
        keyboard = {
            "inline_keyboard": [
                [{"text": "▶️ Start Batch", "callback_data": "batch:start"}],
                [{"text": "⏹ Stop Batch", "callback_data": "batch:stop"}]
            ]
        }
        self.send_message(chat_id, "📦 Batch Operations:", reply_markup=keyboard)
    
    def cmd_product(self, chat_id):
        products = frappe.get_all("Item", filters={"is_stock_item": 1}, fields=["name", "item_name"], limit=10)
        keyboard = {"inline_keyboard": []}
        for product in products:
            keyboard["inline_keyboard"].append([{
                "text": product["item_name"],
                "callback_data": f"product:{product['name']}"
            }])
        self.send_message(chat_id, "📦 Select Product:", reply_markup=keyboard)
    
    def cmd_help(self, chat_id):
        message = """📚 *Available Commands:*

/start - Initialize device
/status - Check device status
/batch - Batch operations
/product - Select product
/help - Show this help

Contact: dev@accord.uz"""
        self.send_message(chat_id, message, parse_mode="Markdown")
    
    def handle_state(self, chat_id, text, user, message_id):
        state = self.get_user_state(chat_id)
        
        if state == "awaiting_erp_url":
            self.set_temp_data(chat_id, "erp_url", text)
            self.set_user_state(chat_id, "awaiting_device_id")
            self.send_message(chat_id, "✅ ERP URL saved.\n\nNow enter Device ID:")
        
        elif state == "awaiting_device_id":
            self.set_temp_data(chat_id, "device_id", text)
            self.set_user_state(chat_id, "awaiting_token")
            self.send_message(chat_id, "🔑 Now enter API Token:\n\n(⚠️ This message will be deleted for security)")
        
        elif state == "awaiting_token":
            self.delete_message(chat_id, message_id)
            erp_url = self.get_temp_data(chat_id, "erp_url")
            device_id = self.get_temp_data(chat_id, "device_id")
            
            frappe.get_doc({
                "doctype": "Telegram Session",
                "chat_id": chat_id,
                "user_id": user["id"],
                "username": user.get("username"),
                "erp_url": erp_url,
                "device_id": device_id,
                "api_token": text,
                "status": "Active"
            }).insert()
            
            frappe.get_doc({
                "doctype": "Telegram Device",
                "device_id": device_id,
                "chat_id": chat_id,
                "user_id": user["id"],
                "status": "Online"
            }).insert()
            
            self.clear_temp_data(chat_id)
            self.set_user_state(chat_id, "authenticated")
            self.send_message(chat_id, "✅ *Authentication Successful!*\n\nYour device is connected.", parse_mode="Markdown")
    
    def send_message(self, chat_id, text, parse_mode=None, reply_markup=None):
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            frappe.log_error(f"Telegram send error: {str(e)}")
    
    def delete_message(self, chat_id, message_id):
        url = f"{self.api_url}/deleteMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "message_id": message_id}, timeout=5)
        except:
            pass
    
    def set_user_state(self, chat_id, state):
        frappe.cache().set_value(f"tg_state:{chat_id}", state)
    
    def get_user_state(self, chat_id):
        return frappe.cache().get_value(f"tg_state:{chat_id}") or "none"
    
    def set_temp_data(self, chat_id, key, value):
        frappe.cache().set_value(f"tg_temp:{chat_id}:{key}", value, expires_in_sec=600)
    
    def get_temp_data(self, chat_id, key):
        return frappe.cache().get_value(f"tg_temp:{chat_id}:{key}")
    
    def clear_temp_data(self, chat_id):
        pass
    
    def get_device_by_chat(self, chat_id):
        if frappe.db.exists("Telegram Device", {"chat_id": chat_id}):
            return frappe.get_doc("Telegram Device", {"chat_id": chat_id})
        return None

def process_updates():
    """Scheduled task to process updates"""
    pass
