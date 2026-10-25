# -*- coding: utf-8 -*-
"""[lotul 12, pachetul d112b] D112: „Baza de calcul al indemnizaţiei de şomaj” (B1_10 / B4_3) și „Venitul brut … realizat în baza
contractului” (B1_sal2) în luna cu concediu medical și la tipul de asigurat 1.11.2 (suma netaxabilă de 200 de lei).

Constatat 24.10.2026 pe copia F5 (tenant_9053), Ionescu 10/2026 (salariul 5.000 + 497,16 elemente variabile, certificat cod 01
13–15.10, indemnizația angajatorului 262): B1_10 = B4_3 = B1_sal2 = 5.497 — brutul PREZENȚEI, cu salariul celor 3 zile de concediu —,
deși baza CAM (B1_5 = B4_14) și E3_8 erau 4.815 (salariul zilelor lucrate) + 262 = 5.077.

SURSE (locale, citite integral pe secțiunile B.1–B.4):
- OPANAF 605/2026 anexa 2 (`anaf_surse/opanaf_605_2026_d112.txt`), B.1 rândul 11: „«Baza de calcul al indemnizaţiei de şomaj» - se
  completează cu suma reprezentând veniturile care constituie baza de calcul al indemnizaţiei de şomaj, conform art. 39 alin. (21) din
  Legea nr. 76/2002 […]”; „beneficiari ai măsurii «200 lei din salariul minim, sumă netaxabilă» […] în baza de calcul al indemnizaţiei
  de şomaj, nu este inclusă suma de 200 lei”; B.4 rândul 8: „Se calculează prin însumarea bazelor de calcul a indemnizaţiei de şomaj
  corespunzătoare tuturor contractelor”.
- Legea 76/2002 art.39 alin.(2^1) (`anaf_surse/legea_76_2002_somaj.txt`, legislatie.just.ro, forma consolidată): „Veniturile care
  constituie baza de calcul al indemnizației de șomaj, prevăzute la alin. (2) lit. b), se stabilesc prin normele metodologice de aplicare
  a prezentei legi și se declară prin Declarația privind obligațiile de plată a contribuțiilor sociale […]”.
- HG 174/2002, normele metodologice, art.19^1 alin.(1) (același fișier): „Veniturile care constituie baza de calcul al indemnizației de
  șomaj prevăzute la art. 39 alin. (2^1) din lege sunt veniturile care constituie baza de calcul al contribuției asiguratorii pentru
  muncă.” -> B1_10 = B1_5 (baza CAM a salariatului), B4_3 = ΣB1_10 (structura D112: „B4_3=ΣB1_10”, DUK regula „B4_3 = Suma(B1_10)”).
- Legea 53/2003 art.49 alin.(2) (`anaf_surse/legea_53_2003_codul_muncii.txt`): „Suspendarea contractului individual de muncă are ca
  efect suspendarea prestării muncii de către salariat și a plății drepturilor de natură salarială de către angajator”; art.50 lit.b):
  se suspendă de drept la „concediu pentru incapacitate temporară de muncă” -> salariul zilelor de concediu nu e „venit realizat”.
- B1_sal2 (INTERPRETARE CU TEMEI, scrisă în `core/d112.py` la `_b1_sal1`): OPANAF 605/2026 anexa 2 descrie A_sal2 și B1_sal2 cu același
  text, iar structura D112 (`anaf_surse/structura_D112_0726_070926.txt`, câmpul 14b) formalizează A_sal2: „A_sal2=E3_8-E3_69”. E3_69
  (venituri neimpozabile art.76 alin.(4)) nu e emis de aplicație -> B1_sal2 = E3_8.

CNP-ul de test are cifra de control verificată (algoritmul din CLAUDE.md): 1800101410013 (același cu `test_lot12_sal2_629_deducere_cm`).
Firma de probă: schemă sintetică, ștearsă la final.
"""
import pytest

from core import d112, db as _db, duk, salariati_api
from core.common import Perioada
from core.test_lot11_s9_deducere_plafon import _setup, structura, unic

_SCHEMA = "test_lot12_d112b"
_CNP = "1800101410013"


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


def _firma(conn, brut):
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": _CNP, "nume": "IONESCU", "dn": "1980-06-01", "brut": brut}], schema=_SCHEMA)
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
        cur.execute("SELECT id FROM salariati")
        return cur.fetchone()[0]


def _d112(conn, luna):
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=luna))[0]
    a = structura(xml)[_CNP]
    return xml, {s: unic(a, s) for s in ("asiguratB1", "asiguratB2", "asiguratB4", "asiguratE3")}, a


def _valid(xml, luna):
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=luna)
    assert rez["stare"] == "valid", rez


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_d112b_luna_cu_cm_baza_somaj_si_venitul_realizat(conn):
    """Salariat 7.000 lei, 09/2026 (22 de zile lucrătoare), certificat cod 01 pe 1–10.09.2026 (8 zile lucrătoare, media 240 lei/zi),
    salvat pe drumul aplicației. ROȘU pe codul de dinainte: B1_10 = B4_3 = B1_sal2 = 7.000 (salariul întreg, cu zilele de concediu)."""
    sid = _firma(conn, 7000)
    salariati_api.salveaza_concediu(conn, sid, {
        "serie": "AB", "numar": "112", "cod": "01", "data_acordare": "2026-09-01", "data_inceput": "2026-09-01",
        "data_sfarsit": "2026-09-10", "loc_prescriere": 1, "zile_cm": 8, "venituri_6_luni": 30000, "zile_6_luni": 125,
        "an": 2026, "luna": 9})
    conn.commit()
    xml, s, a = _d112(conn, 9)
    b1, b2, b4, e3 = s["asiguratB1"], s["asiguratB2"], s["asiguratB4"], s["asiguratE3"]
    d20 = sum(int(x["D_20"]) for x in a.get("asiguratD", []))
    assert d20 > 0 and int(b2["B2_5"]) < 7000, (a.get("asiguratD"), b2)   # premisa: concediul e în lună, salariul realizat e redus
    # HG 174/2002 norme art.19^1 alin.(1): baza indemnizației de șomaj = baza de calcul a CAM (B1_5 = salariul realizat + indemnizația
    # angajatorului, CF art.220^4 alin.(1) + art.220^5)
    assert int(b1["B1_10"]) == int(b1["B1_5"]) == int(b2["B2_5"]) + d20, (b1, b2, d20)
    # structura D112: „B4_3=ΣB1_10” (un singur contract)
    assert int(b4["B4_3"]) == int(b1["B1_10"]) == int(b4["B4_14"]), (b1, b4)
    # Legea 53/2003 art.49 alin.(2) + art.50 lit.b): salariul zilelor de concediu nu se plătește -> nu e venit realizat;
    # structura D112 câmpul 14b „A_sal2=E3_8-E3_69” (același text la B1_sal2), E3_69 neemis -> B1_sal2 = E3_8
    assert int(b1["B1_sal2"]) == int(e3["E3_8"]) < 7000, (b1, e3)
    assert int(b1["B1_sal1"]) == 7000, b1   # OPANAF 605/2026 anexa 2, B.1: „salariul brut de încadrare prevăzut în contract”
    _valid(xml, 9)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_d112b_tipul_1_11_2_fara_suma_netaxabila_in_baza_somaj(conn):
    """Salariat la salariul minim (4.325 lei), 09/2026, fără concediu: tipul de asigurat 1.11.2 (51), suma netaxabilă 200 lei.
    ROȘU pe codul de dinainte: B1_10 = B4_3 = 4.325 (cu suma netaxabilă)."""
    _firma(conn, 4325)
    conn.commit()
    xml, s, _a = _d112(conn, 9)
    b1, b2, b4, e3 = s["asiguratB1"], s["asiguratB2"], s["asiguratB4"], s["asiguratE3"]
    assert b1["B1_1"] == "51" and int(b2["B2_5S"]) == 200, (b1, b2)   # premisa: facilitatea OUG 89/2025 art.III e acordată
    # OPANAF 605/2026 anexa 2, B.1 rândul 11: la 1.11.2, „în baza de calcul al indemnizaţiei de şomaj, nu este inclusă suma de 200 lei”
    assert int(b1["B1_10"]) == int(b4["B4_3"]) == int(b1["B1_5"]) == 4325 - 200, (b1, b4)
    # B1_sal2 = venitul brut realizat, cu suma netaxabilă (e venit din salarii); = E3_8
    assert int(b1["B1_sal2"]) == int(e3["E3_8"]) == 4325, (b1, e3)
    _valid(xml, 9)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_d112b_luna_obisnuita_neschimbata(conn):
    """Salariat 7.000 lei, 09/2026, fără concediu și fără facilitate: baza de șomaj = baza CAM = brutul = 7.000 (neschimbat)."""
    _firma(conn, 7000)
    conn.commit()
    xml, s, _a = _d112(conn, 9)
    b1, b4, e3 = s["asiguratB1"], s["asiguratB4"], s["asiguratE3"]
    # HG 174/2002 norme art.19^1 alin.(1) + structura „B4_3=ΣB1_10”
    assert (int(b1["B1_10"]), int(b4["B4_3"]), int(b1["B1_5"]), int(b1["B1_sal2"]), int(e3["E3_8"])) == (7000,) * 5, (b1, b4, e3)
    _valid(xml, 9)
