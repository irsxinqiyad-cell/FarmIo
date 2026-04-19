import tkinter as tk
from database import initialize_database
from login import open_login

def main():
    initialize_database()

    root = tk.Tk()
    root.title("FarmIo")
    root.geometry("1150x720")
    root.minsize(950, 620)

    open_login(root)
    root.mainloop()

if __name__ == "__main__":
    main()