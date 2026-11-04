# -*- coding: utf-8 -*-
"""scripts/lot_plugin_pytest.py — pluginul pytest al jurnalului lotului (comanda 16.1, pct.2): la începutul și la sfârșitul fiecărei sesiuni scrie în
.lot_jurnal.log faza „pytest” cu argumentele rulării și sha-ul. Se încarcă din conftest.py (rădăcina) și, pentru plasa e2e (rootdir propriu), cu `-p`
din scripts/e2e_poarta.py. Nu scrie: pe procesele xdist (numai controlorul), într-o sesiune pornită de un test (PYTEST_CURRENT_TEST), sub
scripts/cronometru.sh (LOT_CRONOMETRAT=1 — o scrie el)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_stare = {}


def _activ(config):
    return not (hasattr(config, "workerinput") or os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("LOT_CRONOMETRAT"))


def pytest_sessionstart(session):
    if not _activ(session.config):
        return
    try:
        import jurnal_lot as J
        lot = J.lot_curent()
        _stare["lot"], _stare["id"] = lot, J.inceput(lot, "pytest", "argumente=" + " ".join(session.config.invocation_params.args)[:300], pid=os.getpid())
    except Exception:   # jurnalul nu poate opri o sesiune de test; lipsa rândului se vede la publicare  # invariant-intern-ok: jurnal lot
        _stare.clear()


def pytest_sessionfinish(session, exitstatus):
    if _stare:
        try:
            import jurnal_lot as J
            J.sfarsit(_stare["lot"], "pytest", _stare["id"], "verde" if int(exitstatus) == 0 else "rosu_%s" % int(exitstatus))
        except Exception:   # invariant-intern-ok: jurnal lot
            pass
