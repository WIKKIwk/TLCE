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
