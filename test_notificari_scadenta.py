# -*- coding: utf-8 -*-
"""Teste F131 comp.5 — logica de prag (stadiu curent) + email valid. PUR, obiectiv."""
from datetime import date, timedelta
from core.notificari_scadenta import prag_curent, email_valid

AZI = date(2026, 6, 15)
def scad(d):
    """Scadenta pt care (azi - scadenta).days == d (pozitiv = restanta)."""
    return AZI - timedelta(days=d)


def test_prag_inainte_de_scadenta_in_fereastra():
    assert prag_curent(scad(-3), AZI, set()) == -3      # exact 3 zile inainte

def test_prag_prea_devreme_nu_trimite():
    assert prag_curent(scad(-5), AZI, set()) is None     # 5 zile inainte, inainte de -3

def test_prag_curent_supersedeaza_fara_backfill():
    # d=+1: chiar daca -3 n-a fost trimis, stadiul curent e +1 (nu backfill -3)
    assert prag_curent(scad(1), AZI, set()) == 1

def test_prag_deja_trimis_nu_repeta():
    assert prag_curent(scad(1), AZI, {1}) is None

def test_zi_ratata_de_cron_nu_pierde_notificarea():
    # cronul a ratat ziua +1; ruleaza la +5; stadiul curent e tot +1 (7 neatins) -> se trimite
    assert prag_curent(scad(5), AZI, set()) == 1

def test_stadiu_nou_dupa_7_zile():
    assert prag_curent(scad(7), AZI, {-3, 1}) == 7

def test_dupa_ultimul_prag_nu_mai_trimite():
    assert prag_curent(scad(20), AZI, {7}) is None       # fara +14: nu mai spam-uieste

def test_fara_scadenta():
    assert prag_curent(None, AZI, set()) is None

def test_intre_scadenta_si_prima_restanta_ramane_pe_minus3():
    # d=0 (ziua scadentei): stadiul curent e tot -3 (deja trimis) -> None
    assert prag_curent(scad(0), AZI, {-3}) is None


def test_email_valid():
    assert email_valid("client@firma.ro")
    assert email_valid(" a.b@c.d.ro ")
    assert not email_valid("")
    assert not email_valid(None)
    assert not email_valid("fara-arond")
    assert not email_valid("x@y")          # fara punct in domeniu
