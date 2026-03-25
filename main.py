import tkinter as tk
from database import initialize_database
from login import open_login

def main():
    # Initialize database first
    initialize_database()

    # Create main window
    root = tk.Tk()
    root.title("FarmIo")
    root.geometry("1100x700")
    root.minsize(900, 600)

    # Open login screen
    open_login(root)

    # Start the app
    root.mainloop()

if __name__ == "__main__":
    main()