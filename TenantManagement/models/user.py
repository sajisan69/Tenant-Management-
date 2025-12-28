import hashlib


class User:
    def __init__(self, username, password, role="tenant"):
        self.username = username
        self.password_hash = password if len(password) == 64 else self._hash_password(password)
        self.role = role

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        return self.password_hash == self._hash_password(password)

    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role
        }