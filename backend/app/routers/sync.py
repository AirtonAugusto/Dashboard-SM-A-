from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Role
from ..security import exigir_role
from ..services.excel_import import importar_planilha

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/importar-excel", dependencies=[Depends(exigir_role(Role.GESTOR))])
def importar_excel(db: Session = Depends(get_db)):
    try:
        return importar_planilha(db)
    except RuntimeError as exc:
        raise HTTPException(409, str(exc)) from exc
