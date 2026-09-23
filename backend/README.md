# Backend — Dashboard SM&A (API + MySQL)

API que substitui o modelo "planilha = banco de dados" por um MySQL de
verdade, com login, papéis (`GESTOR` / `COLABORADOR`) e a planilha
existente funcionando como fonte de importação inicial/periódica — nunca
mais como arquivo editado ao vivo por várias pessoas. Ver
`../ARQUITETURA_DASHBOARD_WEB.md` para o desenho completo e a justificativa
dessa decisão.

Isto é adicional ao painel estático que já existe neste repositório
(`build_dashboard.py` → `docs/index.html` → GitHub Pages). Aquele fluxo
continua funcionando exatamente como hoje; este backend é o próximo passo,
para quem precisa de login, papéis e edição pela web.

## Rodando localmente

1. Suba o MySQL (requer Docker):
   ```bash
   docker compose up -d
   ```
2. Copie `.env.example` para `.env` e ajuste `EXCEL_IMPORT_PATH` para o
   caminho real da planilha na máquina onde a API vai rodar.
3. Crie o ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Crie o primeiro gestor (lê `.env` automaticamente):
   ```bash
   python create_admin.py "Seu Nome" seu.email@empresa.com "senha-forte"
   ```
5. Suba a API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Documentação interativa (Swagger) em `http://localhost:8000/docs`.
6. Faça login como gestor e chame `POST /api/sync/importar-excel` para
   trazer as atividades da planilha atual para o MySQL.

## Estrutura

- `app/models.py` — tabelas MySQL (`usuarios`, `atividades`, `observacoes`).
- `app/security.py` — hash de senha (bcrypt) e emissão/validação de JWT.
- `app/routers/` — rotas REST por área (`auth`, `usuarios`, `atividades`, `sync`).
- `app/services/excel_import.py` — leitura da planilha protegida por
  file lock + gravação transacional no MySQL (upsert por `N°` da planilha).
- `create_admin.py` — bootstrap do primeiro usuário GESTOR.

## O que este exemplo não cobre (fora do escopo desta entrega)

- Hospedagem em produção (Render/Railway/VPS/Azure — a decidir).
- Refresh token / logout com blacklist server-side.
- Testes automatizados.
- Exportação MySQL → Excel (mencionada como possibilidade no documento de
  arquitetura, não implementada aqui).
