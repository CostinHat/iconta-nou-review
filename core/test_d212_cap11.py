# -*- coding: utf-8 -*-
"""D212 Etapa 2 — venit în sistem real cap-coadă: registrul RIP -> cap11 -> XML -> DUK (01.10.2026).

Fiecare rând al subsecțiunii I.1.1 urmează instrucțiunile de completare (OPANAF 2736/2025 pct.3.5.11),
limita de compensare a pierderii urmează CF art.118 alin.(4), iar codurile și DUK regula R4 urmează artefactele
OFICIALE ANAF (D212Validator.jar pachet v9 / Parameters_v7; D212Pdf.jar Pdf_v8). Asertiuni pe valori, pe
arborele XML (ElementTree) și pe verdictul DUK — nu pe șiruri din mesaje.
"""
import xml.etree.ElementTree as ET
import pytest

from core import d212
from core.common import Perioada

NSX = "{%s}" % d212.NS
CNP = "1800101221144"          # cifra de control verificata (algoritmul oficial); suma cifrelor = 25
ID = {"cif": CNP, "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}


def _cap11(xml):
    rad = ET.fromstring(xml.split("?>", 1)[1])
    return rad, rad.find(NSX + "cap11")


# ── randurile (pct.3.5.11) ──────────────────────────────────────────────────────────────────────────
def test_venit_net_rd3_rd7_fara_impozit_in_cap11():
    # rd.3 = rd.1 - rd.2 „numai daca venitul brut e mai mare"; rd.7 = rd.3 - rd.6; rd.8/rd.9 „nu se completeaza"
    c = d212.cap11_sistem_real(100000, 30000)
    assert (c["venit_net_anual"], c["venit_recalculat"]) == (70000, 70000)
    assert "pierdere" not in c and "impozit11" not in c and "venit_redus" not in c
    assert (c["categ_venit"], c["det_ven_net"], c["forma_org"]) == (1016, 1, 1)   # Pdf_v8: activ. indep./real/individual


@pytest.mark.parametrize("pp,comp,recalc", [
    (10000, 10000, 60000),     # rd.5 < 70% x rd.3 -> se compenseaza integral (pct.3.5.11 lit.c)
    (60000, 49000, 21000),     # rd.5 >= 70% x 70000 = 49000 -> plafonat (lit.d; CF art.118 alin.(4): „limita a 70%")
])
def test_pierderea_reportata_se_compenseaza_in_limita_70(pp, comp, recalc):
    # MUTATIE: PROCENT_COMPENSARE_PIERDERE 70 -> 80 -> 56000 in loc de 49000 -> pica
    c = d212.cap11_sistem_real(100000, 30000, pierdere_precedenta=pp)
    assert (c["pierdere_precedenta"], c["pierdere_compensata"], c["venit_recalculat"]) == (pp, comp, recalc)


def test_pierdere_rd4_si_impozit_zero():
    # rd.4 „numai daca cheltuielile deductibile sunt mai mari"; rd.9 = 0 „s-a inregistrat pierdere fiscala"
    # MUTATIE: scos `c["impozit11"] = 0` -> pica
    c = d212.cap11_sistem_real(20000, 30000, pierdere_precedenta=5000)
    assert (c["pierdere"], c["impozit11"], c["pierdere_precedenta"]) == (10000, 0, 5000)
    assert "venit_net_anual" not in c and "pierdere_compensata" not in c   # rd.6 doar cu venit net


def test_venit_net_zero_impozit_zero_fara_pierdere():
    c = d212.cap11_sistem_real(30000, 30000)
    assert c["impozit11"] == 0 and "pierdere" not in c and "venit_net_anual" not in c


def test_sume_negative_refuzate():
    with pytest.raises(ValueError):
        d212.cap11_sistem_real(-1, 0)


# ── DUK regula R4 (ValidatorCode.validateD212) ────────────────────────────────────────────────────────────────
def test_R4_totalPlata_A_e_MEREU_suma_cifrelor_CNP():
    # bytecode: cif de 13 cifre -> totalPlata_A == suma celor 13 cifre, oricare ar fi sumele de plata.
    # MUTATIE: forma veche (suma sumelor de plata) -> 21580 in loc de 25 -> pica
    assert d212.calcul_d212(dict(ID, sume_de_plata=[7000, 12150, 2430]))["totalPlata_A"] == 25
    assert d212.calcul_d212(dict(ID, totalPlata_A=21580))["totalPlata_A"] == 25


# ── nomenclator + XML ───────────────────────────────────────────────────────────────────────────────
def test_categoria_in_afara_nomenclatorului_e_refuzata():
    with pytest.raises(ValueError):
        d212.genereaza(None, None, Perioada(an=2025), dict(ID, cap11={"categ_venit": 1, "venit_brut": 1}))


def test_xml_cap11_si_bifa111():
    xml, r = d212.genereaza(None, None, Perioada(an=2025), dict(ID, cap11=d212.cap11_sistem_real(100000, 30000)))
    rad, c = _cap11(xml)
    assert c is not None and rad.get("bifa111") == "1"          # R7 + reciproca: I.1.1 completata
    assert (c.get("categ_venit"), c.get("venit_net_anual"), c.get("venit_recalculat")) == ("1016", "70000", "70000")
    assert rad.get("totalPlata_A") == "25"


def _duk():
    try:
        from core import duk
        return duk if duk.poate_valida("d212") else None
    except Exception:
        return None


@pytest.mark.parametrize("vb,cd,pp", [(100000, 30000, 60000), (20000, 30000, 0)])
def test_DUK_valid_pe_cap11_generat(vb, cd, pp):
    duk = _duk()
    if duk is None:
        pytest.skip("DUK indisponibil")
    xml, _ = d212.genereaza(None, None, Perioada(an=2025), dict(ID, cap11=d212.cap11_sistem_real(vb, cd, pp)))
    v = duk.valideaza(xml, "d212", an=2025, luna=12, timeout=120)
    assert v.get("stare") == "valid", v.get("erori")


# ── lantul RIP -> cap11 (baza efemera, ROLLBACK) ────────────────────────────────────────────────────
from core import db as _db, tenant_provisioning as _tp   # noqa: E402

_SCH = "ztest_d212_cap11"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_lant_RIP_cap11_din_operatiunile_VALIDATE():
    # incasari activitate 120000 + 5000 (ciorna, NU intra); plati deductibile 40000; plata limitata 3000 (NU intra)
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCH))
                for tip, cat, suma, st in (("incasare", "activitate", 120000, "validata"),
                                           ("incasare", "activitate", 5000, "ciorna"),
                                           ("plata", "cheltuiala_deductibila", 40000, "validata"),
                                           ("plata", "cheltuiala_limitata", 3000, "validata")):
                    cur.execute("INSERT INTO %s.rip_operatiuni (id,data_operatiune,tip,explicatie,suma,metoda,categorie,status) "
                                "VALUES (nextval('%s.rip_operatiuni_id_seq'),'2025-06-10',%%s,'proba',%%s,'banca',%%s,%%s)"
                                % (_SCH, _SCH), (tip, suma, cat, st))
            xml, r = d212.genereaza(c, _SCH, Perioada(an=2025), dict(ID, din_rip=True, pierdere_precedenta=100000))
            rad, cap = _cap11(xml)
            # 120000 - 40000 = 80000; compensat min(100000, 56000) = 56000; recalculat 24000
            assert (cap.get("venit_brut"), cap.get("chelt_deduc"), cap.get("venit_net_anual"),
                    cap.get("pierdere_compensata"), cap.get("venit_recalculat")) == \
                ("120000", "40000", "80000", "56000", "24000")
            assert rad.get("bifa111") == "1" and r.avertismente, "ciorna + cheltuiala limitata trebuie semnalate"
        finally:
            c.rollback()
