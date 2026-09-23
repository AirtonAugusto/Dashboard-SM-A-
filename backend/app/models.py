import datetime
import enum

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class Role(str, enum.Enum):
    GESTOR = "GESTOR"
    COLABORADOR = "COLABORADOR"


class SituacaoPrazo(str, enum.Enum):
    NO_PRAZO = "No prazo"
    ATRASADO = "Atrasado"
    CONCLUIDO = "Concluído"


class StatusAtividade(str, enum.Enum):
    A_PROGRAMAR = "A programar"
    PROGRAMADO = "Programado"
    EM_ANDAMENTO = "Em andamento"
    CONCLUIDO = "Concluído"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(180), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.COLABORADOR)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.utcnow)

    atividades = relationship(
        "Atividade", back_populates="colaborador", foreign_keys="Atividade.colaborador_id"
    )


class Atividade(Base):
    __tablename__ = "atividades"
    __table_args__ = (UniqueConstraint("numero_planilha", name="uq_numero_planilha"),)

    id = Column(Integer, primary_key=True)
    # N° original da linha na planilha, quando a atividade veio de uma
    # importação — permite fazer "upsert" sem duplicar ao reimportar.
    numero_planilha = Column(String(20), nullable=True, index=True)

    descricao = Column(Text, nullable=False)
    local = Column(String(120))
    data_inicio_prevista = Column(Date)
    data_fim_prevista = Column(Date)
    previsao_horas = Column(Numeric(6, 2), default=0)
    situacao_prazo = Column(Enum(SituacaoPrazo), nullable=False, default=SituacaoPrazo.NO_PRAZO)
    status = Column(Enum(StatusAtividade), nullable=False, default=StatusAtividade.A_PROGRAMAR)

    colaborador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    # Nulo quando a atividade chegou por importação da planilha (não tem
    # um usuário humano como autor).
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    criado_em = Column(DateTime, default=datetime.datetime.utcnow)
    atualizado_em = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    colaborador = relationship("Usuario", back_populates="atividades", foreign_keys=[colaborador_id])
    observacoes = relationship("Observacao", back_populates="atividade", cascade="all, delete-orphan")


class Observacao(Base):
    __tablename__ = "observacoes"

    id = Column(Integer, primary_key=True)
    atividade_id = Column(Integer, ForeignKey("atividades.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    texto = Column(Text, nullable=False)
    criado_em = Column(DateTime, default=datetime.datetime.utcnow)

    atividade = relationship("Atividade", back_populates="observacoes")
    usuario = relationship("Usuario")
