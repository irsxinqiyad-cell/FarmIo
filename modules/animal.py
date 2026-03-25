import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

class AnimalPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    def build(self):
        for w in self.parent.winfo_children(): w.destroy()

        # Topbar
        tb = tk.Frame(self.parent, bg="white", height=50)
        tb.pack(fill="x")
        tk.Label(tb, text="🐄 Animal Group", font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── FORM ──
        form = tk.LabelFrame(body, text="➕ Add Animal Group", font=("Arial", 10, "bold"),
                              bg="#f0ede4", padx=12, pady=10)
        form.pack(fill="x", pady=(0, 14))

        fields = [("Group Name", "name"), ("Animal Type", "type"),
                  ("Quantity", "qty"), ("Age (months)", "age"), ("Purpose", "purpose")]
        self.entries = {}
        row_frame = tk.Frame(form, bg="#f0ede4")
        row_frame.pack(fill="x")
        for i, (label, key) in enumerate(fields):
            col = tk.Frame(row_frame, bg="#f0ede4")
            col.pack(side="left", padx=8)
            tk.Label(col, text=label, font=("Arial", 9), bg="#f0ede4", fg="#555").pack(anchor="w")
            e = tk.Entry(col, width=14, font=("Arial", 11), bd=1, relief="solid")
            e.pack(ipady=5)
            self.entries[key] = e

        tk.Button(form, text="✅ Save", command=self.save,
                  bg="#2d6a4f", fg="white", font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0, cursor="hand2").pack(pady=(10, 0))

        # ── TABLE ──
        tbl_frame = tk.LabelFrame(body, text="📋 Animal Groups", font=("Arial", 10, "bold"),
                                   bg="#f0ede4", padx=8, pady=8)
        tbl_frame.pack(fill="both", expand=True)

        cols = ("ID", "Name", "Type", "Qty", "Age", "Purpose")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "ID" else 40)
        self.tree.pack(fill="both", expand=True)

        tk.Button(tbl_frame, text="🗑️ Delete Selected", command=self.delete,
                  bg="#c0392b", fg="white", font=("Arial", 10),
                  padx=12, pady=4, bd=0, cursor="hand2").pack(pady=8)

        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute("SELECT * FROM animal_groups").fetchall()
        conn.close()
        for r in rows:
            self.tree.insert("", "end", values=tuple(r))

    def save(self):
        data = {k: v.get().strip() for k, v in self.entries.items()}
        if not data["name"] or not data["type"] or not data["qty"]:
            messagebox.showwarning("Missing", "Name, Type and Quantity are required.")
            return
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO animal_groups (name, animal_type, quantity, age_months, purpose) VALUES (?,?,?,?,?)",
                (data["name"], data["type"], int(data["qty"]),
                 int(data["age"]) if data["age"] else None, data["purpose"])
            )
            conn.commit(); conn.close()
            for e in self.entries.values(): e.delete(0, tk.END)
            self.load_data()
            messagebox.showinfo("Saved", "Animal group saved!")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a row to delete.")
            return
        row_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Delete", "Delete this animal group?"):
            conn = get_connection()
            conn.execute("DELETE FROM animal_groups WHERE id=?", (row_id,))
            conn.commit(); conn.close()
            self.load_data()