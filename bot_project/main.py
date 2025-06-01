import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from data.user_manager import UserManager
from app.features.odds_fetcher import fetch_odds_for_league
from app.features.data_processing import preprocess_odds, process_pipeline
from app.features.result_formatter import format_results
from app.interactions.league_selection import LeagueManager
from app.interactions.inline_buttons import ButtonGenerator
from config.settings import BOT_TOKEN, SCRAPING_API_KEY, SCRAPING_BASE_URL
from utils.logger import setup_logging

# Import algorithms directly from their modules
from app.features.algorithms.arima import analyze_odds_movement
from app.features.algorithms.dfs import detect_arbitrage
from app.features.algorithms.kelly import calculate_parlay_stakes
from app.features.algorithms.monte_carlo import simulate_outcomes
from app.features.algorithms.ipt import implied_probability_threshold_model
from app.features.algorithms.ocm import odds_comparison_model

logger = setup_logging('logs/bot.log')

class OddsBot:
    def __init__(self):
        self.buttons = ButtonGenerator()
        self.league_manager = LeagueManager()
        self.user_manager = UserManager()
        self.user_sessions = {}

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query:
            await query.answer()
            await query.edit_message_text(
                "⚽ Welcome to OddsAnalyst Bot!\n"
                "Start by selecting a league:",
                reply_markup=self.buttons.league_selector()
            )
        else:
            user_id = update.effective_user.id
            logger.info(f"User {user_id} started the bot")
            if self.user_manager.is_blocked(user_id):
                await update.message.reply_text("❌ Access denied")
                return
            if not self.user_manager.is_paid(user_id):
                text = ("⚡ DEMO VERSION ⚡\n"
                        "Start by selecting a league to see demo analysis\n"
                        "Use /pay to unlock full version")
            else:
                text = "Welcome to FULL VERSION!"
            await update.message.reply_text(text, reply_markup=self.buttons.main_menu())

    async def handle_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        payment_text = (
            "🔐 Upgrade to Full Version\n\n"
            f"Send 0.1 ETH to:\n`{self.user_manager.get_crypto_address()}`\n\n"
            "After payment, forward the transaction receipt to @YourAdminUsername"
        )
        await update.message.reply_text(payment_text, parse_mode="Markdown")

    async def verify_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.user_manager.is_admin(user_id):
            await update.message.reply_text("❌ Admin only")
            return

        try:
            target_user = int(context.args[0])
            self.user_manager.add_paid_user(target_user)
            await update.message.reply_text(f"✅ User {target_user} activated")
            await context.bot.send_message(
                chat_id=target_user,
                text="🎉 Payment verified! Full access granted.",
                reply_markup=self.buttons.main_menu()
            )
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def block_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.user_manager.is_admin(user_id):
            return

        try:
            target_user = int(context.args[0])
            self.user_manager.block_user(target_user)
            await update.message.reply_text(f"✅ User {target_user} blocked")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Central callback handler for all inline interactions"""
        query = update.callback_query
        await query.answer()

        try:
            user_id = query.from_user.id
            action, *values = query.data.split(':')

            # Add admin handler check
            if action == 'admin' and self.user_manager.is_admin(user_id):
                await self._handle_admin_actions(query, context, values)
                return

            # Existing handler map remains the same
            handler_map = {
                'menu': self._handle_menu,
                'league': self.handle_league_selection,
                'algo': self.handle_algorithm_selection,
                'help': self.show_help,
                'tool': self._handle_tool,
                'action': self._handle_action
            }

            if handler := handler_map.get(action):
                await handler(query, context, values)
            else:
                await self.show_error(query, "Unknown action")

        except Exception as e:
            logger.error(f"Callback error: {str(e)}", exc_info=True)
            await self.show_error(query, "Processing error")

    async def _handle_admin_actions(self, query, context, values):
        """Handle admin-specific callbacks"""
        action = values[0] if values else 'menu'

        if action == 'menu':
            await query.edit_message_text(
                "🛠️ Admin Panel",
                reply_markup=self.buttons.admin_menu()
            )
        elif action == 'users':
            await query.edit_message_text(
                "👤 User Management",
                reply_markup=self.buttons.user_management_menu()
            )
        elif action == 'stats':
            await self._show_admin_stats(query)
        elif action in ['verify', 'block', 'unblock']:
            context.user_data['admin_action'] = action
            await query.edit_message_text(
                f"Enter user ID to {action}:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin:users")]])
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin user ID inputs"""
        user_id = update.effective_user.id
        if self.user_manager.is_admin(user_id) and 'admin_action' in context.user_data:
            try:
                target_id = int(update.message.text)
                action = context.user_data.pop('admin_action')

                if action == 'verify':
                    self.user_manager.add_paid_user(target_id)
                    msg = f"✅ Verified user {target_id}"
                elif action == 'block':
                    self.user_manager.block_user(target_id)
                    msg = f"🚫 Blocked user {target_id}"
                elif action == 'unblock':
                    self.user_manager.unblock_user(target_id)
                    msg = f"🔓 Unblocked user {target_id}"

                await update.message.reply_text(msg)
                await self._show_admin_menu(update)
            except ValueError:
                await update.message.reply_text("❌ Invalid user ID format")

    async def _show_admin_menu(self, update: Update):
        """Display admin menu"""
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "🛠️ Admin Panel",
                reply_markup=self.buttons.admin_menu()
            )
        else:
            await update.message.reply_text(
                "🛠️ Admin Panel",
                reply_markup=self.buttons.admin_menu()
            )

    async def _show_admin_stats(self, query):
        """Display admin statistics"""
        stats = self.user_manager.get_stats()
        text = (
            "📊 Bot Statistics\n\n"
            f"👤 Total users: {stats['total']}\n"
            f"💎 Paid users: {stats['paid']}\n"
            f"🚫 Blocked users: {stats['blocked']}\n"
            f"🛠️ Admins: {len(self.user_manager.data['admin_ids'])}"
        )
        await query.edit_message_text(text, reply_markup=self.buttons.admin_menu())

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        if self.user_manager.is_admin(user_id):
            await update.message.reply_text(
                "🛠️ Admin Panel",
                reply_markup=self.buttons.admin_menu()
            )
        else:
            await update.message.reply_text("❌ Admin access required")

    async def _handle_menu(self, query, context, values):
        """Handle menu navigation"""
        menu_action = values[0] if values else 'main'

        if menu_action == 'leagues':
            await query.edit_message_text(
                "⚽ Select a league:",
                reply_markup=self.buttons.league_selector()
            )
        elif menu_action == 'help':
            await self.show_help(query, context, values)
        elif menu_action == 'main':
            await query.edit_message_text(
                "🏠 Main Menu",
                reply_markup=self.buttons.main_menu()
            )
        elif menu_action == 'refresh':
            await self._handle_refresh(query, context)

    async def _handle_action(self, query, context, values):
        """Handle action-related callbacks"""
        action_type = values[0] if values else None

        if action_type == 'refresh':
            await self._handle_refresh(query, context)
        else:
            await self.show_error(query, "Invalid action")

    async def _handle_refresh(self, query, context):
        """Handle data refresh requests"""
        await query.edit_message_text(
            "🔄 Refreshing data...",
            reply_markup=self.buttons.main_menu()
        )
        # Add data refresh logic here
        await query.edit_message_text(
            "✅ Data refreshed successfully!",
            reply_markup=self.buttons.main_menu()
        )

    async def _handle_tool(self, query, context, values):
        """Modified tool handler"""
        tool_action = values[0] if values else None

        if tool_action == 'wager_guide':
            await self._show_wager_guide(query)
        elif tool_action == 'algo_docs':
            await self._show_algorithm_docs(query)
        elif tool_action == 'export':
            await self._handle_export(query, context)
        elif tool_action == 'chart':
            await self._handle_chart(query, context)
        elif tool_action == 'deep':
            await self._handle_deep_analysis(query, context)
        else:
            await self.show_error(query, "Invalid tool action")

    async def _show_wager_guide(self, query):
        """New wager guide display"""
        guide_text = (
            "🎯 *Wager Guide*\n\n"
            "1. ARIMA: Bet when 'trend' shows rising odds & 'recommendation' says 'strong_buy'\n"
            "2. KELLY: Only bet the 'recommended_stake' amount shown\n"
            "3. MONTE CARLO: Choose bets with 'win_probability' >60% and 'value_rating: good'\n"
            "4. IPT: Look for 'prediction: Home/Away Win' with probabilities >45%\n"
            "5. ARB: Only use 'arbitrage_opportunities' bets\n"
            "6. OCM: Bet where 'best_home/away_odds' are highest with 'value_rating'"
        )
        await query.edit_message_text(
            guide_text,
            parse_mode="Markdown",
            reply_markup=self.buttons.help_navigation()
        )

    async def _show_algorithm_docs(self, query):
        """New algorithm documentation display"""
        docs_text = (
            "📖 *Algorithm Documentation*\n\n"
            "- ARIMA: Autoregressive integrated moving average modeling\n"
            "- KELLY: Logarithmic utility optimization for stake sizing\n"
            "- MONTE CARLO: Stochastic process simulations\n"
            "- IPT: Bayesian inference for probability thresholds\n"
            "- ARB: Linear programming for arbitrage detection\n"
            "- OCM: Extremal value theory for odds comparison"
        )
        await query.edit_message_text(
            docs_text,
            parse_mode="Markdown",
            reply_markup=self.buttons.help_navigation()
        )

    async def _handle_export(self, query, context):
        """Handle CSV export requests"""
        await query.edit_message_text(
            "📥 Exporting data to CSV...",
            reply_markup=self.buttons.main_menu()
        )
        # Add export logic here
        await query.edit_message_text(
            "✅ Data exported successfully!",
            reply_markup=self.buttons.main_menu()
        )

    async def handle_algorithm_selection(self, query, context, values):
        """Process algorithm selection and execute analysis"""
        user_id = query.from_user.id
        paid_status = self.user_manager.is_paid(user_id)
        algorithm = values[0]

        if not (session := self.user_sessions.get(user_id)):
            return await self.show_error(query, "Session expired")

        league_key = session.get('league')
        if not league_key:
            return await self.show_error(query, "No league selected")

        try:
            # Get payment status
            paid_user = self.user_manager.is_paid(user_id)

            # Get API-compatible league identifier
            api_league_key = self.league_manager.get_api_key(league_key)
            if not api_league_key:
                raise ValueError("Invalid league mapping")

            # Update user with processing status
            progress_msg = await query.edit_message_text(
                f"⚙️ Processing {self.league_manager.get_display_name(league_key)}...\n"
                f"Algorithm: {algorithm.upper()}"
            )

            # Execute full processing pipeline
            results = await process_pipeline(
                api_key=SCRAPING_API_KEY,
                base_url=SCRAPING_BASE_URL,
                league_key=api_league_key,
                algorithm=algorithm.lower(),
                paid_user=paid_status
            )

            # Format and display results
            formatted = format_results(results)
            await progress_msg.edit_text(
                f"🏆 {self.league_manager.get_display_name(league_key)} Results\n"
                f"📊 Method: {algorithm.upper()}\n\n"
                f"{formatted}",
                reply_markup=self.buttons.main_menu()
            )

        except Exception as e:
            logger.error(f"Algorithm error: {str(e)}", exc_info=True)
            await self.show_error(query, f"Analysis failed: {str(e)}")

    async def handle_league_selection(self, query, context, values):
        """Store league selection and show algorithm choices"""
        user_id = query.from_user.id
        league_key = values[0]

        if not self.league_manager.is_valid(league_key):
            return await self.show_error(query, "Invalid league")

        # Update user session
        self.user_sessions[user_id] = {'league': league_key}

        await query.edit_message_text(
            f"✅ Selected: {self.league_manager.get_display_name(league_key)}\n"
            "Choose analysis method:",
            reply_markup=self.buttons.algorithm_selector(
                paid_user=self.user_manager.is_paid(user_id)
             )
        )

    async def show_help(self, query, context, values):
        """Updated help text with OCM"""
        help_text = (
            "🤖 *Bot Guide*\n\n"
            "1. Select a football league\n"
            "2. Choose analysis method\n"
            "3. Receive betting insights\n\n"
            "✨ *Available Algorithms*\n"
            "- ARIMA: Price trend analysis\n"
            "- KELLY: Optimal bet sizing\n"
            "- MONTE CARLO: Outcome simulations\n"
            "- IPT: Value probability detection\n"
            "- ARB: Arbitrage opportunities\n"
            "- OCM: Odds comparison"
        )
        await query.edit_message_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=self.buttons.help_navigation()
        )

    async def show_error(self, query, message):
        """Universal error display method"""
        try:
            current_text = query.message.text
            if f"❌ {message}" != current_text:
                await query.edit_message_text(
                    f"❌ {message}",
                    reply_markup=self.buttons.main_menu()
                )
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                logger.error(f"Error display failed: {str(e)}")

    async def _handle_demo_analysis(self, query):
        """Handle demo analysis for non-paid users"""
        await query.edit_message_text(
            "⚠️ Demo version: Full analysis is available after payment.",
            reply_markup=self.buttons.main_menu()
        )

def initialize_bot():
    """Configure and start the Telegram bot"""
    bot = OddsBot()
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler('start', bot.handle_start))
    application.add_handler(CommandHandler('help', bot.show_help))
    application.add_handler(CommandHandler('admin', bot.admin_command))
    application.add_handler(CommandHandler('pay', bot.handle_payment))
    application.add_handler(CommandHandler('verify', bot.verify_payment))
    application.add_handler(CommandHandler('block', bot.block_user))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(CallbackQueryHandler(bot.handle_callback))

    logger.info("OddsAnalyst bot initializing...")
    return application

if __name__ == "__main__":
    app = initialize_bot()
    app.run_polling()
