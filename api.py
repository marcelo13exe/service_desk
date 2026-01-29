from fastapi import FastAPI, HTTPException, Depends, Form
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import init_db
from models import ChamadoCreate, ComentarioCreate
from services_layer import (
    registrar_usuario,
    login_usuario,
    abrir_chamado,
    consultar_chamado,
    fechar_chamado,
    adicionar_comentario_chamado,
    listar_meus_chamados
)
from security import get_usuario_logado


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
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login-web")
def login_web(request: Request, email: str = Form(...), senha: str = Form(...)):
    token = login_usuario(email, senha)
    if not token:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "erro": "Email ou senha inválidos"}
        )

    response = RedirectResponse("/meus-chamados", status_code=302)
    response.set_cookie("token", token, httponly=True)
    return response


# ========= STARTUP =========
@app.on_event("startup")
def startup():
    init_db()


# ========= CHAMADOS =========
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


@app.get("/meus-chamados")
def meus_chamados(
    request: Request,
    usuario_id: int = Depends(get_usuario_logado)
):
    chamados = listar_meus_chamados(usuario_id)
    return templates.TemplateResponse(
        "meus_chamados.html",
        {"request": request, "chamados": chamados}
    )


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
    sucesso, msg = fechar_chamado(id_chamado)
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