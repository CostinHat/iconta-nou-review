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


def _pune_coada_aprobata(cur, tip, xml, res):
    """Insereaza o intrare de coada 'aprobata' cu payload (xml + randuri), intoarce coada_id."""
    payload = {"xml": xml, "randuri": coada_api.randuri_din_res(res), "_an": 2026, "_luna": 6}
    cur.execute("""INSERT INTO public.declaratii_coada
        (cabinet_id, tenant_id, tip, perioada, stare, payload, hash, creat_de)
        VALUES (1,%s,%s,'25/07/2026','aprobata',%s,%s,'tester') RETURNING id""",
        (_TID, tip, _E.Json(payload), tip + xml))
    return cur.fetchone()[0]


def test_rectificativa_versioneaza_si_vederea_da_valorile_noi():
    """TESTUL CARE JUSTIFICA TEMA: re-depunere acelasi tip aceeasi perioada -> DOUA randuri
    (nr_depunere 1 si 2), fiecare cu xml/randuri proprii; vederea 'curente' da valorile NOI;
    depunerea initiala ramane citibila din TABEL. Prin marcheaza_depusa REAL (nu INSERT brut)."""
    conn = _conn()
    try:
        # ux_coada_activa (partial, exclude 'depusa') cere: depui prima INAINTE de a pune a doua
        with conn.cursor() as cur:
            id1 = _pune_coada_aprobata(cur, "d300", "<INITIAL/>", _RezFake(colectata=Decimal("100")))
        coada_api.marcheaza_depusa(conn, id1, depus_de="tester")     # id1 -> 'depusa'
        with conn.cursor() as cur:
            id2 = _pune_coada_aprobata(cur, "d300", "<RECTIFICAT/>", _RezFake(colectata=Decimal("200")))
        coada_api.marcheaza_depusa(conn, id2, depus_de="tester")     # rectificativa -> nr_depunere 2

        with conn.cursor() as cur:
            # TABEL: doua randuri, nr_depunere 1 si 2, xml/randuri proprii
            cur.execute("SELECT nr_depunere, xml, randuri FROM public.declaratii_depuse "
                        "WHERE tenant_id=%s AND tip='d300' ORDER BY nr_depunere", (_TID,))
            randuri_tabel = cur.fetchall()
            # VEDERE: un singur rand, cel curent (nr_depunere max) = valorile NOI
            cur.execute("SELECT nr_depunere, xml, randuri FROM public.declaratii_depuse_curente "
                        "WHERE tenant_id=%s AND tip='d300'", (_TID,))
            curent = cur.fetchall()

        assert [r[0] for r in randuri_tabel] == [1, 2]                    # doua versiuni
        assert randuri_tabel[0][1] == "<INITIAL/>"                        # initiala citibila in tabel
        assert Decimal(randuri_tabel[0][2]["colectata"]) == Decimal("100")
        assert randuri_tabel[1][1] == "<RECTIFICAT/>"
        assert Decimal(randuri_tabel[1][2]["colectata"]) == Decimal("200")

        assert len(curent) == 1                                          # vederea: o singura curenta
        assert curent[0][0] == 2                                         # nr_depunere max
        assert curent[0][1] == "<RECTIFICAT/>"                           # valorile NOI, nu cele vechi
        assert Decimal(curent[0][2]["colectata"]) == Decimal("200")
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
