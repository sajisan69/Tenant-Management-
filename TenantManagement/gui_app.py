import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.building import Building

# Initialize the System Logic
system = Building()

class TenantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tenant & Building Manager")
        self.geometry("700x500")
        self.configure(bg="#f0f0f0")

        # Container for all frames
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        
        # Define all screens (Frames)
        for F in (LoginScreen, SignUpScreen, AdminDashboard, TenantDashboard):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginScreen)

    def show_frame(self, cont, data=None):
        frame = self.frames[cont]
        if hasattr(frame, "update_data") and data:
            frame.update_data(data)
        elif hasattr(frame, "refresh"):
            frame.refresh()
        frame.tkraise()

# --- 1. LOGIN SCREEN ---
class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        # Header
        tk.Label(self, text="🏢 Building Management System", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=40)

        # Notebook for Tabs (Tenant Login / Admin Login)
        tabs = ttk.Notebook(self)
        tabs.pack(expand=True, fill="both", padx=50, pady=20)

        # -- Tenant Tab --
        tab_tenant = tk.Frame(tabs, bg="white")
        tabs.add(tab_tenant, text="  Tenant Login  ")
        
        tk.Label(tab_tenant, text="Tenant ID (e.g., T-001):", bg="white").pack(pady=5)
        self.entry_tid = ttk.Entry(tab_tenant)
        self.entry_tid.pack(pady=5)
        
        tk.Label(tab_tenant, text="Password:", bg="white").pack(pady=5)
        self.entry_tpwd = ttk.Entry(tab_tenant, show="*")
        self.entry_tpwd.pack(pady=5)
        
        ttk.Button(tab_tenant, text="Login", command=self.login_tenant).pack(pady=15)
        
        # Link to Sign Up
        tk.Button(tab_tenant, text="New Tenant? Sign Up Here", command=lambda: controller.show_frame(SignUpScreen), 
                  bg="white", fg="blue", bd=0, cursor="hand2").pack(pady=10)

        # -- Admin Tab --
        tab_admin = tk.Frame(tabs, bg="white")
        tabs.add(tab_admin, text="  Admin Login  ")
        
        tk.Label(tab_admin, text="Username:", bg="white").pack(pady=5)
        self.entry_auser = ttk.Entry(tab_admin)
        self.entry_auser.pack(pady=5)
        
        tk.Label(tab_admin, text="Password:", bg="white").pack(pady=5)
        self.entry_apwd = ttk.Entry(tab_admin, show="*")
        self.entry_apwd.pack(pady=5)
        
        ttk.Button(tab_admin, text="Login as Admin", command=self.login_admin).pack(pady=15)

    def login_tenant(self):
        tid = self.entry_tid.get()
        pwd = self.entry_tpwd.get()
        tenant = system.login_tenant(tid, pwd)
        if tenant:
            self.entry_tid.delete(0, tk.END)
            self.entry_tpwd.delete(0, tk.END)
            self.controller.show_frame(TenantDashboard, data=tenant)
        else:
            messagebox.showerror("Error", "Invalid ID or Password")

    def login_admin(self):
        user = self.entry_auser.get()
        pwd = self.entry_apwd.get()
        if system.admin_login(user, pwd):
            self.entry_auser.delete(0, tk.END)
            self.entry_apwd.delete(0, tk.END)
            self.controller.show_frame(AdminDashboard)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

# --- 2. SIGN UP SCREEN ---
class SignUpScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        tk.Label(self, text="New Tenant Registration", font=("Arial", 16), bg="#f0f0f0").pack(pady=20)
        
        form_frame = tk.Frame(self, bg="#f0f0f0")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Full Name:", bg="#f0f0f0").grid(row=0, column=0, pady=5, sticky="e")
        self.ent_name = ttk.Entry(form_frame)
        self.ent_name.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Phone:", bg="#f0f0f0").grid(row=1, column=0, pady=5, sticky="e")
        self.ent_phone = ttk.Entry(form_frame)
        self.ent_phone.grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Username:", bg="#f0f0f0").grid(row=2, column=0, pady=5, sticky="e")
        self.ent_user = ttk.Entry(form_frame)
        self.ent_user.grid(row=2, column=1, pady=5)

        tk.Label(form_frame, text="Password:", bg="#f0f0f0").grid(row=3, column=0, pady=5, sticky="e")
        self.ent_pass = ttk.Entry(form_frame, show="*")
        self.ent_pass.grid(row=3, column=1, pady=5)

        ttk.Button(self, text="Register", command=self.register).pack(pady=20)
        ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame(LoginScreen)).pack()

    def register(self):
        name = self.ent_name.get()
        phone = self.ent_phone.get()
        user = self.ent_user.get()
        pwd = self.ent_pass.get()

        if name and pwd:
            tid = system.sign_up_tenant(name, phone, user, pwd)
            messagebox.showinfo("Success", f"Account Created!\n\nYOUR ID IS: {tid}\nPlease use this ID to login.")
            self.controller.show_frame(LoginScreen)
        else:
            messagebox.showwarning("Warning", "Name and Password are required.")

# --- 3. ADMIN DASHBOARD ---
class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        
        # Top Bar
        top = tk.Frame(self, bg="#333", height=50)
        top.pack(fill="x")
        tk.Label(top, text="Admin Dashboard", fg="white", bg="#333", font=("Arial", 14)).pack(side="left", padx=20)
        ttk.Button(top, text="Logout", command=lambda: controller.show_frame(LoginScreen)).pack(side="right", padx=10, pady=10)

        # Tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)

        # -- Tab 1: Flats --
        self.tab_flats = tk.Frame(self.tabs, bg="white")
        self.tabs.add(self.tab_flats, text="Manage Flats")
        self.setup_flats_tab()

        # -- Tab 2: Assign --
        self.tab_assign = tk.Frame(self.tabs, bg="white")
        self.tabs.add(self.tab_assign, text="Assign Flat")
        self.setup_assign_tab()

        # -- Tab 3: Reports --
        self.tab_reports = tk.Frame(self.tabs, bg="white")
        self.tabs.add(self.tab_reports, text="Reports")
        self.setup_reports_tab()

    def refresh(self):
        self.update_flat_list()
        self.update_tenant_list()

    def setup_flats_tab(self):
        frame = tk.Frame(self.tab_flats, bg="white")
        frame.pack(pady=10)
        
        # Add Flat Inputs
        ttk.Label(frame, text="Flat ID:").grid(row=0, column=0)
        self.ent_fid = ttk.Entry(frame, width=10)
        self.ent_fid.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame, text="Floor:").grid(row=0, column=2)
        self.ent_flr = ttk.Entry(frame, width=10)
        self.ent_flr.grid(row=0, column=3, padx=5)
        
        ttk.Label(frame, text="Rent:").grid(row=0, column=4)
        self.ent_rent = ttk.Entry(frame, width=10)
        self.ent_rent.grid(row=0, column=5, padx=5)

        ttk.Button(frame, text="Add Flat", command=self.add_flat).grid(row=0, column=6, padx=10)

        # List Area
        columns = ("ID", "Floor", "Rent", "Status", "Tenant")
        self.tree_flats = ttk.Treeview(self.tab_flats, columns=columns, show="headings", height=10)
        for col in columns: self.tree_flats.heading(col, text=col)
        self.tree_flats.pack(pady=10, fill="x")

    def setup_assign_tab(self):
        frame = tk.Frame(self.tab_assign, bg="white")
        frame.pack(pady=20)

        ttk.Label(frame, text="Tenant ID:").grid(row=0, column=0)
        self.ent_assign_tid = ttk.Entry(frame)
        self.ent_assign_tid.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Flat ID:").grid(row=1, column=0)
        self.ent_assign_fid = ttk.Entry(frame)
        self.ent_assign_fid.grid(row=1, column=1, padx=5)

        ttk.Button(frame, text="Assign", command=self.assign_flat).grid(row=2, column=0, columnspan=2, pady=10)

    def setup_reports_tab(self):
        ttk.Button(self.tab_reports, text="Export Financial CSV", command=self.export_csv).pack(pady=20)
        
        # Tenant List
        tk.Label(self.tab_reports, text="All Tenants", bg="white", font=("Arial", 12)).pack()
        columns = ("ID", "Name", "Flat", "Dues")
        self.tree_tenants = ttk.Treeview(self.tab_reports, columns=columns, show="headings", height=10)
        for col in columns: self.tree_tenants.heading(col, text=col)
        self.tree_tenants.pack(pady=10, fill="x")

    # -- Logic --
    def add_flat(self):
        if system.add_flat(self.ent_fid.get(), self.ent_flr.get(), self.ent_rent.get()):
            messagebox.showinfo("Success", "Flat Added")
            self.refresh()
        else:
            messagebox.showerror("Error", "Flat ID already exists")

    def assign_flat(self):
        if system.assign_flat(self.ent_assign_tid.get(), self.ent_assign_fid.get()):
            messagebox.showinfo("Success", "Flat Assigned")
            self.refresh()
        else:
            messagebox.showerror("Error", "Check IDs or Availability")

    def export_csv(self):
        success, path = system.export_payment_history()
        if success: messagebox.showinfo("Export", f"File saved to: {path}")
        else: messagebox.showerror("Error", path)

    def update_flat_list(self):
        for row in self.tree_flats.get_children(): self.tree_flats.delete(row)
        for f in system.list_flats():
            self.tree_flats.insert("", "end", values=(f.flat_id, f.floor, f.rent, f.status, f.tenant_id or "-"))

    def update_tenant_list(self):
        for row in self.tree_tenants.get_children(): self.tree_tenants.delete(row)
        for t in system.list_tenants():
            self.tree_tenants.insert("", "end", values=(t.tenant_id, t.name, t.assigned_flat_id or "-", f"${t.get_pending_dues()}"))

# --- 4. TENANT DASHBOARD ---
class TenantDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        self.current_tenant = None

        # Top Bar
        self.top_lbl = tk.Label(self, text="", bg="#0078D7", fg="white", font=("Arial", 16), pady=10)
        self.top_lbl.pack(fill="x")
        
        # Dues Section
        self.dues_frame = tk.Frame(self, bg="white", bd=1, relief="solid")
        self.dues_frame.pack(pady=20, padx=20, fill="x")
        
        self.lbl_dues = tk.Label(self.dues_frame, text="Pending Dues: $0.00", font=("Arial", 18, "bold"), fg="red", bg="white")
        self.lbl_dues.pack(pady=10)
        
        self.btn_pay = ttk.Button(self.dues_frame, text="Pay Now", command=self.pay_rent)
        self.btn_pay.pack(pady=10)

        # History Section
        tk.Label(self, text="Payment History", bg="#f0f0f0").pack()
        columns = ("Date", "Month", "Amount")
        self.tree_hist = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for col in columns: self.tree_hist.heading(col, text=col)
        self.tree_hist.pack(pady=5, padx=20, fill="both", expand=True)

        ttk.Button(self, text="Logout", command=lambda: controller.show_frame(LoginScreen)).pack(pady=10)

    def update_data(self, tenant):
        self.current_tenant = tenant
        self.top_lbl.config(text=f"Welcome, {tenant.name} ({tenant.tenant_id})")
        self.refresh_dues()
        self.refresh_history()

    def refresh_dues(self):
        dues = self.current_tenant.get_pending_dues()
        self.lbl_dues.config(text=f"Pending Dues: ${dues}")
        if dues == 0:
            self.lbl_dues.config(fg="green")
            self.btn_pay.config(state="disabled")
        else:
            self.lbl_dues.config(fg="red")
            self.btn_pay.config(state="normal")

    def refresh_history(self):
        for row in self.tree_hist.get_children(): self.tree_hist.delete(row)
        for p in self.current_tenant.payments:
            self.tree_hist.insert("", "end", values=(p.date, p.month, f"${p.amount}"))

    def pay_rent(self):
        dues = self.current_tenant.get_pending_dues()
        month = datetime.now().strftime("%B")
        if messagebox.askyesno("Confirm", f"Pay ${dues} for {month}?"):
            system.record_payment(self.current_tenant.tenant_id, dues, month)
            messagebox.showinfo("Success", "Payment Successful! Receipt Saved.")
            self.refresh_dues()
            self.refresh_history()

if __name__ == "__main__":
    app = TenantApp()
    app.mainloop()
