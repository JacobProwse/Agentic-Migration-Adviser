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
        print(field[1], field[2], field[3])

res = cur.execute("PRAGMA foreign_keys")
print(res.fetchall())
cur.execute("PRAGMA foreign_keys = OFF")
res = cur.execute("PRAGMA foreign_keys")
print(res.fetchall())
res = cur.execute("INSERT INTO findings (id, file_id, fingerprint, line, detection_rule_code, detection_method, primitive, operation, confidence) VALUES (0, 0, 'fingerprint1', 12, 'DET-PY-007', 'ast', 'rsa', 'key gen', 'high')")
cur.execute("PRAGMA foreign_keys = ON")
res = cur.execute("INSERT INTO findings (id, file_id, fingerprint, line, detection_rule_code, detection_method, primitive, operation, confidence) VALUES (1, 1, 'fingerprint1', 12, 'DET-PY-007', 'ast', 'rsa', 'key gen', 'high')")