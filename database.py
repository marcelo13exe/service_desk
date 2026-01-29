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
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chamados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        status TEXT NOT NULL,
        prioridade TEXT NOT NULL,
        data_abertura TEXT NOT NULL,
        prazo_sla TEXT NOT NULL,
        data_fechamento TEXT,
        usuario_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
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