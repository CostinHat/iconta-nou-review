# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 486] D406 pe luna L citește numai partenerii PERIOADEI L.

Ce era (core/d406.py `pull`): MasterFiles Customers / Suppliers = TOT nomenclatorul de clienți / furnizori (`SELECT … FROM clienti`, fără
perioadă), iar verificarea localității (`parteneri_fara_localitate`) îi cerea localitatea fiecăruia. Un client adăugat în octombrie, fără
localitate, oprea D406 pe septembrie („D406 nu se poate genera: lipsește localitatea pentru …”), deși nu apare în nicio factură sau notă
din septembrie. La fel un cod fiscal greșit în nomenclator (ValueError din `_partener_id_saft`) oprea orice lună.

Temei (anaf_surse/opanaf_1783_2021_saft_d406.txt): OPANAF 1783/2021 anexa 3 pct.11 „până când toate informaţiile aferente perioadei de
raportat sunt transmise”; pct.27 „în cazul în care într-o perioadă de raportare, pentru o anumită secţiune sau subsecţiune,
contribuabilul/plătitorul nu are date noi de raportat, prin comparaţie cu ce a raportat deja în perioada anterioară, secţiunea sau
subsecţiunea respectivă poate fi lăsată vidă”; d406_schema_anaf.xlsx, „2. MasterFiles”, MF.C.1 / MF.S.1 cardinalitate 0..*. Judecătorul:
validatorul DUK D406 (`core/duk.py`).

Fixtura: schemă efemeră din tenant_template, ROLLBACK. CUI-uri cu cifra de control verificată (`test_fixtura_e_valida`): 14399840 (firma),
2864518 (client din septembrie), 1590082 (client adăugat în octombrie), 361757 (furnizor fără fișă în nomenclator).
"""
import io
import xml.etree.ElementTree as ET

import pytest

from core import d406
from core.erori import RefuzGenerare

_SCHEMA = "ztest_lot12_decl_486"
IBAN = "RO59BTRLRONCRT0C69TEST01"


def _texte(xml, tag, sectiune):
    rad = ET.fromstring(xml.encode("utf-8"))
    local = lambda e: e.tag.rsplit("}", 1)[-1]   # noqa: E731
    return [e.text or "" for s in rad.iter() if local(s) == sectiune for e in s.iter() if local(e) == tag]


def test_fixtura_e_valida():
    from core.identitate import valideaza_cui
    from core.salariati_api import iban_valid
    assert all(valideaza_cui(c)[0] for c in ("14399840", "2864518", "1590082", "361757")) and iban_valid(IBAN)
    assert not valideaza_cui("14399841")[0]   # codul greșit din nomenclator (cifra de control)


def test_masterfiles_ia_numai_partenerii_perioadei():
    """`parteneri_perioadei_master`: din nomenclator rămân numai cei de pe documentele perioadei; cel de pe document fără fișă se adaugă."""
    nom = [d406.Partener(id="002864518", nume="ALTEX ROMANIA SRL", cui="2864518", oras="Voluntari"),
           d406.Partener(id="001590082", nume="BETA OCTOMBRIE SRL", cui="1590082")]
    out = d406.parteneri_perioadei_master(nom, {"002864518": ("ALTEX ROMANIA SRL", "2864518"), "00361757": ("GAMA SRL", "361757")})
    assert [(p.id, p.oras) for p in out] == [("002864518", "Voluntari"), ("00361757", "")]   # OPANAF 1783/2021 anexa 3 pct.11, pct.27


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


def _factura(cur, nr, data, dir_, cui, nume, oras):
    cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_cui, tert_nume, tert_oras, status) "
                "VALUES (%s, %s, %s, 121, 21, %s, %s, %s, %s) RETURNING id", (nr, data, dir_, cui, nume, oras, dir_))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) "
                "VALUES (%s, 'Marfa', 'buc', 1, 100, 21)", (fid,))


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
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, telefon, declarant_nume, "
                            "declarant_prenume, declarant_functie, platitor_tva, tip_decont, regim_fiscal, baza_contabila) VALUES "
                            "(1, 'FIRMA 486 SRL', '14399840', 'Str. Probei 9', 'Cluj-Napoca', 'CJ', '4690', 'BT', %s, '0264111222', "
                            "'POPESCU', 'ION', 'ADMINISTRATOR', true, 'L', 'real', 'A')", (IBAN,))
                # nomenclatorul: clientul din septembrie (cu localitate), clientul adăugat în octombrie (fără), un cod greșit
                cur.execute("INSERT INTO clienti (nume, cui, oras) VALUES ('ALTEX ROMANIA SRL', '2864518', 'Voluntari'), "
                            "('BETA OCTOMBRIE SRL', '1590082', NULL), ('GRESIT SRL', '14399841', NULL)")
                _factura(cur, "FV9", "2026-09-10", "emisa", "RO2864518", "ALTEX ROMANIA SRL", None)
                _factura(cur, "FC9", "2026-09-12", "primita", "361757", "GAMA SRL", "Brasov")   # furnizor fără fișă în nomenclator
                _factura(cur, "FV10", "2026-10-05", "emisa", "1590082", "BETA OCTOMBRIE SRL", None)
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_486_septembrie_nu_e_oprit_de_partenerul_din_octombrie(conn):
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 9)   # era: RefuzGenerare „lipsește localitatea pentru … BETA OCTOMBRIE SRL”
    assert _texte(xml, "Name", "Customers") == ["ALTEX ROMANIA SRL"]   # OPANAF 1783/2021 anexa 3 pct.11: datele perioadei de raportat
    assert _texte(xml, "City", "Customers") == ["Voluntari"]           # localitatea din fișă (S.AD.5 City „Mandatory”)
    assert _texte(xml, "Name", "Suppliers") == ["GAMA SRL"]            # partenerul facturii perioadei, și fără fișă în nomenclator
    assert "BETA" not in xml and "GRESIT" not in xml


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_486_octombrie_cere_in_continuare_localitatea_partenerului_lui(conn, monkeypatch):
    lipsa, parteneri_fara_localitate = [], d406.parteneri_fara_localitate
    monkeypatch.setattr(d406, "parteneri_fara_localitate", lambda *a: lipsa.append(parteneri_fara_localitate(*a)) or lipsa[-1])
    with pytest.raises(RefuzGenerare) as ei:
        d406.genereaza(conn, _SCHEMA, 2026, 10)
    m = str(ei.value)
    # S.AD.5 City „Mandatory” — numai partenerii lunii: refuzul numește exact partenerul din octombrie, cu factura lui (nu ALTEX)
    assert [[(nume, facturi) for nume, _pid, facturi in x] for x in lipsa] == [[("BETA OCTOMBRIE SRL", ["FV10"])]], lipsa
    assert m.split(". ")[1] == "BETA OCTOMBRIE SRL (facturile FV10)" and "ALTEX" not in m, m   # propoziția cu lista partenerilor


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_486_septembrie_e_valid_pe_duk(conn):
    from core import duk
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 9)
    v = duk.valideaza(xml, "d406", an=2026, luna=9)
    if v.get("stare") == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", v   # DUK D406 — judecătorul final


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_486_profil_minim_fara_niciun_partener_e_valid_pe_duk(conn):
    """Profil minim construit manual: luna fără documente (august) — Customers / Suppliers goale, nomenclatorul plin nu contează."""
    from core import duk
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 8)
    assert _texte(xml, "Name", "Customers") == [] and _texte(xml, "Name", "Suppliers") == []   # MF.C.1 / MF.S.1 0..*
    v = duk.valideaza(xml, "d406", an=2026, luna=8)
    if v.get("stare") == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", v
