# -*- coding: utf-8 -*-
"""core/test_email_html_rezultat.py — eșecul unui email nu mai trece neobservat (15.10.2026).

CLASA. `observare.trimite_email_html` semnalează eșecul prin `False` (fără cheie Brevo, Brevo refuză, rețeaua cade) și practic nu
aruncă. Înainte: 4 locuri îl prindeau NUMAI pe excepție, cu alerta R73 „cale de acces” (resetarea parolei, linkul de logare, activarea
asistentului) care deci nu pleca niciodată la un eșec real; 7 ignorau rezultatul; invitația de cabinet îi spunea superadminului „a
plecat” fără să știe (prins în e2e, pe aplicația de probă fără Brevo). Acum: un apel direct își CITEȘTE rezultatul, iar cine nu are
nevoie de el trece prin `trimite_email_html_sau_semnaleaza`, care semnalează eșecul oricum ar veni.
MUTAȚII: un apel direct cu rezultatul aruncat -> ROȘU (testul 1); `if not ok` scos din funcția unică -> ROȘU (testul 2)."""
from __future__ import annotations

import os
import sys
import types

import pytest

from core import observare

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import inventar_email_html as inv  # noqa: E402


def test_orice_apel_direct_isi_citeste_rezultatul():
    locuri = inv.inventar(RAD)
    directe = [x for x in locuri if x["apel"] == inv.NUME]
    aruncate = [x["fisier_linie"] for x in directe if not x["rezultat_citit"]]
    assert aruncate == []                       # rezultatul (True/False) e singurul semnal de eșec: aruncat, eșecul tace
    assert len(locuri) >= 15 and len(directe) >= 5   # scanul vede familia întreagă (o gardă oarbă ar fi verde)


@pytest.mark.parametrize("postas", ["refuza", "arunca"])
def test_functia_unica_semnaleaza_esecul_cu_alerta_ceruta(monkeypatch, postas):
    semnalate = []
    monkeypatch.setattr(observare, "esec_secundar", lambda et, e, alerta=False: semnalate.append((et, type(e).__name__, alerta)))

    def trimite(*a, **k):
        if postas == "arunca":
            raise OSError("retea")
        return False
    monkeypatch.setattr(observare, "trimite_email_html", trimite)
    assert observare.trimite_email_html_sau_semnaleaza("email x", "a@b.ro", "s", "<p/>", alerta=True) is False
    assert semnalate == [("email x", "RuntimeError" if postas == "refuza" else "OSError", True)]


def test_emailul_plecat_nu_semnaleaza_nimic(monkeypatch):
    semnalate = []
    monkeypatch.setattr(observare, "esec_secundar", lambda *a, **k: semnalate.append(a))
    monkeypatch.setattr(observare, "trimite_email_html", lambda *a, **k: True)
    assert observare.trimite_email_html_sau_semnaleaza("email x", "a@b.ro", "s", "<p/>") is True
    assert semnalate == []


def test_invitatia_spune_cand_emailul_n_a_plecat(monkeypatch):
    """Cazul prins în e2e: fără Brevo, ecranul superadminului scria „Invitația a plecat”."""
    from core import db, uc_auth
    db.init_pool()
    email = "ztest_inv_email@exemplu.ro"
    monkeypatch.setattr(observare, "trimite_email_html", lambda *a, **k: False)
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id FROM public.users WHERE rol = 'superadmin' ORDER BY id LIMIT 1")
        uid = cur.fetchone()[0]
        cur.execute("DELETE FROM public.invitatii_cabinet WHERE email = %s", (email,))
        c.commit()
    try:
        r = uc_auth.invitatie_creeaza(types.SimpleNamespace(email=email), {"uid": uid})
        assert (r["email_trimis"], r["email"]) == (False, email)
    finally:
        with db.get_conn() as c, c.cursor() as cur:
            cur.execute("DELETE FROM public.invitatii_cabinet WHERE email = %s", (email,))
            c.commit()
