# -*- coding: utf-8 -*-
"""[lotul 14, deficiența 694] „Declarație vs contabilitate”: fiecare comparație își arată perioada, iar la scadență compară perioada care se
depune (comanda Costin 14.1, verbatim: „F2, 26.10: nu se vede ce perioadă se compară — textul pomenește «fereastra TVA curentă (T4/2026)»,
adică o perioadă neîncheiată, chiar în ziua în care D300 T3/2026 e scadentă. Confirmat: D300 T3/2026 pe F2 dă 5.000 + 1.050 la 21%, TVA de
plată 1.050; controlul fiscal arăta 12.705 / 105 / 12.600, adică T4 în curs. Fiecare comparație își arată perioada, iar la scadență compară
perioada care se depune.”). Regula: perioada comparată = ultima perioadă fiscală TVA COMPLETĂ până la luna confruntată (`perioada_comparata`):
lunar — luna; trimestrial — trimestrul încheiat. Corecte (neatinse): logica de reconciliere, doar notele validate, 4428 neexigibilă semnalată,
absența D300 depus tratată ca gri. MUTAȚII: pasul înapoi scos din `perioada_comparata` -> pică; `perioada` scoasă din rezultat -> pică.
Schemă efemeră din template (2099), ștearsă la ieșire."""
import io
import datetime
from decimal import Decimal

import pytest

from core import control_incrucisat as ci, db as _db, tenant_provisioning as _tp

SCH = "efemer_lot14_perioada"


def test_perioada_comparata_trimestrial_e_ultimul_trimestru_incheiat():
    """T: luna 9 -> T3 (încheiat); luna 10 și 11 (T4 în curs) -> tot T3; luna 12 -> T4; luna 1 din anul următor -> T4 al anului dinainte.
    Lunar: luna însăși. Anual: numai decembrie încheie anul."""
    assert ci.perioada_comparata("trimestrial", 2026, 9) == (2026, 9, "T3/2026")
    assert ci.perioada_comparata("trimestrial", 2026, 10) == (2026, 9, "T3/2026")      # octombrie: D300 T3 e cel care se depune
    assert ci.perioada_comparata("trimestrial", 2026, 11) == (2026, 9, "T3/2026")
    assert ci.perioada_comparata("trimestrial", 2026, 12) == (2026, 12, "T4/2026")
    assert ci.perioada_comparata("T", 2027, 1) == (2026, 12, "T4/2026")
    assert ci.perioada_comparata("T", 2027, 2) == (2026, 12, "T4/2026")
    assert ci.perioada_comparata("lunar", 2026, 10) == (2026, 10, "10/2026")
    assert ci.perioada_comparata(None, 2026, 10) == (2026, 10, "10/2026")               # tip necompletat: ca lunar, ca `_fereastra_tva`
    assert ci.perioada_comparata("anual", 2026, 11) == (2025, 12, "anul 2025")
    assert ci.perioada_comparata("anual", 2026, 12) == (2026, 12, "anul 2026")


@pytest.fixture()
def firma():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, tip_decont, banca, iban, caen, declarant_nume, declarant_prenume, "
                        "declarant_functie, adresa, judet, oras) VALUES (1, 'PERIOADA SRL', 'RO14399840', true, 'T', 'ING Bank', "
                        "'RO63INGB0000999910907330', '6202', 'Popescu', 'Ion', 'ADMINISTRATOR', 'Str. A 1', 'B', 'Bucuresti')" % SCH)
        c.commit()
    yield SCH
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _nota(cur, zi, d, c, s):
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'n', 'jurnal', 'validata', 'NC n') RETURNING id",
                (zi,))
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)", (cur.fetchone()[0], d, c, Decimal(s)))


def test_octombrie_compara_t3_nu_t4_in_curs(firma):
    """Firma trimestrială, 4427 / 4426 cu mișcări în T4 (octombrie: 12.705 colectată, 12.600 deductibilă) și nimic în T3: verificarea cerută pe
    luna 10 compară T3/2099 (coincide: 0 cu 0), nu T4 în curs (care ar arăta diferențe uriașe), își arată perioada și nu pomenește „fereastra TVA
    curentă”. MUTAȚIE: `perioada_comparata` fără pasul înapoi -> pică (diferențe pe T4)."""
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            _nota(cur, datetime.date(2099, 10, 12), "4111", "4427", "12705.00")
            _nota(cur, datetime.date(2099, 10, 13), "4426", "401", "12600.00")
        r = ci.verifica_tva(conn, SCH, 2099, 10)
        d = ci.verifica_d390(conn, SCH, 2099, 10)
        conn.rollback()
    assert (r["an"], r["luna"], r["perioada"]) == (2099, 9, "T3/2099"), r
    assert [c for c in r["constatari"] if c["contabil"] or c["declarat"]] == [], r["constatari"]      # T3 coincide (0 cu 0): nicio diferență; mișcările din T4 în curs nu intră în comparație
    assert (d["an"], d["luna"], d["perioada"]) == (2099, 9, "T3/2099"), d
