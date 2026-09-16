# -*- coding: utf-8 -*-
"""R191 — amortizarea DECLARATA de registru, confruntata cu cea INREGISTRATA in conturile 28xx.

DE UNDE VINE. `CONFORMITATE.md` R191: *„amortizarea se calculeaza de DOUA ori, din surse diferite,
si nimic nu confrunta cifrele"*. Pentru D300 si D394 repo-ul are „a doua cale"; pentru sectiunea
**Assets** a D406 n-avea — iar `core/d406_reconciliere.py` isi declara asta ca limita, verbatim:
*„NU acopera sub-sectiunile … Assets"*.

MASURAT INAINTE DE A FI SCRISA garda (16.09.2026, portofoliul viu, tranzactie anulata): din 20 de
scheme, **trei conturi diverg** — t003 `2808` 666,72 declarat / 0,00 inregistrat · t003 `2813`
927,96 / 0,00 · t013 `2813` 3.500,00 / 2.600,00. *Perechea nu se naste ca precautie; se naste peste
o divergenta care exista.*

CE APARA, si de ce fiecare directie e o proba separata (METODA §22):
  * COINCIDENT -> verde. O pereche care nu poate spune „da" e o constanta, nu o masuratoare.
  * DIVERGENT  -> rosu, cu AMANDOUA valorile numite. Fara ele, constatarea n-ar fi verificabila.
  * CIORNA pe contul de amortizare -> GRI, nu rosu: diferenta se poate inchide la validarea ei,
    deci nu e o eroare constatata. E explicatia legitima ceruta de criteriul lui Costin, INCHISA
    in cod, nu lasata pe seama cititorului.
  * un activ pe care MOTORUL il refuza -> GRI: atunci stanga e INCOMPLETA, iar o comparatie pe o
    suma incompleta ar acuza evidenta pentru o lipsa a registrului.
  * cele doua griuri se deosebesc din DATE (`motiv_gri`), nu dupa un cuvant din mesaj.
  * NON-TAUTOLOGIE, pe AST: dreapta nu are voie sa vina din motorul care produce stanga.
  * forma R192: o ELIMINARE de reevaluare mai mare decat ce s-a inregistrat vreodata face soldul
    contului sa scada sub declarat — si perechea o prinde. *Comparatia cheltuielii anului n-ar
    vedea-o: eliminarea e un DEBIT, nu un credit al lui 6811.*
"""
from __future__ import annotations

import os
import sys
from datetime import date
from decimal import Decimal

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import control_incrucisat as _ci      # noqa: E402
from core import migrare_reevaluare as _mig     # noqa: E402
from core import supervizor as _S               # noqa: E402

SCH = "tenant_proba_r191"
AN = 2026

# Scenariul, DECLARAT: un activ de 6.000 lei, 60 de luni, liniar, PIF 15.12.2025.
#   rata = 100,00/luna · la 31.12.2026 au trecut 12 luni -> cumulat DECLARAT 1.200,00
VALOARE = Decimal("6000")
DNF = 60
PIF = date(2025, 12, 15)
CUMULAT = Decimal("1200.00")
CONT_AM = "2813"


def _db():
    try:
        from core import db
        db.init_pool()
        return db
    except Exception:
        return None


@pytest.fixture
def schema():
    db = _db()
    if not db:
        pytest.skip("fara db.env local")
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)
            c.execute('CREATE SCHEMA "%s"' % SCH)
            c.execute('CREATE TABLE "%s".mijloace_fixe (id integer GENERATED ALWAYS AS IDENTITY '
                      'PRIMARY KEY, cod text, denumire text NOT NULL, cont_imobilizare text, '
                      'cont_amortizare text, valoare numeric NOT NULL DEFAULT 0, rezidual numeric '
                      "DEFAULT 0, dnf_luni integer NOT NULL DEFAULT 12, data_pif date, metoda text "
                      "DEFAULT 'liniara', activ boolean DEFAULT true)" % SCH)
            c.execute('CREATE TABLE "%s".inregistrari (id integer GENERATED ALWAYS AS IDENTITY '
                      "PRIMARY KEY, data date NOT NULL, numar varchar(50), descriere text, "
                      "sursa text, status varchar(20) NOT NULL DEFAULT 'ciorna')" % SCH)
            c.execute('CREATE TABLE "%s".inregistrari_linii (id integer GENERATED ALWAYS AS '
                      "IDENTITY PRIMARY KEY, inregistrare_id integer NOT NULL, cont_debit text, "
                      "cont_credit text, suma numeric NOT NULL)" % SCH)
        _mig.aplica(conn, SCH)          # DDL-ul `reevaluari` din MIGRARE, nu rescris aici
        with conn.cursor() as c:
            c.execute('INSERT INTO "%s".mijloace_fixe (cod, denumire, cont_imobilizare, '
                      "cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda) "
                      "VALUES ('MF-R191','Utilaj proba R191','2131',%%s,%%s,0,%%s,%%s,'liniara')"
                      % SCH, (CONT_AM, VALOARE, DNF, PIF))
    try:
        yield db
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as c:
                c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)


def _nota(db, data_, linii, status="validata"):
    """O nota cu liniile ei. `linii` = [(debit, credit, suma)]."""
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO "%s".inregistrari (data, descriere, sursa, status) '
                      "VALUES (%%s,'proba','amortizare',%%s) RETURNING id" % SCH, (data_, status))
            iid = c.fetchone()[0]
            for dd, cc, ss in linii:
                c.execute('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, '
                          "cont_credit, suma) VALUES (%%s,%%s,%%s,%%s)" % SCH, (iid, dd, cc, ss))
            return iid


def _constatari(db):
    with db.get_conn() as conn:
        out = _ci.orizontal_d406_amortizare(conn, SCH, AN)
        conn.rollback()
    return out


def _una(db):
    cs = [c for c in _constatari(db) if c.get("cont") == CONT_AM or CONT_AM in str(c.get("eticheta"))]
    assert len(cs) == 1, "asteptam exact o constatare pe %s, am primit %d" % (CONT_AM, len(cs))
    return cs[0]


# ─────────────────────────── cele doua directii ───────────────────────────

def test_COINCIDENT_da_VERDE(schema):
    """Directia pe care o pereche stricata n-o poate da. *O pereche care nu poate spune „da" e o
    constanta, nu o masuratoare* (METODA §22, dus de la unitate la portofoliu)."""
    db = schema
    for luna in range(1, 13):
        _nota(db, date(AN, luna, 28), [("6811", CONT_AM, Decimal("100.00"))])
    c = _una(db)
    assert c["stare"] == "verde", c["mesaj"]
    assert c["declarat_registru"] == int(CUMULAT)
    assert c["inregistrat_contabil"] == int(CUMULAT)


def test_DIVERGENT_da_ROSU_si_NUMESTE_ambele_valori(schema):
    """O luna de amortizare neinregistrata. Constatarea trebuie sa poarta AMANDOUA cifrele —
    fara ele n-ar fi verificabila de nimeni."""
    db = schema
    for luna in range(1, 12):                       # unsprezece luni, nu douasprezece
        _nota(db, date(AN, luna, 28), [("6811", CONT_AM, Decimal("100.00"))])
    c = _una(db)
    assert c["stare"] == "rosu", c["mesaj"]
    assert c["declarat_registru"] == 1200
    assert c["inregistrat_contabil"] == 1100
    assert c["diferenta"] == 100
    # Pe CAMPURI, nu pe sirul mesajului: „numeste ambele valori" e o proprietate a STRUCTURII
    # constatarii. Un `"1.200,00" in mesaj` ar pazi formatarea, nu cifra (METODA §23).
    assert c["remediu"]["actiune"], "constatarea rosie n-are ce sa-i spuna omului"


def test_CIORNA_pe_cont_da_GRI_nu_ROSU(schema):
    """Explicatia legitima, INCHISA in cod. O nota nevalidata pe contul de amortizare poate inchide
    diferenta — deci nu se afirma o eroare, se spune ca verificarea asteapta."""
    db = schema
    for luna in range(1, 12):
        _nota(db, date(AN, luna, 28), [("6811", CONT_AM, Decimal("100.00"))])
    _nota(db, date(AN, 12, 28), [("6811", CONT_AM, Decimal("100.00"))], status="ciorna")
    c = _una(db)
    assert c["stare"] == "gri", c["mesaj"]
    assert c["motiv_gri"] == "ciorna_pe_cont", c


def test_MOTOR_care_REFUZA_un_activ_da_GRI_nu_ROSU(schema):
    """Stanga incompleta nu are voie sa acuze dreapta.

    Se strica un activ pe o cale pe care motorul o REFUZA prin lege, nu prin date lipsa: metoda
    `superaccelerata` pe un activ PIF 2025 (CF art.28 alin.8^1 cere PIF in 2026)."""
    db = schema
    for luna in range(1, 13):
        _nota(db, date(AN, luna, 28), [("6811", CONT_AM, Decimal("100.00"))])
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('UPDATE "%s".mijloace_fixe SET metoda=%%s' % SCH, ("superaccelerata",))
    c = _una(db)
    assert c["stare"] == "gri", c["mesaj"]
    assert c["motiv_gri"] == "registru_incomplet", c


def test_FORMA_R192_eliminarea_peste_ce_s_a_inregistrat_e_PRINSA(schema):
    """R192, ca formă: o reevaluare elimina din `28xx` mai mult decat s-a inregistrat vreodata.

    Perechea o prinde fiindca identitatea ei e CUMULATIVA. *Comparatia cheltuielii anului n-ar
    vedea-o: eliminarea e un DEBIT, nu un credit al lui 6811.*
    """
    db = schema
    for luna in range(1, 13):
        _nota(db, date(AN, luna, 28), [("6811", CONT_AM, Decimal("100.00"))])
    assert _una(db)["stare"] == "verde", "precondiția: inainte de eliminare cele doua coincid"
    # eliminare de 300 peste un sold de 1.200: contul scade la 900, registrul spune tot 1.200
    _nota(db, date(AN, 12, 30), [(CONT_AM, "2131", Decimal("300.00"))])
    c = _una(db)
    assert c["stare"] == "rosu", c["mesaj"]
    assert c["inregistrat_contabil"] == 900, c
    assert c["diferenta"] == 300


# ─────────────────────────── non-tautologie si vacuu ───────────────────────────

def test_NON_TAUTOLOGIE_dreapta_nu_vine_din_motorul_care_produce_stanga():
    """Pe ARBORE, nu pe text: functia care citeste evidenta nu are voie sa atinga `d406_active`.

    *O cale care isi ia cifra din cea pe care o verifica nu mai verifica nimic.*
    """
    import ast
    import inspect
    fn = ast.parse(inspect.getsource(_ci._amortizare_inregistrata))
    nume = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    nume |= {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
    # Operatorul de MULTIME, nu `in`: un `in` pe ceva ce ar deveni vreodata un sir s-ar transforma
    # tacut in sub-sir si ar arata identic. `>=` si `isdisjoint` CRAPA acolo. Forma o recomanda chiar
    # instrumentul care numara aserțiunile pe text (`core/scan_garzi_pe_text.py`, antet).
    interzise = {"d406_active", "_d406", "calc_asset", "amortizat_la_data", "amortizare_luna"}
    assert nume.isdisjoint(interzise), (
        "dreapta perechii atinge %s — tautologie" % sorted(nume & interzise))
    assert nume >= {"rulaje_interval"}, (
        "dreapta nu mai trece prin `rulaje_interval` — sursa unica de rulaje pe cont. "
        "Un SQL scris inca o data aici ar fi a doua definitie a aceleiasi citiri")


def test_ANTI_VACUU_perechea_chiar_citeste_AMANDOUA_partile(schema):
    """Un registru gol si o evidenta goala dau acelasi rezultat ca o pereche rupta: nimic."""
    db = schema
    for luna in range(1, 13):
        _nota(db, date(AN, luna, 28), [("6811", CONT_AM, Decimal("100.00"))])
    c = _una(db)
    assert c["declarat_registru"] > 0, "stanga a iesit 0 — nu mai citeste registrul"
    assert c["inregistrat_contabil"] > 0, "dreapta a iesit 0 — nu mai citeste evidenta"


def test_FIRMA_FARA_IMOBILIZARI_tace(schema):
    """Fara subiect nu se produce constatare — nici verde, nici gri. *Un verde pe o multime vida
    afirma mai mult decat s-a masurat.*"""
    db = schema
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DELETE FROM "%s".mijloace_fixe' % SCH)
    assert _constatari(db) == []


# ─────────────────────────── contractul cu supervizorul ───────────────────────────

def test_TIPUL_e_INREGISTRAT_si_FIECARE_constatare_il_poarta(schema):
    """O constatare fara tip ar fi sarita TACUT de supervizor, iar firma ar parea curata."""
    db = schema
    for luna in range(1, 12):
        _nota(db, date(AN, luna, 28), [("6811", CONT_AM, Decimal("100.00"))])
    cs = _constatari(db)
    assert cs, "anti-vacuu: perechea n-a produs nicio constatare pe care sa se verifice tipul"
    for c in cs:
        assert c.get("tip_constatare") == _ci.TIP_D406_ASSETS_VS_28X
    assert _ci.TIP_D406_ASSETS_VS_28X in _S.TIPURI


def test_TARIA_e_NEATRIBUITA_deci_NU_PRODUCE_NICIUN_EFECT():
    """Atribuirea tariei e a lui Costin, pe tip (`core/supervizor.py`, antet). Pana o da, tipul
    **se vede** dar nu cere confirmare — si NU cade pe o valoare implicita, fiindca *orice implicit
    minte*. Proba asta cade in ziua in care tipul primeste tarie: atunci se rescrie cu motivul."""
    t = _ci.TIP_D406_ASSETS_VS_28X
    assert _S.tarie(t) is None, (
        "tipul a primit tarie — rescrie proba asta si cere `motiv_tarie`, nu o lasa sa treaca")
    assert _S.cere_confirmare(t) is False
    assert _S.TIPURI[t].get("propus") in _S.TARII, "propunerea mea lipseste — raspunsul ar lua doua ture"
    assert (_S.TIPURI[t].get("motiv_propunere") or "").strip(), "propunere fara motiv scris"


def test_SUPERVIZORUL_CULEGE_perechea():
    """Cablul, pe ARBORE. Fara el, toate probele de mai sus ar ramane verzi peste o pereche pe care
    nimic n-o cheama — exact lectia gardului lui R59."""
    import ast
    import inspect
    fn = ast.parse(inspect.getsource(_S._culege_firma))
    apeluri = {n.func.attr for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert apeluri >= {"orizontal_d406_amortizare"}, (
        "supervizorul nu mai culege perechea R191 — cablul e taiat")
