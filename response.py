import json

from user import User

class Response:
    def __init__(self, users: list[User]):
        self.users = users

    def toDict(self):
        return {
            'users': [user.toDict() for user in self.users]
        }

    def toJson(self):
        return json.dumps(self.toDict(), ensure_ascii=False)
