# -*- coding: utf-8 -*-
"""Gard: D406 nu emite ID BRUT de nomenclator ca identitate de partener SAF-T.

BUG PROD (11.08.2026): core/d406.py pull() construia Partener(id=str(r["id"])) din tabelele clienti/
furnizori -> RegistrationNumber/CustomerID/SupplierID = id brut de nomenclator ("1", "2"), respins de
DUKIntegrator ("format invalid") pe ORICE tenant cu nomenclator POPULAT. Defectul era mascat de nomenclatorul
gol (atunci rula calea de rezerva - derivarea din facturi cu _partener_id_saft, corecta). Repararea aliniaza
nomenclatorul cu ACEEASI logica (_partener_id_saft: 00/01/02+cod fiscal, 03+CNP, 04+cod din nume).

Gardul CADE daca reapare emiterea de id brut pe campurile de identificare partener (Partener(id=str(r["id"]))),
sau daca buclele de nomenclator nu mai folosesc _partener_id_saft.
"""
import os
import re

from core import scan_sql_efectiv as _efectiv

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(_RAD, "core", "d406.py")


def _text():
    with open(SRC, encoding="utf-8") as f:
        return f.read()


def test_fara_id_brut_ca_identitate_partener():
    """Anti-tipar: Partener(id=str(r["id"])) = identitate SAF-T din id brut de nomenclator."""
    t = _text()
    rele = re.findall(r'Partener\(\s*id\s*=\s*str\(\s*r\[["\']id["\']\]\s*\)', t)
    assert not rele, (
        "D406 pull(): identitatea partenerului (RegistrationNumber/CustomerID/SupplierID) construita "
        "din ID BRUT de nomenclator (Partener(id=str(r['id']))) -> DUK 'format invalid'. Foloseste "
        "_partener_id_saft (ca fallback-ul). Aparitii gasite: %d" % len(rele))


def test_nomenclatorul_foloseste_partener_id_saft():
    """Ambele bucle de nomenclator (clienti, furnizori) trebuie sa treaca prin _partener_id_saft."""
    # [P7 · D4] SQL-ul nomenclatorului a trecut in `core/repo_d406.py`, deci un regex care cerea
    # instructiunea SI `except ValueError` in acelasi text nu mai poate potrivi. Intrebarea ramane
    # aceeasi si se pune in doua bucati, fiecare unde traieste acum: instructiunea EXISTA (in
    # depozit) si bucla care o consuma trece prin `_partener_id_saft`, cu passthrough de ValueError.
    t = _text()
    sql = " ".join(_efectiv.sql_modul("core/d406.py"))
    for tab in ("clienti", "furnizori"):
        assert sql.count("SELECT id, nume, cui, oras FROM %s ORDER BY id" % tab) == 1, (
            "instructiunea de nomenclator '%s' lipseste din SQL-ul efectiv al lui d406" % tab)
        m = re.search(r'_repo\.[a-z0-9_]*%s[a-z0-9_]*\(.*?except ValueError' % tab, t, re.S)
        assert m, "bucla de nomenclator '%s' lipseste sau nu are passthrough ValueError" % tab
        assert "_partener_id_saft" in m.group(0), (
            "bucla de nomenclator '%s' nu foloseste _partener_id_saft (risc de id brut)" % tab)
