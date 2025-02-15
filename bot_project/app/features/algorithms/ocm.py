from typing import List, Dict
from app.features.data_processing import ProcessedMatch

def odds_comparison_model(matches: List[ProcessedMatch]) -> Dict[str, List[Dict]]:
    value_bets = []
    
    for match in matches:
        try:
            best_home = max((odds for odds in match['home_odds'] if odds is not None), default=None)
            best_away = max((odds for odds in match['away_odds'] if odds is not None), default=None)
            
            # Find bookmakers offering best odds
            home_bookmakers = [bm for bm, odds in match['bookmakers'].items() 
                             if odds['home'] == best_home]
            away_bookmakers = [bm for bm, odds in match['bookmakers'].items() 
                             if odds['away'] == best_away]
            
            value_bets.append({
                'match_id': match['match_id'],
                'home_team': match['home_team'],
                'away_team': match['away_team'],
                'best_home_odds': best_home,
                'best_away_odds': best_away,
                'home_bookmaker': home_bookmakers[0] if home_bookmakers else 'N/A',
                'away_bookmaker': away_bookmakers[0] if away_bookmakers else 'N/A',
                'value_rating': 'home' if best_home > best_away else 'away'
            })
        except Exception as e:
            continue
            
    return {'value_bets': value_bets}