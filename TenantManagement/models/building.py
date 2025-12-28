from models.flat import Flat
from models.tenant import Tenant
from models.payment import Payment
from utils.file_handler import FileHandler
from utils.id_generator import IDGenerator


class Building:
    def __init__(self):
        self.flats = []
        self.tenants = []
        self.admin_creds = {"username": "admin", "password": "123"}
        self.load_data()

    def login_tenant(self, tenant_id, password):
        for t in self.tenants:
            if t.tenant_id == tenant_id and t.verify_password(password):
                return t
        return None

    def admin_login(self, username, password):
        return username == self.admin_creds["username"] and password == self.admin_creds["password"]

    def sign_up_tenant(self, name, phone, username, password):
        t_id = IDGenerator.generate_tenant_id(self.tenants)
        new_tenant = Tenant(t_id, name, phone, username, password)
        self.tenants.append(new_tenant)
        self.save_data()
        return t_id

    def add_flat(self, flat_id, floor, rent):
        if any(f.flat_id == flat_id for f in self.flats):
            return False
        self.flats.append(Flat(flat_id, floor, rent))
        self.save_data()
        return True

    def list_flats(self):
        return self.flats

    def list_tenants(self):
        return self.tenants

    def assign_flat(self, tenant_id, flat_id):
        tenant = next((t for t in self.tenants if t.tenant_id == tenant_id), None)
        flat = next((f for f in self.flats if f.flat_id == flat_id), None)

        if tenant and flat and flat.status == "Available":
            flat.status = "Occupied"
            flat.tenant_id = tenant.tenant_id
            tenant.assign_flat(flat.flat_id, flat.rent)
            self.save_data()
            return True
        return False

    def record_payment(self, tenant_id, amount, month):
        tenant = next((t for t in self.tenants if t.tenant_id == tenant_id), None)
        if tenant:
            pay_id = IDGenerator.generate_payment_id()
            new_payment = Payment(pay_id, tenant_id, amount, month)
            tenant.add_payment(new_payment)
            self.save_data()
            self.generate_receipt(tenant, new_payment)
            return True
        return False

    def generate_receipt(self, tenant, payment):
        receipt_text = (
            "================================\n"
            "       PAYMENT RECEIPT          \n"
            "================================\n"
            f"Receipt ID : {payment.payment_id}\n"
            f"Date       : {payment.date}\n"
            f"Tenant     : {tenant.name}\n"
            f"Flat No    : {tenant.assigned_flat_id}\n"
            f"Month      : {payment.month}\n"
            f"Amount Paid: ${payment.amount:.2f}\n"
            "================================\n"
        )
        print(receipt_text)
        path = FileHandler.save_receipt(f"{payment.payment_id}.txt", receipt_text)
        print(f"✅ Receipt saved to: {path}")

    def export_payment_history(self):
        all_payments = []
        for t in self.tenants:
            for p in t.payments:
                row = p.to_dict()
                row['tenant_name'] = t.name
                all_payments.append(row)

        headers = ["payment_id", "tenant_id", "tenant_name", "amount", "month", "date"]
        return FileHandler.export_to_csv("financial_report.csv", all_payments, headers)

    def save_data(self):
        FileHandler.save_json('flats.json', [f.to_dict() for f in self.flats])
        FileHandler.save_json('tenants.json', [t.to_dict() for t in self.tenants])

    def load_data(self):
        flat_data = FileHandler.load_json('flats.json')
        self.flats = [Flat.from_dict(d) for d in flat_data]

        tenant_data = FileHandler.load_json('tenants.json')
        self.tenants = []
        for d in tenant_data:
            t = Tenant.from_dict(d)
            if 'payments' in d:
                t.payments = [Payment.from_dict(p) for p in d['payments']]
            self.tenants.append(t)