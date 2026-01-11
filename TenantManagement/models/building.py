import json
import os
from datetime import datetime
from models.flat import Flat
from models.tenant import Tenant
from models.payment import Payment
from models.complaint import Complaint
from models.notice import Notice

class Building:
    def __init__(self):
        self.flats = []
        self.tenants = []
        self.complaints = []
        self.notices = []
        self.load_data()

    def load_data(self):
        if os.path.exists("data/flats.json"):
            with open("data/flats.json", "r") as f:
                self.flats = [Flat.from_dict(d) for d in json.load(f)]
        if os.path.exists("data/tenants.json"):
            with open("data/tenants.json", "r") as f:
                self.tenants = [Tenant.from_dict(d) for d in json.load(f)]
        if os.path.exists("data/complaints.json"):
            with open("data/complaints.json", "r") as f:
                self.complaints = [Complaint.from_dict(d) for d in json.load(f)]
        if os.path.exists("data/notices.json"):
            with open("data/notices.json", "r") as f:
                self.notices = [Notice.from_dict(d) for d in json.load(f)]

    def save_data(self):
        with open("data/flats.json", "w") as f:
            json.dump([x.to_dict() for x in self.flats], f, indent=4)
        with open("data/tenants.json", "w") as f:
            json.dump([x.to_dict() for x in self.tenants], f, indent=4)
        with open("data/complaints.json", "w") as f:
            json.dump([x.to_dict() for x in self.complaints], f, indent=4)
        with open("data/notices.json", "w") as f:
            json.dump([x.to_dict() for x in self.notices], f, indent=4)

    # --- FLAT & TENANT METHODS ---
    def add_flat(self, flat_id, floor, rent):
        self.flats.append(Flat(flat_id, floor, rent))
        self.save_data()

    def delete_flat(self, flat_id):
        self.flats = [f for f in self.flats if f.flat_id != flat_id]
        self.save_data()

    def register_tenant(self, name, phone, username, password):
        new_id = f"T-{len(self.tenants) + 1:03d}"
        t = Tenant(new_id, name, phone, username, password, is_hashed=False)
        self.tenants.append(t)
        self.save_data()
        return t

    def tenant_login(self, username, password):
        for t in self.tenants:
            if t.username == username and t.verify_password(password):
                return t
        return None

    def admin_login(self, admin_id, password):
        return admin_id == "admin" and password == "123"

    def assign_flat(self, tenant_id, flat_id):
        target_flat = next((f for f in self.flats if f.flat_id == flat_id), None)
        target_tenant = next((t for t in self.tenants if t.tenant_id == tenant_id), None)
        if target_flat and target_tenant and target_flat.status == "Available":
            target_flat.status = "Occupied"
            target_flat.tenant_id = tenant_id
            target_tenant.assigned_flat_id = flat_id
            target_tenant.flat_rent = target_flat.rent
            self.save_data()
            return True
        return False

    # --- PAYMENT METHODS ---
    def add_payment(self, tenant_id, amount, month, trx_id):
        for t in self.tenants:
            if t.tenant_id == tenant_id:
                p = Payment(amount, month, datetime.now().strftime("%Y-%m-%d"), trx_id, "Pending")
                t.payments.append(p)
                self.save_data()
                return True
        return False

    def approve_payment(self, tenant_id, trx_id):
        for t in self.tenants:
            if t.tenant_id == tenant_id:
                for p in t.payments:
                    if p.transaction_id == trx_id and p.status == "Pending":
                        p.status = "Approved"
                        self.save_data()
                        return True
        return False

    # --- NEW: COMPLAINT SYSTEM ---
    def add_complaint(self, tenant_id, tenant_name, description):
        cid = f"C-{len(self.complaints) + 1:03d}"
        date = datetime.now().strftime("%Y-%m-%d")
        comp = Complaint(cid, tenant_id, tenant_name, description, "Pending", date)
        self.complaints.append(comp)
        self.save_data()
        return True

    def resolve_complaint(self, complaint_id):
        for c in self.complaints:
            if c.complaint_id == complaint_id:
                c.status = "Resolved"
                self.save_data()
                return True
        return False

    # --- NEW: NOTICE BOARD ---
    def add_notice(self, message):
        date = datetime.now().strftime("%Y-%m-%d")
        self.notices.insert(0, Notice(message, date)) # Insert at top
        self.save_data()

    def delete_notice(self, index):
        if 0 <= index < len(self.notices):
            self.notices.pop(index)
            self.save_data()
