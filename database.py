import sqlite3

DB_NAME = "chamados.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chamados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT,
        status TEXT,
        prioridade TEXT,
        data_abertura TEXT,
        prazo_sla TEXT,
        data_fechamento TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chamado_id INTEGER,
        tipo TEXT,
        data TEXT,
        mensagem TEXT
    )
    """)

    conn.commit()
    conn.close()