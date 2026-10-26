# -*- coding: utf-8 -*-
"""Lotul 13, salarizarea — pașii comuni pe ecranele noi (677 / 673–676): statul de plată e un tabel cu un rând pe salariat, rândul deschide
fereastra salariatului (cu butoanele lui și compoziția netului pe trei coloane), iar listele scurte sunt butoane alăturate. Folosiți de
testele lotului 13 și de testele mai vechi ale salarizării, ca pașii contabilului să fie scriși o singură dată."""
_F = ".fereastra:last-of-type "


def deschide_salariat(ecran, nume=None):
    """Din statul de plată (deschis): rândul salariatului `nume` (sau primul) -> fereastra lui, cu butoanele (675)."""
    pg = ecran.pg
    rand = _F + "#sp-tabel tbody tr.sp-rand" + (":has-text(%r)" % nume if nume else "")
    pg.wait_for_selector(rand, timeout=30000)
    pg.locator(rand).first.locator(".sp-deschide").click()
    pg.wait_for_selector(_F + "#ss-butoane", timeout=30000)
    return pg


def deschide_salariat_id(ecran, sid):
    """Ca `deschide_salariat`, după id-ul salariatului (rândul `tr.sp-rand[data-sid]`)."""
    pg = ecran.pg
    rand = _F + "#sp-tabel tbody tr.sp-rand[data-sid='%s']" % sid
    pg.wait_for_selector(rand, timeout=30000)
    pg.click(rand + " .sp-deschide")
    pg.wait_for_selector(_F + "#ss-butoane", timeout=30000)
    return pg


def buton(ecran, cheie):
    """Un buton al fereastra salariatului (`data-<cheie>`), apăsat: fiecare deschide o fereastră nouă (673)."""
    ecran.pg.click(_F + "#ss-butoane [data-%s]" % cheie)


def alege(ecran, camp, valoare):
    """Lista scurtă (676): butonul cu valoarea `valoare` al grupului câmpului `camp`."""
    ecran.pg.click(_F + ".alegere-butoane:has(+ #%s) button[data-valoare='%s']" % (camp, valoare))


def coloane(ecran):
    """Compoziția netului din fereastra salariatului: {etichetă: (valoare, net)} citit din rândurile celor trei coloane (677)."""
    return ecran.pg.eval_on_selector_all(
        _F + "#ss-compozitie tr[data-eticheta]",
        "rs => Object.fromEntries(rs.map(r => [r.dataset.eticheta, [r.dataset.valoare === '' ? null : Number(r.dataset.valoare),"
        " r.dataset.net === undefined ? null : Number(r.dataset.net)]]))")


def text_compozitie(ecran):
    return ecran.pg.inner_text(_F + "#ss-compozitie")


def contare_deschisa(ecran):
    """„Contabilizează statul” deschide fereastra contabilizării DUPĂ ce propunerea vine de la server (lotul 13, 673): se așteaptă
    fereastra ei (titlul), nu `#sp-contare-zona` — statul are și el o zonă cu același id (starea notei), deci o așteptare pe zonă
    trece înaintea ferestrei, iar pasul următor lucrează pe stat."""
    ecran.pg.wait_for_selector(_F + "h2.pf-titlu:has-text('Contabilizarea statului')", timeout=30000)


def inchide(ecran):
    """X-ul ferestrei de sus nu e „înapoi”: săgeata întoarce la fereastra de dedesubt (salariatul, statul)."""
    ecran.pg.click(_F + ".nav-inapoi")
