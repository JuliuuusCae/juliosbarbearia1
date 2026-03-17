import sqlite3
from flask import g
from config import Config

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            Config.DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with db:
        db.execute("""CREATE TABLE IF NOT EXISTS horarios(id INTEGER PRIMARY KEY AUTOINCREMENT, horario TEXT UNIQUE)""")
        db.execute("""CREATE TABLE IF NOT EXISTS agendamentos(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, telefone TEXT, data TEXT, horario TEXT, servico TEXT)""")

        # Adicionar colunas faltantes se o esquema for antigo
        # É mais seguro verificar a existência da coluna antes de tentar adicionar
        cursor = db.execute("PRAGMA table_info(agendamentos)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'telefone' not in columns:
            db.execute("ALTER TABLE agendamentos ADD COLUMN telefone TEXT")
        if 'data' not in columns:
            db.execute("ALTER TABLE agendamentos ADD COLUMN data TEXT")
        if 'servico' not in columns:
            db.execute("ALTER TABLE agendamentos ADD COLUMN servico TEXT")

        # Inserir horários padrão se a tabela estiver vazia
        cursor = db.execute("SELECT COUNT(*) FROM horarios")
        if cursor.fetchone()[0] == 0:
            from app import HORARIOS_PADRAO # Importar de app.py temporariamente para evitar circular import
            for horario in HORARIOS_PADRAO:
                db.execute("INSERT INTO horarios(horario) VALUES (?)", (horario,))

    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
