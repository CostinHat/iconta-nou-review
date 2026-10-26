# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”), subagentul PORTAL, partea Date firmă / TVA la încasare / SPV:

  * 525   „Trimiteri între ferestre | «Deschide Date firmă» de la refuzul dividendelor deschide fereastra de la început, nu la secțiunea
           Asociați; după Salvează fereastra sare la început. Trimiterea duce la locul de completat, iar după salvare rămâi unde lucrai.”
  * 526   „Date firmă — Asociați | Cu CNP invalid pe rânduri (verificarea CNP corectă), lângă buton scrie «Total cote: 100%», iar mesajul
           roșu spune «cotele însumează 0%, nu 100%». Mesajul de total nu apare când singura problemă e CNP-ul.”
  * 541   „Date firmă — TVA la încasare | Pe 22.10.2026 s-a salvat «Aplică de la 01.10.2026» fără avertisment: opțiunea nu se aplică
           retroactiv în perioada în curs, ci din prima zi a perioadei fiscale următoare (art. 282; F2 trimestrială → 01.01.2027). Aplicația
           refuză sau propune data corectă. Jurnalul perioadelor există […], dar nu arată cine și când a schimbat, iar «Sșterge» scoate
           perioada fără urmă.”
  * C71.1 „La F4 PFA caseta «Profil incomplet» cere corect doar Banca și IBAN, dar formularul marchează cu * câmpuri de SRL «cerute la
           bilanț» (Nr. registrul comerțului, Mare contribuabil, Forma de proprietate, Entitate de interes public) și oferă Regim fiscal
           micro/profit (D100/D101), care nu privesc un PFA.”
  * 661   „Fereastra firmei / SPV | La F7 (CUI inventat) scrie «SPV: conectat»; conexiunea e a cabinetului, iar certificatul nu acoperă
           acest CUI. Trebuie spus dacă certificatul acoperă CUI-ul firmei (clasa 289).”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`, scoase la final). DATELE DE PORNIRE scrise
în bază (declarate): periodicitatea trimestrială la 541 (ca F2), conexiunea SPV a cabinetului (tokenul, ca `e2e_lot6.py` la 289) și
citirea CUI-ului la 661 — nu sunt pașii probați. CNP-urile: cifra de control calculată cu algoritmul din CLAUDE.md (stricate intenționat
la 526). Mutațiile: `frontend_test/e2e/mut_lot13_portal_p3.json`.

Temei: 525 / 526 / C71.1 / 661 — N/A, reguli de interfață (CLAUDE.md §9); C71.1 — excluderea prin formă (Legea 82/1991 art.28 alin.(1),
`control_fiscal_api._NEAP_FORMA_SIMPLA`); 541 — CF art.282 alin.(3^1) lit.a): „aplică sistemul TVA la încasare începând cu prima zi a
perioadei fiscale următoare celei în care persoana impozabilă și-a exercitat opțiunea” (anaf_surse/cod_fiscal_227_2015_consolidat.txt).
"""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _card, pregateste_firma


def _cnp(baza12):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


CNP_A, CNP_B = _cnp("180010141001"), _cnp("285020241002")
_STRICAT = {CNP_A: CNP_A[:-1] + str((int(CNP_A[-1]) + 1) % 10), CNP_B: CNP_B[:-1] + str((int(CNP_B[-1]) + 1) % 10)}

_IN_VEDERE = """(sel) => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), e = c.querySelector(sel);
  const r = e.getBoundingClientRect(), k = c.getBoundingClientRect(), b = c.querySelector('.bara-fixa');
  const jos = b ? Math.min(k.bottom, b.getBoundingClientRect().top) : k.bottom; return r.top >= k.top && r.bottom <= jos; }"""
_SUS = "() => [...document.querySelectorAll('.fereastra-corp')].pop().scrollTop"


@pytest.fixture(scope="module")
def firma_srl():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_pfa():
    yield from firma_noua("pfa")


def _date_firma(e, firma):
    e.firma(firma["nume"])
    _card(e, "datefirma", "#df-salveaza")
    return e.pg


def _salveaza(pg, text="alvat", timeout=30000):
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=timeout)
    pg.evaluate("() => { const m = document.querySelector('#df-msg'); if (m) m.innerHTML = ''; }")
    pg.click("#df-salveaza")
    pg.wait_for_function("t => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes(t)", arg=text, timeout=timeout)
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=timeout)


# ── 525 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_525_din_refuzul_dividendului_la_asociati_si_ramai_acolo_dupa_salvare(patron, firma_srl):
    """525. Pașii: firmă fără asociați -> Operațiuni speciale -> „Decontări asociați” -> Dividend 10.000, hotărârea nr. 3 -> propunerea
    refuză („Date firmă → Asociați”) cu „Deschide Date firmă” -> clic: Date firmă se deschide cu „+ Asociat” în vedere (nu capul
    ferestrei) -> asociatul (CNP valid, 100%) -> „Salvează”: salvat, iar fereastra rămâne la Asociați (derularea nu cade la început).
    MUTAȚIA: poziționarea pe câmpul cerut înainte de tabelul asociaților / redesenarea fără `peLoc` -> ROȘU."""
    s = firma_srl["schema"]
    sql('DELETE FROM "%s".asociati_istoric' % s)
    sql('DELETE FROM "%s".asociati' % s)
    pregateste_firma(patron, firma_srl)
    pg = patron.pg
    try:
        patron.firma(firma_srl["nume"])
        pg.click("#fa-operatiuni")
        pg.wait_for_selector("[data-op]", timeout=20000)
        pg.locator("button[data-op='asociati']").click()
        pg.wait_for_selector("#op-trimite", timeout=10000)
        pg.select_option("#op-operatie", "dividend")
        pg.fill("#op-brut", "10000")
        pg.fill("#op-numar_hotarare", "3")
        pg.fill("#op-data_hotarare", "2026-05-15")
        pg.locator("#op-data_hotarare").blur()
        b = pg.locator("#op-propunere [data-ecran-destinatie='date_firma']")
        b.wait_for(timeout=20000)
        b.click()
        pg.wait_for_selector(".fereastra:last-of-type #as-adauga", timeout=25000)
        pg.wait_for_timeout(800)
        assert pg.evaluate(_SUS) > 0 and pg.evaluate(_IN_VEDERE, "#as-adauga"), "Date firmă deschisă de la început, nu la Asociați"
        patron.captura("deschisa_la_asociati")
        pg.fill("#as-1-nume", "Ion Popescu")
        pg.fill("#as-1-cnp", CNP_A)
        pg.fill("#as-1-cota", "100")
        inainte = pg.evaluate(_SUS)
        _salveaza(pg)
        pg.wait_for_timeout(500)
        dupa = pg.evaluate(_SUS)
        assert abs(dupa - inainte) < 60 and pg.evaluate(_IN_VEDERE, "#as-adauga"), (inainte, dupa)
        assert sql('SELECT nume, cota::float8 FROM "%s".asociati' % s) == [("Ion Popescu", 100.0)]
        patron.captura("dupa_salvare_ramane_la_asociati")
    finally:
        sql('DELETE FROM "%s".asociati' % s)


# ── 526 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_526_cnp_invalid_fara_mesajul_de_total(patron, firma_srl):
    """526. Pașii: Date firmă -> Asociați: Ion (CNP cu cifra de control greșită) 60%, „+ Asociat”, Ana (la fel) 40% -> „Total cote: 100%”
    -> „Salvează”: refuzul numește CNP-urile, lângă rândurile lor, și NU spune „cotele însumează 0%, nu 100%”; nimic scris.
    MUTAȚIA: `asociati_api.erori_ecran` scos din `uc_asociati._verifica` -> ROȘU („însumează 0%”)."""
    s = firma_srl["schema"]
    sql('DELETE FROM "%s".asociati_istoric' % s)
    sql('DELETE FROM "%s".asociati' % s)
    pg = _date_firma(patron, firma_srl)
    pg.fill("#as-1-nume", "Ion Popescu")
    pg.fill("#as-1-cnp", _STRICAT[CNP_A])
    pg.fill("#as-1-cota", "60")
    pg.click("#as-adauga")
    pg.fill("#as-2-nume", "Ana Pop")
    pg.fill("#as-2-cnp", _STRICAT[CNP_B])
    pg.fill("#as-2-cota", "40")
    assert pg.inner_text("#as-total").strip() == "Total cote: 100%"
    pg.click("#df-salveaza")
    pg.wait_for_selector(".msg-eroare[data-camp='as-1-cnp']", timeout=30000)
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=30000)
    patron.captura("cnp_invalid_fara_total")
    # refuzul stă lângă câmpurile lui (caseta de sus spune numai „Restul NU — vezi câmpurile marcate”): CNP-ul pe fiecare rând, niciun
    # mesaj de total; înainte, „cotele însumează 0%, nu 100%” lângă „Total cote: 100%”
    mesaje = pg.eval_on_selector_all(".fereastra:last-of-type .msg-eroare", "els => els.map((e) => [e.dataset.camp, e.innerText])")
    assert not [m for m in mesaje if "însumează" in m[1]], mesaje
    assert pg.locator(".msg-eroare[data-camp='as-total']").count() == 0, mesaje
    for camp in ("as-1-cnp", "as-2-cnp"):
        assert "CNP" in pg.inner_text(".fereastra:last-of-type .msg-eroare[data-camp='%s']" % camp), mesaje
    assert sql('SELECT count(*) FROM "%s".asociati' % s) == [(0,)]


# ── C71.1 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c71_1_pfa_fara_campurile_bilantului_si_fara_regim_micro_profit(patron, firma_pfa):
    """C71.1. Pașii: firmă PFA nouă -> Date firmă: fără „Mare contribuabil”, „Forma de proprietate”, „Entitate de interes public”;
    „Nr. registrul comerțului” fără „*” și fără „Cerut la bilanț.”; „Regim fiscal” fără lista micro / profit, cu motivul (D212); „Banca”
    și „IBAN” rămân cu „*”. „Salvează” trece (câmpurile lipsă de pe ecran nu se trimit, nimic nu se șterge).
    MUTAȚIA: `firma_profil_api.campuri_forma` întoarce toate `OBLIGATORII` -> ROȘU („Nr. registrul comerțului*”)."""
    pg = _date_firma(patron, firma_pfa)
    for k in ("mare_contribuabil", "forma_proprietate", "interes_public"):
        assert pg.locator("#df-" + k).count() == 0, k
    reg_com = pg.locator(".camp:has(#df-reg_com)").inner_text()
    assert "*" not in reg_com and "Cerut la bilanț" not in reg_com, reg_com
    for k in ("banca", "iban"):
        assert "*" in pg.locator(".camp:has(#df-%s)" % k).inner_text(), k
    assert pg.locator("select#vf-regim_fiscal").count() == 0
    regim = pg.inner_text("#vf-camp-regim_fiscal")
    assert "Nu se aplică" in regim and "D212" in regim, regim
    pg.locator("#vf-camp-regim_fiscal").scroll_into_view_if_needed()
    patron.captura("pfa_fara_regim_micro_profit")
    pg.locator("#df-reg_com").scroll_into_view_if_needed()
    patron.captura("pfa_fara_campurile_bilantului")


# ── 541 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _trimestru(d):
    return _dt.date(d.year, (d.month - 1) // 3 * 3 + 1, 1)


def test_def_541_optiunea_nu_se_aplica_in_perioada_in_curs_si_jurnalul_arata_cine(patron, firma_srl):
    """541. Pașii: firmă plătitoare de TVA, trimestrială (ca F2) -> Date firmă -> „Aplică sistemul TVA la încasare” Da, „Aplică de la” =
    prima zi a trimestrului în curs, fără data notificării -> „Salvează”: refuz lângă „Aplică de la”, cu data corectă (prima zi a
    trimestrului următor) și cererea datei notificării; nimic scris -> „Data notificării” = ultima zi a trimestrului anterior -> „Salvează”:
    perioada intră, iar tabelul arată „Scrisă de, când” (contabilul, azi) și data notificării -> „Șterge” -> confirmare: perioada rămâne în
    tabel, tăiată, „ștearsă”, cu cine și când.
    MUTAȚIA: `regim_tva_incasare.erori_optiune` întoarce [] -> ROȘU (perioada intră retroactiv)."""
    s = firma_srl["schema"]
    pregateste_firma(patron, firma_srl)
    sql('DELETE FROM "%s".tva_incasare_perioade' % s)
    sql('UPDATE "%s".firma_profil SET tip_decont = %%s, platitor_tva_anaf_inceput = %%s, tva_la_incasare = false WHERE id = 1' % s,
        ("trimestrial", "2020-01-01"))   # date-de-pornire: periodicitatea trimestrială a F2
    azi = _dt.date.today()
    inceput = _trimestru(azi)
    urmator = _trimestru(inceput + _dt.timedelta(days=95))
    try:
        pg = _date_firma(patron, firma_srl)
        pg.select_option("#vf-tva_incasare", "da")
        pg.fill("#vf-tva_incasare_de_la", inceput.isoformat())
        pg.click("#df-salveaza")
        pg.wait_for_selector(".msg-eroare[data-camp='vf-tva_incasare_de_la']", timeout=30000)
        refuz = pg.inner_text(".msg-eroare[data-camp='vf-tva_incasare_de_la']")
        patron.captura("refuz_perioada_in_curs")
        assert urmator.strftime("%d.%m.%Y") in refuz and "art. 282 alin. (3^1) lit. a)" in refuz, refuz
        assert sql('SELECT count(*) FROM "%s".tva_incasare_perioade' % s) == [(0,)]
        pg.fill("#vf-tva_incasare_data_optiune", (inceput - _dt.timedelta(days=1)).isoformat())
        _salveaza(pg)
        assert sql('SELECT de_la, data_optiune FROM "%s".tva_incasare_perioade' % s) == [(inceput, inceput - _dt.timedelta(days=1))]
        rand = pg.inner_text("#vf-tva-incasare-perioade tr[data-perioada-rand]")
        assert azi.strftime("%d.%m.%Y") in rand and (inceput - _dt.timedelta(days=1)).strftime("%d.%m.%Y") in rand, rand
        pg.locator("#vf-tva-incasare-perioade").scroll_into_view_if_needed()
        patron.captura("scrisa_de_cine_si_cand")
        pg.click("#vf-tva-incasare-perioade button[data-perioada]")
        pg.click("#ca-ok")
        pg.wait_for_selector("#vf-tva-incasare-perioade tr[data-perioada-scoasa]", timeout=30000)
        scoasa = pg.inner_text("#vf-tva-incasare-perioade tr[data-perioada-scoasa]")
        assert "ștearsă" in scoasa and inceput.strftime("%d.%m.%Y") in scoasa and azi.strftime("%d.%m.%Y") in scoasa, scoasa
        pg.locator("#vf-tva-incasare-perioade").scroll_into_view_if_needed()
        patron.captura("stearsa_ramane_cu_urma")
    finally:
        sql('DELETE FROM "%s".tva_incasare_perioade' % s)


# ── 661 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_661_conectat_nu_inseamna_ca_certificatul_acopera_cui_ul(patron, firma_srl):
    """661. Pașii: cabinetul conectat la SPV (token activ), CUI-ul firmei necitit încă -> fereastra firmei: „încă nu se știe dacă
    certificatul cabinetului are drept pe CUI-ul acestei firme”, nu „SPV: conectat”; citirea întoarce de la ANAF un răspuns care nu e nici
    listă, nici „fără drept” -> „nu e confirmat”, cu răspunsul ANAF; citirea reușită -> „are drept pe CUI-ul acestei firme”.
    MUTAȚIA: ramura „neverificat” din `spv_stare.textStareSpv` înapoi pe „SPV: conectat” -> ROȘU."""
    from core import spv_conector as sc
    tid = firma_srl["tenant_id"]
    cab = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (tid,))[0][0]
    cui = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma_srl["schema"])[0][0] if c.isdigit())
    assert sql("SELECT count(*) FROM public.spv_token WHERE accounting_firm_id = %s AND activ", (cab,)) == [(0,)], "premisa: neconectat"
    tok = sql("INSERT INTO public.spv_token (accounting_firm_id, serial_certificat, access_token, refresh_token, access_expira, "
              "refresh_expira, activ) VALUES (%s, 'E2E-661', %s, %s, now() + interval '30 days', now() + interval '300 days', true) "
              "RETURNING id", (cab, sc.cripteaza("x.e30.y"), sc.cripteaza("r")))[0][0]
    pg = patron.pg

    def linie():
        patron.firma(firma_srl["nume"])
        pg.wait_for_selector("#firma-spv .spv-stare-text", timeout=20000)
        return " ".join(pg.inner_text("#firma-spv").split())
    try:
        t = linie()
        patron.captura("neverificat")
        assert "SPV: conectat" not in t and "încă nu se știe dacă certificatul cabinetului are drept pe CUI-ul acestei firme (%s)" % cui in t, t
        sql("INSERT INTO public.spv_cui_acoperit (token_id, cui, verificat_la, are_drept, eroare, mesaje) VALUES (%s, %s, now(), NULL, %s, 0)",
            (tok, cui, "CIF introdus nu este valid"))
        t = linie()
        patron.captura("neconfirmat")
        assert "SPV: conectat" not in t and "nu e confirmat" in t and "„CIF introdus nu este valid”" in t, t
        sql("UPDATE public.spv_cui_acoperit SET are_drept = true, eroare = NULL WHERE token_id = %s", (tok,))
        t = linie()
        patron.captura("acoperit")
        assert "are drept pe CUI-ul acestei firme (%s)" % cui in t, t
    finally:
        sql("DELETE FROM public.spv_cui_acoperit WHERE token_id = %s", (tok,))
        sql("DELETE FROM public.spv_token WHERE id = %s", (tok,))
