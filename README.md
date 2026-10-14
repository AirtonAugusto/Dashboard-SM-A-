# Programação de Atividades SM&A — Dashboard

Painel de acompanhamento das atividades da equipe de Alta Tensão (Cardozo
Engenharia / AngloGold), gerado a partir da planilha `ProgramaçãoSMA.xlsx`.
É um único arquivo HTML autocontido (HTML + CSS + JS + dados embutidos),
sem backend nem banco de dados — abre em qualquer navegador. O link
público (GitHub Pages) é só leitura.

## Estrutura

```
sma-dashboard/
├── template.html          # layout, estilos e lógica do painel (com
│                           # placeholders: __DATA_JSON__, __LION_B64__)
├── build_dashboard.py      # lê a planilha .xlsx e gera o HTML final
├── local_config.py         # XLSX_PATH — o único lugar onde o caminho da
│                           # planilha é definido (usado pelo script abaixo)
├── atualizar_painel.bat    # 1 clique: gera + commita + envia pro GitHub
├── update_and_publish.py   # lógica usada pelo .bat acima
├── requirements.txt
├── assets/
│   └── logo_anglogold.png # logo usada na barra lateral
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

### Opção 1 — script de um clique (recomendado)

Sempre que salvar a planilha atualizada no caminho de sempre, dê duplo
clique em **`atualizar_painel.bat`**, dentro desta pasta. Ele sozinho:

1. gera o `docs/index.html` a partir da planilha mais recente;
2. commita a mudança;
3. envia (`git push`) para o GitHub.

Em 1–2 minutos o link público já reflete os dados novos. Se a planilha
mudar de nome ou de pasta, o script tenta detectar sozinho um arquivo
parecido na mesma pasta (`local_config.py`); se não conseguir, abra esse
arquivo e ajuste a linha `XLSX_PATH` para o novo caminho.

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

O painel tem duas abas:

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
  "Atividade" funciona como um slicer do Power BI: mostra só categorias
  gerais (ex: "Fibra", "Retrofit"), e marcar uma traz todas as
  atividades daquela categoria. O que não cai em nenhuma categoria vai
  para "Outras". Para adicionar uma categoria nova, edite o objeto
  `CATEGORIAS` no `<script>` de `template.html`.
- Botão Claro/Escuro no topo (sem escolha, segue o tema do aparelho).

### Calendário (3 semanas)

Grade com as três próximas semanas (segunda a sexta), **calculada
automaticamente a partir da data de hoje** — não depende de nenhum botão
"Reprogramar" na planilha. Uma atividade de vários dias aparece em todos
os dias do intervalo em que está em andamento, não só no dia de início.
Clicar num dia mostra a lista de atividades daquele dia, com descrição,
horas e subestação (local).

## Sem servidor, sem instalação para quem só vai usar

Quem só precisa **ver** o painel acessa o link do GitHub Pages acima.
O `build_dashboard.py` é só para quem **atualiza os dados** a partir da
planilha Excel — o painel em si não grava nada, é só leitura.

Os informes diários dos colaboradores (conclusão de atividades,
justificativas, atividades novas ou extras) passaram a ser feitos por
formulário do Google (um por equipe), fora deste painel.
