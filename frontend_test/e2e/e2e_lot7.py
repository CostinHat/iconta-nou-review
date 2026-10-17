# -*- coding: utf-8 -*-
"""Lotul 7 (comanda Costin 17.10.2026, verbatim în DECIZII „Lotul 6 închis”), pe aplicația din index, pe baza de TEST.

2.2 — Setări cont → Notificări: numărul, acordul, codul pe WhatsApp, canalul (implicit email; WhatsApp numai cu numărul confirmat și
acordul). 2.1 — o notificare din clopoțel pleacă pe canalul omului după commit: pe email (cutia de test a aplicației de probă), cu eticheta
tipului și linkul `/deschide/<cheie>`; linkul deschide locul din aplicație."""
import glob
import json
import os
import time

from conftest import BAZA, sql

EMAIL = "patron@prisma-cont.test"


def _uid():
    return sql("SELECT id FROM public.users WHERE email = %s", (EMAIL,))[0][0]


def _reseteaza():
    sql("UPDATE public.users SET canal_notificari = 'email', telefon = NULL, telefon_confirmat_la = NULL, acord_whatsapp_la = NULL "
        "WHERE email = %s", (EMAIL,))


def _wa_inactiv(pg):
    """Proprietatea `disabled` a opțiunii, citită din DOM: `Locator.is_disabled()` nu socotește `<option>` (numai button / select /
    input / textarea), deci ar fi întors mereu False."""
    return pg.eval_on_selector("#not-canal option[value='whatsapp']", "o => o.disabled")


def _deschide_notificari(patron):
    patron.acasa()
    pg = patron.pg
    pg.click("button.cab-card:has([data-cheie='setari'])")
    pg.locator("button.meniu-card", has_text="Notificări").click()
    pg.wait_for_selector("#not-telefon", timeout=20000)
    return pg


def test_l7_setari_cont_notificari_numar_acord_canal(patron):
    """Pașii contabilului: Setări cont → Notificări; scrie un număr greșit — refuzul lângă câmp; scrie 0759 638 499 — „Numărul a fost
    salvat”, „nu e confirmat încă”, opțiunea WhatsApp inactivă cu motivul; bifează acordul și cere codul — WhatsApp nu e activ pe platformă
    (aplicația de probă n-are tokenul): spune asta, acordul rămâne; numărul confirmat (codul primit pe WhatsApp, simulat în bază) ->
    WhatsApp se poate alege și se salvează."""
    _reseteaza()
    try:
        pg = _deschide_notificari(patron)
        assert pg.input_value("#not-canal") == "email", "implicit: email"
        pg.fill("#not-telefon", "07591")
        pg.click("#not-salveaza-telefon")
        pg.wait_for_selector("#not-msg .msg-eroare, #not-telefon ~ .msg-eroare, .msg-eroare", timeout=20000)
        patron.captura("numar_gresit")
        assert "nu e un număr de telefon" in patron.fereastra()
        pg.fill("#not-telefon", "0759 638 499")
        pg.click("#not-salveaza-telefon")
        pg.wait_for_function("() => document.querySelector('#not-stare-telefon').innerText.includes('+40759638499')", timeout=20000)
        assert pg.inner_text("#not-stare-telefon") == "Numărul +40759638499 nu e confirmat încă."
        assert _wa_inactiv(pg), "WhatsApp nu se poate alege înainte de confirmare și acord"
        assert pg.inner_text("#not-motiv-canal") == "WhatsApp: confirmă întâi numărul cu codul primit pe WhatsApp."
        pg.check("#not-acord")
        pg.click("#not-cere-cod")
        pg.wait_for_function("() => document.querySelector('#not-msg').innerText.includes('WhatsApp')", timeout=20000)
        patron.captura("fara_whatsapp_pe_platforma")
        assert "Trimiterea pe WhatsApp nu e încă activă pe iConta.eu. Acordul tău a fost salvat" in pg.inner_text("#not-msg")
        assert sql("SELECT telefon, acord_whatsapp_la IS NOT NULL, canal_notificari FROM public.users WHERE email = %s", (EMAIL,)) == [
            ("+40759638499", True, "email")]

        sql("UPDATE public.users SET telefon_confirmat_la = now() WHERE email = %s", (EMAIL,))   # codul primit pe WhatsApp (simulat)
        pg = _deschide_notificari(patron)
        assert not _wa_inactiv(pg) and pg.inner_text("#not-motiv-canal") == ""
        assert pg.is_hidden("#not-confirmare"), "numărul confirmat nu mai cere cod"
        pg.select_option("#not-canal", "whatsapp")
        pg.click("#not-salveaza-canal")
        pg.wait_for_function("() => document.querySelector('#not-msg').innerText.includes('WhatsApp')", timeout=20000)
        patron.captura("canal_whatsapp")
        assert "Notificările vin pe WhatsApp." in pg.inner_text("#not-msg")
        assert sql("SELECT canal_notificari FROM public.users WHERE email = %s", (EMAIL,)) == [("whatsapp",)]
    finally:
        _reseteaza()


def test_l7_notificarea_pleaca_pe_email_si_linkul_deschide_clopotelul(patron):
    """Pașii: o notificare nouă în clopoțelul contabilului (canalul implicit, email) -> în cel mult 30 + 30 de secunde emailul e în cutia
    aplicației de probă: subiectul = eticheta tipului, fără textul notificării, cu linkul /deschide/notificari; linkul, deschis, arată
    clopoțelul cu notificarea."""
    _reseteaza()
    cutie = os.environ["ICONTA_EMAIL_CUTIE"]
    inainte = set(glob.glob(os.path.join(cutie, "*.json")))
    tag = "E2E-L7-%d" % time.time()
    nid = sql("INSERT INTO public.notificari (user_id, tip, text, link, de_livrat) VALUES (%s, 'de_validat', %s, 'validat:999999902', true) "
              "RETURNING id", (_uid(), "Proba lotului 7 %s: D300 09/2026, 1.234 lei" % tag))[0][0]
    try:
        gasit = None
        for _ in range(60):
            for f in set(glob.glob(os.path.join(cutie, "*.json"))) - inainte:
                e = json.load(open(f, encoding="utf-8"))
                if e["catre"] == EMAIL and e["subiect"] == "iConta.eu — un element nou de validat":
                    gasit = e
            if gasit:
                break
            time.sleep(1)
        assert gasit, "notificarea n-a plecat pe email în 60 de secunde"
        assert tag not in gasit["html"] and "1.234" not in gasit["html"], "fără textul notificării, fără cifre"
        assert "/deschide/notificari" in gasit["html"]
        assert sql("SELECT de_livrat FROM public.notificari WHERE id = %s", (nid,)) == [(False,)]
        patron.acasa()
        pg = patron.pg
        pg.goto(BAZA + "/deschide/notificari", wait_until="domcontentloaded")
        pg.wait_for_selector("#nav-clopot-panou .clopot-item", timeout=30000)
        patron.captura("linkul_deschide_clopotelul")
        assert tag in pg.inner_text("#nav-clopot-panou")
    finally:
        sql("DELETE FROM public.notificari_jurnal WHERE notificare_id = %s", (nid,))
        sql("DELETE FROM public.notificari WHERE id = %s", (nid,))
