import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from .models import Role, SituacaoPrazo, StatusAtividade


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: Role = Role.COLABORADOR


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: EmailStr
    role: Role
    ativo: bool


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    nome: str


class AtividadeCreate(BaseModel):
    descricao: str
    local: Optional[str] = None
    data_inicio_prevista: Optional[datetime.date] = None
    data_fim_prevista: Optional[datetime.date] = None
    previsao_horas: Optional[Decimal] = Decimal("0")
    colaborador_id: Optional[int] = None
    status: StatusAtividade = StatusAtividade.A_PROGRAMAR


class AtividadeUpdateGestor(BaseModel):
    descricao: Optional[str] = None
    local: Optional[str] = None
    data_inicio_prevista: Optional[datetime.date] = None
    data_fim_prevista: Optional[datetime.date] = None
    previsao_horas: Optional[Decimal] = None
    situacao_prazo: Optional[SituacaoPrazo] = None
    status: Optional[StatusAtividade] = None
    colaborador_id: Optional[int] = None


class AtividadeUpdateColaborador(BaseModel):
    status: StatusAtividade


class AtividadeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    descricao: str
    local: Optional[str] = None
    data_inicio_prevista: Optional[datetime.date] = None
    data_fim_prevista: Optional[datetime.date] = None
    previsao_horas: Optional[Decimal] = None
    situacao_prazo: SituacaoPrazo
    status: StatusAtividade
    colaborador_id: Optional[int] = None


class ObservacaoCreate(BaseModel):
    texto: str


class ObservacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    texto: str
    usuario_id: int
    criado_em: datetime.datetime
