# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/api`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:827`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

from core import db, facturi_api, documente_api
from core import repo_tenants
from core import erori as _erori
from core import uc_comun as _uc_comun
from core import db, facturi_api, documente_api
from core import repo_admin


def apiv1_firme(actx):
    """[P7 · use-case] Corpul rutei `/api/v1/firme`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn, conn.cursor() as cur:
        return {"firme": [{"id": r[0], "nume": r[1], "cui": r[2]} for r in repo_tenants.firme_pentru_api(cur, actx["firm"])]}


def apiv1_facturi(tenant_id, an, luna, actx):
    """[P7 · use-case] Corpul rutei `/api/v1/firme/{tenant_id}/facturi`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._api_schema(actx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return {"facturi": facturi_api.lista_facturi(conn, an, luna, None)}
    except ValueError as e:   # [lot 2] acelasi refuz ca in ecran, nu un 500 catre integrator
        raise _erori.DateInvalide(str(e))


def apiv1_kpi(tenant_id, an, luna, actx):
    """[P7 · use-case] Corpul rutei `/api/v1/firme/{tenant_id}/kpi`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from datetime import date as _d
    from core import kpi_client as _kpi
    schema = _uc_comun._api_schema(actx, tenant_id)
    azi = _d.today()
    an = an or azi.year
    luna = luna or azi.month
    with db.get_conn() as conn:
        randuri = documente_api.balanta(conn, schema, an, luna)
    return {"an": an, "luna": luna, "kpi": _kpi.kpi_din_balanta(randuri)}


def apiv1_balanta(tenant_id, an, luna, actx):
    """[P7 · use-case] Corpul rutei `/api/v1/firme/{tenant_id}/balanta`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    schema = _uc_comun._api_schema(actx, tenant_id)
    with db.get_conn() as conn:
        return {"balanta": documente_api.balanta(conn, schema, an, luna)}


def apiv1_factura_emite(tenant_id, corp, actx):
    """[P7 · use-case] Corpul rutei `/api/v1/firme/{tenant_id}/facturi`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._preincalzeste_cursul(corp.get("moneda"), corp.get("data_emitere"))   # [P5 val 3]
    # [26.08.2026] DOUA DIFERENTE FATA DE RUTA DIN ECRAN, amandoua reparate aici.
    #
    # (1) `platitor_tva` venea DIN CORPUL CERERII, cu implicit `True`. E un FAPT DESPRE FIRMA,
    #     nu despre cerere: intra in `_potriveste_linii` -> `cote_tva.potriveste_cota`, deci
    #     decide COTA de pe liniile facturii. Un integrator care nu-l trimite ar fi facturat cu
    #     TVA o firma neplatitoare. Ruta din ecran il citeste din `firma_profil`
    #     (`_platitor_tva_firma`); acum si aceasta. E interdictia 45 (P20): o valoare intrata
    #     din afara, fara sursa si grad de certitudine, peste un fapt pe care il stim.
    #     Masurat inainte de reparatie: `public.api_chei` = 0, deci efectul n-a fost produs.
    # (2) Numele beneficiarului nu era cerut, desi ruta din ecran il refuza explicit — iar o
    #     factura fara beneficiar nu e factura.
    #
    # CE RAMANE DIFERIT, DECLARAT: poarta „pleaca marfa acum?" (descarcarea gestiunii) nu se
    # poate pune pe o cale neinteractiva fara sa alegem in locul integratorului. E o decizie de
    # produs, consemnata, nu una tehnica.
    schema = _uc_comun._api_schema(actx, tenant_id)
    if not str(corp.get("tert_nume") or "").strip():
        raise _erori.DateInvalide("Denumirea beneficiarului e obligatorie pe factură.")
    # [R57, decizia lui Costin 26.08.2026] Aceeași poartă ca în ecran, dar pe o cale
    # neinteractivă nu se poate ÎNTREBA — deci se REFUZĂ fără răspuns explicit. Motivul lui:
    # *„un implicit, oricare ar fi, alege în locul integratorului: «descarcă» îl face să descarce
    # gestiunea fără să știe; «nu descarcă» lasă stocul greșit fără să afle."* Iar refuzul e
    # ieftin acum — `public.api_chei` = 0 — și ar fi imposibil de introdus peste un an.
    # Câmpul spune CE SE ÎNTÂMPLĂ, nu ce face codul: `marfa_pleaca_cu_factura`.
    _linii = corp.get("linii") or []
    _tip = corp.get("tip", "factura")
    _poarta_ceruta = (_tip == "factura") and any(
        isinstance(l, dict) and l.get("articol_id") for l in _linii)
    _pleaca = corp.get("marfa_pleaca_cu_factura")
    if _poarta_ceruta and _pleaca is None:
        raise _erori.DateInvalide({
            "cod": "POARTA_GESTIUNE_FARA_RASPUNS",
            "mesaj": ("Factura are linii de stoc, deci trebuie spus dacă marfa pleacă odată cu ea. "
                      "Nu există un răspuns implicit: unul ar descărca gestiunea fără știrea ta, "
                      "celălalt ar lăsa stocul greșit fără să afli."),
            "camp": "marfa_pleaca_cu_factura",
            "valori": {"true": "marfa pleacă acum — se descarcă gestiunea în aceeași tranzacție",
                       "false": "marfa nu pleacă acum — factura e doar fiscală, stocul rămâne"}})
    with db.get_conn(schema) as conn:
        # [lot 2, 03.09.2026] Ruta din ecran traducea de mult `ValueError` in `422`; asta nu —
        # deci `linii=[]` sau un cod de partener lipsa ieseau catre integrator ca
        # `500 Internal Server Error`, adica fara nicio vorba despre ce lipseste.
        try:
            r = facturi_api.emite_factura(
                conn,
                linii=corp.get("linii"),
                client_id=corp.get("client_id"),
                tert_nume=corp.get("tert_nume"),
                tert_cui=corp.get("tert_cui"),
                tert_adresa=corp.get("tert_adresa"),
                data_emitere=corp.get("data_emitere"),
                data_scadenta=corp.get("data_scadenta"),
                moneda=corp.get("moneda", "RON"),
                platitor_tva=_uc_comun._platitor_tva_firma(conn),
                status=corp.get("status", "de_preluat"),
                curs_manual=corp.get("curs_manual"),
                data_curs_manual=corp.get("data_curs_manual"),   # [R130] data cursului manual
                # [R130] Pe calea de API „cine" e CHEIA cabinetului, nu un utilizator — se scrie ca
                # atare. Un `integer` de utilizator ar fi trebuit sa inventeze unul.
                curs_manual_de="cheie API a cabinetului %s" % actx["firm"],
                tip=_tip,
            )
        except facturi_api.LiniiIncomplete as e:
            raise _erori.DateInvalide({"cod": "LINII_INCOMPLETE",
                                      "mesaj": "Completează liniile: "
                                               + "; ".join(x["eticheta"] for x in e.campuri),
                                      "campuri": e.campuri})
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        # [R57] Acelasi efect ca in ecran: descarcarea se face DOAR la raspuns afirmativ si in
        # ACEEASI tranzactie cu emiterea (atomic), nu intr-un al doilea apel al integratorului.
        if _poarta_ceruta and _pleaca is True and isinstance(r, dict) and r.get("factura_id"):
            from core import stocuri_cv_api as _cv_api
            from datetime import date as _dt_api
            r["descarcare"] = _cv_api.descarca_factura(
                conn, schema, r["factura_id"],
                corp.get("data_emitere") or _dt_api.today().isoformat())
    if not r.get("ok", True) and r.get("cod") == "MONEDA_NECOTATA":
        raise _erori.DateInvalide(r.get("mesaj"))      # [lot 2] aceeasi deosebire ca in ecran
    if not r.get("ok", True) and r.get("cod") == "CURS_PREA_VECHI":
        raise _erori.Conflict(r)            # [R130] acelasi refuz cu iesire ca in ecran
    if not r.get("ok", True) and r.get("cod") == "CURS_INDISPONIBIL":
        raise _erori.DateInvalide(r.get("mesaj"))
    return r



def eveniment_public(date):
    """[P7 · use-case] Corpul rutei `/api/eveniment-public`; docstringul ei a ramas in stratul HTTP."""
    tip = (date.tip or "").strip()
    if tip not in _uc_comun._EVENIMENTE_PUBLICE:
        return {"ok": False}   # tip necunoscut -> se ignora (nu strica clientul)
    pagina = "".join(c for c in (date.pagina or "landing").strip().lower()
                     if c.isalnum() or c in "/_-")[:128] or "landing"
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            repo_admin.scrie_eveniment_public(cur, tip, pagina)
    except Exception:
        return {"ok": False}
    return {"ok": True}

