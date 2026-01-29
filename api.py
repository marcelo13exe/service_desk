from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.hash import bcrypt

from services_layer import (
    abrir_chamado,
    consultar_chamado,
    adicionar_comentario_chamado,
    fechar_chamado
)

from storage import (
    criar_usuario,
    buscar_usuario_por_email
)

from database import init_db

app = FastAPI(title="Service Desk API")


# ✅ Inicializa banco quando subir
@app.on_event("startup")
def startup():
    init_db()


# -------------------------------
# ✅ HOME
# -------------------------------
@app.get("/")
def home():
    return {"status": "Service Desk rodando no Render 🚀"}


# -------------------------------
# ✅ MODELOS (Pydantic)
# -------------------------------

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str


class LoginData(BaseModel):
    email: str
    senha: str


class ChamadoCreate(BaseModel):
    descricao: str
    prioridade: str
    usuario_id: int


class ComentarioData(BaseModel):
    texto: str


# -------------------------------
# ✅ USUÁRIOS
# -------------------------------

@app.post("/usuarios")
def registrar_usuario(dados: UsuarioCreate):

    existente = buscar_usuario_por_email(dados.email)
    if existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hash = bcrypt.hash(dados.senha)

    criar_usuario(dados.nome, dados.email, senha_hash)

    return {"msg": "Usuário criado com sucesso"}


@app.post("/login")
def login(dados: LoginData):

    usuario = buscar_usuario_por_email(dados.email)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not bcrypt.verify(dados.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=401, detail="Senha inválida")

    return {"msg": "Login OK", "usuario_id": usuario["id"]}


# -------------------------------
# ✅ CHAMADOS
# -------------------------------

@app.post("/chamados")
def criar_chamado(dados: ChamadoCreate):

    chamado_id = abrir_chamado(
        descricao=dados.descricao,
        prioridade=dados.prioridade,
        usuario_id=dados.usuario_id
    )

    return {"msg": "Chamado criado", "id": chamado_id}


@app.get("/chamados/{id_chamado}")
def get_chamado(id_chamado: int):

    chamado = consultar_chamado(id_chamado)

    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    return chamado


@app.post("/chamados/{id_chamado}/comentario")
def comentar(id_chamado: int, dados: ComentarioData):

    ok = adicionar_comentario_chamado(id_chamado, dados.texto)

    if not ok:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    return {"msg": "Comentário adicionado"}


@app.post("/chamados/{id_chamado}/fechar")
def encerrar(id_chamado: int):

    ok, msg = fechar_chamado(id_chamado)

    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {"msg": msg}
