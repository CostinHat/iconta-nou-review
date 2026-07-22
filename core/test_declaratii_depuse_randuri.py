# -*- coding: utf-8 -*-
"""Teste F163v2 — persistarea declaratiei depuse (xml + randuri) in public.declaratii_depuse.

Acopera:
  - randuri_din_res pe un dataclass (cu Decimal) -> dict JSON-safe, Decimal round-trip valoric;
  - d112 (res = LISTA de avertismente, nu dataclass) -> randuri None, cu temei in cod;
  - round-trip DB real: scrie randuri (Decimal serializat) in jsonb, citeste, compara VALORIC;
  - rectificativa/re-depunere de acelasi tip NU distruge depunerea initiala (ON CONFLICT DO NOTHING).

Testele DB folosesc un tenant_id SINTETIC intr-o tranzactie ROLLBACK (PK n-are FK pe tenant_id),
deci NU ating tenantii reali.
"""
import dataclasses
from decimal import Decimal

import psycopg2.extras as _E

from core import coada_api, db

_TID = 990163   # tenant_id sintetic, doar in ROLLBACK


@dataclasses.dataclass
class _RezFake:
    """Imita un rezultat de declaratie dataclass (ca RezultatD300 etc.): sume Decimal + avertismente."""
    colectata: Decimal = Decimal("0")
    deductibila: Decimal = Decimal("0")
    avertismente: list = dataclasses.field(default_factory=list)


# ============================================================
#  PURE — randuri_din_res
# ============================================================
def test_randuri_din_res_dataclass_serializeaza_decimal():
    res = _RezFake(colectata=Decimal("1234.56"), deductibila=Decimal("789.10"),
                   avertismente=["Rezultat TVA 445 lei."])
    r = coada_api.randuri_din_res(res)
    assert isinstance(r, dict)
    # Decimal -> str (default=str), valoarea se pastreaza exact
    assert r["colectata"] == "1234.56"
    assert Decimal(r["colectata"]) == Decimal("1234.56")
    assert r["avertismente"] == ["Rezultat TVA 445 lei."]


def test_randuri_din_res_d112_lista_da_None():
    # d112.genereaza intoarce (xml, avertismente) - al 2-lea e o LISTA, nu dataclass -> None
    assert coada_api.randuri_din_res(["avertisment 1", "avertisment 2"]) is None
    assert coada_api.randuri_din_res(None) is None


# ============================================================
#  DB — round-trip Decimal + rectificativa non-distructiva
# ============================================================
def _conn():
    db.init_pool()
    return db.pool().getconn()


def test_round_trip_decimal_prin_jsonb():
    """Scrie randuri (Decimal serializat) -> jsonb -> citeste -> compara VALORIC."""
    res = _RezFake(colectata=Decimal("1000.01"), deductibila=Decimal("250.99"))
    randuri = coada_api.randuri_din_res(res)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (_TID, 2026, 6, "d300", "<x/>", _E.Json(randuri)))
            cur.execute("SELECT xml, randuri FROM public.declaratii_depuse "
                        "WHERE tenant_id=%s AND an=2026 AND luna=6 AND tip='d300'", (_TID,))
            xml, r = cur.fetchone()
        assert xml == "<x/>"
        # jsonb -> dict; Decimal-ul stocat ca str se reconstruieste exact
        assert Decimal(r["colectata"]) == Decimal("1000.01")
        assert Decimal(r["deductibila"]) == Decimal("250.99")
    finally:
        conn.rollback()
        db.pool().putconn(conn)


def test_d112_randuri_null_in_db():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (_TID, 2026, 6, "d112", "<x/>", None))
            cur.execute("SELECT randuri FROM public.declaratii_depuse "
                        "WHERE tenant_id=%s AND tip='d112'", (_TID,))
            assert cur.fetchone()[0] is None       # SQL NULL, nu {} sau ""
    finally:
        conn.rollback()
        db.pool().putconn(conn)


def test_rectificativa_acelasi_tip_nu_distruge_depunerea_initiala():
    """Re-depunere de ACELASI (tenant,an,luna,tip): ON CONFLICT DO NOTHING -> prima ramane."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # depunerea initiala
            cur.execute(
                "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri) "
                "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (_TID, 2026, 6, "d300", "<INITIAL/>", _E.Json({"colectata": "100"})))
            # rectificativa: acelasi PK, xml diferit
            cur.execute(
                "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri) "
                "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (_TID, 2026, 6, "d300", "<RECTIFICAT/>", _E.Json({"colectata": "200"})))
            cur.execute("SELECT xml, randuri FROM public.declaratii_depuse "
                        "WHERE tenant_id=%s AND tip='d300'", (_TID,))
            rows = cur.fetchall()
        assert len(rows) == 1                       # un singur rand (PK unique)
        assert rows[0][0] == "<INITIAL/>"           # prima depunere NEATINSA (non-distructiv)
        assert rows[0][1]["colectata"] == "100"
    finally:
        conn.rollback()
        db.pool().putconn(conn)


def test_d710_tip_separat_coexista_cu_d100():
    """D710 (rectificativa D100) = tip DIFERIT -> rand nou, fara conflict cu d100."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip) "
                        "VALUES (%s,2026,3,'d100') ON CONFLICT DO NOTHING", (_TID,))
            cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip) "
                        "VALUES (%s,2026,3,'d710') ON CONFLICT DO NOTHING", (_TID,))
            cur.execute("SELECT tip FROM public.declaratii_depuse WHERE tenant_id=%s AND an=2026 AND luna=3 "
                        "ORDER BY tip", (_TID,))
            assert [r[0] for r in cur.fetchall()] == ["d100", "d710"]  # coexista
    finally:
        conn.rollback()
        db.pool().putconn(conn)
