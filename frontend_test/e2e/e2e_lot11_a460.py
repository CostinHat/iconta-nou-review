# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.3 pct.1 — deficiența 460 (verbatim, DECIZII „Comanda 11.3”): „cursul BNR nu s-a mai actualizat din 19.10;
factura din 22.10 propune cursul de pe 19.10. Repară preluarea, completează zilele lipsă și pune alertă când cursul zilei lipsește.”

Temei: CF art.290 alin.(2) („ultimul curs de schimb comunicat de Banca Națională a României [...] valabil la data la care intervine
exigibilitatea taxei”) + HG 1/2016 pct.35 alin.(1) („cursul de schimb comunicat de respectiva bancă în ziua anterioară și care este valabil
pentru operațiunile care se vor desfășura în ziua următoare”).

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua` + `pregateste_firma`, pe rutele
ecranelor): Facturi -> Emite factură -> clientul, linia -> Monedă EUR -> sub totaluri, cursul BNR cu care va emite. Și administratorul
platformei: Panou Admin -> Sănătate server -> „Curs BNR”.

DATELE DE PORNIRE (singurele scrise direct, declarate): cache-ul BNR al bazei de test (`public.curs_bnr_zilnic`, date BNR publice) adus în
starea de pe producție din 22.10.2026 — fără cursurile ultimelor două zile bancare (preluarea oprită) — și, la al treilea test, rezervarea
descărcării ocupată (`public.alerte_cooldown`, `bnr_completare`): „BNR nu răspunde” nu se poate produce din aplicație. Aplicația aduce
cursurile lipsă de la BNR (https://curs.bnr.ro), ca în producție; testul citește cache-ul după, ca să știe ce să aștepte.
Clientul DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md."""
import datetime as _dt
import os
import sys

import pytest

from conftest import BAZA, _ecran, firma_noua, sql, zile_de_acum
from e2e_bloc_a import CLIENT, PRODUS, _deschide_emiterea, pregateste_firma

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core import curs_bnr as cb  # noqa: E402  (funcțiile PURE ale regulii: ziua bancară așteptată, pragul)

AZI = _dt.date.today()


def _ro(d):
    return d.strftime("%d.%m.%Y")


def _zile_bancare_inainte(zi, n):
    """Ultimele `n` zile bancare dinaintea lui `zi` (cea mai recentă prima) — aceeași regulă ca aplicația (`ziua_bancara_asteptata`)."""
    out, d = [], zi
    for _ in range(n):
        d = cb.ziua_bancara_asteptata(d)
        out.append(d)
    return out


def _fara_ultimele_zile(n=2):
    """Pornirea: cache-ul fără cursurile ultimelor `n` zile bancare dinaintea zilei de azi (ca pe producție, 22.10.2026)."""
    zile = _zile_bancare_inainte(AZI, n)
    sql("DELETE FROM public.curs_bnr_zilnic WHERE data = ANY(%s)", (zile,))
    sql("DELETE FROM public.alerte_cooldown WHERE categorie = 'bnr_completare'")
    return zile


@pytest.fixture(scope="module")
def firma_a460_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_a460(patron, firma_a460_noua):
    pregateste_firma(patron, firma_a460_noua)
    return firma_a460_noua


@pytest.fixture()
def superadmin(browser, request):
    yield from _ecran(browser, request, "admin@prisma-cont.test")


def _formular_eur(patron, firma, data=None):
    """Emite factură -> (data) -> clientul -> linia (serviciu, 1 × 100, 21%) -> Monedă EUR; întoarce textul zonei de conversie."""
    _deschide_emiterea(patron, firma["nume"])
    pg = patron.pg
    if data:
        pg.fill("#em-data", data.isoformat())
        pg.dispatch_event("#em-data", "change")
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)
    pg.fill("#em-l0-pret_unitar", "100")
    pg.fill("#em-l0-cantitate", "1")
    pg.select_option("#em-moneda", "EUR")
    pg.wait_for_selector("#em-valuta-curs, #em-valuta-mesaj", timeout=60000)
    pg.wait_for_timeout(600)
    return " ".join(pg.inner_text("#em-valuta").split())


def test_def_460_factura_de_azi_propune_ultimul_curs_comunicat(patron, firma_a460):
    """Pașii: (pornire: cache-ul fără ultimele două zile bancare, ca pe producție) -> Emite factură, data de azi -> EUR: cursul propus e
    cel comunicat de BNR în ultima zi bancară dinaintea zilei de azi, nu unul mai vechi; golurile s-au umplut în cache, și nu apare nicio
    avertizare de curs lipsă. Pe codul vechi: cursul din ziua bancară de dinaintea golului (cazul raportat: 19.10 pe 22.10)."""
    asteptata, inainte = _fara_ultimele_zile(2)
    t = _formular_eur(patron, firma_a460)
    patron.captura("curs_propus")
    rand = sql("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data = %s", (asteptata,))
    assert rand, "golul nu s-a umplut: cursul din %s lipsește din cache după previzualizare" % asteptata
    assert sql("SELECT 1 FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data = %s", (inainte,)), "ziua %s n-a revenit" % inainte
    curs_txt = ("%.4f" % rand[0][0]).replace(".", ",")
    # CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1): „comunicat de respectiva bancă în ziua anterioară”
    assert "Curs BNR EUR %s din %s" % (curs_txt, _ro(asteptata)) in t, t
    assert not patron.pg.query_selector("#em-valuta-lipsa"), t
    # data facturii = cea implicită a ecranului (ziua de acum, nu cea de la importul testului)
    assert any("înaintea datei facturii (%s)" % _ro(d) in t for d in zile_de_acum(AZI)), t


def test_def_460_cursul_zilei_lipsa_se_vede_si_ce_se_foloseste(patron, firma_a460):
    """Pașii: Emite factură -> o dată la care cursul care i se cuvine încă nu a fost comunicat de BNR (ziua bancară de după azi) -> EUR:
    sub curs, avertizarea spune ce curs lipsește, de ce, și ce curs se folosește. MUTAȚIE (JS): avertizarea scoasă -> pică."""
    viitoare = AZI + _dt.timedelta(days=1)
    while not cb.ziua_bancara_asteptata(viitoare + _dt.timedelta(days=1)) == viitoare:
        viitoare += _dt.timedelta(days=1)
    data = viitoare + _dt.timedelta(days=1)            # factura de după ziua bancară `viitoare`: îi trebuie cursul comunicat atunci
    t = _formular_eur(patron, firma_a460, data)
    patron.captura("curs_lipsa")
    folosit = sql("SELECT max(data) FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data < %s", (data,))[0][0]
    if (data - folosit).days > cb.PRAG_VECHIME_ZILE:   # sărbători lungi: refuzul „curs prea vechi” (deja existent), nu avertizarea
        assert "mai vechi" in t, t
        return
    m = " ".join(patron.pg.inner_text("#em-valuta-lipsa").split())
    assert "Cursul BNR comunicat pe %s" % _ro(viitoare) in m and "BNR nu l-a comunicat încă" in m, m
    assert "se folosește cursul din %s" % _ro(folosit) in m, m
    assert "din %s" % _ro(folosit) in t, t


def test_def_460_administratorul_vede_cursul_zilei_lipsa(superadmin):
    """Pașii administratorului: (pornire: cache-ul fără cursul ultimei zile bancare și BNR „nu răspunde” — rezervarea descărcării ocupată)
    -> Panou Admin -> Sănătate server -> „Curs BNR”: ultimul curs din aplicație, cursul de care au nevoie facturile de azi și alerta că
    lipsește. Apoi rezervarea se eliberează și cursul revine (următoarea previzualizare / bucla de sănătate). MUTAȚIE (JS): alerta scoasă ->
    pică."""
    asteptata, = _fara_ultimele_zile(1)
    sql("INSERT INTO public.alerte_cooldown (categorie, ultima_trimitere) VALUES ('bnr_completare', now()) "   # date-de-pornire: BNR „nu răspunde” (rezervarea descărcării ocupată) — starea externă nu se produce din aplicație
        "ON CONFLICT (categorie) DO UPDATE SET ultima_trimitere = now()")
    try:
        pg = superadmin.pg
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-grila", timeout=30000)
        pg.click("button.cab-card:has([data-cheie='sanatate'])")
        pg.wait_for_selector("#san-bnr", timeout=30000)
        pg.wait_for_timeout(500)
        superadmin.captura("sanatate_curs_bnr")
        zona = " ".join(pg.inner_text("#san-bnr").split())
        msg = " ".join(pg.inner_text("#san-bnr-msg").split())
        assert _ro(asteptata) in zona, zona
        assert "Cursul BNR comunicat pe %s lipsește din aplicație" % _ro(asteptata) in msg, msg
        assert pg.eval_on_selector("#san-bnr-msg", "(e) => e.classList.contains('msg-eroare')"), msg
    finally:
        sql("DELETE FROM public.alerte_cooldown WHERE categorie = 'bnr_completare'")
