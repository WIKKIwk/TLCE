"""
Utility functions
"""
import frappe

def notify_stock_entry(doc, method):
    """Notify when Stock Entry is submitted"""
    pass

def notify_batch_update(doc, method):
    """Notify when Batch is updated"""
    pass

def cleanup_old_sessions():
    """Daily cleanup of expired sessions"""
    frappe.db.sql("""
        DELETE FROM `tabTelegram Session`
        WHERE modified < DATE_SUB(NOW(), INTERVAL 30 DAY)
        AND status = 'Expired'
    """)
    frappe.db.commit()
