#!/usr/bin/env python3
"""
Telegram Image Bot for Raspberry Pi
Receives images and saves them locally with timestamps
"""

import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
SAVE_PATH = os.getenv("SAVE_PATH", "/home/pi/received_images/")  # Default fallback
ALLOWED_USER_IDS_STR = os.getenv("ALLOWED_USER_IDS")
ALLOWED_USER_IDS = None
if ALLOWED_USER_IDS_STR:
    # Parse comma-separated user IDs and convert to integers
    try:
        ALLOWED_USER_IDS = [
            int(uid.strip()) for uid in ALLOWED_USER_IDS_STR.split(",") if uid.strip()
        ]
    except ValueError:
        print("❌ Error: ALLOWED_USER_IDS must be comma-separated integers")
        ALLOWED_USER_IDS = None

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def ensure_save_directory():
    """Create the save directory if it doesn't exist"""
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
        logger.info(f"Created directory: {SAVE_PATH}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Send me images and I'll save them to your Raspberry Pi.\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/status - Check bot status\n"
        "/help - Show help"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Just send me any image and I'll save it with a timestamp.\n"
        "Supported formats: JPG, PNG, GIF, WebP\n"
        f"Images are saved to: {SAVE_PATH}"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot status and disk space"""
    try:
        # Check if save directory exists and is writable
        ensure_save_directory()

        # Get disk usage
        statvfs = os.statvfs(SAVE_PATH)
        free_space_mb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024)

        # Count existing images
        image_count = len(
            [
                f
                for f in os.listdir(SAVE_PATH)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))
            ]
        )

        status_msg = (
            f"✅ Bot is running\n"
            f"📁 Save path: {SAVE_PATH}\n"
            f"🖼 Images saved: {image_count}\n"
            f"💾 Free space: {free_space_mb:.1f} MB"
        )

        await update.message.reply_text(status_msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Error checking status: {str(e)}")


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received images"""

    # Security check (optional)
    if ALLOWED_USER_IDS and update.effective_user.id not in ALLOWED_USER_IDS:
        await update.message.reply_text("❌ Unauthorized user")
        return

    try:
        # Ensure save directory exists
        ensure_save_directory()

        # Get the largest photo size
        photo = update.message.photo[-1]

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = "jpg"  # Telegram photos are usually JPG
        filename = f"img_{timestamp}_{photo.file_id[:8]}.{file_extension}"
        filepath = os.path.join(SAVE_PATH, filename)

        # Download the file
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(filepath)

        # Get file size
        file_size_kb = os.path.getsize(filepath) / 1024

        # Send confirmation
        await update.message.reply_text(
            f"✅ Image saved!\n📁 {filename}\n📊 Size: {file_size_kb:.1f} KB"
        )

        logger.info(f"Saved image: {filename} ({file_size_kb:.1f} KB)")

    except Exception as e:
        logger.error(f"Error saving image: {e}")
        await update.message.reply_text(f"❌ Error saving image: {str(e)}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image documents (non-compressed images)"""

    # Security check (optional)
    if ALLOWED_USER_IDS and update.effective_user.id not in ALLOWED_USER_IDS:
        await update.message.reply_text("❌ Unauthorized user")
        return

    document = update.message.document

    # Check if it's an image
    if not document.mime_type or not document.mime_type.startswith("image/"):
        await update.message.reply_text("❌ Please send only image files")
        return

    try:
        # Ensure save directory exists
        ensure_save_directory()

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = document.file_name or "image"
        name_parts = original_name.rsplit(".", 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            filename = f"{name}_{timestamp}.{ext}"
        else:
            filename = f"{original_name}_{timestamp}"

        filepath = os.path.join(SAVE_PATH, filename)

        # Download the file
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(filepath)

        # Get file size
        file_size_kb = os.path.getsize(filepath) / 1024

        # Send confirmation
        await update.message.reply_text(
            f"✅ Document saved!\n📁 {filename}\n📊 Size: {file_size_kb:.1f} KB"
        )

        logger.info(f"Saved document: {filename} ({file_size_kb:.1f} KB)")

    except Exception as e:
        logger.error(f"Error saving document: {e}")
        await update.message.reply_text(f"❌ Error saving document: {str(e)}")


async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-image messages"""
    await update.message.reply_text(
        "Please send me an image! I can save:\n"
        "📷 Photos (compressed)\n"
        "🖼 Image documents (uncompressed)\n"
        "\nUse /help for more info."
    )


def main():
    """Start the bot."""

    # Validate token
    if not BOT_TOKEN:
        print("❌ Please set your BOT_TOKEN in the .env file!")
        return

    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))

    # Handle images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    # Handle other messages
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other_messages)
    )

    # Ensure save directory exists
    ensure_save_directory()

    print("🤖 Bot starting...")
    print(f"📁 Images will be saved to: {SAVE_PATH}")
    if ALLOWED_USER_IDS:
        user_list = ", ".join(str(uid) for uid in ALLOWED_USER_IDS)
        print(f"🔒 Restricted to user IDs: {user_list}")
    else:
        print("🌐 Open to all users (no restrictions)")
    print("🔧 Press Ctrl+C to stop")

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
