# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/declaratii`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:840`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

from core import db, auth_api, declaratii_api, control_fiscal_api, declaratii_componente
from core import repo_firma_profil
from core.common import azi_ro
from core.mesaje import FARA_ACCES_TENANT
from core import erori as _erori
from core import uc_comun as _uc_comun


def declaratii_tipuri(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/declaratii/tipuri`; docstringul ei a ramas in stratul HTTP."""
    if tenant_id is None:
        raise _erori.CerereGresita("Alege firma întâi.")
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            row = repo_firma_profil.profil_fiscal(cur)
        _vec = ({"tip_firma": row[0], "tip_decont": row[1], "platitor_tva": row[2],
                 "operatiuni_ic": row[3], "regim_fiscal": row[4]}   # [R94] regimul intra in vector
                if row else {})
        # [21.08.2026] FAPTUL BATE VECTORUL: selectorul nu mai blocheaza D390/D301 pe bifa cand exista
        # operatiuni IC reale (sau cand evidenta e incompleta). Tiparul tenant_006. Sonda se cheama
        # INAINTE de inchiderea conexiunii - inainte era calculata dupa `with`, ceea ce n-ar fi mers.
        _neap = control_fiscal_api.neaplicabile_selector(
            _vec, ic_fapt=(lambda: control_fiscal_api.ic_fapt_din_db(conn, schema, azi_ro().year)))
    _tipd = _vec.get("tip_decont")
    return {"tipuri": declaratii_api.tipuri(),
            "periodicitate": {t: declaratii_api.periodicitate_firma(t, _tipd) for t in declaratii_api.tipuri()},
            "neaplicabile": _neap}


def declaratie_valideaza(tip, date, ctx):
    """[P7 · use-case] Corpul rutei `/declaratii/{tip}/valideaza`; docstringul ei a ramas in stratul HTTP."""
    import base64 as _b64
    from core import duk as _duk
    body = date.model_dump(exclude_none=True)
    tenant_id = body.pop("tenant_id")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent(FARA_ACCES_TENANT)
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, tip, body)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    # an/luna OBLIGATORII pentru D406 (27.07.2026): SAF-T se valideaza cu
    # DUKIntegrator_AnLunaUI.jar, care le primeste ca parametri; fara ele
    # _valideaza_saft intoarce GRI intotdeauna - deci validarea D406 din aplicatie
    # nu s-a facut NICIODATA, desi calea merge (dovedit manual pe tenant_002/iunie
    # 2026: "Validare fara erori"). Celelalte declaratii le ignora (optionale).
    #
    # [R166, 05.09.2026] ...si tot nu se facea: perioada se citea din CORPUL cererii, dar
    # D406 se cere pe `trim` (cu `luna` generatorul da 422), iar conversia trim->luna-ancora
    # se petrece INAUNTRUL lui `declaratii_api` si nu ajunge inapoi in `body`. Rezultat: nu
    # exista niciun corp care sa treaca amandoua portile - forma care genereaza nu valideaza,
    # forma care ar valida nu genereaza. Se ia perioada de pe REZULTATUL generatorului, adica
    # cea folosita efectiv, cu corpul ca rezerva; o a doua conversie trim->luna aici ar fi
    # inceputul aceleiasi divergente tacute pe care a reparat-o R165.
    _an = getattr(res, "an", None) or body.get("an")
    _luna = getattr(res, "luna", None) or body.get("luna")
    rez = _duk.valideaza(xml, tip, an=_an, luna=_luna)  # java blocant
    return {"tip": tip, "stare": rez["stare"], "erori": rez["erori"],
            "severitate": rez.get("severitate"),  # [A2] E:(eroare) vs A:(atentionare) - frontendul il citeste
            "temei": rez["temei"], "limita": rez["limita"],
            "avertismente": getattr(res, "avertismente", None),
            "note_rezultat": getattr(res, "note_rezultat", None) or [],   # canal neutru (fapte despre rezultat); [] pt declaratiile fara canal
            # [poarta_gol_v1 27.07.2026] cate operatiuni are declaratia; None = nu se poate
            # numara (d101/d112). Ecranul pune o poarta la 0, ca declaratia goala legitima
            # sa nu mai arate identic cu cea golita de un query rupt.
            "operatiuni": declaratii_api.numar_operatiuni(tip, res),
            # [lista 5, 30.08.2026] DIN CE e facuta cifra, nu doar CATE. Pana azi ruta intorcea un
            # contor - „valid, 18 operatiuni" - iar contabilul nu putea vedea CARE 18: 0 din 92 de
            # iesiri isi aratau componentele (1c). Componentele existau pe obiectul de rezultat al
            # motorului; lipsea transportul. Ce nu se poate desface spune de ce, nu tace.
            "componente": declaratii_componente.componente(tip, res),
            "xml_b64": _b64.b64encode(xml.encode()).decode()}


def declaratie_genereaza(tip, date, ctx):
    """[P7 · use-case] Corpul rutei `/declaratii/{tip}`; docstringul ei a ramas in stratul HTTP."""
    body = date.model_dump(exclude_none=True)
    tenant_id = body.pop("tenant_id")
    # 1) pe public: aflu schema tenantului + verific accesul userului
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent(FARA_ACCES_TENANT)
    # 2) pe schema tenantului (SET LOCAL search_path în get_conn, PgBouncer-safe):
    #    modulul rulează pe conexiunea deja poziționată, NU mai setează el search_path
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, tip, body)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    avert = getattr(res, "avertismente", None)
    constat = getattr(res, "note_rezultat", None) or []   # canal neutru; [] pt declaratiile fara canal
    return {"tip": tip, "xml": xml, "avertismente": avert, "note_rezultat": constat,
            "operatiuni": declaratii_api.numar_operatiuni(tip, res),  # [poarta_gol_v1]
            "componente": declaratii_componente.componente(tip, res)}  # [lista 5]
