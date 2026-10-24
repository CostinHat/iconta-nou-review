# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 598 — datele existente] `core/migrare_mesaje_spv_tehnice.py`: motivele scrise de codul vechi (textul excepției)
pe rândurile trimiterilor SPV și pe ultima citire a CUI-ului se rescriu pe înțelesul contabilului; textele ANAF și cele noi rămân.

Pe baza de TEST, într-o schemă efemeră (numai coloanele pe care le citește migrarea), într-o tranzacție ANULATĂ.
Temei: N/A — textele aplicației (CLAUDE.md §9).
"""
import re

import pytest

from core import db as _db
from core import migrare_mesaje_spv_tehnice as M
from core import spv_conector as C
from core.efactura_trimitere import MESAJ_NETRIMISA
from core.spv_receive import MESAJ_ANAF_FARA_RASPUNS

SCH = "efemer_lot12_598"
VECHI_RETEA = "exceptie upload: HTTPSConnectionPool(host='api.anaf.ro', port=443): Read timed out. (read timeout=60)"
VECHI_DREPT = "403 fara drept SPV: 403 ANAF: certificatul nu are drept (CIF/serviciu)"
VECHI_NECONECTAT = "exceptie upload: principalul Principal(kind='firm', id=3) nu are token SPV activ"
DUBLURA = ("ANAF a primit și această încărcare, dar factura avea deja o trimitere vie (trimiterea 4): factura e de două ori în SPV. "
           "Verifică în SPV și anulează dublura.")
NOK_ANAF = "E: validator: Eroare Fatala - cardinalitate BT-1"     # răspunsul de validare al ANAF: rămâne


def _din_sablon(sablon, ce):
    """Textul de pe ecran al șablonului `spv_conector.MESAJ_*` ales de `mesaj_pentru_contabil` (aceeași normalizare a spațiilor)."""
    return " ".join(sablon.format(ce=ce.strip()).split())


def test_rescrie_numai_textele_vechi():
    assert M.rescrie(VECHI_RETEA, "efactura") == C.mesaj_pentru_contabil(ConnectionError(), MESAJ_NETRIMISA)
    assert M.rescrie(VECHI_RETEA, "efactura") == _din_sablon(C.MESAJ_ANAF_FARA_RASPUNS, M.CE_FACTURA)   # „ANAF nu a răspuns la timp”
    assert M.rescrie(VECHI_DREPT, "efactura", "14399840") == C.mesaj_fara_drept("14399840", None)
    assert M.rescrie(VECHI_NECONECTAT, "efactura") == _din_sablon(C.MESAJ_SPV_NECONECTAT, M.CE_FACTURA)   # „nu e conectat la SPV”
    assert M.rescrie("exceptie upload: KeyError('x')", "efactura").startswith("Legătura cu ANAF nu a reușit dintr-o eroare a aplicației")
    et = M.rescrie("403 fara drept e-Transport: 403 ANAF: x", "etransport")
    assert et == _din_sablon(C.MESAJ_SPV_FARA_DREPT, M.CE_ETRANSPORT) and set(re.findall(r"[\w-]+", et)) >= {"e-Transport"}, et
    assert M.rescrie("ANAF: ok. " + DUBLURA, "efactura") == DUBLURA
    for ramane in (NOK_ANAF, DUBLURA, MESAJ_NETRIMISA, None, ""):
        assert M.rescrie(ramane, "efactura") is None, ramane
    assert M.rescrie("ANAF n-a răspuns la timp (ReadTimeout); citirea se reia la următoarea rulare.", "citire") == MESAJ_ANAF_FARA_RASPUNS
    assert M.rescrie("principalul Principal(kind='firm', id=3) nu are token SPV activ", "citire") == _din_sablon(
        C.MESAJ_SPV_NECONECTAT, M.CE_CITIRE)
    assert M.rescrie("Nu aveti drept in SPV pentru CIF=14399840", "citire") is None    # textul ANAF: decide `are_drept`, rămâne
    assert M.rescrie("Nu exista mesaje in ultimele 60 zile", "citire") is None


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_aplica_rescrie_randurile_vechi_si_e_idempotenta():
    """MUTAȚIE: `nou and nou != text` -> `False` în `aplica_firma` -> rândurile vechi rămân -> pică."""
    p = _db.pool()
    conn = p.getconn()
    try:
        cur = conn.cursor()
        cur.execute('CREATE SCHEMA "%s"' % SCH)
        cur.execute('CREATE TABLE "%s".firma_profil (id int PRIMARY KEY, cui text)' % SCH)
        cur.execute('INSERT INTO "%s".firma_profil VALUES (1, \'RO14399840\')' % SCH)
        for t in ("efactura_trimiteri", "etransport_trimiteri"):
            cur.execute('CREATE TABLE "%s".%s (id serial PRIMARY KEY, error_message text)' % (SCH, t))
        for m in (VECHI_RETEA, VECHI_DREPT, NOK_ANAF, "ANAF: ok. " + DUBLURA):
            cur.execute('INSERT INTO "%s".efactura_trimiteri (error_message) VALUES (%%s)' % SCH, (m,))
        cur.execute('INSERT INTO "%s".etransport_trimiteri (error_message) VALUES (%%s)' % SCH, ("exceptie upload: timed out",))
        assert M.aplica_firma(conn, SCH) == 4
        cur.execute('SELECT error_message FROM "%s".efactura_trimiteri ORDER BY id' % SCH)
        dupa = [r[0] for r in cur.fetchall()]
        assert dupa == [C.mesaj_pentru_contabil(ConnectionError(), MESAJ_NETRIMISA), C.mesaj_fara_drept("14399840", None), NOK_ANAF,
                        DUBLURA], dupa
        assert M.aplica_firma(conn, SCH) == 0          # idempotentă
    finally:
        conn.rollback()
        p.putconn(conn)
