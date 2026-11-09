import sqlite3
from pathlib import Path
con = sqlite3.connect(":memory:")

cur = con.cursor()

sql_script = Path(__file__).parent / "schema_v02.sql"

cur.executescript(sql_script.read_text())

res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchone())