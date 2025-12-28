class Flat:
    def __init__(self, flat_id, floor, rent):
        self.flat_id = flat_id
        self.floor = floor
        self.rent = float(rent)
        self.status = "Available"
        self.tenant_id = None

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
        flat = cls(data['flat_id'], data['floor'], data['rent'])
        flat.status = data['status']
        flat.tenant_id = data['tenant_id']
        return flat