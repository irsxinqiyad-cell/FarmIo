import sqlite3
import os

# ── DB সবসময় এই script এর পাশে থাকবে ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "farmio.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # data loss থেকে রক্ষা করে
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def initialize_database():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS animal_groups (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            animal_type TEXT    NOT NULL,
            quantity    INTEGER NOT NULL,
            age_months  INTEGER,
            purpose     TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS vaccinations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id     INTEGER,
            vaccine_name TEXT NOT NULL,
            given_date   TEXT NOT NULL,
            next_due     TEXT NOT NULL,
            FOREIGN KEY(group_id) REFERENCES animal_groups(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS feed_expenses (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id  INTEGER,
            feed_type TEXT NOT NULL,
            quantity  REAL NOT NULL,
            cost      REAL NOT NULL,
            date      TEXT NOT NULL,
            FOREIGN KEY(group_id) REFERENCES animal_groups(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS mortality (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id    INTEGER,
            death_count INTEGER NOT NULL,
            date        TEXT    NOT NULL,
            reason      TEXT,
            FOREIGN KEY(group_id) REFERENCES animal_groups(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name     TEXT NOT NULL,
            quantity      REAL NOT NULL,
            unit          TEXT NOT NULL,
            min_threshold REAL NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS financials (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            type     TEXT NOT NULL,
            category TEXT NOT NULL,
            amount   REAL NOT NULL,
            date     TEXT NOT NULL
        )
    """)

    # Default admin
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?,?)",
              ("admin", "admin123"))

    conn.commit()
    conn.close()
    print(f"✅ Database ready → {DB_PATH}")


# ══════════════════════════════════════════════════════
#  CSV IMPORT  ─  বাইরে থেকে data দেওয়ার সিস্টেম
# ══════════════════════════════════════════════════════
import csv
from datetime import datetime

def import_from_csv(filepath: str) -> tuple[int, list[str]]:
    """
    যেকোনো CSV ফাইল import করে।
    CSV এর প্রথম row = header (column নাম)।
    Column নাম database এর table ও field নাম দিয়ে match করে।

    Supported tables (CSV এ 'table' column দিয়ে বলতে হবে):
        animal_groups | vaccinations | feed_expenses |
        mortality     | inventory    | financials

    Returns: (সফল row সংখ্যা, error message list)
    """
    TABLE_MAP = {
        "animal_groups": _import_animal,
        "vaccinations":  _import_vaccination,
        "feed_expenses": _import_feed,
        "mortality":     _import_mortality,
        "inventory":     _import_inventory,
        "financials":    _import_financial,
    }

    success = 0
    errors  = []

    try:
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows   = list(reader)
    except Exception as e:
        return 0, [f"CSV পড়তে ব্যর্থ: {e}"]

    if not rows:
        return 0, ["CSV ফাইলে কোনো data নেই।"]

    # 'table' column আছে কিনা দেখো
    first = rows[0]
    if "table" not in first:
        return 0, ["CSV এ 'table' column নেই। প্রথম column এর নাম 'table' হতে হবে।"]

    conn = get_connection()
    for i, row in enumerate(rows, start=2):   # row 1 = header
        table = row.get("table", "").strip().lower()
        fn    = TABLE_MAP.get(table)
        if not fn:
            errors.append(f"Row {i}: অজানা table '{table}'")
            continue
        err = fn(conn, row, i)
        if err:
            errors.append(err)
        else:
            success += 1
    conn.commit()
    conn.close()
    return success, errors


# ── per-table import helpers ──────────────────────────

def _import_animal(conn, row, i):
    try:
        conn.execute(
            "INSERT INTO animal_groups (name,animal_type,quantity,age_months,purpose) VALUES(?,?,?,?,?)",
            (row["name"], row["animal_type"], int(row["quantity"]),
             int(row["age_months"]) if row.get("age_months") else None,
             row.get("purpose",""))
        )
    except Exception as e:
        return f"Row {i} (animal_groups): {e}"

def _import_vaccination(conn, row, i):
    try:
        # group_id বের করো নাম থেকে
        gid = _group_id_by_name(conn, row.get("group_name",""))
        conn.execute(
            "INSERT INTO vaccinations (group_id,vaccine_name,given_date,next_due) VALUES(?,?,?,?)",
            (gid, row["vaccine_name"], row["given_date"], row["next_due"])
        )
    except Exception as e:
        return f"Row {i} (vaccinations): {e}"

def _import_feed(conn, row, i):
    try:
        gid = _group_id_by_name(conn, row.get("group_name",""))
        conn.execute(
            "INSERT INTO feed_expenses (group_id,feed_type,quantity,cost,date) VALUES(?,?,?,?,?)",
            (gid, row["feed_type"], float(row["quantity"]),
             float(row["cost"]), row["date"])
        )
    except Exception as e:
        return f"Row {i} (feed_expenses): {e}"

def _import_mortality(conn, row, i):
    try:
        gid = _group_id_by_name(conn, row.get("group_name",""))
        conn.execute(
            "INSERT INTO mortality (group_id,death_count,date,reason) VALUES(?,?,?,?)",
            (gid, int(row["death_count"]), row["date"], row.get("reason",""))
        )
    except Exception as e:
        return f"Row {i} (mortality): {e}"

def _import_inventory(conn, row, i):
    try:
        conn.execute(
            "INSERT INTO inventory (item_name,quantity,unit,min_threshold) VALUES(?,?,?,?)",
            (row["item_name"], float(row["quantity"]),
             row["unit"], float(row["min_threshold"]))
        )
    except Exception as e:
        return f"Row {i} (inventory): {e}"

def _import_financial(conn, row, i):
    try:
        conn.execute(
            "INSERT INTO financials (type,category,amount,date) VALUES(?,?,?,?)",
            (row["type"], row["category"], float(row["amount"]), row["date"])
        )
    except Exception as e:
        return f"Row {i} (financials): {e}"

def _group_id_by_name(conn, name):
    r = conn.execute(
        "SELECT id FROM animal_groups WHERE name=?", (name,)
    ).fetchone()
    return r[0] if r else None