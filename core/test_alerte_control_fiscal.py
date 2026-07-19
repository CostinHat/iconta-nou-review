# -*- coding: utf-8 -*-
"""Teste gardian pentru alerte_control_fiscal — stratul pull->push al controlului fiscal.
Punctul CRITIC = dedup (decide): un rosu persistent = O SINGURA alerta, nu una pe zi.
"""
from core.alerte_control_fiscal import decide, text_alerta


# ---- DEDUP (gardul critic) ----

def test_rosu_nou_pe_firma_notifica():
    noi, rez, notif = decide({"d112"}, set())
    assert notif is True
    assert noi == {"d112"} and rez == set()


def test_rosu_persistent_NU_renotifica():
    # firma are d112 rosu, deja notificat -> a doua zi (si a doua rulare) NU se re-notifica
    noi, rez, notif = decide({"d112"}, {"d112"})
    assert notif is False
    assert noi == set() and rez == set()


def test_verificator_rosu_nou_pe_firma_deja_alertata_notifica():
    # d112 era deja notificat; acum apare si d390 -> se notifica (doar d390 e nou)
    noi, rez, notif = decide({"d112", "d390"}, {"d112"})
    assert notif is True
    assert noi == {"d390"} and rez == set()


def test_rosu_rezolvat_se_sterge_din_jurnal_fara_notificare():
    # d112 nu mai e rosu (rezolvat) -> iese din jurnal, dar rezolvarea NU notifica
    noi, rez, notif = decide(set(), {"d112"})
    assert notif is False
    assert noi == set() and rez == {"d112"}


def test_rosu_rezolvat_apoi_reaparut_notifica_din_nou():
    # runda 1: rezolvat -> jurnalul se goleste (rez); runda 2: reapare cu jurnal gol -> NOU
    _, rez1, notif1 = decide(set(), {"d112"})
    assert notif1 is False and rez1 == {"d112"}     # sters din jurnal
    noi2, _, notif2 = decide({"d112"}, set())        # jurnal golit -> regresie = nou
    assert notif2 is True and noi2 == {"d112"}


def test_gri_verde_nu_pusheaza():
    # verificatori_rosii intoarce DOAR rosii; gri/verde -> set gol -> zero push
    noi, rez, notif = decide(set(), set())
    assert notif is False and noi == set()


def test_doua_rulari_aceeasi_zi_o_singura_alerta():
    # rularea 1: rosu nou -> notifica, se scrie in jurnal {d112}
    noi1, _, notif1 = decide({"d112"}, set())
    assert notif1 is True
    jurnal = set(noi1)                                # ce s-a scris in jurnal dupa runda 1
    # rularea 2 (aceeasi zi): acelasi rosu, jurnalul deja contine d112 -> NU re-notifica
    noi2, _, notif2 = decide({"d112"}, jurnal)
    assert notif2 is False and noi2 == set()


# ---- TEXT agregat per firma ----

def test_text_agregat_o_singura_notificare_per_firma():
    t = text_alerta("DANTE SA", [("tva", "TVA"), ("d112", "D112 (salarii)"), ("d390", "D390 (intracom.)")])
    assert "DANTE SA" in t
    assert "3 controale fiscale în roșu" in t
    assert "TVA" in t and "D112" in t and "D390" in t


def test_text_singular_un_control():
    t = text_alerta("Firma X", [("d112", "D112 (salarii)")])
    assert "1 control fiscal în roșu" in t
    assert "D112" in t
