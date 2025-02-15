from typing import Dict, List
import random

def demo_analysis(matches: List[Dict]) -> Dict[str, List[Dict]]:
    return {
        "demo": [{
            "match": f"{m['home_team']} vs {m['away_team']}",
            "prediction": random.choice(["Home Win", "Away Win", "Draw"]),
            "confidence": f"{random.randint(50, 100)}%"
        } for m in matches]
    }