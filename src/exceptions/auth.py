import datetime


class AccessTokenExpired(Exception):
    def __init__(self, expire_at: datetime.datetime):
        self.expired_at = expire_at
        self.message = f"Access token is expired at {self.expired_at}"
        super().__init__(self.message)
