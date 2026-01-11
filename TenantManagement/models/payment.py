class Payment:
    def __init__(self, amount, month, date, transaction_id="", status="Pending"):
        self.amount = amount
        self.month = month
        self.date = date
        self.transaction_id = transaction_id
        self.status = status  # Can be "Pending" or "Approved"

    def to_dict(self):
        return {
            "amount": self.amount,
            "month": self.month,
            "date": self.date,
            "transaction_id": self.transaction_id,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["amount"],
            data["month"],
            data["date"],
            data.get("transaction_id", ""),
            data.get("status", "Approved")  # Old payments default to Approved
        )
