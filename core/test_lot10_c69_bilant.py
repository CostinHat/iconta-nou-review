# -*- coding: utf-8 -*-
"""[lotul 10, deficiența C69] Clasa „valoare inventată pe documentul ANAF în loc de blocaj” — antetul bilanțului.

Ce era (core/bilant.py `xml_s1005`, înainte): `bifaMC=1` (mare contribuabil) pentru ORICE firmă, `codJJ=10` (Buzău) pentru orice firmă,
`codPP=35` (SRL) pentru orice firmă, `nume_admin` = „ADMINISTRATOR” când lipsea declarantul (și numai numele, fără prenume), `codTT`
= 40 (București) când lipsea județul.

Decizia Costin 20.10.2026 (verbatim în DECIZII „Lotul 10, C69 … deciziile lui Costin”, pct.2): „Câmpuri noi + blocaj” — în Date
firmă „Mare contribuabil (Da/Nu)” și „Forma de proprietate” (nomenclatorul ANAF); codJJ din regula structurii; administratorul din
declarant; bilanțul se oprește dacă lipsesc.

Sursa (citită integral pe antet și pe nomenclatoare): anaf_surse/structura_SC_1225_270126.txt —
  „10. bifaMC Bifa pt. Mari contribuabili care depun bilantul la Bucuresti N(1) DA bifaMC=1 pt. Mari contribuabili bifaMC=0 pt.restul
  entitatilor”; „16. codTT Cod judet sediu (fara cod 41) N(2) DA Nomenclator Judete”; „17. codJJ Cod judet (incl.cod 41) pt. N(2) DA
  codJJ=codTT daca bifa_MC=0 codJJ=41 daca bifa_MC=1”; „18. codPP Cod forma de proprietate N(2) DA Nomenclator forme de proprietate”;
  „19. nume_admin Nume si prenume Administrator C(75) DA”; „Nomenclator forme de proprietate” (11 … 50, ultimele pagini).
Fixturile pe bază: schemă efemeră din `tenant_template.sql`, în ROLLBACK. CUI 14399840 (cifra de control verificată în testul
fixturii).
"""
import io
import re

import pytest

from core import bilant as b, bilant_api, firma_profil_api as fp
from core.erori import RefuzGenerare

PROF = {"cui_numeric": "14399840", "nume": "FIRMA C69 SRL", "reg_com": "J12/1/2020", "caen": "6920", "adresa": "Str. Probei 9",
        "cod_judet": 12, "mare_contribuabil": False, "forma_proprietate": "35", "declarant_nume": "POPESCU",
        "declarant_prenume": "ION"}


def _xml(prof):
    return b.xml_s1005(prof, 2025, {}, {49: 100}, {}, {8: 5})


def _at(xml, nume):
    m = re.search(r'\b%s="([^"]*)"' % nume, xml)
    return m.group(1) if m else None


def test_fixtura_e_valida():
    from core.identitate import valideaza_cui
    assert valideaza_cui("14399840")[0]


def test_nomenclatorul_formelor_de_proprietate_e_cel_din_structura():
    """Transcris din „Nomenclator forme de proprietate” (structura_SC_1225_270126.txt): 27 de coduri, de la 11 la 50."""
    assert sorted(b.FORME_PROPRIETATE) == ["11", "12", "13", "14", "15", "16", "21", "22", "23", "24", "25", "26", "27", "28", "29",
                                           "31", "32", "33", "34", "35", "36", "37", "41", "42", "43", "44", "50"]
    assert b.FORME_PROPRIETATE["35"] == "Societăți cu răspundere limitată"   # „35 Societati cu raspundere limitata”
    assert b.FORME_PROPRIETATE["34"] == "Societăți pe acțiuni"               # „34 Societati pe actiuni”
    src = io.open("anaf_surse/structura_SC_1225_270126.txt", encoding="utf-8").read()
    bloc = src[src.rindex("Nomenclator forme de proprietate"):src.index("Coduri CAEN - lista de valori")]   # tabelul de la final
    assert sorted(set(re.findall(r"^[ \t\f]*(\d\d)[ \t]{2,}\S", bloc, re.M))) == sorted(b.FORME_PROPRIETATE)   # aceleași coduri, nu altele


def test_antetul_vine_din_date_firma():
    x = _xml(PROF)
    assert _at(x, "bifaMC") == "0"            # „bifaMC=0 pt.restul entitatilor” (era 1 pentru orice firmă)
    assert _at(x, "codTT") == "12"            # „16. codTT Cod judet sediu” — Cluj
    assert _at(x, "codJJ") == "12"            # „codJJ=codTT daca bifa_MC=0” (era 10, Buzău)
    assert _at(x, "codPP") == "35"            # „18. codPP … Nomenclator forme de proprietate” — al firmei (era 35 fix)
    assert _at(x, "nume_admin") == "POPESCU ION"   # „19. nume_admin Nume si prenume Administrator” (era numai numele / ADMINISTRATOR)
    assert "ADMINISTRATOR" not in x


def test_marele_contribuabil_are_codJJ_41_si_bifa_1():
    x = _xml(dict(PROF, mare_contribuabil=True, forma_proprietate="34"))
    assert _at(x, "bifaMC") == "1"            # „bifaMC=1 pt. Mari contribuabili”
    assert _at(x, "codJJ") == "41"            # „codJJ=41 daca bifa_MC=1” (41 = DGAMC în „Nomenclator ordonatori - Judete”)
    assert _at(x, "codTT") == "12"            # „codTT … (fara cod 41)” — sediul rămâne al firmei
    assert _at(x, "codPP") == "34"


@pytest.mark.parametrize("camp,valoare,text", [
    ("mare_contribuabil", None, "„Mare contribuabil” (Da / Nu) în Date firmă"),        # „10. bifaMC … DA”
    ("forma_proprietate", None, "„Forma de proprietate” în Date firmă"),               # „18. codPP … DA”
    ("forma_proprietate", "99", "„Forma de proprietate” în Date firmă"),               # cod în afara nomenclatorului
    ("declarant_prenume", "", "„Prenume declarant” în Date firmă"),                    # „19. nume_admin Nume si prenume … DA”
    ("declarant_nume", None, "„Nume declarant”"),
    ("cod_judet", None, "„Județul” în Date firmă"),                                    # „16. codTT … DA”
])
def test_lipsa_opreste_bilantul_numit_pe_orice_cale(camp, valoare, text):
    p = dict(PROF, **{camp: valoare})
    assert any(text in e for e in b.erori_antet(p))
    assert any(text in e for e in bilant_api.erori_generare(p))
    with pytest.raises(ValueError) as ei:   # nici `xml_s1005` / `xml_s1003` chemate direct nu completează din capul lor
        _xml(p)
    assert text in str(ei.value)
    with pytest.raises(ValueError):
        b.xml_s1003(p, 2025, {}, {}, {}, {})


def test_harta_obligatoriilor_si_lipsurile():
    assert fp.OBLIGATORII["mare_contribuabil"] == ("Bilanț",) and fp.OBLIGATORII["forma_proprietate"] == ("Bilanț",)
    assert set(fp.OBLIGATORII["declarant_prenume"]) >= {"Bilanț"}   # „Nume si prenume Administrator”
    camp = {x["camp"] for x in fp.lipsuri({"mare_contribuabil": False, "forma_proprietate": "35"})}
    assert "mare_contribuabil" not in camp and "forma_proprietate" not in camp   # „Nu” e o alegere, nu o lipsă
    camp = {x["camp"] for x in fp.lipsuri({"mare_contribuabil": None, "forma_proprietate": ""})}
    assert {"mare_contribuabil", "forma_proprietate"} <= camp                   # nedeclarat = lipsă -> „Profil incomplet”


# ── pe bază: schemă efemeră, ROLLBACK ───────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_SCHEMA = "ztest_c69_bilant"


@pytest.fixture
def conn():
    from core import db, tenant_provisioning as tp
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, reg_com, adresa, oras, judet, caen, declarant_nume, declarant_prenume, "
                            "declarant_functie, platitor_tva, tip_decont) VALUES (1, 'FIRMA C69 SRL', '14399840', 'J12/1/2020', "
                            "'Str. Probei 9', 'Cluj-Napoca', 'CJ', '6920', 'POPESCU', 'ION', 'ADMINISTRATOR', false, 'T')")
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_bilantul_pe_baza_refuza_cu_trimitere_apoi_iese_cu_datele_firmei(conn):
    with pytest.raises(RefuzGenerare) as ei:
        bilant_api.genereaza(conn, _SCHEMA, 2025)
    d = ei.value.detaliu()
    assert d["ecran"] == "date_firma" and d["camp_ecran"] == "df-mare_contribuabil", d   # primul câmp lipsă, adus în vedere
    # refuzul e EXACT cele două câmpuri nedeclarate în fixtură („10. bifaMC … DA”, „18. codPP … DA”), din sursa unică `erori_antet`
    asteptate = b.erori_antet(dict(PROF, mare_contribuabil=None, forma_proprietate=None))
    assert len(asteptate) == 2, asteptate
    assert d["mesaj"].split(": ", 1)[1] == " ".join(asteptate), d
    with pytest.raises(RefuzGenerare):
        bilant_api.genereaza_s1003(conn, _SCHEMA, 2025)                                     # S1003: aceeași poartă
    # salvarea din Date firmă (calea ecranului): „Nu” și „Societăți cu răspundere limitată”
    r = fp.salveaza_date(conn, {"mare_contribuabil": "0", "forma_proprietate": "35"}, user_id=1)
    assert r["ok"] is True, r
    assert not [x for x in r["lipsuri"] if x["camp"] in ("mare_contribuabil", "forma_proprietate")]
    xml, _av = bilant_api.genereaza(conn, _SCHEMA, 2025)
    assert (_at(xml, "bifaMC"), _at(xml, "codTT"), _at(xml, "codJJ"), _at(xml, "codPP")) == ("0", "12", "12", "35")
    assert _at(xml, "nume_admin") == "POPESCU ION"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_salvarea_refuza_o_forma_in_afara_nomenclatorului(conn):
    r = fp.salveaza_date(conn, {"forma_proprietate": "99"}, user_id=1)
    assert r["ok"] is False and r["camp"] == "forma_proprietate"   # numai coduri din „Nomenclator forme de proprietate”
    r = fp.salveaza_date(conn, {"mare_contribuabil": "poate"}, user_id=1)
    assert r["ok"] is False and r["camp"] == "mare_contribuabil"   # Da / Nu, nu ghicit (`uc_comun.bifa`)
    d = fp.citeste_date(conn)
    assert ["35", "Societăți cu răspundere limitată"] in d["forme_proprietate"]   # lista ecranului = nomenclatorul ANAF


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_bilantul_cu_antetul_firmei_e_valid_pe_DUK(conn):
    """Validatorul oficial S1005 e judecătorul final: bifaMC=0 / codJJ=codTT / codPP=35 / nume_admin din declarant trec."""
    from core import duk
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET mare_contribuabil = false, forma_proprietate = '35' WHERE id = 1")
    xml, _av = bilant_api.genereaza(conn, _SCHEMA, 2025)
    v = duk.valideaza(xml, "s1005")
    if v.get("stare") == "gri":
        pytest.skip("validator S1005 indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", v
