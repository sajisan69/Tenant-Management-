from datetime import datetime

class Payment:
    def __init__(self, amount, month, date=None):
        self.amount = amount
        self.month = month
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {"amount": self.amount, "month": self.month, "date": self.date}

    @classmethod
    def from_dict(cls, data):
        return cls(data["amount"], data["month"], data["date"])
