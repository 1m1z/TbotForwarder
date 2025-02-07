import sqlite3

conn = sqlite3.connect('forwarder.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY,
        from_chat INTEGER,
        to_chat INTEGER
    )
''')

conn.commit()
conn.close()

print("✅ دیتابیس مقداردهی اولیه شد.")
