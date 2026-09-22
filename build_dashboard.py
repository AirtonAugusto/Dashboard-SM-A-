#!/usr/bin/env python3
"""
Gera o dashboard HTML (Programação de Atividades SM&A) a partir da planilha
ProgramaçãoSMA.xlsx.

Uso:
    python build_dashboard.py --xlsx caminho/para/ProgramacaoSMA.xlsx \
                               --logo assets/logo_anglogold.png \
                               --template template.html \
                               --out docs/index.html

Basta rodar este script de novo, apontando para a planilha atualizada,
sempre que quiser refletir os dados mais recentes no painel. O arquivo
gerado em --out é autocontido (HTML + CSS + JS + dados + logo embutidos).
O padrão é docs/index.html porque é o caminho que o GitHub Pages usa
para publicar o painel automaticamente em um link público (veja o
README) — mas também pode ser aberto direto no navegador, sem precisar
de internet.
"""
import argparse
import base64
import datetime
import json
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("Faltou instalar a dependência: pip install openpyxl")


def extrair_atividades(ws):
    headers = [c.value for c in ws[1]]
    acts = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if all(c is None for c in row):
            continue
        d = dict(zip(headers, row))
        ini = d.get("DATA PREVISTA INICIO ")
        fim = d.get("DATA PREVISTA CONCLUSÃO")
        acts.append({
            "id": d.get("N°"),
            "desc": (d.get("DESCRIÇÃO DAS ATIVIDADES") or "").strip(),
            "local": d.get("LOCAL"),
            "ini": ini.strftime("%Y-%m-%d") if isinstance(ini, (datetime.date, datetime.datetime)) else None,
            "fim": fim.strftime("%Y-%m-%d") if isinstance(fim, (datetime.date, datetime.datetime)) else None,
            "horas": d.get("PREVISÃO DE HORAS") or 0,
            "situacao": (d.get("SITUAÇÃO DO PRAZO ") or "").strip(),
            "status": (d.get("STATUS") or "").strip(),
            "obs": (d.get("OBSERVAÇÕES") or "").strip() if d.get("OBSERVAÇÕES") else None,
        })
    return acts


def extrair_carga_diaria(ws):
    carga = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None or not isinstance(row[0], (datetime.date, datetime.datetime)):
            continue
        carga.append({
            "data": row[0].strftime("%Y-%m-%d"),
            "tarefas": row[1],
            "horas": round(row[2], 2) if row[2] is not None else 0,
            "situacao": row[3],
        })
    return carga


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", required=True, help="Caminho da planilha ProgramaçãoSMA.xlsx")
    ap.add_argument("--logo", default="assets/logo_anglogold.png", help="Logo (PNG) para a barra lateral")
    ap.add_argument("--template", default="template.html", help="Template HTML com os placeholders")
    ap.add_argument("--out", default="docs/index.html", help="Arquivo HTML final a gerar")
    ap.add_argument("--aba-atividades", default="Atividades(SM&A)", help="Nome da aba de atividades")
    ap.add_argument("--aba-carga", default="Carga Diária", help="Nome da aba de carga diária")
    args = ap.parse_args()

    wb = openpyxl.load_workbook(args.xlsx, data_only=True)
    acts = extrair_atividades(wb[args.aba_atividades])
    carga = extrair_carga_diaria(wb[args.aba_carga]) if args.aba_carga in wb.sheetnames else []

    data_json = json.dumps({"acts": acts, "carga": carga}, ensure_ascii=False, separators=(",", ":"))
    data_json = data_json.replace("</script>", "<\\/script>")

    logo_b64 = base64.b64encode(Path(args.logo).read_bytes()).decode() if Path(args.logo).exists() else ""

    template = Path(args.template).read_text(encoding="utf-8")
    out_html = template.replace("__DATA_JSON__", data_json).replace("__LION_B64__", logo_b64)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_html, encoding="utf-8")

    print(f"OK: {len(acts)} atividades, {len(carga)} dias de carga diária.")
    print(f"Painel gerado em: {out_path.resolve()}")


if __name__ == "__main__":
    main()
