# Programação de Atividades SM&A — Dashboard

Painel de acompanhamento das atividades da equipe de Alta Tensão (Cardozo
Engenharia / AngloGold), gerado a partir da planilha `ProgramaçãoSMA.xlsx`.
É um único arquivo HTML autocontido (HTML + CSS + JS + dados embutidos).
O link público (GitHub Pages) é só leitura, sem servidor. Para a equipe
concluir atividades, justificar pendências e cadastrar tarefas direto
pelo painel — escrevendo na hora na própria planilha — existe também um
modinho local opcional (aba "Colaborador", ver seção própria abaixo).

## Estrutura

```
sma-dashboard/
├── template.html           # layout, estilos e lógica do painel (com dois
│                            # placeholders: __DATA_JSON__ e __LION_B64__;
│                            # tem a aba "Painel" e a aba "Colaborador")
├── build_dashboard.py       # lê a planilha .xlsx e gera o HTML final
├── atualizar_painel.bat     # script de um clique: gera + commita + envia
├── update_and_publish.py    # lógica usada pelo .bat acima (tem o XLSX_PATH)
├── colaborador_server.py    # servidor local da aba "Colaborador"
├── abrir_colaborador.bat    # script de um clique para abrir a aba Colaborador
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

- KPIs (total de atividades, programadas, a programar, atrasadas,
  concluídas, horas previstas, % concluído).
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

## Sem servidor, sem instalação para quem só vai usar

Quem só precisa **ver** o painel acessa o link do GitHub Pages acima.
O `build_dashboard.py` é só para quem **atualiza os dados**.

## Aba "Colaborador" — concluir, justificar e cadastrar atividades

Além de ver o painel, quem faz parte da equipe pode:

- marcar as próprias atividades como concluídas;
- justificar por que uma atividade não foi concluída no prazo;
- cadastrar uma atividade nova.

Cada ação grava **na hora** na própria planilha `ProgramaçãoSMA.xlsx` e
atualiza o painel na tela, sem precisar rodar o `atualizar_painel.bat`
para ver o resultado (esse script continua sendo o passo separado e
deliberado para levar a versão mais recente para o **link público**).

### Como usar

1. Dê duplo clique em **`abrir_colaborador.bat`**, na raiz do repositório.
2. O navegador abre sozinho em `http://localhost:5678`.
3. Clique na aba **Colaborador**, digite seu nome no campo "Meu nome"
   (é só para filtrar a visualização — ver aviso de segurança abaixo) e
   use os botões **Concluir** / **Justificar** em cada atividade, ou o
   formulário para adicionar uma nova.
4. Deixe a janela do `.bat` aberta enquanto estiver usando. Feche-a (ou
   Ctrl+C) quando terminar.

A aba Colaborador só funciona nesse modo local — pelo link público do
GitHub Pages ela aparece só com um aviso, porque ali não tem servidor
para gravar nada.

### Como a planilha é organizada por baixo

- A planilha ganha (ou já precisa ter) duas colunas: **RESPONSÁVEL**
  (de quem é a atividade) e **JUSTIFICATIVA** (preenchida quando alguém
  usa o botão Justificar). Se ainda não existirem, `colaborador_server.py`
  as cria sozinho na primeira vez que alguém usa a função correspondente.
- Uma atividade nova ganha o próximo N° disponível e status "A programar".
- Concluir uma atividade escreve "concluído" em STATUS (e "Concluído" em
  SITUAÇÃO DO PRAZO, se essa célula não for uma fórmula).
- Toda escrita é protegida por um lock em memória no servidor, para duas
  ações quase simultâneas não corromperem o arquivo.

### Sobre segurança

**Não tem login.** Qualquer pessoa com acesso a esse endereço local
(`http://localhost:5678`) pode editar qualquer atividade — o campo "Meu
nome" é só um filtro de visualização, não uma trava de acesso. Isso foi
uma escolha deliberada para manter o projeto simples (sem banco de
dados, sem senha para gerenciar); se isso deixar de ser suficiente para
o time, dá para evoluir depois.
