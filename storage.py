from database import get_connection

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


   cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
   row = cursor.fetchone()
   conn.close()


   return dict(row) if row else None

def inserir_chamado(descricao, status, prioridade, data_abertura, prazo_sla):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chamados (
            descricao, status, prioridade, data_abertura, prazo_sla
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        descricao,
        status,
        prioridade,
        data_abertura,
        prazo_sla
    ))

    conn.commit()
    chamado_id = cursor.lastrowid
    conn.close()

    return chamado_id


def buscar_chamado(id_chamado):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM chamados WHERE id = ?", (id_chamado,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def atualizar_status_chamado(id_chamado, status, data_fechamento):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chamados
        SET status = ?, data_fechamento = ?
        WHERE id = ?
    """, (status, data_fechamento, id_chamado))

    conn.commit()
    conn.close()


def inserir_historico(chamado_id, tipo, mensagem):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO historico (chamado_id, tipo, data, mensagem)
        VALUES (?, ?, datetime('now'), ?)
    """, (chamado_id, tipo, mensagem))

    conn.commit()
    conn.close()


def inserir_comentario(chamado_id, mensagem):
    inserir_historico(chamado_id, "comentario", mensagem)