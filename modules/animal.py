import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

# ── helper: uniform label+entry column ───────────────
def _field(parent, label, width=15):
    f = tk.Frame(parent, bg="#f0ede4")
    f.pack(side="left", padx=8, pady=4)
    tk.Label(f, text=label, font=("Arial", 9),
             bg="#f0ede4", fg="#555").pack(anchor="w")
    e = tk.Entry(f, width=width, font=("Arial", 11), bd=1, relief="solid")
    e.pack(ipady=5)
    return e


class AnimalPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    # ─────────────────────────────────────────────────
    def build(self):
        for w in self.parent.winfo_children():
            w.destroy()

        # Topbar
        tb = tk.Frame(self.parent, bg="white", height=52)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        tk.Label(tb, text="🐄  Animal Group",
                 font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── FORM ─────────────────────────────────────
        form = tk.LabelFrame(body, text="➕  Add Animal Group",
                             font=("Arial", 10, "bold"),
                             bg="#f0ede4", padx=12, pady=10)
        form.pack(fill="x", pady=(0, 14))

        row = tk.Frame(form, bg="#f0ede4")
        row.pack(fill="x")

        self.e_name    = _field(row, "Group Name",    16)
        self.e_type    = _field(row, "Animal Type",   14)
        self.e_qty     = _field(row, "Quantity",      10)
        self.e_age     = _field(row, "Age (months)",  10)
        self.e_purpose = _field(row, "Purpose",       16)

        tk.Button(form, text="✅  Save",
                  command=self.save,
                  bg="#2d6a4f", fg="white",
                  font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0,
                  cursor="hand2").pack(anchor="w", pady=(8, 0))

        # ── TABLE ────────────────────────────────────
        tbl = tk.LabelFrame(body, text="📋  Animal Groups",
                            font=("Arial", 10, "bold"),
                            bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)

        cols = ("ID", "Name", "Type", "Qty", "Age", "Purpose")
        self.tree = ttk.Treeview(tbl, columns=cols,
                                 show="headings", height=12)
        widths = {"ID": 40, "Name": 160, "Type": 120,
                  "Qty": 70, "Age": 80, "Purpose": 150}
        for col in cols:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=widths[col],
                             anchor="w", stretch=True)

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
            "SELECT id,name,animal_type,quantity,age_months,purpose "
            "FROM animal_groups ORDER BY id DESC"
        ).fetchall()
        conn.close()
        for r in rows:
            self.tree.insert("", "end", values=tuple(r))

    # ─────────────────────────────────────────────────
    def save(self):
        name    = self.e_name.get().strip()
        a_type  = self.e_type.get().strip()
        qty_str = self.e_qty.get().strip()
        age_str = self.e_age.get().strip()
        purpose = self.e_purpose.get().strip()

        if not name or not a_type or not qty_str:
            messagebox.showwarning("Missing",
                "Name, Type and Quantity are required.")
            return
        try:
            qty = int(qty_str)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number.")
            return
        age = None
        if age_str:
            try:
                age = int(age_str)
            except ValueError:
                messagebox.showerror("Error",
                    "Age must be a number (months).")
                return

        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO animal_groups "
                "(name,animal_type,quantity,age_months,purpose) "
                "VALUES (?,?,?,?,?)",
                (name, a_type, qty, age, purpose)
            )
            conn.commit()
            conn.close()
        except Exception as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        # clear fields
        for e in (self.e_name, self.e_type, self.e_qty,
                  self.e_age, self.e_purpose):
            e.delete(0, tk.END)

        self.load_data()
        messagebox.showinfo("Saved", "Animal group saved! ✅")

    # ─────────────────────────────────────────────────
    def delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select",
                "Please select a row to delete.")
            return
        row_id = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete",
                "Delete this animal group?\n"
                "(Related records will also be affected.)"):
            conn = get_connection()
            conn.execute(
                "DELETE FROM animal_groups WHERE id=?", (row_id,))
            conn.commit()
            conn.close()
            self.load_data()