import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from datetime import date


class FeedPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    # ─────────────────────────────────────────────────
    def _get_groups(self):
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, name FROM animal_groups ORDER BY name"
        ).fetchall()
        conn.close()
        return rows

    # ─────────────────────────────────────────────────
    def build(self):
        for w in self.parent.winfo_children():
            w.destroy()

        # Topbar
        tb = tk.Frame(self.parent, bg="white", height=52)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        tk.Label(tb, text="🌾  Feed & Expense",
                 font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── FORM ─────────────────────────────────────
        form = tk.LabelFrame(body, text="➕  Add Feed Record",
                             font=("Arial", 10, "bold"),
                             bg="#f0ede4", padx=12, pady=10)
        form.pack(fill="x", pady=(0, 14))

        groups      = self._get_groups()
        group_names = [f"{g[0]}: {g[1]}" for g in groups]

        # Row 1 ── Group + Feed Type
        r1 = tk.Frame(form, bg="#f0ede4")
        r1.pack(fill="x", pady=(0, 6))

        tk.Label(r1, text="Animal Group",
                 font=("Arial", 9), bg="#f0ede4",
                 fg="#555").grid(row=0, column=0, sticky="w", padx=(0,4))
        self.group_var = tk.StringVar()
        ttk.Combobox(r1, textvariable=self.group_var,
                     values=group_names, width=22,
                     state="readonly").grid(row=1, column=0,
                                            sticky="w", padx=(0,12), ipady=3)

        tk.Label(r1, text="Feed Type",
                 font=("Arial", 9), bg="#f0ede4",
                 fg="#555").grid(row=0, column=1, sticky="w", padx=(0,4))
        self.feed_type = tk.Entry(r1, width=18,
                                  font=("Arial", 11), bd=1, relief="solid")
        self.feed_type.grid(row=1, column=1, sticky="w",
                            padx=(0,12), ipady=5)

        # Row 2 ── Qty + Cost + Date
        r2 = tk.Frame(form, bg="#f0ede4")
        r2.pack(fill="x", pady=(0, 8))

        for col_i, (lbl, attr, w) in enumerate([
            ("Qty (kg)", "qty",        10),
            ("Cost (৳)", "cost",       10),
            ("Date",     "date_entry", 13),
        ]):
            tk.Label(r2, text=lbl, font=("Arial", 9),
                     bg="#f0ede4", fg="#555"
                     ).grid(row=0, column=col_i, sticky="w", padx=(0,4))
            e = tk.Entry(r2, width=w, font=("Arial", 11),
                         bd=1, relief="solid")
            e.grid(row=1, column=col_i, sticky="w",
                   padx=(0,12), ipady=5)
            setattr(self, attr, e)

        self.date_entry.insert(0, date.today().isoformat())

        tk.Button(form, text="✅  Save",
                  command=self.save,
                  bg="#2d6a4f", fg="white",
                  font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0,
                  cursor="hand2").pack(anchor="w", pady=(4, 0))

        # ── TABLE ────────────────────────────────────
        tbl = tk.LabelFrame(body, text="📋  Feed Records",
                            font=("Arial", 10, "bold"),
                            bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)

        cols   = ("ID", "Group", "Feed Type", "Qty (kg)", "Cost (৳)", "Date")
        widths = {"ID": 40, "Group": 140, "Feed Type": 140,
                  "Qty (kg)": 80, "Cost (৳)": 90, "Date": 100}
        self.tree = ttk.Treeview(tbl, columns=cols,
                                 show="headings", height=12)
        for col in cols:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=widths[col],
                             anchor="w", stretch=True)

        vsb = ttk.Scrollbar(tbl, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.load_data()

    # ─────────────────────────────────────────────────
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute("""
            SELECT f.id,
                   COALESCE(ag.name,'—') AS grp,
                   f.feed_type, f.quantity, f.cost, f.date
            FROM feed_expenses f
            LEFT JOIN animal_groups ag ON f.group_id = ag.id
            ORDER BY f.date DESC, f.id DESC
        """).fetchall()
        conn.close()
        for r in rows:
            self.tree.insert("", "end", values=tuple(r))

    # ─────────────────────────────────────────────────
    def save(self):
        group_str = self.group_var.get().strip()
        feed      = self.feed_type.get().strip()
        qty_str   = self.qty.get().strip()
        cost_str  = self.cost.get().strip()
        dt        = self.date_entry.get().strip()

        if not group_str:
            messagebox.showwarning("Missing", "Please select an Animal Group.")
            return
        if not feed:
            messagebox.showwarning("Missing", "Feed Type is required.")
            return
        if not qty_str or not cost_str or not dt:
            messagebox.showwarning("Missing",
                "Quantity, Cost and Date are required.")
            return

        try:
            qty  = float(qty_str)
            cost = float(cost_str)
        except ValueError:
            messagebox.showerror("Error",
                "Quantity and Cost must be numbers.")
            return

        group_id = int(group_str.split(":")[0])

        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO feed_expenses "
                "(group_id,feed_type,quantity,cost,date) "
                "VALUES (?,?,?,?,?)",
                (group_id, feed, qty, cost, dt)
            )
            conn.commit()
            conn.close()
        except Exception as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        self.feed_type.delete(0, tk.END)
        self.qty.delete(0, tk.END)
        self.cost.delete(0, tk.END)
        self.load_data()
        messagebox.showinfo("Saved", "Feed record saved! ✅")