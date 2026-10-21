# -*- coding: utf-8 -*-
"""[deficiența 383, retestul Costin 19.10.2026, verbatim în DECIZII „Comanda 9.1”] „D300 pe 10/2026 e oferită cu «Confirmă depunerea» pe
19.10.2026, înainte de sfârșitul lunii. O declarație nu se oferă spre depunere înainte de încheierea perioadei.”
Regula e una (`coada_api.perioada_neincheiata`): lista cozii n-o mai oferă (`perioada_neincheiata` pe element, `gata_de_depus` fals), iar
tranziția ireversibilă (`marcheaza_depusa`) o refuză pe orice drum. Proba pe ecran: `e2e_lot91.py::test_def_383_…`."""
import datetime as _dt

from core import coada_api


def test_luna_in_curs_nu_se_depune():
    # comanda 9.1: 10/2026 pe 19.10.2026 -> neîncheiată
    m = coada_api.perioada_neincheiata(2026, 10, azi=_dt.date(2026, 10, 19))
    assert m == ("Perioada 10/2026 nu s-a încheiat: declarația se generează și se depune după 31.10.2026, când toate operațiunile perioadei sunt "
                 "înregistrate."), m


def test_ultima_zi_a_lunii_inca_nu_s_a_incheiat():
    assert coada_api.perioada_neincheiata(2026, 10, azi=_dt.date(2026, 10, 31))
    assert coada_api.perioada_neincheiata(2026, 10, azi=_dt.date(2026, 11, 1)) is None


def test_trimestrul_si_anul():
    assert coada_api.perioada_neincheiata(2026, None, trim=4, azi=_dt.date(2026, 11, 15)) == (
        "Perioada T4/2026 nu s-a încheiat: declarația se generează și se depune după 31.12.2026, când toate operațiunile perioadei sunt înregistrate.")
    assert coada_api.perioada_neincheiata(2026, None, trim=3, azi=_dt.date(2026, 10, 19)) is None
    assert coada_api.perioada_neincheiata(2026, None, azi=_dt.date(2026, 12, 20)) == (
        "Anul 2026 nu s-a încheiat: declarația se generează și se depune după 31.12.2026, când toate operațiunile perioadei sunt înregistrate.")
    assert coada_api.perioada_neincheiata(2025, None, azi=_dt.date(2026, 1, 2)) is None


def test_fara_perioada_nu_se_opreste():
    assert coada_api.perioada_neincheiata(None, None) is None


def test_lista_si_depunerea_folosesc_aceeasi_regula():
    """Gard de structură: marcarea ca depusă și lista cozii cheamă aceeași funcție (o singură regulă, nu două) — apelurile din arborele
    sintactic, nu un sub-șir din sursă."""
    import ast
    import inspect
    import textwrap

    def cheama(f):
        return {n.func.id for n in ast.walk(ast.parse(textwrap.dedent(inspect.getsource(f))))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert {"perioada_neincheiata"} <= cheama(coada_api.marcheaza_depusa) & cheama(coada_api.lista_coada)


# ── tranziția ireversibilă, pe un element sintetic (tenant negativ, perioada 2099, ROLLBACK — fixtura din test_verdict_persistat) ──
from core.test_verdict_persistat import XML_A, _valid, element  # noqa: E402,F401 — fixtura și ajutoarele ei, refolosite


def test_depunerea_pe_perioada_neincheiata_e_refuzata(element):
    """Elementul cu verdict valid și aprobat, pe 01/2099 (neîncheiată): `marcheaza_depusa` refuză cu PERIOADA_NEINCHEIATA și nu scrie.
    MUTAȚIA: verificarea scoasă din `marcheaza_depusa` -> ok -> ROȘU."""
    conn, cid, uid = element
    _valid(conn, cid, XML_A)
    coada_api.aproba(conn, cid, "ztest", aprobat_de_id=uid)
    r = coada_api.marcheaza_depusa(conn, cid, depus_de="ztest", depus_de_id=uid)
    assert r == {"ok": False, "cod": "PERIOADA_NEINCHEIATA", "mesaj": "Perioada 01/2099 nu s-a încheiat: declarația se generează și se depune după "
                 "31.01.2099, când toate operațiunile perioadei sunt înregistrate."}, r
    with conn.cursor() as cur:
        cur.execute("SELECT stare FROM public.declaratii_coada WHERE id=%s", (cid,))
        assert cur.fetchone()[0] == "aprobata"


def test_CALIBRARE_dupa_incheierea_perioadei_depunerea_trece(element, monkeypatch):
    """Aceeași depunere, cu „azi” după 31.01.2099: trece (garda nu refuză orice)."""
    from core import common
    conn, cid, uid = element
    _valid(conn, cid, XML_A)
    coada_api.aproba(conn, cid, "ztest", aprobat_de_id=uid)
    monkeypatch.setattr(common, "azi_ro", lambda: _dt.date(2099, 2, 1))
    r = coada_api.marcheaza_depusa(conn, cid, depus_de="ztest", depus_de_id=uid)
    assert r["ok"] is True, r
