from . import __version__

app_name = "titan_telegram"
app_title = "Titan Telegram"
app_publisher = "Accord Team"
app_description = "Telegram Bot for Titan Warehouse System"
app_icon = "octicon octicon-radio-tower"
app_color = "blue"
app_email = "dev@accord.uz"
app_license = "MIT"
app_version = __version__

# Hooks
after_install = "titan_telegram.install.after_install"

# Scheduled Tasks
scheduler_events = {
    "all": [
        "titan_telegram.telegram_bot.process_updates"
    ],
    "daily": [
        "titan_telegram.utils.cleanup_old_sessions"
    ]
}

# Document Events
doc_events = {
    "Stock Entry": {
        "on_submit": "titan_telegram.utils.notify_stock_entry"
    },
    "Batch": {
        "on_update": "titan_telegram.utils.notify_batch_update"
    }
}
