import asyncio
import logging
import hashlib
import numpy as np
from typing import List, Dict, Union, Any
from app.features.odds_fetcher import fetch_odds_for_league

logger = logging.getLogger('OddsBot')

# Define the ProcessedMatch type with bookmaker data
ProcessedMatch = Dict[str, Union[str, List[float], Dict[str, Dict[str, float]]]]

def preprocess_odds(raw_odds: List[Dict]) -> List[ProcessedMatch]:
    """
    Robust preprocessing with error handling and bookmaker data storage.
    Returns a list of processed matches with bookmaker-specific odds.
    """
    processed = []
    
    for match in raw_odds:
        try:
            # Extract basic match information
            home_team = match.get('home_team', 'Unknown')
            away_team = match.get('away_team', 'Unknown')
            commence_time = match.get('commence_time', '')
            
            # Generate a unique match ID
            match_id = hashlib.md5(
                f"{home_team}|{away_team}|{commence_time}".encode()
            ).hexdigest()[:8]

            # Initialize match data structure
            odds_data: ProcessedMatch = {
                'match_id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'commence_time': commence_time,
                'bookmakers': {},  # Store bookmaker-specific odds
                'home_odds': [],
                'away_odds': [],
                'draw_odds': []
            }

            # Process bookmaker data
            for bookmaker in match.get('bookmakers', []):
                bookmaker_name = bookmaker.get('key', 'unknown')
                odds_data['bookmakers'][bookmaker_name] = {
                    'home': None,
                    'away': None,
                    'draw': None
                }
                
                # Extract market data
                for market in bookmaker.get('markets', []):
                    if market.get('key') == 'h2h':
                        for outcome in market.get('outcomes', []):
                            name = outcome.get('name', '')
                            price = outcome.get('price', 1.0)
                            
                            # Assign odds to the correct category
                            if name == home_team:
                                odds_data['home_odds'].append(price)
                                odds_data['bookmakers'][bookmaker_name]['home'] = price
                            elif name == away_team:
                                odds_data['away_odds'].append(price)
                                odds_data['bookmakers'][bookmaker_name]['away'] = price
                            elif name == 'Draw':
                                odds_data['draw_odds'].append(price)
                                odds_data['bookmakers'][bookmaker_name]['draw'] = price

            # Validate minimum data requirements
            if (len(odds_data['home_odds']) >= 2 and 
                len(odds_data['away_odds']) >= 2 and 
                len(odds_data['draw_odds']) >= 2):
                processed.append(odds_data)
            else:
                logger.warning(f"Insufficient odds for {match_id}")

        except KeyError as e:
            logger.error(f"Missing key in match data: {str(e)}")
            continue
            
    logger.info(f"Preprocessed {len(processed)} valid matches")
    return processed

async def process_pipeline(
    api_key: str,
    base_url: str,
    league_key: str,
    algorithm: str,
    paid_user: bool
) -> Dict[str, Any]:
    """
    Robust processing pipeline with error handling and algorithm execution.
    Returns results from the selected algorithm or an error message.
    """
    try:
        # Fetch raw data from the API
        raw_data = await fetch_odds_for_league(api_key, base_url, league_key)
        
        if not raw_data:
            return {"error": "No data fetched from API"}
        
        # Preprocess the raw data
        processed_matches = preprocess_odds(raw_data)
        
        if not processed_matches:
            return {"error": "No valid matches after preprocessing"}
        
        # Check user payment status
        if not paid_user:
            from app.features.algorithms.demo import demo_analysis
            return demo_analysis(processed_matches)
        
        # Import algorithms only for paid users
        from app.features.algorithms import (
            analyze_odds_movement,
            detect_arbitrage,
            calculate_parlay_stakes,
            simulate_outcomes,
            implied_probability_threshold_model,
            odds_comparison_model
        )
        
        # Map algorithms to their functions
        algorithm_map = {
            'arima': analyze_odds_movement,
            'arb': detect_arbitrage,
            'kelly': calculate_parlay_stakes,
            'monte': simulate_outcomes,
            'ipt': implied_probability_threshold_model,
            'value': odds_comparison_model
        }
        
        # Validate the selected algorithm
        if algorithm not in algorithm_map:
            return {"error": f"Invalid algorithm: {algorithm}"}
        
        # Get the processor function
        processor = algorithm_map[algorithm]
        
        # Execute the algorithm
        if asyncio.iscoroutinefunction(processor):
            results = await processor(processed_matches)
        else:
            results = processor(processed_matches)
            
        return results or {"status": "no_opportunities"}
        
    except Exception as e:
        logger.error(f"Pipeline failure: {str(e)}", exc_info=True)
        return {"error": str(e)}