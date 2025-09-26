# DaguerreBot
Telegram script to save images sent to it.

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and set your configuration:
     - `BOT_TOKEN`: Your Telegram bot token (get from @BotFather)
     - `SAVE_PATH`: Directory where images will be saved
     - `ALLOWED_USER_IDS`: (Optional) Comma-separated list of Telegram user IDs for security

3. **Run the bot:**
   ```bash
   uv run python daguerre_bot.py
   ```

## Configuration

The bot uses the following environment variables:

- `BOT_TOKEN` (required): Your Telegram bot token
- `SAVE_PATH` (optional): Path where images are saved (default: `/home/pi/received_images/`)
- `ALLOWED_USER_IDS` (optional): Comma-separated list of user IDs to restrict bot access

## Features

- Receives and saves images with timestamps
- Supports both compressed photos and uncompressed documents
- Status command to check disk space and image count
- Optional user restriction for security

### User ID Restrictions

To restrict the bot to specific users, set the `ALLOWED_USER_IDS` environment variable:

- **Single user**: `ALLOWED_USER_IDS=123456789`
- **Multiple users**: `ALLOWED_USER_IDS=123456789,987654321,555444333`
- **No restrictions** (allow all users): Leave `ALLOWED_USER_IDS` empty or unset

To find your Telegram user ID, message @userinfobot on Telegram.
