import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from datetime import date

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class FinancialPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    def build(self):
        for w in self.parent.winfo_children():
            w.destroy()

        tb = tk.Frame(self.parent, bg="white", height=52)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        tk.Label(tb, text="💰  Financial Report",
                 font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── STAT CARDS ───────────────────────────────
        ms   = date.today().replace(day=1).isoformat()
        conn = get_connection()
        income  = conn.execute(
            "SELECT SUM(amount) FROM financials "
            "WHERE type='Income' AND date>=?", (ms,)
        ).fetchone()[0] or 0
        expense = conn.execute(
            "SELECT SUM(amount) FROM financials "
            "WHERE type='Expense' AND date>=?", (ms,)
        ).fetchone()[0] or 0
        conn.close()
        net = income - expense

        cards = tk.Frame(body, bg="#f0ede4")
        cards.pack(fill="x", pady=(0, 14))

        for i, (lbl, val, color) in enumerate([
            ("Total Income",    f"৳{income:,.0f}", "#1b7a3e"),
            ("Total Expense",   f"৳{expense:,.0f}", "#c0392b"),
            ("Net Profit/Loss", f"৳{net:,.0f}",
             "#1b7a3e" if net >= 0 else "#c0392b"),
        ]):
            card = tk.Frame(cards, bg="white",
                            relief="solid", bd=1, padx=16, pady=14)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            cards.columnconfigure(i, weight=1)
            tk.Label(card, text=lbl, font=("Arial", 9),
                     bg="white", fg="#555").pack()
            tk.Label(card, text=val, font=("Arial", 14, "bold"),
                     bg="white", fg=color).pack()

        # ── TWO COLUMNS ───────────────────────────────
        two = tk.Frame(body, bg="#f0ede4")
        two.pack(fill="both", expand=True, pady=(0, 14))
        two.columnconfigure(0, weight=1)
        two.columnconfigure(1, weight=2)

        # ── FORM ─────────────────────────────────────
        form = tk.LabelFrame(two, text="➕  Add Transaction",
                             font=("Arial", 10, "bold"),
                             bg="#f0ede4", padx=12, pady=10)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(form, text="Type", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w", pady=(0, 2))
        self.type_var = tk.StringVar(value="Income")
        ttk.Combobox(form, textvariable=self.type_var,
                     values=["Income", "Expense"],
                     width=22, state="readonly"
                     ).pack(anchor="w", ipady=3, pady=(0, 8))

        tk.Label(form, text="Category", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w", pady=(0, 2))
        self.cat_var = tk.StringVar(value="Milk Sales")
        ttk.Combobox(form, textvariable=self.cat_var,
                     values=["Milk Sales", "Meat Sales", "Feed Cost",
                             "Medicine", "Labour", "Other"],
                     width=22, state="readonly"
                     ).pack(anchor="w", ipady=3, pady=(0, 8))

        tk.Label(form, text="Amount (৳)", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w", pady=(0, 2))
        self.amount = tk.Entry(form, width=24, font=("Arial", 11),
                               bd=1, relief="solid")
        self.amount.pack(anchor="w", ipady=5, pady=(0, 8))

        tk.Label(form, text="Date (YYYY-MM-DD)", font=("Arial", 9),
                 bg="#f0ede4", fg="#555").pack(anchor="w", pady=(0, 2))
        self.fin_date = tk.Entry(form, width=24, font=("Arial", 11),
                                 bd=1, relief="solid")
        self.fin_date.insert(0, date.today().isoformat())
        self.fin_date.pack(anchor="w", ipady=5, pady=(0, 10))

        tk.Button(form, text="✅  Save Transaction",
                  command=self.save,
                  bg="#2d6a4f", fg="white",
                  font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0,
                  cursor="hand2").pack(anchor="w")

        # ── CHART ─────────────────────────────────────
        chart_frame = tk.LabelFrame(two,
                                    text="📊  Monthly Income vs Expense",
                                    font=("Arial", 10, "bold"),
                                    bg="#f0ede4")
        chart_frame.grid(row=0, column=1, sticky="nsew")
        self._draw_chart(chart_frame)

        # ── TABLE ─────────────────────────────────────
        tbl = tk.LabelFrame(body, text="📋  Recent Transactions",
                            font=("Arial", 10, "bold"),
                            bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True)

        cols   = ("ID", "Type", "Category", "Amount (৳)", "Date")
        widths = {"ID": 40, "Type": 90, "Category": 160,
                  "Amount (৳)": 110, "Date": 110}
        self.tree = ttk.Treeview(tbl, columns=cols,
                                 show="headings", height=7)
        for col in cols:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=widths[col],
                             anchor="w", stretch=True)

        self.tree.tag_configure("income",  foreground="#1b7a3e")
        self.tree.tag_configure("expense", foreground="#c0392b")

        vsb = ttk.Scrollbar(tbl, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.load_data()

    def _draw_chart(self, parent):
        plt.close("all")

        conn = get_connection()
        rows = conn.execute("""
            SELECT strftime('%m', date) AS month,
                   type, SUM(amount)
            FROM financials
            GROUP BY month, type
            ORDER BY month
        """).fetchall()
        conn.close()

        inc_map = {}
        exp_map = {}
        for r in rows:
            if r[1] == "Income":
                inc_map[r[0]] = r[2]
            else:
                exp_map[r[0]] = r[2]

        all_months = sorted(
    set(list(inc_map.keys()) + list(exp_map.keys()))
    - {None}
)

        # Data না থাকলে message দেখাও
        if not all_months:
            tk.Label(parent,
                     text="📊 No data yet.\nAdd transactions to see chart.",
                     font=("Arial", 11), bg="#f0ede4", fg="#888",
                     justify="center").pack(expand=True, pady=40)
            return

        inc = [inc_map.get(m, 0) for m in all_months]
        exp = [exp_map.get(m, 0) for m in all_months]
        x   = list(range(len(all_months)))

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor("#f0ede4")
        ax.set_facecolor("#f8f4e8")

        ax.bar([i - 0.2 for i in x], inc, 0.35,
               label="Income",  color="#52b788")
        ax.bar([i + 0.2 for i in x], exp, 0.35,
               label="Expense", color="#e57373")

        ax.set_xticks(x)
        ax.set_xticklabels(all_months, fontsize=8)
        ax.legend(fontsize=8)
        ax.tick_params(labelsize=8)
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: f"৳{v:,.0f}")
        )
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True,
                                    padx=4, pady=4)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, type, category, amount, date "
            "FROM financials "
            "ORDER BY date DESC, id DESC "
            "LIMIT 100"
        ).fetchall()
        conn.close()
        for r in rows:
            tag = "income" if r[1] == "Income" else "expense"
            self.tree.insert("", "end", values=tuple(r), tags=(tag,))

    def save(self):
        t_type  = self.type_var.get()
        cat     = self.cat_var.get()
        amt_str = self.amount.get().strip()
        dt      = self.fin_date.get().strip()

        if not amt_str or not dt:
            messagebox.showwarning("Missing",
                "Amount and Date are required.")
            return
        try:
            amt = float(amt_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO financials "
                "(type, category, amount, date) "
                "VALUES (?, ?, ?, ?)",
                (t_type, cat, amt, dt)
            )
            conn.commit()
            conn.close()
        except Exception as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        self.amount.delete(0, tk.END)
        self.build()  # পুরো page refresh করে chart ও update হবে
        messagebox.showinfo("Saved", "Transaction saved! ✅")