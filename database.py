import sqlite3
import os

DB_NAME = "farmio.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Animal groups table
    c.execute("""
        CREATE TABLE IF NOT EXISTS animal_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            animal_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            age_months INTEGER,
            purpose TEXT
        )
    """)

    # Vaccinations table
    c.execute("""
        CREATE TABLE IF NOT EXISTS vaccinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            vaccine_name TEXT NOT NULL,
            given_date TEXT NOT NULL,
            next_due TEXT NOT NULL,
            FOREIGN KEY(group_id) REFERENCES animal_groups(id)
        )
    """)

    # Feed expenses table
    c.execute("""
        CREATE TABLE IF NOT EXISTS feed_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            feed_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            cost REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(group_id) REFERENCES animal_groups(id)
        )
    """)

    # Mortality table
    c.execute("""
        CREATE TABLE IF NOT EXISTS mortality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            death_count INTEGER NOT NULL,
            date TEXT NOT NULL,
            reason TEXT,
            FOREIGN KEY(group_id) REFERENCES animal_groups(id)
        )
    """)

    # Inventory table
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            min_threshold REAL NOT NULL
        )
    """)

    # Financials table
    c.execute("""
        CREATE TABLE IF NOT EXISTS financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)

    # Default admin user (password: admin123)
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
              ("admin", "admin123"))

    conn.commit()
    conn.close()
    print("✅ Database initialized.")