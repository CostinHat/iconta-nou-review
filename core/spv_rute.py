# -*- coding: utf-8 -*-
"""
core/spv_rute.py — rutele HTTP ale conectorului SPV (pas 4 din ARHITECTURA_SPV.md).

Doua rute, subtiri: toata logica sta in spv_conector.py.
  GET /spv/autorizare        (auth cabinet) -> URL-ul de autorizare ANAF (+ state semnat)
  GET /anaf/oauth/callback   (fara auth)     -> ANAF redirecteaza aici; schimba codul pe token

MONTARE: proiectul nu foloseste APIRouter (main.py = @app.get direct). Ca sa nu introduc
un pattern nou si sa evit importul circular (dependenta cere_cabinet traieste in main.py),
main.py apeleaza monteaza(app, cere_cabinet). Nu se muta auth-ul, nu se refactorizeaza main.

ECRANUL de conectare (butonul care cheama /spv/autorizare, pagina de succes dupa callback)
= UI => Regula 0 (DESIGN_SYSTEM.md) => STOP, se stabileste cu Costin. Aici doar contractul
API (JSON), nu ecran.

APEL REAL ANAF: /anaf/oauth/callback -> finalizeaza_autorizare (schimb code->token). Se
executa doar cu state valid + code real, adica la testul real cu certificatul (pasul 5).
"""
from fastapi import Depends, HTTPException

from core import db
from core import spv_conector

MODUL = "spv_rute"


def monteaza(app, dep_cabinet):
    """Inregistreaza cele doua rute SPV pe app. dep_cabinet = dependenta de context cabinet."""

    @app.get("/spv/autorizare")
    def spv_autorizare(ctx=Depends(dep_cabinet)):
        """Intoarce URL-ul de autorizare ANAF. Butonul care-l deschide = Regula 0 (UI)."""
        firm = ctx.get("firm")
        if not firm:
            raise HTTPException(400, "utilizatorul nu are cabinet asociat")
        url, _state = spv_conector.url_autorizare(firm)
        return {"url": url, "expira_sec": spv_conector.STATE_DURATA_SEC}

    @app.get("/spv/stare")
    def spv_stare(ctx=Depends(dep_cabinet)):
        """Starea conexiunii SPV pentru ecran (fara secrete, fara apel ANAF)."""
        firm = ctx.get("firm")
        if not firm:
            raise HTTPException(400, "utilizatorul nu are cabinet asociat")
        with db.get_conn() as conn:
            return spv_conector.stare_conexiune(conn, firm)

    @app.get("/anaf/oauth/callback")
    def anaf_oauth_callback(code: str = "", state: str = "", error: str = ""):
        """
        Callback OAuth (URL inregistrat la ANAF, exact). Fara auth de sesiune: identitatea
        cabinetului vine din state-ul semnat. State invalid => iesire INAINTE de orice apel ANAF.
        """
        if error or not code:
            return {"ok": False, "eroare": error or "cod lipsa"}
        try:
            firm = spv_conector.verifica_state(state)
        except spv_conector.EroareSpv as e:
            return {"ok": False, "eroare": str(e)}
        with db.get_conn() as conn:
            token_id = spv_conector.finalizeaza_autorizare(conn, firm, code)  # APEL REAL ANAF
        return {"ok": True, "firm": firm, "token_id": token_id}
