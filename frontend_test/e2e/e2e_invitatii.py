# -*- coding: utf-8 -*-
"""Conturile noi de cabinet numai prin invitație (comanda Costin 14.10.2026, pct.3, verbatim în DECIZII „Lotul 2”: „Înregistrarea
liberă se închide: în pilot, conturile noi se creează numai prin invitație.”) — pașii vizitatorului și ai superadminului, în browser,
pe aplicația din index, pe baza de TEST (fără Brevo: emailul nu pleacă, linkul se ia de pe ecran, ca la „dă-i linkul direct”)."""
import os

import pytest

from conftest import BAZA, LAT, INALT, Ecran, _ecran, sql

EMAIL = "e2e.invitatie@exemplu.ro"
CABINET = "E2E Probă Cabinet Invitat"


def _curata():
    """Cabinetul creat de probă + invitațiile lui: generic, pe coloanele `user_id` / `accounting_firm_id` din `public` (nu o listă
    scrisă de mână, care rămâne în urma tabelelor noi)."""
    def tabele(col):
        return [r[0] for r in sql("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t "
                                  "ON t.table_schema = c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' "
                                  "WHERE c.table_schema = 'public' AND c.column_name = %s AND c.table_name NOT IN ('users', "
                                  "'accounting_firms')", (col,))]
    uids = [r[0] for r in sql("SELECT id FROM public.users WHERE email = %s", (EMAIL,))]
    fids = [r[0] for r in sql("SELECT id FROM public.accounting_firms WHERE nume = %s", (CABINET,))]
    sql("DELETE FROM public.invitatii_cabinet WHERE email = %s", (EMAIL,))
    sql("DELETE FROM public.acord_termeni WHERE email = %s", (EMAIL,))
    if uids:
        for t in tabele("user_id"):
            sql('DELETE FROM public."%s" WHERE user_id = ANY(%%s)' % t, (uids,))
        sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))
    if fids:
        for t in tabele("accounting_firm_id"):
            sql('DELETE FROM public."%s" WHERE accounting_firm_id = ANY(%%s)' % t, (fids,))
        sql("DELETE FROM public.accounting_firms WHERE id = ANY(%s)", (fids,))


@pytest.fixture()
def superadmin(browser, request):
    yield from _ecran(browser, request, "admin@prisma-cont.test")


@pytest.fixture()
def vizitator(browser, request):
    """O pagină FĂRĂ cont (vizitatorul paginii publice)."""
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    e = Ecran(ctx.new_page(), request.node.name)
    yield e
    erori, rele = list(e.erori), list(e.cereri_rele)
    ctx.close()
    assert not erori, "erori JavaScript pe ecran: %s" % erori[:3]
    assert not rele, "cereri cu răspuns 5xx: %s" % rele[:3]


def mod_inregistrare(mod):
    """[15.10.2026, lotul 4] Pune comutatorul înregistrării (`public.setari_platforma`) și întoarce valoarea de dinainte."""
    era = sql("SELECT valoare FROM public.setari_platforma WHERE cheie = 'inregistrare'")
    sql("INSERT INTO public.setari_platforma (cheie, valoare) VALUES ('inregistrare', %s) ON CONFLICT (cheie) DO UPDATE SET "
        "valoare = EXCLUDED.valoare", (mod,))
    return era[0][0] if era else None


@pytest.fixture()
def numai_invitatie():
    """Comutatorul pe „numai prin invitație” cât ține testul (invitația trebuie să meargă și cu înregistrarea închisă)."""
    era = mod_inregistrare("invitatie")
    yield
    mod_inregistrare(era or "invitatie")


@pytest.fixture()
def fara_cabinet_de_proba():
    _curata()
    yield
    _curata()


def _client_nou(pg, url):
    pg.goto(url, wait_until="domcontentloaded")
    if not pg.query_selector("#pr-continua"):
        pg.wait_for_selector("#pagina-acces-btn", timeout=20000)
        pg.click("#pagina-acces-btn")
        pg.click("#acces-client-nou")
    pg.wait_for_selector("#pr-continua", timeout=20000)
    pg.click("#pr-continua")


def test_invitatie_fara_link_client_nou_nu_mai_deschide_formularul(vizitator, numai_invitatie):
    from core import setari_platforma
    pg = vizitator.pg
    _client_nou(pg, BAZA + "/")
    pg.wait_for_selector("#fi-mesaj", timeout=10000)
    assert pg.inner_text("#fi-mesaj") == setari_platforma.MESAJ_NUMAI_INVITATIE
    assert pg.query_selector("#reg-email") is None          # formularul de cont nu apare deloc
    vizitator.captura()


def _invita(superadmin):
    """Superadminul: Panou Admin -> „Invitații cabinete” -> emailul -> „Trimite invitația”. Întoarce linkul de pe ecran."""
    pg = superadmin.pg
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    pg.click("button.cab-card:has([data-cheie='invitatii'])")
    pg.wait_for_selector("#inv-email", timeout=10000)
    pg.fill("#inv-email", EMAIL)
    pg.click("#inv-trimite")
    pg.wait_for_selector("#inv-link", timeout=10000)
    return pg.input_value("#inv-link")


def test_def_c34_invitatia_spune_cand_emailul_n_a_plecat(superadmin, fara_cabinet_de_proba):
    """Emailul NU pleacă, iar ecranul trebuie s-o spună (15.10.2026: scria „Invitația a plecat”). [15.10.2026, lotul 4] Aplicația de
    probă scrie emailurile în cutia de test; o cutie needitabilă e emailul care n-a plecat."""
    cutie = os.environ["ICONTA_EMAIL_CUTIE"]
    os.makedirs(cutie, exist_ok=True)
    os.chmod(cutie, 0o500)
    try:
        _invita(superadmin)
    finally:
        os.chmod(cutie, 0o700)
    pg = superadmin.pg
    assert pg.get_attribute("#inv-rezultat", "class") == "caseta-atentie"
    assert pg.inner_text("#inv-rezultat .ca-mesaj") == ("Emailul către %s nu s-a putut trimite — dă-i linkul de mai jos direct. "
                                                        "Linkul (valabil 14 zile, o singură folosire):" % EMAIL)
    superadmin.captura()


def test_invitatie_superadminul_invita_iar_linkul_creeaza_contul_o_singura_data(superadmin, browser, request, fara_cabinet_de_proba,
                                                                                numai_invitatie):
    link = _invita(superadmin)
    pg = superadmin.pg
    assert link.split("#invitatie=")[0] == os.environ["ICONTA_BAZA_URL"] + "/"   # adresa publică a aplicației, din același mediu
    assert len(link.split("#invitatie=")[1]) == 43                 # token_urlsafe(32)
    assert pg.locator("#inv-lista tbody tr", has_text=EMAIL).count() == 1
    superadmin.captura("superadmin")

    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    viz = Ecran(ctx.new_page(), request.node.name)
    try:
        vp = viz.pg
        url = BAZA + "/#invitatie=" + link.split("#invitatie=")[1]
        _client_nou(vp, url)
        vp.wait_for_selector("#reg-email", timeout=10000)
        assert vp.input_value("#reg-email") == EMAIL
        assert vp.get_attribute("#reg-email", "readonly") == ""     # emailul invitat nu se schimbă
        vp.fill("#reg-cabinet", CABINET)
        vp.fill("#reg-nume-admin", "Popescu Ana")
        vp.fill("#reg-parola", "ParolaE2e!2026x")
        vp.fill("#reg-parola2", "ParolaE2e!2026x")
        vp.check("#reg-termeni")
        viz.captura("formular")
        vp.click("#reg-buton")
        vp.wait_for_selector(".cab-grila", timeout=30000)           # contul s-a creat și a intrat în aplicație
        assert sql("SELECT count(*) FROM public.users WHERE email = %s", (EMAIL,))[0][0] == 1
        assert sql("SELECT folosita_la IS NOT NULL FROM public.invitatii_cabinet WHERE email = %s", (EMAIL,))[0][0] is True
        assert "#invitatie=" not in vp.url                          # linkul consumat nu mai stă în bară
        assert not viz.erori and not viz.cereri_rele
    finally:
        ctx.close()

    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    viz = Ecran(ctx.new_page(), request.node.name)
    try:
        vp = viz.pg
        _client_nou(vp, url)                                        # același link, a doua oară
        vp.wait_for_selector("#fi-mesaj.caseta-atentie", timeout=10000)
        assert vp.inner_text("#fi-mesaj") == "Invitația a fost folosită deja: contul cabinetului există. Intră în cont."
        assert vp.query_selector("#reg-email") is None
        viz.captura("refolosita")
    finally:
        ctx.close()
