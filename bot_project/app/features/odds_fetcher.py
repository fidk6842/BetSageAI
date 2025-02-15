import aiohttp
import logging
from typing import List, Dict, Any

logger = logging.getLogger('OddsBot')

async def fetch_odds_for_league(api_key: str, base_url: str, league_key: str) -> List[Dict[str, Any]]:
    """
    Fetch raw odds data from API
    Returns list of matches with complete bookmaker data
    """
    url = f"{base_url}/sports/{league_key}/odds"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Fetched {len(data)} matches for {league_key}")
                    return data
                logger.error(f"API Error: {response.status}")
                return []
                
    except Exception as e:
        logger.error(f"Fetch failed: {str(e)}")
        return []