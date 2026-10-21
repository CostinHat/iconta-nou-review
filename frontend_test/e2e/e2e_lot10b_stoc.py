# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.2 (Costin 20.10.2026, retestul lotului 9): stocul și borderoul de achiziție — 434 (numerotarea borderourilor),
435 (orice articol din stoc în nomenclator), 401 (textul de sub nota borderoului), 402 (refuzul complet la contul de stoc), 404 (rândul cu
lipsă la inventar), 419 (rândul de retur din fișa de magazie). Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ
de test (`firma_noua`); CUI-ul partenerului are cifra de control verificată (algoritmul din CLAUDE.md: 14399840)."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql

AZI = _dt.date.today()


@pytest.fixture(scope="module")
def firma_cv_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_cv(patron, firma_cv_noua):
    """Firma nouă, cu Date firmă (stocul la cost), vectorul fiscal, seria și nomenclatorul (pregătirea e idempotentă)."""
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_cv_noua)
    return firma_cv_noua


_VANZATOR = {"furnizor_adresa": "Str. Florilor 1, Ploiești", "furnizor_act": "PH 123456", "categorie": "alte_bunuri"}


def _borderou_api(patron, firma, **corp):
    from e2e_bloc_a import _api, _ok
    c = {"data": AZI.isoformat(), "valoare": 200, "cont_cheltuiala": "371", "um": "kg", **_VANZATOR, **corp}
    return _ok(_api(patron, "POST", "/tenants/%d/achizitie-neinregistrat" % firma["tenant_id"], c), "borderou")


def _formular_borderou(patron, firma):
    from e2e_bloc_a import _card
    patron.firma(firma["nume"])
    _card(patron, "operatiuni", "[data-op='neinregistrat']")
    pg = patron.pg
    pg.click("[data-op='neinregistrat']")
    pg.wait_for_selector("#op-furnizor_nume", timeout=20000)
    pg.fill("#op-data", AZI.isoformat())
    return pg


def _scrie_borderou(pg, nume, numar="", articol="Grâu E2E 434", adresa=True):
    pg.fill("#op-furnizor_nume", nume)
    if adresa:
        pg.fill("#op-furnizor_adresa", _VANZATOR["furnizor_adresa"])
        pg.fill("#op-furnizor_act", _VANZATOR["furnizor_act"])
    pg.fill("#op-valoare", "150")
    pg.fill("#op-cont_cheltuiala", "371")
    pg.fill("#op-articol", articol)
    pg.fill("#op-cantitate", "100")
    pg.fill("#op-um", "kg")
    pg.fill("#op-numar", numar)
    pg.select_option("#op-categorie", "alte_bunuri")
    pg.click("#op-trimite")


def _numere_borderouri(firma):
    return [r[0] for r in sql('SELECT numar FROM "%s".facturi WHERE tip = \'borderou\' ORDER BY id' % firma["schema"])]


# ── 434 — numerotarea borderourilor e unică și continuă ─────────────────────────────────────────────────────────────────
def test_def_434_borderoul_nou_primeste_numarul_urmator_nu_unul_deja_dat(patron, firma_cv):
    """434 (comanda 10.2 pct.4). Pașii: Operațiuni speciale -> „Achiziție de la neînregistrat”: borderoul lui Ion Popescu cu numărul
    scris „BA-<n+1>” (n = cel mai mare de până acum); apoi borderoul Mariei Ionescu cu „Nr. borderou” gol -> primește BA-<n+2>, nu un
    număr deja dat; apoi un al treilea cu numărul scris „BA-<n+1>” -> refuzat lângă „Nr. borderou”: numărul e deja al borderoului lui Ion
    Popescu, iar aplicația propune numărul următor. Niciun număr nu apare de două ori.
    MUTAȚIA: core/documente_interne.py, `peste = cel_mai_mare(cur, schema, tip, d.year)` -> `peste = 0` -> ROȘU."""
    pg = _formular_borderou(patron, firma_cv)
    n = max([int(x[3:]) for x in _numere_borderouri(firma_cv) if x.upper().startswith("BA-") and x[3:].isdigit()] or [0])
    _scrie_borderou(pg, "Ion Popescu", numar="BA-%d" % (n + 1))
    pg.wait_for_function("() => (document.querySelector('#op-mesaj') || {}).innerText && "
                         "document.querySelector('#op-mesaj').innerText.includes('Notă generată')", timeout=30000)
    pg = _formular_borderou(patron, firma_cv)
    _scrie_borderou(pg, "Maria Ionescu")
    pg.wait_for_function("() => (document.querySelector('#op-mesaj') || {}).innerText && "
                         "document.querySelector('#op-mesaj').innerText.includes('Notă generată')", timeout=30000)
    patron.captura("al_doilea")
    nr = _numere_borderouri(firma_cv)
    assert nr[-2:] == ["BA-%d" % (n + 1), "BA-%d" % (n + 2)], nr
    pg = _formular_borderou(patron, firma_cv)
    _scrie_borderou(pg, "Vasile Pop", numar="ba-%d" % (n + 1))
    pg.wait_for_selector('.msg-eroare[data-camp="op-numar"]', timeout=20000)
    t = pg.inner_text('.msg-eroare[data-camp="op-numar"]')
    patron.captura()
    assert ("Numărul BA-%d e deja al borderoului din %s (Ion Popescu)" % (n + 1, AZI.strftime("%d.%m.%Y"))) in t, t   # AZI-dat-de-test (data borderoului)
    assert "(BA-%d)" % (n + 3) in t, t
    nr = _numere_borderouri(firma_cv)
    assert len(nr) == len({x.upper() for x in nr}), nr   # „unică”: niciun număr de două ori


# ── 435 — orice articol din stoc apare în nomenclator, cu cota completabilă ────────────────────────────────────────────
def test_def_435_articolul_din_stoc_apare_in_produse_si_cota_se_completeaza(patron, firma_cv):
    """435 (comanda 10.2 pct.5). Pașii: un articol intrat în stoc fără cotă (intrarea din „Mișcări, fișe de magazie”) și grâu din
    borderou -> fereastra firmei -> Produse: amândouă apar, „cotă lipsă”, cu „— alege cota —” și „Salvează cota”; „Salvează cota” fără
    alegere -> refuzul lângă listă; 21% -> confirmarea „Cota 21% salvată: … e acum în nomenclator” și rândul arată „TVA 21%”.
    MUTAȚIA: core/produse_api.py, `if not doar_confirmate:` -> `if False:` -> ROȘU."""
    from e2e_bloc_a import _api, _ok
    tid = firma_cv["tenant_id"]
    den = "Marfa B E2E 435"
    aid = _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % tid, {"denumire": den, "um": "buc", "data": AZI.isoformat(),
                                                                       "cantitate": 4, "pret_unitar": 25, "document": "NIR nr 3 E2E"}),
              "intrare")["articol_id"]
    _borderou_api(patron, firma_cv, furnizor_nume="Ion Popescu", articol="Grâu E2E 435", cantitate=100)
    gid = sql('SELECT id FROM "%s".articole WHERE denumire = %%s' % firma_cv["schema"], ("Grâu E2E 435",))[0][0]
    patron.firma(firma_cv["nume"])
    pg = patron.pg
    pg.click("#fa-produse")
    pg.wait_for_selector("#pr-rand-s%d" % aid, timeout=25000)
    for a, nume in ((aid, den), (gid, "Grâu E2E 435")):
        t = " ".join(pg.inner_text("#pr-rand-s%d" % a).split())
        assert nume in t and "cotă lipsă" in t and "Salvează cota" in t, t
    pg.click("#pr-cota-salveaza-s%d" % aid)
    pg.wait_for_selector('.msg-eroare[data-camp="pr-cota-s%d"]' % aid, timeout=10000)
    pg.select_option("#pr-cota-s%d" % aid, "21")
    pg.click("#pr-cota-salveaza-s%d" % aid)
    pg.wait_for_function("() => (document.querySelector('#pr-mesaj') || {}).innerText && "
                         "document.querySelector('#pr-mesaj').innerText.includes('e acum în nomenclator')", timeout=20000)
    patron.captura()
    assert ("Cota 21%% salvată: %s e acum în nomenclator" % den) in pg.inner_text("#pr-mesaj")
    rand = pg.locator(".pr-rand", has_text=den).first
    assert "TVA 21%" in rand.inner_text() and not pg.query_selector("#pr-rand-s%d" % aid)
    assert sql('SELECT cota_tva FROM "%s".produse WHERE denumire = %%s' % firma_cv["schema"], (den,))[0][0] == 21


# ── 401 — textul de sub nota borderoului ────────────────────────────────────────────────────────────────────────────────
def test_def_401_sub_nota_borderoului_scrie_borderoul_nu_factura(patron, firma_cv):
    """401 (comanda 10.2 pct.7a). Pașii: un borderou (ciornă) -> Registru jurnal: sub nota lui, textul numește „borderoul de achiziție
    BA-n din …” și trimite la Operațiuni („Achiziție de la neînregistrat”), nu „factura de achiziție” și nu „în Facturi”.
    MUTAȚIA: core/note_derivate.py, `return d("borderou" if borderou else "factura")` -> `return d("factura")` -> ROȘU."""
    from e2e_bloc_a import _card
    r = _borderou_api(patron, firma_cv, furnizor_nume="Ion Popescu", articol="Grâu E2E 401", cantitate=50)
    patron.firma(firma_cv["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg = patron.pg
    sub = pg.locator("[data-nota-id='%s'] .jn-derivata" % r["inregistrare_id"]).first
    sub.wait_for(timeout=30000)
    t = " ".join(sub.inner_text().split())
    patron.captura()
    assert ("borderoul de achiziție %s din %s" % (r["numar"], AZI.strftime("%d.%m.%Y"))) in t, t   # AZI-dat-de-test (data borderoului)
    assert "Achiziție de la neînregistrat" in t and "factura de achiziție" not in t and "în Facturi:" not in t, t


# ── 402 — refuzul la contul de stoc spune complet ce lipsește ───────────────────────────────────────────────────────────
def test_def_402_refuzul_la_contul_de_stoc_spune_ce_lipseste_si_de_ce(patron, firma_cv):
    """402 (comanda 10.2 pct.7b). Pașii: „Achiziție de la neînregistrat” pe 371, cu vânzătorul identificat, fără articol și cantitate ->
    lângă „Articolul” și „Cantitatea” câte o frază întreagă (ce se cere și de ce), nu „articolul” / „cantitatea”; motivul de jos spune
    „completează articolul și cantitatea”.
    MUTAȚIA: core/uc_tenants.py, mesajul de lângă „op-articol” -> „articolul” -> ROȘU."""
    pg = _formular_borderou(patron, firma_cv)
    _scrie_borderou(pg, "Maria Ionescu", articol="")
    pg.fill("#op-cantitate", "")
    pg.click("#op-trimite")
    pg.wait_for_selector('.msg-eroare[data-camp="op-articol"]', timeout=20000)
    patron.captura()
    art = pg.inner_text('.msg-eroare[data-camp="op-articol"]').strip()
    cant = pg.inner_text('.msg-eroare[data-camp="op-cantitate"]').strip()
    assert art == "Scrie articolul care intră în stoc pe contul 371: marfa intră în gestiune odată cu borderoul.", art
    assert cant.startswith("Scrie cantitatea care intră în stoc pe contul 371, mai mare decât zero"), cant
    assert "completează articolul și cantitatea" in pg.inner_text("#op-mesaj")


# ── 404 — rândul cu lipsă la inventar nu mai e înghesuit ────────────────────────────────────────────────────────────────
def test_def_404_randul_cu_lipsa_la_inventar_nu_rupe_denumirea(patron, firma_cv):
    """404 (comanda 10.2 pct.7c). Pașii: un articol cu denumire lungă în stoc -> Stocuri -> „Mișcări, fișe…” -> Inventar: faptic 0 ->
    apare încadrarea lipsei SUB rând, iar denumirea rămâne pe cel mult două rânduri (era ruptă pe 5).
    MUTAȚIA: static/js/ecrane/firme.js, `id="cvi-a${a.id}-rand" style="flex-wrap:wrap"` -> `id="cvi-a${a.id}-rand"` -> ROȘU."""
    from e2e_bloc_a import _api, _card, _ok
    tid = firma_cv["tenant_id"]
    den = "Marfa cu denumire lungă pentru inventarul E2E 404, ambalaj de carton"
    aid = _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % tid, {"denumire": den, "um": "buc", "data": AZI.isoformat(),
                                                                       "cantitate": 5, "pret_unitar": 10, "document": "NIR E2E 404"}),
              "intrare")["articol_id"]
    patron.firma(firma_cv["nume"])
    _card(patron, "stocuri", "#cv-toggle")
    pg = patron.pg
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-inv", timeout=20000)
    pg.click("#cv-inv")
    pg.fill("#cvi-a%d-faptic" % aid, "3")
    pg.wait_for_selector("#cvi-a%d-lipsa" % aid, state="visible", timeout=5000)
    patron.captura()
    g = pg.evaluate("""(id) => {
        const r = document.querySelector('#cvi-a' + id + '-rand'), n = r.querySelector('.pf-frand-nume'),
              z = document.querySelector('#cvi-a' + id + '-lipsa-zona');
        const lh = parseFloat(getComputedStyle(n).lineHeight) || parseFloat(getComputedStyle(n).fontSize) * 1.3;
        return {randuri: Math.round(n.getBoundingClientRect().height / lh), sub: z.getBoundingClientRect().top >= n.getBoundingClientRect().bottom - 1};
    }""", aid)
    assert g["sub"] and g["randuri"] <= 2, g


# ── 419 — rândul de retur din fișa de magazie ───────────────────────────────────────────────────────────────────────────
def test_def_419_fisa_arata_returul_din_stornare_cu_un_singur_semn(patron, firma_cv):
    """419 (comanda 10.2 pct.7f, partea fișei). Pașii: articol în stoc -> factură cu 1 buc, „Pleacă marfa acum: Da” -> stornare cu retur
    -> Stocuri -> fișa articolului: ultimul rând e „retur în stoc (ieșirea stornată în roșu) +1 · <valoarea> lei”, fără „−-1” și fără
    valoare cu minus.
    MUTAȚIA: core/stocuri_cv_api.py, `"storno": bool(l.get("anuleaza_id")),` -> `"storno": False,` -> ROȘU."""
    from e2e_bloc_a import ARTICOL, _api, _card, _ok, articol_in_stoc, emite_api
    tid = firma_cv["tenant_id"]
    aid = articol_in_stoc(patron, firma_cv, cantitate=22, pret=10)
    f = emite_api(patron, firma_cv, linii=[{"descriere": ARTICOL, "cantitate": 1, "um": "buc", "pret_unitar": 20.0, "cota_tva": 21,
                                             "cota_propusa": 21, "articol_id": aid}], pleaca_marfa=True)
    _ok(_api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (tid, f["factura_id"]), {"retur": True}), "storno cu retur")
    patron.firma(firma_cv["nume"])
    _card(patron, "stocuri", "#cv-toggle")
    pg = patron.pg
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-art", timeout=20000)
    pg.select_option("#cv-art", str(aid))
    pg.click("#cv-fisa")
    pg.wait_for_selector("#cv-fisa-zona .pf-frand", timeout=20000)
    randuri = [" ".join(x.split()) for x in pg.eval_on_selector_all("#cv-fisa-zona .pf-frand .pf-frand-nume", "e => e.map(x => x.innerText)")]
    patron.captura()
    retur = randuri[-1]
    assert "retur în stoc (ieșirea stornată în roșu) +1 · " in retur, randuri
    assert "−-" not in " ".join(randuri) and "· -" not in " ".join(randuri), randuri
