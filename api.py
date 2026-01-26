from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from database import init_db
from models import ChamadoCreate, ComentarioCreate
from services import (
    registrar_usuario,
    login_usuario,
    abrir_chamado,
    consultar_chamado,
    fechar_chamado,
    adicionar_comentario_chamado,
    listar_meus_chamados
)
from security import get_usuario_logado
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi import Form
from fastapi.staticfiles import StaticFiles



app = FastAPI()



templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# ========= MODELS =========
class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str


class Login(BaseModel):
    email: str
    senha: str


# ========= AUTH =========
@app.post("/register")
def register(dados: UsuarioCreate):
    registrar_usuario(dados.nome, dados.email, dados.senha)
    return {"mensagem": "Usuário criado com sucesso"}


@app.post("/login")
def login(dados: Login):
    token = login_usuario(dados.email, dados.senha)

    if not token:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    return {"access_token": token, "token_type": "bearer"}

@app.get("/login")
def tela_login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


# ========= STARTUP =========
@app.on_event("startup")
def startup():
    init_db()


# ========= CHAMADOS (PROTEGIDOS) =========
@app.post("/chamados")
def criar_chamado(
    dados: ChamadoCreate,
    usuario_id: int = Depends(get_usuario_logado)
):
    chamado_id = abrir_chamado(
        dados.descricao,
        dados.prioridade,
        usuario_id
    )

    return {
        "mensagem": "Chamado criado com sucesso",
        "id": chamado_id
    }


@app.get("//chamados")
def meus_chamados(usuario_id: int = Depends(get_usuario_logado)):
    return listar_meus_chamados(usuario_id)


@app.get("/chamados/{id_chamado}")
def consultar(
    id_chamado: int,
    usuario_id: int = Depends(get_usuario_logado)
):
    chamado = consultar_chamado(id_chamado)

    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    return chamado


@app.post("/chamados/{id_chamado}/fechar")
def fechar(
    id_chamado: int,
    usuario_id: int = Depends(get_usuario_logado)
):
    sucesso, msg = fechar_chamado(id_chamado, usuario_id)


    if not sucesso:
        raise HTTPException(status_code=403, detail=msg)


    return {"mensagem": msg}


@app.post("/chamados/{id_chamado}/comentario")
def adicionar_comentario(
    id_chamado: int,
    dados: ComentarioCreate,
    usuario_id: int = Depends(get_usuario_logado)
):
    sucesso = adicionar_comentario_chamado(
        id_chamado,
        dados.mensagem
    )

    if not sucesso:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    return {"mensagem": "Comentário adicionado com sucesso"}