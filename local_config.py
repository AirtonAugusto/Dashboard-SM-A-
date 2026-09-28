# Configuração local desta máquina — não depende do resto do código.
#
# O nome/extensão da planilha já mudou várias vezes (espaço no nome, depois
# sem espaço, depois .xlsx virou .xlsm quando os macros de "Reprogramar"
# foram adicionados). Por isso, além do caminho mais recente conhecido,
# `resolver_xlsx_path()` procura sozinho na mesma pasta se esse nome exato
# não existir mais -- assim um próximo renome não quebra os scripts de novo.
#
# Tanto o update_and_publish.py quanto o sync_sheets_to_excel.py usam este
# arquivo, então corrigir aqui corrige os dois de uma vez (se um dia o
# auto-detect não achar nada, é só atualizar a linha XLSX_PATH abaixo).
import glob
import os

PASTA_PLANILHA = r"C:\Users\CARDOZO\Documents\Airton Augusto"
XLSX_PATH = os.path.join(PASTA_PLANILHA, "Programação(SM&A).xlsm")


def resolver_xlsx_path():
    """Caminho da planilha oficial. Se XLSX_PATH não existir mais (arquivo
    renomeado), procura na mesma pasta por algo como "Programação...SM&A....xlsx/.xlsm"
    e usa o modificado mais recentemente — ignorando os arquivos de trava do
    Excel (~$...) e o proprio PDF exportado."""
    if os.path.exists(XLSX_PATH):
        return XLSX_PATH

    padrao = os.path.join(PASTA_PLANILHA, "Programa*SM*A*.xls*")
    candidatos = [
        c for c in glob.glob(padrao)
        if not os.path.basename(c).startswith("~$")
    ]
    if not candidatos:
        return XLSX_PATH  # deixa o erro de "planilha não encontrada" de sempre acontecer

    mais_recente = max(candidatos, key=os.path.getmtime)
    if mais_recente != XLSX_PATH:
        print(f"Aviso: {os.path.basename(XLSX_PATH)} não foi encontrado; usando "
              f"{os.path.basename(mais_recente)} (arquivo mais recente parecido nesta pasta).")
        print("Se esse for o nome definitivo, atualize XLSX_PATH em local_config.py.")
    return mais_recente
