# -*- coding: utf-8 -*-
"""309 + 310 — Bancă și Casă cu notele încă la validare (comanda Costin 17.10.2026 7.2, verbatim în DECIZII).

309: „linia contată arată «Contat ✓» cât nota e încă la validare; text «match exact pe o factura» (engleză, fără diacritice)”.
310: „F1A4 nu apare la facturile deschise din cauza încasării bancare aflate la validare, fără să se spună asta”.
Schemă efemeră din `tenant_template.sql`, an sintetic 2099. Temei: N/A — starea notei (OMFP 1802/2014: evidența = notele validate) nu se
schimbă aici; ecranul spune ce e.
"""
import io
import json

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

_SCH = "efemer_309"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()


@pytest.fixture()
def lume():
    if not _DB:
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
        c.rollback()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _incasare(cur, fid, status):
    cur.execute("INSERT INTO inregistrari (data, descriere, status, factura_id, document_ref) VALUES ('2099-10-16', 'incasare', %s, %s, "
                "'EXTRAS 1') RETURNING id", (status, fid))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5121', '4111', 242)", (nid,))
    return nid


def test_309_linia_contata_cu_nota_la_validare_si_motivul_vechi_pe_romaneste(lume):
    """MUTAȚIE: `stari.get(i) not in (None, "validata")` -> `False` -> linia apare „Contat ✓” -> pică."""
    from core import reconciliere_api as ra
    with lume.cursor() as cur:
        nid = _incasare(cur, None, "ciorna")
        cur.execute("INSERT INTO extras_linii (data, descriere, suma, tip, status, alocari) VALUES ('2099-10-16', 'CUI 14399840', 242, "
                    "'incasare', 'contat', %s)", (json.dumps({"motiv": "match exact pe o factura", "status_match": "verde",
                                                             "alocari": [], "inregistrari_ids": [nid]}),))
    (l,) = ra.lista(lume, '"%s"' % _SCH)
    assert l["note_de_validat"] == 1 and l["alocari"]["motiv"] == "potrivire exactă pe o factură", l
    with lume.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
    assert ra.lista(lume, '"%s"' % _SCH)[0]["note_de_validat"] == 0


def test_310_factura_stinsa_de_o_nota_la_validare_se_spune(lume):
    """MUTAȚIE: ramura `elif cu_asteptare` scoasă din `facturi_deschise` -> lista de așteptare e goală -> pică."""
    from core import casa_api
    with lume.cursor() as cur:
        cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, total, tva, status, tert_nume, tert_cui) VALUES "
                    "('F1A', '4', '2099-10-10', 'emisa', 242, 42, 'emisa', 'Client SRL', '14399840') RETURNING id")
        fid = cur.fetchone()[0]
        _incasare(cur, fid, "ciorna")
    assert casa_api.facturi_partener(lume, '"%s"' % _SCH, "incasare_client", "14399840") == [], "nu se poate alege: e deja încasată"
    (f,) = casa_api.facturi_in_asteptare(lume, '"%s"' % _SCH, "incasare_client", "14399840")
    assert (f["numar"], f["suma"], f["note"]) == ("F1A4", "242.00", ["din 16.10.2099"]), f
