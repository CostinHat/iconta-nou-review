# -*- coding: utf-8 -*-
"""Lotul 7, comanda 7.2 (Costin 17.10.2026, verbatim în DECIZII „Comanda 7.2”): contul și începutul — 315, 319, 320, titlul din
Notificări (pct.2) — pe aplicația din index, pe baza de TEST. Cabinetul de probă al lui 319 / 320 se creează pe drumul aplicației
(`auth_api.inregistreaza_cabinet`) și se scoate la final."""
import io
import os
import secrets
import time

import pytest

from conftest import BAZA, _ecran, sql, cui_cu_control
from curatenie import PREFIX_FIRMA

PAROLA = secrets.token_urlsafe(12) + "!Aa1"   # generată la rulare (garda secretelor din git), ca în `e2e_inregistrare_libera.py`


def _scoate_cabinetul(firm_id, uids):
    tabele = lambda col: [r[0] for r in sql(  # noqa: E731
        "SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t ON t.table_schema = c.table_schema AND "
        "t.table_name = c.table_name AND t.table_type = 'BASE TABLE' WHERE c.table_schema = 'public' AND c.column_name = %s AND "
        "c.table_name NOT IN ('users', 'accounting_firms', 'tenants')", (col,))]
    from conftest import _scoate_firmele_e2e
    for (tid,) in sql("SELECT id FROM public.tenants WHERE accounting_firm_id = %s", (firm_id,)):
        _scoate_firmele_e2e(tid)
    for t in tabele("user_id"):
        sql('DELETE FROM public."%s" WHERE user_id = ANY(%%s)' % t, (uids,))
    sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))
    for t in tabele("accounting_firm_id"):
        sql('DELETE FROM public."%s" WHERE accounting_firm_id = %%s' % t, (firm_id,))
    sql("DELETE FROM public.accounting_firms WHERE id = %s", (firm_id,))


@pytest.fixture()
def cabinet_nou():
    """Un cabinet nou, cu administratorul lui, fără nimic făcut: {email, uid, firm_id}."""
    from core import auth_api, db
    email = "e2e-inceput-%d@prisma-cont.test" % (int(time.time() * 1000) % 100000000)
    with db.get_conn() as c:
        r = auth_api.inregistreaza_cabinet(c, email, PAROLA, "Cabinet E2E început %s" % email[12:20], nume="Admin E2E", prenume="Ioana")
        c.commit()
    assert r["ok"], r
    # prezentarea de bun venit (bun_venit_v1, altă funcție) e văzută: sesiunea de test se scrie o dată, la pornire, deci altfel ar reveni
    # peste carduri la fiecare reîncărcare; în aplicație fanionul se salvează pe server la închidere
    sql("UPDATE public.users SET bun_venit_vazut_la = now() WHERE id = %s", (r["user_id"],))
    try:
        yield {"email": email, "uid": r["user_id"], "firm_id": r["firm_id"]}
    finally:
        _scoate_cabinetul(r["firm_id"], [r["user_id"]])


def deschide_setari_panou(e, titlu, asteapta):
    """Setări cont -> ecranul `titlu` (pe drumul omului: cardul „Setări cont”, apoi elementul din meniu)."""
    e.acasa()
    e.pg.click("button.cab-card:has([data-cheie='setari'])")
    e.pg.locator("button.meniu-card", has_text=titlu).first.click()
    e.pg.wait_for_selector(".fereastra:last-of-type " + asteapta, timeout=20000)


def _card(pg, cheie):
    return "#inceput-carduri .inceput-card[data-card='%s']" % cheie


def _facut(pg, cheie):
    return "inceput-facut" in (pg.get_attribute(_card(pg, cheie), "class") or "")


def test_def_319_cardurile_administratorului_cu_textul_aprobat_se_bifeaza_din_ecranele_reale(browser, request, cabinet_nou):
    """319. Cardurile de bun venit ale administratorului cabinetului, cu textul aprobat (numele ecranelor, butoanelor și verificările
    auditului de preluare aliniate cu cele reale).
    Pașii administratorului unui cabinet nou: pagina principală -> „Primii pași”, trei carduri, nefăcute, fără „închide”: textul aprobat
    (pașii, nota, „Cardul devine verde când …”); „Deschide Migrare cabinet” deschide Migrare cabinet; „Lucrez singur” -> pasul 3 verde;
    certificatul conectat și notificările salvate -> pasul 2 verde; o firmă cu balanța importată și auditul de preluare făcut -> pasul 1
    verde -> toate făcute: cardurile dispar, iar „?” le arată, verzi, la „Primii pași”."""
    from core import uc_inceput as ui
    gen = _ecran(browser, request, cabinet_nou["email"])
    e = next(gen)
    try:
        pg = e.pg
        e.acasa()
        pg.wait_for_selector(_card(pg, "echipa"), timeout=30000)
        titluri = pg.eval_on_selector_all("#inceput-carduri .inceput-titlu", "hs => hs.map((h) => h.innerText.trim())")
        assert titluri == [c["titlu"] for c in ui.CARDURI_ADMIN], titluri
        for s in pg.locator("#inceput-carduri .inceput-card > details.dec-xml > summary").all():   # [lotul 12, 596] pașii stau pliați în „Cum se face”
            s.click()
        text = pg.inner_text("#inceput-carduri")
        for c in ui.CARDURI_ADMIN:
            for p in c["pasi"]:
                assert p in text, p
            assert c["verde"] in text and c["ce_faci"] in text
        assert ui.CARDURI_ADMIN[0]["nota"] in text
        assert "Exportă din ea, pe rând, patru fișiere: balanța de verificare la sfârșitul ultimei luni închise" in text
        assert pg.locator("#inceput-carduri [aria-label='închide'], #inceput-carduri .inceput-inchide").count() == 0
        assert not any(_facut(pg, k) for k in ("preluare", "anaf", "echipa"))
        e.captura("nefacute")
        pg.click(_card(pg, "preluare") + " [data-inceput='migrare']")
        pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return !!f && f.innerText.includes('Migrare cabinet'); }",
                             timeout=20000)
        e.acasa()
        pg.click(_card(pg, "echipa") + " [data-inceput='lucrez_singur']")
        pg.wait_for_function("(s) => (document.querySelector(s) || {className: ''}).className.includes('inceput-facut')",
                             arg=_card(pg, "echipa"), timeout=20000)
        from core import spv_conector as sc
        tok = sql("INSERT INTO public.spv_token (accounting_firm_id, serial_certificat, access_token, refresh_token, access_expira, "
                  "refresh_expira, activ) VALUES (%s, 'E2E-319', %s, %s, now() + interval '30 days', now() + interval '300 days', true) "
                  "RETURNING id", (cabinet_nou["firm_id"], sc.cripteaza("x.e30.y"), sc.cripteaza("r")))[0][0]
        from e2e_bloc_a import _api
        assert _api(e, "PUT", "/eu/notificari", {"canal": "email", "tipuri": {}})["status"] == 200
        e.acasa()
        pg.wait_for_selector(_card(pg, "anaf"), timeout=20000)
        assert _facut(pg, "anaf") and _facut(pg, "echipa") and not _facut(pg, "preluare")
        e.captura("doi_din_trei")
        from core import db, tenant_provisioning as tp
        rad = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with db.get_conn() as c:
            t = tp.provision_tenant(c, PREFIX_FIRMA + " 319 SRL", cui_cu_control(70000000 + int(time.time()) % 9000000), cabinet_nou["firm_id"],
                                    cabinet_nou["uid"], io.open(os.path.join(rad, "tenant_template.sql"), encoding="utf-8").read())
            c.commit()
        s = t["schema_name"]
        sql('INSERT INTO "%s".solduri_initiale (cont, sold_debitor, sold_creditor) VALUES (\'5311\', 100, 0)' % s)
        sql('INSERT INTO "%s".artefacte_produse (fel, cheie, exemplar, continut, amprenta) VALUES (\'audit_preluare\', \'2026\', 1, '
            '\'{}\', \'e2e\')' % s)
        e.acasa()
        pg.wait_for_timeout(1500)
        assert pg.locator("#inceput-carduri .inceput-card").count() == 0, "toate făcute: cardurile dispar"
        e.captura("toate_facute")
        pg.click("#nav-ghid")
        pg.wait_for_selector("#ans-inceput .inceput-card", timeout=20000)
        assert pg.locator("#ans-inceput .inceput-card.inceput-facut").count() == 3
        e.captura("ghidul_din_semnul_intrebarii")
        sql("DELETE FROM public.spv_token WHERE id = %s", (tok,))
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


def test_def_320_prima_intrare_cere_telefonul_canalul_si_bifele_grupate_dupa_drepturi(browser, request, cabinet_nou):
    """320. Carduri de început și notificări pe tipuri: la prima intrare telefonul, canalul și bifele sunt obligatorii; în Notificări
    toate tipurile care te privesc, grupate, cu un rând despre ce face aplicația; termenele și validările bifate din oficiu; emailurile
    contului în afara listei.
    Pașii administratorului unui cabinet nou, la prima intrare: „Înainte de a începe”, „Continuă în aplicație” blocat; grupele „Termene
    și declarații”, „Facturi și SPV”, „Validări”, „Clienți”, „Cont și echipă”, cu rândul fiecărui tip; bifate din oficiu numai termenele și
    validările; nota emailurilor de cont; „Salvează” fără telefon -> refuzul la telefon; numărul salvat, apoi „Salvează” -> „Continuă”
    se deblochează -> pagina principală. Un asistent fără „Poate valida” nu vede „un element nou de validat”."""
    from conftest import sesiune
    ctx = browser.new_context(viewport={"width": 1500, "height": 1100})
    ctx.add_init_script(sesiune(cabinet_nou["email"], prima_intrare=True))
    pg = ctx.new_page()
    try:
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector("#prima-intrare #not-tipuri .not-grup", timeout=30000)
        assert pg.eval_on_selector("#pi-continua", "b => b.disabled") is True
        grupe = pg.eval_on_selector_all("#not-tipuri .cf-grup-titlu", "gs => gs.map((g) => g.textContent.trim())")
        assert grupe == ["Termene și declarații", "Facturi și SPV", "Validări", "Clienți", "Cont și echipă"], grupe
        bifate = pg.eval_on_selector_all("#not-tipuri [data-tip]", "cs => cs.filter((c) => c.checked).map((c) => c.dataset.tip)")
        assert set(bifate) == {"termen_declaratie", "declaratie_reluata", "depusa", "control_fiscal", "de_validat", "aprobata",
                               "respinsa"}, bifate
        assert "Emailurile contului" in pg.inner_text("#not-tipuri") and "pleacă mereu" in pg.inner_text("#not-tipuri")
        assert "Cu trei zile înainte de termenul unei declarații" in pg.inner_text("#not-tipuri")
        pg.screenshot(path=os.path.join(os.environ.get("E2E_CAPTURI", "/tmp"), "320_prima_intrare.png"), full_page=True)
        pg.click("#not-salveaza-canal")
        pg.wait_for_function("() => document.querySelector('#not-msg').innerText.includes('telefon')", timeout=10000)
        assert pg.eval_on_selector("#pi-continua", "b => b.disabled") is True
        pg.fill("#not-telefon", "0700000001")
        pg.click("#not-salveaza-telefon")
        pg.wait_for_function("() => document.querySelector('#not-stare-telefon').innerText.includes('+40700000001')", timeout=10000)
        pg.uncheck("#not-tipuri [data-tip='control_fiscal']")
        pg.click("#not-salveaza-canal")
        pg.wait_for_function("() => !document.querySelector('#pi-continua').disabled", timeout=10000)
        pg.click("#pi-continua")
        pg.wait_for_selector(".cab-grila", timeout=30000)
        pg.screenshot(path=os.path.join(os.environ.get("E2E_CAPTURI", "/tmp"), "320_dupa_prima_intrare.png"))
        r = sql("SELECT notificari_tipuri->>'control_fiscal', notificari_salvate_la IS NOT NULL FROM public.users WHERE id = %s",
                (cabinet_nou["uid"],))
        assert r == [("false", True)], r
    finally:
        ctx.close()
    from core import notificari as n
    asist = {"rol": "angajat", "poate_pregati": True, "poate_valida": False}
    tipuri = [t["cheie"] for g in n.lista_pentru(asist, None) for t in g["tipuri"]]
    assert "de_validat" not in tipuri and "aprobata" in tipuri and "asistent_activat" not in tipuri, tipuri
    client = [t["cheie"] for g in n.lista_pentru({"rol": "client"}, None) for t in g["tipuri"]]
    assert client == ["pachet_lunar", "mesaj_cabinet"], client


def test_def_320_contul_existent_intra_direct_fara_prima_intrare(browser, request, cabinet_nou):
    """320, decizia Costin 17.10.2026 („7.2 – continuare”): „Numai conturile noi” trec prin prima intrare.
    Pașii: un cont care exista la publicarea lotului (scutit de migrare), fără telefon și fără bife salvate -> intră direct pe pagina
    principală, fără „Înainte de a începe”; Setări cont -> Notificări îi arată bifele implicite (termenele și validările)."""
    from conftest import sesiune
    sql("UPDATE public.users SET prima_intrare_scutita_la = now(), telefon = NULL, notificari_salvate_la = NULL WHERE id = %s",
        (cabinet_nou["uid"],))
    ctx = browser.new_context(viewport={"width": 1500, "height": 1100})
    ctx.add_init_script(sesiune(cabinet_nou["email"], prima_intrare=True))
    pg = ctx.new_page()
    try:
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-grila", timeout=30000)
        assert pg.locator("#prima-intrare").count() == 0
        pg.screenshot(path=os.path.join(os.environ.get("E2E_CAPTURI", "/tmp"), "320_cont_existent_direct.png"))
    finally:
        ctx.close()


def test_def_315_conectare_spv_explicatia_o_data_si_un_rand_pe_firma(patron, firma_e2e):
    """315. Conectare SPV: explicația lungă (OMFP 660/2017) se repeta întreagă la fiecare firmă.
    Pașii: certificatul conectat, două firme fără drept -> Setări cont -> Conectare SPV: explicația o dată, sus (cu răspunsul ANAF), apoi
    câte un rând pe firmă: „<firmă> · fără drept în SPV · verificat <data, ora>”."""
    from core import spv_conector as sc
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_e2e)
    cab = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (firma_e2e["tenant_id"],))[0][0]
    if sql("SELECT count(*) FROM public.spv_token WHERE accounting_firm_id = %s AND activ", (cab,))[0][0]:
        pytest.skip("cabinetul de test are deja certificatul conectat")
    tok = sql("INSERT INTO public.spv_token (accounting_firm_id, serial_certificat, access_token, refresh_token, access_expira, "
              "refresh_expira, activ) VALUES (%s, 'E2E-315', %s, %s, now() + interval '30 days', now() + interval '300 days', true) "
              "RETURNING id", (cab, sc.cripteaza("x.e30.y"), sc.cripteaza("r")))[0][0]
    try:
        for cui in ("14399840", "55229657"):
            sql("INSERT INTO public.spv_cui_acoperit (token_id, cui, verificat_la, are_drept, eroare, mesaje) VALUES (%s, %s, now(), false, "
                "%s, 0)", (tok, cui, "Nu aveti drept in SPV pentru CIF=%s" % cui))
        pg = patron.pg
        deschide_setari_panou(patron, "Conectare SPV", "#spv-cuiuri")
        tot = pg.inner_text("#spv-cuiuri")
        patron.captura("o_data")
        assert tot.count("OMFP 660/2017") == 1, tot
        randuri = pg.eval_on_selector_all("#spv-cuiuri .spv-cui", "ls => ls.map((l) => l.innerText)")
        assert len(randuri) == 2 and all("· fără drept în SPV · verificat " in r and "OMFP" not in r for r in randuri), randuri
    finally:
        sql("DELETE FROM public.spv_cui_acoperit WHERE token_id = %s", (tok,))
        sql("DELETE FROM public.spv_token WHERE id = %s", (tok,))


def test_def_notificari_titlul_o_singura_data(patron):
    """Comanda 7.2 pct.2 (decizia lui Costin la raportul porții 3): „titlul din Notificări rămâne o singură dată, în corpul ferestrei, ca
    la celelalte ecrane.” Pașii: Setări cont -> Notificări: un singur titlu „Notificări” în fereastră; la fel pe celelalte ecrane ale
    meniului."""
    pg = patron.pg
    for titlu, asteapta in (("Notificări", "#not-telefon"), ("Date profil", "input"), ("Schimbă parola", "input")):
        deschide_setari_panou(patron, titlu, asteapta)
        n = pg.evaluate("(t) => { const f = [...document.querySelectorAll('.fereastra')].pop(); return [...f.querySelectorAll('h1, h2, h3, "
                        ".cap-titlu')].filter((h) => h.textContent.trim() === t).length; }", titlu)   # textContent: .cap-titlu e cu majuscule pe ecran
        assert n == 1, (titlu, n)
    patron.captura("notificari_un_titlu")
