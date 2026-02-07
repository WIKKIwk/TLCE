"""
Installation hooks
"""
import frappe
from .workspace_utils import ensure_workspace

def after_install():
    """Create default settings after install"""
    if not frappe.db.exists("Telegram Settings"):
        doc = frappe.get_doc({
            "doctype": "Telegram Settings",
            "enabled": 0,
            "bot_username": "YourBotUsername",
            "session_timeout": 24
        })
        doc.insert()
        frappe.db.commit()
    ensure_workspace()
