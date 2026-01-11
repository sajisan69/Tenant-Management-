import hashlib
from datetime import datetime
from models.payment import Payment


class Tenant:
    def __init__(self, tenant_id, name, phone, username, password_hash, role="tenant", assigned_flat_id=None,
                 flat_rent=0.0, payments=None, is_hashed=True):
        self.tenant_id = tenant_id
        self.name = name
        self.phone = phone
        self.username = username

        if is_hashed:
            self.password_hash = password_hash
        else:
            self.password_hash = hashlib.sha256(password_hash.encode()).hexdigest()

        self.role = role
        self.assigned_flat_id = assigned_flat_id
        self.flat_rent = float(flat_rent)
        self.payments = payments if payments else []

    def verify_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash

    def get_due_amount(self):
        """
        Logic:
        1. If no flat -> Due 0
        2. If current month is PAID and APPROVED -> Due 0
        3. Else -> Due is Rent Amount
        """
        if not self.assigned_flat_id or self.flat_rent == 0:
            return 0.0

        current_month = datetime.now().strftime("%B")

        for p in reversed(self.payments):
            # Must match month AND be Approved
            if p.month == current_month and p.status == "Approved":
                return 0.0

        return self.flat_rent

    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "phone": self.phone,
            "assigned_flat_id": self.assigned_flat_id,
            "flat_rent": self.flat_rent,
            "payments": [p.to_dict() for p in self.payments]
        }

    @classmethod
    def from_dict(cls, data):
        payments = [Payment.from_dict(p) for p in data.get("payments", [])]
        def_hash = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
        return cls(
            tenant_id=data.get("tenant_id"),
            name=data.get("name"),
            phone=data.get("phone"),
            username=data.get("username"),
            password_hash=data.get("password_hash", def_hash),
            role=data.get("role", "tenant"),
            assigned_flat_id=data.get("assigned_flat_id"),
            flat_rent=data.get("flat_rent", 0.0),
            payments=payments,
            is_hashed=True
        )
