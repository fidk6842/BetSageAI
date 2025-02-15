from telegram import Update
from telegram.ext import ContextTypes
from app.interactions.inline_buttons import ButtonGenerator

buttons = ButtonGenerator()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /menu command.
    """
    await update.message.reply_text(
        "Choose an option from the menu:",
        reply_markup=buttons.league_buttons(),  # Assuming menu options are league selections
    )
