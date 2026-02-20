import os
import json
import time
import hashlib
from datetime import datetime, timedelta

class SimpleCache:
    def __init__(self, cache_dir=".cache", default_timeout=3600):
        self.cache_dir = cache_dir
        self.default_timeout = default_timeout
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, key):
        hashed_key = hashlib.md5(key.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.json")

    def get(self, key):
        path = self._get_cache_path(key)
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check expiration
            expires_at = data.get('expires_at')
            if expires_at and time.time() > expires_at:
                os.remove(path)
                return None
            
            return data.get('value')
        except Exception:
            return None

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
            
        path = self._get_cache_path(key)
        expires_at = time.time() + timeout
        
        data = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            return True
        except Exception:
            return False

    def delete(self, key):
        path = self._get_cache_path(key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def clear(self):
        for f in os.listdir(self.cache_dir):
            if f.endswith(".json"):
                os.remove(os.path.join(self.cache_dir, f))

# Global instance
cache = SimpleCache()
