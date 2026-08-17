# -*- coding: utf-8 -*-
"""core/test_vector_platitor_tva_oblig.py — GARD: `platitor_tva` necompletat (None) la salvarea
vectorului fiscal NU devine tacit `False` — se refuza explicit, simetric cu `operatiuni_ic`.

DE CE (audit vizual tenant_001, ecranul Date firma, 17.08.2026):
  firma_profil.platitor_tva = NULL (necompletat). Ecranul afisa selectul „Inregistrata in scopuri de
  TVA" pe prima optiune „Nu" (default fabricat, fara optiune-placeholder), iar la Salvare frontendul
  trimitea `platitor_tva=false`. Backendul `vector_fiscal_api.salveaza` facea `tva = bool(platitor_tva)`
  -> None coerce tacit la False si SE PERSISTA. Semaforul, care citea NULL ca „necompletat" (gri onest),
  trecea brusc la verdict „neplatitor TVA" pe o alegere pe care contabilul nu a facut-o (Regula 4:
  fara valori implicite fabricate). `operatiuni_ic` era deja corect (None -> IC_LIPSA); `platitor_tva`
  ramasese asimetric.

TEMEI: DECIZII 23.07 + DESIGN_SYSTEM cap.17 („None (necompletat) -> eroare, nu False tacit").

Garda cheama `salveaza` cu un conn FALS (fara DB): pe codul VECHI, platitor_tva=None trece de
`bool()` si ajunge la UPDATE (scrie tva=False) -> ok=True -> PICA. Pe codul NOU, refuz timpuriu
inainte de orice acces DB -> ok=False, cod TVA_LIPSA.
"""


class _FakeCur:
    def __init__(self, store):
        self.store = store
        self._r = ("srl",)  # tip_firma -> partida dubla, ca regimul sa mearga pe ramura micro/profit

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        s = " ".join(sql.split())
        if s.startswith("SELECT tip_firma"):
            self._r = ("srl",)
        else:
            # orice UPDATE/INSERT = scriere efectiva a vectorului (nu ar trebui sa se ajunga aici cu None)
            self.store["scris"] = True
            self.store["sql"] = s
            self.store["params"] = params

    def fetchone(self):
        return self._r


class _FakeConn:
    def __init__(self, store):
        self.store = store

    def cursor(self):
        return _FakeCur(self.store)


def test_platitor_tva_none_nu_devine_false_tacit():
    from core import vector_fiscal_api as vfa
    store = {}
    r = vfa.salveaza(_FakeConn(store), regim_fiscal="micro", platitor_tva=None,
                     tip_decont=None, operatiuni_ic=False, nume="X SRL", cui="1")
    assert not r.get("ok"), (
        "platitor_tva=None a fost persistat tacit (default fabricat False); scris=%s" % store.get("scris"))
    assert r.get("cod") == "TVA_LIPSA", "cod asteptat TVA_LIPSA, primit %r" % r.get("cod")
    assert not store.get("scris"), "nu trebuie sa se scrie nimic in DB cand platitor_tva lipseste"


def test_operatiuni_ic_none_ramane_respins():
    """Regresie: perechea deja corecta (operatiuni_ic) ramane refuzata."""
    from core import vector_fiscal_api as vfa
    r = vfa.salveaza(_FakeConn({}), regim_fiscal="micro", platitor_tva=True,
                     tip_decont="lunar", operatiuni_ic=None, nume="X SRL", cui="1")
    assert not r.get("ok") and r.get("cod") == "IC_LIPSA"
