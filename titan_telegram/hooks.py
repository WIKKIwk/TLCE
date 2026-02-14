from . import __version__

app_name = "titan_telegram"
app_title = "Titan Telegram"
app_publisher = "Accord Team"
app_description = "Titan LCE monitor and ERP integration"
app_icon = "octicon octicon-radio-tower"
app_color = "blue"
app_email = "dev@accord.uz"
app_license = "MIT"
app_version = __version__

# Hooks
after_install = "titan_telegram.install.after_install"
after_migrate = "titan_telegram.workspace_utils.ensure_workspace"

# Scheduled Tasks (disabled; Telegram bot lives inside LCE)
scheduler_events = {}

# Document Events
# Stock Entry o'zgarganda LCE bridge cache'ni real-time yangilash uchun webhook yuboramiz.
doc_events = {
    "Stock Entry": {
        "after_insert": "titan_telegram.utils.on_stock_entry_event",
        "on_update": "titan_telegram.utils.on_stock_entry_event",
        "on_submit": "titan_telegram.utils.on_stock_entry_event",
        "on_cancel": "titan_telegram.utils.on_stock_entry_event",
    }
}
