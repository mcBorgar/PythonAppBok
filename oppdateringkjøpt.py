import sqlite3

conn = sqlite3.connect('varer.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS varer (
    id INTEGER PRIMARY KEY,
    navn TEXT NOT NULL,
    antall INTEGER NOT NULL
)
''')

def oppdater_vare(vare_id, nytt_antall):
    cursor.execute('''
    UPDATE varer
    SET antall = ?
    WHERE id = ?
    ''', (nytt_antall, vare_id))
    conn.commit()

vare_id = 1
nytt_antall = 5  
oppdater_vare(vare_id, nytt_antall)

conn.close()