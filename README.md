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
└── dist/
    └── dashboard.html      # painel gerado (não versionado por padrão — veja .gitignore)
```

## Como atualizar o painel com uma planilha nova

Sempre que a `ProgramaçãoSMA.xlsx` for atualizada, rode:

```bash
pip install -r requirements.txt   # só na primeira vez
python build_dashboard.py --xlsx "/caminho/para/ProgramaçãoSMA.xlsx"
```

Isso gera (ou substitui) `dist/dashboard.html` com os dados mais recentes.
Basta abrir esse arquivo no navegador, ou publicá-lo onde preferir (GitHub
Pages, um servidor interno, etc.).

Parâmetros opcionais:

| Parâmetro | Padrão | Para quê |
| --- | --- | --- |
| `--logo` | `assets/logo_anglogold.png` | Trocar a logo da barra lateral |
| `--template` | `template.html` | Usar outro template/layout |
| `--out` | `dist/dashboard.html` | Onde salvar o HTML gerado |
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

Quem só precisa **ver** o painel não roda nada — recebe o
`dist/dashboard.html` (por e-mail, rede interna, ou publicado no GitHub
Pages) e abre no navegador. O `build_dashboard.py` é só para quem
**atualiza os dados**.
