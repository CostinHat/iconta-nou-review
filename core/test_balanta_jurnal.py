# -*- coding: utf-8 -*-
"""[08.10.2026, decizia Costin W1, verbatim în DECIZII] Balanța nu poate conține ce jurnalul nu arată.

„Jurnalul și balanța trebuie să arate aceleași note pentru același utilizator; dacă dreptul ascunde unele note, jurnalul spune
asta explicit, iar balanța nu poate conține ce jurnalul nu arată.”

MĂSURAT pe F2 (tenant_050) 10/2026, înainte: registrul-jurnal pe octombrie 0 note, balanța pe octombrie „rulaje” 7.750 — notele
de septembrie, fiindcă `rul_*` aduna tot ce era înainte de sfârșitul lunii, fără limită de jos. Drepturile nu ascundeau nimic:
niciun cititor nu primește utilizatorul.

Temei: OMFP 2634/2015 anexa 2, Balanța de verificare (cod 14-6-30/a) — „soldurile inițiale debitoare și creditoare; totalul
sumelor debitoare și creditoare ale lunii precedente, după caz; rulajele curente debitoare și creditoare; … totalul sumelor
debitoare și creditoare; soldurile finale”.
"""
import inspect
import io
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import db as _db  # noqa: E402
from core import documente_api as _doc  # noqa: E402
from core import repo_contabilitate as _repo  # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402

SCH = "ztest_w1_balanta"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


@pytest.fixture
def schema_doua_luni():
    """Sold inițial 5311 D 1.000 / 1012 C 1.000; o notă în 2099-09 (4111=704 600), două în 2099-10 (5311=4111 250, 401=5311 40)."""
    sablon = io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(sablon, SCH))
            cur.execute(f"INSERT INTO {SCH}.solduri_initiale (cont, denumire, sold_debitor, sold_creditor) VALUES "
                        "('5311', 'Casa', 1000, 0), ('1012', 'Capital', 0, 1000)")
            for data, deb, cre, suma in (("2099-09-20", "4111", "704", 600), ("2099-10-02", "5311", "4111", 250),
                                         ("2099-10-15", "401", "5311", 40)):
                cur.execute(f"INSERT INTO {SCH}.inregistrari (data, numar, descriere, status, sursa) VALUES "
                            "(%s, 'W1', 'proba W1', 'validata', 'manual') RETURNING id", (data,))
                cur.execute(f"INSERT INTO {SCH}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s, %s, %s, %s)", (cur.fetchone()[0], deb, cre, suma))
        conn.commit()
        try:
            yield conn
        finally:
            conn.rollback()
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            conn.commit()


def _jurnal_luna(conn, an, luna):
    with conn.cursor() as cur:
        return _repo.jurnal_pe_an(cur, SCH, "%d-01-01" % an, "%d-%02d-01" % (an, luna))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_rulajele_lunii_sunt_exact_notele_din_jurnalul_lunii(schema_doua_luni):
    conn = schema_doua_luni
    for luna in (9, 10, 11):
        bal = _doc.balanta(conn, SCH, 2099, luna)
        jur = _jurnal_luna(conn, 2099, luna)
        tot = _doc.totaluri_balanta(bal)
        # OMFP 2634/2015 anexa 2 cod 14-6-30/a: „rulajele curente” = operațiunile lunii, adică registrul-jurnal al lunii
        assert tot["rul_d"] == tot["rul_c"] == round(sum(float(r[15]) for r in jur), 2), (luna, tot, len(jur))
        assert _doc.note_lunii(conn, SCH, 2099, luna) == len({r[0] for r in jur})
    # octombrie: 2 note (290); noiembrie: 0 note -> rulaj 0, nu 890 (cazul F2)
    assert _doc.totaluri_balanta(_doc.balanta(conn, SCH, 2099, 11))["rul_d"] == 0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cinci_egalitati_si_sold_final_neschimbat(schema_doua_luni):
    conn = schema_doua_luni
    bal = {r["cont"]: r for r in _doc.balanta(conn, SCH, 2099, 10)}
    # OMFP 2634/2015 anexa 2: „totalul sumelor … ale lunii precedente” — septembrie stă în sume precedente, nu în rulajul lui octombrie
    assert (bal["4111"]["prec_d"], bal["4111"]["rul_c"], bal["4111"]["sf_d"]) == (600, 250, 350)
    # „soldurile inițiale” — soldul introdus, neatins de note
    assert (bal["5311"]["si_d"], bal["5311"]["rul_d"], bal["5311"]["rul_c"], bal["5311"]["tot_d"], bal["5311"]["sf_d"]) == (
        1000, 250, 40, 1250, 1210)
    inc = _doc.inchidere_balanta(list(bal.values()))
    assert inc["stare"] == "se_inchide" and [p["ce"] for p in inc["perechi"]] == [
        "sold inițial", "sume precedente", "rulaje curente", "total sume", "sold final"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_notele_anilor_anteriori_intra_in_soldul_de_la_1_ianuarie(schema_doua_luni):
    conn = schema_doua_luni
    bal = {r["cont"]: r for r in _doc.balanta(conn, SCH, 2100, 1)}
    # OMFP 2634/2015 anexa 2: „Balanța de verificare la 1 ianuarie se completează cu soldurile finale … ale lunii decembrie a anului precedent”
    assert (bal["4111"]["si_d"], bal["4111"]["prec_d"], bal["4111"]["rul_d"]) == (350, 0, 0)
    assert (bal["5311"]["si_d"], bal["5311"]["si_c"]) == (1210, 0)
    assert _doc.inchidere_balanta(list(bal.values()))["stare"] == "se_inchide"


def test_niciun_cititor_nu_filtreaza_dupa_utilizator():
    """W1: „dacă dreptul ascunde unele note, jurnalul spune asta explicit”. Azi niciun drept nu ascunde note: cei doi cititori
    nu primesc utilizatorul. Cine adaugă un filtru pe utilizator la unul din ei cade aici — și trebuie să scrie atunci, în
    jurnal și în balanță, ce ascunde."""
    for f in (_doc.balanta, _repo.jurnal_pe_an, _doc.note_lunii):
        param = set(inspect.signature(f).parameters)
        assert not param & {"uid", "user_id", "utilizator", "ctx", "rol", "drepturi"}, (f.__name__, param)
