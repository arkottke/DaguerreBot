# DaguerreBot
Telegram script to save images sent to it.

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

## Configuration

The bot uses the following environment variables:

- `BOT_TOKEN` (required): Your Telegram bot token
- `SAVE_PATH` (optional): Path where images are saved (default: `/home/pi/received_images/`)
- `ALLOWED_USER_IDS` (optional): Comma-separated list of user IDs to restrict bot access

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

## Running as a System Service

To run the bot automatically as a system service (recommended for production):

1. **Install the service:**
   ```bash
   # Copy the service file to systemd directory
   sudo cp daguerre-bot.service /etc/systemd/system/
   
   # Reload systemd to recognize the new service
   sudo systemctl daemon-reload
   ```

2. **Enable and start the service:**
   ```bash
   # Enable the service to start automatically on boot
   sudo systemctl enable daguerre-bot.service
   
   # Start the service immediately
   sudo systemctl start daguerre-bot.service
   ```

3. **Manage the service:**
   ```bash
   # Check service status
   sudo systemctl status daguerre-bot.service
   
   # View service logs
   sudo journalctl -u daguerre-bot.service -f
   
   # Stop the service
   sudo systemctl stop daguerre-bot.service
   
   # Restart the service
   sudo systemctl restart daguerre-bot.service
   
   # Disable auto-start on boot
   sudo systemctl disable daguerre-bot.service
   ```

4. **Update the service:**
   If you modify the bot code or configuration:
   ```bash
   # Restart the service to apply changes
   sudo systemctl restart daguerre-bot.service
   
   # Or if you modified the .service file:
   sudo cp daguerre-bot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl restart daguerre-bot.service
   ```

**Note:** The service is configured to automatically restart if the bot crashes and will start automatically on system boot.