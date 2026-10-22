# -*- coding: utf-8 -*-
"""[lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”] „Întocmitorul bilanțului: calitatea întocmitorului în profilul
cabinetului, interesul public în Date firmă; ambele blochează dacă lipsesc.”

Ce era (core/bilant.py `xml_s1005`, înainte): `interes_public=0` oricărei firme, `calit_intocmit=12` („CONTABIL SEF”) oricărui întocmitor,
`nume_intocmit` = administratorul — valori puse în locul celor ale firmei / cabinetului (clasa C69).

Sursa, citită pe tot antetul și pe nomenclator: anaf_surse/structura_SC_1225_270126.txt (S1002 / S1003 / S1005; la fel S1004):
  „15. interes_public Entitati de interes public N(1) DA interes_public=(0,1)”
  „20. nume_intocmit Nume si prenume Intocmit C(75 DA”
  „21. calit_intocmit Calitate intocmit N(2) DA Nomenclator calitate - Intocmit”
  „22. nri_intocmit Numar de inreg.in org.profesional C(15)”
  „22a cif_intocmit CIF intocmit C(13) NU … daca calit_intocmit=(21,22) atunci cif_intocmit#null altfel cif_intocmit=null”
  „Nomenclator calitate - Intocmit: 11 DIRECTOR ECONOMIC, 12 CONTABIL SEF, 13 ALTA PERSOANA IMPUTERNICITA, POTRIVIT LEGII, 21 PERSOANE
  FIZICE AUTORIZATE, MEMBRE CECCAR, 22 PERSOANE JURIDICE AUTORIZATE, MEMBRE CECCAR”.
Fixturile pe bază: schemă efemeră din `tenant_template.sql` + un cabinet și o firmă sintetice în `public`, totul în ROLLBACK. CUI 14399840
(cifra de control verificată în `test_lot10_c69_bilant.py::test_fixtura_e_valida`).
MUTAȚII (unit): `erori_intocmitor` întoarce [] -> `test_lipsa_opreste_bilantul` pică; `interes_public` scris 0 fix -> `test_antetul_din_date_firma_si_cabinet` pică.
"""
import io
import re

import pytest

from core import bilant as b, bilant_api, firma_profil_api as fp
from core.erori import RefuzGenerare

PROF = {"cui_numeric": "14399840", "nume": "FIRMA L11 SRL", "reg_com": "J12/1/2020", "caen": "6920", "adresa": "Str. Probei 9",
        "cod_judet": 12, "mare_contribuabil": False, "forma_proprietate": "35", "declarant_nume": "POPESCU",
        "declarant_prenume": "ION", "interes_public": False, "calit_intocmit": 22, "intocmit_nume": "CABINET PROBA SRL",
        "cif_intocmit": "14399840", "nri_intocmit": "12345"}


def _xml(prof):
    return b.xml_s1005(prof, 2025, {}, {49: 100}, {}, {8: 5})


def _at(xml, nume):
    m = re.search(r'\b%s="([^"]*)"' % nume, xml)
    return m.group(1) if m else None


def test_nomenclatorul_calitatii_e_cel_din_structura():
    """„Nomenclator calitate - Intocmit” (ultima parte a structurii): exact codurile 11, 12, 13, 21, 22."""
    src = io.open("anaf_surse/structura_SC_1225_270126.txt", encoding="utf-8").read()
    bloc = src[src.rindex("Nomenclator calitate - Intocmit"):src.index("Nomenclator ordonatori - Judete")]
    assert sorted(int(x) for x in re.findall(r"^\s*(\d\d)\s+\S", bloc, re.M)) == sorted(b.CALITATI_INTOCMIT)
    assert b.CODURI_CALITATE_CU_CIF == (21, 22)   # „daca calit_intocmit=(21,22) atunci cif_intocmit#null”


def test_antetul_din_date_firma_si_cabinet():
    x = _xml(PROF)
    assert _at(x, "interes_public") == "0"                 # „15. interes_public … (0,1)” — al firmei
    assert _at(_xml(dict(PROF, interes_public=True)), "interes_public") == "1"
    assert _at(x, "calit_intocmit") == "22"                # „21. calit_intocmit … Nomenclator calitate - Intocmit” (era 12 fix)
    assert _at(x, "nume_intocmit") == "CABINET PROBA SRL"  # „20. nume_intocmit … DA” (era administratorul)
    assert _at(x, "cif_intocmit") == "14399840"            # „daca calit_intocmit=(21,22) atunci cif_intocmit#null”
    assert _at(x, "nri_intocmit") == "12345"               # „22. nri_intocmit Numar de inreg.in org.profesional”
    x12 = _xml(dict(PROF, calit_intocmit=12, cif_intocmit="14399840"))
    assert _at(x12, "cif_intocmit") is None                # „altfel cif_intocmit=null”


@pytest.mark.parametrize("camp,valoare,text", [
    ("interes_public", None, "„Entitate de interes public” (Da / Nu) în Date firmă"),   # „15. interes_public … DA”
    ("calit_intocmit", None, "Calitatea întocmitorului bilanțului lipsește"),           # „21. calit_intocmit … DA”
    ("calit_intocmit", 99, "Calitatea întocmitorului bilanțului lipsește"),             # cod în afara nomenclatorului
    ("intocmit_nume", "", "Numele întocmitorului bilanțului lipsește"),                 # „20. nume_intocmit … DA”
    ("cif_intocmit", "", "CIF-ul întocmitorului lipsește"),                             # „(21,22) atunci cif_intocmit#null”
])
def test_lipsa_opreste_bilantul(camp, valoare, text):
    p = dict(PROF, **{camp: valoare})
    assert any(text in e for e in b.erori_antet(p)), b.erori_antet(p)
    assert any(text in e for e in bilant_api.erori_generare(p))
    with pytest.raises(ValueError) as ei:   # nici `xml_s1005` / `xml_s1003` chemate direct nu completează din capul lor
        _xml(p)
    assert text in str(ei.value)
    with pytest.raises(ValueError):
        b.xml_s1003(p, 2025, {}, {}, {}, {})


def test_tinta_refuzului():
    assert bilant_api.tinta_refuz(dict(PROF, interes_public=None)) == ("date_firma", "df-interes_public")
    assert bilant_api.tinta_refuz(dict(PROF, calit_intocmit=None)) == ("date_cabinet", "cab-calit_intocmit")
    assert bilant_api.tinta_refuz(dict(PROF, intocmit_nume=None)) == ("date_cabinet", "cab-nume_intocmit")
    assert bilant_api.tinta_refuz(dict(PROF, cif_intocmit=None)) == ("date_cabinet", "cab-cif_intocmit")
    # întâi Date firmă: un refuz are un singur buton, textul le numește pe toate
    assert bilant_api.tinta_refuz(dict(PROF, interes_public=None, calit_intocmit=None)) == ("date_firma", "df-interes_public")


def test_interesul_public_in_profil_incomplet():
    assert fp.OBLIGATORII["interes_public"] == ("Bilanț",)
    assert {x["camp"] for x in fp.lipsuri({"tip_firma": "srl"})} >= {"interes_public"}   # operator de mulțime: crapă pe șir (garzi_pe_text)
    assert "interes_public" not in {x["camp"] for x in fp.lipsuri({"tip_firma": "srl", "interes_public": False})}   # „Nu” e o alegere
    # PFA nu întocmește bilanț (Legea 82/1991 art.28 alin.(1), sursa unică `neaplicabile_forma`)
    assert "interes_public" not in {x["camp"] for x in fp.lipsuri({"tip_firma": "pfa"})}


# ── pe bază: schemă efemeră + cabinet și firmă sintetice în `public`, ROLLBACK ─────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_SCHEMA = "ztest_l11p_bilant"


@pytest.fixture
def conn():
    from core import db, tenant_provisioning as tp
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('Cabinet sintetic L11P') RETURNING id")
                fid = cur.fetchone()[0]
                cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id, creat_la) VALUES (%s, 'FIRMA L11 SRL', %s, "
                            "'2020-01-01')",   # creată înainte de exercițiu: luna preluării nu taie anul 2025 (`data_soldurilor`)
                            (_SCHEMA, fid))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, reg_com, adresa, oras, judet, caen, declarant_nume, declarant_prenume, "
                            "declarant_functie, platitor_tva, tip_decont, mare_contribuabil, forma_proprietate) VALUES (1, 'FIRMA L11 SRL', "
                            "'14399840', 'J12/1/2020', 'Str. Probei 9', 'Cluj-Napoca', 'CJ', '6920', 'POPESCU', 'ION', 'ADMINISTRATOR', "
                            "false, 'T', false, '35')")
            yield c, fid
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_bilantul_pe_baza_refuza_cu_trimitere_apoi_iese_valid_pe_DUK(conn):
    conn, fid = conn
    from core import duk, uc_cabinet
    with pytest.raises(RefuzGenerare) as ei:
        bilant_api.genereaza(conn, _SCHEMA, 2025)
    d = ei.value.detaliu()
    assert (d["ecran"], d["camp_ecran"]) == ("date_firma", "df-interes_public"), d   # întâi Date firmă
    assert d["mesaj"] == (   # textul le numește pe toate, întreg (core/test_garzi_pe_text.py)
        "Bilanț nu se poate genera: Nu e declarat dacă firma e entitate de interes public — bilanțul o cere. Alege „Entitate de interes "
        "public” (Da / Nu) în Date firmă. Calitatea întocmitorului bilanțului lipsește — bilanțul o cere, din nomenclatorul ANAF (director "
        "economic, contabil șef, persoană fizică sau juridică autorizată CECCAR …). Completeaz-o în profilul cabinetului (Setări cont → "
        "Date cabinet, „Întocmitorul bilanțului”). Numele întocmitorului bilanțului lipsește — bilanțul îl cere. Completează-l în profilul "
        "cabinetului (Setări cont → Date cabinet, „Întocmitorul bilanțului”)."), d
    # Date firmă, pe calea ecranului: „Entitate de interes public: Nu”
    r = fp.salveaza_date(conn, {"interes_public": "0"}, user_id=1)
    assert r["ok"] is True and "interes_public" not in {x["camp"] for x in r["lipsuri"]}, r
    with pytest.raises(RefuzGenerare) as ei:
        bilant_api.genereaza_s1003(conn, _SCHEMA, 2025)
    d = ei.value.detaliu()
    assert (d["ecran"], d["camp_ecran"]) == ("date_cabinet", "cab-calit_intocmit"), d   # apoi profilul cabinetului
    # profilul cabinetului, pe calea ecranului (`uc_cabinet.intocmitor_salveaza`): persoană juridică CECCAR fără CIF -> refuz numit
    r = uc_cabinet.salveaza_intocmitor_conn(conn, fid, {"calit_intocmit": "22", "nume_intocmit": "CABINET PROBA SRL"})
    assert r["ok"] is False and r["camp"] == "cif_intocmit" and r["mesaj"].startswith("Scrie CIF-ul întocmitorului"), r
    r = uc_cabinet.salveaza_intocmitor_conn(conn, fid, {"calit_intocmit": "22", "nume_intocmit": "CABINET PROBA SRL",
                                                             "cif_intocmit": "RO 14399840"})
    assert r["ok"] is True and r["intocmitor"]["cif_intocmit"] == "14399840", r   # CUI fără „RO” și fără spații (decizia 10.3)
    xml, _av = bilant_api.genereaza(conn, _SCHEMA, 2025)
    assert (_at(xml, "interes_public"), _at(xml, "calit_intocmit"), _at(xml, "nume_intocmit"), _at(xml, "cif_intocmit")) == (
        "0", "22", "CABINET PROBA SRL", "14399840")
    v = duk.valideaza(xml, "s1005")
    if v.get("stare") == "gri":
        pytest.skip("validator S1005 indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", v
    xml3, _av = bilant_api.genereaza_s1003(conn, _SCHEMA, 2025)
    v3 = duk.valideaza(xml3, "s1003", an=2025, luna=12)
    assert v3.get("stare") in ("valid", "gri"), v3


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cabinetul_refuza_calitatea_in_afara_nomenclatorului(conn):
    conn, fid = conn
    from core import uc_cabinet
    r = uc_cabinet.salveaza_intocmitor_conn(conn, fid, {"calit_intocmit": "14", "nume_intocmit": "X"})
    assert r["ok"] is False and r["camp"] == "calit_intocmit", r
    r = uc_cabinet.salveaza_intocmitor_conn(conn, fid, {"calit_intocmit": "12", "nume_intocmit": "X" * 76})
    assert r["ok"] is False and r["camp"] == "nume_intocmit", r     # „C(75)”
    r = uc_cabinet.salveaza_intocmitor_conn(conn, fid, {"calit_intocmit": "12", "nume_intocmit": "IONESCU MARIA",
                                                             "cif_intocmit": "14399840"})
    assert r["ok"] is True and r["intocmitor"]["cif_intocmit"] is None, r   # „altfel cif_intocmit=null”
    assert uc_cabinet.citeste_intocmitor_conn(conn, fid)["calitati"][0] == [11, "Director economic"]
