"""
Cria o primeiro usuário GESTOR do sistema (bootstrap).

Uso:
    python create_admin.py "Nome do Gestor" gestor@empresa.com "senha-forte"

Depois disso, novos usuários (gestores ou colaboradores) são cadastrados
pela própria interface web, por um GESTOR já autenticado — não existe uma
tela pública de "criar minha conta" (ver ARQUITETURA_DASHBOARD_WEB.md,
seção de autenticação, para o motivo).
"""
import sys

from app.database import Base, SessionLocal, engine
from app.models import Role, Usuario
from app.security import hash_senha


def main():
    if len(sys.argv) != 4:
        sys.exit("Uso: python create_admin.py <nome> <email> <senha>")

    nome, email, senha = sys.argv[1:4]

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Usuario).filter(Usuario.email == email).first():
            sys.exit(f"Já existe um usuário com o e-mail {email}.")

        usuario = Usuario(nome=nome, email=email, senha_hash=hash_senha(senha), role=Role.GESTOR)
        db.add(usuario)
        db.commit()
        print(f"Gestor '{nome}' criado com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
