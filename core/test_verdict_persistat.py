# -*- coding: utf-8 -*-
"""GARD — verdictul de validare se păstrează, și un verdict stătut nu ține locul unuia proaspăt.

**R41.** Validatorul oficial rula deja: `GET /coada/{id}/continut` cheamă DUKIntegrator la fiecare
deschidere a unui element din coadă. Ruta e `Read-only`, deci verdictul se **producea și se arunca**.
Consecința măsurată pe date: `coerenta` NULL pe 3 din 3, badge „neverificat" pentru orice declarație,
iar ecranul numea **„De depus"** o listă care conținea declarații fără verdict — o **afirmație
falsă**, nu o listă incompletă.

**MIEZUL, și e al patrulea câmp, nu primul:** *un verdict pe un XML care s-a regenerat între timp nu
mai e verdict.* De aceea se persistă **amprenta conținutului validat**, iar la citire se compară cu
amprenta XML-ului din coadă **acum**. Dacă diferă, verdictul e **stătut** și se tratează ca
**absent**, nu ca favorabil (P6: necunoscutul domină favorabilul).

**CE FACE IMPOSIBIL:** ca o declarație fără verdict proaspăt și valid să treacă în `aprobata` sau
`depusa` **tăcut**. Se poate trece — dar numai explicit, cu motiv, iar motivul se consemnează.

**CE NU VERIFICĂ, declarat:** dacă DUKIntegrator are dreptate. Verdictul lui e luat ca dat; aici se
păzește doar că **se păstrează, se leagă de un conținut, și se consultă**.
"""
import ast
import io
import os

import pytest

from core import coada_api
from core import db as _db

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XML_A = "<D300><R17_2>100</R17_2></D300>"
XML_B = "<D300><R17_2>200</R17_2></D300>"


def _db_ok():
    try:
        _db.init_pool()
        return True
    except Exception:                                         # noqa: BLE001
        return False


@pytest.fixture()
def element():
    """Un element de coadă efemer. Rollback la final: nimic nu rămâne în public."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    conn = _db.pool().getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume, patru_ochi_activ) "
                        "VALUES ('ZTEST VERDICT', false) RETURNING id")
            fid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email, password_hash, nume, rol, "
                        "accounting_firm_id, activ, poate_valida, poate_depune) "
                        "VALUES ('ztest_verdict@invalid','x','ZTest','angajat',%s,true,true,true) "
                        "RETURNING id", (fid,))
            uid = cur.fetchone()[0]
            # fixtura-sintetica-ok: tenant_id NEGATIV (spațiu imposibil în producție) + rollback
            cur.execute(
                "INSERT INTO public.declaratii_coada "
                "  (cabinet_id, tenant_id, tip, perioada, stare, payload, creat_de, creat_de_id) "
                "VALUES (%s,-42,'d300','2099-01','la_senior',%s,%s,%s) RETURNING id",
                (fid, __import__("json").dumps({"xml": XML_A, "_an": 2099, "_luna": 1}),
                 str(uid), uid))
            cid = cur.fetchone()[0]
        yield conn, cid, uid
    finally:
        conn.rollback()
        _db.pool().putconn(conn)


def _valid(conn, cid, xml):
    coada_api.scrie_verdict(conn, cid, {"stare": "valid", "erori": ""}, "test-validator", xml)


# ── amprenta: pură, pe conținut ──────────────────────────────────────────────
def test_amprenta_e_pe_continut_nu_pe_moment():
    assert coada_api.amprenta_xml(XML_A) == coada_api.amprenta_xml(XML_A)
    assert coada_api.amprenta_xml(XML_A) != coada_api.amprenta_xml(XML_B)


def test_CALIBRARE_o_diferenta_de_UN_caracter_schimba_amprenta():
    """Dacă amprenta ar fi pe lungime sau pe primele octeți, o regenerare cu aceeași formă și alte
    cifre ar păstra verdictul — exact cazul pe care câmpul există ca să-l prindă."""
    assert coada_api.amprenta_xml("<a>1</a>") != coada_api.amprenta_xml("<a>2</a>")


# ── cele trei stări ─────────────────────────────────────────────────────────
def test_fara_verdict_starea_e_LIPSA(element):
    conn, cid, uid = element
    assert coada_api.verdict_stare(conn, cid)["stare"] == "lipsa"


def test_cu_verdict_pe_acelasi_continut_starea_e_PROASPAT(element):
    conn, cid, uid = element
    _valid(conn, cid, XML_A)
    st = coada_api.verdict_stare(conn, cid)
    assert st["stare"] == "proaspat" and st["verdict"] == "valid", st


def test_MIEZUL_daca_XML_ul_s_a_regenerat_verdictul_e_STATUT(element):
    """Cel mai important test din fișier. Verdictul rămâne în bază, dar conținutul s-a schimbat —
    deci verdictul nu mai e despre ce se depune."""
    conn, cid, uid = element
    _valid(conn, cid, XML_A)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.declaratii_coada SET payload = jsonb_set(payload,'{xml}',%s) "
                    "WHERE id=%s", ('"%s"' % XML_B, cid))
    st = coada_api.verdict_stare(conn, cid)
    assert st["stare"] == "statut", st
    assert st["amprenta_verdict"] != st["amprenta_acum"]


# ── poarta ──────────────────────────────────────────────────────────────────
def test_fara_verdict_aprobarea_e_REFUZATA(element):
    conn, cid, uid = element
    r = coada_api.aproba(conn, cid, "ztest", aprobat_de_id=uid)
    assert r["ok"] is False and r["cod"] == "FARA_VERDICT", r


def test_verdictul_STATUT_nu_tine_locul_unuia_proaspat(element):
    """P6 pe traseu: un verdict care nu mai e despre conținutul curent se tratează ca ABSENT."""
    conn, cid, uid = element
    _valid(conn, cid, XML_A)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.declaratii_coada SET payload = jsonb_set(payload,'{xml}',%s) "
                    "WHERE id=%s", ('"%s"' % XML_B, cid))
    r = coada_api.aproba(conn, cid, "ztest", aprobat_de_id=uid)
    assert r["ok"] is False and r["cod"] == "FARA_VERDICT", r


def test_CALIBRARE_cu_verdict_proaspat_aprobarea_TRECE(element):
    """Direcția opusă: dacă poarta ar refuza și starea bună, ar bloca tot, iar testele de mai sus
    ar trece dintr-un motiv greșit."""
    conn, cid, uid = element
    _valid(conn, cid, XML_A)
    r = coada_api.aproba(conn, cid, "ztest", aprobat_de_id=uid)
    assert r["ok"] is True and r["stare"] == "aprobata", r


def test_trecerea_peste_blocare_e_POSIBILA_dar_CONSEMNATA(element):
    """«Cu trecere explicită și consemnată». Fără consemnare, poarta ar fi doar o întârziere."""
    conn, cid, uid = element
    r = coada_api.aproba(conn, cid, "ztest", aprobat_de_id=uid,
                         motiv_trecere="urgență declarată, validator indisponibil")
    assert r["ok"] is True, r
    with conn.cursor() as cur:
        cur.execute("SELECT trecere_motiv, trecut_de_id, trecut_la IS NOT NULL "
                    "FROM public.declaratii_coada WHERE id=%s", (cid,))
        motiv, cine, cand = cur.fetchone()
    assert motiv == "urgență declarată, validator indisponibil", motiv
    assert cine == uid and cand is True


def test_depunerea_e_pazita_la_fel(element):
    """Tranziția ireversibilă: `depusa` n-are nicio ieșire în TRANZITII, deci poarta contează aici
    mai mult decât oriunde."""
    conn, cid, uid = element
    _valid(conn, cid, XML_A)
    coada_api.aproba(conn, cid, "ztest", aprobat_de_id=uid)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.declaratii_coada SET payload = jsonb_set(payload,'{xml}',%s) "
                    "WHERE id=%s", ('"%s"' % XML_B, cid))
    r = coada_api.marcheaza_depusa(conn, cid, depus_de="ztest", depus_de_id=uid)
    assert r["ok"] is False and r["cod"] == "FARA_VERDICT", r


# ── lanțul, în cod ──────────────────────────────────────────────────────────
def test_ruta_care_valideaza_chiar_SCRIE_verdictul():
    """Validatorul rula deja acolo; ce lipsea era scrierea. Dacă apelul dispare, verdictul redevine
    o valoare care se afișează și se pierde — iar toate testele de mai sus rămân verzi."""
    t = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    arb = ast.parse(t)
    for n in ast.walk(arb):
        if isinstance(n, ast.FunctionDef) and n.name == "coada_continut":
            apeluri = {getattr(c.func, "attr", None) or getattr(c.func, "id", None)
                       for c in ast.walk(n) if isinstance(c, ast.Call)}
            assert apeluri >= {"valideaza", "scrie_verdict"}, (
                "ruta nu mai scrie verdictul pe care îl produce: %s" % sorted(apeluri))
            return
    raise AssertionError("nu mai găsesc ruta `coada_continut` — gardul măsoară ce nu vede")
