from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import atividades, auth, sync, usuarios

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dashboard SM&A — API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restrinja ao(s) domínio(s) do frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(atividades.router)
app.include_router(sync.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
