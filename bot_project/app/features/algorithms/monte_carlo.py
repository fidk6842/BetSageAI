import numpy as np
from typing import List, Dict
from app.features.data_processing import ProcessedMatch

def simulate_outcomes(matches: List[ProcessedMatch], simulations: int = 10000) -> Dict[str, List[Dict]]:
    """
    Enhanced Monte Carlo simulation with market selection
    Returns: {simulation_results: [...]}
    """
    results = []
    
    for match in matches:
        try:
            best_market = None
            max_value = -1
            
            # Analyze all three markets
            for market in ['home', 'away', 'draw']:
                odds_key = f'{market}_odds'
                if not match.get(odds_key):
                    continue
                
                # Use median odds for simulation
                median_odds = np.median(match[odds_key])
                if median_odds < 1.1:  # Skip invalid odds
                    continue
                
                implied_prob = 1 / median_odds
                outcomes = np.random.binomial(1, implied_prob, simulations)
                win_rate = outcomes.mean()
                
                # Calculate value score
                value_score = win_rate * median_odds
                edge = value_score - 1
                
                if edge > max_value:
                    max_value = edge
                    kelly_stake = (edge / (median_odds - 1)) * 100 if edge > 0 else 0
                    best_market = {
                        'market': market.upper(),
                        'team': match[f'{market}_team'] if market != 'draw' else 'Draw',
                        'win_probability': round(win_rate, 2),
                        'odds': round(median_odds, 2),
                        'value_rating': 'good' if value_score > 1.05 else 'fair' if value_score > 1 else 'poor',
                        'recommended_stake_pct': round(kelly_stake, 1)
                    }

            if best_market and best_market['value_rating'] != 'poor':
                results.append({
                    'match_id': match['match_id'],
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    **best_market
                })
                
        except Exception as e:
            continue
            
    return {'simulation_results': results} if results else {'error': 'no_valuable_markets'}