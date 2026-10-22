# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 452 — comanda Costin 11.1 pct.8, verbatim] „nota «Retur în stoc Marfa B × 1 buc (stornare)» de pe F1 e refuzată
la validare cu un motiv fals («documentul ei a fost respins»).”

CAUZA (citită pe F1, tenant_049, 21.10.2026, numai citire): `stocuri_anulare.document_stornat` socotea „stornat la respingere” orice rând
cu `anuleaza_id` legat de notă. Returul la stornarea facturii (`stocuri_cv_api.retur_la_stornare`) e tot un rând cu `anuleaza_id` — dar e
documentul DE CORECȚIE, cu nota lui nouă și cu `factura_id` = factura de stornare. Pe F1 erau refuzate astfel patru note: returul F1A9
(170), contarea facturii de stornare F1A9 (142), returul F1A11 (152) și contarea F1A11 (151). Aceeași confuzie în `reface_factura`.

GARDA (`test_garda_citirile_lui_anuleaza_id`): orice SQL din `core/` care citește rândul stornării prin `anuleaza_id` (join pe
`o.id = r.anuleaza_id` sau `r.anuleaza_id IS NOT NULL`) poartă definiția unică `STORNARE_LA_RESPINGERE`, ori e declarat mai jos cu motiv.

Schemă efemeră din `tenant_template.sql`, în tranzacție anulată; date în 2099 (sintetic)."""
import glob
import io
import os
import re
from decimal import Decimal

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot11_s_452"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'S452 SRL', '14399840', 'cantitativ_valoric') "
                            "ON CONFLICT (id) DO UPDATE SET metoda_stoc = 'cantitativ_valoric'")
            yield c
        finally:
            c.rollback()


def _factura(cur, numar, storno_din=None, semn=1):
    cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, status, total, tva, storno_din_id) "
                "VALUES (%s, 'F1A', '2099-10-19', 'emisa', 'emisa', %s, 0, %s) RETURNING id", (numar, Decimal("27.50") * semn, storno_din))
    return cur.fetchone()[0]


def _scenariu(conn):
    """Factura F1A8 cu ieșirea ei de stoc (drumul aplicației, `iesire` cu `factura_id`), stornată de F1A9 cu retur în stoc (drumul
    aplicației, `retur_la_stornare`, cu documentul pe care îl scrie `facturi_api.storneaza`)."""
    from core import jurnal_api as _j, stocuri_cv_api as cva
    r = cva.intrare(conn, SCH, {"denumire": "Marfa B", "um": "buc", "data": "2099-10-01", "cantitate": 20, "pret_unitar": "27.50",
                                "document": "NIR nr 3 din 01.10.2099"})
    assert "eroare" not in r, r
    with conn.cursor() as cur:
        f8 = _factura(cur, "8")
        f9 = _factura(cur, "9", storno_din=f8, semn=-1)
    ies = cva.iesire(conn, SCH, {"articol_id": r["articol_id"], "data": "2099-10-19", "cantitate": 1,
                                 "document": _j.eticheta_factura("factura", "F1A", "8", "2099-10-19")}, factura_id=f8)
    assert ies and "eroare" not in ies, ies
    retur = cva.retur_la_stornare(conn, SCH, f8, f9, "2099-10-19", "Retur la " + _j.eticheta_factura("factura", "F1A", "9", "2099-10-19"))
    assert len(retur) == 1, retur
    return {"articol": r["articol_id"], "f8": f8, "f9": f9, "iesire_nota": ies["inregistrare_id"], "retur_nota": retur[0]["inregistrare_id"]}


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def test_def_452_returul_la_stornare_nu_e_document_respins(conn):
    from core import stocuri_anulare as sa
    s = _scenariu(conn)
    with conn.cursor() as cur:
        # roșu înainte (21.10.2026, codul publicat): „Stornare factura F1A nr. 8 …” / „Retur la Factură F1A9 …” — motivul fals
        assert sa.document_stornat(cur, SCH, s["retur_nota"]) is None
        # aceeași clasă: contarea facturii de stornare (nota cu `factura_id` = F1A9) — pe F1 nota 142
        cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status) VALUES ('2099-10-19', %s, 'Contare F1A9', "
                    "'facturi', 'ciorna') RETURNING id", (s["f9"],))
        contare_storno = cur.fetchone()[0]
        assert sa.document_stornat(cur, SCH, contare_storno) is None


def test_def_452_returul_se_valideaza_pe_drumul_unic(conn):
    """Nota returului trece de validare (`jurnal_api.valideaza` — drumul jurnalului și al cozii): OMFP 1802/2014 pct.69, stornarea
    în roșu e „corectarea cu semnul minus a operațiunii inițiale”, deci intră în evidență."""
    from core import jurnal_api as _j
    s = _scenariu(conn)
    assert _j.valideaza(conn, SCH, s["iesire_nota"]) == {"ok": True}
    rez = _j.valideaza(conn, SCH, s["retur_nota"])
    assert rez == {"ok": True}, rez


def test_452_stornarea_la_respingere_ramane_refuzata(conn):
    """Partea care rămâne adevărată: documentul RESPINS, cu stocul stornat (`storneaza`), nu se validează (OMFP 1802/2014 pct.69)."""
    from core import jurnal_api as _j, stocuri_anulare as sa, stocuri_cv_api as cva
    r = cva.intrare(conn, SCH, {"denumire": "Marfa C", "um": "buc", "data": "2099-10-01", "cantitate": 5, "pret_unitar": "10",
                                "document": "NIR nr 4 din 01.10.2099"})
    ies = cva.iesire(conn, SCH, {"articol_id": r["articol_id"], "data": "2099-10-02", "cantitate": 1, "document": "Bon de consum nr 9 din 02.10.2099"})
    out = sa.storneaza(conn, SCH, None, [ies["inregistrare_id"]], "probă")
    assert out.get("stornate"), out
    with conn.cursor() as cur:
        assert sa.document_stornat(cur, SCH, ies["inregistrare_id"])
    rez = _j.valideaza(conn, SCH, ies["inregistrare_id"])
    assert rez.get("cod") == sa.COD_DOCUMENT_STORNAT, rez


def test_452_reface_factura_nu_reface_returul_ca_iesire(conn):
    """`reface_factura` pe factura de STORNARE (recontabilizarea ei după respingere) nu „reface” ca ieșiri marfa întoarsă."""
    from core import stocuri_anulare as sa
    s = _scenariu(conn)
    assert sa.reface_factura(conn, SCH, s["f9"]) is None
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM miscari_stoc WHERE factura_id = %s", (s["f9"],))
        assert cur.fetchone()[0] == 1   # numai rândul returului


#: citirile lui `anuleaza_id` care NU deduc „documentul a fost respins” — fiecare cu motivul
_DECLARATE = {
    # reparația pe date din 09.10.2026, rulată pe producție înainte să existe returul la stornare (lotul 10); rândurile ei sunt stornări
    # la respingere peste mișcări în evidență. Patch-ul cu predicatul e cerut în raportul lotului 11 (S, 452), fiindcă schimbarea
    # fișierului unei migrări rulate îi cere o nouă rulare pe producție
    "core/migrare_nota_corectie.py": "reparația 09.10.2026 (patch cerut, schimbarea cere o nouă rulare)",
}
_CITIRE = re.compile(r"o\.id\s*=\s*r\.anuleaza_id|r\.anuleaza_id\s+IS\s+NOT\s+NULL", re.I)


def test_garda_citirile_lui_anuleaza_id():
    """MUTAȚIE: `{STORNARE_LA_RESPINGERE}` scos din `document_stornat` -> pică (și testele de mai sus)."""
    fara = []
    for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))):
        rel = os.path.relpath(f, RAD)
        if os.path.basename(f).startswith("test_") or rel in _DECLARATE:
            continue
        t = open(f, encoding="utf-8").read()
        for m in _CITIRE.finditer(t):
            # instrucțiunea SQL din jur: între ghilimelele triple / șirul în care stă potrivirea
            inceput = max(t.rfind('"""', 0, m.start()), t.rfind('("', 0, m.start()))
            sfarsit = t.find('"""', m.end())
            bucata = t[inceput:sfarsit if sfarsit > 0 else m.end() + 400]
            if "STORNARE_LA_RESPINGERE" not in bucata:
                fara.append("%s:%d" % (rel, t[:m.start()].count("\n") + 1))
    assert fara == [], fara
