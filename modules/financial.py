import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FinancialPage:
    def __init__(self, parent):
        self.parent = parent
        self.build()

    def build(self):
        for w in self.parent.winfo_children(): w.destroy()

        tb = tk.Frame(self.parent, bg="white")
        tb.pack(fill="x")
        tk.Label(tb, text="💰 Financial Report", font=("Arial", 14, "bold"),
                 bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.parent, bg="#f0ede4")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Stat cards
        month_start = date.today().replace(day=1).isoformat()
        conn = get_connection()
        income = conn.execute("SELECT SUM(amount) FROM financials WHERE type='Income' AND date>=?", (month_start,)).fetchone()[0] or 0
        expense = conn.execute("SELECT SUM(amount) FROM financials WHERE type='Expense' AND date>=?", (month_start,)).fetchone()[0] or 0
        conn.close()
        net = income - expense

        cards = tk.Frame(body, bg="#f0ede4"); cards.pack(fill="x", pady=(0,14))
        for i, (lbl, val, color) in enumerate([
            ("Total Income", f"৳{income:,.0f}", "#1b7a3e"),
            ("Total Expense", f"৳{expense:,.0f}", "#c0392b"),
            ("Net Profit/Loss", f"৳{net:,.0f}", "#1b7a3e" if net>=0 else "#c0392b"),
        ]):
            card = tk.Frame(cards, bg="white", padx=16, pady=14)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            cards.columnconfigure(i, weight=1)
            tk.Label(card, text=lbl, font=("Arial", 9), bg="white", fg="#555").pack()
            tk.Label(card, text=val, font=("Arial", 14, "bold"), bg="white", fg=color).pack()

        two_col = tk.Frame(body, bg="#f0ede4"); two_col.pack(fill="both", expand=True)
        two_col.columnconfigure(0, weight=1); two_col.columnconfigure(1, weight=1)

        # Form
        form = tk.LabelFrame(two_col, text="➕ Add Transaction",
                              font=("Arial", 10, "bold"), bg="#f0ede4", padx=12, pady=10)
        form.grid(row=0, column=0, padx=(0,8), sticky="nsew")

        self.type_var = tk.StringVar(value="Income")
        self.cat_var = tk.StringVar(value="Milk Sales")
        tk.Label(form, text="Type", font=("Arial", 9), bg="#f0ede4").pack(anchor="w")
        ttk.Combobox(form, textvariable=self.type_var, values=["Income","Expense"], width=20).pack(ipady=3, pady=(0,6))
        tk.Label(form, text="Category", font=("Arial", 9), bg="#f0ede4").pack(anchor="w")
        ttk.Combobox(form, textvariable=self.cat_var,
                     values=["Milk Sales","Meat Sales","Feed Cost","Medicine","Labour","Other"],
                     width=20).pack(ipady=3, pady=(0,6))
        tk.Label(form, text="Amount (৳)", font=("Arial", 9), bg="#f0ede4").pack(anchor="w")
        self.amount = tk.Entry(form, width=22, font=("Arial", 11), bd=1, relief="solid")
        self.amount.pack(ipady=5, pady=(0,6))
        tk.Label(form, text="Date", font=("Arial", 9), bg="#f0ede4").pack(anchor="w")
        self.fin_date = tk.Entry(form, width=22, font=("Arial", 11), bd=1, relief="solid")
        self.fin_date.insert(0, date.today().isoformat()); self.fin_date.pack(ipady=5, pady=(0,8))
        tk.Button(form, text="✅ Save", command=self.save,
                  bg="#2d6a4f", fg="white", font=("Arial", 10, "bold"),
                  padx=16, pady=6, bd=0, cursor="hand2").pack()

        # Chart
        chart_frame = tk.LabelFrame(two_col, text="📊 Income vs Expense",
                                     font=("Arial", 10, "bold"), bg="#f0ede4")
        chart_frame.grid(row=0, column=1, sticky="nsew")
        self.draw_chart(chart_frame)

        # Table
        tbl = tk.LabelFrame(body, text="📋 Recent Transactions",
                             font=("Arial", 10, "bold"), bg="#f0ede4", padx=8, pady=8)
        tbl.pack(fill="both", expand=True, pady=(14,0))
        cols = ("ID", "Type", "Category", "Amount", "Date")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings", height=6)
        for col in cols:
            self.tree.heading(col, text=col); self.tree.column(col, width=110)
        self.tree.pack(fill="both", expand=True)
        self.load_data()

    def draw_chart(self, parent):
        conn = get_connection()
        rows = conn.execute("""
            SELECT strftime('%m', date) as month, type, SUM(amount)
            FROM financials GROUP BY month, type ORDER BY month
        """).fetchall()
        conn.close()
        months_income = {}; months_expense = {}
        for r in rows:
            if r[1]=="Income": months_income[r[0]] = r[2]
            else: months_expense[r[0]] = r[2]
        all_months = sorted(set(list(months_income.keys())+list(months_expense.keys())))
        if not all_months: all_months = ["--"]
        inc = [months_income.get(m,0) for m in all_months]
        exp = [months_expense.get(m,0) for m in all_months]
        x = range(len(all_months))
        fig, ax = plt.subplots(figsize=(4,3))
        fig.patch.set_facecolor("#f0ede4")
        ax.set_facecolor("#f8f4e8")
        ax.bar([i-0.2 for i in x], inc, 0.35, label="Income", color="#52b788")
        ax.bar([i+0.2 for i in x], exp, 0.35, label="Expense", color="#e57373")
        ax.set_xticks(list(x)); ax.set_xticklabels(all_months, fontsize=8)
        ax.legend(fontsize=8); ax.tick_params(labelsize=8)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        conn = get_connection()
        rows = conn.execute("SELECT * FROM financials ORDER BY date DESC LIMIT 50").fetchall()
        conn.close()
        for r in rows: self.tree.insert("", "end", values=tuple(r))

    def save(self):
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO financials (type, category, amount, date) VALUES (?,?,?,?)",
                (self.type_var.get(), self.cat_var.get(), float(self.amount.get()), self.fin_date.get())
            )
            conn.commit(); conn.close()
            self.load_data()
            messagebox.showinfo("Saved", "Transaction saved!")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))