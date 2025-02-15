from telegram import Update
from telegram.ext import ContextTypes
from app.interactions.inline_buttons import ButtonGenerator

buttons = ButtonGenerator()

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_manager = UserManager()
    buttons = ButtonGenerator()
    user_id = update.effective_user.id
    
    if user_manager.is_blocked(user_id):
        await update.message.reply_text("❌ Access denied")
        return
        
    reply_markup = buttons.main_menu()
    
    if not user_manager.is_paid(user_id):
        reply_markup = buttons.algorithm_selector(paid_user=False)

    await update.message.reply_text(
        "Welcome to BetSageAIBot! Choose an option:",
        reply_markup=reply_markup
    )
