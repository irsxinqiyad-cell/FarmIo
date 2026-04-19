import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from datetime import date


class MortalityPage:
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
        tk.Label(tb, text="💀  Mortality",
                 font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── FORM ─────────────────────────────────────
        form = tk.LabelFrame(body, text="➕  Record Deaths",
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

        # Deaths
        g2 = tk.Frame(r, bg="#f0ede4"); g2.pack(side="left", padx=8)
        tk.Label(g2, text="Death Count", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.deaths = tk.Entry(g2, width=10, font=("Arial", 11),
                               bd=1, relief="solid")
        self.deaths.pack(ipady=5)

        # Date
        g3 = tk.Frame(r, bg="#f0ede4"); g3.pack(side="left", padx=8)
        tk.Label(g3, text="Date", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.mort_date = tk.Entry(g3, width=13, font=("Arial", 11),
                                  bd=1, relief="solid")
        self.mort_date.insert(0, date.today().isoformat())
        self.mort_date.pack(ipady=5)

        # Reason
        g4 = tk.Frame(r, bg="#f0ede4"); g4.pack(side="left", padx=8)
        tk.Label(g4, text="Reason (optional)", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w")
        self.reason = tk.Entry(g4, width=22, font=("Arial", 11),
                               bd=1, relief="solid")
        self.reason.pack(ipady=5)

        tk.Button(form, text="✅  Save",
                  command=self.save,
                  bg="#2d6a4f", fg="white",
                  font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0,
                  cursor="hand2").pack(anchor="w", pady=(10, 0))

        # ── TABLE ────────────────────────────────────
        tbl = tk.LabelFrame(body, text="📋  Mortality Log",
                            font=("Arial", 10, "bold"),
                            bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)

        cols   = ("ID", "Group", "Deaths", "Date", "Reason")
        widths = {"ID": 40, "Group": 160, "Deaths": 80,
                  "Date": 110, "Reason": 200}
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
            SELECT m.id,
                   COALESCE(ag.name,'—'),
                   m.death_count, m.date, m.reason
            FROM mortality m
            LEFT JOIN animal_groups ag ON m.group_id = ag.id
            ORDER BY m.date DESC, m.id DESC
        """).fetchall()
        conn.close()
        for r in rows:
            self.tree.insert("", "end", values=tuple(r))

    # ─────────────────────────────────────────────────
    def save(self):
        group_str   = self.group_var.get().strip()
        deaths_str  = self.deaths.get().strip()
        dt          = self.mort_date.get().strip()
        reason      = self.reason.get().strip()

        if not group_str:
            messagebox.showwarning("Missing", "Please select an Animal Group.")
            return
        if not deaths_str or not dt:
            messagebox.showwarning("Missing",
                "Death Count and Date are required.")
            return
        try:
            deaths = int(deaths_str)
        except ValueError:
            messagebox.showerror("Error", "Death Count must be a whole number.")
            return

        group_id = int(group_str.split(":")[0])
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO mortality "
                "(group_id,death_count,date,reason) "
                "VALUES (?,?,?,?)",
                (group_id, deaths, dt, reason)
            )
            conn.commit()
            conn.close()
        except Exception as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        self.deaths.delete(0, tk.END)
        self.reason.delete(0, tk.END)
        self.load_data()
        messagebox.showinfo("Saved", "Mortality record saved! ✅")