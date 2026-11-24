"""Employee Management System - Tkinter frontend.

Run this file (python gui.py) from the same folder as Employee.py and employee_db.py.
It reuses your existing backend: Emp.make_entry / deletion / show_all_employee / promote_employee.
"""
import re
import tkinter as tk
from tkinter import ttk, messagebox

from employee_db import cursor, mydb, create_Employee_table, create_promotion_table
from Employee import Emp

# ---------- theme ----------
BG = "#f1f5f9"
SIDEBAR = "#1e293b"
SIDEBAR_HOVER = "#334155"
ACCENT = "#6366f1"
ACCENT_DARK = "#4f46e5"
DANGER = "#ef4444"
DANGER_DARK = "#dc2626"
SUCCESS = "#10b981"
CARD = "#ffffff"
TEXT = "#0f172a"
MUTED = "#64748b"
FONT = "Segoe UI"


def get_employee(eid):
    cursor.execute(
        "SELECT E_id, name, email, City, gender, Position, Salary FROM Employee WHERE E_id=%s",
        (eid,),
    )
    row = cursor.fetchone()
    mydb.commit()
    return row


def money(v):
    return f"₹ {float(v):,.2f}"


class FlatButton(tk.Button):
    def __init__(self, master, text, command, bg=ACCENT, hover=ACCENT_DARK, **kw):
        super().__init__(
            master, text=text, command=command, bg=bg, fg="white",
            activebackground=hover, activeforeground="white", relief="flat",
            bd=0, cursor="hand2", font=(FONT, 10, "bold"), padx=18, pady=8, **kw,
        )
        self.bind("<Enter>", lambda e: self.config(bg=hover))
        self.bind("<Leave>", lambda e: self.config(bg=bg))


class Page(tk.Frame):
    """Base page with a title bar."""

    def __init__(self, master, app, title, subtitle=""):
        super().__init__(master, bg=BG)
        self.app = app
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=30, pady=(25, 10))
        tk.Label(head, text=title, font=(FONT, 22, "bold"), bg=BG, fg=TEXT).pack(anchor="w")
        if subtitle:
            tk.Label(head, text=subtitle, font=(FONT, 10), bg=BG, fg=MUTED).pack(anchor="w")

    def on_show(self):
        pass


# ---------- Employees (display) ----------
class EmployeesPage(Page):
    COLS = [("E_id", "ID", 60), ("name", "Name", 150), ("email", "Email", 220),
            ("city", "City", 110), ("gender", "Gender", 70),
            ("position", "Position", 160), ("salary", "Salary", 120)]

    def __init__(self, master, app):
        super().__init__(master, app, "Employees", "All employees stored in the database")
        self.records = []
        self.sort_rev = {}

        # stat cards
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", padx=30, pady=5)
        self.stat_vars = {}
        for i, (key, label, color) in enumerate([
            ("count", "Total Employees", ACCENT),
            ("payroll", "Total Payroll", SUCCESS),
            ("avg", "Average Salary", "#f59e0b"),
        ]):
            c = tk.Frame(cards, bg=CARD, highlightbackground="#e2e8f0", highlightthickness=1)
            c.grid(row=0, column=i, padx=(0, 15), sticky="ew")
            cards.grid_columnconfigure(i, weight=1)
            tk.Frame(c, bg=color, height=4).pack(fill="x")
            tk.Label(c, text=label, font=(FONT, 9), bg=CARD, fg=MUTED).pack(anchor="w", padx=15, pady=(10, 0))
            v = tk.StringVar(value="-")
            self.stat_vars[key] = v
            tk.Label(c, textvariable=v, font=(FONT, 17, "bold"), bg=CARD, fg=TEXT).pack(anchor="w", padx=15, pady=(0, 12))

        # toolbar
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=30, pady=(15, 5))
        tk.Label(bar, text="Search:", font=(FONT, 10), bg=BG, fg=MUTED).pack(side="left")
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self.render())
        e = ttk.Entry(bar, textvariable=self.search, width=30, font=(FONT, 10))
        e.pack(side="left", padx=8, ipady=3)
        FlatButton(bar, "⟳ Refresh", self.refresh, bg=MUTED, hover="#475569").pack(side="right")
        FlatButton(bar, "Promote Selected", self.promote_selected).pack(side="right", padx=8)
        FlatButton(bar, "Remove Selected", self.remove_selected, bg=DANGER, hover=DANGER_DARK).pack(side="right")

        # table
        wrap = tk.Frame(self, bg=CARD, highlightbackground="#e2e8f0", highlightthickness=1)
        wrap.pack(fill="both", expand=True, padx=30, pady=(5, 25))
        self.tree = ttk.Treeview(wrap, columns=[c[0] for c in self.COLS], show="headings", style="Emp.Treeview")
        for key, label, w in self.COLS:
            self.tree.heading(key, text=label, command=lambda k=key: self.sort_by(k))
            self.tree.column(key, width=w, anchor="w" if key not in ("E_id", "gender") else "center")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.tag_configure("odd", background="#f8fafc")
        self.tree.tag_configure("even", background="#ffffff")

    def on_show(self):
        self.refresh()

    def refresh(self):
        try:
            self.records = Emp().show_all_employee()
        except Exception as ex:
            messagebox.showerror("Database error", str(ex))
            self.records = []
        self.render()

    def render(self):
        q = self.search.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        shown = [r for r in self.records if not q or q in " ".join(str(x).lower() for x in r)]
        for i, r in enumerate(shown):
            vals = list(r)
            vals[6] = money(vals[6]) if vals[6] is not None else ""
            self.tree.insert("", "end", values=vals, tags=("odd" if i % 2 else "even",))
        total = sum(float(r[6] or 0) for r in self.records)
        n = len(self.records)
        self.stat_vars["count"].set(str(n))
        self.stat_vars["payroll"].set(money(total))
        self.stat_vars["avg"].set(money(total / n) if n else "-")

    def sort_by(self, key):
        idx = [c[0] for c in self.COLS].index(key)
        rev = self.sort_rev.get(key, False)
        self.records.sort(key=lambda r: (r[idx] is None, str(r[idx]).lower() if isinstance(r[idx], str) else r[idx]), reverse=rev)
        self.sort_rev[key] = not rev
        self.render()

    def selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select an employee", "Please click a row in the table first.")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def promote_selected(self):
        eid = self.selected_id()
        if eid is not None:
            self.app.show("promote", eid)

    def remove_selected(self):
        eid = self.selected_id()
        if eid is not None:
            self.app.show("remove", eid)


# ---------- Add ----------
class AddPage(Page):
    def __init__(self, master, app):
        super().__init__(master, app, "Add Employee", "Create a new employee record")
        card = tk.Frame(self, bg=CARD, highlightbackground="#e2e8f0", highlightthickness=1)
        card.pack(anchor="nw", padx=30, pady=10)
        form = tk.Frame(card, bg=CARD)
        form.pack(padx=35, pady=30)
        self.vars = {}
        fields = [("name", "Full Name"), ("mail", "Email"), ("city", "City"),
                  ("gender", "Gender"), ("position", "Position"), ("salary", "Salary (₹)")]
        for i, (key, label) in enumerate(fields):
            tk.Label(form, text=label, font=(FONT, 10), bg=CARD, fg=MUTED).grid(row=i, column=0, sticky="w", pady=9, padx=(0, 25))
            v = tk.StringVar()
            self.vars[key] = v
            if key == "gender":
                w = ttk.Combobox(form, textvariable=v, values=["M", "F", "O"], state="readonly", width=33, font=(FONT, 11))
            else:
                w = ttk.Entry(form, textvariable=v, width=35, font=(FONT, 11))
            w.grid(row=i, column=1, ipady=4)
            if i == 0:
                self.first = w
        btns = tk.Frame(form, bg=CARD)
        btns.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(25, 0))
        FlatButton(btns, "Clear", self.clear, bg=MUTED, hover="#475569").pack(side="left", padx=8)
        FlatButton(btns, "Add Employee", self.submit, bg=SUCCESS, hover="#059669").pack(side="left")

    def on_show(self):
        self.first.focus_set()

    def clear(self):
        for v in self.vars.values():
            v.set("")
        self.first.focus_set()

    def submit(self):
        d = {k: v.get().strip() for k, v in self.vars.items()}
        if not all(d.values()):
            return messagebox.showwarning("Missing data", "Please fill in all fields.")
        if len(d["name"]) > 20:
            return messagebox.showwarning("Too long", "Name can be at most 20 characters.")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", d["mail"]) or len(d["mail"]) > 50:
            return messagebox.showwarning("Invalid email", "Please enter a valid email (max 50 characters).")
        if len(d["city"]) > 20:
            return messagebox.showwarning("Too long", "City can be at most 20 characters.")
        if len(d["position"]) > 20:
            return messagebox.showwarning("Too long", "Position can be at most 20 characters.")
        try:
            sal = float(d["salary"])
            if sal <= 0 or sal >= 1e8:
                raise ValueError
        except ValueError:
            return messagebox.showwarning("Invalid salary", "Salary must be a positive number.")
        try:
            Emp(d["name"], d["mail"], d["city"], d["gender"], d["position"], sal).make_entry()
        except Exception as ex:
            mydb.rollback()
            return messagebox.showerror("Database error", str(ex))
        self.app.toast(f"✔ {d['name']} added successfully")
        self.clear()


# ---------- Promote ----------
class PromotePage(Page):
    def __init__(self, master, app):
        super().__init__(master, app, "Promote Employee", "Update an employee's position and salary (history is logged)")
        card = tk.Frame(self, bg=CARD, highlightbackground="#e2e8f0", highlightthickness=1)
        card.pack(anchor="nw", padx=30, pady=10)
        f = tk.Frame(card, bg=CARD)
        f.pack(padx=35, pady=30)

        tk.Label(f, text="Employee ID", font=(FONT, 10), bg=CARD, fg=MUTED).grid(row=0, column=0, sticky="w", pady=9, padx=(0, 25))
        self.eid = tk.StringVar()
        ttk.Entry(f, textvariable=self.eid, width=15, font=(FONT, 11)).grid(row=0, column=1, sticky="w", ipady=4)
        FlatButton(f, "Load", self.load, bg=MUTED, hover="#475569").grid(row=0, column=1, sticky="e")

        self.info = tk.Label(f, text="Enter an ID and click Load", font=(FONT, 10), bg="#eef2ff", fg=ACCENT_DARK,
                             justify="left", anchor="w", padx=14, pady=10, width=48)
        self.info.grid(row=1, column=0, columnspan=2, pady=12, sticky="ew")

        self.pos, self.sal = tk.StringVar(), tk.StringVar()
        for i, (label, var) in enumerate([("New Position", self.pos), ("New Salary (₹)", self.sal)], start=2):
            tk.Label(f, text=label, font=(FONT, 10), bg=CARD, fg=MUTED).grid(row=i, column=0, sticky="w", pady=9, padx=(0, 25))
            ttk.Entry(f, textvariable=var, width=35, font=(FONT, 11)).grid(row=i, column=1, ipady=4)
        FlatButton(f, "Promote", self.submit).grid(row=4, column=1, sticky="e", pady=(20, 0))
        self.current = None

    def prefill(self, eid):
        self.eid.set(str(eid))
        self.load()

    def on_show(self):
        pass

    def load(self):
        try:
            eid = int(self.eid.get())
        except ValueError:
            return messagebox.showwarning("Invalid ID", "Employee ID must be a number.")
        row = get_employee(eid)
        if not row:
            self.current = None
            self.info.config(text=f"No employee found with ID {eid}")
            return
        self.current = row
        self.info.config(text=f"{row[1]}  ({row[2]})\nCurrent: {row[5]}  •  {money(row[6])}")
        self.pos.set(row[5])
        self.sal.set(str(row[6]))

    def submit(self):
        if not self.current:
            return messagebox.showwarning("No employee", "Load a valid employee first.")
        pos = self.pos.get().strip()
        if not pos or len(pos) > 20:
            return messagebox.showwarning("Invalid position", "Position is required (max 20 characters).")
        try:
            sal = float(self.sal.get())
            if sal <= 0 or sal >= 1e8:
                raise ValueError
        except ValueError:
            return messagebox.showwarning("Invalid salary", "Salary must be a positive number.")
        eid, name = self.current[0], self.current[1]
        if not messagebox.askyesno("Confirm promotion", f"Promote {name} to '{pos}' with salary {money(sal)}?"):
            return
        try:
            Emp(id=eid).promote_employee(eid, pos, sal)
        except Exception as ex:
            mydb.rollback()
            return messagebox.showerror("Database error", str(ex))
        self.app.toast(f"✔ {name} promoted to {pos}")
        self.load()


# ---------- Remove ----------
class RemovePage(Page):
    def __init__(self, master, app):
        super().__init__(master, app, "Remove Employee", "Permanently delete an employee (their promotion history is removed too)")
        card = tk.Frame(self, bg=CARD, highlightbackground="#e2e8f0", highlightthickness=1)
        card.pack(anchor="nw", padx=30, pady=10)
        f = tk.Frame(card, bg=CARD)
        f.pack(padx=35, pady=30)
        tk.Label(f, text="Employee ID", font=(FONT, 10), bg=CARD, fg=MUTED).grid(row=0, column=0, sticky="w", pady=9, padx=(0, 25))
        self.eid = tk.StringVar()
        ttk.Entry(f, textvariable=self.eid, width=15, font=(FONT, 11)).grid(row=0, column=1, sticky="w", ipady=4)
        FlatButton(f, "Look up", self.load, bg=MUTED, hover="#475569").grid(row=0, column=1, sticky="e")
        self.info = tk.Label(f, text="Enter an ID and click Look up", font=(FONT, 10), bg="#fef2f2", fg=DANGER_DARK,
                             justify="left", anchor="w", padx=14, pady=10, width=48)
        self.info.grid(row=1, column=0, columnspan=2, pady=12, sticky="ew")
        FlatButton(f, "Delete Employee", self.submit, bg=DANGER, hover=DANGER_DARK).grid(row=2, column=1, sticky="e", pady=(10, 0))
        self.current = None

    def prefill(self, eid):
        self.eid.set(str(eid))
        self.load()

    def load(self):
        try:
            eid = int(self.eid.get())
        except ValueError:
            return messagebox.showwarning("Invalid ID", "Employee ID must be a number.")
        row = get_employee(eid)
        self.current = row
        if not row:
            self.info.config(text=f"No employee found with ID {eid}")
        else:
            self.info.config(text=f"{row[1]}  ({row[2]})\n{row[5]}  •  {row[3]}  •  {money(row[6])}")

    def submit(self):
        if not self.current:
            return messagebox.showwarning("No employee", "Look up a valid employee first.")
        eid, name = self.current[0], self.current[1]
        if not messagebox.askyesno("Confirm deletion", f"Permanently delete {name} (ID {eid})?\nThis cannot be undone.", icon="warning"):
            return
        try:
            Emp(id=eid).deletion(eid)
        except Exception as ex:
            mydb.rollback()
            return messagebox.showerror("Database error", str(ex))
        self.app.toast(f"✔ {name} removed")
        self.eid.set("")
        self.current = None
        self.info.config(text="Enter an ID and click Look up")


# ---------- App shell ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Employee Management System")
        self.geometry("1100x680")
        self.minsize(950, 600)
        self.configure(bg=BG)
        self.setup_style()

        side = tk.Frame(self, bg=SIDEBAR, width=230)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="👥  EMS", font=(FONT, 20, "bold"), bg=SIDEBAR, fg="white").pack(pady=(30, 2))
        tk.Label(side, text="Employee Management", font=(FONT, 9), bg=SIDEBAR, fg="#94a3b8").pack(pady=(0, 30))

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {
            "employees": EmployeesPage(self.content, self),
            "add": AddPage(self.content, self),
            "promote": PromotePage(self.content, self),
            "remove": RemovePage(self.content, self),
        }
        self.nav = {}
        for key, label in [("employees", "📋   Employees"), ("add", "➕   Add Employee"),
                           ("promote", "⬆   Promote Employee"), ("remove", "🗑   Remove Employee")]:
            b = tk.Label(side, text=label, font=(FONT, 11), bg=SIDEBAR, fg="#cbd5e1", anchor="w",
                         padx=25, pady=12, cursor="hand2")
            b.pack(fill="x")
            b.bind("<Button-1>", lambda e, k=key: self.show(k))
            b.bind("<Enter>", lambda e, k=key: self.nav[k].config(bg=SIDEBAR_HOVER) if k != self.current else None)
            b.bind("<Leave>", lambda e, k=key: self.nav[k].config(bg=SIDEBAR) if k != self.current else None)
            self.nav[key] = b
        tk.Label(side, text="Connected to MySQL", font=(FONT, 8), bg=SIDEBAR, fg="#64748b").pack(side="bottom", pady=15)

        self.toast_lbl = tk.Label(self, text="", font=(FONT, 10, "bold"), bg=SUCCESS, fg="white", padx=18, pady=10)
        self.current = None
        self.show("employees")

    def setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Emp.Treeview", background="white", fieldbackground="white", foreground=TEXT,
                    rowheight=32, font=(FONT, 10), borderwidth=0)
        s.configure("Emp.Treeview.Heading", background="#e2e8f0", foreground=TEXT,
                    font=(FONT, 10, "bold"), relief="flat", padding=8)
        s.map("Emp.Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])
        s.map("Emp.Treeview.Heading", background=[("active", "#cbd5e1")])
        s.configure("TEntry", padding=4)

    def show(self, key, eid=None):
        for p in self.pages.values():
            p.pack_forget()
        if self.current:
            self.nav[self.current].config(bg=SIDEBAR, fg="#cbd5e1")
        self.current = key
        self.nav[key].config(bg=ACCENT, fg="white")
        page = self.pages[key]
        page.pack(fill="both", expand=True)
        page.on_show()
        if eid is not None and hasattr(page, "prefill"):
            page.prefill(eid)

    def toast(self, msg):
        self.toast_lbl.config(text=msg)
        self.toast_lbl.place(relx=1.0, rely=1.0, x=-25, y=-25, anchor="se")
        self.after(2500, self.toast_lbl.place_forget)


if __name__ == "__main__":
    create_Employee_table()
    create_promotion_table()
    App().mainloop()
