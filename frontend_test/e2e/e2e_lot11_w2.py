# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1”) — subagentul W2: 440 (pct.16, „toate erorile apar
deodată, fiecare cu textul ei, în casetă și lângă câmp. Fără «motivul e mai sus». Pe toată aplicația.”), 441 (pct.17, „orice câmp de dată
opțional se poate goli.”) și 445 (pct.21, „orice buton «Deschide X» dintr-un refuz întoarce în formularul de plecare, cu datele
intacte.”) pe formularele zilnice. Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_e2e`).

Date de pornire scrise direct: niciuna. Firma se pregătește pe rutele ecranelor (`pregateste_firma`), articolul din stoc prin ruta
„Intrare” a fișei de magazie (`POST stocuri/intrare`, cum îl scrie ecranul); ce se probează se face pe ecran. CUI-ul clientului
(14399840, DANTE INTERNATIONAL SA) are cifra de control verificată (algoritmul din CLAUDE.md)."""
import datetime

from conftest import sql
from e2e_bloc_a import _api, _card, _deschide_emiterea, _ok, pregateste_firma


def _caseta(pg):
    """Caseta „NU s-a salvat.”: textele rândurilor la vedere."""
    return pg.eval_on_selector_all(".refuz-salvare .refuz-salvare-lista > li", "lis => lis.filter(li => !li.hidden).map(li => li.textContent.trim())")


def _invalide(pg, ids):
    return {i: pg.get_attribute("#" + i, "aria-invalid") for i in ids}


def _langa(pg, camp):
    """Textul erorii de lângă câmp (`eroareCamp`: `.msg-eroare[data-camp]`)."""
    return pg.inner_text('.msg-eroare[data-camp="%s"]' % camp).strip()


# ── 440 — Casă: data, tipul și suma lipsă se spun DEODATĂ ─────────────────────────────────────────────────────────────────
def test_def_440_casa_data_tipul_si_suma_lipsa_toate_deodata(patron, firma_e2e):
    """440. Pașii: fereastra firmei -> Casă -> „+ Dispoziție nouă” -> golește data, nu alege tipul, nu scrie suma -> „Adaugă”: cele TREI
    câmpuri marcate deodată (aria-invalid), fiecare cu textul lui lângă el, iar caseta „NU s-a salvat.” le are pe toate trei, cu textul
    lor. Înainte: data și suma, apoi abia la a doua apăsare tipul (`return` înainte de `cereAlegerile`)."""
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "casa", "#c-toggle")
    if not pg.locator("#c-campuri").count():   # [lotul 13, 673] dispoziția nouă e o fereastră
        pg.click("#c-toggle")
    pg.fill("#c-data", "")
    pg.fill("#c-suma", "")
    pg.click("#c-adauga")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    patron.captura()
    assert _invalide(pg, ["c-data", "c-cat", "c-suma"]) == {"c-data": "true", "c-cat": "true", "c-suma": "true"}, _invalide(pg, ["c-data", "c-cat", "c-suma"])
    assert _langa(pg, "c-data") == "Completează data dispoziției."
    assert _langa(pg, "c-suma") == "Suma trebuie să fie un număr mai mare ca 0."
    caseta = _caseta(pg)
    assert len(caseta) == 3, caseta
    assert any(t.endswith("— Completează data dispoziției.") for t in caseta), caseta
    assert any(t.endswith("— Suma trebuie să fie un număr mai mare ca 0.") for t in caseta), caseta
    assert any(t.endswith("— Alege o valoare — aplicația nu alege în locul tău.") for t in caseta), caseta
    assert "motivul e" not in patron.fereastra()   # 440: „Fără «motivul e mai sus»”


# ── 440 — NIR: alegerile lipsă și articolul necompletat se spun DEODATĂ ────────────────────────────────────────────────────
def test_def_440_nir_alegerile_si_campurile_articolului_toate_deodata(patron, firma_e2e):
    """440. Pașii: Stocuri -> „+ NIR nou” -> numărul, articol nou cu denumirea, FĂRĂ cantitate și preț, transport 5 lei, fără „factura a
    sosit?” și fără cota transportului -> „Salvează”: alegerile ȘI cantitatea și prețul articolului marcate deodată, fiecare cu textul
    lui; caseta le are pe toate patru. Înainte: întâi alegerile; cantitatea și prețul abia la apăsarea următoare (de la server)."""
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "stocuri", "#sn-toggle")
    pg.click("#sn-toggle")
    pg.fill("#sn-numar", "N440")
    pg.select_option("#nir-l0-articol", "nou")
    pg.fill("#nir-l0-denumire", "Marfa NIR 440")
    pg.fill("#sn-transport", "5")
    pg.click("#sn-salveaza")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    patron.captura()
    ids = ["sn-factura-sosita", "sn-transport-cota", "nir-l0-cantitate", "nir-l0-pret_achizitie"]
    assert set(_invalide(pg, ids).values()) == {"true"}, _invalide(pg, ids)
    assert _langa(pg, "nir-l0-cantitate") == "Articolul 1: scrie cantitatea, un număr mai mare decât zero."
    assert _langa(pg, "nir-l0-pret_achizitie") == "Articolul 1: scrie prețul de achiziție, un număr mai mare decât zero."
    caseta = _caseta(pg)
    assert len(caseta) == 4, caseta
    assert any(t.startswith("Factura furnizorului a sosit?") for t in caseta), caseta
    assert any(t.endswith("— Articolul 1: scrie cantitatea, un număr mai mare decât zero.") for t in caseta), caseta
    assert not sql('SELECT 1 FROM "%s".nir WHERE numar = %%s' % firma_e2e["schema"], ("N440",))   # nimic scris


# ── 440 — Plan de conturi: clicul pe „Adaugă” cu câmpurile goale nu arăta NIMIC (TypeError) ─────────────────────────────────
def test_def_440_plan_de_conturi_simbolul_si_denumirea_lipsa_se_vad(patron, firma_e2e):
    """440 (defectul real găsit de U0, firme.js `eroareCamp("pcf-simbol", …)` fără rădăcină -> TypeError, nimic vizibil). Pașii: Plan de
    conturi -> „Adaugă” fără simbol și fără denumire: AMBELE câmpuri marcate, fiecare cu textul lui, și caseta „NU s-a salvat.” cu
    amândouă."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "planconturi", "#pcf-adauga")
    pg.click("#pcf-adauga")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    patron.captura()
    assert _invalide(pg, ["pcf-simbol", "pcf-denumire"]) == {"pcf-simbol": "true", "pcf-denumire": "true"}
    assert _langa(pg, "pcf-simbol") == "Completează simbolul contului (ex. 4111.01)."
    assert _langa(pg, "pcf-denumire") == "Completează denumirea contului."
    assert len(_caseta(pg)) == 2, _caseta(pg)


# ── 441 — Registratură: data opțională se golește din „×” ─────────────────────────────────────────────────────────────────
def test_def_441_registratura_data_se_goleste_si_ia_data_zilei(patron, firma_e2e):
    """441. Pașii: Registratură (formular zilnic) -> data 10.03.2025 -> „×” lângă ea („Golește data”) -> câmpul gol -> descrierea ->
    „Înregistrează”: înregistrarea NU poartă data golită, ci data zilei (serverul pune ziua când data lipsește — `registratura_api.adauga`),
    în anul de azi."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "registratura", "#rg-add")
    pg.fill("#rg-data", "2025-03-10")
    x = pg.locator("#rg-data + .data-goleste")
    assert x.is_visible() and x.get_attribute("aria-label") == "Golește data"
    patron.captura("cu_data")
    x.click()
    assert pg.input_value("#rg-data") == "" and not x.is_visible()
    pg.fill("#rg-desc", "Adresa ANAF 441")
    pg.click("#rg-add")
    pg.wait_for_function("() => document.body.innerText.includes('Adresa ANAF 441')", timeout=20000)
    patron.captura("golita")
    rand = sql('SELECT data, an FROM "%s".registratura WHERE descriere = %%s' % firma_e2e["schema"], ("Adresa ANAF 441",))
    azi = datetime.date.today()
    assert rand == [(azi, azi.year)], rand   # 441: data golită nu pleacă (nu 10.03.2025)


# ── 445 — „Deschide Produse” din refuzul liniei -> cota salvată -> „← Înapoi la …”: formularul, cu datele intacte ──────────
def test_def_445_deschide_produse_din_factura_salveaza_cota_si_intoarce_la_factura(patron, firma_e2e):
    """445. Pașii: articol din stoc fără cotă în nomenclator -> Emite factură -> CUI-ul clientului + articolul pe linie: sub linie „…n-are
    cota TVA în nomenclator” cu „Deschide Produse” -> apăsat: Produse se deschide PESTE factură -> cota 21% pe rândul articolului ->
    „Salvează cota”: confirmarea și butonul „← Înapoi la …” -> apăsat: factura, cu CUI-ul și articolul aleși (nimic pierdut)."""
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % tid, {"denumire": "Marfa A 445", "um": "buc",
                                                                   "data": datetime.date.today().isoformat(), "cantitate": 5,
                                                                   "pret_unitar": 10, "document": "NIR 445"}), "intrare")
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    pg.fill("#em-cui", "14399840")
    pg.wait_for_selector("#em-l0-articol", timeout=20000)
    eticheta = pg.eval_on_selector("#em-l0-articol", "(s) => [...s.options].find((o) => o.textContent.startsWith('Marfa A 445')).textContent")
    pg.select_option("#em-l0-articol", label=eticheta)
    articol = pg.input_value("#em-l0-articol")
    pg.wait_for_selector("#em-l0-cota-mesaj [data-ecran-destinatie='produse']", timeout=15000)
    pg.click("#em-l0-cota-mesaj [data-ecran-destinatie='produse']")
    sel = pg.wait_for_selector(".fereastra:last-of-type .pr-cota-rand[aria-label='Cota TVA Marfa A 445']", timeout=20000)
    cheie = sel.get_attribute("id").replace("pr-cota-", "")
    v21 = pg.eval_on_selector("#pr-cota-" + cheie, "(s) => [...s.options].find((o) => o.value && o.textContent.trim().startsWith('21')).value")
    pg.select_option("#pr-cota-" + cheie, v21)
    pg.click("#pr-cota-salveaza-" + cheie)
    inapoi = pg.wait_for_selector(".fereastra:last-of-type #pr-inapoi-la", timeout=20000)
    patron.captura("produse_salvat")
    assert inapoi.inner_text().startswith("← Înapoi la "), inapoi.inner_text()
    assert "Marfa A 445" in pg.inner_text(".fereastra:last-of-type #pr-mesaj")
    inapoi.click()
    pg.wait_for_selector(".fereastra:last-of-type #em-emite", timeout=20000)
    patron.captura("inapoi_la_factura")
    assert pg.input_value("#em-cui") == "14399840" and pg.input_value("#em-l0-articol") == articol   # 445: „cu datele intacte”
