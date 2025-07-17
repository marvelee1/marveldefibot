import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Configuration
BOT_TOKEN = "7901548275:AAEe1RCehwd8fL4_EeZtzQgx25uUSgpnw5M"
CHANNEL_USERNAME = "@YourChannel"  # REPLACE WITH YOUR ACTUAL CHANNEL
GROUP_USERNAME = "@YourGroup"      # REPLACE WITH YOUR ACTUAL GROUP
TWITTER_USERNAME = "@YourTwitter"  # REPLACE WITH YOUR ACTUAL TWITTER

# States for conversation
JOIN_STATE, SOLANA_STATE = range(2)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("Join Group", url=f"https://t.me/{GROUP_USERNAME[1:]}")],
        [InlineKeyboardButton("Follow Twitter", url=f"https://twitter.com/{TWITTER_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ I've Joined", callback_data="joined")]
    ]
    
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "To participate in our airdrop:\n"
        f"1. Join our channel: {CHANNEL_USERNAME}\n"
        f"2. Join our group: {GROUP_USERNAME}\n"
        f"3. Follow our Twitter: {TWITTER_USERNAME}\n\n"
        "Click ✅ after completing all steps:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return JOIN_STATE

async def handle_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎉 Thanks for joining!\n\n"
        "Please send your Solana wallet address now:"
    )
    return SOLANA_STATE

async def handle_solana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    solana_address = update.message.text.strip()
    user = update.effective_user
    
    # Basic validation (for testing only)
    if len(solana_address) < 32 or len(solana_address) > 44:
        await update.message.reply_text("⚠️ That doesn't look like a Solana address. Please try again:")
        return SOLANA_STATE
    
    # Log the submission
    logger.info(
        f"New TEST submission:\n"
        f"User: {user.id} | @{user.username}\n"
        f"Wallet: {solana_address}\n"
        "NOTE: This is a test - no verification or storage implemented"
    )
    
    await update.message.reply_text(
        "✅ Registration complete!\n\n"
        "You'll receive test tokens soon!\n\n"
        "Note: This is a TEST bot - no real tokens will be distributed."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main() -> None:
    # Create Application with simplified initialization
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            JOIN_STATE: [CallbackQueryHandler(handle_join, pattern="^joined$")],
            SOLANA_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_solana)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Start the bot
    if 'RENDER' in os.environ:
        # Render deployment settings
        port = int(os.environ.get('PORT', 8443))
        webhook_url = f"https://your-render-service.onrender.com/{BOT_TOKEN}"
        
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            url_path=BOT_TOKEN
        )
        logger.info(f"Running in WEBHOOK mode on Render: {webhook_url}")
    else:
        # Local development
        application.run_polling()
        logger.info("Running in POLLING mode (local development)")

if __name__ == "__main__":
    main()
