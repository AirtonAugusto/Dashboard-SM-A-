#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza o painel (docs/index.html) a partir da planilha ProgramacaoSMA.xlsx
mais recente, e envia a mudanca para o GitHub (commit + push) automaticamente.

Chamado pelo atualizar_painel.bat -- normalmente voce nao precisa rodar este
arquivo diretamente, so clicar duas vezes no .bat depois de salvar a planilha
atualizada.

Se a planilha mudar de nome ou de pasta, so editar o caminho em XLSX_PATH
abaixo.
"""
import datetime
import os
import subprocess
import sys

# Caminho completo da planilha no seu computador.
XLSX_PATH = r"C:\Users\CARDOZO\Documents\Airton Augusto\Programação (SM&A).xlsx"

REPO_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    print("> " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=REPO_DIR)
    return result.returncode


def main():
    if not os.path.exists(XLSX_PATH):
        print("ERRO: não encontrei a planilha em:")
        print("  " + XLSX_PATH)
        print()
        print("Causas mais comuns:")
        print("  1. O OneDrive mudou o caminho da pasta Documentos sem avisar")
        print('     (ex: virou "C:\\Users\\CARDOZO\\OneDrive\\Documents\\..." em vez de')
        print('     "C:\\Users\\CARDOZO\\Documents\\...").')
        print("  2. O arquivo foi renomeado, movido, ou o nome tem um acento/caractere")
        print("     diferente do que está gravado aqui.")
        print()
        print("Como corrigir: no Explorador de Arquivos, clique com o botão direito na")
        print('planilha e escolha "Copiar como caminho"; depois abra update_and_publish.py')
        print("num editor de texto e cole esse caminho na linha XLSX_PATH (perto do topo).")
        sys.exit(1)

    print("=" * 60)
    print("Gerando painel a partir da planilha...")
    print("=" * 60)
    rc = run([sys.executable, "build_dashboard.py", "--xlsx", XLSX_PATH, "--out", "docs/index.html"])
    if rc != 0:
        print("\nERRO ao gerar o painel — veja a mensagem acima.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Enviando a atualização para o GitHub...")
    print("=" * 60)
    run(["git", "add", "docs/index.html"])
    msg = "Atualiza painel com nova planilha ({})".format(
        datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    )
    rc = run(["git", "commit", "-m", msg])
    if rc != 0:
        print("\nNada para enviar — o painel gerado é igual ao da última atualização.")
        return

    rc = run(["git", "push"])
    if rc != 0:
        print("\nERRO ao enviar para o GitHub.")
        print("Rode 'git push' manualmente nesta pasta para ver o motivo (login, conexão, etc).")
        sys.exit(1)

    print("\nPainel atualizado e publicado com sucesso!")
    print("Link (atualiza em 1-2 minutos): https://airtonaugusto.github.io/Dashboard-SM-A-/")


if __name__ == "__main__":
    main()
