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
import urllib.parse

from fastapi import Depends, HTTPException
from fastapi.responses import RedirectResponse

from core import db
from core import spv_conector

_PAGINA_RETUR = "/static/spv_callback.html"

MODUL = "spv_rute"


def spv_principal(ctx):
    """
    RESOLVER UNIC context->principal (GARDUL 2) cu PROPRIETATE (GARDUL 4):
      - cabinet (are firm) -> principal_firm(firma LUI).
    Nu deschide la "orice user autentificat": cine nu detine un principal SPV -> 403.
    """
    firm = ctx.get("firm")
    if firm:
        return spv_conector.principal_firm(firm)
    raise HTTPException(403, "contul nu poate conecta SPV (fără cabinet)")


def monteaza(app, dep_context):
    """Inregistreaza rutele SPV. dep_context = dependenta de context autentificat (cere_context);
    proprietatea principalului o impune spv_principal, nu dependenta (cabinet)."""

    @app.get("/spv/autorizare")
    def spv_autorizare(ctx=Depends(dep_context)):
        """URL-ul de autorizare ANAF pentru principalul apelantului. Butonul = Regula 0 (UI)."""
        principal = spv_principal(ctx)
        url, _state = spv_conector.url_autorizare(principal)
        return {"url": url, "expira_sec": spv_conector.STATE_DURATA_SEC}

    @app.get("/spv/stare")
    def spv_stare(ctx=Depends(dep_context)):
        """Starea conexiunii SPV pentru ecran (fara secrete, fara apel ANAF)."""
        principal = spv_principal(ctx)
        with db.get_conn() as conn:
            return spv_conector.stare_conexiune(conn, principal)

    @app.get("/anaf/oauth/callback")
    def anaf_oauth_callback(code: str = "", state: str = "", error: str = ""):
        """
        Callback OAuth (URL inregistrat la ANAF, exact). Fara auth de sesiune: identitatea
        PRINCIPALULUI vine din state-ul semnat. State invalid => iesire INAINTE de orice apel ANAF.
        Redirecteaza (303) catre pagina prietenoasa de retur (succes/eroare), nu JSON.
        """
        def _retur(params):
            return RedirectResponse(_PAGINA_RETUR + "?" + urllib.parse.urlencode(params), status_code=303)
        if error or not code:
            return _retur({"eroare": error or "cod lipsă"})
        try:
            principal = spv_conector.verifica_state(state)
        except spv_conector.EroareSpv as e:
            return _retur({"eroare": str(e)})
        try:
            with db.get_conn() as conn:
                spv_conector.finalizeaza_autorizare(conn, principal, code)  # APEL REAL ANAF
        except spv_conector.EroareSpv as e:
            return _retur({"eroare": str(e)})
        return _retur({"ok": "1"})
