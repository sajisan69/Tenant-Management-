import json
import os
from models.flat import Flat
from models.tenant import Tenant
from models.user import User
from utils.id_generator import generate_tenant_id

class Building:
    def __init__(self):
        self.data_dir = "data"
        self.flats_file = os.path.join(self.data_dir, "flats.json")
        self.tenants_file = os.path.join(self.data_dir, "tenants.json")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.flats = []
        self.tenants = []
        self.admins = []
        self.check_data_folder()
        self.load_all_data()

    def check_data_folder(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_all_data(self):
        if os.path.exists(self.flats_file):
            with open(self.flats_file, 'r') as f:
                self.flats = [Flat.from_dict(x) for x in json.load(f)]

        if os.path.exists(self.tenants_file):
            with open(self.tenants_file, 'r') as f:
                self.tenants = [Tenant.from_dict(x) for x in json.load(f)]

        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.admins = [User.from_dict(x) for x in json.load(f)]

        if not self.admins:
            self.admins.append(User("admin", "12"))
            self.save_users()

    def save_flats(self):
        with open(self.flats_file, 'w') as f:
            json.dump([x.to_dict() for x in self.flats], f, indent=4)

    def save_tenants(self):
        with open(self.tenants_file, 'w') as f:
            json.dump([x.to_dict() for x in self.tenants], f, indent=4)

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump([x.to_dict() for x in self.admins], f, indent=4)

    def register_tenant(self, name, phone, username, password):
        if any(t.username == username for t in self.tenants):
            print("Username already taken")
            return False

        new_id = generate_tenant_id(self.tenants)

        new_tenant = Tenant(
            tenant_id=new_id,
            name=name,
            phone=phone,
            username=username,
            password_hash=password,
            is_hashed=False,
            role="tenant"
        )

        self.tenants.append(new_tenant)
        self.save_tenants()
        print(f"✅ Registered Tenant: {name} ({new_id})")
        return True

    def tenant_login(self, username, password):
        tenant = next((t for t in self.tenants if t.username == username), None)
        if tenant and tenant.verify_password(password):
            return tenant
        return None

    def admin_login(self, username, password):
        user = next((u for u in self.admins if u.username == username), None)
        if user and user.verify_password(password):
            return True
        return False

    def add_flat(self, flat_id, floor, rent):
        self.flats.append(Flat(flat_id, floor, rent))
        self.save_flats()

    def delete_flat(self, flat_id):
        self.flats = [f for f in self.flats if f.flat_id != flat_id]
        self.save_flats()

    def assign_flat(self, tenant_id, flat_id):
        tenant = next((t for t in self.tenants if t.tenant_id == tenant_id), None)
        flat = next((f for f in self.flats if f.flat_id == flat_id), None)

        if tenant and flat:
            if flat.status == "Occupied":
                print(f"❌ Error: Flat {flat_id} is already occupied!")
                return False

            if tenant.assigned_flat_id:
                old = next((f for f in self.flats if f.flat_id == tenant.assigned_flat_id), None)
                if old:
                    old.status = "Available"
                    old.tenant_id = None

            flat.status = "Occupied"
            flat.tenant_id = tenant_id

            tenant.assigned_flat_id = flat_id
            tenant.flat_rent = flat.rent

            self.save_flats()
            self.save_tenants()
            print(f"✅ Assigned {flat_id} to {tenant.name}")
            return True
        return False

    def add_payment(self, tenant_id, amount, month):
        tenant = next((t for t in self.tenants if t.tenant_id == tenant_id), None)
        if tenant:
            tenant.add_payment(amount, month)
            self.save_tenants()
            print(f"✅ Payment saved for {tenant.name}: {amount}")
            return True
        else:
            print(f"❌ Error: Tenant {tenant_id} not found.")
            return False
