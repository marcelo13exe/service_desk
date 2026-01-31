from fastapi import (
    FastAPI,
    Request,
    Form,
    HTTPException,
    Depends
)

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


from pydantic import BaseModel
from passlib.hash import bcrypt

# ✅ Services
from services_layer import (
    abrir_chamado,
    consultar_chamado,
    listar_meus_chamados,
    login_usuario
)

# ✅ Storage
from storage import (
    criar_usuario,
    buscar_usuario_por_email
)

# ✅ Segurança
from security import get_usuario_logado

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
# ✅ HOME
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
# ✅ LOGIN HTML
# -------------------------------
@app.get("/login", response_class=HTMLResponse)
def tela_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login-web")
def login_web(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...)
):
    token = login_usuario(email, senha)

    if not token:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "erro": "Email ou senha inválidos"
            }
        )

    response = RedirectResponse("/meus-chamados", status_code=302)
    response.set_cookie("token", token)
    return response


# -------------------------------
# ✅ MEUS CHAMADOS (PROTEGIDO)
# -------------------------------
@app.get("/meus-chamados", response_class=HTMLResponse)
def meus_chamados(
    request: Request,
    usuario_id: int = Depends(get_usuario_logado)
):
    chamados = listar_meus_chamados(usuario_id)

    return templates.TemplateResponse(
        "meus_chamados.html",
        {
            "request": request,
            "chamados": chamados
        }
    )


# -------------------------------
# ✅ ABRIR CHAMADO (PROTEGIDO)
# -------------------------------
@app.get("/abrir", response_class=HTMLResponse)
def tela_abrir(request: Request):
    return templates.TemplateResponse("abrir_chamado.html", {"request": request})


@app.post("/abrir", response_class=HTMLResponse)
def abrir(
    request: Request,
    descricao: str = Form(...),
    prioridade: str = Form(...),
    usuario_id: int = Depends(get_usuario_logado)
):
    chamado_id = abrir_chamado(descricao, prioridade, usuario_id)

    return templates.TemplateResponse(
        "abrir_chamado.html",
        {
            "request": request,
            "msg": f"Chamado aberto com sucesso! ID: {chamado_id}"
        }
    )


# -------------------------------
# ✅ CONSULTAR CHAMADO
# -------------------------------
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
        {
            "request": request,
            "chamado": chamado
        }
    )
