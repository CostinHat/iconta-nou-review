# -*- coding: utf-8 -*-
"""Comanda Costin 13.10.2026 (verbatim în DECIZII): varianta (a) — propunerea notei de închidere la 31.12 — și deficiența 242 (retestul
din aceeași zi). Pașii contabilului pe ecranul Bilanț, pe aplicația din index, pe baza de TEST."""
import os
import re

import pytest

from conftest import BAZA, firma_noua, sql
from e2e_bloc_d import PATRON, _api, _date_firma, _deschide, _nota_validata
from e2e_comanda_1010 import _alege_bilant, _solduri, _valideaza_bilant


def _bilant_2025(patron, f):
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    return _alege_bilant(patron, 2025)


# ── 242 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_toate_motivele():
    """Cazul F2 din producție: soldurile de preluare la 31.12.2024; în 2025 un avans plătit pe 401 (401 debitor 500), TVA colectată
    neînchisă (4427 creditor 1.050), o depunere de numerar înregistrată numai în bancă (581 creditor 1.000) și o vânzare de 800 (704),
    neînchisă în 121."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        _nota_validata(f, "2025-03-10", "401", "5121", 500, "Avans furnizor 242")
        _nota_validata(f, "2025-03-11", "4111", "4427", 1050, "TVA colectata 242")
        _nota_validata(f, "2025-03-12", "5121", "581", 1000, "Depunere numerar 242")
        _nota_validata(f, "2025-03-13", "4111", "704", 800, "Vanzare 242")
        yield f


def test_def_242_toate_motivele_de_oprire_deodata(patron, firma_toate_motivele):
    """242 (retestul Costin 13.10.2026): „Bilanț F2 2026, S1005: apare numai motivul «închide clasele 6/7 în 121». Soldurile 401 D 500,
    4427 C 1.050 și 581 C 1.000, raportate ieri pe aceeași firmă, nu se mai văd. Afișează deodată toate motivele de oprire, fiecare cu
    acțiunea lui, ca să le poată rezolva contabilul dintr-o singură trecere. Dacă soldurile au dispărut din alt motiv, spune care.”
    Cauza: soldurile n-au dispărut — verificarea 6/7 (C15) oprea generarea înaintea celei a soldurilor fără loc (238).
    Pașii: firma de mai sus -> Bilanț 2025, S1005: un singur refuz, „2 motive”: (1) clasele 6/7, cu rezultatul de închis (profit 800,00
    lei) și butonul propunerii; (2) 401 / 4427 / 581, fiecare cu acțiunea lui.
    MUTAȚIA din plasă: refuzul la primul motiv (ca înainte) -> ROȘU."""
    pg = patron.pg
    zona = _bilant_2025(patron, firma_toate_motivele)
    patron.captura()
    pg.locator(".fereastra:last-of-type .bl-inchidere-propune").scroll_into_view_if_needed()
    patron.captura("al_doilea_motiv")                                         # soldurile 401 / 4427 / 581, cu acțiunile, și butonul
    assert zona.startswith("Bilanțul pe 2025 nu se poate genera — 2 motive; rezolvă-le pe toate, apoi generează din nou."), zona
    assert re.findall(r"^(\d)\. ([^:]+):", zona, re.M) == [("1", "Clasele 6 / 7"), ("2", "Soldurile de la 31.12 de mai jos nu au loc în bilanț")]
    assert re.findall(r"Rezultatul de închis: (profit [\d.,]+ lei)", zona) == ["profit 800,00 lei"], zona
    assert re.findall(r"• (\d+) sold (debitor|creditor) ([\d.,]+) — ", zona) == [("401", "debitor", "500,00"),
                                                                                 ("4427", "creditor", "1.050,00"),
                                                                                 ("581", "creditor", "1.000,00")], zona
    assert pg.locator(".fereastra:last-of-type .bl-inchidere-propune[data-an='2025']").count() == 1


# ── varianta (a) ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_de_inchis():
    """Soldurile de preluare la 31.12.2024; în 2025 o vânzare 1.000 + TVA 210, servicii 200 + TVA 42, încasarea și plata — neînchise."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        for zi, d, c, s, ce in (("2025-03-10", "4111", "704", 1000, "Vanzare"), ("2025-03-10", "4111", "4427", 210, "TVA vanzare"),
                                ("2025-03-11", "628", "401", 200, "Servicii"), ("2025-03-11", "4426", "401", 42, "TVA servicii"),
                                ("2025-03-20", "5121", "4111", 1210, "Incasare"), ("2025-03-21", "401", "5121", 242, "Plata")):
            _nota_validata(f, zi, d, c, s, "%s inchidere" % ce)
        yield f


def test_varianta_a_propunerea_notei_de_inchidere(patron, firma_de_inchis):
    """Varianta (a), decizia Costin 13.10.2026: „Aplicația propune, la cererea contabilului, nota de închidere la 31.12: clasele 6/7 →
    121 și regularizarea TVA 4426/4427 → 4423/4424. Nota apare ca propunere și intră în evidență numai după ce contabilul o validează
    (R36).” TEMEI: OMFP 1802/2014, conturile 121, 4423, 4424, 4426, 4427.
    Pașii: firma cu vânzări 1.000 (+TVA 210) și servicii 200 (+TVA 42), neînchise -> Bilanț 2025: refuzul „închide clasele 6/7” și
    butonul „Propune nota de închidere la 31.12.2025” -> apăsat: „Am propus la 31.12.2025 …” (+ starea notelor, [279]), rezultatul închis în 121: profit 800,00 lei;
    în evidență: două note CIORNĂ (regularizarea TVA — 4427 = 4426 42, 4427 = 4423 168 — și închiderea — 704 = 121, 121 = 628) -> cât
    sunt ciorne, bilanțul se oprește tot („Notele de închidere propuse așteaptă validarea”, 244) -> validate (jurnalul) -> Bilanț 2025: coloana „An precedent” (2024 nu e în aplicație)
    completată -> „Validează”: fără erori, profitul în bilanț (F10 rd.43 = 800), TVA de plată 168 în datorii (rd.13).
    MUTAȚIA din plasă: notele propuse scrise validate (fără contabil) -> ROȘU."""
    pg = patron.pg
    f = firma_de_inchis
    zona = _bilant_2025(patron, f)
    assert "închide clasele 6/7 în 121 la 31.12.2025" in zona, zona
    pg.click(".fereastra:last-of-type .bl-inchidere-propune[data-an='2025']")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type .bl-inchidere-mesaj') || {}).innerText", timeout=60000)
    mesaj = pg.inner_text(".fereastra:last-of-type .bl-inchidere-mesaj")
    patron.captura("propunerea")
    assert mesaj.startswith("Am propus la 31.12.2025: Regularizarea TVA la 31.12.2025 (Notă de calcul nr"), mesaj
    assert "Notele sunt ciorne. Le validezi din Registrul jurnal." in mesaj, mesaj   # [279] patronul validează el
    assert re.findall(r"Rezultatul închis în 121: (profit [\d.,]+ lei)", mesaj) == ["profit 800,00 lei"], mesaj
    note = sql('SELECT i.id, i.status, l.cont_debit, l.cont_credit, l.suma FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = i.id WHERE i.sursa = 'inchidere_an' ORDER BY i.id, l.id" % (f["schema"], f["schema"]))
    assert [(st, d, c, str(s)) for _i, st, d, c, s in note] == [
        ("ciorna", "4427", "4426", "42.00"), ("ciorna", "4427", "4423", "168.00"),
        ("ciorna", "121", "628", "200.00"), ("ciorna", "704", "121", "1000.00")], note
    st, r = _api(PATRON, "POST", "/tenants/%d/s1005-valideaza?an=2025" % f["tenant_id"], {})
    assert st >= 400 and "Notele de închidere propuse așteaptă validarea" in str(r), (st, r)    # ciornele nu sunt evidență (R36; 244)
    for nid in sorted({n[0] for n in note}):
        st, r = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid), {})
        assert st == 200 and r.get("ok"), (st, r)
    _bilant_2025(patron, f)
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura("dupa_validare")
    assert "Validare fără erori" in text, text[:600]
    assert (rand[("F10", 43)][1], rand[("F10", 13)][1]) == ("800,00", "168,00"), sorted(rand.items())


# ── C17 + pct.2c (site-ul public /ghid/) ────────────────────────────────────────────────────────────────────────────────────────────
_AXE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vizual", "axe.min.js")


def test_def_c17_paginile_publice_au_contrast_si_data_actualizarii(patron):
    """C17 (găsită de Code la proba vizuală a lotului 2, comanda Costin 13.10.2026): axe pe paginile publice — butonul „Intră în cont”
    și numărul pasului din procedură, alb pe #0672FE = 4,33:1 (< 4,5); pe cuprinsul temelor, linkurile se deosebeau de textul din jur
    numai prin culoare (1,05:1). Și pct.2c: fiecare ghid arată „Actualizat la zz.ll.aaaa” sub titlu, fără autor.
    Pașii: un ghid cu procedură -> sub titlu „Actualizat la …”; axe (contrast + link în text) pe ghid, pe cuprins și pe o temă: 0.
    MUTAȚIA din plasă: `--p-brand` înapoi la #0672FE -> ROȘU."""
    pg = patron.pg
    for cale in ("/ghid/diurna-interna-neimpozabila", "/ghid", "/ghid/tema/tva"):
        pg.goto(BAZA + cale, wait_until="domcontentloaded")
        pg.add_script_tag(path=_AXE)
        rele = pg.evaluate("async () => (await axe.run(document, {runOnly: ['color-contrast', 'link-in-text-block']})).violations"
                           ".map(v => v.id + ': ' + v.nodes.map(n => n.target.join(' ')).join(', '))")
        if cale.startswith("/ghid/diurna"):
            assert re.fullmatch(r"Actualizat la \d\d\.\d\d\.\d{4}", pg.inner_text("h1 + .ghid-actualizat")), cale
            pg.locator(".ghid-procedura").first.scroll_into_view_if_needed()
            patron.captura("ghid_procedura")
        assert rele == [], (cale, rele)


def test_def_c18_procedura_cu_buline_nu_numara_zero(patron):
    """C18 (găsită de Code la captura C17, 13.10.2026): în ghidul „diurna internă neimpozabilă”, lista cu buline din blocul de procedură
    („Ce se greșește în practică”) arăta un cerc cu „0” la fiecare punct — regula veche numerota orice `li`, iar contorul crește numai
    pe lista ordonată. Pașii: ghidul -> punctele listei cu buline nu au cifră; pașii numerotați (lista ordonată) păstrează 1, 2, 3 …
    MUTAȚIA din plasă: regula veche repusă -> ROȘU."""
    pg = patron.pg
    pg.goto(BAZA + "/ghid/diurna-interna-neimpozabila", wait_until="domcontentloaded")
    pg.locator(".ghid-procedura ul").first.scroll_into_view_if_needed()
    patron.captura()
    cifre_buline = pg.evaluate("() => [...document.querySelectorAll('.ghid-procedura ul > li')]"
                               ".map(li => getComputedStyle(li, '::before').content)")
    assert cifre_buline and set(cifre_buline) <= {"none", "normal"}, cifre_buline


# ── C20 (răspunsul la §6 COMANDA_13_10) ─────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_pfa():
    yield from firma_noua(tip_firma="pfa")


def test_def_c20_pfa_d406_nu_se_datoreaza_cu_litera_corecta(patron, firma_pfa):
    """C20 (găsită de Code la rescrierea unui ghid, 13.10.2026): la o firmă în partidă simplă, motivul „D406 nu se datorează” cita
    „Anexa 5 pct.4 lit.q)” — litera q) e la pct.3 (entitățile OBLIGATE). TEMEI: OPANAF 407/2025, Anexa 5 pct.4 lit.a)–d) (persoanele
    fizice: PFA, II, IF, PFL; anaf_surse/opanaf_407_2025_saft_d406.txt).
    Pașii contabilului: firma PFA -> Declarații -> tipul declarației: D406 e dezactivat, cu motivul care trimite la pct.4 lit.a)–d).
    MUTAȚIA din plasă: litera repusă la „lit.q)” în `core/control_fiscal_api.py` -> ROȘU."""
    pg = patron.pg
    patron.firma(firma_pfa["nume"])
    _deschide(patron, "#fa-declaratii", "Pasul 1 din 3")
    opt = pg.locator(".fereastra:last-of-type #dec-tip option[value='d406']")
    # captura arată lista deschisă (o listă derulantă închisă nu-și arată opțiunile), cu motivul D406 pe rândul lui
    pg.eval_on_selector(".fereastra:last-of-type #dec-tip", "s => { s.size = s.options.length; s.style.height = 'auto'; }")
    opt.scroll_into_view_if_needed()
    patron.captura()
    assert opt.evaluate("o => o.disabled"), opt.inner_text()          # dezactivat, cu motivul ca text (nu ascuns)
    assert re.findall(r"pct\.4 lit\.(\S+)", opt.inner_text()) == ["a)–d)"], opt.inner_text()
