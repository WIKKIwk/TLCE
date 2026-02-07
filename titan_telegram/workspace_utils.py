import json
import frappe


def ensure_workspace():
    shortcuts = []

    links = [
        {"type": "Card Break", "label": "Settings", "icon": "octicon octicon-gear"},
        {"type": "Link", "label": "LCE Settings", "link_type": "DocType", "link_to": "LCE Settings"},
        {"type": "Card Break", "label": "Devices", "icon": "octicon octicon-device-mobile"},
        {"type": "Link", "label": "Telegram Device", "link_type": "DocType", "link_to": "Telegram Device"},
        {"type": "Link", "label": "Telegram Session", "link_type": "DocType", "link_to": "Telegram Session"},
        {"type": "Card Break", "label": "Monitoring", "icon": "octicon octicon-dashboard"},
        {"type": "Link", "label": "LCE Dashboard", "link_type": "Page", "link_to": "lce-dashboard"},
        {"type": "Card Break", "label": "Reports", "icon": "octicon octicon-graph"},
        {"type": "Link", "label": "Telegram Log", "link_type": "DocType", "link_to": "Telegram Log"},
        {"type": "Link", "label": "LCE Draft", "link_type": "DocType", "link_to": "LCE Draft"},
    ]

    content = [
        {
            "id": "tg_header_sections",
            "type": "header",
            "data": {"text": "<span class=\"h4\"><b>Sections</b></span>", "col": 12},
        },
        {"id": "tg_card_settings", "type": "card", "data": {"card_name": "Settings", "col": 4}},
        {"id": "tg_card_devices", "type": "card", "data": {"card_name": "Devices", "col": 4}},
        {"id": "tg_card_monitoring", "type": "card", "data": {"card_name": "Monitoring", "col": 4}},
        {"id": "tg_card_reports", "type": "card", "data": {"card_name": "Reports", "col": 4}},
    ]

    if frappe.db.exists("Workspace", "Titan Telegram"):
        ws = frappe.get_doc("Workspace", "Titan Telegram")
    else:
        ws = frappe.new_doc("Workspace")
        ws.name = "Titan Telegram"

    ws.label = "Titan Telegram"
    ws.title = "Titan Telegram"
    ws.module = "Titan Telegram"
    ws.public = 1
    ws.is_hidden = 0
    ws.content = json.dumps(content)
    ws.set("shortcuts", shortcuts)
    ws.set("links", links)
    ws.set("roles", [{"role": "System Manager"}, {"role": "Administrator"}])

    ws.save(ignore_permissions=True)
    frappe.db.commit()
