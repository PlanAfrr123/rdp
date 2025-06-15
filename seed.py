import sqlite3

dediks = [
    ("VDS Level 3", 5.00),
    ("VDS Level 4", 19.99),
    ("VDS Level 5", 59.99),
]

conn = sqlite3.connect("dediks.db")
cur = conn.cursor()

cur.execute("DELETE FROM dediks")  # очистить перед добавлением (опционально)

for name, price in dediks:
    cur.execute("INSERT INTO dediks (name, price) VALUES (?, ?)", (name, price))

conn.commit()
print("✅ Тарифы добавлены!")
