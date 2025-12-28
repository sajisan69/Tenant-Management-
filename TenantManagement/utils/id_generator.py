import random

class IDGenerator:
    @staticmethod
    def generate_tenant_id(existing_tenants_list):
        count = len(existing_tenants_list) + 1
        return f"T-{count:03d}"

    @staticmethod
    def generate_payment_id():
        return f"PAY-{random.randint(1000, 9999)}"