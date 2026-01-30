from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


from pydantic import BaseModel

from passlib.hash import bcrypt

# ✅ Services
from services_layer import (
    abrir_chamado,
    consultar_chamado,
    adicionar_comentario_chamado,
    fechar_chamado
)

# ✅ Storage
from storage import (
    criar_usuario,
    buscar_usuario_por_email
)

# ✅ Database
from database import init_db


# -------------------------------
# 🚀 APP
# -------------------------------
app = FastAPI(title="Service Desk Web")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup():
    init_db()


# -------------------------------
# ✅ HOME HTML
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def tela_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login_web(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...)
):
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "erro": "Usuário não encontrado"}
        )

    if not bcrypt.verify(senha, usuario["senha_hash"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "erro": "Senha inválida"}
        )

    # ✅ Login OK → Redireciona para home
    response = RedirectResponse("/", status_code=302)
    response.set_cookie("usuario_id", str(usuario["id"]))
    return response


# -------------------------------
# ✅ ROTAS HTML
# -------------------------------

@app.get("/abrir", response_class=HTMLResponse)
def tela_abrir(request: Request):
    return templates.TemplateResponse("abrir_chamado.html", {"request": request})


@app.post("/abrir", response_class=HTMLResponse)
def abrir(
    request: Request,
    descricao: str = Form(...),
    prioridade: str = Form(...),
    usuario_id: int = Form(...)
):
    chamado_id = abrir_chamado(descricao, prioridade, usuario_id)

    return templates.TemplateResponse(
        "abrir_chamado.html",
        {
            "request": request,
            "msg": f"Chamado aberto com sucesso! ID: {chamado_id}"
        }
    )


@app.get("/consultar", response_class=HTMLResponse)
def tela_consultar(request: Request):
    return templates.TemplateResponse("consultar.html", {"request": request})


@app.post("/consultar", response_class=HTMLResponse)
def consultar(
    request: Request,
    id_chamado: int = Form(...)
):
    chamado = consultar_chamado(id_chamado)

    return templates.TemplateResponse(
        "consultar.html",
        {"request": request, "chamado": chamado}
    )


# -------------------------------
# ✅ MODELOS JSON (API)
# -------------------------------

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str


class LoginData(BaseModel):
    email: str
    senha: str


# -------------------------------
# ✅ API USUÁRIOS
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
