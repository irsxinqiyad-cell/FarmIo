import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from datetime import date

class VaccinationPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    def build(self):
        for w in self.parent.winfo_children(): w.destroy()

        tb = tk.Frame(self.parent, bg="white")
        tb.pack(fill="x")
        tk.Label(tb, text="💉 Vaccination", font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        form = tk.LabelFrame(body, text="➕ Add Vaccination Record",
                              font=("Arial", 10, "bold"), bg="#f0ede4", padx=12, pady=10)
        form.pack(fill="x", pady=(0,14))

        groups = get_connection().execute("SELECT id, name FROM animal_groups").fetchall()
        get_connection().close()
        group_names = [f"{g[0]}: {g[1]}" for g in groups]

        row = tk.Frame(form, bg="#f0ede4"); row.pack(fill="x")
        for lbl, attr, w in [("Group", "group_var", 20), ("Vaccine", "vaccine", 16),
                              ("Given Date", "given_date", 12), ("Next Due", "next_due", 12)]:
            col = tk.Frame(row, bg="#f0ede4"); col.pack(side="left", padx=6)
            tk.Label(col, text=lbl, font=("Arial", 9), bg="#f0ede4").pack(anchor="w")
            if attr == "group_var":
                self.group_var = tk.StringVar()
                ttk.Combobox(col, textvariable=self.group_var, values=group_names, width=w).pack(ipady=3)
            else:
                e = tk.Entry(col, width=w, font=("Arial", 11), bd=1, relief="solid")
                e.pack(ipady=5)
                if "date" in attr: e.insert(0, date.today().isoformat())
                setattr(self, attr, e)

        tk.Button(form, text="✅ Save", command=self.save,
                  bg="#2d6a4f", fg="white", font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0, cursor="hand2").pack(pady=(8,0))

        tbl = tk.LabelFrame(body, text="📋 Vaccination Records",
                             font=("Arial", 10, "bold"), bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)
        cols = ("ID", "Group", "Vaccine", "Given Date", "Next Due", "Status")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)
        self.tree.tag_configure("overdue", background="#fdecea", foreground="#c0392b")
        self.tree.pack(fill="both", expand=True)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute("""
            SELECT v.id, ag.name, v.vaccine_name, v.given_date, v.next_due
            FROM vaccinations v LEFT JOIN animal_groups ag ON v.group_id = ag.id
        """).fetchall()
        conn.close()
        today = date.today().isoformat()
        for r in rows:
            status = "⚠️ Overdue" if r[4] < today else "✅ OK"
            tag = "overdue" if r[4] < today else ""
            self.tree.insert("", "end", values=(*r, status), tags=(tag,))

    def save(self):
        group_str = self.group_var.get()
        group_id = int(group_str.split(":")[0]) if group_str else None
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO vaccinations (group_id, vaccine_name, given_date, next_due) VALUES (?,?,?,?)",
                (group_id, self.vaccine.get(), self.given_date.get(), self.next_due.get())
            )
            conn.commit(); conn.close()
            self.load_data()
            messagebox.showinfo("Saved", "Vaccination record saved!")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))