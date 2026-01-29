from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "chave_super_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_senha(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha, senha_hash):
    return pwd_context.verify(senha, senha_hash)

def criar_token(dados: dict):
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados.update({"exp": expira})
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)

def get_usuario_logado(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = payload.get("sub")

        if usuario_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        return int(usuario_id)

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")