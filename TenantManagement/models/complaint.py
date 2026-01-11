class Complaint:
    def __init__(self, complaint_id, tenant_id, tenant_name, description, status="Pending", date=""):
        self.complaint_id = complaint_id
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name
        self.description = description
        self.status = status
        self.date = date

    def to_dict(self):
        return {
            "complaint_id": self.complaint_id,
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant_name,
            "description": self.description,
            "status": self.status,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["complaint_id"],
            data["tenant_id"],
            data["tenant_name"],
            data["description"],
            data["status"],
            data["date"]
        )