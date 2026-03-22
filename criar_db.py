import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# horários agora com dia da semana
cur.execute("""
CREATE TABLE horarios(
id INTEGER PRIMARY KEY AUTOINCREMENT,
dia_semana TEXT,
horario TEXT
)
""")

# agendamentos
cur.execute("""
CREATE TABLE agendamentos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
servico TEXT,
data TEXT,
horario TEXT
)
""")

conn.commit()
print("Banco criado com sucesso!")