# -*- coding: utf-8 -*-
"""Lotul 5 — emailurile și salutul, în browser, pe aplicația din index, pe baza de TEST. Emailurile aplicației de probă stau în cutia de
test (`ICONTA_EMAIL_CUTIE`, `observare._in_cutia_de_test`), de unde proba ia linkul „Dezabonează-te” — linkul pe care altfel numai
destinatarul îl vede.
268 — „emailurile tranzacționale (confirmare, invitație, resetare parolă, anunț cabinet nou, alerte) nu au link «Dezabonează-te»”.
269 — „salutul ia ultimul cuvânt din nume («Salut, 253» pentru «Test 253»)”.
C37 — numele scris de om ajungea în pagină ca HTML (salutul, bara de sus): se afișează ca text."""
import os
import re
from urllib.parse import urlsplit

import pytest

from conftest import BAZA, LAT, INALT, Ecran, _ecran, sesiune, sql
from e2e_inregistrare_libera import _scrisori

EMAIL = "e2e.dezabonare@exemplu.ro"
PATRON = "patron@prisma-cont.test"


@pytest.fixture()
def superadmin(browser, request):
    yield from _ecran(browser, request, "admin@prisma-cont.test")


@pytest.fixture()
def curat():
    def _curata():
        sql("DELETE FROM public.emailuri_dezabonate WHERE email = %s", (EMAIL,))
        sql("DELETE FROM public.invitatii_cabinet WHERE email = %s", (EMAIL,))
    _curata()
    yield
    _curata()


def _invita(superadmin):
    """Superadminul: Panou Admin -> „Invitații cabinete” -> emailul -> „Trimite invitația”."""
    pg = superadmin.pg
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    pg.click("button.cab-card:has([data-cheie='invitatii'])")
    pg.wait_for_selector("#inv-email", timeout=10000)
    pg.fill("#inv-email", EMAIL)
    pg.click("#inv-trimite")
    pg.wait_for_selector("#inv-rezultat", timeout=10000)
    return pg.get_attribute("#inv-rezultat", "class"), pg.inner_text("#inv-rezultat .ca-mesaj, #inv-rezultat .ci-mesaj")


@pytest.fixture()
def patron_cu_numele(request):
    """Numele contabilului-șef de test pus cum îl scrie un om la înregistrare (tot în `nume`, `prenume` gol); la sfârșit, înapoi."""
    (era,) = sql("SELECT nume, prenume FROM public.users WHERE email = %s", (PATRON,))

    def pune(nume):
        sql("UPDATE public.users SET nume = %s, prenume = NULL WHERE email = %s", (nume, PATRON))
    yield pune
    sql("UPDATE public.users SET nume = %s, prenume = %s WHERE email = %s", (era[0], era[1], PATRON))


def _pagina_principala(browser, request, sufix):
    """Contextul se face DUPĂ schimbarea numelui: sesiunea poartă utilizatorul de la logare."""
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    ctx.add_init_script(sesiune(PATRON))
    e = Ecran(ctx.new_page(), "%s_%s" % (request.node.name, sufix))
    e.pg.goto(BAZA + "/", wait_until="domcontentloaded")
    e.pg.wait_for_selector("h1.cab-salut-nume", timeout=30000)
    return ctx, e


def test_def_269_salutul_foloseste_numele_intreg_cand_prenumele_nu_e_scris_separat(browser, request, patron_cu_numele):
    patron_cu_numele("Test 253")
    ctx, e = _pagina_principala(browser, request, "")
    try:
        assert e.pg.inner_text("h1.cab-salut-nume") == "Salut, Test 253"
        e.captura()
        assert not e.erori and not e.cereri_rele
    finally:
        ctx.close()


def test_def_c37_numele_cu_semne_html_se_afiseaza_ca_text(browser, request, patron_cu_numele):
    nume = 'Test <b id="injectat">253</b>'
    patron_cu_numele(nume)
    ctx, e = _pagina_principala(browser, request, "")
    try:
        assert e.pg.inner_text("h1.cab-salut-nume") == "Salut, " + nume          # textul, așa cum l-a scris omul
        assert e.pg.query_selector("#injectat") is None                       # nu un element nou în pagină
        e.captura()
        assert not e.erori and not e.cereri_rele
    finally:
        ctx.close()


# [268] ULTIMUL în fișier: invitațiile superadminului sunt scrieri, iar după orice scriere aplicația pornește recalcularea
# cardurilor în fundal (`firma_rezumat.recalculeaza_in_fundal`), care ține conexiuni din pool cât rulează; pagina principală a
# contabilului, încărcată imediat după, își vede atunci cererile refuzate („connection pool exhausted” pe GET /coada).
def test_def_268_linkul_dezaboneaza_te_din_email_opreste_emailurile_urmatoare(superadmin, browser, request, curat):
    """Superadminul trimite o invitație -> emailul din cutie are linkul „Dezabonează-te” și antetele List-Unsubscribe -> destinatarul
    deschide linkul: pagina cere confirmarea (deschiderea singură nu dezabonează) -> „Dezabonează-mă” -> adresa e în registru -> a doua
    invitație nu mai pleacă, iar superadminul vede de ce."""
    inainte = len(_scrisori(EMAIL))
    cls, text = _invita(superadmin)
    assert cls == "caseta-info" and text.startswith("Invitația a plecat pe %s." % EMAIL), (cls, text)
    scrisori = _scrisori(EMAIL)
    assert len(scrisori) == inainte + 1
    scrisoare = scrisori[-1]
    assert scrisoare["subiect"] == "Invitație iConta.eu"
    m = re.search(r'<a href="([^"]+)"[^>]*>Dezabonează-te</a>', scrisoare["html"])
    assert m, scrisoare["html"][-400:]
    link = m.group(1).replace("&amp;", "&")
    assert scrisoare["antete"] == {"List-Unsubscribe": "<%s>" % link, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}
    parti = urlsplit(link)
    assert parti.scheme == "https" and parti.path == "/public/dezabonare", link
    superadmin.captura("invitatia_trimisa")

    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})   # destinatarul: fără cont, din email
    viz = Ecran(ctx.new_page(), request.node.name)
    try:
        vp = viz.pg
        vp.goto(BAZA + parti.path + "?" + parti.query, wait_until="domcontentloaded")
        vp.wait_for_selector("#dz-confirma", timeout=10000)
        assert EMAIL in vp.inner_text("#dz-mesaj")
        assert "resetarea parolei, linkul de logare" in vp.inner_text("#dz-pagina")
        assert sql("SELECT count(*) FROM public.emailuri_dezabonate WHERE email = %s", (EMAIL,)) == [(0,)]   # deschiderea nu dezabonează
        viz.captura("pagina")
        vp.click("#dz-confirma")
        vp.wait_for_function("() => (document.querySelector('#dz-mesaj') || {}).innerText?.startsWith('Gata:')", timeout=10000)
        assert vp.inner_text("#dz-mesaj") == ("Gata: adresa %s e dezabonată. De acum nu mai primești emailuri de la iConta.eu." % EMAIL)
        assert sql("SELECT count(*) FROM public.emailuri_dezabonate WHERE email = %s", (EMAIL,)) == [(1,)]
        viz.captura("dezabonat")
        vp.goto(BAZA + parti.path + "?e=" + EMAIL + "&s=semnatura-falsa", wait_until="domcontentloaded")   # linkul altcuiva, ghicit
        assert vp.inner_text("#dz-mesaj").startswith("Linkul de dezabonare nu e valid.")
        assert not viz.erori
    finally:
        ctx.close()

    cls, text = _invita(superadmin)                                             # următorul email nu mai pleacă
    assert len(_scrisori(EMAIL)) == inainte + 1
    assert cls == "caseta-atentie"
    assert text.startswith("Emailul către %s nu a plecat: adresa %s s-a dezabonat de la emailurile iConta.eu. Dă-i linkul de mai jos "
                           "direct." % (EMAIL, EMAIL)), text
    superadmin.captura("a_doua_invitatie")
