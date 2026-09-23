import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import Role, Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def criar_access_token(usuario: Usuario) -> str:
    expira = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(usuario.id), "role": usuario.role.value, "exp": expira}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        usuario_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise credenciais_invalidas

    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas
    return usuario


def exigir_role(*roles: Role):
    def checador(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não tem permissão para esta ação.")
        return usuario

    return checador
