# -*- coding: utf-8 -*-
"""[lotul 13, zona comp — reparațiile finale înaintea porții] C15 pe interogările noi ale lotului 13, pe schemă efemeră (ROLLBACK).

Clasa C15 (`core/test_bilant_f30.py::test_c15_inchiderea_in_121_nu_e_rulaj_in_nicio_interogare_pe_clasele_6_7`): o interogare care adună
rulaje pe clasele 6 / 7 exclude închiderea în 121 — altfel, după închiderea lunii / anului, 709 închis (`121 = 709`, credit 709) umflă
veniturile. Lotul 13 (zona ops, deficiența 532) a adus `repo_operatiuni.venituri_70x` — cifra de afaceri a anului până la data notei de
sponsorizare, din care se calculează plafonul de 0,75% (`sponsorizari.plafon_credit`) — fără excludere: o firmă care închide lunar
conturile de venituri vedea cifra de afaceri mărită cu reducerile acordate (709) și plafonul de sponsorizare mai mare decât cel real.
"""
import io
import os
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core.test_lot12_emit_recurente import mediu as mediu_recurente  # noqa: F401 — fixture-ul firmei cu șabloane recurente (anulat la capăt)

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot13_comp_finale"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def cur():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as k:
            k.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            k.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            k.execute("SET search_path TO %s, public" % SCH)
            yield k
        c.rollback()


def _nota(cur, data, linii, status="validata"):
    cur.execute("INSERT INTO inregistrari (data, descriere, document_ref, status) VALUES (%s, 'proba C15', 'NC-C15', 'ciorna') RETURNING id", (data,))
    iid = cur.fetchone()[0]
    for d, c, s in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)", (iid, d, c, s))
    if status != "ciorna":
        cur.execute("UPDATE inregistrari SET status = %s WHERE id = %s", (status, iid))
    return iid


def test_c15_cifra_de_afaceri_a_sponsorizarii_nu_numara_inchiderea_lui_709(cur):
    """Vânzare 704 = 1.000; reducere acordată 709 = 100 (709 = 4111); închiderea lunii: 704 = 121 (1.000) și 121 = 709 (100). Rulajul
    creditor 70x fără închidere = 1.000 (vânzarea); cu închiderea, rândul `121 = 709` ar adăuga 100 -> 1.100.
    MUTAȚIE: excluderea `NOT LIKE '121…'` scoasă din `repo_operatiuni.venituri_70x` -> 1.100 -> pică."""
    from core import repo_operatiuni
    _nota(cur, "2026-03-10", [("4111", "704", Decimal("1000.00"))])
    _nota(cur, "2026-03-12", [("709", "4111", Decimal("100.00"))])
    _nota(cur, "2026-03-31", [("704", "121", Decimal("1000.00")), ("121", "709", Decimal("100.00"))])
    assert Decimal(str(repo_operatiuni.venituri_70x(cur, SCH, "2026-01-01", "2026-12-31"))) == Decimal("1000.00")   # [C15]


def test_252_factura_furnizorului_preluata_se_leaga_proforma_nu(cur):
    """[lotul 12, 252 — garda `test_lot12_p252_garda_cititori.py`] Cititorul nou al lotului 13 (506, `factura_primita_dupa_furnizor_si_numar`)
    spune ce face cu facturile preluate: factura deschisă preluată a furnizorului e în evidență (prin soldurile inițiale), deci operațiunea
    care ar înregistra-o din nou se leagă de ea; o proformă cu același număr nu e factură și nu oprește înregistrarea.
    MUTAȚIE: `clauza_tip_cu_incasare` scoasă din interogare -> proforma e luată drept factura existentă -> pică."""
    from core import repo_operatiuni
    cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tert_cui, tert_nume, tip) VALUES "
                "('PF-1', '2026-09-01', 'primita', 100, '31654471', 'Furnizor SA', 'proforma'), "
                "('UT-9', '2026-08-01', 'primita', 1210, 'RO31654471', 'Furnizor SA', 'preluata') RETURNING id")
    _proforma, preluata = [r[0] for r in cur.fetchall()]
    assert (repo_operatiuni.factura_primita_dupa_furnizor_si_numar(cur, SCH, "31654471", "PF-1"),
            repo_operatiuni.factura_primita_dupa_furnizor_si_numar(cur, SCH, "RO31654471", "ut-9")[0]) == (None, preluata)   # [252]


def test_680_cronul_trimite_in_spv_fara_nicio_conexiune_in_mana(mediu_recurente, monkeypatch):
    """[lotul 13, 680 — clasa P4 / P5: niciun efect extern (încărcarea în SPV, apelul la ANAF) cu o conexiune ținută] Factura emisă de
    cron pe un șablon cu „pleacă singură în SPV” se trimite DUPĂ ce emiterea s-a comis și conexiunea ei s-a închis: la apelul
    `efactura_trimitere.trimite` nicio conexiune nu e deschisă (scanerul P4: `core/test_tranzactii_clasificate.py`, locurile
    `efactura_send.valideaza` / `spv_conector.apel_anaf` / `anaf_api.valideaza_cui` din `core/p4_clasificare.EFECTE_EXTERNE`).
    MUTAȚIE: trimiterea mutată înapoi în bucla emiterii (cu conexiunea emiterii în mână) -> la apel e o conexiune deschisă -> pică."""
    import json as _json
    from core import db as _dbm, efactura_trimitere as _eft, facturi_recurente as fr, spv_conector as _sc
    from core.test_lot12_emit_recurente import AZI, CUI_CLIENT, LINIE, _SCHEMA as SR
    deschise, la_trimitere = [0], []
    gc = _dbm.get_conn

    import contextlib

    @contextlib.contextmanager
    def _numarat(*a, **k):
        deschise[0] += 1
        try:
            with gc(*a, **k) as c:
                yield c
        finally:
            deschise[0] -= 1
    monkeypatch.setattr(_dbm, "get_conn", _numarat)
    monkeypatch.setattr(_sc, "principal_pentru_schema", lambda conn, schema: "principal-proba")
    monkeypatch.setattr(_eft, "trimite", lambda schema, fid, principal, mediu=None: la_trimitere.append((deschise[0], principal))
                        or {"stare": "incarcat"})
    with mediu_recurente.cursor() as k:
        k.execute("INSERT INTO %s.facturi_recurente (id, tert_nume, tert_cui, linii, zi_emitere, trimite_spv) VALUES (1, 'Client Recurent SRL', "
                  "%%s, %%s, 1, true)" % SR, (CUI_CLIENT, _json.dumps([LINIE])))
    e = fr.emite_scadente(SR, AZI)
    assert ([x.get("spv") for x in e if x.get("sablon") == 1], la_trimitere) == (["incarcat"], [(0, "principal-proba")]), (e, la_trimitere)
