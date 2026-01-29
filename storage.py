from database import get_connection


# ==========================
# USUÁRIOS
# ==========================

def criar_usuario(nome, email, senha_hash):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha_hash)
        VALUES (?, ?, ?)
    """, (nome, email, senha_hash))

    conn.commit()
    conn.close()


def buscar_usuario_por_email(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM usuarios WHERE email = ?
    """, (email,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


# ==========================
# CHAMADOS
# ==========================

def inserir_chamado(descricao, status, prioridade, data_abertura, prazo_sla, usuario_id):
    """
    Agora o chamado fica vinc
