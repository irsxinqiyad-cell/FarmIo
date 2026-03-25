import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from datetime import date

class FeedPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    def get_groups(self):
        conn = get_connection()
        rows = conn.execute("SELECT id, name FROM animal_groups").fetchall()
        conn.close()
        return rows

    def build(self):
        for w in self.parent.winfo_children(): w.destroy()

        tb = tk.Frame(self.parent, bg="white")
        tb.pack(fill="x")
        tk.Label(tb, text="🌾 Feed & Expense", font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        form = tk.LabelFrame(body, text="➕ Add Feed Record", font=("Arial", 10, "bold"),
                              bg="#f0ede4", padx=12, pady=10)
        form.pack(fill="x", pady=(0, 14))

        groups = self.get_groups()
        group_names = [f"{g[0]}: {g[1]}" for g in groups]

        row1 = tk.Frame(form, bg="#f0ede4"); row1.pack(fill="x")
        tk.Label(row1, text="Animal Group", font=("Arial", 9), bg="#f0ede4").pack(side="left", padx=4)
        self.group_var = tk.StringVar()
        ttk.Combobox(row1, textvariable=self.group_var, values=group_names, width=20).pack(side="left", padx=4)

        tk.Label(row1, text="Feed Type", font=("Arial", 9), bg="#f0ede4").pack(side="left", padx=4)
        self.feed_type = tk.Entry(row1, width=14, font=("Arial", 11), bd=1, relief="solid")
        self.feed_type.pack(side="left", padx=4, ipady=5)

        row2 = tk.Frame(form, bg="#f0ede4"); row2.pack(fill="x", pady=8)
        tk.Label(row2, text="Qty (kg)", font=("Arial", 9), bg="#f0ede4").pack(side="left", padx=4)
        self.qty = tk.Entry(row2, width=10, font=("Arial", 11), bd=1, relief="solid")
        self.qty.pack(side="left", padx=4, ipady=5)

        tk.Label(row2, text="Cost (৳)", font=("Arial", 9), bg="#f0ede4").pack(side="left", padx=4)
        self.cost = tk.Entry(row2, width=10, font=("Arial", 11), bd=1, relief="solid")
        self.cost.pack(side="left", padx=4, ipady=5)

        tk.Label(row2, text="Date", font=("Arial", 9), bg="#f0ede4").pack(side="left", padx=4)
        self.date_entry = tk.Entry(row2, width=12, font=("Arial", 11), bd=1, relief="solid")
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.pack(side="left", padx=4, ipady=5)

        tk.Button(form, text="✅ Save", command=self.save,
                  bg="#2d6a4f", fg="white", font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0, cursor="hand2").pack(pady=(6,0))

        # Table
        tbl = tk.LabelFrame(body, text="📋 Feed Records", font=("Arial", 10, "bold"),
                              bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)
        cols = ("ID", "Group", "Feed Type", "Qty", "Cost", "Date")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90 if col != "ID" else 40)
        self.tree.pack(fill="both", expand=True)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute("""
            SELECT f.id, ag.name, f.feed_type, f.quantity, f.cost, f.date
            FROM feed_expenses f LEFT JOIN animal_groups ag ON f.group_id = ag.id
        """).fetchall()
        conn.close()
        for r in rows: self.tree.insert("", "end", values=tuple(r))

    def save(self):
        group_str = self.group_var.get()
        group_id = int(group_str.split(":")[0]) if group_str else None
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO feed_expenses (group_id, feed_type, quantity, cost, date) VALUES (?,?,?,?,?)",
                (group_id, self.feed_type.get(), float(self.qty.get()),
                 float(self.cost.get()), self.date_entry.get())
            )
            conn.commit(); conn.close()
            self.load_data()
            messagebox.showinfo("Saved", "Feed record saved!")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))