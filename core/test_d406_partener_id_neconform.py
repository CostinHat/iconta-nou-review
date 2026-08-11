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
    t = _text()
    for tab in ("clienti", "furnizori"):
        m = re.search(r'SELECT id, nume, cui, oras FROM %s ORDER BY id.*?except ValueError' % tab, t, re.S)
        assert m, "bucla de nomenclator '%s' lipseste sau nu are passthrough ValueError" % tab
        assert "_partener_id_saft" in m.group(0), (
            "bucla de nomenclator '%s' nu foloseste _partener_id_saft (risc de id brut)" % tab)
