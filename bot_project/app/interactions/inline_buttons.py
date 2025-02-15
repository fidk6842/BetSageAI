from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class ButtonGenerator:
    def __init__(self):
        self.league_data = {
            'epl': ('🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League', 'soccer_epl'),
            'la_liga': ('🇪🇸 La Liga', 'soccer_spain_la_liga'),
            'bundesliga': ('🇩🇪 Bundesliga', 'soccer_germany_bundesliga'),
            'serie_a': ('🇮🇹 Serie A', 'soccer_italy_serie_a'),
            'ligue_1': ('🇫🇷 Ligue 1', 'soccer_france_ligue_one'),
            'champions': ('🏆 UCL', 'soccer_uefa_champions_league')
        }

        self.algorithm_data = {
            'arima': ('📈 ARIMA', 'Time Series Analysis'),
            'kelly': ('💰 Kelly', 'Stake Optimization'),
            'monte': ('🎲 Monte Carlo', 'Simulations'),
            'ipt': ('⚖️ IPT', 'Implied Probability'),
            'arb': ('🔀 Arbitrage', 'Opportunity Detection'),
            'value': ('📊 Value Bets', 'Odds Comparison')
        }

    def _create_grid(self, items, prefix):
        return [
            [InlineKeyboardButton(item[1][0], callback_data=f"{prefix}:{item[0]}") 
             for item in row]
            for row in [list(items)[i:i+2] for i in range(0, len(items), 2)]
        ]

    def main_menu(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⚽ Select League", callback_data="menu:leagues")],
            [InlineKeyboardButton("❓ Help Center", callback_data="menu:help")],
            [InlineKeyboardButton("🔄 Refresh Data", callback_data="action:refresh")]
        ])

    def league_selector(self):
        buttons = self._create_grid(self.league_data.items(), 'league')
        buttons.append([InlineKeyboardButton("🔙 Main Menu", callback_data="menu:main")])
        return InlineKeyboardMarkup(buttons)

    def algorithm_selector(self, paid_user: bool):
        if not paid_user:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Demo Analysis", callback_data="algo:demo")],
                [InlineKeyboardButton("💎 Upgrade", callback_data="payment:upgrade")]
            ])
        
        buttons = self._create_grid(self.algorithm_data.items(), 'algo')
        buttons.append([
            InlineKeyboardButton("🔙 Back", callback_data="menu:leagues"),
            InlineKeyboardButton("🏠 Home", callback_data="menu:main")
        ])
        return InlineKeyboardMarkup(buttons)

    def help_navigation(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Wager Guide", callback_data='tool:wager_guide'),
             InlineKeyboardButton("📖 Algorithm Docs", callback_data='tool:algo_docs')],
            [InlineKeyboardButton("🏠 Main Menu", callback_data='menu:main')]
        ])
    def admin_menu(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 User Management", callback_data="admin:users")],
            [InlineKeyboardButton("📊 Statistics", callback_data="admin:stats")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="menu:main")]
        ])

    def user_management_menu(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Verify User", callback_data="admin:verify")],
            [InlineKeyboardButton("🚫 Block User", callback_data="admin:block")],
            [InlineKeyboardButton("🔓 Unblock User", callback_data="admin:unblock")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin:menu")]
        ])