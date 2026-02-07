"""
API Endpoints for Telegram Bot Integration
"""
import frappe
from frappe import _
import json
import requests
from frappe.utils import now_datetime, add_to_date
from frappe.core.doctype.user.user import generate_keys
from frappe.utils import get_url

@frappe.whitelist(allow_guest=True)
def webhook():
    """Telegram Bot Webhook Endpoint"""
    try:
        return {
            "ok": False,
            "error": "Webhook disabled. Telegram bot is handled by LCE."
        }
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


@frappe.whitelist()
def get_lce_status():
    """Fetch aggregated LCE status for dashboards."""
    try:
        settings = frappe.get_doc("LCE Settings")
        base_url = (settings.lce_url or "").rstrip("/")
        if not base_url:
            return {"ok": False, "error": "LCE URL is not configured"}

        resp = requests.get(f"{base_url}/api/status", timeout=5)
        if resp.status_code >= 400:
            return {"ok": False, "error": f"LCE status failed: {resp.status_code}"}
        return resp.json()
    except Exception as e:
        frappe.log_error(f"LCE status error: {str(e)}")
        return {"ok": False, "error": str(e)}


@frappe.whitelist()
def get_bot_health():
    """Return basic health metrics for dashboard UI (via LCE)."""
    try:
        lce = get_lce_status()

        now = now_datetime()
        since_24h = add_to_date(now, hours=-24)

        last_log = frappe.db.get_value(
            "Telegram Log",
            filters={},
            fieldname="creation",
            order_by="creation desc",
        )

        error_count = frappe.db.count(
            "Telegram Log",
            filters={"status": "Error", "creation": (">", since_24h)},
        )

        total_logs = frappe.db.count("Telegram Log")
        active_sessions = frappe.db.count("Telegram Session", filters={"status": "Active"})
        online_devices = frappe.db.count("Telegram Device", filters={"status": "Online"})
        total_devices = frappe.db.count("Telegram Device")

        return {
            "ok": True,
            "lce": lce,
            "last_log": last_log,
            "error_count_24h": error_count,
            "total_logs": total_logs,
            "active_sessions": active_sessions,
            "online_devices": online_devices,
            "total_devices": total_devices,
        }
    except Exception as e:
        frappe.log_error(f"Bot health error: {str(e)}")
        return {"ok": False, "error": str(e)}


@frappe.whitelist()
def generate_current_user_token():
    """Generate API key/secret for current user and store in LCE Settings."""
    try:
        frappe.only_for("System Manager")
        user = frappe.session.user

        result = generate_keys(user)
        api_key = result.get("api_key")
        api_secret = result.get("api_secret")
        api_key, api_secret = _normalize_key_secret(api_key, api_secret)
        token = f"{api_key}:{api_secret}" if api_key and api_secret else ""
        erp_url = get_url()

        frappe.db.set_value(
            "LCE Settings",
            "LCE Settings",
            {
                "erp_url": erp_url,
                "erp_user": user,
                "erp_api_key": api_key,
                "erp_api_secret": api_secret,
                "erp_api_token": token,
            },
            update_modified=False,
        )
        frappe.db.commit()

        return {
            "ok": True,
            "user": user,
            "erp_url": erp_url,
            "api_key": api_key,
            "api_secret": api_secret,
            "token": token,
        }
    except Exception as e:
        frappe.log_error(f"Generate API token error: {str(e)}")
        return {"ok": False, "error": str(e)}


@frappe.whitelist()
def get_lce_secrets():
    """Return decrypted API secrets for copy-to-clipboard."""
    try:
        frappe.only_for("System Manager")
        settings = frappe.get_doc("LCE Settings")
        from frappe.utils.password import get_decrypted_password

        api_secret = get_decrypted_password("LCE Settings", "LCE Settings", "erp_api_secret", raise_exception=False)
        api_token = get_decrypted_password("LCE Settings", "LCE Settings", "erp_api_token", raise_exception=False)

        api_key = settings.erp_api_key
        api_key, api_secret = _normalize_key_secret(api_key, api_secret)
        if api_key != settings.erp_api_key or (api_secret and api_secret != settings.erp_api_secret):
            frappe.db.set_value(
                "LCE Settings",
                "LCE Settings",
                {"erp_api_key": api_key, "erp_api_secret": api_secret},
                update_modified=False,
            )
            frappe.db.commit()
        if not api_token and api_key and api_secret:
            api_token = f"{api_key}:{api_secret}"
            frappe.db.set_value(
                "LCE Settings",
                "LCE Settings",
                "erp_api_token",
                api_token,
                update_modified=False,
            )
            frappe.db.commit()

        return {
            "ok": True,
            "lce_url": settings.lce_url,
            "erp_url": settings.erp_url,
            "api_key": api_key,
            "api_secret": api_secret or "",
            "api_token": api_token or "",
        }
    except Exception as e:
        frappe.log_error(f"Get LCE secrets error: {str(e)}")
        return {"ok": False, "error": str(e)}


@frappe.whitelist()
def push_erp_config_to_lce():
    """Push ERP URL + token from LCE Settings to LCE bridge config."""
    try:
        settings = frappe.get_doc("LCE Settings")
        lce_url = (settings.lce_url or "").strip().rstrip("/")
        if not lce_url:
            detect = detect_lce_url()
            if detect.get("ok"):
                lce_url = detect.get("lce_url", "").strip().rstrip("/")
                if lce_url:
                    frappe.db.set_value(
                        "LCE Settings",
                        "LCE Settings",
                        "lce_url",
                        lce_url,
                        update_modified=False,
                    )
                    frappe.db.commit()
            else:
                return {"ok": False, "error": "LCE URL is not configured"}

        erp_url = (settings.erp_url or "").strip() or get_url()
        token = (settings.erp_api_token or "").strip()
        if not token:
            if settings.erp_api_key and settings.erp_api_secret:
                token = f"{settings.erp_api_key}:{settings.erp_api_secret}"
        if not token:
            return {"ok": False, "error": "API token not set. Generate token first."}

        payload = {"erp_url": erp_url, "erp_token": token}
        resp = requests.post(f"{lce_url}/api/config", json=payload, timeout=5)
        if resp.status_code >= 400:
            return {"ok": False, "error": f"LCE config failed: {resp.status_code}"}

        return {"ok": True}
    except Exception as e:
        frappe.log_error(f"Push ERP config error: {str(e)}")
        return {"ok": False, "error": str(e)}


@frappe.whitelist()
def detect_lce_url():
    """Best-effort detection of local LCE base URL."""
    try:
        candidates = [
            "http://127.0.0.1:4000",
            "http://localhost:4000",
        ]
        for base in candidates:
            try:
                resp = requests.get(f"{base}/api/health", timeout=1.5)
                if resp.status_code < 400:
                    return {"ok": True, "lce_url": base}
            except Exception:
                continue
        return {"ok": False, "error": "LCE not reachable on default ports"}
    except Exception as e:
        frappe.log_error(f"Detect LCE URL error: {str(e)}")
        return {"ok": False, "error": str(e)}


def _normalize_key_secret(api_key, api_secret):
    api_key = api_key or ""
    api_secret = api_secret or ""
    if ":" in api_key:
        key_part, secret_part = api_key.split(":", 1)
        if not api_secret:
            api_secret = secret_part
        api_key = key_part
    return api_key, api_secret
