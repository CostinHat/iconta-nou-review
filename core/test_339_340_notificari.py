# -*- coding: utf-8 -*-
"""[deficiențele 339 + 340, comanda Costin 8.1, 18.10.2026, verbatim în DECIZII „Comanda 8.1”]
339: „Ana a primit «un element nou de validat» când B a pus propria D300 în «De depus» (validarea în doi a declarațiilor e oprită).”
340: „«Sesizare nouă» și «cerere de import» vin nebifate la superadmin (decizia 16.10 le cerea); superadminul vede tipuri care nu-l
privesc.” Temei: N/A — produs (cine primește ce)."""
import contextlib
from types import SimpleNamespace

from core import notificari as N


def _cu(monkeypatch, efectiv):
    from core import uc_coada as U
    trimise = []
    monkeypatch.setattr(U.db, "get_conn", lambda *a, **k: contextlib.nullcontext(object()))
    monkeypatch.setattr(U.coada_api, "patru_ochi_stare", lambda conn, cab: {"activ": efectiv, "posibil": True, "efectiv": efectiv})
    monkeypatch.setattr(U._uc_comun, "_notif_de_validat", lambda *a, **k: trimise.append(a))
    U._anunta_validatorii({"ok": True, "coada_id": 7, "perioada": "10/2026"},
                          SimpleNamespace(tip="d300", luna=10, trim=None, an=2026, tenant_id=3), {"firm": 1, "uid": 5})
    return trimise


def test_339_fara_validarea_in_doi_nimeni_nu_primeste_de_validat(monkeypatch):
    """MUTAȚIE: condiția `efectiv` scoasă din `uc_coada._anunta_validatorii` -> notificarea pleacă -> pică."""
    assert _cu(monkeypatch, efectiv=False) == []


def test_339_cu_validarea_in_doi_validatorii_primesc_de_validat(monkeypatch):
    assert len(_cu(monkeypatch, efectiv=True)) == 1


SUPER = {"rol": "superadmin", "poate_pregati": True, "poate_valida": True}
ADMIN = {"rol": "admin_firma", "poate_pregati": True, "poate_valida": True}


def test_340_superadminul_vede_numai_tipurile_lui_bifate_din_oficiu():
    """MUTAȚIE: ramura `superadmin` din `vede_tipul` pusă înapoi la „toate” -> superadminul vede tipurile cabinetului -> pică;
    `implicit` numai pe grupe -> sesizarea / cererea de import nebifate -> pică."""
    tipuri = {t["cheie"]: t["bifat"] for g in N.lista_pentru(SUPER, {}) for t in g["tipuri"]}
    assert tipuri == {"alerta_legislativa": True, "sesizare": True, "cerere_import": True}, tipuri
    assert N.dorit("sesizare", {}) and N.dorit("cerere_import", {}), "pleacă pe canalul lui fără bifa salvată"
    assert N.dorit("sesizare", {"sesizare": False}) is False, "bifa scoasă de el rămâne scoasă"


def test_340_administratorul_cabinetului_nu_vede_tipurile_platformei():
    vazute = {t["cheie"] for g in N.lista_pentru(ADMIN, {}) for t in g["tipuri"]}
    assert not vazute & {"alerta_legislativa", "sesizare", "cerere_import"}, vazute
    assert {"de_validat", "termen_declaratie", "asistent_activat"} <= vazute
