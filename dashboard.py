import tkinter as tk
from tkinter import ttk
from rules import run_all_rules

SIDEBAR_BG = "#1b4332"
CONTENT_BG = "#f0ede4"
NAV_ITEMS = [
    ("📊", "Dashboard"),
    ("🐄", "Animal Group"),
    ("🌾", "Feed & Expense"),
    ("💉", "Vaccination"),
    ("💀", "Mortality"),
    ("📦", "Inventory"),
    ("💰", "Financial"),
]

def open_dashboard(root, username="admin"):
    for widget in root.winfo_children():
        widget.destroy()
    root.title("FarmIo — Dashboard")
    root.configure(bg=CONTENT_BG)

    # ── SIDEBAR ──
    sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=200)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # Logo
    tk.Label(sidebar, text="🌿FarmIo", font=("Arial", 15, "bold"),
             bg=SIDEBAR_BG, fg="white").pack(pady=(20, 2))
    tk.Label(sidebar, text="Farm Informations & Operations", font=("Arial", 9),
             bg=SIDEBAR_BG, fg="#95d5b2").pack(pady=(0, 16))
    ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10)

    # Content area
    content = tk.Frame(root, bg=CONTENT_BG)
    content.pack(side="left", fill="both", expand=True)

    # Current page tracker
    current_page = [None]

    def show_page(name):
        for widget in content.winfo_children():
            widget.destroy()
        # Update sidebar highlight
        for btn in nav_buttons:
            if btn["text"].split(" ", 1)[-1] == name:
                btn.config(bg="#40916c", fg="white")
            else:
                btn.config(bg=SIDEBAR_BG, fg="#95d5b2")

        current_page[0] = name
        if name == "Dashboard":
            show_dashboard_page(content, username)
        elif name == "Animal Group":
            from modules.animal import AnimalPage
            AnimalPage(content)
        elif name == "Feed & Expense":
            from modules.feed import FeedPage
            FeedPage(content)
        elif name == "Vaccination":
            from modules.vaccination import VaccinationPage
            VaccinationPage(content)
        elif name == "Mortality":
            from modules.mortality import MortalityPage
            MortalityPage(content)
        elif name == "Inventory":
            from modules.inventory import InventoryPage
            InventoryPage(content)
        elif name == "Financial":
            from modules.financial import FinancialPage
            FinancialPage(content)

    # Nav buttons
    nav_buttons = []
    for icon, name in NAV_ITEMS:
        btn = tk.Button(sidebar, text=f"{icon} {name}",
                        font=("Arial", 11), bg=SIDEBAR_BG, fg="#95d5b2",
                        bd=0, padx=16, pady=10, anchor="w", width=18,
                        cursor="hand2",
                        command=lambda n=name: show_page(n))
        btn.pack(fill="x")
        nav_buttons.append(btn)

    # Logout
    ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=8)
    tk.Label(sidebar, text=f"👤 {username}", font=("Arial", 9),
             bg=SIDEBAR_BG, fg="#74c69d").pack(pady=2)
    tk.Button(sidebar, text="🚪 Logout", font=("Arial", 10),
              bg="#c0392b", fg="white", bd=0, pady=6, cursor="hand2",
              command=lambda: logout(root)).pack(fill="x", padx=16, pady=8)

    # Show dashboard first
    show_page("Dashboard")

def show_dashboard_page(parent, username):
    from database import get_connection
    from datetime import date

    # Topbar
    topbar = tk.Frame(parent, bg="white", height=50)
    topbar.pack(fill="x")
    tk.Label(topbar, text="📊 Dashboard", font=("Arial", 14, "bold"),
             bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)
    tk.Label(topbar, text=f"Today: {date.today().strftime('%d %b %Y')}",
             font=("Arial", 10), bg="white", fg="#555").pack(side="right", padx=20)

    scroll_frame = tk.Frame(parent, bg="#f0ede4")
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=16)

    # ── ALERT BANNER ──
    alerts = run_all_rules()
    alert_frame = tk.LabelFrame(scroll_frame, text="🔔 Alerts", font=("Arial", 10, "bold"),
                                 bg="#f0ede4", fg="#c0392b", pady=8, padx=12)
    alert_frame.pack(fill="x", pady=(0, 14))

    if alerts:
        for tag, msg in alerts:
            tk.Label(alert_frame, text=f"{tag}: {msg}", font=("Arial", 10),
                     bg="#fdecea", fg="#c0392b", padx=8, pady=4,
                     anchor="w", relief="flat").pack(fill="x", pady=2)
    else:
        tk.Label(alert_frame, text="✅ All systems normal. No alerts.",
                 font=("Arial", 10), bg="#d8f3dc", fg="#1b4332",
                 padx=8, pady=4).pack(fill="x")

    # ── STAT CARDS ──
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM animal_groups"); animals = c.fetchone()[0]
    c.execute("SELECT SUM(quantity) FROM inventory"); inv_qty = c.fetchone()[0] or 0
    month_start = date.today().replace(day=1).isoformat()
    c.execute("SELECT SUM(amount) FROM financials WHERE type='Income' AND date>=?", (month_start,))
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM financials WHERE type='Expense' AND date>=?", (month_start,))
    expense = c.fetchone()[0] or 0
    conn.close()

    cards_frame = tk.Frame(scroll_frame, bg="#f0ede4")
    cards_frame.pack(fill="x", pady=(0, 14))

    stats = [
        ("🐄", "Animal Groups", str(animals), "#2d6a4f"),
        ("📦", "Total Stock", f"{inv_qty:.0f} units", "#2471a3"),
        ("💚", "Income (Month)", f"৳{income:,.0f}", "#1b7a3e"),
        ("❤️", "Expense (Month)", f"৳{expense:,.0f}", "#c0392b"),
    ]
    for i, (icon, label, val, color) in enumerate(stats):
        card = tk.Frame(cards_frame, bg="white", relief="flat", bd=1, padx=16, pady=14)
        card.grid(row=0, column=i, padx=6, sticky="nsew")
        cards_frame.columnconfigure(i, weight=1)
        tk.Label(card, text=icon, font=("Arial", 20), bg="white").pack()
        tk.Label(card, text=val, font=("Arial", 16, "bold"), bg="white", fg=color).pack()
        tk.Label(card, text=label, font=("Arial", 9), bg="white", fg="#555").pack()

def logout(root):
    from login import open_login
    open_login(root) 