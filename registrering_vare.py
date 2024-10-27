import sqlite3

conn = sqlite3.connect('varer.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS varer (
    id INTEGER PRIMARY KEY,
    navn TEXT NOT NULL,
    antall INTEGER NOT NULL,
    pris REAL NOT NULL
)
''')

def legg_til_vare(navn, antall, pris):
    cursor.execute('''
    INSERT INTO varer (navn, antall, pris)
    VALUES (?, ?, ?)
    ''', (navn, antall, pris))
    conn.commit()

def oppdater_vare(vare_id, nytt_antall):
    cursor.execute('''
    UPDATE varer
    SET antall = ?
    WHERE id = ?
    ''', (nytt_antall, vare_id))
    conn.commit()

def vis_varer(sort_by=None):
    query = 'SELECT * FROM varer'
    if sort_by:
        query += f' ORDER BY {sort_by}'
    cursor.execute(query)
    varer = cursor.fetchall()
    for vare in varer:
        print(f'ID: {vare[0]}, Navn: {vare[1]}, Antall: {vare[2]}, Pris: {vare[3]}')

def main():
    while True:
        print("\n1. Legg til vare")
        print("2. Oppdater vare")
        print("3. Vis varer")
        print("4. Sorter varer")
        print("5. Avslutt")
        
        valg = input("Velg et alternativ (1-5): ")
        
        if valg == '1':
            navn = input("Skriv inn navnet på varen: ")
            antall = int(input("Skriv inn antall: "))
            pris = float(input("Skriv inn pris: "))
            legg_til_vare(navn, antall, pris)
            print(f'Vare "{navn}" med antall {antall} og pris {pris} lagt til.')
        
        elif valg == '2':
            vare_id = int(input("Skriv inn ID-en til varen du vil oppdatere: "))
            nytt_antall = int(input("Skriv inn nytt antall: "))
            oppdater_vare(vare_id, nytt_antall)
            print(f'Vare med ID {vare_id} oppdatert til antall {nytt_antall}.')
        
        elif valg == '3':
            vis_varer()
        
        elif valg == '4':
            sort_option = input("Sorter etter (navn, antall, pris): ")
            vis_varer(sort_by=sort_option)
        
        elif valg == '5':
            print("Avslutter programmet.")
            break
        
        else:
            print("Ugyldig valg, prøv igjen.")

if __name__ == "__main__":
    main()

conn.close()
