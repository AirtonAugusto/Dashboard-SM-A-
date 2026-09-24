# Programação de Atividades SM&A — Dashboard

Painel de acompanhamento das atividades da equipe de Alta Tensão (Cardozo
Engenharia / AngloGold), gerado a partir da planilha `Programação (SM&A).xlsx`.
É um único arquivo HTML autocontido (HTML + CSS + JS + dados embutidos),
sem backend nem banco de dados — abre em qualquer navegador.

## Estrutura

```
sma-dashboard/
├── template.html          # layout, estilos e lógica do painel (com dois
│                           # placeholders: __DATA_JSON__ e __LION_B64__)
├── build_dashboard.py      # lê a planilha .xlsx e gera o HTML final
├── atualizar_painel.bat    # script de um clique: gera + commita + envia
├── update_and_publish.py   # lógica usada pelo .bat acima (tem o XLSX_PATH)
├── requirements.txt
├── assets/
│   └── logo_anglogold.png  # logo usada na barra lateral
└── docs/
    └── index.html          # painel gerado — É este arquivo que o GitHub
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

Isto é para quem **atualiza os dados** — quem só vai ver o painel usa o
link público acima, sem instalar nada.

### Opção 1 — script de um clique (recomendado)

Sempre que salvar a planilha atualizada no caminho de sempre, dê duplo
clique em **`atualizar_painel.bat`**, dentro desta pasta. Ele sozinho:

1. gera o `docs/index.html` a partir da planilha mais recente;
2. commita a mudança;
3. envia (`git push`) para o GitHub.

Em 1–2 minutos o link público já reflete os dados novos. Se a planilha
mudar de nome ou de pasta, abra `update_and_publish.py` e ajuste a linha
`XLSX_PATH` para o novo caminho.

### Opção 2 — passo a passo manual

```bash
pip install -r requirements.txt   # só na primeira vez
python build_dashboard.py --xlsx "/caminho/para/Programação (SM&A).xlsx"
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

- KPIs (total de atividades, programadas, a programar, atrasadas,
  concluídas, horas previstas).
- Atividades por local e Atividades por responsável (gráficos, respeitam
  os filtros; "Não atribuído" agrupa atividades sem responsável
  definido na planilha).
- Tipo de atividade da semana e Atividades da semana (segunda a sexta) —
  esses dois **sempre mostram a semana corrente**, calculada a partir da
  data real de quem está com o painel aberto, e não são afetados pelos
  filtros da barra lateral.
- Tabelas de atividades concluídas, com observações/pendências e com
  justificativas (respeitam os filtros). A coluna JUSTIFICATIVA (se
  existir na planilha) é o motivo de uma atividade não ter sido
  concluída no prazo.
- Filtros de período, local, situação do prazo e atividade — o filtro
  "Atividade" tem tanto as descrições individuais quanto categorias
  gerais (ex: "Fibra", "Retrofit") que reúnem várias descrições
  parecidas no mesmo lugar; para adicionar uma categoria nova, edite o
  objeto `CATEGORIAS` no `<script>` de `template.html`.
- Uma atividade sem nenhuma data prevista (nem início, nem fim) só
  aparece no filtro "Ver período completo" — nunca em uma semana
  específica, já que não haveria como saber a qual semana ela pertence.

## Sem servidor, sem instalação para quem só vai usar

Quem só precisa **ver** o painel acessa o link do GitHub Pages acima.
O `build_dashboard.py` é só para quem **atualiza os dados**.
