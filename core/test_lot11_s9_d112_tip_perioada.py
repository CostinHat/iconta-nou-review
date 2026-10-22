# -*- coding: utf-8 -*-
"""[lotul 11, C93, C94, C92] D112: tipul de asigurat al beneficiarului facilității (1.11.2 = 51), venitul lunii cu E3_4 = „P” și refuzul
certificatului cod 10 fără avizul medicului expert.

SURSE (locale):
- C93. OPANAF 605/2026 anexa 2 (`anaf_surse/opanaf_605_2026_d112.txt`), secțiunea B.1 rândul 1: „În cazul unui salariat care desfăşoară
  activitatea în baza unui contract individual de muncă cu normă întreagă, la locul unde se află funcţia de bază […] beneficiar al
  prevederilor art. III alin. (1) din O.U.G. nr. 89/2025 […] se va alege tipul de asigurat 1.11.2”; B.2 rândurile 5.2 / 5.3 și B.4 rândurile
  5.4 / 5.5 (suma netaxabilă și „Câştig brut realizat”). Structura D112 (`anaf_surse/d112_struct_anaf.txt`): nomenclatorul 5 „51 1.11.2
  Salariat (are CIM cu norma intreaga), beneficiar al masurii '200 300 de lei din sal.minim, suma netaxabila'”; „0<=B2_5S<=300 pt.B1_1=51”,
  „B2_5C= B2_5+ B2_5S pt.B1_1=51”, „B3_7C= B3_7+ B3_7S pt.B1_1=51”, „B4_7S=B2_5S+B2_6S+B2_7S+B3_7S”, „Daca B4_7S>0 atunci B4_7C = B4_7 +
  B4_7S”, „C1_11= ΣA_13 + ΣB2_5 + ΣB1_16 + ΣA_13S + ΣB2_5S”, „Daca (E3_1=’B’ sau E3_1=’A’) si E3_2=51,52,54 Atunci E3_3=1”.
- C94. OPANAF 605/2026 anexa 2, E.3 rândul 4: „"P" - se utilizează pentru veniturile realizate în perioada de raportare”; rândurile 5-6:
  „Se completează doar dacă la rândul 4 […] a fost utilizată opţiunea "A"”. Structura: „E3_5=null daca E3_4=’P’”.
- C92. Structura D112, D_13: „D_13#null pentru D_9 = 10 … ERR: Daca D_9 = 10 si D_13 null : Pentru reducerea cu 1/4 a duratei normale de
  lucru se completeaza numarul avizului medicului expert” (DUK regula S102).

CNP-urile de test sunt verificate cu algoritmul cifrei de control (CLAUDE.md): 1800101410013, 1800202410011.
"""
import pytest

from core import d112, db as _db
from core.common import Perioada
from core.test_lot11_s9_deducere_plafon import _setup, structura, unic

_SCHEMA = "test_lot11_s9_tip"


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
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _xml(conn, luna, salariati, cm=False):
    with conn.cursor() as cur:
        _setup(cur, salariati, schema=_SCHEMA)
        if cm:   # date de pornire: certificat cod 01 cu suma stocată (ca după `salveaza_concediu`), 5 zile din care 4 plătite de angajator
            cur.execute("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,brut_fnuass,baza,"
                        "media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere) "
                        "SELECT id,2026,%s,'01',5,4,0,500,0,4325,0,'AB','1',%s,%s,%s,1 FROM salariati WHERE nume='MINIM'",
                        (luna, "2026-%02d-05" % luna, "2026-%02d-05" % luna, "2026-%02d-09" % luna))
    conn.commit()
    return d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=luna))[0]


def _duk_valid_ultim(conn, luna):
    _duk_valid(d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=luna))[0], luna)


def _duk_valid(xml, luna):
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=luna)
    assert rez["stare"] == "valid", rez


_MINIM_10 = {"cnp": "1800101410013", "nume": "MINIM", "dn": "1980-06-01", "brut": 4325}
_MATUR = {"cnp": "1800202410011", "nume": "MATUR", "dn": "1980-06-01", "brut": 5000}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c93_beneficiarul_facilitatii_declarat_cu_tipul_51(conn):
    """10/2026: salariatul la minim (4.325, normă întreagă, funcția de bază) primește suma netaxabilă de 200 -> tip 51 (1.11.2) în B1_1 și
    E3_2, B2_5S = B4_7S = 200, B2_5C = B4_7C = 4.125 + 200; salariatul cu 5.000 rămâne tip 1, fără sumele „S”. C1_11 = ΣB2_5 + ΣB2_5S.
    ROȘU pe codul vechi: B1_1 = E3_2 = 1, fără B2_5S. DUK valid."""
    st = structura(_xml(conn, 10, [_MINIM_10, _MATUR]))
    m, t = st["1800101410013"], st["1800202410011"]
    b1, b2, b4, e3 = (unic(m, x) for x in ("asiguratB1", "asiguratB2", "asiguratB4", "asiguratE3"))
    # OPANAF 605/2026 anexa 2, B.1 rândul 1: beneficiarul art.III alin.(1) din OUG 89/2025 -> „tipul de asigurat 1.11.2” (cod 51);
    # structura: „Daca (E3_1=’B’ sau E3_1=’A’) si E3_2=51,52,54 Atunci E3_3=1”
    assert (b1["B1_1"], e3["E3_2"], e3["E3_3"]) == ("51", "51", "1"), (b1, e3)
    # B.2 rândul 5.2 (B2_5S) = suma netaxabilă acordată; 5.3 (B2_5C) = rândul 5 + rândul 5.2 („B2_5C= B2_5+ B2_5S pt.B1_1=51”)
    assert (b2["B2_5"], b2["B2_5S"], b2["B2_5C"]) == ("4125", "200", "4325"), b2
    # B.4 rândul 5.4 (B4_7S = B2_5S + …) și 5.5 („Daca B4_7S>0 atunci B4_7C = B4_7 + B4_7S”)
    assert (b4["B4_7"], b4["B4_7S"], b4["B4_7C"]) == ("4125", "200", "4325"), b4
    # salariatul fără facilitate: tip 1; structura: „Altfel B2_5S=0” (atribut neemis), B4_7S = B4_7C = 0
    tb2, tb4 = unic(t, "asiguratB2"), unic(t, "asiguratB4")
    assert (unic(t, "asiguratB1")["B1_1"], unic(t, "asiguratE3")["E3_2"]) == ("1", "1")
    assert set(tb2) & {"B2_5S", "B2_5C"} == set() and (tb4["B4_7S"], tb4["B4_7C"]) == ("0", "0"), (tb2, tb4)
    # angajatorC1: „C1_11= … ΣB2_5 + … ΣB2_5S”, „C1_T1=C1_11+ C1_21+ C1_31” -> 4.125 + 5.000 + 200
    c1 = unic(st["_angajator"], "angajatorC1")
    assert (c1["C1_11"], c1["C1_T1"]) == ("9325", "9325"), c1
    _duk_valid_ultim(conn, 10)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c93_tipul_51_in_semestrul_intai_si_cu_concediu_medical(conn):
    """03/2026 (suma netaxabilă 300, salariul minim 4.050) și 10/2026 cu concediu medical în lună: B2_5S = 300 / 200; cu B3 prezent,
    B3_7S = 0 și B3_7C = B3_7 (structura: „B3_7C= B3_7+ B3_7S pt.B1_1=51”; rândul 8.2 din B.3 „doar pentru tipurile de asiguraţi 3.9 şi
    3.10”). DUK valid pe ambele."""
    xml = _xml(conn, 3, [{**_MINIM_10, "brut": 4050}])
    b2 = unic(structura(xml)["1800101410013"], "asiguratB2")
    assert (b2["B2_5"], b2["B2_5S"], b2["B2_5C"]) == ("3750", "300", "4050"), b2   # OUG 89/2025 art.III: 300 lei (S1)
    _duk_valid(xml, 3)
    xml = _xml(conn, 10, [_MINIM_10], cm=True)
    m = structura(xml)["1800101410013"]
    b3, b4 = unic(m, "asiguratB3"), unic(m, "asiguratB4")
    assert (b3["B3_7"], b3["B3_7S"], b3["B3_7C"]) == ("500", "0", "500"), b3
    assert (b4["B4_7S"], int(b4["B4_7C"])) == ("200", int(b4["B4_7"]) + 200), b4
    _duk_valid(xml, 10)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c94_venitul_lunii_cu_e3_4_p_fara_e3_5_e3_6(conn):
    """Fiecare asiguratE3 al lunii: E3_4 = „P”, fără E3_5 / E3_6 (OPANAF 605/2026 anexa 2, E.3 rândurile 4-6). ROȘU pe codul vechi:
    E3_4="A" E3_5="10.2026" E3_6="10.2026"."""
    st = structura(_xml(conn, 10, [_MINIM_10, _MATUR]))
    e3 = [unic(st[cnp], "asiguratE3") for cnp in ("1800101410013", "1800202410011")]   # premisa: ambii asigurați au E3 (unic o cere)
    # „"P" - se utilizează pentru veniturile realizate în perioada de raportare”; structura: „E3_5=null daca E3_4=’P’”
    assert [(el["E3_4"], set(el) & {"E3_5", "E3_6"}) for el in e3] == [("P", set()), ("P", set())], e3
    _duk_valid_ultim(conn, 10)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c92_d112_refuza_numit_cod10_fara_aviz(conn):
    """Certificat cod 10 stocat fără numărul avizului medicului expert: D112 nu se generează, iar refuzul numește certificatul și câmpul
    (înainte: D_13 se omitea și declarația pica abia la DUK regula S102)."""
    with conn.cursor() as cur:
        _setup(cur, [_MATUR], schema=_SCHEMA)
        cur.execute("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,brut_fnuass,baza,"
                    "media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere) "
                    "SELECT id,2026,6,'10',5,0,5,0,500,30000,240,'AB','77','2026-06-01','2026-06-01','2026-06-05',1 FROM salariati")
    conn.commit()
    # structura D112, D_13: „D_13#null pentru D_9 = 10” — refuzul numește certificatul (seria/numărul) și câmpul D_13
    with pytest.raises(ValueError, match=r"^D112: certificatul de concediu medical AB/77 \(salariat CNP 1800202410011\) are codul 10, dar "
                                         r"nu are numărul avizului medicului expert, pe care D112 îl cere la acest cod\. Completează-l în certificat "
                                         r"\(ecranul Concediu medical, „Numărul avizului medicului expert”\)\.$"):
        d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=6))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c92_aceeasi_clasa_cod05_poarta_d12(conn):
    """Aceeași clasă ca avizul de la cod 10: la codurile 05 / 51 D112 cere codul bolii infecto-contagioase (D_12) — structura: „daca D_9=
    (05,51) atunci D_12#null … ERR: Nu s-a completat codul de boli infeco-contagioase”. Certificatul cod 05 cu codul 7 pe câmpul ecranului
    -> D_12 = 7, DUK valid; fără el -> generarea se oprește numit. ROȘU pe codul vechi: D_12 nu se emitea deloc (DUK: eroare)."""
    with conn.cursor() as cur:
        _setup(cur, [_MATUR], schema=_SCHEMA)
        cur.execute("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,brut_fnuass,baza,"
                    "media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere,cod_urgenta) "
                    "SELECT id,2026,6,'05',5,0,5,0,1000,30000,240,'AB','78','2026-06-01','2026-06-01','2026-06-05',1,7 FROM salariati")
    conn.commit()
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=6))[0]
    d = unic(structura(xml)["1800202410011"], "asiguratD")
    assert (d["D_9"], d.get("D_12"), d.get("D_11"), d.get("D_13")) == ("05", "7", None, None), d
    _duk_valid(xml, 6)
    with conn.cursor() as cur:
        cur.execute("UPDATE %s.concedii_medicale SET cod_urgenta = NULL" % _SCHEMA)
    conn.commit()
    with pytest.raises(ValueError, match=r"^D112: certificatul de concediu medical AB/78 .* are codul 05, dar nu are codul bolii "
                                         r"infecto-contagioase, pe care D112 îl cere la acest cod\."):
        d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=6))
