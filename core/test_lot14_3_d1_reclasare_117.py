"""[D1, comanda 14.3] Reclasificarea soldului de preluare 117 -> 1171 la firmele de test: notă validată la data preluării, idempotentă, fără să rescrie preluarea."""
import importlib.util
import os

from core.test_lot11_t import conn_t  # noqa: F401 — fixtura schemei sintetice

_CALE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "lot14_3_reclaseaza_117.py")
_spec = importlib.util.spec_from_file_location("lot14_3_reclaseaza_117", _CALE)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
SCHEMA = "tenant_test_lot11_t"


def _sold(conn, cont, deb, cred, data="2026-09-30"):
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS solduri_initiale (cont text PRIMARY KEY, denumire text, sold_debitor numeric DEFAULT 0, "
                    "sold_creditor numeric DEFAULT 0, data_referinta date, si_an_debit numeric, si_an_credit numeric, rulaj_an_debit numeric, rulaj_an_credit numeric)")
        cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES (%s,'x',%s,%s,%s)", (cont, deb, cred, data))


def test_profitul_de_pe_117_trece_pe_1171_cu_nota_validata_si_a_doua_rulare_nu_face_nimic(conn_t):
    _sold(conn_t, "117", 0, 14000)
    m = S.reclaseaza(conn_t, SCHEMA)
    assert m == "nota %s validată la 2026-09-30: 117 = 1171 14000.00 lei" % m.split()[1], m
    with conn_t.cursor() as cur:
        cur.execute("SELECT i.status, i.document_ref, l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id")
        assert [(a, b, c, d, float(e)) for a, b, c, d, e in cur.fetchall()] == [("validata", S.DOCUMENT, "117", "1171", 14000.0)]
        cur.execute("SELECT cont, sold_creditor FROM solduri_initiale")
        assert [(c, float(s)) for c, s in cur.fetchall()] == [("117", 14000.0)], "preluarea validată nu se rescrie"
    assert S.reclaseaza(conn_t, SCHEMA) == "are deja nota de reclasificare: nimic de făcut"


def test_pierderea_se_reclasifica_invers_iar_analiticul_existent_nu_se_atinge(conn_t):
    _sold(conn_t, "117", 500, 0)
    assert S.reclaseaza(conn_t, SCHEMA).endswith("1171 = 117 500.00 lei")


def test_balanta_cu_analitic_sau_fara_117_nu_se_atinge(conn_t):
    _sold(conn_t, "117", 0, 100)
    _sold(conn_t, "1171", 0, 100)
    assert S.reclaseaza(conn_t, SCHEMA) == "are deja analitic al lui 117 în balanță: nu se atinge"
