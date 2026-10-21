# -*- coding: utf-8 -*-
"""[lotul 10, deficiența C69] Clasa „valoare inventată pe documentul ANAF în loc de blocaj”: antetul D406 nu mai scrie nimic din
capul lui.

Ce era (core/d406.py `_header`, înainte): StreetName „-”, City „-”, PostalCode „000000”, ContactPerson FirstName „-” și LastName =
DENUMIREA FIRMEI, Telephone „-”, IBANNumber „RO00BANK0000000000000000” — iar validatorul DUK le accepta pe toate (proba din raport:
„telefon_liniuta stare=valid”, „iban_fals_RO00BANK stare=valid”), deci nimic nu oprea un fișier cu date fabricate. Același antet,
scris a doua oară, în `d406_active.xml_d406_anual_active`. Iar `repo_d406.select_firma_profil` nici nu citea telefonul, IBAN-ul,
declarantul și norma contabilă (`baza_contabila`, deci TaxAccountingBasis ieșea mereu „A”).

Sursele (citite integral pe secțiunea Header/Company):
  - anaf_surse/d406_schema_anaf.xlsx, foaia „5. Structures”;
  - XSD /opt/duk/saft/saft.xsd (CompanyHeaderStructure, AddressStructure, ContactHeaderStructure, PersonNameStructure,
    BankAccountStructure).
Și bilanțul: „16. codTT Cod judet sediu (fara cod 41) N(2) DA Nomenclator Judete” (anaf_surse/structura_SC_1225_270126.txt) — un
județ lipsă devenea „bucuresti”, unul nerecunoscut (ex. „CJ”) tot 40.
Fixturile pe bază: schemă efemeră din `tenant_template.sql`, în ROLLBACK. CUI 14399840 (cifra de control verificată), IBAN sintetic
RO59BTRLRONCRT0C69TEST01 (cifra de control mod-97 verificată cu `salariati_api.iban_valid`).
"""
import re
import io
import xml.etree.ElementTree as ET

import pytest

from core import d406, d406_active, firma_profil_api as fp, bilant_api
from core.salariati_api import iban_valid

IBAN = "RO59BTRLRONCRT0C69TEST01"
PROF = {"cui": "14399840", "nume": "FIRMA C69 SRL", "platitor_tva": True, "tip_decont": "L", "baza_contabila": "A",
        "adresa": "Str. Probei 9", "oras": "Cluj-Napoca", "cod_postal": "400001", "telefon": "0264 111 222",
        "iban": "RO59 BTRL RONC RT0C 69TE ST01", "declarant_nume": "POPESCU", "declarant_prenume": "ION"}


def _company(prof):
    return "\n".join(d406.antet_firma(prof))


def _texte(xml, tag):
    """Textele elementelor `tag` (numele local, fără namespace), din XML-ul PARSAT — ordinea documentului."""
    return [e.text or "" for e in ET.fromstring(xml.encode("utf-8")).iter() if e.tag.rsplit("}", 1)[-1] == tag]


def _el(xml, tag):
    t = _texte(xml, tag)
    return t[0] if len(t) == 1 else (None if not t else t)


def test_fixtura_e_valida():
    """Datele de test se verifică înainte de folosire (CLAUDE.md, „Date de test”)."""
    from core.identitate import valideaza_cui
    assert valideaza_cui("14399840")[0]
    assert iban_valid(IBAN)


def test_antetul_ia_campurile_din_date_firma_nu_le_inventeaza():
    x = _company(PROF)
    assert _el(x, "City") == "Cluj-Napoca"            # schema ANAF S.AD.5 City „Mandatory … 1” — localitatea firmei (era „-”)
    assert _el(x, "Telephone") == "0264 111 222"      # S.CTH.2 Telephone „Mandatory … 1” — telefonul firmei (era „-”)
    assert _el(x, "FirstName") == "ION"               # S.PN.2 FirstName „Prenumele persoanei … Mandatory” (era „-”)
    assert _el(x, "LastName") == "POPESCU"            # S.PN.5 LastName „Numele de familie al persoanei” (era DENUMIREA firmei)
    assert _el(x, "IBANNumber") == IBAN               # S.BA.1 IBANNumber „ISO 13616 … Mandatory” — al firmei, fără spații (era RO00BANK…)
    assert _el(x, "StreetName") == "Str. Probei 9"
    assert _el(x, "PostalCode") == "400001"
    assert _el(x, "RegistrationNumber") == "RO14399840"   # S.CMH.1: plătitor de TVA -> RO + CIF
    for inventat in ("<FirstName>-</FirstName>", "<Telephone>-</Telephone>", "RO00BANK0000000000000000", "000000", ">-<"):
        assert inventat not in x, inventat


def test_optionalele_lipsa_se_omit_nu_se_umplu():
    p = dict(PROF, adresa="", cod_postal=None)
    x = _company(p)
    assert _texte(x, "StreetName") == []    # S.AD.1 StreetName „Optional … 0..1”, XSD minOccurs="0" — lipsă => absent (era „-”)
    assert _texte(x, "PostalCode") == []    # S.AD.6 PostalCode „Optional … 0..1”, XSD minOccurs="0" — lipsă => absent (era „000000”)
    assert _texte(x, "City") == ["Cluj-Napoca"]   # S.AD.5 City „Mandatory … 1”


@pytest.mark.parametrize("camp,eticheta", [
    ("oras", "Localitatea"),               # S.AD.5 City „Mandatory … 1”
    ("telefon", "Telefon"),                # S.CTH.2 Telephone „Mandatory … 1”
    ("declarant_prenume", "Prenume declarant"),   # S.PN.2 FirstName „Mandatory … 1”
    ("declarant_nume", "Nume declarant"),  # S.PN.5 LastName „Mandatory … 1”
    ("iban", "IBAN"),                      # S.CMH.6 BankAccount „Mandatory … 1..*”, S.BA.1 IBANNumber
])
def test_lipsa_unui_camp_cerut_opreste_D406_numit(camp, eticheta):
    p = dict(PROF, **{camp: "  "})
    er = d406.erori_generare(p)
    assert any("„%s” în Date firmă" % eticheta in e for e in er), er   # mesajul numește câmpul ecranului și locul
    with pytest.raises(ValueError) as ei:                               # nicio cale nu scrie antetul cu golul umplut
        d406.antet_firma(p)
    assert eticheta in str(ei.value)
    res = d406.construieste(p, 2026, 6, [], [], [])
    with pytest.raises(ValueError):
        d406.build_xml(res)                                             # nici `build_xml` chemat direct
    with pytest.raises(ValueError):
        d406_active.xml_d406_anual_active(p, [], 2026)                  # nici fișierul anual de active


def test_harta_spune_ce_blocheaza_lipsa():
    """`OBLIGATORII` = sursa panoului „Profil incomplet — blochează …”; perechea (câmp, D406) e păzită și de test_camp_blocant."""
    blocheaza_d406 = {camp for camp, decl in fp.OBLIGATORII.items() if set(decl) >= {"D406"}}
    assert blocheaza_d406 >= {"oras", "telefon", "iban", "declarant_nume", "declarant_prenume", "nume", "cui"}, blocheaza_d406
    assert set(fp.OBLIGATORII["judet"]) >= {"Bilanț"}   # structura_SC_1225 „16. codTT Cod judet sediu … DA Nomenclator Judete”
    assert {"camp": "telefon", "declaratii": list(fp.OBLIGATORII["telefon"])} in fp.lipsuri(dict(PROF, telefon=""))


def test_anualul_de_active_foloseste_acelasi_antet():
    xml = d406_active.xml_d406_anual_active(PROF, [], 2026)
    assert _company(PROF) in xml                                         # aceeași sursă, nu o a doua copie
    assert _texte(xml, "RegistrationNumber") == ["RO14399840"]          # S.CMH.1 (copia veche scria CUI-ul fără RO)


def test_judetul_bilantului_din_nomenclator_fara_implicit():
    c = bilant_api.cod_judet_sediu
    assert c("CJ") == 12 and c("Cluj") == 12           # Nomenclator 1-Judete (d394_struct_anaf.txt): „12 Cluj” (era 40 pentru „CJ”)
    assert c("București") == 40 and c("B") == 40       # „40 Municipiul Bucuresti”
    assert c("Călărași") == 51 and c("GR") == 52       # „51 Calarasi”, „52 Giurgiu”
    assert c(None) is None and c("") is None           # lipsă => niciun cod (era „bucuresti” -> 40)
    assert c("XX") is None and c("41") is None         # nerecunoscut / „fara cod 41” => niciun cod (era 40)
    p = {"cui_numeric": "14399840", "nume": "X", "reg_com": "J12/1/2020", "cod_judet": None}
    er = bilant_api.erori_generare(p)
    assert len([e for e in er if "Județul firmei lipsește" in e]) == 1, er   # codTT „DA” -> lipsa oprește bilanțul, numită
    assert bilant_api.camp_lipsa(p) == "df-judet"                            # refuzul aduce în vedere câmpul „Județul” din Date firmă


# ── pe bază: schemă efemeră, generarea completă până la XML, ROLLBACK ────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_SCHEMA = "ztest_c69_d406_antet"


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
                # firma fără telefon (cazul contabilului): restul antetului e completat
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, declarant_nume, "
                            "declarant_prenume, declarant_functie, platitor_tva, tip_decont, regim_fiscal, baza_contabila) VALUES "
                            "(1, 'FIRMA C69 SRL', '14399840', 'Str. Probei 9', 'Cluj-Napoca', 'CJ', '6920', 'BT', %s, 'POPESCU', "
                            "'ION', 'ADMINISTRATOR', true, 'L', 'real', 'IFRS')", (IBAN,))
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D406_pe_baza_refuza_fara_telefon_apoi_iese_cu_datele_firmei(conn):
    with pytest.raises(ValueError) as ei:
        d406.genereaza(conn, _SCHEMA, 2026, 6)
    # S.CTH.2 Telephone „Mandatory” — refuzul numește câmpul și locul lui pe ecran
    assert re.findall(r"Lipsă (\w+ \w+): D406 îl cere obligatoriu în antetul fișierului \(datele de contact ale firmei\)\. Completează „(\w+)” "
                      r"în Date firmă", str(ei.value)) == [("telefonul firmei", "Telefon")], str(ei.value)
    # refuzul trimite la ecranul unde se repară (butonul „Date firmă”, câmpul Telefon adus în vedere — `RefuzGenerare`, 431)
    assert ei.value.detaliu()["ecran"] == "date_firma" and ei.value.detaliu()["camp_ecran"] == "df-telefon", ei.value.detaliu()
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET telefon = '0264111222' WHERE id = 1")
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 6)
    assert _texte(xml, "Telephone") == ["0264111222"]          # S.CTH.2 — telefonul firmei, citit din Date firmă (repo_d406)
    assert _texte(xml, "IBANNumber") == [IBAN]                  # S.BA.1 — IBAN-ul firmei (era RO00BANK0000000000000000)
    assert (_texte(xml, "FirstName"), _texte(xml, "LastName")) == (["ION"], ["POPESCU"])   # S.PN.2 / S.PN.5 — declarantul
    assert _texte(xml, "City") == ["Cluj-Napoca"]               # S.AD.5
    assert _texte(xml, "PostalCode") == []                      # S.AD.6 opțional, lipsă => omis
    # H.2 TaxAccountingBasis „Mandatory … Valorile din enumerarea A, I, IFRS …” — norma firmei, nu „A” implicit (select-ul n-o aducea)
    assert _texte(xml, "TaxAccountingBasis") == ["IFRS"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D406_cu_antetul_firmei_e_valid_pe_DUK(conn):
    """Validatorul oficial (DUKIntegrator_AnLunaUI) e judecătorul final (CLAUDE.md, REGULA DE AUR)."""
    from core import duk
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET telefon = '0264111222', baza_contabila = 'A' WHERE id = 1")
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 6)
    v = duk.valideaza(xml, "d406", an=2026, luna=6)
    if v.get("stare") == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", v


def test_D300_caen_lipsa_opreste_si_nu_se_inventeaza_0():
    """[lotul 10, C69] `d300.build_xml` scria `caen="0"` când lipsea CAEN-ul. Pe drumul `genereaza` era inaccesibil (CAEN-ul lipsă /
    altul decât 4 cifre e refuzat de `erori_generare`), deci fallback-ul era cod mort — scos, ca nici chemat direct să nu inventeze."""
    from core import d300
    from core.common import Perioada
    p = {"declarant_nume": "Popescu", "declarant_prenume": "Ion", "declarant_functie": "ADMINISTRATOR", "cui": "14399840",
         "nume": "PROBA SRL", "banca": "ING", "iban": IBAN, "platitor_tva": True, "tip_decont": "L", "adresa": "Str. 1"}
    er = d300.erori_generare(p)
    assert len(er) == 1 and "Lipsă CAEN" in er[0], er         # structura ANAF D300 „17. caen Cod CAEN C(4) DA” — lipsa oprește D300
    xml = d300.build_xml(d300.calcul_d300(p, Perioada(2099, luna=1), [], None, None))
    assert ET.fromstring(xml.encode("utf-8")).get("caen") == ""   # niciun cod CAEN inventat pe declarație (era „0”)


def test_D710_fara_declarant_se_opreste_nu_scrie_ADMINISTRATOR():
    """[lotul 10, C69] D710 „completa” declarantul lipsă cu „ADMINISTRATOR” / „-”. Structura D100-D710
    (anaf_surse/structura_D100-D710_0126_140926.txt): „nume_declar … DA … ERR - Nume declarant necompletat”, „prenume_declar … DA”,
    „functie_declar … DA”; DUK, pe atributul gol: „functie_declar: atribut prezent dar vid nepermis” (proba din raport)."""
    from core import d710
    p = {"cui": "14399840", "nume": "T SRL", "adresa": "Str. Testului nr. 1"}
    er, asteptate = d710.erori_generare(p), fp.erori_declarant(p)
    assert len(asteptate) == 3, asteptate                            # nume, prenume, funcție — toate trei „DA” în structură
    assert [e for e in er if e in asteptate] == asteptate, er        # D710 le refuză pe toate trei, din sursa unică `erori_declarant`
    assert set(fp.OBLIGATORII["declarant_functie"]) >= {"D710"}     # panoul „Profil incomplet” o spune
    assert not d710.erori_generare(dict(p, declarant_nume="POPESCU", declarant_prenume="ION", declarant_functie="ADMINISTRATOR"))
