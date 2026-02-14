# Telegram Companion Bot (18+)

## Overview
A Telegram bot built with Python (aiogram 3.x) that provides virtual companion conversations for adult audiences. Uses OpenAI Platform API (gpt-4o-mini) for AI-powered chat responses. Monetized through Telegram Stars payments.

## Architecture
- **Framework**: aiogram 3.x (polling mode, no webhooks)
- **AI**: OpenAI Platform API (gpt-4o-mini) via OPENAI_API_KEY
- **Storage**: Local JSON file (`data/users.json`)
- **Payments**: Telegram Stars (75 Stars = 10 min access)

## Project Structure
```
main.py                 - Entry point
src/
  __init__.py
  bot.py                - Main bot handlers (age gate, chat, payments, menu, admin)
  config.py             - Configuration constants
  companions.py         - Virtual companion definitions
  storage.py            - JSON-based user data storage
  ai_engine.py          - OpenAI integration, mood system, emoji logic
data/
  users.json            - User data (auto-created, gitignored)
```

## Key Features
- Age gate (18+ confirmation required before any interaction)
- Free funnel: 2 companions, 2 AI replies each
- Telegram Stars payments for extended access
- Mood system (warm/playful/calm/dreamy) with emoji injection
- Photo sharing with cooldown logic
- Bonus access for returning users
- Admin /grant command
- Token-saving short message detection

## Environment Variables
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `ADMIN_ID` - Telegram user ID of the bot owner
- `OPENAI_API_KEY` - Your OpenAI Platform API key

## Running
```bash
python main.py
```
