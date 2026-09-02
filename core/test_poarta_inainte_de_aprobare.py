# -*- coding: utf-8 -*-
"""GARD [02.09.2026]: POARTA CONFIRMARII CADE INAINTE DE APROBARE, nu dupa.

**DEFECTUL, masurat in `uvicorn.log`, nu dedus** — elementul 8052, la prima apasare reala:

    POST /coada/8052/aproba  -> 200 OK      <- clientul aproba INTAI
    POST /coada/8052/depune  -> 409         <- poarta cadea DUPA
    POST /coada/8052/aproba  -> 409         <- a doua apasare: "nu pot aproba din starea 'aprobata'"

**CE LASA IN URMA un refuz al portii, in forma veche:** elementul ramane `aprobata`. Din starea aia
**nu se mai poate RESPINGE** (`respinge` cere `la_senior`) — deci un refuz al supervizorului INGUSTA
optiunile omului, iar contractul modulului spune, scris, ca *nu blocheaza niciodata*. Si un client
care si-a pastrat starea veche re-cheama `aproba` si moare inainte sa ajunga la `depune`.

**CE PAZESTE GARDUL:**
  1. **ordinea in ruta** — poarta, apoi refuzul ei, apoi aprobarea, apoi depunerea. Citita din AST,
     nu din text: numerele de linie ale apelurilor, in `coada_depune`.
  2. **aprobarea nu se face cand nu trebuie** — pe un element care nu e `la_senior` se SARE explicit;
     cu patru-ochi efectiv REFUZA (validarea in doi nu se ocoleste de aici).
  3. **clientul nu mai inlantuie** — un singur `POST /aproba` in tot ecranul, cel al butonului de
     aprobare propriu-zis.

**CE NU PAZESTE, declarat:** nu verifica raspunsul HTTP al rutei (ar cere client de test peste toata
aplicatia); verifica ORDINEA in care ruta cheama cele trei lucruri, si comportamentul functiei pe
care a inceput s-o cheme.
"""
import ast
import io
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import coada_api as _ca            # noqa: E402
from core import db as _db                   # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402

_SCHEMA = "ztest_ordine_poarta"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _linii_apeluri(nume_functie):
    """{nume_apel: prima linie} pentru apelurile din functia data din `main.py`, citite cu AST.

    Se citeste STRUCTURA, nu textul: un apel numit intr-un comentariu sau intr-un sir nu conteaza
    (METODA §23). Numele apelului = atributul final (`poarta_confirmarii`, `marcheaza_depusa`...)."""
    arbore = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    fn = next((n for n in ast.walk(arbore)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nume_functie), None)
    assert fn is not None, "n-am gasit functia %r in main.py" % nume_functie
    out = {}
    for nod in ast.walk(fn):
        if isinstance(nod, ast.Call) and isinstance(nod.func, ast.Attribute):
            out.setdefault(nod.func.attr, nod.lineno)
    return out, fn


def test_ordinea_in_ruta_e_POARTA_apoi_APROBARE_apoi_DEPUNERE():
    apeluri, _fn = _linii_apeluri("coada_depune")
    for cerut in ("poarta_confirmarii", "auto_aproba_daca_e_cazul", "marcheaza_depusa"):
        assert cerut in apeluri, (
            "[anti-vacuu] `coada_depune` nu mai cheama %r — ordinea nu se poate verifica pe ceva "
            "ce nu se cheama. Apeluri gasite: %s" % (cerut, sorted(apeluri)))
    assert apeluri["poarta_confirmarii"] < apeluri["auto_aproba_daca_e_cazul"], (
        "poarta confirmarii (linia %d) vine DUPA aprobare (linia %d) — un refuz ar lasa elementul "
        "`aprobata`, stare din care nu se mai poate respinge. Exact defectul masurat pe 8052."
        % (apeluri["poarta_confirmarii"], apeluri["auto_aproba_daca_e_cazul"]))
    assert apeluri["auto_aproba_daca_e_cazul"] < apeluri["marcheaza_depusa"], (
        "aprobarea (linia %d) vine dupa depunere (linia %d)"
        % (apeluri["auto_aproba_daca_e_cazul"], apeluri["marcheaza_depusa"]))


def test_refuzul_portii_iese_din_ruta_INAINTE_de_aprobare():
    """Nu e destul ca poarta sa fie chemata mai sus: refuzul ei trebuie sa PARASEASCA ruta acolo.
    Altfel s-ar putea cheama poarta, ignora rezultatul, si aproba oricum."""
    apeluri, fn = _linii_apeluri("coada_depune")
    ridicari = [n.lineno for n in ast.walk(fn)
                if isinstance(n, ast.Raise) and n.lineno > apeluri["poarta_confirmarii"]]
    assert ridicari, "nu exista nicio iesire prin exceptie dupa poarta"
    assert min(ridicari) < apeluri["auto_aproba_daca_e_cazul"], (
        "prima iesire de dupa poarta (linia %d) e DUPA aprobare (linia %d) — deci un refuz al "
        "portii nu opreste aprobarea" % (min(ridicari), apeluri["auto_aproba_daca_e_cazul"]))


def test_ecranul_nu_mai_INLANTUIE_aprobarea_cu_depunerea():
    """Ancorat pe TEXT, si spun de ce: nu exista parser de JS in repo, iar proprietatea pazita e
    „cate apeluri catre /aproba mai exista in ecran". E o NUMARATOARE, nu o cautare de sir — un
    apel in plus o face rosie, ceea ce un `in` n-ar face."""
    sursa = io.open(os.path.join(_RAD, "static", "js", "ecrane", "validat.js"),
                    encoding="utf-8").read()
    n = sursa.count("/aproba`")
    assert n == 1, (
        "in `validat.js` sunt %d apeluri catre /aproba; trebuie sa ramana UNUL — cel al butonului "
        "de aprobare propriu-zis. Depunerea nu mai inlantuie: aprobarea e a serverului si vine "
        "DUPA poarta." % n)


@pytest.fixture
def coada_efemera():
    """Un rand de coada pe o firma sintetica, in tranzactie intoarsa."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                # fixtura-sintetica-ok: cabinet si tenant sintetice, in rollback
                cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('PROBA ORDINE') "
                            "RETURNING id")
                cab = cur.fetchone()[0]
                cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) "
                            "VALUES (%s,'PROBA ORDINE SRL',%s) RETURNING id", (_SCHEMA, cab))
                tid = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, perioada, "
                    "stare, payload, hash, creat_de, creat_de_id) VALUES "
                    "(%s,%s,'d300','25.01.2099','la_senior','{}','h-ordine','7777',NULL) "
                    "RETURNING id", (cab, tid))   # creat_de_id are cheie straina catre users
                cid = cur.fetchone()[0]
            yield conn, cid
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pe_un_element_care_nu_e_la_senior_aprobarea_SE_SARE_explicit(coada_efemera):
    """`{"ok": True, "sarit": True}` — un „n-am facut nimic" EXPLICIT. Un `True` gol s-ar citi ca
    „am aprobat", iar cine il primeste n-ar putea deosebi cele doua."""
    conn, cid = coada_efemera
    with conn.cursor() as cur:
        cur.execute("UPDATE public.declaratii_coada SET stare='aprobata' WHERE id=%s", (cid,))
    r = _ca.auto_aproba_daca_e_cazul(conn, cid, "8888", None)
    assert r.get("ok") and r.get("sarit") is True and r.get("stare") == "aprobata", r
    with conn.cursor() as cur:
        cur.execute("SELECT stare, aprobat_de FROM public.declaratii_coada WHERE id=%s", (cid,))
        stare, aprobat_de = cur.fetchone()
    assert stare == "aprobata" and aprobat_de is None, (
        "a rescris aprobarea unui element deja aprobat: %r/%r" % (stare, aprobat_de))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_inexistentul_nu_trece_drept_sarit(coada_efemera):
    """Directia opusa lui «sarit»: un element care NU EXISTA nu are voie sa raspunda `ok`."""
    conn, _cid = coada_efemera
    r = _ca.auto_aproba_daca_e_cazul(conn, 999999999, "8888", None)
    assert not r.get("ok") and r.get("cod") == "INEXISTENT", r
