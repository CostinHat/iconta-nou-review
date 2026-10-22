# -*- coding: utf-8 -*-
"""[deficiența 419, comanda Costin 9.3, 19.10.2026, PRIORITAR] „F1A8 a descărcat 1 buc Marfa B (22 → 21). Stornarea integrală F1A9 nu a
readus-o în stoc: fișa arată tot 21 buc, iar 607 rămâne înregistrat pe o vânzare anulată. Aplicația nici nu întreabă dacă marfa se
întoarce fizic (retur) sau rămâne la client (doar corecție de preț).”

Temei: OMFP 1802/2014 pct.69: „Înregistrarea stornării unei operațiuni contabile [...] se efectuează fie prin corectarea cu semnul minus
a operațiunii inițiale (stornare în roșu) [...]”; funcțiunea contului 371 (stocul scriptic = cel faptic). Regula de fond R5 din bază:
stornarea unei mișcări în evidență se scrie numai cu documentul de corecție, o notă NOUĂ în ciornă.
Schemă efemeră din template, ștearsă la ieșire."""
import datetime
import io
from decimal import Decimal

import pytest

from core import db as _db, facturi_api as _fa, stocuri_cv_api as cv, tenant_provisioning as _tprov

SCH = "efemer_419_retur"
ZI = datetime.date(2026, 10, 19)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc, serie_factura) "
                        "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric', 'F1A')")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _f1a8(conn):
    """Marfa B: 22 buc la 10 lei; F1A8 vinde 1 buc (descărcarea validată: 607 = 371, 10,00 lei)."""
    art = cv.intrare(conn, SCH, {"denumire": "Marfa B", "um": "buc", "data": "2026-10-01", "cantitate": 22, "pret_unitar": 10})
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva, tert_nume, tert_cui, status, tip) "
                    "VALUES ('F1A8', 'F1A', %s, 'emisa', 24.20, 4.20, 'DANTE INTERNATIONAL SA', 'RO14399840', 'emisa', 'factura') RETURNING id",
                    (ZI,))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, articol_id) "
                    "VALUES (%s, 'Marfa B', 1, 20, 21, %s)", (fid, art["articol_id"]))
    assert cv.descarca_factura(conn, SCH, fid, ZI)["erori"] == []
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE sursa = 'stocuri'")
    return fid, art["articol_id"]


def _stoc(conn, aid):
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(CASE WHEN tip = 'intrare' THEN cantitate ELSE -cantitate END), 0) FROM miscari_stoc "
                    "WHERE articol_id = %s", (aid,))
        return cur.fetchone()[0]


def test_stornarea_intreaba_daca_marfa_se_intoarce(conn):
    fid, aid = _f1a8(conn)
    assert [(x["articol"], x["cantitate_text"]) for x in _fa.detalii_factura(conn, fid)["iesiri_stoc"]] == [("Marfa B", "1 buc")]
    with pytest.raises(ValueError) as e:
        _fa.storneaza(conn, fid)
    assert getattr(e.value, "cod", None) == _fa.COD_CERE_RETUR and str(e.value) == (
        "Factura F1A8 a descărcat din stoc: Marfa B × 1 buc. Marfa se întoarce în stoc (retur) sau rămâne la client (numai corecția "
        "valorii)? Alege, apoi confirmă stornarea.")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE storno_din_id = %s", (fid,))
        assert cur.fetchone()[0] == 0                                    # fără răspuns, nimic scris
    assert _stoc(conn, aid) == Decimal("21")


def test_returul_readuce_marfa_si_storneaza_costul(conn):
    fid, aid = _f1a8(conn)
    r = _fa.storneaza(conn, fid, retur=True)
    assert [(x["articol"], x["cantitate"], x["valoare"]) for x in r["retur"]] == [("Marfa B", "1.000", "10.00")]
    assert _stoc(conn, aid) == Decimal("22")                            # 22 → 21 → 22
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (r["retur"][0]["inregistrare_id"],))
        doc = cur.fetchone()[0]
        cur.execute("SELECT serie FROM facturi WHERE numar = %s", (r["numar"],))
        ser = cur.fetchone()[0]
        # [lotul 11, 443, comanda Costin 11.1 pct.19] seria și numărul separat: „Factură F1A nr. 1”, nu „F1A1”
        assert ser and r["numar"].startswith(ser)
        assert doc == "Retur la Factură %s nr. %s din %s" % (ser, r["numar"][len(ser):], datetime.date.today().strftime("%d.%m.%Y"))
        cur.execute("SELECT i.status, l.cont_debit, l.cont_credit, l.suma FROM inregistrari i "
                    "JOIN inregistrari_linii l ON l.inregistrare_id = i.id WHERE i.id = %s", (r["retur"][0]["inregistrare_id"],))
        assert cur.fetchone() == ("ciorna", "607", "371", Decimal("-10.00"))   # 607 stornat în roșu, nota de corecție
        cur.execute("SELECT m.factura_id, m.anuleaza_id IS NOT NULL FROM miscari_stoc m WHERE m.cantitate < 0")
        assert cur.fetchone() == (r["factura_id"], True)                 # stornarea ieșirii, legată de factura de stornare
    assert _fa.detalii_factura(conn, fid)["iesiri_stoc"] == []           # nimic de întors a doua oară


def test_fara_retur_stocul_ramane(conn):
    fid, aid = _f1a8(conn)
    r = _fa.storneaza(conn, fid, retur=False)
    assert r["retur"] == [] and _stoc(conn, aid) == Decimal("21")
