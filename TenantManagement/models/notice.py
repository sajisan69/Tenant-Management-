class Notice:
    def __init__(self, message, date=""):
        self.message = message
        self.date = date

    def to_dict(self):
        return {"message": self.message, "date": self.date}

    @classmethod
    def from_dict(cls, data):
        return cls(data["message"], data["date"])