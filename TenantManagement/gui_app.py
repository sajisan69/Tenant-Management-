import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from PIL import Image, ImageTk

# --- CONFIGURATION ---
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


def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg="gray")
    entry.bind("<FocusIn>",
               lambda e: (entry.delete(0, "end"), entry.config(fg="black")) if entry.get() == placeholder else None)
    entry.bind("<FocusOut>",
               lambda e: (entry.insert(0, placeholder), entry.config(fg="gray")) if entry.get() == "" else None)


class MainApp(tk.Tk):
    def __init__(self, system):
        super().__init__()
        self.title("Tenant & Building Management System")
        self.geometry("1200x800")
        self.configure(bg=COLOR_BG)
        self.system = system

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#BDC3C7", foreground="black",
                        padding=5)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30, background="white")
        style.map("Treeview", background=[('selected', COLOR_ACCENT)])

        self.container = tk.Frame(self, bg=COLOR_BG)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LoginFrame, SignupFrame, AdminFrame, TenantFrame):
            frame = F(self.container, self, system)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, cont, data=None):
        frame = self.frames[cont]
        if hasattr(frame, "refresh"): frame.refresh(data)
        frame.tkraise()


# --- LOGIN FRAME ---
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller, system):
        super().__init__(parent, bg=COLOR_PRIMARY)
        self.controller = controller
        self.system = system
        self.is_admin_mode = False

        self.card = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised", bd=1)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_title = tk.Label(self.card, text="Welcome Tenant", font=FONT_HEADER, bg="white", fg=COLOR_TEXT)
        self.lbl_title.pack(pady=(0, 20))

        tk.Label(self.card, text="Username / Tenant ID", font=FONT_SUB, bg="white", fg="gray").pack(anchor="w")
        self.e_user = tk.Entry(self.card, font=FONT_BODY, width=35, relief="solid", bd=1)
        self.e_user.pack(pady=(0, 10), ipady=5)

        tk.Label(self.card, text="Password", font=FONT_SUB, bg="white", fg="gray").pack(anchor="w")
        self.e_pass = tk.Entry(self.card, show="•", font=FONT_BODY, width=35, relief="solid", bd=1)
        self.e_pass.pack(pady=(0, 20), ipady=5)

        self.btn_login = ModernButton(self.card, text="LOGIN", command=self.do_login)
        self.btn_login.pack(fill="x", pady=5)

        self.btn_switch = tk.Button(self.card, text="Login as Admin", font=("Segoe UI", 9, "underline"),
                                    bg="white", fg=COLOR_ACCENT, bd=0, cursor="hand2", command=self.toggle_mode)
        self.btn_switch.pack(pady=5)

        tk.Button(self.card, text="Create New Account", font=("Segoe UI", 9),
                  bg="white", fg="gray", bd=0, cursor="hand2",
                  command=lambda: controller.show_frame(SignupFrame)).pack(pady=5)

    def toggle_mode(self):
        self.is_admin_mode = not self.is_admin_mode
        if self.is_admin_mode:
            self.lbl_title.config(text="Welcome Admin")
            self.btn_switch.config(text="Login as Tenant")
        else:
            self.lbl_title.config(text="Welcome Tenant")
            self.btn_switch.config(text="Login as Admin")

    def do_login(self):
        u = self.e_user.get()
        p = self.e_pass.get()
        if self.is_admin_mode:
            if self.system.admin_login(u, p):
                self.controller.show_frame(AdminFrame)
                self.e_pass.delete(0, 'end')
            else:
                messagebox.showerror("Error", "Invalid Admin Credentials")
        else:
            t = self.system.tenant_login(u, p)
            if t:
                self.controller.show_frame(TenantFrame, t)
                self.e_pass.delete(0, 'end')
            else:
                messagebox.showerror("Error", "Invalid Tenant Credentials")


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


# --- ADMIN FRAME ---
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

        menu_items = [
            ("Manage Flats", self.show_flats),
            ("Manage Tenants", self.show_tenants),
            ("Verify Payments", self.show_payments),
            ("Maintenance", self.show_maintenance),
            ("Notices", self.show_notices),
            ("Logout", lambda: controller.show_frame(LoginFrame))
        ]

        for btn_text, cmd in menu_items:
            b = tk.Button(sidebar, text=btn_text, bg=COLOR_PRIMARY, fg="white",
                          activebackground=COLOR_PRIMARY, activeforeground="white",
                          font=("Segoe UI", 12), bd=0, pady=15, command=cmd)
            b.pack(fill="x")

        self.show_flats()

    def clear_content(self):
        for widget in self.content_area.winfo_children(): widget.destroy()

    def show_flats(self):
        self.clear_content()
        tk.Label(self.content_area, text="Flats & Occupancy", font=FONT_HEADER, bg=COLOR_BG).pack(anchor="w", pady=10)

        tabs = ttk.Notebook(self.content_area)
        tabs.pack(fill="both", expand=True, pady=10)

        self.tab_free = tk.Frame(tabs, bg=COLOR_BG, padx=10, pady=10)
        tabs.add(self.tab_free, text="   Free / Available Flats   ")

        self.tab_occ = tk.Frame(tabs, bg=COLOR_BG, padx=10, pady=10)
        tabs.add(self.tab_occ, text="   Occupied Flats (Tenant Details)   ")

        ctrl = tk.Frame(self.tab_free, bg=COLOR_BG)
        ctrl.pack(fill="x", pady=10)
        fid = tk.Entry(ctrl, width=10);
        fid.pack(side="left", padx=5);
        add_placeholder(fid, "ID")
        ffl = tk.Entry(ctrl, width=10);
        ffl.pack(side="left", padx=5);
        add_placeholder(ffl, "Floor")
        frt = tk.Entry(ctrl, width=10);
        frt.pack(side="left", padx=5);
        add_placeholder(frt, "Rent")

        ModernButton(ctrl, text="+ Add Flat", command=lambda: [self.system.add_flat(fid.get(), ffl.get(), frt.get()),
                                                               self.refresh_flats()]).pack(side="left", padx=10)
        tk.Button(ctrl, text="Delete Selected", bg="#E74C3C", fg="white", font=FONT_BODY, relief="flat", padx=10,
                  command=self.del_flat).pack(side="right")

        self.tree_free = ttk.Treeview(self.tab_free, columns=("ID", "Floor", "Rent", "Status"), show="headings")
        for c in ("ID", "Floor", "Rent", "Status"): self.tree_free.heading(c, text=c)
        self.tree_free.pack(fill="both", expand=True)

        self.tree_occ = ttk.Treeview(self.tab_occ,
                                     columns=("Flat ID", "Floor", "Tenant Name", "Tenant ID", "Phone", "Rent"),
                                     show="headings")
        cols = ["Flat ID", "Floor", "Tenant Name", "Tenant ID", "Phone", "Rent"]
        for c in cols: self.tree_occ.heading(c, text=c)
        self.tree_occ.column("Tenant Name", width=150)
        self.tree_occ.column("Phone", width=120)
        self.tree_occ.pack(fill="both", expand=True)

        self.refresh_flats()

    def refresh_flats(self):
        for i in self.tree_free.get_children(): self.tree_free.delete(i)
        for i in self.tree_occ.get_children(): self.tree_occ.delete(i)

        for f in self.system.flats:
            if f.status == "Available":
                self.tree_free.insert("", "end", values=(f.flat_id, f.floor, f.rent, f.status))
            else:
                tenant_details = next((t for t in self.system.tenants if t.tenant_id == f.tenant_id), None)
                t_name = tenant_details.name if tenant_details else "Unknown"
                t_phone = tenant_details.phone if tenant_details else "--"
                t_id = f.tenant_id

                self.tree_occ.insert("", "end", values=(f.flat_id, f.floor, t_name, t_id, t_phone, f.rent))

    def del_flat(self):
        sel = self.tree_free.selection()
        if sel:
            self.system.delete_flat(self.tree_free.item(sel[0])['values'][0])
            self.refresh_flats()
        else:
            messagebox.showwarning("Warning", "Please select a flat from the 'Free/Available' tab to delete.")

    def show_tenants(self):
        self.clear_content()
        tk.Label(self.content_area, text="Tenant Assignment", font=FONT_HEADER, bg=COLOR_BG).pack(anchor="w", pady=10)

        tk.Label(self.content_area, text="(Double-click a tenant to view Verification Info)",
                 font=("Segoe UI", 9, "italic"), bg=COLOR_BG, fg="gray").pack(anchor="w")

        ctrl = tk.Frame(self.content_area, bg=COLOR_BG)
        ctrl.pack(fill="x", pady=10)
        tid = tk.Entry(ctrl, width=15);
        tid.pack(side="left", padx=5);
        add_placeholder(tid, "Tenant ID")
        fid = tk.Entry(ctrl, width=15);
        fid.pack(side="left", padx=5);
        add_placeholder(fid, "Flat ID")
        ModernButton(ctrl, text="Assign Flat",
                     command=lambda: [self.system.assign_flat(tid.get(), fid.get()), self.refresh_tenants()]).pack(
            side="left", padx=10)

        # --- REMOVED "Verified" COLUMN HERE ---
        self.tree_tenants = ttk.Treeview(self.content_area, columns=("ID", "Name", "Phone", "Flat", "Dues"),
                                         show="headings")
        for c in ("ID", "Name", "Phone", "Flat", "Dues"): self.tree_tenants.heading(c, text=c)
        self.tree_tenants.pack(fill="both", expand=True)

        self.tree_tenants.bind("<Double-1>", self.view_tenant_details)

        self.refresh_tenants()

    def refresh_tenants(self):
        for i in self.tree_tenants.get_children(): self.tree_tenants.delete(i)
        for t in self.system.tenants:
            # --- REMOVED Verification status from INSERT call ---
            self.tree_tenants.insert("", "end", values=(t.tenant_id, t.name, t.phone, t.assigned_flat_id or "None",
                                                        t.get_due_amount()))

    def view_tenant_details(self, event):
        item = self.tree_tenants.selection()
        if not item: return
        t_id = self.tree_tenants.item(item[0])['values'][0]

        tenant = next((t for t in self.system.tenants if str(t.tenant_id) == str(t_id)), None)
        if not tenant: return

        top = tk.Toplevel(self)
        top.title(f"Details: {tenant.name}")
        top.geometry("400x450")

        tk.Label(top, text="Tenant Verification Profile", font=("Segoe UI", 14, "bold")).pack(pady=10)

        def row(k, v):
            f = tk.Frame(top, pady=2);
            f.pack(fill="x", padx=20)
            tk.Label(f, text=k, font=("Segoe UI", 10, "bold"), width=15, anchor="w").pack(side="left")
            tk.Label(f, text=v, font=("Segoe UI", 10), wraplength=200, justify="left").pack(side="left")

        row("Name:", tenant.name)
        row("Phone:", tenant.phone)
        row("Tenant ID:", str(tenant.tenant_id))

        tk.Label(top, text="-------------------------------").pack(pady=5)

        if hasattr(tenant, 'profile_data') and tenant.profile_data:
            data = tenant.profile_data
            row("Job:", data.get("Job", "-"))
            row("Hometown:", data.get("Hometown", "-"))
            row("NID No:", data.get("NID", "-"))
            row("Perm. Address:", data.get("Address", "-"))

            tk.Label(top, text="✅ VERIFIED", fg="green", font=("Segoe UI", 16, "bold")).pack(pady=20)
        else:
            tk.Label(top, text="❌ NOT VERIFIED", fg="red", font=("Segoe UI", 16, "bold")).pack(pady=20)
            tk.Label(top, text="Tenant has not submitted details yet.").pack()

    def show_payments(self):
        self.clear_content()
        tk.Label(self.content_area, text="Payment Verification", font=FONT_HEADER, bg=COLOR_BG).pack(anchor="w",
                                                                                                     pady=10)
        self.tree_pay = ttk.Treeview(self.content_area, columns=("Tenant ID", "Amount", "Month", "Trx ID", "Status"),
                                     show="headings")
        for c in ("Tenant ID", "Amount", "Month", "Trx ID", "Status"): self.tree_pay.heading(c, text=c)
        self.tree_pay.pack(fill="both", expand=True, pady=10)
        ModernButton(self.content_area, text="Approve Selected", command=self.approve_pay).pack(pady=5)
        self.refresh_payments()

    def refresh_payments(self):
        for i in self.tree_pay.get_children(): self.tree_pay.delete(i)
        for t in self.system.tenants:
            for p in t.payments:
                if p.status == "Pending":
                    self.tree_pay.insert("", "end", values=(t.tenant_id, p.amount, p.month, p.transaction_id, p.status))

    def approve_pay(self):
        sel = self.tree_pay.selection()
        if sel:
            item = self.tree_pay.item(sel[0])['values']
            self.system.approve_payment(str(item[0]), str(item[3]))
            messagebox.showinfo("Success", "Payment Approved!")
            self.refresh_payments()

    def show_maintenance(self):
        self.clear_content()
        tk.Label(self.content_area, text="Maintenance Complaints", font=FONT_HEADER, bg=COLOR_BG).pack(anchor="w",
                                                                                                       pady=10)
        tk.Label(self.content_area, text="(Double-click a row to read full details)", font=("Segoe UI", 9, "italic"),
                 bg=COLOR_BG, fg="gray").pack(anchor="w")

        tree_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        tree_frame.pack(fill="both", expand=True, pady=10)

        cols = ("Tenant ID", "Name", "Description", "Date", "Status")
        self.tree_comp = ttk.Treeview(tree_frame, columns=cols, show="headings")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_comp.yview)
        self.tree_comp.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self.tree_comp.pack(side="left", fill="both", expand=True)

        self.tree_comp.heading("Tenant ID", text="Tenant ID")
        self.tree_comp.column("Tenant ID", width=70, anchor="center", stretch=False)
        self.tree_comp.heading("Name", text="Tenant Name")
        self.tree_comp.column("Name", width=120, anchor="w")
        self.tree_comp.heading("Description", text="Description")
        self.tree_comp.column("Description", width=350, anchor="w")
        self.tree_comp.heading("Date", text="Date")
        self.tree_comp.column("Date", width=100, anchor="center")
        self.tree_comp.heading("Status", text="Status")
        self.tree_comp.column("Status", width=100, anchor="center")

        btn_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        btn_frame.pack(fill="x", pady=5)
        ModernButton(btn_frame, text="Mark as Resolved", command=self.resolve_comp).pack(side="left", padx=5)

        self.tree_comp.bind("<Double-1>", self.view_full_complaint)
        self.refresh_maintenance()

    def refresh_maintenance(self):
        for i in self.tree_comp.get_children(): self.tree_comp.delete(i)
        for c in self.system.complaints:
            self.tree_comp.insert("", "end", iid=c.complaint_id,
                                  values=(c.tenant_id, c.tenant_name, c.description, c.date, c.status))

    def resolve_comp(self):
        sel = self.tree_comp.selection()
        if sel:
            cid = sel[0]
            self.system.resolve_complaint(cid)
            self.refresh_maintenance()
            messagebox.showinfo("Success", "Complaint marked as Resolved.")

    def view_full_complaint(self, event):
        item_id = self.tree_comp.identify_row(event.y)
        if not item_id: return

        vals = self.tree_comp.item(item_id)['values']

        top = tk.Toplevel(self)
        top.title(f"Complaint Details")
        top.geometry("400x300")

        tk.Label(top, text=f"Submitted by: {vals[1]} ({vals[0]})", font=("Segoe UI", 12, "bold")).pack(pady=10)
        tk.Label(top, text=f"Date: {vals[3]}", font=("Segoe UI", 10)).pack()

        tk.Label(top, text="--- Issue Description ---", font=("Segoe UI", 10, "bold"), fg="gray").pack(pady=(20, 5))
        txt = tk.Text(top, height=8, width=40, font=("Segoe UI", 11), wrap="word", relief="flat", bg="#ECF0F1")
        txt.insert("1.0", vals[2])
        txt.config(state="disabled")
        txt.pack(padx=20, pady=5)
        tk.Button(top, text="Close", command=top.destroy).pack(pady=10)

    # --- NOTICES PAGE (ADMIN) ---
    def show_notices(self):
        self.clear_content()
        tk.Label(self.content_area, text="Manage Notice Board", font=FONT_HEADER, bg=COLOR_BG).pack(anchor="w", pady=10)
        ctrl = tk.Frame(self.content_area, bg=COLOR_BG)
        ctrl.pack(fill="x", pady=10)
        e_msg = tk.Entry(ctrl, width=50);
        e_msg.pack(side="left", padx=5);
        add_placeholder(e_msg, "Type announcement here...")
        ModernButton(ctrl, text="Post Notice",
                     command=lambda: [self.system.add_notice(e_msg.get()), self.refresh_notices(),
                                      e_msg.delete(0, "end")]).pack(side="left", padx=10)
        tk.Button(ctrl, text="Delete Selected", bg="#E74C3C", fg="white", font=FONT_BODY, relief="flat", padx=10,
                  command=self.del_notice).pack(side="right")
        self.tree_notice = ttk.Treeview(self.content_area, columns=("Date", "Message"), show="headings")
        self.tree_notice.heading("Date", text="Date");
        self.tree_notice.heading("Message", text="Message")
        self.tree_notice.column("Message", width=500)
        self.tree_notice.pack(fill="both", expand=True, pady=10)
        self.refresh_notices()

    def refresh_notices(self):
        for i in self.tree_notice.get_children(): self.tree_notice.delete(i)
        for n in self.system.notices:
            self.tree_notice.insert("", "end", values=(n.date, n.message))

    def del_notice(self):
        sel = self.tree_notice.selection()
        if sel:
            idx = self.tree_notice.index(sel[0])
            self.system.delete_notice(idx)
            self.refresh_notices()


# --- TENANT FRAME ---
class TenantFrame(tk.Frame):
    def __init__(self, parent, controller, system):
        super().__init__(parent, bg=COLOR_BG)
        self.system = system;
        self.tenant = None;
        self.controller = controller

        # --- HEADER (UPDATED) ---
        self.header = tk.Frame(self, bg=COLOR_PRIMARY, height=80)
        self.header.pack(fill="x")

        # Welcome Text (Left)
        self.lbl_welcome = tk.Label(self.header, text="Welcome", bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 18))
        self.lbl_welcome.pack(side="left", padx=20, pady=20)

        # Right Side Container (Holds Verification + Logout)
        right_header = tk.Frame(self.header, bg=COLOR_PRIMARY)
        right_header.pack(side="right", padx=20, pady=10)

        # Logout Button (Far Right)
        tk.Button(right_header, text="Logout", bg="#E74C3C", fg="white", relief="flat", padx=10,
                  command=lambda: controller.show_frame(LoginFrame)).pack(side="right", fill="y", padx=(10, 0))

        # Verification Box (Beside Logout, Status Below Button)
        self.verify_box = tk.Frame(right_header, bg=COLOR_PRIMARY)
        self.verify_box.pack(side="right")

        self.btn_verify = tk.Button(self.verify_box, text="Complete Verification", bg="#E67E22", fg="white",
                                    font=("Segoe UI", 8), relief="flat", command=self.fill_verification_form)
        self.btn_verify.pack(anchor="e")

        self.lbl_verify_status = tk.Label(self.verify_box, text="Status: ?", bg=COLOR_PRIMARY, fg="white",
                                          font=("Segoe UI", 8))
        self.lbl_verify_status.pack(anchor="e", pady=(2, 0))

        # --- Quick Notice Bar ---
        self.notice_bar = tk.Label(self, text="📢 No new notices.", bg="#F1C40F", fg=COLOR_TEXT,
                                   font=("Segoe UI", 10, "bold"), pady=5)
        self.notice_bar.pack(fill="x")

        # --- Main Area ---
        main = tk.Frame(self, bg=COLOR_BG, padx=40, pady=20)
        main.pack(fill="both", expand=True)

        # Info Card
        info_card = tk.Frame(main, bg="white", padx=20, pady=20, relief="solid", bd=1)
        info_card.pack(fill="x", pady=10)

        # Left side of info card (Personal Details)
        self.lbl_details = tk.Label(info_card, text="--", font=FONT_SUB, bg="white", justify="left")
        self.lbl_details.pack(side="left", anchor="w")

        # Right side of info card (Financial Stats)
        self.stats_frame = tk.Frame(info_card, bg="white")
        self.stats_frame.pack(side="right", anchor="e")

        self.lbl_rent = tk.Label(self.stats_frame, text="Rent: ৳0", font=("Segoe UI", 14), fg=COLOR_TEXT, bg="white")
        self.lbl_rent.pack(anchor="e")

        self.lbl_paid = tk.Label(self.stats_frame, text="Paid: ৳0", font=("Segoe UI", 14), fg="#27AE60", bg="white")
        self.lbl_paid.pack(anchor="e")

        self.lbl_total_due = tk.Label(self.stats_frame, text="Due: ৳0", font=("Segoe UI", 16, "bold"), fg="#E74C3C",
                                      bg="white")
        self.lbl_total_due.pack(anchor="e")

        # --- ACTION BUTTONS ---
        btn_frame = tk.Frame(main, bg=COLOR_BG)
        btn_frame.pack(fill="x", pady=20)

        # Pay Button Section with Status Label
        pay_section = tk.Frame(btn_frame, bg=COLOR_BG)
        pay_section.pack(side="left", padx=5)

        self.btn_pay = ModernButton(pay_section, text="Make Payment (QR)", command=self.pay)
        self.btn_pay.pack()

        self.lbl_pay_status = tk.Label(pay_section, text="", font=("Segoe UI", 9, "bold"), bg=COLOR_BG)
        self.lbl_pay_status.pack(pady=2)

        # Right Side Actions
        ModernButton(btn_frame, text="📋 Notice Board", command=self.view_notices).pack(side="right", padx=5)
        ModernButton(btn_frame, text="🛠️ Report Issue", command=self.report_issue).pack(side="right", padx=5)

        # --- PAYMENT HISTORY & RECEIPTS ---
        tk.Label(main, text="Payment History", font=("Segoe UI", 14, "bold"), bg=COLOR_BG).pack(anchor="w",
                                                                                                pady=(20, 5))

        self.tree = ttk.Treeview(main, columns=("Date", "Month", "Amount", "Status"), show="headings", height=6)
        self.tree.heading("Date", text="Date");
        self.tree.heading("Month", text="Month")
        self.tree.heading("Amount", text="Amount");
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill="x")

        # Receipt Button
        dl_frame = tk.Frame(main, bg=COLOR_BG)
        dl_frame.pack(fill="x", pady=5)
        tk.Label(dl_frame, text="* Select an 'Approved' payment above to download receipt", fg="gray", bg=COLOR_BG,
                 font=("Segoe UI", 9, "italic")).pack(side="left")
        ModernButton(dl_frame, text="Download Receipt", command=self.download_selected).pack(side="right")

    def refresh(self, tenant):
        self.tenant = tenant
        self.lbl_welcome.config(text=f"Welcome, {tenant.name}")
        self.lbl_details.config(
            text=f"Tenant ID: {tenant.tenant_id}\nPhone: {tenant.phone}\nFlat: {tenant.assigned_flat_id or 'Not Assigned'}")

        # --- UPDATED: Check verification status and update Header UI ---
        if hasattr(tenant, 'profile_data') and tenant.profile_data:
            self.lbl_verify_status.config(text="Verified ✅", fg="#2ECC71")  # Greenish text
            self.btn_verify.pack_forget()  # Hide button
        else:
            self.lbl_verify_status.config(text="Not Verified ❌", fg="#F1C40F")  # Yellow/Orange text
            self.btn_verify.pack(anchor="e")  # Show button

        if self.system.notices:
            last = self.system.notices[0]
            self.notice_bar.config(text=f"📢 NOTICE ({last.date}): {last.message}")
        else:
            self.notice_bar.config(text="📢 No new notices.")

        rent = tenant.flat_rent
        due = tenant.get_due_amount()

        current_month = datetime.now().strftime("%B")
        paid_this_month = 0
        for p in tenant.payments:
            if p.month == current_month and p.status == "Approved":
                paid_this_month += int(p.amount)

        self.lbl_rent.config(text=f"Rent: ৳{rent}")
        self.lbl_paid.config(text=f"Paid (This Month): ৳{paid_this_month}")
        self.lbl_total_due.config(text=f"Total Due: ৳{due}", fg="#E74C3C" if due > 0 else "#27AE60")

        status_text = f"Due for {current_month} ❌"
        status_fg = "#E74C3C"

        for p in tenant.payments:
            if p.month == current_month:
                if p.status == "Approved":
                    status_text = f"Payment Done ({current_month}) ✅"
                    status_fg = "#27AE60"
                elif p.status == "Pending":
                    status_text = "Pending Approval ⏳"
                    status_fg = "#F39C12"
                break

        self.lbl_pay_status.config(text=status_text, fg=status_fg)

        for i in self.tree.get_children(): self.tree.delete(i)
        for p in reversed(tenant.payments):
            self.tree.insert("", "end", values=(p.date, p.month, f"৳{p.amount}", p.status))

    def fill_verification_form(self):
        top = tk.Toplevel(self)
        top.title("Verification Form")
        top.geometry("400x500")

        tk.Label(top, text="Complete Your Profile", font=("Segoe UI", 16, "bold")).pack(pady=20)

        entries = {}
        fields = ["Job / Occupation", "Hometown", "NID Number", "Permanent Address"]

        for f in fields:
            tk.Label(top, text=f, anchor="w", font=("Segoe UI", 10)).pack(fill="x", padx=30, pady=(10, 0))
            e = tk.Entry(top, font=("Segoe UI", 10))
            e.pack(fill="x", padx=30, pady=5)
            entries[f] = e

        def save():
            data = {
                "Job": entries["Job / Occupation"].get(),
                "Hometown": entries["Hometown"].get(),
                "NID": entries["NID Number"].get(),
                "Address": entries["Permanent Address"].get()
            }
            if all(data.values()):
                self.tenant.profile_data = data
                messagebox.showinfo("Success", "Profile Updated! Verification Pending.")
                self.refresh(self.tenant)
                top.destroy()
            else:
                messagebox.showerror("Error", "All fields are required.")

        ModernButton(top, text="Submit Verification", command=save).pack(pady=30)

    def view_notices(self):
        top = tk.Toplevel(self)
        top.title("Building Notices")
        top.geometry("600x400")
        tk.Label(top, text="Notice Board", font=("Segoe UI", 16, "bold")).pack(pady=10)
        cols = ("Date", "Message")
        tree = ttk.Treeview(top, columns=cols, show="headings")
        tree.heading("Date", text="Date");
        tree.column("Date", width=120, anchor="center")
        tree.heading("Message", text="Notice");
        tree.column("Message", width=450, anchor="w")
        vsb = ttk.Scrollbar(top, orient="vertical", command=tree.yview);
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10);
        vsb.pack(side="right", fill="y", pady=10)
        for n in self.system.notices: tree.insert("", "end", values=(n.date, n.message))
        tk.Button(top, text="Close", command=top.destroy, width=20).pack(pady=10)

    def pay(self):
        rent_amount = self.tenant.flat_rent
        if rent_amount <= 0: return messagebox.showwarning("Error", "No rent due.")

        top = tk.Toplevel(self)
        top.geometry("350x650")
        top.title("Scan & Pay")

        tk.Label(top, text=f"Pay Rent: ৳{rent_amount}", font=("Segoe UI", 14, "bold")).pack(pady=10)

        try:
            load = Image.open("qrcode.jpg")
            load = load.resize((250, 250))
            self.qr_image = ImageTk.PhotoImage(load)
            tk.Label(top, image=self.qr_image).pack(pady=10)
        except Exception:
            err_frame = tk.Frame(top, bg="black", width=250, height=250)
            err_frame.pack(pady=10);
            err_frame.pack_propagate(False)
            tk.Label(err_frame, text="qrcode.jpg not found", fg="white", bg="black").place(relx=0.5, rely=0.5,
                                                                                           anchor="center")

        instr_text = "Instructions:\n1. Scan the QR code and make payment.\n2. Copy the Transaction ID from your banking app.\n3. Paste the Transaction ID below.\n4. Wait for Admin approval."
        tk.Label(top, text=instr_text, font=("Segoe UI", 9), justify="left", fg="#555", bg="#f0f0f0", relief="groove",
                 padx=10, pady=10).pack(pady=10, padx=20, fill="x")

        tk.Label(top, text="Enter Transaction ID:", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        trx = tk.Entry(top, font=("Segoe UI", 12), width=20, justify="center")
        trx.pack(pady=5)

        def confirm():
            if not trx.get(): return messagebox.showwarning("Error", "Transaction ID is required.")
            if self.system.add_payment(self.tenant.tenant_id, rent_amount, datetime.now().strftime("%B"), trx.get()):
                messagebox.showinfo("Submitted", "Payment Pending Approval.")
                self.refresh(self.tenant)
                top.destroy()

        ModernButton(top, text="Submit", command=confirm).pack(pady=20)

    def download_selected(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("Select Payment",
                                                  "Please select a payment row from the history table first.")
        item = self.tree.item(sel[0])['values']
        status = item[3]
        if status != "Approved": return messagebox.showerror("Error",
                                                             "Receipts are only available for 'Approved' payments.")
        f = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"Receipt_{item[1]}.txt")
        if f:
            with open(f, "w") as file:
                file.write(
                    f"--- RENT RECEIPT ---\nTenant Name: {self.tenant.name}\nTenant ID:   {self.tenant.tenant_id}\nDate Paid:   {item[0]}\nRent Month:  {item[1]}\nAmount:      {item[2]}\nStatus:      PAID (Verified)\n--------------------\nThank you for your payment.")
            messagebox.showinfo("Success", "Receipt Downloaded Successfully.")

    def report_issue(self):
        desc = simpledialog.askstring("Report Issue", "Describe your problem (e.g. Leaky tap):")
        if desc:
            self.system.add_complaint(self.tenant.tenant_id, self.tenant.name, desc)
            messagebox.showinfo("Success", "Complaint submitted to Admin.")
