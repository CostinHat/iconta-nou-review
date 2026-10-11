# -*- coding: utf-8 -*-
"""GARD — deficiența 221 (comanda Costin 10.10.2026, verbatim în DECIZII): „Bilanț: coloana «An precedent» e copiată din anul curent
(grav, cifre greșite în declarație).” Cauza: `f10p` era soldul de preluare (`solduri_initiale`) oricare ar fi anul, iar pe anul
preluării coloana curentă ieșea tot din el (fără mișcări) — două coloane identice.

TEMEI: OMFP 1802/2014, Reglementări, pct.130 (forma consolidată din corpus, `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`):
„Pentru fiecare element de bilanţ … trebuie prezentată valoarea aferentă exerciţiului financiar la care se referă bilanţul … precum
şi valoarea aferentă elementului corespondent pentru exerciţiul financiar precedent.” Deci coloana 1 = soldul la 31.12 al anului
precedent; cunoscut numai de la data soldurilor de preluare încoace (`bilant_api.data_soldurilor` — luna preluării, decizia Costin
08.10.2026 §6 pct.4). Necunoscut -> nu se fabrică: coloana curentă necunoscută = refuz; cea precedentă = goală, cu avertisment.
Schemă efemeră din `tenant_template.sql`, ROLLBACK."""
import datetime
from decimal import Decimal

import pytest
from psycopg2.extras import RealDictCursor

from core import bilant_api as ba, db as _db, tenant_provisioning as _tp

_SCHEMA = "ztest_bilant_an_precedent"


@pytest.fixture
def cur():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                c.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                c.execute("SET search_path TO %s, public" % _SCHEMA)
                c.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'PROBA SRL', '14399840') ON CONFLICT (id) DO NOTHING")
                yield c
        finally:
            conn.rollback()


def _nota(c, zi, debit, credit, suma):
    c.execute("INSERT INTO inregistrari (data, status, sursa, descriere) VALUES (%s, 'validata', 't', 'Probă') RETURNING id", (zi,))
    c.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
              (c.fetchone()["id"], debit, credit, suma))


def test_coloana_precedenta_e_soldul_de_la_31_12_al_anului_precedent(cur):
    """Solduri de preluare la 31.12.2025 (5121 = 10.000), o încasare în 2026 (+2.000). Bilanțul 2026: an precedent 10.000, an curent
    12.000 — nu două coloane egale. MUTAȚIE: `coloanele_f10` întoarce soldul de preluare pe ambele coloane -> pică."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2025-12-31'), ('1012', 'Capital', 0, 10000, '2025-12-31')")
    _nota(cur, datetime.date(2026, 3, 10), "5121", "4111", Decimal("2000"))
    av = []
    f10p, f10c = ba.coloanele_f10(cur, _SCHEMA, 2026, av)
    assert f10p and f10c and f10p != f10c, (f10p, f10c)
    casa_p, casa_c = f10p.get(8), f10c.get(8)      # rd.08 „Casa și conturi la bănci” (F10, S1005)
    assert (casa_p, casa_c) == (10000, 12000), (casa_p, casa_c)
    assert not av, av


def test_anul_precedent_dinaintea_preluarii_nu_se_fabrica(cur):
    """Solduri de preluare la 31.08.2026: bilanțul 2026 are coloana curentă (soldul + mișcările de după), iar „An precedent” e gol, cu
    avertismentul care spune de ce; bilanțul 2025 se refuză (31.12.2025 e înainte de preluare). MUTAȚIE: verificarea `zi < ref` scoasă
    din `sold_la` -> 2025 se generează cu soldul de preluare -> pică."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2026-08-31'), ('1012', 'Capital', 0, 10000, '2026-08-31')")
    av = []
    f10p, f10c = ba.coloanele_f10(cur, _SCHEMA, 2026, av)
    assert f10p == {} and f10c.get(8) == 10000, (f10p, f10c)
    assert len(av) == 1 and "An precedent" in av[0] and "31.08.2026" in av[0], av
    with pytest.raises(ValueError, match="nu se poate întocmi"):
        ba.coloanele_f10(cur, _SCHEMA, 2025, [])


def test_data_soldurilor_vine_din_luna_preluarii_cand_lipseste(cur):
    """Fără `data_referinta`: soldurile sunt la ziua dinaintea lunii preluării (aceeași regulă ca Date firmă / Control fiscal). Luna
    salvată 09/2026 -> 31.08.2026."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor) VALUES ('5121', 'Banca', 500, 0)")
    cur.execute("UPDATE firma_profil SET luna_preluare = '2026-09-01' WHERE id = 1")
    assert ba.data_soldurilor(cur, _SCHEMA) == datetime.date(2026, 8, 31)
