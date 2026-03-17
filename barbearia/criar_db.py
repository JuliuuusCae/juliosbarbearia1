import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE horarios(
id INTEGER PRIMARY KEY AUTOINCREMENT,
horario TEXT
)
""")

cur.execute("""
CREATE TABLE agendamentos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
telefone TEXT,
data TEXT,
horario TEXT
)
""")

conn.commit()

print("Banco criado com sucesso!")