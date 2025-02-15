import logging
from typing import Dict, Optional, List

logger = logging.getLogger('OddsBot')

class LeagueManager:
    """Central hub for league data management and validation."""
    
    # Complete league database with API identifiers
    LEAGUE_DB: Dict[str, Dict[str, str]] = {
        'epl': {
            'display': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League',
            'api_key': 'soccer_epl'
        },
        'la_liga': {
            'display': '🇪🇸 La Liga',
            'api_key': 'soccer_spain_la_liga'
        },
        'bundesliga': {
            'display': '🇩🇪 Bundesliga',
            'api_key': 'soccer_germany_bundesliga'
        },
        'serie_a': {
            'display': '🇮🇹 Serie A',
            'api_key': 'soccer_italy_serie_a'
        },
        'ligue_1': {
            'display': '🇫🇷 Ligue 1',
            'api_key': 'soccer_france_ligue_one'
        },
        'champions': {
            'display': '🏆 Champions League',
            'api_key': 'soccer_uefa_champs_league'
        }
    }

    @classmethod
    def is_valid(cls, league_key: str) -> bool:
        """Validate league key existence."""
        valid = league_key in cls.LEAGUE_DB
        if not valid:
            logger.warning(f"Invalid league key: {league_key}")
        return valid

    @classmethod
    def get_display_name(cls, league_key: str) -> str:
        """Get formatted league name for UI."""
        try:
            return cls.LEAGUE_DB[league_key]['display']
        except KeyError:
            logger.error(f"Missing display name for: {league_key}")
            return "Unknown League"

    @classmethod
    def get_api_key(cls, league_key: str) -> str:
        """Retrieve API identifier for a league."""
        try:
            return cls.LEAGUE_DB[league_key]['api_key']
        except KeyError:
            logger.error(f"Missing API key for: {league_key}")
            return ''

    @classmethod
    def get_ui_mapping(cls) -> Dict[str, str]:
        """Get league key to display name mapping for buttons."""
        return {k: v['display'] for k, v in cls.LEAGUE_DB.items()}

    @classmethod
    def get_all_leagues(cls) -> List[Dict[str, str]]:
        """Complete league data for system operations."""
        return [
            {
                'key': key,
                'display': info['display'],
                'api_key': info['api_key']
            }
            for key, info in cls.LEAGUE_DB.items()
        ]

    @classmethod
    def reverse_lookup(cls, api_key: str) -> Optional[str]:
        """Find league key from API identifier."""
        for key, info in cls.LEAGUE_DB.items():
            if info['api_key'] == api_key:
                return key
        logger.warning(f"No league found for API key: {api_key}")
        return None

    @classmethod
    def validate_config(cls) -> bool:
        """Ensure data integrity through automated checks."""
        required_keys = {'display', 'api_key'}
        try:
            for key, info in cls.LEAGUE_DB.items():
                if not required_keys.issubset(info.keys()):
                    logger.error(f"Missing required fields in: {key}")
                    return False
                if not all(isinstance(v, str) for v in info.values()):
                    logger.error(f"Invalid data types in: {key}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            return False