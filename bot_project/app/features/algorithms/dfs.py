import numpy as np
from typing import List, Dict
from app.features.data_processing import ProcessedMatch

def detect_arbitrage(matches: List[ProcessedMatch]) -> Dict[str, List[Dict]]:
    """
    Find arbitrage opportunities within individual matches using bookmaker odds
    Returns: {arbitrage_opportunities: [...]}
    """
    opportunities = []
    
    for match in matches:
        try:
            best_home = max((odds for bm in match['bookmakers'].values() 
                           if (odds := bm['home']) is not None), default=None)
            best_away = max((odds for bm in match['bookmakers'].values() 
                           if (odds := bm['away']) is not None), default=None)
            best_draw = max((odds for bm in match['bookmakers'].values() 
                           if (odds := bm['draw']) is not None), default=None)

            if all([best_home, best_away, best_draw]):
                total_implied_prob = (1/best_home + 1/best_away + 1/best_draw)
                roi = (1 - total_implied_prob) * 100
                
                if total_implied_prob < 1:  # ROI > 0%
                    # Find bookmakers offering these odds
                    home_bms = [bm for bm, odds in match['bookmakers'].items() 
                              if odds['home'] == best_home]
                    away_bms = [bm for bm, odds in match['bookmakers'].items() 
                              if odds['away'] == best_away]
                    draw_bms = [bm for bm, odds in match['bookmakers'].items() 
                              if odds['draw'] == best_draw]
                    
                    opportunities.append({
                        'home_team': match['home_team'],
                        'away_team': match['away_team'],
                        'home_odds': best_home,
                        'away_odds': best_away,
                        'draw_odds': best_draw,
                        'home_bookmakers': home_bms[:2],  # Top 2 bookmakers
                        'away_bookmakers': away_bms[:2],
                        'draw_bookmakers': draw_bms[:2],
                        'potential_return': round(roi, 1)
                    })
        except Exception as e:
            continue

    return {'arbitrage_opportunities': opportunities[:5]} if opportunities else {'status': 'no_arbitrage'}