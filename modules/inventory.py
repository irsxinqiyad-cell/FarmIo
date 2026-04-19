import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection


class InventoryPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    # ─────────────────────────────────────────────────
    def build(self):
        for w in self.parent.winfo_children():
            w.destroy()

        tb = tk.Frame(self.parent, bg="white", height=52)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        tk.Label(tb, text="📦  Inventory",
                 font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── FORM ─────────────────────────────────────
        form = tk.LabelFrame(body, text="➕  Add / Update Item",
                             font=("Arial", 10, "bold"),
                             bg="#f0ede4", padx=12, pady=10)
        form.pack(fill="x", pady=(0, 14))

        r = tk.Frame(form, bg="#f0ede4")
        r.pack(fill="x")

        # Item Name
        g = tk.Frame(r, bg="#f0ede4"); g.pack(side="left", padx=8)
        tk.Label(g, text="Item Name", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.item_name = tk.Entry(g, width=22, font=("Arial", 11),
                                  bd=1, relief="solid")
        self.item_name.pack(ipady=5)

        # Quantity
        g2 = tk.Frame(r, bg="#f0ede4"); g2.pack(side="left", padx=8)
        tk.Label(g2, text="Quantity", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.qty = tk.Entry(g2, width=12, font=("Arial", 11),
                            bd=1, relief="solid")
        self.qty.pack(ipady=5)

        # Unit
        g3 = tk.Frame(r, bg="#f0ede4"); g3.pack(side="left", padx=8)
        tk.Label(g3, text="Unit", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.unit_var = tk.StringVar(value="kg")
        ttk.Combobox(g3, textvariable=self.unit_var,
                     values=["kg", "litre", "piece", "bag"],
                     width=10, state="readonly").pack(ipady=3)

        # Min Threshold
        g4 = tk.Frame(r, bg="#f0ede4"); g4.pack(side="left", padx=8)
        tk.Label(g4, text="Min Threshold", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.min_thresh = tk.Entry(g4, width=12, font=("Arial", 11),
                                   bd=1, relief="solid")
        self.min_thresh.pack(ipady=5)

        tk.Button(form, text="✅  Save",
                  command=self.save,
                  bg="#2d6a4f", fg="white",
                  font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0,
                  cursor="hand2").pack(anchor="w", pady=(10, 0))

        # ── TABLE ────────────────────────────────────
        tbl = tk.LabelFrame(body, text="📋  Stock List",
                            font=("Arial", 10, "bold"),
                            bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)

        cols   = ("ID", "Item", "Qty", "Unit", "Min", "Status")
        widths = {"ID": 40, "Item": 200, "Qty": 90,
                  "Unit": 80, "Min": 80, "Status": 100}
        self.tree = ttk.Treeview(tbl, columns=cols,
                                 show="headings", height=12)
        for col in cols:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=widths[col],
                             anchor="w", stretch=True)

        self.tree.tag_configure("low",
                                background="#fdecea",
                                foreground="#c0392b")

        vsb = ttk.Scrollbar(tbl, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        tk.Button(tbl, text="🗑️  Delete Selected",
                  command=self.delete,
                  bg="#c0392b", fg="white",
                  font=("Arial", 10),
                  padx=12, pady=4, bd=0,
                  cursor="hand2").pack(anchor="w", pady=8)

        self.load_data()

    # ─────────────────────────────────────────────────
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute(
            "SELECT id,item_name,quantity,unit,min_threshold "
            "FROM inventory ORDER BY item_name"
        ).fetchall()
        conn.close()
        for r in rows:
            low    = r[2] < r[4]
            status = "⚠️ Low" if low else "✅ OK"
            tag    = "low"     if low else ""
            self.tree.insert("", "end",
                             values=(*r, status), tags=(tag,))

    # ─────────────────────────────────────────────────
    def save(self):
        name     = self.item_name.get().strip()
        qty_str  = self.qty.get().strip()
        unit     = self.unit_var.get()
        mn_str   = self.min_thresh.get().strip()

        if not name:
            messagebox.showwarning("Missing", "Item Name is required.")
            return
        if not qty_str or not mn_str:
            messagebox.showwarning("Missing",
                "Quantity and Min Threshold are required.")
            return
        try:
            qty = float(qty_str)
            mn  = float(mn_str)
        except ValueError:
            messagebox.showerror("Error",
                "Quantity and Min Threshold must be numbers.")
            return

        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO inventory "
                "(item_name,quantity,unit,min_threshold) "
                "VALUES (?,?,?,?)",
                (name, qty, unit, mn)
            )
            conn.commit()
            conn.close()
        except Exception as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        self.item_name.delete(0, tk.END)
        self.qty.delete(0, tk.END)
        self.min_thresh.delete(0, tk.END)
        self.load_data()
        messagebox.showinfo("Saved", "Inventory item saved! ✅")

    # ─────────────────────────────────────────────────
    def delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select",
                "Please select a row to delete.")
            return
        row_id = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete",
                "Delete this inventory item?"):
            conn = get_connection()
            conn.execute(
                "DELETE FROM inventory WHERE id=?", (row_id,))
            conn.commit()
            conn.close()
            self.load_data()