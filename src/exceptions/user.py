import uuid


class UserCreationException(Exception):
    def __init__(self):
        self.message = "Some exception occurred while user creation..."
        super().__init__(self.message)


class UserNotFoundException(Exception):
    def __init__(self, user_id: uuid.UUID):
        self.message = f"User with {user_id=} not found!"
        super().__init__(self.message)


class UserPasswordNotFoundException(Exception):
    def __init__(self, user_id: uuid.UUID):
        self.message = f"User's password with {user_id=} not found!"
        super().__init__(self.message)


class UserAlreadyExistException(Exception):
    def __init__(self):
        self.message = "User with this email address already exist!"
        super().__init__(self.message)
