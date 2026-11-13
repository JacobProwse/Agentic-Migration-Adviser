import sqlite3
from pathlib import Path

""" Initialise database schema """
con = sqlite3.connect(":memory:") # Set up connection
cur = con.cursor()# Set up connection
sql_script = Path(__file__).parent / "schema_v02.sql" # Set up connection
cur.executescript(sql_script.read_text()) # Initialise the database with the schema

""" Set internal database settings """
cur.execute("PRAGMA foreign_keys = ON") # Enable foreign key constraints
cur.execute("PRAGMA user_version = 1") # Set database version

""" Output the database schema """
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

"""  Check foreign key constraints """
try:
    res = cur.execute("INSERT INTO findings (id, file_id, fingerprint, line, detection_rule_code, detection_method, primitive, operation, confidence) VALUES (0, 0, 'fingerprint1', 12, 'DET-PY-007', 'ast', 'rsa', 'key gen', 'high')")
except Exception as e:
    assert isinstance(e, sqlite3.IntegrityError)
    print("Foreign key constraint violation caught as expected:", e)