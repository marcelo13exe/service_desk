from datetime import datetime, timedeltafrom datetime import datetime, timedelta

from storage import (
    # usuários
    criar_usuario,
    buscar_usuario_por_email,

    # chamados
    inserir_chamado,
    buscar_chamado,
    buscar_chamados_por_usuario,
    atualizar_status_chamado,

    # extras
    inserir_historico,
    inserir_comentario,
)

from security import (
    hash_senha,
    verificar_senha,
    criar_token
)

# ==========================
# SLA
# ==========================

SLA_POR_PRIORIDADE = {
    "Baixa": 72,
    "Média": 48,
    "Alta": 24,
    "Crítica": 4
}


# ==========================
# USUÁRIOS
# ==========================

def registrar_usuario(nome, email, senha):
    """
    Cria usuário no banco com senha hash
    """
    senha_hash = hash_senha(senha)
    criar_usuario(nome, email, senha_hash)


def login_usuario(email, senha):
    """
    Verifica login e retorna token JWT
    """
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return None

    if not verificar_senha(senha, usuario["senha_hash"]):
        return None

    token = criar_token({
        "sub": str(usuario["id"]),
        "email": usuario["email"]
    })

    return token


# ==========================
# CHAMADOS
# ==========================

def abrir_chamado(descricao, prioridade, usuario_id):
    """
    Abre chamado vinculado ao usuário logado
    """
    agora = datetime.now()

    horas_sla = SLA_POR_PRIORIDADE.get(prioridade, 48)
    prazo_sla = agora + timedelta(hours=horas_sla)

    chamado_id = inserir_chamado(
        descricao=descricao,
        status="Aberto",
        prioridade=prioridade,
        data_abertura=agora.strftime("%Y-%m-%d %H:%M:%S"),
        prazo_sla=prazo_sla.strftime("%Y-%m-%d %H:%M:%S"),
        usuario_id=usuario_id
    )

    inserir_historico(
        chamado_id,
        "abertura",
        "Chamado aberto pelo usuário"
    )

    return chamado_id


def consultar_chamado(id_chamado):
    return buscar_chamado(id_chamado)


def listar_meus_chamados(usuario_id):
    """
    Retorna todos chamados do usuário logado
    """
    return buscar_chamados_por_usuario(usuario_id)


def adicionar_comentario_chamado(id_chamado, texto):
    chamado = buscar_chamado(id_chamado)

    if not chamado:
        return False

    inserir_comentario(id_chamado, texto)

    inserir_historico(
        id_chamado,
        "comentario",
        texto
    )

    return True


def fechar_chamado(id_chamado, usuario_id):
    """
    Fecha chamado apenas se for do usuário logado
    """
    chamado = buscar_chamado(id_chamado)

    if not chamado:
        return False, "Chamado não encontrado"

    if chamado["usuario_id"] != usuario_id:
        return False, "Você não tem permissão para fechar este chamado"

    if chamado["status"] == "Fechado":
        return False, "Chamado já está fechado"

    atualizar_status_chamado(
        id_chamado,
        "Fechado",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    inserir_historico(
        id_chamado,
        "fechamento",
        "Chamado fechado pelo usuário"
    )

    return True, "Chamado fechado com sucesso"


def verificar_sla(chamado):
    if chamado["status"] == "Fechado":
        return "Encerrado"

    agora = datetime.now()
    prazo = datetime.strptime(chamado["prazo_sla"], "%Y-%m-%d %H:%M:%S")

    return "SLA ESTOURADO" if agora > prazo else "Dentro do SLA"

