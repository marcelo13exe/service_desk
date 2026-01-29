from datetime import datetime, timedelta
from storage import (
    inserir_chamado,
    buscar_chamado,
    atualizar_status_chamado,
    inserir_historico,
    inserir_comentario,
)

SLA_POR_PRIORIDADE = {
    "Baixa": 72,
    "Média": 48,
    "Alta": 24,
    "Crítica": 4
}

def criar_evento(tipo, mensagem):
    return {
        "tipo": tipo,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mensagem": mensagem
    }

# 🔑 AGORA RECEBE O USUÁRIO
def abrir_chamado(descricao, prioridade, usuario_id):
    agora = datetime.now()

    horas_sla = SLA_POR_PRIORIDADE.get(prioridade, 48)
    prazo_sla = agora + timedelta(hours=horas_sla)

    chamado_id = inserir_chamado(
        descricao=descricao,
        status="Aberto",
        prioridade=prioridade,
        data_abertura=agora.strftime("%Y-%m-%d %H:%M:%S"),
        prazo_sla=prazo_sla.strftime("%Y-%m-%d %H:%M:%S"),
        usuario_id=usuario_id  # 🔥 vínculo correto
    )

    inserir_historico(
        chamado_id,
        "abertura",
        "Chamado aberto"
    )

    return chamado_id


def consultar_chamado(id_chamado):
    return buscar_chamado(id_chamado)


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


def fechar_chamado(id_chamado):
    chamado = buscar_chamado(id_chamado)

    if not chamado:
        return False, "Chamado não encontrado"

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
        "Chamado fechado pelo sistema"
    )

    return True, "Chamado fechado com sucesso"


def reabrir_chamado(id_chamado):
    chamado = buscar_chamado(id_chamado)
    if not chamado:
        return False

    atualizar_status_chamado(id_chamado, "Aberto", None)

    inserir_historico(
        id_chamado,
        "reabertura",
        "Chamado reaberto pelo usuário"
    )

    return True


def verificar_sla(chamado):
    if chamado["status"] == "Fechado":
        return "Encerrado"

    agora = datetime.now()
    prazo = datetime.strptime(chamado["prazo_sla"], "%Y-%m-%d %H:%M:%S")

    return "SLA ESTOURADO" if agora > prazo else "Dentro do SLA"