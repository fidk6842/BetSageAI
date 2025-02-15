from typing import List, Dict, Any

def format_results(processed_data: Dict[str, Any]) -> str:
    """
    Updated formatter for market-specific recommendations
    """
    output = []
     
    if 'demo' in processed_data:
        return "\n".join([
            "⚡ DEMO RESULTS ⚡",
            *[f"• {item['match']} - {item['prediction']}" 
              for item in processed_data.get('demo', [])]
        ])
    
    
    def safe_get(item, key, default="N/A"):
        return str(item.get(key, default) or default).strip()
    
    def format_percentage(value: float) -> str:
        return f"{max(0, min(100, value * 100)):.0f}%"
    
    def format_odds(value: float) -> str:
        return f"{max(1, value):.2f}"
    
    def add_section(title: str, items: List[Dict], formatter: callable):
        if items:
            output.append(f"\n{title}")
            output.extend([f"• {formatter(item)}" for item in items])

    if 'error' in processed_data:
        return f"❌ Error: {processed_data['error']}"
    
    # ARIMA Market Analysis
    add_section(
        "📊 ARIMA Trend Recommendations",
        processed_data.get('arima', {}).values(),
        lambda x: (
            f"{safe_get(x, 'home_team')} vs {safe_get(x, 'away_team')}\n"
            f"  🎯 Market: {safe_get(x, 'recommended_market')} ({safe_get(x, 'recommended_team')})\n"
            f"  📈 Trend: {safe_get(x, 'trend').capitalize()} | Odds: {format_odds(x.get('current_odds', 0))}\n"
            f"  📉 Volatility: {float(x.get('volatility', 0)):.2f} | Rec: {safe_get(x, 'recommendation').replace('_', ' ').title()}"
        )
    )
    
    # Monte Carlo Simulations
    add_section(
        "🎲 Monte Carlo Value Picks",
        processed_data.get('simulation_results', []),
        lambda x: (
            f"{safe_get(x, 'home_team')} vs {safe_get(x, 'away_team')}\n"
            f"  🎯 Market: {safe_get(x, 'market')} ({safe_get(x, 'team')})\n"
            f"  📈 Odds: {format_odds(x.get('odds', 0))} | Win Prob: {format_percentage(x.get('win_probability', 0))}\n"
            f"  💰 Stake: {x.get('recommended_stake_pct', 0):.1f}% | Value: {safe_get(x, 'value_rating').title()}"
        )
    )
    
    # Kelly Criterion (updated formatting)
    add_section(
        "💰 Kelly Optimal Stakes",
        processed_data.get('recommended_parlays', []),
        lambda x: (
            f"{safe_get(x, 'home_team')} vs {safe_get(x, 'away_team')}\n"
            f"  📊 Market: {safe_get(x, 'market', 'N/A')} @ {format_odds(x.get('odds', 0))}\n"
            f"  💰 Stake: {x.get('recommended_stake_pct', 0):.1f}% | Edge: {x.get('edge_percentage', 0):.1f}%"
        )
    )
    
    # Arbitrage Opportunities
    add_section(
        "🔍 Arbitrage Opportunities",
        processed_data.get('arbitrage_opportunities', []),
        lambda x: (
            f"{safe_get(x, 'match_ids', 'Multiple')}\n"
            f"  💰 ROI: {format_percentage(x.get('potential_return', 0)/100)}\n"
            f"  📈 Markets: {safe_get(x, 'markets', 'N/A')}"
        )
    )
    
    # Value Bets (OCM)
    add_section(
        "🔎 Value Bet Recommendations",
        processed_data.get('value_bets', []),
        lambda x: (
            f"{safe_get(x, 'home_team')} vs {safe_get(x, 'away_team')}\n"
            f"  🏆 Market: {safe_get(x, 'recommended_market')}\n"
            f"  📈 Odds: {format_odds(x.get('best_odds', 0))} | Value: {safe_get(x, 'value_rating')}"
        )
    )
    
    return "\n".join(output) if output else "❌ No actionable insights found"