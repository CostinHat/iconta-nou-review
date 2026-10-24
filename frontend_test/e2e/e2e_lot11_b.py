# -*- coding: utf-8 -*-
"""Lotul 11, subagentul b (comanda Costin 11.1 pct.9, pct.10, pct.23 și deciziile 10.3): borderoul de achiziție — 450 (articolul din
nomenclator, fără dublarea notei), pct.23 (butonul lângă NIR, „Borderou de achiziție”), stornarea borderoului (decizia 10.3), NIR-ul cu
număr repetat (decizia 10.3) — și 449 (categoria cotei 0% în Produse).

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua`). Datele de PORNIRE pe care aplicația
nu le produce altfel decât pe un alt ecran (articolul din stoc, primul NIR) se pun prin rutele aplicației (`POST stocuri/intrare`,
`POST stocuri/nir`), nu prin INSERT; `sql` numai citește. CUI-ul furnizorului: 14399840 (cifra de control verificată, CLAUDE.md)."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql

AZI = _dt.date.today()
ART = "Grâu E2E 450"


@pytest.fixture(scope="module")
def firma_b_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_b(patron, firma_b_noua):
    """Firma nouă, cu Date firmă (stocul la cost), vectorul fiscal, seria și nomenclatorul (pregătirea e idempotentă)."""
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_b_noua)
    return firma_b_noua


def _api(patron, metoda, cale, corp=None):
    from e2e_bloc_a import _api as a
    return a(patron, metoda, cale, corp)


def _articol(patron, firma, den=ART):
    """Articolul din stoc, pe drumul aplicației (Stocuri › Mișcări › intrare „articol nou”) — o singură dată pe firmă."""
    s = firma["schema"]
    r = sql('SELECT id FROM "%s".articole WHERE denumire = %%s' % s, (den,))
    if r:
        return r[0][0]
    from e2e_bloc_a import _ok
    return _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % firma["tenant_id"],
                    {"denumire": den, "um": "kg", "data": AZI.isoformat(), "cantitate": 10, "pret_unitar": 1, "cont_stoc": "371"}),
               "articolul de pornire")["articol_id"]


def _ecran_borderou(patron, firma):
    """Stocuri -> „Borderou de achiziție” (lângă „+ NIR nou”)."""
    from e2e_bloc_a import _card
    patron.firma(firma["nume"])
    _card(patron, "stocuri", "#s-borderou")
    pg = patron.pg
    assert pg.inner_text("#s-borderou").strip() == "Borderou de achiziție"
    pg.click("#s-borderou")
    pg.wait_for_selector("#op-furnizor_nume", timeout=20000)
    pg.fill("#op-data", AZI.isoformat())
    return pg


def _completeaza(pg, nume="Maria Ionescu", articol_id=None, nou=None, valoare="200", cantitate="200"):
    pg.fill("#op-furnizor_nume", nume)
    pg.fill("#op-furnizor_adresa", "Str. Mare 2, Cluj-Napoca")
    pg.fill("#op-furnizor_act", "CJ 123456")
    pg.fill("#op-valoare", valoare)
    pg.fill("#op-cont_cheltuiala", "371")
    if nou is not None:
        pg.select_option("#op-articol", "__nou__")
        pg.fill("#op-articol_den", nou)
        pg.fill("#op-um", "kg")
    else:
        pg.select_option("#op-articol", str(articol_id))
    pg.fill("#op-cantitate", cantitate)
    pg.select_option("#op-categorie", "1001")


def _articole_cu_cheia(firma, cheie="grau e2e 450"):
    from core.produse_api import cheie_denumire
    return [r for r in sql('SELECT id, denumire FROM "%s".articole ORDER BY id' % firma["schema"]) if cheie_denumire(r[1]) == cheie]


# ── 450 — articolul se alege din nomenclator; după generare formularul nu mai dublează nota ───────────────────────────────────────
def test_def_450_borderoul_alege_articolul_din_nomenclator_si_se_inchide_dupa_generare(patron, firma_b):
    """450 (comanda 11.1 pct.9). Pașii: Stocuri -> „Borderou de achiziție”: articolul „Grâu E2E 450” ALES din listă -> „Generează nota”
    -> confirmarea cu nota (371 = 401), câmpurile și butonul inactive („Borderou nou” pentru altul); în nomenclator rămâne UN singur
    articol „grâu” (înainte: al doilea „grau”, creat tacit). Retrimiterea aceluiași borderou (pe API, ca un al doilea clic) se refuză.
    MUTAȚIA: core/uc_tenants.py, intrarea în stoc cu `"articol_id": None` -> al doilea articol -> ROȘU."""
    aid = _articol(patron, firma_b)
    pg = _ecran_borderou(patron, firma_b)
    _completeaza(pg, articol_id=aid)
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=20000)
    patron.captura()
    t = pg.inner_text("#op-mesaj")
    assert "371 = 401 · 200,00 lei" in t and "Borderou BA-" in t, t
    assert pg.is_disabled("#op-trimite") and pg.is_disabled("#op-furnizor_nume"), "după generare formularul se închide"
    assert pg.query_selector("#ba-nou") is not None
    assert len(_articole_cu_cheia(firma_b)) == 1, _articole_cu_cheia(firma_b)   # comanda 11.1 pct.9: „Articolul se alege din nomenclator”
    r = _api(patron, "POST", "/tenants/%d/achizitie-neinregistrat" % firma_b["tenant_id"],
             {"data": AZI.isoformat(), "furnizor_nume": "Maria Ionescu", "furnizor_adresa": "Str. Mare 2, Cluj-Napoca",
              "furnizor_act": "CJ 123456", "valoare": 200, "cont_cheltuiala": "371", "articol_id": aid, "cantitate": 200,
              "categorie": "1001"})
    assert r["status"] == 422 and r["json"]["detail"]["cod"] == "BORDEROU_DUBLAT", r


def test_def_450_articolul_nou_cu_denumirea_unuia_existent_se_refuza(patron, firma_b):
    """450. Pașii: „Articol nou…” cu denumirea „grau e2e 450” (fără diacritice), când „Grâu E2E 450” e deja în nomenclator -> refuz lângă
    denumire, cu numele articolului existent; nimic scris.
    MUTAȚIA: core/produse_api.py, `cheie_denumire` fără scoaterea diacriticelor -> denumirea trece, al doilea articol -> ROȘU."""
    _articol(patron, firma_b)
    n = len(sql('SELECT 1 FROM "%s".facturi' % firma_b["schema"]))
    pg = _ecran_borderou(patron, firma_b)
    _completeaza(pg, nume="Vasile Pop", nou="grau e2e 450")
    pg.click("#op-trimite")
    pg.wait_for_selector('.msg-eroare[data-camp="op-articol_den"]', timeout=20000)
    patron.captura()
    assert pg.inner_text('.msg-eroare[data-camp="op-articol_den"]').strip() == (
        "Articolul «Grâu E2E 450» e deja în nomenclator: alege-l din listă — borderoul nu creează un al doilea articol cu același nume.")
    assert len(_articole_cu_cheia(firma_b)) == 1 and len(sql('SELECT 1 FROM "%s".facturi' % firma_b["schema"])) == n


# ── decizia 10.3 — borderoul se corectează prin stornare ────────────────────────────────────────────────────────────────────────
def test_decizia_103_borderoul_se_storneaza_din_lista_lunii(patron, firma_b):
    """Decizia 10.3 („Borderoul se corectează prin stornare, ca factura.”). Pașii: un borderou generat -> „Borderourile lunii” ->
    „Stornează” -> confirmă -> rândul spune „Stornat prin BA-n”, stornarea apare cu „Stornare pentru …”, fără „Stornează”; nota
    inversă (371 = 401 cu minus) și stornarea intrării în stoc. MUTAȚIA: core/uc_tenants.py, verificarea „deja stornat” scoasă și butonul
    oferit și pe stornare -> a doua stornare trece -> ROȘU."""
    aid = _articol(patron, firma_b)
    pg = _ecran_borderou(patron, firma_b)
    _completeaza(pg, nume="Ion Stornescu", articol_id=aid, valoare="50", cantitate="5")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=20000)
    fid = sql('SELECT id FROM "%s".facturi WHERE tert_nume = %%s AND storno_din_id IS NULL ORDER BY id DESC LIMIT 1' % firma_b["schema"],
              ("Ion Stornescu",))[0][0]
    pg.wait_for_selector("#ba-storneaza-%d" % fid, timeout=20000)
    pg.click("#ba-storneaza-%d" % fid)
    pg.click("#ca-ok")
    pg.wait_for_selector("#ba-lista-mesaj .caseta-ok", timeout=20000)
    patron.captura()
    rand = pg.inner_text('[data-borderou="%d"]' % fid)
    assert "Stornat prin Borderou de achiziție BA-" in rand and pg.query_selector("#ba-storneaza-%d" % fid) is None, rand
    s = sql('SELECT id FROM "%s".facturi WHERE storno_din_id = %%s' % firma_b["schema"], (fid,))
    assert len(s) == 1 and pg.query_selector("#ba-storneaza-%d" % s[0][0]) is None
    assert sql('SELECT l.cont_debit, l.cont_credit, l.suma FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
               'WHERE i.factura_id = %%s' % (firma_b["schema"], firma_b["schema"]), (s[0][0],)) == [("371", "401", -50)]   # OMFP 1802/2014 pct.69
    r = _api(patron, "POST", "/tenants/%d/borderouri/%d/storneaza" % (firma_b["tenant_id"], fid), {})
    assert r["status"] == 422 and "e deja stornat" in str(r["json"]), r   # CF art.330 alin.(1) lit.b)


# ── decizia 10.3 — NIR cu număr repetat ─────────────────────────────────────────────────────────────────────────────────────────
def test_decizia_103_nir_cu_numar_repetat_se_refuza_langa_numar(patron, firma_b):
    """Decizia 10.3 („NIR cu număr repetat: refuzat, cu mesaj numit.”). Pașii: NIR nr. „E2E-450” salvat; „+ NIR nou” cu același număr,
    același an -> lângă „număr NIR”: „Numărul E2E-450 e deja al NIR-ului din …”; nimic scris.
    MUTAȚIA: core/uc_tenants.py, `_nir_cu_numarul` întoarce None -> al doilea NIR cu același număr -> ROȘU."""
    from e2e_bloc_a import _card, _ok
    aid = _articol(patron, firma_b)
    s, tid = firma_b["schema"], firma_b["tenant_id"]
    if not sql('SELECT 1 FROM "%s".nir WHERE numar = %%s' % s, ("E2E-450",)):
        _ok(_api(patron, "POST", "/tenants/%d/stocuri/nir" % tid, {"numar": "E2E-450", "data": AZI.isoformat(), "furnizor": "DANTE INTERNATIONAL SA",
                                                                  "cui": "14399840", "factura_sosita": False,
                                                                  "linii": [{"articol_id": aid, "denumire": ART, "cantitate": 2,
                                                                             "pret_achizitie": 3, "cota_tva": 11}]}), "primul NIR")
    n = len(sql('SELECT 1 FROM "%s".nir' % s))
    patron.firma(firma_b["nume"])
    _card(patron, "stocuri", "#sn-toggle")
    pg = patron.pg
    pg.click("#sn-toggle")
    pg.fill("#sn-numar", "e2e-450")
    pg.fill("#sn-data", AZI.isoformat())
    pg.fill("#sn-furn", "DANTE INTERNATIONAL SA")
    pg.fill("#sn-cui", "14399840")
    pg.select_option("#sn-factura-sosita", "false")
    pg.select_option("#nir-l0-articol", str(aid))   # rândul cu care se deschide formularul; fără „+ articol” (un rând gol ar fi refuzat și el)
    pg.fill("#nir-l0-cantitate", "2")
    pg.fill("#nir-l0-pret_achizitie", "3")
    pg.select_option("#nir-l0-cota_tva", "11")
    pg.click("#sn-salveaza")
    pg.wait_for_selector('.msg-eroare[data-camp="sn-numar"]', timeout=20000)
    patron.captura()
    assert pg.inner_text('.msg-eroare[data-camp="sn-numar"]').strip().startswith("Numărul E2E-450 e deja al NIR-ului din ")   # numărul NIR-ului care îl are
    assert len(sql('SELECT 1 FROM "%s".nir' % s)) == n


# ── pct.23 — butonul borderoului lângă NIR, nu în „TVA regimuri speciale” ───────────────────────────────────────────────────────
def test_def_450_pct23_borderoul_sta_langa_nir_nu_in_operatiuni(patron, firma_b):
    """Comanda 11.1 pct.23: „butonul borderoului stă în «TVA regimuri speciale» cu nume tehnic”. Pașii: Stocuri -> „Borderou de achiziție”
    lângă „+ NIR nou”; Operațiuni speciale -> nu mai are „Achiziție de la neînregistrat (persoană fizică) — D394 op. N”.
    MUTAȚIA: static/js/ecrane/firme.js, butonul `s-borderou` scos -> ROȘU."""
    from e2e_bloc_a import _card
    patron.firma(firma_b["nume"])
    _card(patron, "stocuri", "#s-borderou")
    pg = patron.pg
    rand = pg.eval_on_selector("#sn-toggle", "b => b.parentElement.innerText")
    assert "+ NIR nou" in rand and "Borderou de achiziție" in rand, rand
    patron.captura()
    patron.firma(firma_b["nume"])
    _card(patron, "operatiuni", "[data-op]")
    assert pg.query_selector("[data-op='neinregistrat']") is None


# ── 449 — categoria cotei 0% în Produse ─────────────────────────────────────────────────────────────────────────────────────────
def test_def_449_produsul_cu_taxare_inversa_se_salveaza_cu_categoria_si_bunul(patron, firma_b):
    """449 (comanda 11.1 pct.10). Pașii: Produse -> „+ Adaugă produs”: „Porumb E2E 449”, cota „0% — Taxare inversă (art.331)” -> apare
    lista bunurilor -> „Cereale: Porumb (NC 1005)” -> Salvează -> rândul arată „0% · Taxare inversă (art.331)”; în nomenclator
    categoria și codul NC. Fără bun ales -> refuz lângă listă. MUTAȚIA: static/js/ecrane/produse_ecran.js, opțiunile 0% cu categorie scoase
    din listă -> ROȘU."""
    from e2e_bloc_a import _card
    patron.firma(firma_b["nume"])
    _card(patron, "produse", "#pr-add")
    pg = patron.pg
    pg.click("#pr-add")
    pg.fill("#pr-den", "Porumb E2E 449")
    pg.select_option("#pr-cota", "0:taxare_inversa")
    assert pg.is_visible("#pr-c331")
    pg.click("#pr-salveaza")
    pg.wait_for_selector('.msg-eroare[data-camp="pr-c331"]', timeout=20000)
    pg.select_option("#pr-c331", "1005")
    pg.click("#pr-salveaza")
    pg.wait_for_selector("text=Porumb E2E 449", timeout=20000)
    patron.captura()
    rand = pg.inner_text('.pr-rand:has-text("Porumb E2E 449")')
    assert "0% · Taxare inversă (art.331)" in rand, rand
    assert sql('SELECT cota_tva, categorie_tva, categorie_331 FROM "%s".produse WHERE denumire = %%s' % firma_b["schema"],
               ("Porumb E2E 449",)) == [(0, "taxare_inversa", "1005")]   # CF art.331 alin.(2) lit.c), HG 1/2016 pct.109 alin.(7)
