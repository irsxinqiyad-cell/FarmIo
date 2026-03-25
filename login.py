import tkinter as tk
from tkinter import messagebox
from database import get_connection

def open_login(root):
    # Clear window
    for widget in root.winfo_children():
        widget.destroy()

    root.title("FarmIo — Login")
    root.configure(bg="#1b4332")

    # Center frame
    frame = tk.Frame(root, bg="#f8f4e8", padx=40, pady=40)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    # Logo
    tk.Label(frame, text="🌿", font=("Arial", 36), bg="#f8f4e8").pack()
    tk.Label(frame, text="FarmIo", font=("Arial", 22, "bold"), bg="#f8f4e8", fg="#1b4332").pack()
    tk.Label(frame, text="Farm Operations Management", font=("Arial", 10), bg="#f8f4e8", fg="#555").pack(pady=(0, 20))

    # Username
    tk.Label(frame, text="USERNAME", font=("Arial", 9, "bold"), bg="#f8f4e8", fg="#555").pack(anchor="w")
    username_entry = tk.Entry(frame, width=28, font=("Arial", 12), bd=1, relief="solid")
    username_entry.pack(pady=(2, 12), ipady=6)

    # Password
    tk.Label(frame, text="PASSWORD", font=("Arial", 9, "bold"), bg="#f8f4e8", fg="#555").pack(anchor="w")
    password_entry = tk.Entry(frame, width=28, font=("Arial", 12), bd=1, relief="solid", show="*")
    password_entry.pack(pady=(2, 20), ipady=6)

    # Error label
    error_label = tk.Label(frame, text="", font=("Arial", 10), bg="#f8f4e8", fg="red")
    error_label.pack()

    def do_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            error_label.config(text="⚠️ Please enter username and password.")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            from dashboard import open_dashboard
            open_dashboard(root, username)
        else:
            error_label.config(text="❌ Invalid credentials. Try again.")
            password_entry.delete(0, tk.END)

    # Login button
    tk.Button(frame, text="Login →", command=do_login,
              bg="#2d6a4f", fg="white", font=("Arial", 12, "bold"),
              width=24, pady=8, bd=0, cursor="hand2").pack(pady=(10, 0))

    # Default hint
    tk.Label(frame, text="Default: admin / admin123",
             font=("Arial", 9), bg="#d8f3dc", fg="#2d6a4f",
             padx=10, pady=6).pack(pady=(16, 0))

    # Enter key binding
    root.bind("<Return>", lambda e: do_login())