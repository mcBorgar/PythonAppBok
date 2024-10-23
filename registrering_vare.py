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

def legg_til_vare(navn, antall):
    cursor.execute('''
    INSERT INTO varer (navn, antall)
    VALUES (?, ?)
    ''', (navn, antall))
    conn.commit()

def oppdater_vare(vare_id, nytt_antall):
    cursor.execute('''
    UPDATE varer
    SET antall = ?
    WHERE id = ?
    ''', (nytt_antall, vare_id))
    conn.commit()

def vis_varer():
    cursor.execute('SELECT * FROM varer')
    varer = cursor.fetchall()
    for vare in varer:
        print(f'ID: {vare[0]}, Navn: {vare[1]}, Antall: {vare[2]}')

def main():
    while True:
        print("\n1. Legg til vare")
        print("2. Oppdater vare")
        print("3. Vis varer")
        print("4. Avslutt")
        
        valg = input("Velg et alternativ (1-4): ")
        
        if valg == '1':
            navn = input("Skriv inn navnet på varen: ")
            antall = int(input("Skriv inn antall: "))
            legg_til_vare(navn, antall)
            print(f'Vare "{navn}" med antall {antall} lagt til.')
        
        elif valg == '2':
            vare_id = int(input("Skriv inn ID-en til varen du vil oppdatere: "))
            nytt_antall = int(input("Skriv inn nytt antall: "))
            oppdater_vare(vare_id, nytt_antall)
            print(f'Vare med ID {vare_id} oppdatert til antall {nytt_antall}.')
        
        elif valg == '3':
            vis_varer()
        
        elif valg == '4':
            print("Avslutter programmet.")
            break
        
        else:
            print("Ugyldig valg, prøv igjen.")

if __name__ == "__main__":
    main()

conn.close()