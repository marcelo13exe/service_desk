from datetime import datetime, timedelta
from storage import (
    criar_usuario,
    buscar_usuario_por_email,
    inserir_chamado,
    buscar_chamado,
    buscar_chamados_por_usuario,
    atualizar_status_chamado,
    inserir_historico,
    inserir_comentario
)
from security import hash_senha, verificar_senha, criar_token


# ========= USUÁRIO =========

def registrar_usuario(nome, email, senha):
    senha_hash = hash_senha(senha)
    criar_usuario(nome, email, senha_hash)

def login_usuario(email, senha):
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


# ========= SLA =========
SLA_POR_PRIORIDADE = {
    "Baixa": 72,
    "Média": 48,
    "Alta": 24,
    "Crítica": 4
}


# ========= CHAMADOS =========
def abrir_chamado(descricao: str, prioridade: str, usuario_id: int):
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
        "Chamado aberto"
    )

    return chamado_id


def consultar_chamado(id_chamado: int):
    return buscar_chamado(id_chamado)


def listar_meus_chamados(usuario_id: int):
    return buscar_chamados_por_usuario(usuario_id)


def fechar_chamado(id_chamado: int, usuario_id: int):
    chamado = buscar_chamado(id_chamado)

    if not chamado:
        return False, "Chamado não encontrado"

    if chamado["usuario_id"] != usuario_id:
        return False, "Você não tem permissão para fechar este chamado"

    if chamado["status"] == "Fechado":
        return False, "Chamado já está fechado"

    data_fechamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    atualizar_status_chamado(
        id_chamado=id_chamado,
        status="Fechado",
        data_fechamento=data_fechamento
    )

    inserir_historico(
        id_chamado,
        "fechamento",
        "Chamado fechado pelo usuário"
    )

    return True, "Chamado fechado com sucesso"


def adicionar_comentario_chamado(id_chamado: int, mensagem: str):
    chamado = buscar_chamado(id_chamado)

    if not chamado:
        return False

    inserir_comentario(
        chamado_id=id_chamado,
        mensagem=mensagem
    )

    return True


def verificar_sla(chamado: dict):
    if chamado["status"] == "Fechado":
        return "Encerrado"

    agora = datetime.now()
    prazo = datetime.strptime(chamado["prazo_sla"], "%Y-%m-%d %H:%M:%S")

    if agora > prazo:
        return "SLA ESTOURADO"

    return "Dentro do SLA"

print(">>> FUNÇÕES DEFINIDAS <<<")