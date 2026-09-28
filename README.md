# Programação de Atividades SM&A — Dashboard

Painel de acompanhamento das atividades da equipe de Alta Tensão (Cardozo
Engenharia / AngloGold), gerado a partir da planilha `ProgramaçãoSMA.xlsx`.
É um único arquivo HTML autocontido (HTML + CSS + JS + dados embutidos),
sem backend nem banco de dados — abre em qualquer navegador. O link
público (GitHub Pages) é só leitura.

## Estrutura

```
sma-dashboard/
├── template.html               # layout, estilos e lógica do painel (com
│                                # placeholders: __DATA_JSON__, __LION_B64__,
│                                # __SHEETS_API_URL__)
├── build_dashboard.py           # lê a planilha .xlsx e gera o HTML final
├── local_config.py              # XLSX_PATH — o único lugar onde o caminho
│                                 # da planilha é definido (usado pelos dois
│                                 # scripts .py abaixo)
├── sheets_config.json           # URL do Web App do Google Apps Script
│                                 # (banco de dados das ações do colaborador)
├── atualizar_painel.bat         # 1 clique: gera + commita + envia pro GitHub
├── update_and_publish.py        # lógica usada pelo .bat acima
├── atualizar_do_colaborador.bat # 1 clique: traz do Google Sheets pro Excel
│                                 # e já atualiza/publica o painel em seguida
├── sync_sheets_to_excel.py      # lógica usada pelo .bat acima
├── apps-script/
│   └── Code.gs                 # backend (Google Apps Script) — cole isso
│                                 # dentro da planilha Google, veja mais abaixo
├── requirements.txt
├── assets/
│   └── logo_anglogold.png      # logo usada na barra lateral
└── docs/
    └── index.html              # painel gerado — É este arquivo que o GitHub
                                 # Pages publica no link público (versionado)
```

## Link público (GitHub Pages)

O painel fica disponível em:

**https://airtonaugusto.github.io/Dashboard-SM-A-/**

Esse link é gerado automaticamente pelo GitHub a partir do arquivo
`docs/index.html` sempre que ele é atualizado neste repositório (branch
`main`). Quem só precisa **ver** o painel usa esse link — não precisa
baixar nada, instalar nada, nem abrir arquivo local. Ele atualiza sozinho
de 1 a 2 minutos depois de cada `git push`.

Configuração feita uma única vez em Settings → Pages → Source: "Deploy
from a branch" → Branch: `main` / pasta `/docs`.

## Como atualizar o painel com uma planilha nova

### Opção 1 — script de um clique (recomendado)

Sempre que salvar a planilha atualizada no caminho de sempre, dê duplo
clique em **`atualizar_painel.bat`**, dentro desta pasta. Ele sozinho:

1. gera o `docs/index.html` a partir da planilha mais recente;
2. commita a mudança;
3. envia (`git push`) para o GitHub.

Em 1–2 minutos o link público já reflete os dados novos. Se a planilha
mudar de nome ou de pasta, abra `local_config.py` e ajuste a linha
`XLSX_PATH` para o novo caminho.

### Opção 2 — passo a passo manual

```bash
pip install -r requirements.txt   # só na primeira vez
python build_dashboard.py --xlsx "/caminho/para/ProgramaçãoSMA.xlsx"
git add docs/index.html
git commit -m "Atualiza painel com nova planilha"
git push
```

(sem o commit/push, o arquivo muda só na sua máquina — o link
público continua mostrando a versão anterior.)

Parâmetros opcionais do `build_dashboard.py`:

| Parâmetro | Padrão | Para quê |
| --- | --- | --- |
| `--logo` | `assets/logo_anglogold.png` | Trocar a logo da barra lateral |
| `--template` | `template.html` | Usar outro template/layout |
| `--out` | `docs/index.html` | Onde salvar o HTML gerado |
| `--aba-atividades` | `Atividades(SM&A)` | Nome da aba de atividades, se mudar na planilha |
| `--aba-carga` | `Carga Diária` | Nome da aba de carga diária, se mudar na planilha |

## O que o painel mostra

O painel tem três abas:

### Painel

- KPIs (total de atividades, programadas, a programar, atrasadas,
  concluídas, horas previstas).
- Atividades por local e Atividades por responsável (gráficos, respeitam
  os filtros).
- Tipo de atividade da semana e Atividades da semana (segunda a sexta) —
  esses dois **sempre mostram a semana corrente**, calculada a partir da
  data real de quem está com o painel aberto, e não são afetados pelos
  filtros da barra lateral.
- Tabelas de atividades concluídas, com observações/pendências e com
  justificativas (respeitam os filtros).
- Filtros de período, local, situação do prazo e atividade — o filtro
  "Atividade" tem tanto as descrições individuais quanto categorias
  gerais (ex: "Fibra", "Retrofit") que reúnem várias descrições
  parecidas no mesmo lugar; para adicionar uma categoria nova, edite o
  objeto `CATEGORIAS` no `<script>` de `template.html`.

### Calendário (3 semanas)

Grade com as três próximas semanas (segunda a sexta), **calculada
automaticamente a partir da data de hoje** — não depende de nenhum botão
"Reprogramar" na planilha. Clicar num dia mostra a lista de atividades
daquele dia, com descrição, horas e subestação (local).

### Ações do Colaborador

Onde o Thiago (ou qualquer colaborador) concluiu atividades, justifica
atrasos, adiciona uma atividade nova ao backlog (quando identifica uma
oportunidade) ou registra uma atividade extra já executada por
proatividade. Cada ação grava o nome de quem fez e a data. Isso só
funciona com o Google Sheets configurado (próxima seção) — sem ele, o
painel mostra um aviso e continua funcionando normalmente só para
leitura.

## Ações do colaborador — configurando o "banco de dados" (Google Sheets)

O painel publicado (GitHub Pages) é um arquivo estático — sozinho, ele não
tem onde gravar o que um colaborador faz. Por isso as ações do colaborador
usam uma planilha Google como banco de dados, através de um Web App feito
com Google Apps Script (gratuito, sem precisar de MySQL nem de login
próprio). O fluxo completo:

```
Colaborador (painel, de qualquer lugar) --> Google Sheets  --[um clique]-->  Excel real  --[um clique]-->  GitHub Pages
                                              (ações ficam                  (sync_sheets_   (atualizar_painel.bat,
                                               registradas aqui)             to_excel.py)     de sempre)
```

### Configuração (uma única vez)

1. Crie uma planilha nova em [sheets.google.com](https://sheets.google.com).
2. Nela, crie duas abas: **Atividades** e **Log**.
   - Na aba **Atividades**, a primeira linha (cabeçalho) deve ter exatamente
     estas colunas, nesta ordem: `id`, `desc`, `local`, `ini`, `fim`,
     `horas`, `situacao`, `status`, `obs`, `resp`, `justificativa`,
     `origem`, `dataExecucao`, `criadoEm`, `atualizadoEm`.
   - Na aba **Log**, cabeçalho: `Timestamp`, `Ação`, `ID`, `Responsável`,
     `Detalhe`.
   - Cole as atividades atuais nessa aba (pode copiar as colunas
     equivalentes direto do Excel — `id`=N°, `desc`=descrição, etc.).
3. No menu da planilha: **Extensões → Apps Script**.
4. Apague o conteúdo padrão e cole o conteúdo de `apps-script/Code.gs`
   deste repositório. Salve (ícone de disquete).
5. Clique em **Implantar → Nova implantação**. Tipo: **App da Web**.
   Em "Executar como": sua conta. Em "Quem pode acessar": **Qualquer pessoa**.
   Clique em Implantar e autorize o acesso quando pedido (é a sua própria
   planilha, então é seguro).
6. Copie a **URL do app da Web** gerada (termina em `/exec`).
7. Cole essa URL em `sheets_config.json`, no campo `sheets_api_url`, e rode
   `atualizar_painel.bat` de novo para publicar o painel já conectado.

### Uso do dia a dia

- O colaborador acessa o link público do painel, vai na aba **Ações do
  Colaborador**, digita o nome e usa os botões normalmente — tudo isso
  grava direto na planilha Google, de qualquer lugar, sem precisar tocar
  nesta pasta nem no Excel.
- Quando o PCM quiser trazer essas atualizações de volta para o Excel
  real (para os cálculos/relatórios que dependem dele), é só dar duplo
  clique em **`atualizar_do_colaborador.bat`** nesta pasta. Ele puxa tudo
  do Google Sheets, atualiza a planilha Excel (sem mexer em fórmulas) e já
  publica o painel atualizado no GitHub.
- Atividades adicionadas pelo colaborador (novas ou extras) ganham colunas
  novas automaticamente no Excel na primeira sincronização
  (`ORIGEM`, `DATA DE EXECUÇÃO`, `JUSTIFICATIVA`), sem apagar nada que já
  existia.

## Sem servidor, sem instalação para quem só vai usar

Quem só precisa **ver** o painel acessa o link do GitHub Pages acima.
O `build_dashboard.py` é só para quem **atualiza os dados**, e o Google
Sheets só entra em jogo se as ações do colaborador estiverem habilitadas.
