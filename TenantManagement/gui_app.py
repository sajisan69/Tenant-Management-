import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

COLOR_PRIMARY = "#2C3E50"
COLOR_ACCENT = "#2980B9"
COLOR_BG = "#ECF0F1"
COLOR_TEXT = "#2C3E50"
FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUB = ("Segoe UI", 12)
FONT_BODY = ("Segoe UI", 10)

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = COLOR_ACCENT
        self.config(
            bg=self.default_bg, fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat", pady=8, padx=15,
            cursor="hand2",
            activebackground=self.default_bg,
            activeforeground="white"
        )
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def on_hover(self, e):
        self.config(bg=self.default_bg)

    def on_leave(self, e):
        self.config(bg=self.default_bg)

def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg="gray")
    entry.bind("<FocusIn>", lambda e: (entry.delete(0, "end"), entry.config(fg="black"))
               if entry.get() == placeholder else None)
    entry.bind("<FocusOut>", lambda e: (entry.insert(0, placeholder), entry.config(fg="gray"))
               if entry.get() == "" else None)

class MainApp(tk.Tk):
    def __init__(self, system):
        super().__init__()
        self.title("Tenant & Building Management System")
        self.geometry("1200x800")
        self.configure(bg=COLOR_BG)
        self.system = system

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#BDC3C7", foreground="black", padding=5)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30, background="white")
        style.map("Treeview", background=[('selected', COLOR_ACCENT)])

        self.container = tk.Frame(self, bg=COLOR_BG)
        self.container.pack(fill="both", expand=True)
        self.frames = {}

        for F in (LoginFrame, SignupFrame, AdminFrame, TenantFrame):
            frame = F(self.container, self, system)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, cont, data=None):
        frame = self.frames[cont]
        if hasattr(frame, "refresh"):
            frame.refresh(data)
        frame.tkraise()

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller, system):
        super().__init__(parent, bg=COLOR_PRIMARY)
        self.controller = controller
        self.system = system

        card = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised", bd=1)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Welcome Back", font=FONT_HEADER, bg="white", fg=COLOR_TEXT).pack(pady=(0, 20))

        self.notebook = ttk.Notebook(card)
        self.notebook.pack(fill="x", pady=10)

        t_frame = tk.Frame(self.notebook, bg="white", pady=15)
        self.notebook.add(t_frame, text="  Tenant Login  ")
        self.create_form(t_frame, "Username", "Password", self.do_t_login)

        a_frame = tk.Frame(self.notebook, bg="white", pady=15)
        self.notebook.add(a_frame, text="  Admin Login  ")
        self.create_form(a_frame, "Admin ID", "Password", self.do_a_login)

        tk.Button(card, text="Create New Tenant Account", font=("Segoe UI", 9, "underline"),
                  bg="white", fg=COLOR_ACCENT, bd=0, cursor="hand2",
                  command=lambda: controller.show_frame(SignupFrame)).pack(pady=10)

    def create_form(self, parent, lbl1, lbl2, cmd):
        tk.Label(parent, text=lbl1, font=FONT_SUB, bg="white", fg="gray").pack(anchor="w")
        e1 = tk.Entry(parent, font=FONT_BODY, width=30, relief="solid", bd=1)
        e1.pack(pady=(0, 10), ipady=5)

        tk.Label(parent, text=lbl2, font=FONT_SUB, bg="white", fg="gray").pack(anchor="w")
        e2 = tk.Entry(parent, show="•", font=FONT_BODY, width=30, relief="solid", bd=1)
        e2.pack(pady=(0, 15), ipady=5)

        ModernButton(parent, text="LOGIN", command=lambda: cmd(e1.get(), e2.get())).pack(fill="x")

    def do_t_login(self, u, p):
        t = self.system.tenant_login(u, p)
        if t:
            self.controller.show_frame(TenantFrame, t)
        else:
            messagebox.showerror("Login Failed", "Invalid Tenant credentials")

    def do_a_login(self, u, p):
        if self.system.admin_login(u, p):
            self.controller.show_frame(AdminFrame)
        else:
            messagebox.showerror("Login Failed", "Invalid Admin credentials")

class SignupFrame(tk.Frame):
    def __init__(self, parent, controller, system):
        super().__init__(parent, bg=COLOR_BG)
        card = tk.Frame(self, bg="white", padx=40, pady=40, relief="groove")
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="New Account", font=FONT_HEADER, bg="white").pack(pady=(0, 20))

        self.entries = {}
        for label in ["Name", "Phone", "Username", "Password"]:
            tk.Label(card, text=label, bg="white", anchor="w").pack(fill="x")
            e = tk.Entry(card, width=35, relief="solid", bd=1)
            if label == "Password": e.config(show="•")
            e.pack(pady=5, ipady=3)
            self.entries[label] = e

        ModernButton(card, text="REGISTER", command=lambda: self.register(controller, system)).pack(fill="x", pady=20)
        tk.Button(card, text="Back to Login", bg="white", bd=0, fg="gray",
                  command=lambda: controller.show_frame(LoginFrame)).pack()

    def register(self, controller, system):
        vals = {k: v.get() for k, v in self.entries.items()}
        if all(vals.values()):
            system.register_tenant(vals["Name"], vals["Phone"], vals["Username"], vals["Password"])
            messagebox.showinfo("Success", "Account created! Please login.")
            controller.show_frame(LoginFrame)
        else:
            messagebox.showerror("Error", "All fields are required.")

class AdminFrame(tk.Frame):
    def __init__(self, parent, controller, system):
        super().__init__(parent, bg=COLOR_BG)
        self.system = system

        sidebar = tk.Frame(self, bg=COLOR_PRIMARY, width=250)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Admin\nPanel", bg=COLOR_PRIMARY, fg="white",
                 font=("Segoe UI", 20, "bold"), pady=30).pack()

        self.content_area = tk.Frame(self, bg=COLOR_BG, padx=20, pady=20)
        self.content_area.pack(side="right", fill="both", expand=True)

        for btn_text, cmd in [("Manage Flats", self.show_flats),
                              ("Manage Tenants", self.show_tenants),
                              ("Logout", lambda: controller.show_frame(LoginFrame))]:
            b = tk.Button(sidebar, text=btn_text, bg=COLOR_PRIMARY, fg="white",
                          font=("Segoe UI", 12), bd=0, pady=15, command=cmd)
            b.pack(fill="x")

        self.show_flats()

    def clear_content(self):
        for widget in self.content_area.winfo_children(): widget.destroy()

    def show_flats(self):
        self.clear_content()
        tk.Label(self.content_area, text="Flats Management", font=FONT_HEADER, bg=COLOR_BG).pack(anchor="w", pady=10)

        ctrl = tk.Frame(self.content_area, bg=COLOR_BG)
        ctrl.pack(fill="x", pady=10)

        fid = tk.Entry(ctrl, width=10); fid.pack(side="left", padx=5); add_placeholder(fid, "ID")
        ffl = tk.Entry(ctrl, width=10); ffl.pack(side="left", padx=5); add_placeholder(ffl, "Floor")
        frt = tk.Entry(ctrl, width=10); frt.pack(side="left", padx=5); add_placeholder(frt, "Rent")

        ModernButton(ctrl, text="+ Add Flat", command=lambda: [self.system.add_flat(fid.get(), ffl.get(), frt.get()),
                                                               self.refresh_flats()]).pack(side="left", padx=10)
        tk.Button(ctrl, text="Delete Selected", bg="#E74C3C", fg="white", font=FONT_BODY, relief="flat", padx=10,
                  command=self.del_flat).pack(side="right")

        cols = ("ID", "Floor", "Rent", "Status", "Tenant")
        self.tree_flats = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: self.tree_flats.heading(c, text=c)
        self.tree_flats.pack(fill="both", expand=True)
        self.refresh_flats()

    def refresh_flats(self):
        for i in self.tree_flats.get_children(): self.tree_flats.delete(i)
        for f in self.system.flats:
            self.tree_flats.insert("", "end", values=(f.flat_id, f.floor, f.rent, f.status, f.tenant_id or "-"))

    def del_flat(self):
        sel = self.tree_flats.selection()
        if sel:
            self.system.delete_flat(self.tree_flats.item(sel[0])['values'][0])
            self.refresh_flats()

    def show_tenants(self):
        self.clear_content()
        tk.Label(self.content_area, text="Tenant Assignment", font=FONT_HEADER, bg=COLOR_BG).pack(anchor="w", pady=10)

        ctrl = tk.Frame(self.content_area, bg=COLOR_BG)
        ctrl.pack(fill="x", pady=10)

        tid = tk.Entry(ctrl, width=15); tid.pack(side="left", padx=5); add_placeholder(tid, "Tenant ID")
        fid = tk.Entry(ctrl, width=15); fid.pack(side="left", padx=5); add_placeholder(fid, "Flat ID")

        ModernButton(ctrl, text="Assign Flat",
                     command=lambda: [self.system.assign_flat(tid.get(), fid.get()), self.refresh_tenants()]).pack(side="left", padx=10)

        cols = ("ID", "Name", "Phone", "Flat", "Dues")
        self.tree_tenants = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: self.tree_tenants.heading(c, text=c)
        self.tree_tenants.pack(fill="both", expand=True)
        self.refresh_tenants()

    def refresh_tenants(self):
        for i in self.tree_tenants.get_children(): self.tree_tenants.delete(i)
        for t in self.system.tenants:
            self.tree_tenants.insert("", "end", values=(t.tenant_id, t.name, t.phone, t.assigned_flat_id or "None",
                                                        t.get_due_amount()))

class TenantFrame(tk.Frame):
    def __init__(self, parent, controller, system):
        super().__init__(parent, bg=COLOR_BG)
        self.system = system
        self.tenant = None
        self.controller = controller

        self.header = tk.Frame(self, bg=COLOR_PRIMARY, height=80)
        self.header.pack(fill="x")
        self.lbl_welcome = tk.Label(self.header, text="Welcome", bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 18))
        self.lbl_welcome.pack(side="left", padx=20, pady=20)
        tk.Button(self.header, text="Logout", bg="#E74C3C", fg="white", relief="flat", padx=10,
                  command=lambda: controller.show_frame(LoginFrame)).pack(side="right", padx=20)

        main = tk.Frame(self, bg=COLOR_BG, padx=40, pady=40)
        main.pack(fill="both", expand=True)

        info_card = tk.Frame(main, bg="white", padx=20, pady=20, relief="solid", bd=1)
        info_card.pack(fill="x", pady=10)
        self.lbl_details = tk.Label(info_card, text="--", font=FONT_SUB, bg="white", justify="left")
        self.lbl_details.pack(anchor="w")
        self.lbl_due = tk.Label(info_card, text="Due: $0", font=("Segoe UI", 24, "bold"), fg="#E74C3C", bg="white")
        self.lbl_due.pack(anchor="e")

        btn_frame = tk.Frame(main, bg=COLOR_BG)
        btn_frame.pack(fill="x", pady=20)
        ModernButton(btn_frame, text="Make Payment (QR)", command=self.pay).pack(side="left", padx=5)
        ModernButton(btn_frame, text="Download Receipt", command=self.download).pack(side="left", padx=5)

        tk.Label(main, text="Payment History", font=("Segoe UI", 14, "bold"), bg=COLOR_BG).pack(anchor="w")
        self.tree = ttk.Treeview(main, columns=("Date", "Month", "Amount"), show="headings", height=8)
        self.tree.heading("Date", text="Date")
        self.tree.heading("Month", text="Month")
        self.tree.heading("Amount", text="Amount")
        self.tree.pack(fill="x", pady=5)

    def refresh(self, tenant):
        self.tenant = tenant
        self.lbl_welcome.config(text=f"Welcome, {tenant.name}")
        self.lbl_details.config(
            text=f"Tenant ID: {tenant.tenant_id}\nPhone: {tenant.phone}\nFlat: {tenant.assigned_flat_id or 'Not Assigned'}")
        due = tenant.get_due_amount()
        self.lbl_due.config(text=f"Due: ৳{due}", fg="#E74C3C" if due > 0 else "#27AE60")

        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in reversed(tenant.payments):
            self.tree.insert("", "end", values=(p.date, p.month, f"৳{p.amount}"))

    def pay(self):
        rent_amount = self.tenant.flat_rent
        if rent_amount <= 0:
            messagebox.showwarning("Payment Error", "You do not have an assigned flat or rent amount is 0.")
            return

        top = tk.Toplevel(self)
        top.geometry("300x400")
        top.title("Scan & Pay")
        tk.Label(top, text=f"Pay Rent: ৳{rent_amount}", font=("Segoe UI", 14, "bold")).pack(pady=10)
        tk.Label(top, text="[ QR CODE ]", bg="black", fg="white", width=20, height=10).pack(pady=10)
        tk.Label(top, text="(Scan with bKash/Nagad)", font=("Segoe UI", 10)).pack()

        def confirm():
            current_month = datetime.now().strftime("%B")
            success = self.system.add_payment(self.tenant.tenant_id, rent_amount, current_month)
            if success:
                messagebox.showinfo("Success", "Payment Verified and Saved!")
                self.refresh(self.tenant)
                top.destroy()
            else:
                messagebox.showerror("Error", "Could not save payment. Check console.")

        ModernButton(top, text="I have Paid", command=confirm).pack(pady=20)

    def download(self):
        if not self.tenant.payments:
            return messagebox.showinfo("Info", "No payments found.")
        last = self.tenant.payments[-1]
        f = filedialog.asksaveasfilename(defaultextension=".txt")
        if f:
            with open(f, "w") as file:
                file.write(f"RECEIPT\nTenant: {self.tenant.name}\nAmount: {last.amount}\nDate: {last.date}")
