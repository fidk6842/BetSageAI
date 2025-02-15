import numpy as np
from typing import List, Dict
from app.features.data_processing import ProcessedMatch

def calculate_parlay_stakes(matches: List[ProcessedMatch], bankroll: float = 1000.0) -> Dict[str, List[Dict]]:
    """
    Enhanced Kelly Criterion with bookmaker-specific recommendations
    Returns: {recommended_parlays: [...]}
    """
    parlays = []
    
    for match in matches:
        try:
            # Get all valid home odds from bookmakers
            bookmaker_odds = [
                (bm_name, bm_data['home']) 
                for bm_name, bm_data in match['bookmakers'].items()
                if bm_data['home'] is not None
            ]
            
            if not bookmaker_odds:
                continue
                
            # Find best odds and corresponding bookmaker
            best_odds, best_bookmaker = max(
                bookmaker_odds, 
                key=lambda x: x[1]
            )
            
            # Calculate probability and edge
            implied_prob = 1 / best_odds
            edge = implied_prob * best_odds - 1  # Simplified edge calculation
            
            if edge > 0.05:  # Minimum 5% edge threshold
                stake = (edge / (best_odds - 1)) * bankroll
                
                parlays.append({
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'bookmaker': best_bookmaker,
                    'odds': best_odds,
                    'recommended_stake': stake,
                    'edge_percentage': edge * 100
                })
                
        except Exception as e:
            continue
            
    return {'recommended_parlays': parlays[:5]} if parlays else {'status': 'no_valuable_parlays'}