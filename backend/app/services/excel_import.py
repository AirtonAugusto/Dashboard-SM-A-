"""
Importa a planilha ProgramaçãoSMA.xlsx para o MySQL.

Decisão de arquitetura (ver ARQUITETURA_DASHBOARD_WEB.md): a planilha
deixa de ser o banco "ao vivo". Ela só é lida aqui, sob um lock de
arquivo (evita ler no meio de um "Salvar" do Excel), para popular ou
atualizar o MySQL. Toda a operação do dia a dia — mudar status, anexar
observação, remanejar prazo — acontece só no banco, que resolve
concorrência sozinho via transações (o problema que a planilha, sendo
editada por várias pessoas ao mesmo tempo, não resolveria bem).
"""
import datetime

import openpyxl
from filelock import FileLock, Timeout
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Atividade, SituacaoPrazo, StatusAtividade

ABA_ATIVIDADES = "Atividades(SM&A)"


def _mapear_status(valor) -> StatusAtividade:
    valor = (valor or "").strip().lower()
    if "conclu" in valor:
        return StatusAtividade.CONCLUIDO
    if "andamento" in valor:
        return StatusAtividade.EM_ANDAMENTO
    if "programad" in valor:
        return StatusAtividade.PROGRAMADO
    return StatusAtividade.A_PROGRAMAR


def _mapear_situacao(valor) -> SituacaoPrazo:
    valor = (valor or "").strip().lower()
    if "atras" in valor:
        return SituacaoPrazo.ATRASADO
    if "conclu" in valor:
        return SituacaoPrazo.CONCLUIDO
    return SituacaoPrazo.NO_PRAZO


def importar_planilha(db: Session, caminho: str | None = None) -> dict:
    caminho = caminho or settings.excel_import_path
    if not caminho:
        raise RuntimeError("EXCEL_IMPORT_PATH não configurado (.env).")

    lock = FileLock(caminho + ".lock", timeout=10)
    criadas, atualizadas = 0, 0

    try:
        with lock:
            wb = openpyxl.load_workbook(caminho, data_only=True)
            ws = wb[ABA_ATIVIDADES]
            headers = [c.value for c in ws[1]]

            for row in ws.iter_rows(min_row=2, values_only=True):
                if all(c is None for c in row):
                    continue
                d = dict(zip(headers, row))
                numero = str(d.get("N°") or "").strip()
                if not numero:
                    continue

                ini = d.get("DATA PREVISTA INICIO ")
                fim = d.get("DATA PREVISTA CONCLUSÃO")

                atividade = db.query(Atividade).filter(Atividade.numero_planilha == numero).first()
                nova = atividade is None
                if nova:
                    atividade = Atividade(numero_planilha=numero)
                    db.add(atividade)

                atividade.descricao = (d.get("DESCRIÇÃO DAS ATIVIDADES") or "").strip()
                atividade.local = d.get("LOCAL")
                atividade.data_inicio_prevista = (
                    ini.date() if isinstance(ini, datetime.datetime) else ini
                )
                atividade.data_fim_prevista = (
                    fim.date() if isinstance(fim, datetime.datetime) else fim
                )
                atividade.previsao_horas = d.get("PREVISÃO DE HORAS") or 0
                atividade.situacao_prazo = _mapear_situacao(d.get("SITUAÇÃO DO PRAZO "))
                atividade.status = _mapear_status(d.get("STATUS"))

                criadas += 1 if nova else 0
                atualizadas += 0 if nova else 1

            db.commit()
    except Timeout as exc:
        raise RuntimeError(
            "Não consegui obter o lock da planilha — outra importação está em andamento "
            "ou o arquivo está aberto de um jeito que impede a leitura."
        ) from exc
    except Exception:
        db.rollback()
        raise

    return {"criadas": criadas, "atualizadas": atualizadas}
