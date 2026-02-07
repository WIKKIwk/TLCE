from frappe import _


def get_data():
    return [
        {
            "label": _("LCE"),
            "items": [
                {"type": "doctype", "name": "LCE Settings", "label": _("LCE Settings")},
                {"type": "page", "name": "lce-dashboard", "label": _("LCE Dashboard")},
            ],
        },
        {
            "label": _("Monitoring"),
            "items": [
                {"type": "doctype", "name": "LCE Draft", "label": _("LCE Draft")},
                {"type": "doctype", "name": "Telegram Log", "label": _("Telegram Log")},
                {"type": "doctype", "name": "Telegram Device", "label": _("Telegram Device")},
                {"type": "doctype", "name": "Telegram Session", "label": _("Telegram Session")},
            ],
        },
    ]
