from database import get_connection
from datetime import date, timedelta

def run_all_rules():
    alerts = []
    conn   = get_connection()
    c      = conn.cursor()
    today  = date.today().isoformat()

    # Rule 1: Vaccination overdue
    c.execute("SELECT COUNT(*) FROM vaccinations WHERE next_due < ?", (today,))
    count = c.fetchone()[0]
    if count > 0:
        alerts.append(("🔴 Rule 1",
                        f"{count} vaccination(s) are overdue!"))

    # Rule 2: High mortality (>5 deaths in last 7 days)
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    c.execute("SELECT SUM(death_count) FROM mortality WHERE date >= ?", (week_ago,))
    deaths = c.fetchone()[0] or 0
    if deaths > 5:
        alerts.append(("🔴 Rule 2",
                        f"High mortality: {deaths} deaths in last 7 days!"))

    # Rule 3: Feed cost spike (this week > last week × 1.3)
    this_week_start = (date.today() - timedelta(days=7)).isoformat()
    last_week_start = (date.today() - timedelta(days=14)).isoformat()
    c.execute("SELECT SUM(cost) FROM feed_expenses WHERE date >= ?",
              (this_week_start,))
    this_week = c.fetchone()[0] or 0
    c.execute("SELECT SUM(cost) FROM feed_expenses WHERE date >= ? AND date < ?",
              (last_week_start, this_week_start))
    last_week = c.fetchone()[0] or 0
    if last_week > 0 and this_week > last_week * 1.3:
        alerts.append(("🟡 Rule 3",
                        f"Feed cost spike! This week: {this_week:.0f} "
                        f"vs last week: {last_week:.0f}"))

    # Rule 4: Low inventory
    c.execute("SELECT COUNT(*) FROM inventory WHERE quantity < min_threshold")
    low = c.fetchone()[0]
    if low > 0:
        alerts.append(("🟡 Rule 4",
                        f"{low} inventory item(s) below minimum threshold!"))

    # Rule 5: Monthly loss
    month_start = date.today().replace(day=1).isoformat()
    c.execute("SELECT SUM(amount) FROM financials "
              "WHERE type='Income' AND date >= ?", (month_start,))
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM financials "
              "WHERE type='Expense' AND date >= ?", (month_start,))
    expense = c.fetchone()[0] or 0
    if expense > income:
        alerts.append(("🔴 Rule 5",
                        f"Monthly LOSS! Income: ৳{income:,.0f} | "
                        f"Expense: ৳{expense:,.0f}"))

    conn.close()
    return alerts