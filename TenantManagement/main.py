import sys
from datetime import datetime
from models.building import Building

system = Building()


def admin_menu():
    while True:
        print("\n=== ADMIN DASHBOARD ===")
        print("1. Add Flat")
        print("2. List All Flats")
        print("3. List All Tenants")
        print("4. Assign Flat to Tenant")
        print("5. Record Rent Payment (Manual)")
        print("6. Export Financial Report (CSV)")
        print("7. Logout")

        choice = input("Select: ")

        if choice == '1':
            fid = input("Flat ID: ")
            flr = input("Floor: ")
            rent = input("Rent: ")
            if system.add_flat(fid, flr, rent):
                print("✅ Flat Added.")
            else:
                print("❌ ID Exists.")

        elif choice == '2':
            print(f"{'ID':<10} {'Rent':<10} {'Status':<15} {'Tenant'}")
            print("-" * 45)
            for f in system.list_flats():
                print(f"{f.flat_id:<10} ${f.rent:<9} {f.status:<15} {f.tenant_id}")

        elif choice == '3':
            print(f"{'ID':<10} {'Name':<15} {'Flat':<10} {'Dues'}")
            print("-" * 45)
            for t in system.list_tenants():
                dues = t.get_pending_dues()
                print(f"{t.tenant_id:<10} {t.name:<15} {t.assigned_flat_id or 'None':<10} ${dues}")

        elif choice == '4':
            tid = input("Tenant ID: ")
            fid = input("Flat ID: ")
            if system.assign_flat(tid, fid):
                print("✅ Assigned Successfully.")
            else:
                print("❌ Failed.")

        elif choice == '5':
            tid = input("Tenant ID: ")
            amt = input("Amount: ")
            mth = input("Month: ")
            if system.record_payment(tid, amt, mth):
                print("✅ Payment Recorded.")
            else:
                print("❌ Failed.")

        elif choice == '6':
            success, path = system.export_payment_history()
            print(f"✅ Exported to: {path}" if success else "❌ Export Failed")

        elif choice == '7':
            break


def tenant_menu(current_tenant):
    while True:
        dues = current_tenant.get_pending_dues()
        print(f"\n=== HELLO, {current_tenant.name.upper()} ===")
        print(f"💰 CURRENT DUES: ${dues}")
        print("1. View Profile")
        print("2. Pay Rent Online")
        print("3. Payment History")
        print("4. Logout")

        choice = input("Select: ")

        if choice == '1':
            print(f"ID: {current_tenant.tenant_id} | Flat: {current_tenant.assigned_flat_id or 'Not Assigned'}")

        elif choice == '2':
            if dues == 0:
                print("✅ Great news! You have NO pending dues.")
                continue

            print(f"\nPaying ${dues} for {datetime.now().strftime('%B')}")
            print("[ QR CODE SCANNING... ]")
            if input("Confirm Payment? (y/n): ") == 'y':
                system.record_payment(current_tenant.tenant_id, dues, datetime.now().strftime('%B'))
                print("✅ Payment Successful! Receipt Saved.")

        elif choice == '3':
            print("\n--- HISTORY ---")
            if not current_tenant.payments:
                print("No payment history.")
            else:
                for p in current_tenant.payments:
                    print(f"{p.date} | {p.month} | ${p.amount}")

        elif choice == '4':
            break


def main():
    while True:
        print("\n=== TENANT & BUILDING SYSTEM ===")
        print("1. Admin Login")
        print("2. Tenant Login (Use Tenant ID)")
        print("3. Tenant Sign Up (New User)")
        print("4. Exit")

        choice = input("Select: ")

        if choice == '1':
            if system.admin_login(input("User: "), input("Pass: ")):
                admin_menu()
            else:
                print("❌ Invalid Admin Credentials")

        elif choice == '2':
            t_id = input("Enter Tenant ID (e.g., T-001): ")
            pwd = input("Enter Password: ")
            t = system.login_tenant(t_id, pwd)
            if t:
                tenant_menu(t)
            else:
                print("❌ Login Failed. Check ID and Password.")

        elif choice == '3':
            print("--- SIGN UP ---")
            name = input("Name: ")
            phone = input("Phone: ")
            user = input("Display Name: ")
            pwd = input("Password: ")
            tid = system.sign_up_tenant(name, phone, user, pwd)
            print(f"\n✅ SIGN UP SUCCESSFUL!\n🔑 YOUR LOGIN ID: {tid}\n⚠️ REMEMBER THIS ID TO LOGIN.")

        elif choice == '4':
            sys.exit()


if __name__ == "__main__":
    main()