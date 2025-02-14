import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('armoire.db')
cursor = conn.cursor()

cursor.executemany('''
INSERT OR IGNORE INTO users (nom, prenom, identifiant, admin) 
VALUES (?, ?, ?, ?)
''', [
    ("PEREIRA", "Manuel", "MPE", 0),
])

conn.commit()
conn.close()
print("Base de données initialisée.")
