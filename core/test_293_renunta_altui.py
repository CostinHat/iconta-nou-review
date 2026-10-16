# -*- coding: utf-8 -*-
"""293 — coada: pe declarația altcuiva, fără „Poate depune”, numai vizualizare (comanda Costin 16.10.2026, completarea 290–295, verbatim
în DECIZII): „Ana senior, fără «Poate depune», vede pe D300 F1 10/2026, pregătită de administrator, butonul «Renunță». Pe o declarație a
altcuiva, fără dreptul de depunere, nu se oferă nicio acțiune în afară de vizualizare; serverul refuză la fel.” Temei: N/A — drepturi."""
import contextlib

import pytest


class _Cur:
    def __init__(self, autor):
        self.autor = autor


def test_293_renuntarea_la_declaratia_altuia_cere_dreptul_de_depunere(monkeypatch):
    """MUTAȚIE: condiția `autor != int(ctx["uid"])` scoasă -> și autorul fără „Poate depune” e refuzat -> pică;
    garda scoasă cu totul -> Ana trece -> pică."""
    from core import uc_coada as uq, repo_declaratii as rd, erori
    stare = {"autor": 1, "efectiv": False, "depune": False}
    monkeypatch.setattr(uq, "_schema_notei", lambda cid, ctx: ("declaratie", None, None))
    monkeypatch.setattr(uq.db, "get_conn", lambda schema=None: contextlib.nullcontext(type("C", (), {"cursor": lambda s: contextlib.nullcontext(None)})()))
    monkeypatch.setattr(rd, "autorul_elementului", lambda cur, cid: stare["autor"])
    monkeypatch.setattr(uq.coada_api, "patru_ochi_stare", lambda c, f: {"efectiv": stare["efectiv"]})
    monkeypatch.setattr(uq._uc_comun, "_are_permisiune", lambda ctx, p: p == "poate_valida" or (p == "poate_depune" and stare["depune"]))
    trecut = []
    monkeypatch.setattr(uq.coada_api, "respinge", lambda *a, **k: trecut.append(1) or {"ok": True})
    monkeypatch.setattr(uq._uc_comun, "_notif_pregatitor", lambda *a, **k: None)
    date = type("D", (), {"motiv": "nu"})()
    ana = {"uid": 2, "firm": 1}
    with pytest.raises(erori.FaraDrept) as e:
        uq.coada_respinge(9, date, ana)
    assert e.value.detaliu == uq.MESAJ_RENUNTA_ALTUI and not trecut
    stare["autor"] = 2
    uq.coada_respinge(9, date, ana)                       # a pregătit-o ea: renunță
    stare.update(autor=1, depune=True)
    uq.coada_respinge(9, date, ana)                       # o depune ea: renunță
    stare.update(depune=False, efectiv=True)
    uq.coada_respinge(9, date, ana)                       # validarea în doi: „respinge” e actul validatorului
    assert len(trecut) == 3
