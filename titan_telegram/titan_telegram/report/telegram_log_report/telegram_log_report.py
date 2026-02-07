import frappe
from frappe import _
from frappe.utils import get_datetime


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": _("Date"), "fieldname": "creation", "fieldtype": "Datetime", "width": 160},
        {"label": _("Device ID"), "fieldname": "device_id", "fieldtype": "Data", "width": 140},
        {"label": _("Action"), "fieldname": "action", "fieldtype": "Data", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Batch ID"), "fieldname": "batch_id", "fieldtype": "Data", "width": 140},
        {"label": _("Product ID"), "fieldname": "product_id", "fieldtype": "Data", "width": 140},
        {"label": _("Message"), "fieldname": "message", "fieldtype": "Data", "width": 300},
        {"label": _("Error"), "fieldname": "error", "fieldtype": "Data", "width": 300},
    ]

    conditions = []
    values = {}

    if filters.get("device_id"):
        conditions.append("device_id = %(device_id)s")
        values["device_id"] = filters["device_id"]

    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]

    if filters.get("action"):
        conditions.append("action = %(action)s")
        values["action"] = filters["action"]

    if filters.get("from_date"):
        conditions.append("creation >= %(from_date)s")
        values["from_date"] = get_datetime(filters["from_date"])

    if filters.get("to_date"):
        conditions.append("creation <= %(to_date)s")
        values["to_date"] = get_datetime(filters["to_date"])

    where = " where " + " and ".join(conditions) if conditions else ""

    data = frappe.db.sql(
        f"""
            select
                creation, device_id, action, status, batch_id, product_id, message, error
            from `tabTelegram Log`
            {where}
            order by creation desc
        """,
        values,
        as_dict=True,
    )

    return columns, data
