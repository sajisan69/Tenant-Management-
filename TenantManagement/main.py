import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# --- CRASH PROTECTION: CHECK IMPORTS ---
try:
    from models.building import Building
except ImportError as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Setup Error", 
        f"Could not load the system files.\n\nError: {e}\n\n"
        "Make sure 'models' folder exists next to main.py")
    sys.exit()

# Initialize the System Logic
system = Building()

class TenantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tenant & Building Manager")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")

        # Container for screens
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        
        # Initialize all screens
        for F in (LoginScreen, SignUpScreen, AdminDashboard, TenantDashboard):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginScreen)

    def show_frame(self, cont, data=None):
        frame = self.frames[cont]
        # Refresh data if the screen has a refresh method
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

        # Center Box
        box = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised", bd=2)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="🏢 Building Management", font=("Arial", 22, "bold"), bg="white", fg="#333").pack(pady=(0, 20))

        # Tabs for Tenant/Admin
        tabs = ttk.Notebook(box)
        tabs.pack(fill="both", expand=True)

        # -- Tenant Tab --
        t_tab = tk.Frame(tabs, bg="white", padx=15, pady=15)
        tabs.add(t_tab, text="  Tenant Login  ")
        
        tk.Label(t_tab, text="Tenant ID (e.g. T-001)", bg="white", fg="#555").pack(anchor="w")
        self.entry_tid = ttk.Entry(t_tab, width=30)
        self.entry_tid.pack(pady=5)
        
        tk.Label(t_tab, text="Password", bg="white", fg="#555").pack(anchor="w")
        self.entry_tpwd = ttk.Entry(t_tab, show="*", width=30)
        self.entry_tpwd.pack(pady=5)
        
        ttk.Button(t_tab, text="Login", command=self.login_tenant).pack(pady=15, fill="x")
        
        # -- Admin Tab --
        a_tab = tk.Frame(tabs, bg="white", padx=15, pady=15)
        tabs.add(a_tab, text="  Admin Login  ")
        
        tk.Label(a_tab, text="Username", bg="white", fg="#555").pack(anchor="w")
        self.entry_auser = ttk.Entry(a_tab, width=30)
        self.entry_auser.pack(pady=5)
        
        tk.Label(a_tab, text="Password", bg="white", fg="#555").pack(anchor="w")
        self.entry_apwd = ttk.Entry(a_tab, show="*", width=30)
        self.entry_apwd.pack(pady=5)
        
        ttk.Button(a_tab, text="Login as Admin", command=self.login_admin).pack(pady=15, fill="x")

        # Footer Link
        tk.Button(box, text="New User? Create Account", command=lambda: controller.show_frame(SignUpScreen),
                  bg="white", fg="#0078D7", bd=0, cursor="hand2", font=("Arial", 9, "underline")).pack(pady=15)

    def login_tenant(self):
        tid = self.entry_tid.get()
        pwd = self.entry_tpwd.get()
        t = system.login_tenant(tid, pwd)
        if t:
            self.entry_tid.delete(0, tk.END)
            self.entry_tpwd.delete(0, tk.END)
            self.controller.show_frame(TenantDashboard, data=t)
        else:
            messagebox.showerror("Login Error", "Invalid Tenant ID or Password.\nRemember ID format is T-XXX (e.g. T-001)")

    def login_admin(self):
        if system.admin_login(self.entry_auser.get(), self.entry_apwd.get()):
            self.entry_auser.delete(0, tk.END)
            self.entry_apwd.delete(0, tk.END)
            self.controller.show_frame(AdminDashboard)
        else:
            messagebox.showerror("Login Error", "Invalid Admin Credentials.")

# --- 2. SIGN UP SCREEN ---
class SignUpScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        box = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised", bd=2)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="Create Tenant Account", font=("Arial", 18), bg="white").pack(pady=10)

        grid = tk.Frame(box, bg="white")
        grid.pack(pady=10)

        # Form Fields
        labels = ["Full Name:", "Phone Number:", "Username:", "Password:"]
        self.entries = {}
        
        for i, lbl in enumerate(labels):
            tk.Label(grid, text=lbl, bg="white", width=15, anchor="e").grid(row=i, column=0, pady=8, padx=5)
            ent = ttk.Entry(grid, width=25)
            if "Password" in lbl: ent.config(show="*")
            ent.grid(row=i, column=1, pady=8)
            self.entries[lbl] = ent

        btn_frame = tk.Frame(box, bg="white")
        btn_frame.pack(pady=20, fill="x")
        
        ttk.Button(btn_frame, text="Register", command=self.register).pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=lambda: controller.show_frame(LoginScreen)).pack(side="right", expand=True, fill="x", padx=5)

    def register(self):
        name = self.entries["Full Name:"].get()
        phone = self.entries["Phone Number:"].get()
        user = self.entries["Username:"].get()
        pwd = self.entries["Password:"].get()

        if name and pwd:
            tid = system.sign_up_tenant(name, phone, user, pwd)
            # Clear entries
            for ent in self.entries.values(): ent.delete(0, tk.END)
            
            messagebox.showinfo("Registration Successful", 
                f"Welcome, {name}!\n\n"
                f"🔑 YOUR LOGIN ID IS: {tid}\n\n"
                "Please memorize this ID to login.")
            self.controller.show_frame(LoginScreen)
        else:
            messagebox.showwarning("Incomplete", "Please fill in all fields.")

# --- 3. ADMIN DASHBOARD ---
class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        # Navbar
        nav = tk.Frame(self, bg="#2c3e50", height=60)
        nav.pack(fill="x")
        tk.Label(nav, text="🛠️ Admin Control Panel", fg="white", bg="#2c3e50", font=("Arial", 16, "bold")).pack(side="left", padx=20, pady=15)
        ttk.Button(nav, text="Logout", command=lambda: controller.show_frame(LoginScreen)).pack(side="right", padx=20)

        # Main Content Area
        content = tk.Frame(self, bg="#f0f0f0", padx=20, pady=20)
        content.pack(fill="both", expand=True)

        # Tabs
        nb = ttk.Notebook(content)
        nb.pack(fill="both", expand=True)

        # -- Tab 1: Flats Management --
        self.tab_flats = tk.Frame(nb, bg="white")
        nb.add(self.tab_flats, text="  Manage Flats  ")
        
        # Add Flat Bar
        bar = tk.LabelFrame(self.tab_flats, text="Add New Flat", bg="white", padx=10, pady=10)
        bar.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(bar, text="Flat ID (e.g. F101):").pack(side="left")
        self.fid = ttk.Entry(bar, width=10); self.fid.pack(side="left", padx=5)
        
        ttk.Label(bar, text="Floor:").pack(side="left", padx=(10,0))
        self.flr = ttk.Entry(bar, width=10); self.flr.pack(side="left", padx=5)
        
        ttk.Label(bar, text="Rent Amount:").pack(side="left", padx=(10,0))
        self.rent = ttk.Entry(bar, width=10); self.rent.pack(side="left", padx=5)
        
        ttk.Button(bar, text="+ Create Flat", command=self.add_flat).pack(side="left", padx=20)

        # Flats List
        cols = ("ID", "Floor", "Rent ($)", "Status", "Occupied By")
        self.tree_flats = ttk.Treeview(self.tab_flats, columns=cols, show="headings")
        for c in cols: self.tree_flats.heading(c, text=c)
        self.tree_flats.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # -- Tab 2: Tenant Assignment --
        self.tab_assign = tk.Frame(nb, bg="white")
        nb.add(self.tab_assign, text="  Tenants & Assignment  ")
        
        # Assignment Bar
        abar = tk.LabelFrame(self.tab_assign, text="Assign Flat to Tenant", bg="white", padx=10, pady=10)
        abar.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(abar, text="Tenant ID:").pack(side="left")
        self.atid = ttk.Entry(abar, width=15); self.atid.pack(side="left", padx=5)
        
        ttk.Label(abar, text="Flat ID:").pack(side="left", padx=(10,0))
        self.afid = ttk.Entry(abar, width=15); self.afid.pack(side="left", padx=5)
        
        ttk.Button(abar, text="Assign Now", command=self.assign).pack(side="left", padx=20)
        ttk.Button(abar, text="⬇ Export Financial Report (CSV)", command=self.export).pack(side="right")

        # Tenants List
        tcols = ("Tenant ID", "Name", "Assigned Flat", "Pending Dues ($)")
        self.tree_tenants = ttk.Treeview(self.tab_assign, columns=tcols, show="headings")
        for c in tcols: self.tree_tenants.heading(c, text=c)
        self.tree_tenants.pack(fill="both", expand=True, padx=10, pady=(0,10))

    def refresh(self):
        # Update Flats
        for i in self.tree_flats.get_children(): self.tree_flats.delete(i)
        for f in system.list_flats():
            self.tree_flats.insert("", "end", values=(f.flat_id, f.floor, f.rent, f.status, f.tenant_id or "-"))

        # Update Tenants
        for i in self.tree_tenants.get_children(): self.tree_tenants.delete(i)
        for t in system.list_tenants():
            self.tree_tenants.insert("", "end", values=(t.tenant_id, t.name, t.assigned_flat_id or "Not Assigned", f"{t.get_pending_dues()}"))

    def add_flat(self):
        if system.add_flat(self.fid.get(), self.flr.get(), self.rent.get()):
            messagebox.showinfo("Success", "New Flat Added Successfully!")
            self.refresh()
            self.fid.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Flat ID already exists.")

    def assign(self):
        if system.assign_flat(self.atid.get(), self.afid.get()):
            messagebox.showinfo("Success", f"Flat {self.afid.get()} assigned to {self.atid.get()}!")
            self.refresh()
        else:
            messagebox.showerror("Error", "Assignment Failed.\n1. Check if Tenant ID exists.\n2. Check if Flat ID exists.\n3. Check if Flat is already occupied.")

    def export(self):
        s, p = system.export_payment_history()
        if s: messagebox.showinfo("Export Complete", f"Data saved to:\n{p}")
        else: messagebox.showerror("Export Failed", p)

# --- 4. TENANT DASHBOARD ---
class TenantDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        self.tenant = None

        # Navbar
        self.nav = tk.Frame(self, bg="#0078D7", height=70)
        self.nav.pack(fill="x")
        self.lbl_welcome = tk.Label(self.nav, text="Welcome", bg="#0078D7", fg="white", font=("Arial", 18, "bold"))
        self.lbl_welcome.pack(side="left", padx=20, pady=20)
        ttk.Button(self.nav, text="Logout", command=lambda: controller.show_frame(LoginScreen)).pack(side="right", padx=20)

        # Main Layout
        main = tk.Frame(self, bg="#f0f0f0", padx=30, pady=20)
        main.pack(fill="both", expand=True)

        # -- Left Side: Status Card --
        card = tk.Frame(main, bg="white", relief="raised", bd=1, padx=20, pady=20)
        card.pack(fill="x", pady=10)

        tk.Label(card, text="CURRENT DUES STATUS", font=("Arial", 10, "bold"), fg="#888", bg="white").pack(anchor="w")
        
        self.lbl_due_amt = tk.Label(card, text="$0.00", font=("Arial", 36, "bold"), fg="#27ae60", bg="white")
        self.lbl_due_amt.pack(anchor="center", pady=10)
        
        self.lbl_msg = tk.Label(card, text="You are all caught up!", font=("Arial", 12), fg="#27ae60", bg="white")
        self.lbl_msg.pack(anchor="center")

        self.btn_pay = tk.Button(card, text="💳 PAY RENT NOW", command=self.pay_rent, 
                                 bg="#0078D7", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10, state="disabled")
        self.btn_pay.pack(pady=15)

        # -- Bottom: History --
        tk.Label(main, text="Payment History", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#333").pack(anchor="w", pady=(20, 5))
        
        cols = ("Date", "Month Paid For", "Amount Paid")
        self.tree_hist = ttk.Treeview(main, columns=cols, show="headings", height=8)
        for c in cols: self.tree_hist.heading(c, text=c)
        self.tree_hist.pack(fill="both", expand=True)

    def update_data(self, tenant):
        self.tenant = tenant
        self.lbl_welcome.config(text=f"Welcome, {tenant.name}")
        self.refresh()

    def refresh(self):
        # 1. Update Dues
        dues = self.tenant.get_pending_dues()
        self.lbl_due_amt.config(text=f"${dues:.2f}")

        if dues > 0:
            self.lbl_due_amt.config(fg="#c0392b") # Red color
            self.lbl_msg.config(text=f"Rent due for {datetime.now().strftime('%B')}", fg="#c0392b")
            self.btn_pay.config(state="normal", bg="#0078D7")
        else:
            self.lbl_due_amt.config(fg="#27ae60") # Green color
            self.lbl_msg.config(text="You have no pending dues.", fg="#27ae60")
            self.btn_pay.config(state="disabled", bg="#95a5a6")

        # 2. Update History
        for i in self.tree_hist.get_children(): self.tree_hist.delete(i)
        for p in reversed(self.tenant.payments): # Show newest first
            self.tree_hist.insert("", "end", values=(p.date, p.month, f"${p.amount:.2f}"))

    def pay_rent(self):
        amt = self.tenant.get_pending_dues()
        month = datetime.now().strftime("%B")
        
        # Confirmation Dialog
        if messagebox.askyesno("Confirm Payment", f"Are you sure you want to pay ${amt} for {month}?"):
            # Process Payment
            system.record_payment(self.tenant.tenant_id, amt, month)
            messagebox.showinfo("Payment Successful", "✅ Thank you! Your payment has been recorded.\nA receipt has been saved.")
            self.refresh()

if __name__ == "__main__":
    app = TenantApp()
    app.mainloop()
