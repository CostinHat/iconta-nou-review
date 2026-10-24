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


#: [deficiența 600, lotul 12] motivele cu care contabilul se întoarce din ANAF pe pagina de retur — mulțime ÎNCHISĂ; textul fiecăruia
#: (pe înțelesul lui, cu ce face mai departe) stă în `static/spv_callback.html` (`MESAJE`), gard `core/test_lot12_notif_600_spv_retur.py`.
#: Înainte: `?eroare=<textul excepției>` („state invalid: token expirat”, „HTTP 400 la /token: …”), iar o cădere din afara lui
#: `EroareSpv` (rețeaua spre ANAF, baza) ieșea 500 — contabilul rămânea pe o pagină de eroare a serverului, nu în iConta.
#:   ok         — conectat;
#:   anulata    — ANAF s-a întors cu `error` (autorizarea n-a fost dată);
#:   fara_cod   — ANAF s-a întors fără cod de autorizare;
#:   expirata   — drumul la ANAF a durat peste `spv_conector.STATE_DURATA_SEC`;
#:   nelegata   — întoarcerea nu poartă semnătura cererii plecate din iConta.eu (state lipsă / modificat / ilizibil);
#:   refuz_anaf — ANAF a refuzat schimbul codului pe acces (cod folosit deja, expirat) sau a răspuns fără cheile de acces;
#:   anaf_tace  — ANAF nu a răspuns la schimbul codului;
#:   nesalvata  — orice altă cădere (salvarea conexiunii, configurarea serverului).
MOTIVE_RETUR = ("ok", "anulata", "fara_cod", "expirata", "nelegata", "refuz_anaf", "anaf_tace", "nesalvata")


def _semnaleaza(motiv, detaliu):
    """Detaliul tehnic al unei întoarceri nereușite: în jurnalul serverului (nu pe ecran, nu în URL). Fără cod, fără state."""
    from core import observare as _obs
    _obs.esec_secundar("conectare SPV: %s" % motiv, detaliu)


def rezultat_callback(code, state, error="", error_description=""):
    """[600] Întoarcerea din ANAF -> motivul (din `MOTIVE_RETUR`). Nu ridică niciodată: orice cădere devine un motiv."""
    import requests
    if error:
        _semnaleaza("anulata", RuntimeError("ANAF a întors error=%r, error_description=%r" % (error[:200], (error_description or "")[:300])))
        return "anulata"
    if not code:
        _semnaleaza("fara_cod", RuntimeError("ANAF a întors fără `code` (state %s)" % ("prezent" if state else "lipsă")))
        return "fara_cod"
    try:
        principal = spv_conector.verifica_state(state)
    except spv_conector.EroareStateExpirat as e:
        _semnaleaza("expirata", e)
        return "expirata"
    except spv_conector.EroareSpv as e:
        _semnaleaza("nelegata", e)
        return "nelegata"
    except Exception as e:  # noqa: BLE001 — secretul de semnare lipsă din configurare: tot o întoarcere cu mesaj, nu 500
        _semnaleaza("nesalvata", e)
        return "nesalvata"
    try:
        # [P5 val 3, 11.09.2026] FARA conexiune in mana. Schimbul `code -> token` are termen de
        # 30 s si fereastra ANAF de 60 s; baza se atinge abia dupa raspuns, iar
        # `finalizeaza_autorizare` isi deschide singura tranzactia scurta in care persista si
        # COMITE — deci tokenul e salvat inainte ca ruta sa se intoarca.
        spv_conector.finalizeaza_autorizare(principal, code)  # APEL REAL ANAF
    except spv_conector.EroareSpv as e:
        _semnaleaza("refuz_anaf", e)
        return "refuz_anaf"
    except requests.exceptions.RequestException as e:
        _semnaleaza("anaf_tace", e)
        return "anaf_tace"
    except Exception as e:  # noqa: BLE001 — baza / decriptarea / orice altceva: contabilul se întoarce în iConta cu motivul
        _semnaleaza("nesalvata", e)
        return "nesalvata"
    return "ok"


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
            st = spv_conector.stare_conexiune(conn, principal)
            if st.get("conectat"):
                # [289, decizia Costin 17.10.2026] CUI-urile verificate cu tokenul activ — cu drept / fără drept (ce faci, la cele fără)
                st["cuiuri"] = spv_conector.cuiuri_verificate(conn, principal)
                st["explicatie_fara_drept"] = spv_conector.explicatie_fara_drept(st["cuiuri"])   # [315] o dată, nu pe fiecare firmă
            conn.rollback()
            return st

    @app.get("/anaf/oauth/callback")
    def anaf_oauth_callback(code: str = "", state: str = "", error: str = "", error_description: str = ""):
        """
        Callback OAuth (URL inregistrat la ANAF, exact). Fara auth de sesiune: identitatea
        PRINCIPALULUI vine din state-ul semnat. State invalid => iesire INAINTE de orice apel ANAF.
        Redirecteaza (303) catre pagina de retur cu un MOTIV dintr-o multime inchisa (`MOTIVE_RETUR`),
        niciodata cu textul unei exceptii (deficienta 600).
        """
        motiv = rezultat_callback(code, state, error, error_description)
        # parametrul `motiv` al adresei de retur e un COD din `MOTIVE_RETUR` (mulțime închisă), nu o afirmație despre datele firmei:
        # textul pentru om îl alege pagina de retur (`static/spv_callback.html`, `MESAJE`), iar conexiunea SPV e a cabinetului
        return RedirectResponse(_PAGINA_RETUR + "?" + urllib.parse.urlencode([("motiv", motiv)]), status_code=303)
