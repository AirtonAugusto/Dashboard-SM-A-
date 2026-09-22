# Programação de Atividades SM&A — Dashboard

Painel de acompanhamento das atividades da equipe de Alta Tensão (Cardozo
Engenharia / AngloGold), gerado a partir da planilha `ProgramaçãoSMA.xlsx`.
É um único arquivo HTML autocontido (HTML + CSS + JS + dados embutidos),
sem backend nem banco de dados — abre em qualquer navegador.

## Estrutura

```
sma-dashboard/
├── template.html          # layout, estilos e lógica do painel (com dois
│                           # placeholders: __DATA_JSON__ e __LION_B64__)
├── build_dashboard.py      # lê a planilha .xlsx e gera o HTML final
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

Sempre que a `ProgramaçãoSMA.xlsx` for atualizada, rode:

```bash
pip install -r requirements.txt   # só na primeira vez
python build_dashboard.py --xlsx "/caminho/para/ProgramaçãoSMA.xlsx"
```

Isso sobrescreve `docs/index.html` com os dados mais recentes. Para o
link público refletir a mudança, é preciso commitar e subir:

```bash
git add docs/index.html
git commit -m "Atualiza painel com nova planilha"
git push
```

(sem esse commit/push, o arquivo muda só na sua máquina — o link
público continua mostrando a versão anterior.)

Parâmetros opcionais:

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
- Atividades por local (gráfico, respeita os filtros).
- Tipo de atividade da semana e Atividades da semana (segunda a sexta) —
  esses dois **sempre mostram a semana corrente**, calculada a partir da
  data real de quem está com o painel aberto, e não são afetados pelos
  filtros da barra lateral.
- Tabela de atividades com observações/pendências (respeita os filtros).
- Filtros de período, local, situação do prazo e atividade.

## Sem servidor, sem instalação para quem só vai usar

Quem só precisa **ver** o painel acessa o link do GitHub Pages acima.
O `build_dashboard.py` é só para quem **atualiza os dados**.
