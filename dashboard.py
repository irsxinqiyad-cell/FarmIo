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
    for w in root.winfo_children():
        w.destroy()
    root.title("FarmIo — Dashboard")
    root.configure(bg=CONTENT_BG)

    # ── SIDEBAR ──────────────────────────────────────
    sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=210)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="🌿 FarmIo", font=("Arial", 15, "bold"),
             bg=SIDEBAR_BG, fg="white").pack(pady=(20, 2))
    tk.Label(sidebar, text="Farm Informations & Operations",
             font=("Arial", 8), bg=SIDEBAR_BG,
             fg="#95d5b2", wraplength=180).pack(pady=(0, 10))
    ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10)

    # ── CONTENT ──────────────────────────────────────
    content = tk.Frame(root, bg=CONTENT_BG)
    content.pack(side="left", fill="both", expand=True)

    current_page = [None]

    def show_page(name):
        for w in content.winfo_children():
            w.destroy()
        for btn in nav_buttons:
            lbl = btn["text"].split(" ", 1)[-1].strip()
            if lbl == name:
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
        btn = tk.Button(sidebar,
                        text=f"{icon}  {name}",
                        font=("Arial", 11),
                        bg=SIDEBAR_BG, fg="#95d5b2",
                        bd=0, padx=16, pady=10,
                        anchor="w", width=20,
                        cursor="hand2",
                        command=lambda n=name: show_page(n))
        btn.pack(fill="x")
        nav_buttons.append(btn)

    # Logout
    ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=8)
    tk.Label(sidebar, text=f"👤 {username}", font=("Arial", 9),
             bg=SIDEBAR_BG, fg="#74c69d").pack(pady=2)
    tk.Button(sidebar, text="🚪  Logout",
              font=("Arial", 10), bg="#c0392b", fg="white",
              bd=0, pady=6, cursor="hand2",
              command=lambda: _logout(root)
              ).pack(fill="x", padx=16, pady=8)

    show_page("Dashboard")


def show_dashboard_page(parent, username):
    from database import get_connection
    from datetime import date

    # Topbar
    topbar = tk.Frame(parent, bg="white", height=52)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    tk.Label(topbar, text="📊  Dashboard",
             font=("Arial", 14, "bold"),
             bg="white", fg="#1b4332").pack(side="left", padx=20, pady=12)
    tk.Label(topbar,
             text=f"Today: {date.today().strftime('%d %b %Y')}",
             font=("Arial", 10), bg="white", fg="#555"
             ).pack(side="right", padx=20)

    # Scrollable body
    outer = tk.Frame(parent, bg=CONTENT_BG)
    outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(outer, bg=CONTENT_BG, highlightthickness=0)
    sb     = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    body = tk.Frame(canvas, bg=CONTENT_BG)
    win  = canvas.create_window((0, 0), window=body, anchor="nw")

    def _on_resize(event):
        canvas.itemconfig(win, width=event.width)
    canvas.bind("<Configure>", _on_resize)
    body.bind("<Configure>",
              lambda e: canvas.configure(
                  scrollregion=canvas.bbox("all")))

    pad = {"padx": 20, "pady": (0, 14)}

    # ── ALERTS ──
    alerts      = run_all_rules()
    alert_frame = tk.LabelFrame(body, text="🔔  Alerts",
                                font=("Arial", 10, "bold"),
                                bg=CONTENT_BG, fg="#c0392b",
                                pady=8, padx=12)
    alert_frame.pack(fill="x", **pad)

    if alerts:
        for tag, msg in alerts:
            tk.Label(alert_frame,
                     text=f"  {tag}: {msg}",
                     font=("Arial", 10),
                     bg="#fdecea", fg="#c0392b",
                     anchor="w", relief="flat",
                     padx=8, pady=4
                     ).pack(fill="x", pady=2)
    else:
        tk.Label(alert_frame,
                 text="✅  All systems normal. No alerts.",
                 font=("Arial", 10),
                 bg="#d8f3dc", fg="#1b4332",
                 padx=8, pady=4).pack(fill="x")

    # ── STAT CARDS ──
    conn = get_connection()
    c    = conn.cursor()
    c.execute("SELECT COUNT(*) FROM animal_groups")
    animals = c.fetchone()[0]
    c.execute("SELECT SUM(quantity) FROM inventory")
    inv_qty = c.fetchone()[0] or 0
    ms = date.today().replace(day=1).isoformat()
    c.execute("SELECT SUM(amount) FROM financials "
              "WHERE type='Income' AND date>=?", (ms,))
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM financials "
              "WHERE type='Expense' AND date>=?", (ms,))
    expense = c.fetchone()[0] or 0
    conn.close()

    cards_frame = tk.Frame(body, bg=CONTENT_BG)
    cards_frame.pack(fill="x", **pad)

    stats = [
        ("🐄", "Animal Groups",   str(animals),           "#2d6a4f"),
        ("📦", "Total Stock",     f"{inv_qty:.0f} units", "#2471a3"),
        ("💚", "Income (Month)",  f"৳{income:,.0f}",      "#1b7a3e"),
        ("❤️", "Expense (Month)", f"৳{expense:,.0f}",     "#c0392b"),
    ]
    for i, (icon, label, val, color) in enumerate(stats):
        card = tk.Frame(cards_frame, bg="white",
                        relief="solid", bd=1, padx=16, pady=14)
        card.grid(row=0, column=i, padx=6, sticky="nsew")
        cards_frame.columnconfigure(i, weight=1)
        tk.Label(card, text=icon,  font=("Arial", 20),
                 bg="white").pack()
        tk.Label(card, text=val,   font=("Arial", 16, "bold"),
                 bg="white", fg=color).pack()
        tk.Label(card, text=label, font=("Arial", 9),
                 bg="white", fg="#555").pack()


def _logout(root):
    from login import open_login
    open_login(root)