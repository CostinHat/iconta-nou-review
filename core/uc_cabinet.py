# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/cabinet`.

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

from core import db, documente_api
from core import repo_cabinet, repo_tenants
from core import erori as _erori
from core import uc_comun as _uc_comun


def api_cheie_creeaza(corp, ctx):
    """[P7 · use-case] Corpul rutei `/cabinet/api-chei`; docstringul ei a ramas in stratul HTTP."""
    from core import api_public as _ap
    # [lotul 9] Corpul gol crea o cheie **fara nume** — iar cheia se arata O SINGURA DATA, la
    # creare. Una fara nume nu se mai poate recunoaste in lista ca s-o revoci: ramane activa, si
    # nimeni nu stie ce deschide.
    _nume = str((corp or {}).get("nume") or "").strip()
    if not _nume:
        raise _erori.DateInvalide("Cheia de API are nevoie de un nume. Ea se arată o singură dată, "
                                     "la creare; una fără nume nu se mai poate recunoaște în listă ca "
                                     "s-o revoci.")
    with db.get_conn() as conn:
        return _ap.genereaza(conn, ctx["firm"], _nume)


def api_chei_lista(ctx):
    """[P7 · use-case] Corpul rutei `/cabinet/api-chei`; docstringul ei a ramas in stratul HTTP."""
    from core import api_public as _ap
    with db.get_conn() as conn:
        return {"chei": _ap.lista(conn, ctx["firm"])}


def api_cheie_revoca(kid, ctx):
    """[P7 · use-case] Corpul rutei `/cabinet/api-chei/{kid}`; docstringul ei a ramas in stratul HTTP."""
    from core import api_public as _ap
    with db.get_conn() as conn:
        r = _ap.revoca(conn, ctx["firm"], kid)
    if r.get("eroare"):
        raise _erori.Inexistent(r["eroare"])
    return r


def cabinet_consolidare(an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/cabinet/consolidare`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from datetime import date as _d
    from core import kpi_client as _kpi
    azi = _d.today()
    an = an or azi.year
    luna = luna or azi.month
    with db.get_conn() as conn, conn.cursor() as cur:
        tenanti = repo_tenants.firme_cu_schema(cur, ctx["firm"])
        vizibile = _uc_comun._firme_vizibile(conn, ctx)   # [C26] asistentul: numai firmele alocate lui
    if vizibile is not None:
        tenanti = [t for t in tenanti if t[0] in vizibile]
    firme = []
    total = {"venituri": 0, "cheltuieli": 0, "profit": 0,
             "cash": 0, "de_incasat": 0, "de_platit": 0}
    with db.get_conn() as conn:
        for tid, nume, schema in tenanti:
            try:
                k = _kpi.kpi_din_balanta(documente_api.balanta(conn, schema, an, luna))
            except Exception:
                k = None
            firme.append({"tenant_id": tid, "nume": nume, "kpi": k})
            if k:
                for c in total:
                    total[c] = round(total[c] + k[c], 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    return {"an": an, "luna": luna, "firme": firme, "total": total}


# ── [lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”: „Întocmitorul bilanțului: calitatea întocmitorului în profilul
# cabinetului, interesul public în Date firmă; ambele blochează dacă lipsesc.”] Întocmitorul bilanțului e al cabinetului (îl întocmește
# cabinetul, pentru toate firmele lui). Structura ANAF (anaf_surse/structura_SC_1225_270126.txt): „20. nume_intocmit Nume si prenume
# Intocmit C(75 DA”, „21. calit_intocmit Calitate intocmit N(2) DA Nomenclator calitate - Intocmit”, „22. nri_intocmit Numar de inreg.in
# org.profesional C(15)”, „22a cif_intocmit CIF intocmit C(13) NU … daca calit_intocmit=(21,22) atunci cif_intocmit#null altfel
# cif_intocmit=null”. Coloanele: core/migrare_intocmitor_bilant.py. Citirea la generare: `bilant_api.intocmitor_cabinet`.
def citeste_intocmitor_conn(conn, firm_id):
    """{intocmitor: {calit_intocmit, nume_intocmit, cif_intocmit, nri_intocmit}, calitati: [[cod, eticheta]], cu_cif: [21, 22]}."""
    from core.migrare_intocmitor_bilant import CALITATI_INTOCMIT
    with conn.cursor() as cur:
        r = repo_cabinet.intocmitorul(cur, firm_id) or (None, None, None, None)
    return {"intocmitor": dict(zip(("calit_intocmit", "nume_intocmit", "cif_intocmit", "nri_intocmit"), r)),
            "calitati": [[k, v] for k, v in sorted(CALITATI_INTOCMIT.items())], "cu_cif": [21, 22]}


def salveaza_intocmitor_conn(conn, firm_id, date):
    """Scrie întocmitorul cabinetului. Un câmp gol NU refuză salvarea (bilanțul îl cere la generare, ca Date firmă — 427); se refuză numai
    o valoare INVALIDĂ: calitatea în afara nomenclatorului, numele peste 75 de caractere, CIF-ul cerut de calitățile 21 / 22 și lipsă sau
    cu cifra de control greșită. CIF-ul se păstrează fără „RO” și fără spații (decizia 10.3, `cui_forma.stocare`); la celelalte calități
    se golește („altfel cif_intocmit=null”). {ok, intocmitor} sau {ok: False, camp, mesaj}. Nu comite (tranzacția e a apelantului)."""
    from core import bilant as _b, cui_forma as _cf
    from core.identitate import valideaza_cif
    date = date or {}
    _c = str(date.get("calit_intocmit") or "").strip()
    try:
        calit = int(_c) if _c else None
    except ValueError:
        calit = -1
    # [lotul 11, deficiența 440, comanda Costin 11.1 pct.16] toate valorile invalide deodată (`ErorileFormularului`), fiecare cu câmpul
    # ei (`camp` = numele din cerere; ecranul pune prefixul „cab-”); {ok: False, camp: al primei, mesaj: toate, erori_campuri}
    from core.erori import ErorileFormularului as _Erori
    er = _Erori("Întocmitorul nu s-a salvat")
    if calit is not None and calit not in _b.CALITATI_INTOCMIT:
        er.camp("calit_intocmit",
                "Calitatea întocmitorului: una din nomenclatorul ANAF al bilanțului (director economic, contabil șef, altă persoană "
                         "împuternicită, persoană fizică sau juridică autorizată CECCAR).")
    nume = str(date.get("nume_intocmit") or "").strip() or None
    if nume and len(nume) > 75:
        er.camp("nume_intocmit", "Numele întocmitorului: cel mult 75 de caractere (structura bilanțului, C(75)).")
    nri = str(date.get("nri_intocmit") or "").strip() or None
    if nri and len(nri) > 15:
        er.camp("nri_intocmit", "Numărul de înregistrare în organizația profesională: cel mult 15 caractere (structura bilanțului, C(15)).")
    cif = _cf.stocare(date.get("cif_intocmit"))
    if calit in _b.CODURI_CALITATE_CU_CIF:
        if not cif:
            er.camp("cif_intocmit", "Scrie CIF-ul întocmitorului: bilanțul îl cere când întocmitorul e %s." % _b.CALITATI_INTOCMIT[calit].lower())
        else:
            ok, _tip, motiv = valideaza_cif(cif)
            if not ok:
                er.camp("cif_intocmit", "CIF-ul întocmitorului %s nu e valid (%s)." % (cif, motiv))
    else:
        cif = None
    if er:
        d = er.detaliu()
        prima = next(iter(d["erori_campuri"]), {}).get("camp")
        return {"ok": False, "camp": prima, "mesaj": d["mesaj"], "erori_campuri": d["erori_campuri"]}
    with conn.cursor() as cur:
        repo_cabinet.scrie_intocmitorul(cur, firm_id, calit, nume, cif, nri)
    return dict({"ok": True}, **citeste_intocmitor_conn(conn, firm_id))


def intocmitor_citeste(ctx):
    """Corpul rutei GET `/cabinet/intocmitor`."""
    with db.get_conn() as conn:
        return citeste_intocmitor_conn(conn, ctx["firm"])


def intocmitor_salveaza(date, ctx):
    """Corpul rutei POST `/cabinet/intocmitor` — numai administratorul cabinetului (ca „Date cabinet”, `uc_eu.eu_cabinet_set`)."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise _erori.FaraDrept("Doar administratorul cabinetului poate edita întocmitorul bilanțului (Date cabinet).")
    with db.get_conn() as conn:
        r = salveaza_intocmitor_conn(conn, ctx["firm"], date)
    if not r.get("ok"):
        raise _erori.DateInvalide({"mesaj": r["mesaj"], "erori_campuri": r.get("erori_campuri") or [{"camp": r["camp"], "mesaj": r["mesaj"]}]})
    return r
