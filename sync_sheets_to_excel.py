#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traz para a planilha Excel real as atualizações feitas pelos colaboradores
no painel (que ficam guardadas no Google Sheets): atividades concluídas,
justificativas, atividades novas adicionadas ao backlog e atividades extras
registradas por proatividade.

Chamado pelo atualizar_do_colaborador.bat -- normalmente você não precisa
rodar este arquivo diretamente, só clicar duas vezes no .bat.

Não mexe em nenhuma fórmula existente na planilha: só escreve nas colunas
STATUS, SITUAÇÃO DO PRAZO, RESPONSÁVEL, JUSTIFICATIVA, ORIGEM e
DATA DE EXECUÇÃO (as três últimas são criadas automaticamente na primeira
vez que não existirem ainda) e só adiciona linhas novas no final para
atividades que nasceram no painel.

Pré-requisitos:
  1. sheets_config.json com a URL do Web App do Apps Script (veja README).
  2. A planilha Excel precisa estar FECHADA no Excel enquanto este script
     roda (senão o Windows bloqueia a escrita no arquivo).
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

import openpyxl

from local_config import XLSX_PATH

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(REPO_DIR, "sheets_config.json")
ABA_ATIVIDADES = "Atividades(SM&A)"

# Nome da coluna no Excel <- nome do campo vindo do Google Sheets.
# As três últimas colunas são criadas automaticamente se ainda não existirem.
MAPA_COLUNAS = {
    "RESPONSÁVEL": "resp",
    "STATUS": "status",
    "SITUAÇÃO DO PRAZO ": "situacao",
    "JUSTIFICATIVA": "justificativa",
    "ORIGEM": "origem",
    "DATA DE EXECUÇÃO": "dataExecucao",
}
COLUNAS_NOVAS_SE_FALTAR = ["JUSTIFICATIVA", "ORIGEM", "DATA DE EXECUÇÃO"]


def carregar_api_url():
    if not os.path.exists(CONFIG_PATH):
        sys.exit(
            "ERRO: não encontrei sheets_config.json nesta pasta.\n"
            'Crie um arquivo sheets_config.json com o conteúdo:\n'
            '  {"sheets_api_url": "https://script.google.com/macros/s/SEU_ID/exec"}\n'
            "(a URL é gerada quando você publica o Apps Script como Web App — veja o README)."
        )
    cfg = json.loads(Path(CONFIG_PATH).read_text(encoding="utf-8"))
    url = (cfg.get("sheets_api_url") or "").strip()
    if not url:
        sys.exit("ERRO: sheets_config.json existe mas o campo sheets_api_url está vazio.")
    return url


def buscar_atividades_do_sheets(api_url):
    with urllib.request.urlopen(api_url + "?action=listar", timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if not payload.get("ok"):
        sys.exit("ERRO ao ler o Google Sheets: " + str(payload.get("erro")))
    return payload.get("acts", [])


def verificar_planilha_fechada(xlsx_path):
    lock_path = os.path.join(os.path.dirname(xlsx_path), "~$" + os.path.basename(xlsx_path))
    if os.path.exists(lock_path):
        sys.exit(
            "ERRO: a planilha parece estar aberta no Excel agora\n"
            "(" + lock_path + " existe).\n"
            "Feche o arquivo e rode este script de novo."
        )


def garantir_colunas(ws, headers):
    """Cria no fim da planilha qualquer coluna de COLUNAS_NOVAS_SE_FALTAR que
    ainda não exista, sem tocar em nenhuma coluna/fórmula já existente."""
    proxima_col = len(headers) + 1
    criou_alguma = False
    for nome in COLUNAS_NOVAS_SE_FALTAR:
        if nome not in headers:
            ws.cell(row=1, column=proxima_col, value=nome)
            headers.append(nome)
            proxima_col += 1
            criou_alguma = True
    if criou_alguma:
        print("Colunas novas criadas na planilha: " +
              ", ".join(n for n in COLUNAS_NOVAS_SE_FALTAR if n in headers))
    return headers


def main():
    api_url = carregar_api_url()
    verificar_planilha_fechada(XLSX_PATH)

    print("Buscando atualizações no Google Sheets...")
    atividades_sheets = buscar_atividades_do_sheets(api_url)
    print(f"{len(atividades_sheets)} atividade(s) recebida(s) do Sheets.")

    wb = openpyxl.load_workbook(XLSX_PATH)  # sem data_only: preserva fórmulas
    if ABA_ATIVIDADES not in wb.sheetnames:
        sys.exit(f'ERRO: aba "{ABA_ATIVIDADES}" não encontrada na planilha.')
    ws = wb[ABA_ATIVIDADES]

    headers = [c.value for c in ws[1]]
    headers = garantir_colunas(ws, headers)
    col_idx = {h: i + 1 for i, h in enumerate(headers) if h}
    col_id = col_idx.get("N°")
    col_desc = col_idx.get("DESCRIÇÃO DAS ATIVIDADES")
    col_local = col_idx.get("LOCAL")
    col_ini = col_idx.get("DATA PREVISTA INICIO ")
    col_fim = col_idx.get("DATA PREVISTA CONCLUSÃO")
    col_horas = col_idx.get("PREVISÃO DE HORAS")
    col_obs = col_idx.get("OBSERVAÇÕES")
    if col_id is None:
        sys.exit('ERRO: não encontrei a coluna "N°" na planilha.')

    # mapeia N° -> linha, para as atividades que já existem no Excel
    linha_por_id = {}
    for r in range(2, ws.max_row + 1):
        v = ws.cell(row=r, column=col_id).value
        if v is not None:
            linha_por_id[str(v)] = r

    atualizadas = 0
    novas = 0
    proxima_linha_livre = ws.max_row + 1

    for a in atividades_sheets:
        aid = str(a.get("id"))
        if aid in linha_por_id:
            linha = linha_por_id[aid]
            for col_nome, campo in MAPA_COLUNAS.items():
                idx = col_idx.get(col_nome)
                if idx is None:
                    continue
                valor_novo = a.get(campo)
                if valor_novo in (None, ""):
                    continue
                valor_atual = ws.cell(row=linha, column=idx).value
                if str(valor_atual or "") != str(valor_novo):
                    ws.cell(row=linha, column=idx, value=valor_novo)
            atualizadas += 1
        else:
            # atividade nova (criada no painel: backlog ou extra/proatividade)
            linha = proxima_linha_livre
            proxima_linha_livre += 1
            if col_id: ws.cell(row=linha, column=col_id, value=a.get("id"))
            if col_desc: ws.cell(row=linha, column=col_desc, value=a.get("desc"))
            if col_local: ws.cell(row=linha, column=col_local, value=a.get("local"))
            if col_ini and a.get("ini"): ws.cell(row=linha, column=col_ini, value=a.get("ini"))
            if col_fim and a.get("fim"): ws.cell(row=linha, column=col_fim, value=a.get("fim"))
            if col_horas: ws.cell(row=linha, column=col_horas, value=a.get("horas") or 0)
            if col_obs and a.get("obs"): ws.cell(row=linha, column=col_obs, value=a.get("obs"))
            for col_nome, campo in MAPA_COLUNAS.items():
                idx = col_idx.get(col_nome)
                if idx is None:
                    continue
                valor = a.get(campo)
                if valor not in (None, ""):
                    ws.cell(row=linha, column=idx, value=valor)
            novas += 1

    if atualizadas == 0 and novas == 0:
        print("Nada novo para trazer da planilha do Google — já está tudo sincronizado.")
        return

    wb.save(XLSX_PATH)
    print(f"OK: {atualizadas} atividade(s) atualizada(s), {novas} atividade(s) nova(s) adicionada(s).")
    print("Planilha Excel salva com sucesso:")
    print("  " + XLSX_PATH)
    print()
    print("Agora rode atualizar_painel.bat para gerar o painel com esses dados e publicar no GitHub.")


if __name__ == "__main__":
    try:
        main()
    except PermissionError:
        sys.exit(
            "ERRO: não consegui salvar a planilha (sem permissão).\n"
            "Verifique se ela não está aberta no Excel e tente de novo."
        )
