"""
Sobe o backend + frontend localmente para TESTAR a interface, sem precisar
instalar MySQL nem Docker. Usa um banco SQLite temporário
(backend/teste_local.db) só para esta finalidade — não é o banco de
produção (esse é o MySQL, ver ../ARQUITETURA_DASHBOARD_WEB.md).

Chamado por testar_dashboard_web.bat (na raiz do repositório) — normalmente
você não precisa rodar este arquivo diretamente, só dar duplo clique no
.bat.
"""
import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend-example"
DB_PATH = BACKEND_DIR / "teste_local.db"

GESTOR_EMAIL = "teste@sma.com"
COLABORADOR_EMAIL = "colaborador@sma.com"
SENHA = "teste123"


def preparar_banco():
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
    os.environ.setdefault("JWT_SECRET_KEY", "chave-so-para-teste-local")

    sys.path.insert(0, str(BACKEND_DIR))
    from app.database import Base, SessionLocal, engine
    from app.models import Atividade, Role, SituacaoPrazo, StatusAtividade, Usuario
    from app.security import hash_senha

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Usuario).filter(Usuario.email == GESTOR_EMAIL).first():
            return  # já rodou antes, não recria

        gestor = Usuario(nome="Gestor de Teste", email=GESTOR_EMAIL,
                          senha_hash=hash_senha(SENHA), role=Role.GESTOR)
        colaborador = Usuario(nome="Colaborador de Teste", email=COLABORADOR_EMAIL,
                               senha_hash=hash_senha(SENHA), role=Role.COLABORADOR)
        db.add_all([gestor, colaborador])
        db.commit()
        db.refresh(colaborador)
        db.refresh(gestor)

        db.add(Atividade(
            descricao="Atividade de exemplo (pode editar ou apagar à vontade)",
            local="SE-01", previsao_horas=4,
            situacao_prazo=SituacaoPrazo.NO_PRAZO, status=StatusAtividade.A_PROGRAMAR,
            colaborador_id=colaborador.id, criado_por_id=gestor.id,
        ))
        db.commit()
        print("Banco de teste criado com um gestor, um colaborador e uma atividade de exemplo.")
    finally:
        db.close()


def main():
    preparar_banco()

    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
    env.setdefault("JWT_SECRET_KEY", "chave-so-para-teste-local")

    def _encerrar(signum, frame):
        raise SystemExit(0)

    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _encerrar)

    # A criação dos subprocessos também fica dentro do try: uma
    # interrupção a qualquer momento depois que "api" existe (não só
    # enquanto bloqueado em api.wait()) precisa passar pelo finally e
    # encerrar os dois processos. Deixar algo sensível a interrupção fora
    # do try é o jeito clássico de vazar subprocesso órfão.
    api = frontend = None
    try:
        api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
            cwd=BACKEND_DIR, env=env,
        )
        frontend = subprocess.Popen(
            [sys.executable, "-m", "http.server", "5500"], cwd=FRONTEND_DIR,
        )

        time.sleep(2)
        print("\n" + "=" * 60)
        print("Painel de teste no ar!")
        print("=" * 60)
        print(f"Gestor:      {GESTOR_EMAIL} / {SENHA}")
        print(f"Colaborador: {COLABORADOR_EMAIL} / {SENHA}")
        print("\nAbrindo o navegador. Se não abrir sozinho, acesse:")
        print("  http://localhost:5500/login.html")
        print("\nDeixe esta janela aberta enquanto estiver testando.")
        print("Feche a janela (ou Ctrl+C) para encerrar.\n")
        webbrowser.open("http://localhost:5500/login.html")

        api.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        if api:
            api.terminate()
            api.wait(timeout=5)
        if frontend:
            frontend.terminate()
            frontend.wait(timeout=5)


if __name__ == "__main__":
    main()
