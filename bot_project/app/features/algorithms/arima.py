import numpy as np
from typing import List, Dict
from app.features.data_processing import ProcessedMatch

def analyze_odds_movement(matches: List[ProcessedMatch]) -> Dict[str, Dict]:
    """
    ARIMA analysis with market selection
    Returns: {match_id: {analysis}, ...}
    """
    results = {}
    
    for match in matches:
        try:
            market_analysis = {}
            
            # Analyze all available markets
            for market in ['home', 'away', 'draw']:
                odds_key = f'{market}_odds'
                if not match.get(odds_key) or len(match[odds_key]) < 3:
                    continue
                
                prices = match[odds_key]
                prices_array = np.array(prices)
                
                # Trend analysis
                window_size = min(3, len(prices))
                moving_avg = np.convolve(prices_array, np.ones(window_size)/window_size, mode='valid')
                trend = 'rising' if moving_avg[-1] > moving_avg[0] else 'falling'
                
                market_analysis[market] = {
                    'current_odds': round(float(np.mean(prices_array[-3:])), 2),
                    'volatility': round(float(np.std(prices_array)), 3),
                    'trend': trend,
                    'trend_strength': abs(moving_avg[-1] - moving_avg[0])
                }
            
            if not market_analysis:
                continue
                
            # Select best market
            best_market = max(market_analysis.items(), 
                            key=lambda x: (x[1]['trend_strength'], -x[1]['volatility']))
            
            results[match['match_id']] = {
                'home_team': match['home_team'],
                'away_team': match['away_team'],
                'recommended_market': best_market[0].upper(),
                'recommended_team': match[f'{best_market[0]}_team'] if best_market[0] != 'draw' else 'Draw',
                'current_odds': best_market[1]['current_odds'],
                'trend': best_market[1]['trend'],
                'volatility': best_market[1]['volatility'],
                'recommendation': 'strong_buy' if (
                    best_market[1]['trend'] == 'rising' and 
                    best_market[1]['volatility'] > 0.3
                ) else 'hold'
            }
            
        except Exception as e:
            continue
            
    return {'arima': results} if results else {'error': 'no_clear_trends'}