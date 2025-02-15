import numpy as np
from typing import List, Dict
from app.features.data_processing import ProcessedMatch

def implied_probability_threshold_model(matches: List[ProcessedMatch], threshold: float = 0.4) -> Dict[str, List[Dict]]:
    """
    Predict outcomes based on implied probabilities
    Returns: {predictions: [...]}
    """
    predictions = []
    
    for match in matches:
        try:
            home_prob = np.median([1/o for o in match['home_odds']])
            away_prob = np.median([1/o for o in match['away_odds']])
            draw_prob = np.median([1/o for o in match['draw_odds']])
            
            total = home_prob + away_prob + draw_prob
            home_prob /= total
            away_prob /= total
            
            prediction = (
                "Home Win" if home_prob > threshold else
                "Away Win" if away_prob > threshold else
                "No Clear Favorite"
            )
            
            predictions.append({
                'match_id': match['match_id'],
                'prediction': "Home Win" if home_prob > threshold else "Away Win" if away_prob > threshold else "No Clear Favorite",
                'home_team': match['home_team'],   
                'away_team': match['away_team'],
                'home_prob': round(home_prob, 2),
                'away_prob': round(away_prob, 2)
            })
        except:
            continue
            
    return {'predictions': predictions} if predictions else {'error': 'no_predictions'}