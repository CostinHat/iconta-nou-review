# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.1 (Costin 20.10.2026, verbatim în DECIZII „Comanda 10.1”): Date firmă — 427 (ce s-a completat se salvează),
428 (regimul TVA la încasare pe firmă), 431 (asociații și cotele, cu istoricul cesiunilor). Pașii contabilului pe aplicația din index,
pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua`). CNP-urile au cifra de control verificată (algoritmul din CLAUDE.md)."""
import re

import pytest

from conftest import firma_noua, sql


def _cnp(baza12):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


CNP_A, CNP_B, CNP_C = _cnp("180010141001"), _cnp("285020241002"), _cnp("190030341003")


@pytest.fixture(scope="module")
def firma_df():
    for f in firma_noua():
        yield f


def _date_firma(patron, firma):
    from e2e_bloc_a import _card
    patron.firma(firma["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    return patron.pg


def _salveaza_si_asteapta(pg, text, timeout=30000):
    """Ca omul: apasă „Salvează” când e activ (salvarea de dinainte s-a încheiat), apoi așteaptă mesajul ACESTEI salvări — nu pe cel
    rămas de la salvarea de dinainte (prins la prima rulare: „S-au salvat: …” vechi conținea textul căutat) — și butonul înapoi."""
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=timeout)
    pg.evaluate("() => { const m = document.querySelector('#df-msg'); if (m) m.innerHTML = ''; }")
    pg.click("#df-salveaza")
    pg.wait_for_function("t => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes(t)", arg=text, timeout=timeout)
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=timeout)


def _refuz(pg):
    return pg.eval_on_selector_all(".refuz-salvare .refuz-salvare-lista > li",
                                   "lis => lis.map(li => [li.querySelector('button').textContent.trim(), "
                                   "li.textContent.slice(li.querySelector('button').textContent.length).trim()])")


# ── 427 — vectorul fiscal se salvează deși lipsesc Nr. reg. com., CAEN, adresa ───────────────────────────────────────
def test_def_427_vectorul_se_salveaza_cat_timp_lipsesc_reg_com_caen_adresa(patron, firma_df):
    """427. Pașii: fereastra firmei -> Date firmă (firmă nouă: Nr. registrul comerțului, CAEN, adresa goale) -> Vector fiscal: regim
    micro, înregistrată în scopuri de TVA Da, lunar, fără operațiuni intracomunitare -> Salvează: vectorul se salvează; mesajul spune
    „Salvat. Lipsesc … — blochează …”; panoul „Profil incomplet” rămâne, cu Nr. registrul comerțului, Cod CAEN și Adresa."""
    s = firma_df["schema"]
    sql('UPDATE "%s".firma_profil SET reg_com = NULL, caen = NULL, adresa = NULL, regim_fiscal = NULL, platitor_tva = NULL, '
        'tip_decont = NULL, operatiuni_ic = NULL WHERE id = 1' % s)
    pg = _date_firma(patron, firma_df)
    assert pg.input_value("#df-reg_com") == "" and pg.input_value("#df-caen") == "" and pg.input_value("#df-adresa") == ""
    pg.select_option("#vf-regim_fiscal", "micro")
    pg.select_option("#vf-platitor_tva", "da")
    pg.select_option("#vf-tip_decont", "lunar")
    pg.select_option("#vf-operatiuni_ic", "nu")
    pg.fill("#df-telefon", "0722000427")          # ce s-a completat se salvează
    _salveaza_si_asteapta(pg, "Salvat. Lipsesc")
    patron.captura()
    msg = pg.inner_text("#df-msg")
    for et in ("Nr. registrul comerțului", "Cod CAEN", "Adresa"):
        assert et in msg, msg
    assert "blochează" in msg and "D300" in msg, msg
    assert not pg.query_selector(".refuz-salvare"), "un câmp obligatoriu gol nu mai refuză salvarea"
    assert sql('SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, telefon FROM "%s".firma_profil' % s) == \
        [("micro", True, "lunar", False, "0722000427")]
    panou = pg.inner_text(".dec-avert")
    assert "Profil incomplet" in panou and "Nr. registrul comerțului" in panou and "Cod CAEN" in panou and "Adresa" in panou, panou


def test_def_427_refuzul_unei_valori_a_profilului_nu_pierde_vectorul(patron, firma_df):
    """427 (decuplarea). Pașii: Date firmă -> seria chitanțelor „CH-427!” (invalidă) + periodicitatea TVA trimestrial -> Salvează: seria
    e refuzată lângă câmpul ei („NU s-a salvat”), iar periodicitatea s-a salvat (mesajul spune ce a intrat)."""
    s = firma_df["schema"]
    pg = _date_firma(patron, firma_df)
    pg.fill("#df-serie_chitanta", "CH-427!")
    pg.select_option("#vf-tip_decont", "trimestrial")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => [...document.querySelectorAll('.refuz-salvare-lista > li')].some(li => li.textContent.includes('Seria'))",
                         timeout=20000)
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('S-au salvat')", timeout=20000)
    patron.captura()
    assert "vectorul fiscal" in pg.inner_text("#df-msg")
    assert sql('SELECT tip_decont, serie_chitanta FROM "%s".firma_profil' % s) == [("trimestrial", None)]


# ── 428 — TVA la încasare: regimul pe firmă, cu data ─────────────────────────────────────────────────────────────────
def test_def_428_firma_se_declara_cu_tva_la_incasare_de_la_o_data(patron, firma_df):
    """428 (PRIORITAR). Pașii: Date firmă -> Vector fiscal: înregistrată în scopuri de TVA Da -> „Aplică sistemul TVA la încasare”: Da,
    de la 15.03.2026 -> Salvează: refuz lângă „Aplică de la” (prima zi a unei perioade fiscale, CF art. 282 alin. (3^1)); de la
    01.03.2026 -> Salvează: perioada intră, „Azi firma aplică sistemul”, iar lista perioadelor o arată; „Verifică în registrul ANAF” e
    pe ecran."""
    s = firma_df["schema"]
    sql('DELETE FROM "%s".tva_incasare_perioade' % s)
    sql('UPDATE "%s".firma_profil SET platitor_tva = true, tip_decont = \'lunar\', regim_fiscal = \'micro\', operatiuni_ic = false, '
        'tva_la_incasare = false, platitor_tva_anaf_inceput = \'2025-01-01\' WHERE id = 1' % s)
    pg = _date_firma(patron, firma_df)
    assert pg.is_visible("#vf-tva_incasare") and pg.is_visible("#vf-tva-incasare-anaf")
    assert pg.input_value("#vf-tva_incasare") == "nu"
    pg.select_option("#vf-tva_incasare", "da")
    assert pg.is_visible("#vf-tva_incasare_de_la") and pg.is_visible("#vf-tva_incasare_pana_la")
    pg.fill("#vf-tva_incasare_de_la", "2026-03-15")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => [...document.querySelectorAll('.refuz-salvare-lista > li')].some(li => li.textContent.includes('prima zi'))",
                         timeout=30000)
    patron.captura("refuz")
    assert sql('SELECT count(*) FROM "%s".tva_incasare_perioade' % s) == [(0,)]
    pg.fill("#vf-tva_incasare_de_la", "2026-03-01")
    _salveaza_si_asteapta(pg, "Salvat")
    patron.captura()
    assert sql('SELECT de_la::text, pana_la, sursa FROM "%s".tva_incasare_perioade' % s) == [("2026-03-01", None, "manual")]
    assert sql('SELECT tva_la_incasare FROM "%s".firma_profil' % s) == [(True,)]
    assert "Azi firma aplică sistemul TVA la încasare" in pg.inner_text("#vf-camp-tva_incasare")
    assert "01.03.2026" in pg.inner_text("#vf-tva-incasare-perioade")
    assert sql('SELECT valoare_noua FROM "%s".firma_profil_jurnal WHERE camp = \'tva_incasare_perioade\' ORDER BY id DESC LIMIT 1' % s) \
        == [("de la 01.03.2026",)]


# ── 431 — asociații și cotele în Date firmă, cu cesiunea ─────────────────────────────────────────────────────────────
def test_def_431_asociatii_si_cesiunea_in_date_firma(patron, firma_df):
    """431. Pașii: Date firmă -> Asociați: Ion (CNP valid) 60%, „+ Asociat”, Ana 30% -> Salvează: refuz lângă total („însumează 90%,
    nu 100%”), nimic scris; Ana 40% -> Salvează: asociații intră; apoi cesiune: Ana înlocuită de Vlad 40%, data cesiunii 01.03.2026 ->
    Salvează: structura nouă e cea curentă, iar istoricul arată „până la 28.02.2026: Ion — 60%; Ana — 40%”."""
    s = firma_df["schema"]
    sql('DELETE FROM "%s".asociati_istoric' % s)
    sql('DELETE FROM "%s".asociati' % s)
    pg = _date_firma(patron, firma_df)
    assert pg.is_visible("#as-tabel") and pg.is_visible("#as-istoric-gol")
    pg.fill("#as-1-nume", "Ion Popescu")
    pg.fill("#as-1-cnp", CNP_A)
    pg.fill("#as-1-cota", "60")
    pg.click("#as-adauga")
    pg.fill("#as-2-nume", "Ana Pop")
    pg.fill("#as-2-cnp", CNP_B)
    pg.fill("#as-2-cota", "30")
    assert "90%" in pg.inner_text("#as-total")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => [...document.querySelectorAll('.refuz-salvare-lista > li')].some(li => li.textContent.includes('100%'))",
                         timeout=30000)
    patron.captura("refuz")
    assert sql('SELECT count(*) FROM "%s".asociati' % s) == [(0,)]
    pg.fill("#as-2-cota", "40")
    _salveaza_si_asteapta(pg, "alvat")
    assert sorted(sql('SELECT nume, cnp, cota::float8 FROM "%s".asociati' % s)) == [("Ana Pop", CNP_B, 40.0), ("Ion Popescu", CNP_A, 60.0)]
    # cesiunea: Ana -> Vlad, de la 01.03.2026
    rand_ana = 1 if pg.input_value("#as-1-nume") == "Ana Pop" else 2
    pg.fill("#as-%d-nume" % rand_ana, "Vlad Ionescu")
    pg.fill("#as-%d-cnp" % rand_ana, CNP_C)
    pg.fill("#as-data-cesiune", "2026-03-01")
    _salveaza_si_asteapta(pg, "alvat")
    patron.captura()
    assert sorted(sql('SELECT nume, cota::float8 FROM "%s".asociati' % s)) == [("Ion Popescu", 60.0), ("Vlad Ionescu", 40.0)]
    assert sorted(sql('SELECT nume, cota::float8, valabil_pana_la::text FROM "%s".asociati_istoric' % s)) == \
        [("Ana Pop", 40.0, "2026-02-28"), ("Ion Popescu", 60.0, "2026-02-28")]
    ist = pg.inner_text("#as-istoric")
    assert "28.02.2026" in ist and "Ana Pop — 40%" in ist and "Ion Popescu — 60%" in ist, ist


# ── C71 — „Profil incomplet” cere numai ce datorează forma firmei ─────────────────────────────────────────────────────
@pytest.fixture()
def firma_pfa():
    yield from firma_noua("pfa")


def test_def_c71_pfa_nu_vede_campurile_bilantului_in_profil_incomplet(patron, firma_pfa):
    """C71 (găsită de Code la C69, lotul 10). Pașii: o firmă PFA nouă (partidă simplă) -> Date firmă: panoul „Profil incomplet” nu
    numește „Mare contribuabil” / „Forma de proprietate” și nu spune că ceva „blochează Bilanț”, D101 sau D406 (PFA nu întocmește
    situații financiare anuale — Legea 82/1991 art.28 alin.(1) — și nu depune D101 / D406); numește în continuare ce datorează PFA.
    MUTAȚIA: filtrul formei scos din `firma_profil_api.lipsuri` -> ROȘU („Mare contribuabil — blochează Bilanț”)."""
    pg = _date_firma(patron, firma_pfa)
    pg.wait_for_selector(".dec-avert", timeout=30000)
    panou = " ".join(pg.inner_text(".dec-avert").split())
    patron.captura()
    assert "Profil incomplet" in panou, panou
    assert "Mare contribuabil" not in panou and "Forma de proprietate" not in panou and "Bilanț" not in panou, panou
    assert not re.search(r"\b(D101|D406)\b", panou), panou            # D101G e altă declarație
    assert "D112" in panou or "D300" in panou, panou            # anti-vacuu: ce datorează PFA rămâne cerut
