from pydantic import BaseModel
from typing import Literal


class ChamadoCreate(BaseModel):
    descricao: str
    prioridade: Literal["Baixa", "Média", "Alta", "Crítica"]


class ComentarioCreate(BaseModel):
    mensagem: str
    
    
class Chamado:
 def __init__(self, titulo, descricao, status="aberto", prioridade="normal", id=None):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.status = status
        self.prioridade = prioridade