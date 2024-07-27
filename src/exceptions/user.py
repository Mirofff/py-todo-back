import uuid


class UserException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message if message is not None else "Some exception occurred while user creation..."
        super().__init__(self.message)


class UserNotFoundException(UserException):
    def __init__(self, user_id: uuid.UUID):
        self.message = f"User with {user_id=} not found!"
        super().__init__(self.message)


class UserPasswordNotFoundException(UserException):
    def __init__(self, user_id: uuid.UUID):
        self.message = f"User's password with {user_id=} not found!"
        super().__init__(self.message)


class UserAlreadyExistException(UserException):
    def __init__(self):
        self.message = "User with this email address already exist!"
        super().__init__(self.message)
