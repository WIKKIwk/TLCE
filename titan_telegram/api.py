"""
API Endpoints for Telegram Bot Integration
"""
import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=True)
def webhook():
    """Telegram Bot Webhook Endpoint"""
    try:
        data = frappe.request.get_json()
        if not data:
            return {"ok": False, "error": "No data received"}
        
        from .telegram_bot import TelegramBotManager
        manager = TelegramBotManager()
        manager.process_update(data)
        
        return {"ok": True}
    except Exception as e:
        frappe.log_error(f"Webhook error: {str(e)}")
        return {"ok": False, "error": str(e)}

@frappe.whitelist()
def register_device(device_id, chat_id, user_id):
    """Register new device from Telegram"""
    try:
        if frappe.db.exists("Telegram Device", {"device_id": device_id}):
            doc = frappe.get_doc("Telegram Device", {"device_id": device_id})
            doc.chat_id = chat_id
            doc.user_id = user_id
            doc.status = "Online"
            doc.save()
        else:
            doc = frappe.get_doc({
                "doctype": "Telegram Device",
                "device_id": device_id,
                "chat_id": chat_id,
                "user_id": user_id,
                "status": "Online"
            })
            doc.insert()
        
        frappe.db.commit()
        return {"ok": True, "message": "Device registered"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@frappe.whitelist()
def start_batch(device_id, batch_id, product_id):
    """Start batch from Telegram"""
    try:
        if not frappe.db.exists("Telegram Device", {"device_id": device_id}):
            return {"ok": False, "error": "Device not found"}
        
        if not frappe.db.exists("Batch", batch_id):
            batch = frappe.get_doc({
                "doctype": "Batch",
                "batch_id": batch_id,
                "item": product_id
            })
            batch.insert()
        
        frappe.get_doc({
            "doctype": "Telegram Log",
            "device_id": device_id,
            "action": "start_batch",
            "batch_id": batch_id,
            "product_id": product_id,
            "status": "Success"
        }).insert()
        
        frappe.db.commit()
        return {"ok": True, "message": f"Batch {batch_id} started"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@frappe.whitelist()
def get_products(warehouse=None):
    """Get available products"""
    try:
        products = frappe.get_all(
            "Item",
            filters={"is_stock_item": 1},
            fields=["name", "item_name", "item_code"],
            limit=50
        )
        return {"ok": True, "products": products}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@frappe.whitelist()
def get_warehouses():
    """Get warehouse list"""
    try:
        warehouses = frappe.get_all(
            "Warehouse",
            filters={"is_group": 0, "disabled": 0},
            fields=["name", "warehouse_name"]
        )
        return {"ok": True, "warehouses": warehouses}
    except Exception as e:
        return {"ok": False, "error": str(e)}
