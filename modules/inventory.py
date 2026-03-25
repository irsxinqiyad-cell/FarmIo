import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

class InventoryPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    def build(self):
        for w in self.parent.winfo_children(): w.destroy()

        tb = tk.Frame(self.parent, bg="white")
        tb.pack(fill="x")
        tk.Label(tb, text="📦 Inventory", font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        form = tk.LabelFrame(body, text="➕ Add / Update Item",
                              font=("Arial", 10, "bold"), bg="#f0ede4", padx=12, pady=10)
        form.pack(fill="x", pady=(0,14))

        row = tk.Frame(form, bg="#f0ede4"); row.pack(fill="x")
        labels = [("Item Name", "item_name", 20), ("Quantity", "qty", 10),
                  ("Unit", "unit", 10), ("Min Threshold", "min_thresh", 10)]
        self.entries = {}
        for lbl, key, w in labels:
            col = tk.Frame(row, bg="#f0ede4"); col.pack(side="left", padx=6)
            tk.Label(col, text=lbl, font=("Arial", 9), bg="#f0ede4").pack(anchor="w")
            if key == "unit":
                var = tk.StringVar(value="kg")
                ttk.Combobox(col, textvariable=var, values=["kg","litre","piece","bag"], width=w).pack(ipady=3)
                self.entries[key] = var
            else:
                e = tk.Entry(col, width=w, font=("Arial", 11), bd=1, relief="solid")
                e.pack(ipady=5)
                self.entries[key] = e

        tk.Button(form, text="✅ Save", command=self.save,
                  bg="#2d6a4f", fg="white", font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0, cursor="hand2").pack(pady=(8,0))

        tbl = tk.LabelFrame(body, text="📋 Stock List",
                             font=("Arial", 10, "bold"), bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)
        cols = ("ID", "Item", "Qty", "Unit", "Min", "Status")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)
        self.tree.tag_configure("low", background="#fdecea", foreground="#c0392b")
        self.tree.pack(fill="both", expand=True)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute("SELECT * FROM inventory").fetchall()
        conn.close()
        for r in rows:
            status = "⚠️ Low" if r[2] < r[4] else "✅ OK"
            tag = "low" if r[2] < r[4] else ""
            self.tree.insert("", "end", values=(*r, status), tags=(tag,))

    def save(self):
        try:
            name = self.entries["item_name"].get()
            qty = float(self.entries["qty"].get())
            unit = self.entries["unit"].get()
            mn = float(self.entries["min_thresh"].get())
            conn = get_connection()
            conn.execute(
                "INSERT INTO inventory (item_name, quantity, unit, min_threshold) VALUES (?,?,?,?)",
                (name, qty, unit, mn)
            )
            conn.commit(); conn.close()
            self.load_data()
            messagebox.showinfo("Saved", "Inventory item saved!")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))