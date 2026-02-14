# Titan Telegram

Telegram Bot Integration for Titan Warehouse RFID System

## Features

- Device registration via Telegram
- Batch management commands
- Real-time weight notifications
- Secure token handling (auto-delete from chat)
- ERPNext integration

## Installation

```bash
bench get-app titan_telegram
bench --site site1.local install-app titan_telegram
```

## Configuration

1. Go to Titan Telegram Settings in ERPNext
2. Enter Bot Token from @BotFather
3. Set Webhook URL
4. Enable the bot

## Commands

- `/start` - Initialize device
- `/status` - Check device status
- `/batch start` - Start new batch
- `/batch stop` - Stop current batch
- `/product` - Select product
- `/help` - Show help

## Fast Draft Cache API

Use this ERPNext method to fetch open Stock Entry drafts for RFID cache in one call:

- Method: `titan_telegram.api.get_open_stock_entry_drafts_fast`
- URL: `/api/method/titan_telegram.api.get_open_stock_entry_drafts_fast`

Example:

```bash
curl -H "Authorization: token <API_KEY>:<API_SECRET>" \
  "https://your-erp.example.com/api/method/titan_telegram.api.get_open_stock_entry_drafts_fast?modified_since=2026-02-13%2000:00:00&limit=5000&include_items=1&only_with_epc=1"
```

Response includes:

- `count_drafts`
- `count_epcs`
- `max_modified` (cursor for next incremental fetch)
- `drafts[]` with `name`, warehouses, `epcs[]`, and optional `items[]`

Ultra-minimum payload (only EPC list):

```bash
curl -H "Authorization: token <API_KEY>:<API_SECRET>" \
  "https://your-erp.example.com/api/method/titan_telegram.api.get_open_stock_entry_drafts_fast?modified_since=2026-02-13%2000:00:00&limit=5000&only_with_epc=1&compact=1&epc_only=1"
```

Returns: `epcs[]`, `count_epcs`, `max_modified` (and empty `drafts[]`).
