# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”), deficiența 560 (fork P1 al subagentului PORTAL) — linkurile de acces.

  * „Link deja folosit: mesajul «link invalid sau expirat» să spună «Contul e deja activat — intră cu emailul și parola»”:
    `uc_public.motiv_link_nevalid` (peticul `l13_petice/portal_p1_2.json`) spune ce s-a întâmplat cu linkul și ce face omul.
  * linkul „Intră în portal” deschis într-o filă unde aplicația rulează deja: `static/js/app.js` citește fragmentul și la schimbarea lui
    (peticul `l13_petice/portal_p1_1.json`).

Temei: N/A — regulă de produs (comanda 13.1). Testele rulează după aplicarea peticelor (sesiunea principală le aplică la integrare).
"""
import os
import re

from core import repo_utilizatori, uc_public

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _motiv(monkeypatch, stare, fel):
    monkeypatch.setattr(repo_utilizatori, "stare_token_activare", lambda cur, h: stare)
    return uc_public.motiv_link_nevalid(None, "ml_x", fel)


def test_def_560_activarea_folosita_spune_contul_e_deja_activat(monkeypatch):
    """MUTAȚIE: mesajul linkului folosit înapoi pe „link de activare invalid sau expirat” -> pică."""
    assert _motiv(monkeypatch, (True, False, True), "activare") == "Contul e deja activat — intră cu emailul și parola."
    assert "a expirat" in _motiv(monkeypatch, (False, True, False), "activare")
    assert "nu e valid" in _motiv(monkeypatch, None, "activare")


def test_def_560_linkul_de_logare_folosit_trimite_la_link_nou_si_la_parola_numai_cand_exista(monkeypatch):
    fara = _motiv(monkeypatch, (True, False, False), "logare")
    cu = _motiv(monkeypatch, (True, False, True), "logare")
    assert "deja folosit" in fara and "Trimite-mi link de logare" in fara and "parola" not in fara, fara   # clientul invitat n-are parolă
    assert "intră cu emailul și parola" in cu, cu


def test_def_560_aplicatia_citeste_linkul_si_la_schimbarea_fragmentului():
    """Gard static: `app.js` ascultă `hashchange` pentru `#magic=` / `#activare=` / `#reset=` / `#email-nou=` (e2e:
    `e2e_lot13_portal_p1.py::test_def_560_linkul_invitatiei_intra_in_cont_si_in_fila_deja_deschisa`)."""
    js = open(os.path.join(RAD, "static", "js", "app.js"), encoding="utf-8").read()
    m = re.search(r'window\.addEventListener\("hashchange", \(\) => \{\s*if \(/\^#\(([a-z|-]+)\)=/\.test\(location\.hash\)\) randeaza\(\);', js)
    assert m and set(m.group(1).split("|")) == {"magic", "activare", "reset", "email-nou"}, "app.js nu citește linkul la schimbarea fragmentului"
