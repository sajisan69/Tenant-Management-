import hashlib

class User:
    def __init__(self, username, password, is_hashed=False):
        self.username = username
        if is_hashed:
            self.password_hash = password
        else:
            self.password_hash = self._hash_pass(password)

    def _hash_pass(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        return self._hash_pass(password) == self.password_hash

    def to_dict(self):
        return {"username": self.username, "password": self.password_hash}

    @classmethod
    def from_dict(cls, data):
        return cls(data["username"], data["password"], is_hashed=True)
