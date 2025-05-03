from user import User

class Response:

    def __init__(self, users:list[User]):

        self.users = users

    def toDict(self):
        return {
            "users": [user.toDict() for user in self.__users]
        }
