# -*- coding: utf-8 -*-
"""Lotul 12, comanda 12.1, pachetul `ctrl` — Control fiscal, clasele numerelor vechi reverificate: 157 și 213.

  * 157 „D100/D205 2025 la «Nu pot verifica» deși sunt înainte de preluare”. Necunoașterile cu domeniu ÎNCHIS (un an, o lună) se
    desfăceau deja în grupul „Înainte de preluare”; cele DESCHISE (toată fereastra evaluată, „din 12/2025”: vector incomplet, periodicitate
    necunoscută) rămâneau „Nu se poate verifica” cu domeniul începând înaintea preluării. Acum domeniul lor începe la luna preluării.
  * 213 „Confirmarea anulării scrie «D406 03/2026» pentru T1”. Ecranul folosea deja perioada rândului; mesajele SERVERULUI despre
    marcări (anularea fără marcare, marcarea peste o depunere, perioadele sărite la „Marchează toate”) scriau tot luna de ancoră
    („D406 pe 03/2026”). Acum: `control_fiscal_api.perioada_declaratiei`, după periodicitatea firmei (`declaratii_api.periodicitate_firma`).

Temei: N/A — forma afișată a perioadei (DS cap.4 v2.85: luna „LL/AAAA”, trimestrul „T3/2026”, anul „2026”); periodicitatea declarațiilor
vine din sursa unică a selectorului (OPANAF 1783/2021 anexa 4 pct.2–3 pentru D406, CF art.322 pentru perioada fiscală TVA — citate acolo).
"""
import pytest

from core import afirmatii as _af
from core import control_fiscal_api as _cf


def test_157_necunoasterea_deschisa_incepe_la_luna_preluarii():
    deschisa = _af.afirmatie("necunoastere", "d300", "Perioada fiscală TVA nu e completată.", domeniu_de="2025-12", domeniu_pana=None)
    an_2025 = _af.afirmatie("necunoastere", "d205", "necunoscut declarat: dividende 2025", domeniu_de="2025-01", domeniu_pana="2025-12")
    ramase, inainte = _cf.separa_neclar_inainte_de_preluare([deschisa, an_2025], (2026, 9))
    assert [(x["tip"], x.get("domeniu_de"), x.get("domeniu_pana")) for x in ramase] == [("d300", "2026-09", None)], ramase
    # D205 2025 (an închis, dinaintea preluării) -> „Înainte de preluare”, cu perioada „2025”
    assert [(x["tip"], x["perioada"]) for x in inainte] == [("d205", "2025")], inainte
    # fără luna preluării nimic nu se mută
    assert _cf.separa_neclar_inainte_de_preluare([deschisa], None) == ([deschisa], [])


class _Cur:
    def __init__(self, rand):
        self.rand = rand

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a):
        pass

    def fetchone(self):
        return self.rand


class _Conn:
    def __init__(self, rand):
        self.rand = rand

    def cursor(self):
        return _Cur(self.rand)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.mark.parametrize("profil,tip,an,luna,asteptat", [
    (("micro", True, "trimestrial"), "d406", 2026, 3, "T1/2026"),    # D406 urmează perioada TVA trimestrială
    (("micro", True, "trimestrial"), "d300", 2026, 6, "T2/2026"),
    (("micro", True, "lunar"), "d300", 2026, 3, "03/2026"),
    (("micro", False, None), "d406", 2026, 3, "T1/2026"),            # neplătitorul depune D406 trimestrial (OPANAF 1783/2021 anexa 4 pct.3)
    (("micro", True, "lunar"), "d100", 2025, 12, "T4/2025"),
    (("micro", True, "lunar"), "d205", 2025, 12, "2025"),
    (("micro", True, "lunar"), "d112", 2026, 3, "03/2026"),
    (("micro", True, "trimestrial"), "d300", 2026, 5, "05/2026"),   # lună care nu e ancoră de trimestru: nu se inventează un trimestru
])
def test_213_perioada_declaratiei_marcate_e_a_periodicitatii(profil, tip, an, luna, asteptat):
    assert _cf.perioada_declaratiei(_Conn(profil), tip, an, luna) == asteptat


def test_213_mesajul_serverului_la_anulare_spune_trimestrul(monkeypatch):
    """«Anulează marcarea» pe D406 T1/2026 care nu (mai) e o marcare: refuzul spune „D406 pe T1/2026”, nu „D406 pe 03/2026”."""
    from core import uc_control_fiscal as U, repo_control_fiscal_api as R, erori
    monkeypatch.setattr(U._uc_comun, "_schema_sau_404", lambda ctx, tid: "tenant_1")
    monkeypatch.setattr(U.db, "get_conn", lambda *a: _Conn(("micro", True, "trimestrial")))
    monkeypatch.setattr(R, "select_depusa_curenta", lambda cur, tid, an, luna, tip: None)
    with pytest.raises(erori.Conflict) as e:
        U.control_fiscal_anuleaza_marcare(1, {"tip": "d406", "an": 2026, "luna": 3}, {"uid": 1})
    assert str(e.value) == "D406 pe T1/2026 nu e o marcare — nu e nimic de anulat.", str(e.value)
