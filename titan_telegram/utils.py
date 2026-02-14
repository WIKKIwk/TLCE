"""Utility functions for Titan Telegram app."""
from __future__ import annotations

import requests
import frappe


def on_stock_entry_event(doc, method=None):
    """
    Stock Entry doc_event handler.

    Sends lightweight webhook to LCE bridge so RFID draft/EPC cache updates
    immediately when draft is created/updated/submitted/cancelled.
    """
    try:
        name = (getattr(doc, "name", None) or "").strip()
        if not name:
            return

        payload = {
            "doctype": "Stock Entry",
            "name": name,
            "event": (method or "").strip() or "unknown",
        }

        # Best effort, non-blocking for ERP user flow.
        enqueue_kwargs = {
            "queue": "short",
            "payload": payload,
            "enqueue_after_commit": True,
        }

        try:
            frappe.enqueue("titan_telegram.utils.push_lce_webhook", **enqueue_kwargs)
        except TypeError:
            enqueue_kwargs.pop("enqueue_after_commit", None)
            frappe.enqueue("titan_telegram.utils.push_lce_webhook", **enqueue_kwargs)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "TitanTelegram: on_stock_entry_event failed")


def push_lce_webhook(payload=None):
    """Background job: POST webhook event to LCE bridge."""
    payload = payload or {}
    try:
        settings = frappe.get_doc("LCE Settings")
        lce_url = (settings.lce_url or "").strip().rstrip("/")
        if not lce_url:
            return

        url = f"{lce_url}/api/webhook/erp"
        event_payload = {
            "doctype": payload.get("doctype") or "Stock Entry",
            "name": payload.get("name"),
            "event": payload.get("event") or "unknown",
        }

        if not event_payload["name"]:
            return

        resp = requests.post(url, json=event_payload, timeout=2)
        if resp.status_code >= 400:
            frappe.logger("titan_telegram").warning(
                "LCE webhook failed: status=%s body=%s",
                resp.status_code,
                (resp.text or "")[:240],
            )
    except Exception:
        # Warning level yetarli — webhook best-effort.
        frappe.logger("titan_telegram").warning(
            "LCE webhook request error:\n%s", frappe.get_traceback()
        )


def notify_stock_entry(doc, method):
    """Backward-compatible alias."""
    on_stock_entry_event(doc, method)


def notify_batch_update(doc, method):
    """Reserved for future hooks."""
    return None


def cleanup_old_sessions():
    """Daily cleanup of expired sessions."""
    frappe.db.sql(
        """
        DELETE FROM `tabTelegram Session`
        WHERE modified < DATE_SUB(NOW(), INTERVAL 30 DAY)
        AND status = 'Expired'
        """
    )
    frappe.db.commit()
