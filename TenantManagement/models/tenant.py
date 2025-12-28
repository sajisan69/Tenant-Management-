from models.user import User
from datetime import datetime


class Tenant(User):
    def __init__(self, tenant_id, name, phone, username, password):
        super().__init__(username, password, role="tenant")
        self.tenant_id = tenant_id
        self.name = name
        self.phone = phone
        self.assigned_flat_id = None
        self.flat_rent = 0.0
        self.payments = []

    def assign_flat(self, flat_id, rent):
        self.assigned_flat_id = flat_id
        self.flat_rent = float(rent)

    def add_payment(self, payment_obj):
        self.payments.append(payment_obj)

    def get_pending_dues(self):
        if not self.assigned_flat_id:
            return 0.0

        current_month = datetime.now().strftime("%B")
        is_paid = any(p.month.lower() == current_month.lower() for p in self.payments)

        if is_paid:
            return 0.0
        else:
            return self.flat_rent

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "tenant_id": self.tenant_id,
            "name": self.name,
            "phone": self.phone,
            "assigned_flat_id": self.assigned_flat_id,
            "flat_rent": self.flat_rent,
            "payments": [p.to_dict() for p in self.payments]
        })
        return data

    @classmethod
    def from_dict(cls, data):
        t = cls(data['tenant_id'], data['name'], data['phone'], data['username'], data['password_hash'])
        t.assigned_flat_id = data.get('assigned_flat_id')
        t.flat_rent = data.get('flat_rent', 0.0)
        return t