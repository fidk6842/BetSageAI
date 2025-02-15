from telegram import Update
from telegram.ext import ContextTypes
from app.interactions.inline_buttons import ButtonGenerator

buttons = ButtonGenerator()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /help command.
    """
    await update.message.reply_text(
        "Help: Use the buttons to navigate between menus. If you're unsure, return to the main menu.",
        reply_markup=buttons.help_buttons(),
    )
