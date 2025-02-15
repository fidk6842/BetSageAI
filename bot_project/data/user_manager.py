import json
import os

class UserManager:
    DATA_FILE = "data/user_data.json"
    CRYPTO_ADDRESS = "Hot Penis"
    
    def __init__(self):
        os.makedirs(os.path.dirname(self.DATA_FILE), exist_ok=True)
        self.data = self._load_data()
        
    def _load_data(self):
        try:
            with open(self.DATA_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"paid_users": [], "blocked_users": [], "admin_ids": ["YOUR_ADMIN_ID"]}
            
    def _save_data(self):
        with open(self.DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def is_paid(self, user_id: int) -> bool:
        return str(user_id) in self.data["paid_users"]
    
    def is_blocked(self, user_id: int) -> bool:
        return str(user_id) in self.data["blocked_users"]
    
    def is_admin(self, user_id: int) -> bool:
        return str(user_id) in self.data["admin_ids"]
    
    def add_paid_user(self, user_id: int):
        if str(user_id) not in self.data["paid_users"]:
            self.data["paid_users"].append(str(user_id))
            self._save_data()
    
    def block_user(self, user_id: int):
        if str(user_id) not in self.data["blocked_users"]:
            self.data["blocked_users"].append(str(user_id))
            self._save_data()
    
    def get_crypto_address(self) -> str:
        return self.CRYPTO_ADDRESS
    def unblock_user(self, user_id: int):
        if str(user_id) in self.data["blocked_users"]:
            self.data["blocked_users"].remove(str(user_id))
            self._save_data()

    def get_stats(self):
        return {
            'total': len(self.data["paid_users"]) + len(self.data["blocked_users"]),
            'paid': len(self.data["paid_users"]),
            'blocked': len(self.data["blocked_users"])
        }

    def list_users(self):
        return {
            'paid': self.data["paid_users"],
            'blocked': self.data["blocked_users"],
            'admins': self.data["admin_ids"]
        }