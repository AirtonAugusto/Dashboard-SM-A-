from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import LoginRequest, TokenResponse, UsuarioOut
from ..security import criar_access_token, get_current_user, verificar_senha

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not usuario.ativo or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos.")

    token = criar_access_token(usuario)
    return TokenResponse(access_token=token, role=usuario.role, nome=usuario.nome)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario
