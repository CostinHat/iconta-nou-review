# -*- coding: utf-8 -*-
"""GARD — deficiențele 125 + 224, decizia Costin 11.10.2026 (verbatim în DECIZII): „cardul Control fiscal și fereastra care se deschide
din el arată aceleași 4 stări, cu aceleași numere, calculate dintr-o singură sursă.”

Sursa unică = `sumar` din `/control-fiscal` (`uc_control_fiscal.control_fiscal_portofoliu`): partiția firmelor pe stări, fiecare firmă
într-o singură stare — aceeași stare pe care o poartă rândul ei. Cardul (cabinet.js, asistent.js) și fereastra (control.js) randează
amândouă `semaforPatruLumini(sumar)` (gardul SEMAFOR_PATRU_LUMINI din verificator). Aici: răspunsul n-are altă numărătoare (contoarele de
fapte au fost a doua sursă — 125), iar fiecare cifră din `sumar` = firmele din listă în starea aceea."""
import contextlib

from core import auth_api, db, firma_rezumat as fr, uc_control_fiscal as u


def _portofoliu(monkeypatch, rezumate):
    @contextlib.contextmanager
    def _conn():
        yield None
    monkeypatch.setattr(db, "get_conn", _conn)
    monkeypatch.setattr(auth_api, "tenantii_userului", lambda conn, uid: [{"id": t, "nume": "F%d" % t, "cui": "1"} for t in rezumate])
    monkeypatch.setattr(fr, "citeste", lambda conn, ids, chei: {
        t: {"control_fiscal": r} for t, r in rezumate.items() if r is not None})
    return u.control_fiscal_portofoliu({"uid": 1})


def test_fereastra_si_cardul_au_o_singura_numaratoare_pe_stari(monkeypatch):
    """Cinci firme: roșie cu un necunoscut (era numărată de contoarele de fapte și la „nu se pot verifica”), galbenă cu neconcordanță,
    verde, una cu rezumatul în recalculare (gri) și una fără rezumat (gri). `sumar` = {roșu 1, galben 1, verde 1, gri 2} = rândurile
    listei pe stări; nicio altă cifră de sumar în răspuns. MUTAȚIE: `contoare` readus în răspuns, sau starea firmei în recalculare
    numărată pe culoarea veche -> pică."""
    cur = lambda d: {"stare": fr.CURENT, "date": d}   # noqa: E731
    r = _portofoliu(monkeypatch, {
        1: cur({"stare": "rosu", "lipsa": 1, "urmarit": 0, "neclar": 2, "contabil": []}),
        2: cur({"stare": "galben", "lipsa": 0, "urmarit": 3, "neclar": 0, "contabil": [{"stare": "rosu", "eticheta": "TVA"}]}),
        3: cur({"stare": "verde", "lipsa": 0, "urmarit": 0, "neclar": 0, "contabil": []}),
        4: {"stare": "veche", "date": {"stare": "verde"}},
        5: None})
    assert set(r) == {"firme", "sumar"}, sorted(r)          # o singură sursă de cifre: nicio a doua numărătoare
    pe_randuri = {s: sum(1 for f in r["firme"] if f["stare"] == s) for s in ("rosu", "galben", "verde", "gri")}
    assert r["sumar"] == pe_randuri == {"rosu": 1, "galben": 1, "verde": 1, "gri": 2}, (r["sumar"], pe_randuri)
    assert sum(r["sumar"].values()) == len(r["firme"]) == 5
    # faptele rămân pe rând: firma roșie spune și ce nu se poate verifica, deși lumina ei e roșie
    f1 = next(f for f in r["firme"] if f["tenant_id"] == 1)
    assert f1["lipsa"] == 1 and f1["neverificabil"] == "2 declarații nu se pot verifica", f1
