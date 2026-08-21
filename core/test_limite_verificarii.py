# -*- coding: utf-8 -*-
"""GARD (P4, 21.08.2026): „Ce nu poate spune verificarea asta" e PERMANENTĂ și se COMPUNE.
DESIGN_SYSTEM cap.25.4.

DE CE. Câmpul `limita` există de mult pe constatări — dar se randează DOAR când există o constatare.
Pe o firmă curată limitele dispar, adică exact când verdictul e cel mai ușor de citit greșit: verdele
arată ca „am verificat tot" fiindcă n-are nimic sub el care să spună ce nu. Aceeași eroare ca
`absenta_observatie`, mutată un nivel mai sus.

CE PĂZEȘTE:
  1. Secțiunea nu poate dispărea (permanența e esențială: dacă apare doar câteodată, prezența ei
     devine semnal și absența ei minte).
  2. Un verificator care ajunge pe ecran fără `limita` declarată nu poate trece — altfel secțiunea
     ar fi completă doar pe hârtie.
  3. Nu se scrie de mână: perimetrul se CALCULEAZĂ din fereastra reală.
"""
import datetime

import pytest

from core.control_fiscal_api import limite_verificarii

AZI = datetime.date(2026, 8, 21)


def test_sectiunea_exista_si_fara_nicio_constatare():
    """Miezul. Pe o firmă fără verificatori și fără constatări, limitele NU dispar."""
    lim = limite_verificarii(AZI)
    assert lim, "limitele au dispărut pe o firmă curată — exact cazul care a cerut secțiunea"
    assert {x["fel"] for x in lim} >= {"acoperire", "perimetru"}


def test_perimetrul_se_calculeaza_nu_se_scrie():
    """Fereastra vine din datele reale; un text redactat separat ar descrie peste șase luni un
    instrument care s-a schimbat."""
    lim = limite_verificarii(AZI, sus_zile=7)
    per = [x for x in lim if x["fel"] == "perimetru"][0]
    assert "28.08.2026" in per["text"], per["text"]        # azi + 7
    assert "01.12.2025" in per["text"], per["text"]        # dec. anului precedent
    alt = limite_verificarii(AZI, jos=datetime.date(2026, 6, 1))
    assert "01.06.2026" in [x for x in alt if x["fel"] == "perimetru"][0]["text"]


def test_acoperirea_spune_si_ce_NU_compara():
    """O declarație de acoperire care spune doar ce face nu e o limită, e o reclamă."""
    t = " ".join(x["text"] for x in limite_verificarii(AZI) if x["fel"] == "acoperire")
    assert "NU compar" in t and "SPV" in t, t


def test_limitele_verificatorilor_se_aduna_nu_se_repovestesc():
    """Fiecare verificator își declară SINGUR limita; secțiunea o preia verbatim, cu sursa."""
    vc = {"tva_incrucisat": {"limita": "Comparat doar pe luna închisă."},
          "d112_incrucisat": {"limita": "Fără salariați, nimic de verificat."},
          "fara_limita": {"altceva": 1}}
    lim = limite_verificarii(AZI, vc=vc)
    texte = [x["text"] for x in lim]
    assert "Comparat doar pe luna închisă." in texte
    assert any(x.get("sursa") == "d112_incrucisat" for x in lim)


def test_invitatia_de_intarire_apare_doar_cand_e_ceva_de_facut():
    """Al treilea fel o face utilă, nu doar onestă — dar o invitație care nu mai are obiect e zgomot."""
    fara = limite_verificarii(AZI, inchide_luni=False)
    assert any(x["fel"] == "intarire" for x in fara)
    cu = limite_verificarii(AZI, inchide_luni=True)
    assert not [x for x in cu if x["fel"] == "intarire"], \
        "firma închide deja lunile — invitația n-are ce să mai ceară"


def test_randerul_chiar_o_afiseaza():
    """Doc-cod: o listă corectă în payload poate fi complet nefolosită pe ecran."""
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    js = open(os.path.join(rad, "static", "js", "ecrane", "control_verdict.js"),
              encoding="utf-8").read()
    assert "Ce nu poate spune verificarea asta" in js, "secțiunea nu se randează"
    assert "d.limite" in js, "rendererul nu citește limitele din payload"


def test_semaforul_pune_limitele_in_payload():
    import inspect

    from core import control_fiscal_api as cf
    src = inspect.getsource(cf.evalueaza_firma)
    assert '"limite": limite_verificarii(' in src, "semaforul nu mai trimite limitele"


@pytest.mark.parametrize("fel", ["acoperire", "perimetru", "intarire"])
def test_toate_cele_trei_feluri_sunt_produse(fel):
    """Anti-vacuu: dacă un fel nu se produce niciodată, secțiunea e mai săracă decât pretinde."""
    assert any(x["fel"] == fel for x in limite_verificarii(AZI, inchide_luni=False))
