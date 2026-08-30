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
    """Imita un rezultat de declaratie dataclass (ca RezultatD300 etc.): sume Decimal + avertismente + note_rezultat."""
    colectata: Decimal = Decimal("0")
    deductibila: Decimal = Decimal("0")
    avertismente: list = dataclasses.field(default_factory=list)
    note_rezultat: list = dataclasses.field(default_factory=list)   # canal neutru (fapte despre rezultat)


# ============================================================
#  PURE — randuri_din_res
# ============================================================
def test_randuri_din_res_dataclass_serializeaza_decimal():
    # "Rezultat TVA" e o CONSTATARE (fapt neutru despre rezultat), nu un avertisment: canal separat.
    res = _RezFake(colectata=Decimal("1234.56"), deductibila=Decimal("789.10"),
                   avertismente=["Sub-declarare: cota in afara 21/11/9."],
                   note_rezultat=["Rezultat TVA 445 lei."])
    r = coada_api.randuri_din_res(res)
    assert isinstance(r, dict)
    # Decimal -> str (default=str), valoarea se pastreaza exact
    assert r["colectata"] == "1234.56"
    assert Decimal(r["colectata"]) == Decimal("1234.56")
    # canalele se serializeaza distinct: constatarea in note_rezultat, avertismentul in avertismente
    assert r["note_rezultat"] == ["Rezultat TVA 445 lei."]
    assert r["avertismente"] == ["Sub-declarare: cota in afara 21/11/9."]
    assert "Rezultat TVA 445 lei." not in r["avertismente"]


def test_randuri_din_res_pe_ce_nu_e_dataclass_da_None():
    # Regula generala a functiei, nu un caz al lui d112: pana la 30.08.2026 d112 era chiar instanta
    # ei (intorcea o LISTA de avertismente), iar numele testului spunea asta. R105 i-a dat obiect de
    # rezultat, deci exemplul a ramas fara stapan - se pastreaza ca REGULA, cu numele corect.
    assert coada_api.randuri_din_res(["avertisment 1", "avertisment 2"]) is None
    assert coada_api.randuri_din_res(None) is None


def test_randuri_din_res_serializeaza_acum_si_d112():
    """[R105] Consecinta care se vede in BAZA, nu doar pe ecran: D112 isi persista randurile."""
    from core.d112 import RezultatD112, ObligatieD112
    r = RezultatD112(an=2026, luna=8, obligatii=[ObligatieD112("602", "5503XXXXXX", 1234)],
                     total_plata_a=1234)
    d = coada_api.randuri_din_res(r)
    assert d is not None and d["obligatii"][0]["datorat"] == 1234, d


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
            # fixtura-sintetica-ok: tenant_id sintetic (nu coliziune PK cu depunere reala)
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
            # fixtura-sintetica-ok: tenant_id sintetic (nu coliziune PK cu depunere reala)
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
    # fixtura-sintetica-ok: tenant_id sintetic (nu coliziune PK cu depunere reala)
    cur.execute("""INSERT INTO public.declaratii_coada
        (cabinet_id, tenant_id, tip, perioada, stare, payload, hash, creat_de)
        VALUES (1,%s,%s,'25/07/2026','aprobata',%s,%s,'tester') RETURNING id""",
        (_TID, tip, _E.Json(payload), tip + xml))
    return cur.fetchone()[0]


def _verdict_valid(conn, cid, xml):
    """[R41] Depunerea cere un verdict proaspat si valid. Fixtura il pune pe XML-ul ei real."""
    coada_api.scrie_verdict(conn, cid, {"stare": "valid", "erori": ""}, "test-validator", xml)


def test_rectificativa_versioneaza_si_vederea_da_valorile_noi():
    """TESTUL CARE JUSTIFICA TEMA: re-depunere acelasi tip aceeasi perioada -> DOUA randuri
    (nr_depunere 1 si 2), fiecare cu xml/randuri proprii; vederea 'curente' da valorile NOI;
    depunerea initiala ramane citibila din TABEL. Prin marcheaza_depusa REAL (nu INSERT brut)."""
    conn = _conn()
    try:
        # ux_coada_activa (partial, exclude 'depusa') cere: depui prima INAINTE de a pune a doua
        with conn.cursor() as cur:
            id1 = _pune_coada_aprobata(cur, "d300", "<INITIAL/>", _RezFake(colectata=Decimal("100")))
        _verdict_valid(conn, id1, "<INITIAL/>")                      # [R41] fara verdict, poarta refuza
        coada_api.marcheaza_depusa(conn, id1, depus_de="tester")     # id1 -> 'depusa'
        with conn.cursor() as cur:
            id2 = _pune_coada_aprobata(cur, "d300", "<RECTIFICAT/>", _RezFake(colectata=Decimal("200")))
        _verdict_valid(conn, id2, "<RECTIFICAT/>")                   # [R41]
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
            # fixtura-sintetica-ok: tenant_id sintetic (nu coliziune PK cu depunere reala)
            cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip) "
                        "VALUES (%s,2026,3,'d100') ON CONFLICT DO NOTHING", (_TID,))
            # fixtura-sintetica-ok: tenant_id sintetic (nu coliziune PK cu depunere reala)
            cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip) "
                        "VALUES (%s,2026,3,'d710') ON CONFLICT DO NOTHING", (_TID,))
            cur.execute("SELECT tip FROM public.declaratii_depuse WHERE tenant_id=%s AND an=2026 AND luna=3 "
                        "ORDER BY tip", (_TID,))
            assert [r[0] for r in cur.fetchall()] == ["d100", "d710"]  # coexista
    finally:
        conn.rollback()
        db.pool().putconn(conn)
