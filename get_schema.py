import sqlite3
import json

conn = sqlite3.connect('food_recognition.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

schema = {}
for table in tables:
    table_name = table['name']
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    schema[table_name] = [{'name': col['name'], 'type': col['type']} for col in columns]

with open('schema.json', 'w', encoding='utf-8') as f:
    json.dump(schema, f, indent=4)
