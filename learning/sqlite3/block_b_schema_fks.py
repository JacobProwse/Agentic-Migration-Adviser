import sqlite3
from pathlib import Path
con = sqlite3.connect(":memory:")

cur = con.cursor()

sql_script = Path(__file__).parent / "schema_v02.sql"

cur.executescript(sql_script.read_text())

res = cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = res.fetchall()
print(tables)

for table in tables:
    table_name = table[0]
    res = cur.execute("PRAGMA table_info({})".format(table_name))
    fields = res.fetchall()
    print("\n")
    print(f"Table: {table_name}")
    for field in fields:
        print(field[1], field[2])  # field name and type