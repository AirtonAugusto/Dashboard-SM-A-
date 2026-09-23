from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Role, Usuario
from ..schemas import UsuarioCreate, UsuarioOut
from ..security import exigir_role, hash_senha

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioOut], dependencies=[Depends(exigir_role(Role.GESTOR))])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).order_by(Usuario.nome).all()


@router.post(
    "", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_role(Role.GESTOR))],
)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um usuário com este e-mail.")

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        role=dados.role,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch(
    "/{usuario_id}/desativar", response_model=UsuarioOut,
    dependencies=[Depends(exigir_role(Role.GESTOR))],
)
def desativar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado.")
    usuario.ativo = False
    db.commit()
    db.refresh(usuario)
    return usuario
