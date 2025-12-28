from datetime import datetime

class Payment:
    def __init__(self, payment_id, tenant_id, amount, month, date=None):
        self.payment_id = payment_id
        self.tenant_id = tenant_id
        self.amount = float(amount)
        self.month = month
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "payment_id": self.payment_id,
            "tenant_id": self.tenant_id,
            "amount": self.amount,
            "month": self.month,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['payment_id'],
            data['tenant_id'],
            data['amount'],
            data['month'],
            data['date']
        )