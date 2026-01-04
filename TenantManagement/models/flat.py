class Flat:
    def __init__(self, flat_id, floor, rent, status="Available", tenant_id=None):
        self.flat_id = flat_id
        self.floor = floor
        self.rent = int(rent)
        self.status = status
        self.tenant_id = tenant_id

    def to_dict(self):
        return {
            "flat_id": self.flat_id,
            "floor": self.floor,
            "rent": self.rent,
            "status": self.status,
            "tenant_id": self.tenant_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["flat_id"], data["floor"], data["rent"], data["status"], data["tenant_id"])
