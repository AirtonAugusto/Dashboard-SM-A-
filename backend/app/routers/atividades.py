from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Atividade, Observacao, Role, Usuario
from ..schemas import (
    AtividadeCreate, AtividadeOut, AtividadeUpdateColaborador, AtividadeUpdateGestor,
    ObservacaoCreate, ObservacaoOut,
)
from ..security import exigir_role, get_current_user

router = APIRouter(prefix="/api/atividades", tags=["atividades"])


def _buscar_ou_404(db: Session, atividade_id: int) -> Atividade:
    atividade = db.get(Atividade, atividade_id)
    if not atividade:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada.")
    return atividade


def _garantir_dono_se_colaborador(usuario: Usuario, atividade: Atividade) -> None:
    if usuario.role == Role.COLABORADOR and atividade.colaborador_id != usuario.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Esta atividade não é sua.")


@router.get("", response_model=list[AtividadeOut])
def listar_atividades(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # Regra central do controle de acesso: o colaborador só enxerga as
    # próprias tarefas, o filtro é aplicado aqui no servidor (nunca confie
    # em um filtro só no frontend).
    query = db.query(Atividade)
    if usuario.role == Role.COLABORADOR:
        query = query.filter(Atividade.colaborador_id == usuario.id)
    return query.order_by(Atividade.data_fim_prevista).all()


@router.post(
    "", response_model=AtividadeOut, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_role(Role.GESTOR))],
)
def criar_atividade(
    dados: AtividadeCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)
):
    atividade = Atividade(**dados.model_dump(), criado_por_id=usuario.id)
    db.add(atividade)
    db.commit()
    db.refresh(atividade)
    return atividade


@router.patch("/{atividade_id}", response_model=AtividadeOut)
def atualizar_atividade(
    atividade_id: int, dados: dict,
    usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db),
):
    atividade = _buscar_ou_404(db, atividade_id)
    _garantir_dono_se_colaborador(usuario, atividade)

    schema = AtividadeUpdateGestor if usuario.role == Role.GESTOR else AtividadeUpdateColaborador
    try:
        # Modelo construído manualmente (não via injeção do FastAPI), então
        # o erro de validação precisa ser convertido à mão em 422 — senão
        # vira um 500 não tratado.
        campos = schema(**dados)
    except ValidationError as exc:
        raise HTTPException(422, exc.errors()) from exc

    for campo, valor in campos.model_dump(exclude_unset=True).items():
        setattr(atividade, campo, valor)

    db.commit()
    db.refresh(atividade)
    return atividade


@router.delete(
    "/{atividade_id}", status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exigir_role(Role.GESTOR))],
)
def excluir_atividade(atividade_id: int, db: Session = Depends(get_db)):
    atividade = _buscar_ou_404(db, atividade_id)
    db.delete(atividade)
    db.commit()


@router.get("/{atividade_id}/observacoes", response_model=list[ObservacaoOut])
def listar_observacoes(
    atividade_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)
):
    atividade = _buscar_ou_404(db, atividade_id)
    _garantir_dono_se_colaborador(usuario, atividade)
    return atividade.observacoes


@router.post(
    "/{atividade_id}/observacoes", response_model=ObservacaoOut, status_code=status.HTTP_201_CREATED
)
def criar_observacao(
    atividade_id: int, dados: ObservacaoCreate,
    usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db),
):
    atividade = _buscar_ou_404(db, atividade_id)
    _garantir_dono_se_colaborador(usuario, atividade)

    observacao = Observacao(atividade_id=atividade_id, usuario_id=usuario.id, texto=dados.texto)
    db.add(observacao)
    db.commit()
    db.refresh(observacao)
    return observacao
