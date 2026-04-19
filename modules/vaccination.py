import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from datetime import date


class VaccinationPage:
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
        tk.Label(tb, text="💉  Vaccination",
                 font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── FORM ─────────────────────────────────────
        form = tk.LabelFrame(body, text="➕  Add Vaccination Record",
                             font=("Arial", 10, "bold"),
                             bg="#f0ede4", padx=12, pady=10)
        form.pack(fill="x", pady=(0, 14))

        conn        = get_connection()
        groups      = conn.execute(
            "SELECT id,name FROM animal_groups ORDER BY name"
        ).fetchall()
        conn.close()
        group_names = [f"{g[0]}: {g[1]}" for g in groups]

        r = tk.Frame(form, bg="#f0ede4")
        r.pack(fill="x")

        # Group
        g = tk.Frame(r, bg="#f0ede4"); g.pack(side="left", padx=8)
        tk.Label(g, text="Animal Group", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.group_var = tk.StringVar()
        ttk.Combobox(g, textvariable=self.group_var,
                     values=group_names, width=22,
                     state="readonly").pack(ipady=3)

        # Vaccine name
        g2 = tk.Frame(r, bg="#f0ede4"); g2.pack(side="left", padx=8)
        tk.Label(g2, text="Vaccine Name", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.vaccine = tk.Entry(g2, width=18, font=("Arial", 11),
                                bd=1, relief="solid")
        self.vaccine.pack(ipady=5)

        # Given date
        g3 = tk.Frame(r, bg="#f0ede4"); g3.pack(side="left", padx=8)
        tk.Label(g3, text="Given Date", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.given_date = tk.Entry(g3, width=13, font=("Arial", 11),
                                   bd=1, relief="solid")
        self.given_date.insert(0, date.today().isoformat())
        self.given_date.pack(ipady=5)

        # Next due
        g4 = tk.Frame(r, bg="#f0ede4"); g4.pack(side="left", padx=8)
        tk.Label(g4, text="Next Due", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.next_due = tk.Entry(g4, width=13, font=("Arial", 11),
                                 bd=1, relief="solid")
        self.next_due.insert(0, date.today().isoformat())
        self.next_due.pack(ipady=5)

        tk.Button(form, text="✅  Save",
                  command=self.save,
                  bg="#2d6a4f", fg="white",
                  font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0,
                  cursor="hand2").pack(anchor="w", pady=(10, 0))

        # ── TABLE ────────────────────────────────────
        tbl = tk.LabelFrame(body, text="📋  Vaccination Records",
                            font=("Arial", 10, "bold"),
                            bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)

        cols   = ("ID", "Group", "Vaccine", "Given Date", "Next Due", "Status")
        widths = {"ID": 40, "Group": 140, "Vaccine": 150,
                  "Given Date": 100, "Next Due": 100, "Status": 100}
        self.tree = ttk.Treeview(tbl, columns=cols,
                                 show="headings", height=12)
        for col in cols:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=widths[col],
                             anchor="w", stretch=True)

        self.tree.tag_configure("overdue",
                                background="#fdecea",
                                foreground="#c0392b")

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
            SELECT v.id,
                   COALESCE(ag.name,'—'),
                   v.vaccine_name, v.given_date, v.next_due
            FROM vaccinations v
            LEFT JOIN animal_groups ag ON v.group_id = ag.id
            ORDER BY v.next_due ASC
        """).fetchall()
        conn.close()
        today = date.today().isoformat()
        for r in rows:
            overdue = r[4] < today
            status  = "⚠️ Overdue" if overdue else "✅ OK"
            tag     = "overdue"    if overdue else ""
            self.tree.insert("", "end",
                             values=(*r, status), tags=(tag,))

    # ─────────────────────────────────────────────────
    def save(self):
        group_str = self.group_var.get().strip()
        vaccine   = self.vaccine.get().strip()
        gd        = self.given_date.get().strip()
        nd        = self.next_due.get().strip()

        if not group_str:
            messagebox.showwarning("Missing", "Please select an Animal Group.")
            return
        if not vaccine or not gd or not nd:
            messagebox.showwarning("Missing",
                "Vaccine name, Given Date and Next Due are required.")
            return

        group_id = int(group_str.split(":")[0])
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO vaccinations "
                "(group_id,vaccine_name,given_date,next_due) "
                "VALUES (?,?,?,?)",
                (group_id, vaccine, gd, nd)
            )
            conn.commit()
            conn.close()
        except Exception as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        self.vaccine.delete(0, tk.END)
        self.load_data()
        messagebox.showinfo("Saved", "Vaccination record saved! ✅")