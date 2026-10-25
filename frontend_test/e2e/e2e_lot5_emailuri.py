# -*- coding: utf-8 -*-
"""Lotul 5 — emailurile și salutul, în browser, pe aplicația din index, pe baza de TEST. Emailurile aplicației de probă stau în cutia de
test (`ICONTA_EMAIL_CUTIE`, `observare._in_cutia_de_test`), de unde proba ia linkul „Dezabonează-te” — linkul pe care altfel numai
destinatarul îl vede.
268 — comanda 4 a lotului 5: „emailurile tranzacționale nu au deloc «Dezabonează-te» și nici antet List-Unsubscribe … Dezabonarea
rămâne numai pe emailurile informative/de promovare” (aici: recomandarea).
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
def patron(browser, request):
    yield from _ecran(browser, request, PATRON)


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


def _recomanda(patron):
    """Contabilul-șef: pagina principală -> banda „Recomandă” -> adresa -> „Trimite invitația”; întoarce mesajul ecranului."""
    pg = patron.pg
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    pg.click("[data-banda='recomanda']")                       # banda de lângă „Suport” (salut.js), nu un card
    pg.wait_for_selector("#rec-emails", timeout=10000)
    pg.fill("#rec-emails", EMAIL)
    pg.click("#rec-trimite")
    pg.wait_for_function("() => { const t = (document.querySelector('#rec-msg') || {innerText: ''}).innerText; "
                         "return t && !t.startsWith('Se trimite'); }", timeout=15000)
    return pg.inner_text("#rec-msg")


# [268] ULTIMUL în fișier: invitațiile superadminului sunt scrieri, iar după orice scriere aplicația pornește recalcularea
# cardurilor în fundal (`firma_rezumat.recalculeaza_in_fundal`), care ține conexiuni din pool cât rulează; pagina principală a
# contabilului, încărcată imediat după, își vede atunci cererile refuzate („connection pool exhausted” pe GET /coada).
def test_def_268_dezabonarea_numai_pe_emailurile_informative(superadmin, patron, browser, request, curat):
    """Superadminul trimite o invitație (tranzacțională) -> emailul din cutie n-are „Dezabonează-te” și nici antete List-Unsubscribe.
    Contabilul-șef recomandă iConta.eu aceleiași adrese (promovare) -> emailul are linkul și antetele -> destinatarul deschide linkul:
    pagina cere confirmarea (deschiderea singură nu dezabonează) și spune că emailurile legate de cont vin în continuare ->
    „Dezabonează-mă” -> a doua recomandare nu mai pleacă, iar contabilul vede de ce -> o nouă invitație pleacă totuși."""
    inainte = len(_scrisori(EMAIL))
    cls, text = _invita(superadmin)
    assert cls == "caseta-info" and text.startswith("Invitația a plecat pe %s." % EMAIL), (cls, text)
    (invitatia,) = _scrisori(EMAIL)[inainte:]
    assert invitatia["subiect"] == "Invitație iConta.eu"
    assert invitatia["antete"] == {} and invitatia["html"].count("Dezabonează-te") == 0, invitatia["html"][-400:]
    superadmin.captura("invitatia_fara_dezabonare")

    assert _recomanda(patron) == "Invitație trimisă către 1 adresă."
    (recomandarea,) = _scrisori(EMAIL)[inainte + 1:]
    m = re.search(r'<a href="([^"]+)"[^>]*>Dezabonează-te</a>', recomandarea["html"])
    assert m, recomandarea["html"][-400:]
    link = m.group(1).replace("&amp;", "&")
    assert recomandarea["antete"] == {"List-Unsubscribe": "<%s>" % link, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}
    parti = urlsplit(link)
    assert parti.scheme == "https" and parti.path == "/public/dezabonare", link
    patron.captura("recomandarea_trimisa")

    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})   # destinatarul: fără cont, din email
    viz = Ecran(ctx.new_page(), request.node.name)
    try:
        vp = viz.pg
        vp.goto(BAZA + parti.path + "?" + parti.query, wait_until="domcontentloaded")
        vp.wait_for_selector("#dz-confirma", timeout=10000)
        assert EMAIL in vp.inner_text("#dz-mesaj")
        assert "confirmări, invitații, resetarea parolei, linkul de logare" in vp.inner_text("#dz-pagina")
        assert sql("SELECT count(*) FROM public.emailuri_dezabonate WHERE email = %s", (EMAIL,)) == [(0,)]   # deschiderea nu dezabonează
        viz.captura("pagina")
        vp.click("#dz-confirma")
        vp.wait_for_function("() => (document.querySelector('#dz-mesaj') || {}).innerText?.startsWith('Gata:')", timeout=10000)
        assert vp.inner_text("#dz-mesaj") == ("Gata: adresa %s e dezabonată. De acum nu mai primești emailurile informative iConta.eu."
                                              % EMAIL)
        assert sql("SELECT count(*) FROM public.emailuri_dezabonate WHERE email = %s", (EMAIL,)) == [(1,)]
        viz.captura("dezabonat")
        vp.goto(BAZA + parti.path + "?e=" + EMAIL + "&s=semnatura-falsa", wait_until="domcontentloaded")   # linkul altcuiva, ghicit
        assert vp.inner_text("#dz-mesaj").startswith("Linkul de dezabonare nu e valid.")
        assert not viz.erori
    finally:
        ctx.close()

    # [lotul 12, 163 — texte fără persoana întâi a aplicației] „Nu am scris la …” -> „Nu s-a trimis la …” (`recomanda.js`)
    assert _recomanda(patron) == "Nu s-a trimis la %s: adresa s-a dezabonat de la recomandări." % EMAIL
    assert len(_scrisori(EMAIL)) == inainte + 2                                  # recomandarea n-a plecat
    patron.captura("a_doua_recomandare")
    sql("DELETE FROM public.invitatii_cabinet WHERE email = %s", (EMAIL,))
    cls, text = _invita(superadmin)                                             # invitația (tranzacțională) pleacă oricum
    assert cls == "caseta-info" and text.startswith("Invitația a plecat pe %s." % EMAIL), (cls, text)
    assert len(_scrisori(EMAIL)) == inainte + 3
    superadmin.captura("invitatia_dupa_dezabonare")
