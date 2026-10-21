# -*- coding: utf-8 -*-
"""Lotul 10, decizia Costin A (verbatim în DECIZII, „Lotul 10: deciziile lui Costin la întrebările din lot”): „Varianta 2: D205 include
și dividendele distribuite neplătite la 31.12, pe anul distribuirii, cu impozitul datorat (Cap. V are rânduri separate distribuite /
plătite). Încadrarea pe câmpuri o iei din instrucțiunile oficiale de completare D205 și o verifici pe DUKIntegrator.”

Temei (citat pe linie lângă assert):
  · OPANAF 179/2022 anexa 1, instrucțiunile D205, cap.II pct.9 (`anaf_surse/opanaf_179_2022_d205_d207_baza.txt`):
    „Col. 3 - se înscrie, pe fiecare beneficiar de venit, suma reprezentând totalul venitului distribuit din dividende, într-un an
    fiscal. Col. 4 - [...] totalul venitului plătit acţionarilor sau asociaţilor din dividendele distribuite, într-un an fiscal. Col. 5
    - [...] baza de calcul al impozitului, într-un an fiscal. Col. 6 - [...] totalul impozitului pe venit calculat şi reţinut în cursul
    anului. Impozitul aferent dividendelor distribuite, dar care nu au fost plătite acţionarilor sau asociaţilor până la sfârşitul
    anului în care s-a aprobat distribuirea acestora se cuprinde în declaraţia aferentă perioadei în care s-a aprobat distribuirea
    dividendelor.”
  · CF art.97 alin.(7): „În cazul dividendelor [...] distribuite, dar care nu au fost plătite acționarilor/asociaților/investitorilor
    până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data de 25
    ianuarie inclusiv a anului următor distribuirii.”
  · Coloanele în XML: divid_D = col.3 (7.V), divid_P = col.4 (8.V), baza1 / imp1 (structura ANAF `anaf_surse/d205_struct_anaf.txt`
    rd.39.a / 39.b / 44 / 45); validatorul DUK D205 v8 cere numai >= 0 pe fiecare (R39a, R39b, R44, R45).
CNP-uri sintetice cu cifra de control verificată (algoritmul din CLAUDE.md): 1800101400016, 2850202400023; CUI 14399840 (verificat)."""
import datetime
import io
import os
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from core import db as _db
from core import dividende_curs as dc
from core import tenant_provisioning as _tprov
from core.common import Perioada

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot10_d205_neplatite"
R = lambda d: Decimal("0.10") if d.year == 2025 else Decimal("0.16")   # noqa: E731 — cota după data distribuirii (Legea 141/2025 art.VII)


def _m(data, **k):
    return dict({"data": datetime.date(*data)}, **k)


# ── atribuirea pe an (pur) ────────────────────────────────────────────────────────────────────────────────────────────────────
def test_distribuit_neplatit_la_31_12_intra_cu_impozitul_in_anul_distribuirii():
    m = [_m((2026, 5, 20), distribuit=10000, impozit=1600)]
    imp, platit, dist = dc.impozit_ponderat(m, 2026, R)
    # OPANAF 179/2022 cap.II pct.9: impozitul dividendelor distribuite și neplătite la sfârșitul anului „se cuprinde în declaraţia
    # aferentă perioadei în care s-a aprobat distribuirea dividendelor” -> baza (= distribuit) și impozitul pe 2026, plătit 0
    assert (imp, platit, dist) == (Decimal("1600.00"), 0, 10000)


def test_distribuit_intr_un_an_platit_in_urmatorul_nu_se_declara_de_doua_ori():
    m = [_m((2025, 12, 20), distribuit=50000), _m((2026, 1, 15), platit=50000)]
    # anul distribuirii: baza și impozitul cu cota lui (10% în 2025, Legea 141/2025 art.VII), nimic plătit
    assert dc.impozit_ponderat(m, 2025, R) == (Decimal("5000.00"), 0, 50000)
    # anul plății: col.4 „totalul venitului plătit [...] într-un an fiscal” = 50.000; baza și impozitul 0 — declarate deja în 2025
    assert dc.impozit_ponderat(m, 2026, R) == (0, 50000, 0)


def test_platit_in_acelasi_an_ramane_ca_inainte():
    m = [_m((2026, 5, 20), distribuit=10000, impozit=1600), _m((2026, 6, 10), platit=8400)]
    # brutul plătit = netul 8.400 + impozitul reținut 1.600; baza = distribuitul anului = 10.000
    assert dc.impozit_ponderat(m, 2026, R) == (Decimal("1600.00"), Decimal("10000"), 10000)


def test_sold_de_deschidere_457_platit_dupa_preluare_e_numai_platit():
    """Generalizarea pe clasă: soldul creditor 457 din balanța de deschidere e un dividend distribuit înainte de evidență; baza și
    impozitul lui sunt în declarația anului distribuirii (depusă înainte de preluare). Fără el, plata ieșea distribuire nouă, impozitată
    a doua oară (16% pe 20.000 = 3.200)."""
    m = [_m((2025, 12, 31), preluat=20000), _m((2026, 3, 1), platit=20000)]
    assert dc.impozit_ponderat(m, 2026, R) == (0, 20000, 0)


def test_plata_fara_distribuire_in_registru_e_distribuire_si_plata_a_zilei_ei():
    """O plată fără distribuire deschisă (inconsecvență de registru) se atribuie propriei date — conservator, nu se pierde."""
    assert dc.impozit_ponderat([_m((2026, 4, 10), platit=5000)], 2026, R) == (Decimal("800.00"), 5000, 5000)


def test_pe_asociati_impozitul_e_pe_distribuit():
    struct = dc.structura_la([("A", "1800101400016", 60), ("B", "2850202400023", 40)], [])
    pe = dc.atribuie_pe_asociati([_m((2026, 5, 20), distribuit=10000)], 2026, R, struct)
    assert {k: (v["distribuit"], v["platit"], v["impozit"]) for k, v in pe.items()} == {
        "1800101400016": (Decimal("6000"), 0, Decimal("960.00")), "2850202400023": (Decimal("4000"), 0, Decimal("640.00"))}


# ── generarea pe schemă efemeră, cu DUK ───────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def firma():
    """Firmă în schemă EFEMERĂ (nicio tabelă `public.*` scrisă), 2 asociați 60 / 40, declarantul complet."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1, 'DIVIDENDE TEST SRL', '14399840', 'Str. Test 1, Bucuresti', 'POPESCU', 'ION', 'ADMINISTRATOR')")
        cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('POPESCU ION', '1800101400016', 60), ('IONESCU MARIA', '2850202400023', 40)")
        c.commit()
    yield SCH
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _sql(q, a=()):
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, a)
        c.commit()
        return cur.fetchall() if cur.description else None


def _nota(data, linii):
    nid = _sql("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'dividende', 'operatiuni', 'ciorna', "
               "'Hotărârea AGA nr 3') "
               "RETURNING id", (data,))[0][0]
    for d, c, s in linii:
        _sql("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))
    _sql("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))


def _genereaza(an):
    from core import d205
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        return d205.genereaza(c, SCH, Perioada(an))


def _randuri(res):
    return [(b.nume1, b.divid_d, b.divid_p, b.baza1, b.imp1) for b in res.beneficiari]


def _duk_valid(xml, an):
    from core import duk
    if not duk.poate_valida("d205"):
        pytest.skip("validatorul DUK D205 nu e instalat")
    v = duk.valideaza(xml, "d205", an=an)
    assert v["stare"] == "valid", v


def test_431_d205_cuprinde_dividendele_neplatite_la_31_12(firma):
    _nota("2026-05-20", [("117", "457", 10000), ("457", "446", 1600)])   # „Dividendul se plătește acum: Nu” — neplătit la 31.12
    xml, res = _genereaza(2026)
    # OPANAF 179/2022 cap.II pct.9: col.3 distribuit 6.000 / 4.000, col.4 plătit 0, col.5-6 baza și impozitul (16%, CF art.97 alin.(7))
    assert _randuri(res) == [("POPESCU ION", 6000, 0, 6000, 960), ("IONESCU MARIA", 4000, 0, 4000, 640)]
    # aceleași cifre în XML-ul depus: atributele elementelor `benef`, citite din XML parsat (nu din text)
    benef = [el.attrib for el in ET.fromstring(xml).iter() if el.tag.rsplit("}", 1)[-1] == "benef"]
    assert [{k: b.get(k) for k in ("divid_D", "divid_P", "baza1", "imp1")} for b in benef] == [
        {"divid_D": "6000", "divid_P": "0", "baza1": "6000", "imp1": "960"},
        {"divid_D": "4000", "divid_P": "0", "baza1": "4000", "imp1": "640"}], benef
    _duk_valid(xml, 2026)


def test_distribuit_2025_platit_2026_d205_pe_ambii_ani_valid_la_duk(firma):
    _nota("2025-12-20", [("117", "457", 50000)])
    _nota("2026-01-15", [("457", "5121", 50000)])
    xml25, res25 = _genereaza(2025)
    # anul distribuirii: baza + impozitul cu cota de la data distribuirii (10%, Legea 141/2025 art.VII), plătit 0
    assert _randuri(res25) == [("POPESCU ION", 30000, 0, 30000, 3000), ("IONESCU MARIA", 20000, 0, 20000, 2000)]
    _duk_valid(xml25, 2025)
    xml26, res26 = _genereaza(2026)
    # anul plății: numai col.4 („plătit [...] într-un an fiscal”); baza și impozitul 0 — nu se declară de două ori
    assert _randuri(res26) == [("POPESCU ION", 0, 30000, 0, 0), ("IONESCU MARIA", 0, 20000, 0, 0)]
    _duk_valid(xml26, 2026)


def test_platit_in_acelasi_an_d205_ca_inainte(firma):
    _nota("2026-05-20", [("117", "457", 10000), ("457", "446", 1600)])
    _nota("2026-06-10", [("457", "5121", 8400)])
    xml, res = _genereaza(2026)
    assert _randuri(res) == [("POPESCU ION", 6000, 6000, 6000, 960), ("IONESCU MARIA", 4000, 4000, 4000, 640)]
    _duk_valid(xml, 2026)


def test_sold_de_deschidere_platit_dupa_preluare_numai_la_platite(firma):
    _sql("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES ('457', 0, 20000, '2025-12-31')")
    _nota("2026-03-01", [("457", "5121", 20000)])
    xml, res = _genereaza(2026)
    # distribuit înainte de preluare: impozitul lui e în D205 a anului distribuirii (cap.II pct.9) — aici numai plătit
    assert _randuri(res) == [("POPESCU ION", 0, 12000, 0, 0), ("IONESCU MARIA", 0, 8000, 0, 0)]
    _duk_valid(xml, 2026)


def test_calea_a_doua_si_controlul_cad_de_acord_pe_neplatite(firma):
    from core import control_incrucisat, d205_reconciliere
    _nota("2025-12-20", [("117", "457", 50000)])
    _nota("2026-01-15", [("457", "5121", 30000)])
    _nota("2026-07-01", [("117", "457", 10000)])
    for an in (2025, 2026):
        _xml, res = _genereaza(an)
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            assert d205_reconciliere.reconciliaza(c, SCH, Perioada(an), res)["divergente"] == []
            assert control_incrucisat._thunk_d205(c, SCH, an, 12)()["divergente"] == []
    # 2026: distribuit 10.000 (neplătit) + plătit 30.000 din distribuirea 2025
    assert _randuri(res) == [("POPESCU ION", 6000, 18000, 6000, 960), ("IONESCU MARIA", 4000, 12000, 4000, 640)]


def test_calea_a_doua_prinde_baza_pusa_pe_platit(firma):
    """Calea a doua NU e tautologică: dacă generatorul ar pune baza pe plătit (regula veche), divergența se numește."""
    from core import d205_reconciliere
    _nota("2026-05-20", [("117", "457", 10000), ("457", "446", 1600)])
    _xml, res = _genereaza(2026)
    for b in res.beneficiari:
        b.baza1, b.imp1 = b.divid_p, 0
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        div = d205_reconciliere.reconciliaza(c, SCH, Perioada(2026), res)["divergente"]
    assert {(d["camp"], d["cale2"]) for d in div} == {("baza", 6000), ("impozit", 960), ("baza", 4000), ("impozit", 640)}, div


def test_calea_a_doua_prinde_platitul_gresit(firma):
    """divid_P (col.4) e acum separat de bază: calea a doua îl confruntă și pe el (un plătit greșit nu trece de poartă)."""
    from core import d205_reconciliere
    _nota("2025-12-20", [("117", "457", 50000)])
    _nota("2026-01-15", [("457", "5121", 50000)])
    _xml, res = _genereaza(2026)
    res.beneficiari[0].divid_p = 0
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        div = d205_reconciliere.reconciliaza(c, SCH, Perioada(2026), res)["divergente"]
    assert [(d["camp"], d["generator"], d["cale2"]) for d in div] == [("dividende plătite", 0, 30000)], div


def test_control_fiscal_d205_datorat_pe_distribuirea_neplatita(firma):
    from core import control_incrucisat
    _nota("2026-05-20", [("117", "457", 10000), ("457", "446", 1600)])
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        fapt, are_note = control_incrucisat.dividende_distribuite(c, SCH, 2026)
    # decizia A: distribuirea neplătită face D205 datorat pe anul ei (înainte: numai debitul 457 — nedatorată)
    assert (fapt["fel"], fapt["tip"], fapt["an"], are_note) == ("fapt", "d205", 2026, True)
    assert fapt["motiv"] == "dividende distribuite în 2026 (10.000,00 lei)", fapt


def test_431_mesajul_vechi_al_neplatitelor_nu_mai_exista():
    """Decizia A supersedează refuzul „dividendele distribuite [...] nu sunt plătite”: textul nu mai e în generator."""
    src = io.open(os.path.join(RAD, "core", "d205.py"), encoding="utf-8").read()
    assert "nu sunt plătite în" not in src and "D205 cuprinde dividendele plătite" not in src
