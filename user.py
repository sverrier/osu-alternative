import json

class User:
    def __init__(self, user):
        self.user = user

    def __str__(self):
        return json.dumps(self.user, indent=4)