from werkzeug.contrib.cache import SimpleCache
import json

class Settings:
    def __init__(self):
        self.cache = SimpleCache()

    def get_token(self):
        token = self.cache.get("token")
        if (type(token) == type(None)):
            return None

        return json.loads(token)

    def set_token(self, token):
        self.cache.set("token", token)
