# -*- coding: utf-8 -*-
"""core/test_aplicatii_migrare.py — gardurile registrului aplicațiilor din care se migrează (deficiența 270, comanda Costin 15.10.2026,
verbatim în DECIZII: „Activ e doar butonul unei aplicații ale cărei exporturi iConta le citește deja (azi SAGA) … Celelalte butoane sunt
inactive și devin active fără alte modificări de ecran când iConta începe să le citească exportul.”).

Ce fac imposibil:
- un buton activ fără cititor în spate: „activ” e derivat din pașii citiți, iar un pas „citit” trebuie să-și CITEASCĂ proba — un export
  al aplicației (aceleași fișiere inventate, cu antetele din manualul SAGA, ca `core/test_import_saga.py`); un pas declarat citit fără
  probă pică;
- un pas cu cititor, dar fără exportul descris (omul n-ar ști ce să scoată) sau fără sursa din manual;
- o aplicație care devine activă numai pe ecran: ecranul nu are nicio listă de aplicații (le ia de la `/migrare/aplicatii`).
Temei: N/A — registru de ecran (tooling).
"""
import os
import re

import pytest

from core import aplicatii_migrare as am
from core import migrare_api
from core.test_import_saga import BALANTA_SAGA, MF_SAGA, SALARIATI_SAGA, SITUATIE_CLIENTI, _cp1250

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: (aplicație, pas) -> (octeții exportului, numele fișierului, argumente în plus, câte rânduri trebuie citite)
PROBE = {
    ("saga", "solduri"): (_cp1250(BALANTA_SAGA), "balanta_saga.csv", {}, 4),
    ("saga", "solduri_parteneri"): (SITUATIE_CLIENTI.encode("utf-8"), "clienti_saga.csv", {"cont_implicit": "4111"}, 2),
    ("saga", "salariati"): (_cp1250(SALARIATI_SAGA), "salariati_saga.csv", {}, 2),
    ("saga", "mijloace_fixe"): (_cp1250(MF_SAGA), "imobilizari_saga.csv", {}, 2),
}


def _randuri(rez):
    return rez["randuri"] if isinstance(rez, dict) else rez


def test_cheile_pasilor_sunt_pasii_migrarii():
    """Un pas cu o cheie care nu e în `migrare_api.STRATURI` n-ar apărea pe ecran niciodată (ecranul desenează pașii lui)."""
    straine = [(a.cheie, k) for a in am.APLICATII for k in a.pasi if k not in migrare_api.STRATURI]
    assert not straine, straine


def test_fiecare_pas_cu_cititor_are_exportul_si_sursa_din_manual():
    """Un cititor fără exportul descris ar face aplicația activă cu un pas care nu spune ce să scoți; sursa trebuie să fie fișierul
    salvat al manualului (cu amprenta lui), nu memoria."""
    rele = []
    for a in am.APLICATII:
        for k, p in a.pasi.items():
            if p.cititor and not (p.export or "").strip():
                rele.append((a.cheie, k, "fără export"))
            if p.cititor and not (p.sursa and os.path.isfile(os.path.join(RAD, p.sursa))
                                  and os.path.isfile(os.path.join(RAD, p.sursa + ".sha256"))):
                rele.append((a.cheie, k, "sursa %r lipsește sau n-are amprenta" % (p.sursa,)))
    assert not rele, rele


@pytest.mark.parametrize("cheie_apl, cheie_pas", [(a.cheie, k) for a in am.APLICATII for k, p in a.pasi.items() if p.cititor])
def test_pasul_citit_isi_citeste_proba_exportului(cheie_apl, cheie_pas):
    """Un pas e „citit” numai dacă cititorul lui chiar citește un export al aplicației. Un pas nou fără probă aici pică: întâi proba
    (un fișier cu antetele din manualul aplicației), apoi butonul activ. MUTAȚIA: cititorul balanței înlocuit cu cel al asociaților
    -> nu găsește antetul -> ROȘU."""
    assert (cheie_apl, cheie_pas) in PROBE, "pasul %s/%s e declarat citit, dar n-are probă de export" % (cheie_apl, cheie_pas)
    octeti, nume, extra, cate = PROBE[(cheie_apl, cheie_pas)]
    pas = dict((a.cheie, a) for a in am.APLICATII)[cheie_apl].pasi[cheie_pas]
    rez = am.cititor(pas.cititor)(octeti, nume, **extra)
    assert len(_randuri(rez)) == cate, rez


def test_activ_e_derivat_din_pasii_cititi(monkeypatch):
    """Azi: SAGA activă (are pași citiți), WinMentor, Ciel, SmartBill inactive. Adăugarea unui pas citit la WinMentor (numai în registru)
    o face activă — fără nimic altceva. Un pas cu cititor, dar fără export, NU o face activă. MUTAȚIA: `activa` = True -> ROȘU."""
    stare = {r["cheie"]: r["activa"] for r in am.registru()}
    assert stare == {"saga": True, "winmentor": False, "ciel": False, "smartbill": False}, stare
    assert [r["nume"] for r in am.registru()] == ["SAGA", "WinMentor", "Ciel", "SmartBill"]
    wm = am.Aplicatie("winmentor", "WinMentor", {"solduri": am.Pas("", "x", "core.solduri_api:extrage_balanta_detaliat")})
    monkeypatch.setattr(am, "APLICATII", (am.APLICATII[0], wm) + am.APLICATII[2:])
    assert {r["cheie"]: r["activa"] for r in am.registru()}["winmentor"] is False   # cititor fără export: nu e citit
    wm = am.Aplicatie("winmentor", "WinMentor", {"solduri": am.Pas("balanța", "x", "core.solduri_api:extrage_balanta_detaliat")})
    monkeypatch.setattr(am, "APLICATII", (am.APLICATII[0], wm) + am.APLICATII[2:])
    r = {x["cheie"]: x for x in am.registru()}["winmentor"]
    assert r["activa"] is True and r["pasi"] == {"solduri": {"export": "balanța"}}, r


def test_ecranul_nu_are_lista_lui_de_aplicatii():
    """Ecranul ia aplicațiile de la server (`/migrare/aplicatii`, probat în e2e `test_def_270_…`); o listă scrisă în JS (numele unei
    aplicații, un „activ” de mână) ar face butonul să nu urmeze registrul. MUTAȚIA: „WinMentor” scris în migrare.js -> ROȘU."""
    js = open(os.path.join(RAD, "static", "js", "ecrane", "migrare.js"), encoding="utf-8").read()
    gasite = [a.nume for a in am.APLICATII if re.search(r"\b%s\b" % re.escape(a.nume), js)]
    assert not gasite, "numele aplicațiilor scrise în migrare.js: %s" % gasite
