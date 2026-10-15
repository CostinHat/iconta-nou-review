# -*- coding: utf-8 -*-
"""Curățarea plasei se reia la DEADLOCK (15.10.2026, poarta a treia a lotului 3: `DROP SCHEMA … CASCADE` al firmei de probă s-a
încrucișat cu o cerere a paginii încă deschise — „deadlock detected” la curățarea testului 243, iar plasa a respins un lot verde).
`frontend_test/e2e/curatenie.scoate` scoate fiecare firmă pe tranzacția ei și o reia la `DeadlockDetected`; după ultima încercare
eroarea urcă. MUTAȚIE: reluarea scoasă (`_scoate_una` chemat o dată) -> pică primul test."""
import os
import sys

import pytest
from psycopg2 import errors

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend_test", "e2e"))
import curatenie   # noqa: E402


class _DbFals:
    """Numai citirea listei de tabele publice; ștergerea propriu-zisă e `_scoate_una`, înlocuită în teste."""
    class _Cur:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def execute(self, *a): pass
        def fetchall(self): return [("tabela_a",)]

    class _Conn:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def cursor(self): return _DbFals._Cur()

    def get_conn(self):
        return _DbFals._Conn()


def test_deadlockul_se_reia_iar_firma_se_scoate(monkeypatch):
    apeluri = []
    def _una(db, tabele, tid, schema):
        apeluri.append(tid)
        if len(apeluri) < 3:
            raise errors.DeadlockDetected("deadlock detected")
    monkeypatch.setattr(curatenie, "_scoate_una", _una)
    monkeypatch.setattr("time.sleep", lambda s: None)
    curatenie.scoate(_DbFals(), [(7, "tenant_9999")])
    assert apeluri == [7, 7, 7]


def test_dupa_ultima_incercare_eroarea_urca(monkeypatch):
    def _una(db, tabele, tid, schema):
        raise errors.DeadlockDetected("deadlock detected")
    monkeypatch.setattr(curatenie, "_scoate_una", _una)
    monkeypatch.setattr("time.sleep", lambda s: None)
    with pytest.raises(errors.DeadlockDetected):
        curatenie.scoate(_DbFals(), [(7, "tenant_9999")], incercari=3)
