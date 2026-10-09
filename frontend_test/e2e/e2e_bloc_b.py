# -*- coding: utf-8 -*-
"""Blocul B (DEFICIENTE.md 34–63, 06.10 — salarii F5, coada de validare, retestul facturii) probat în browser, pe firma sintetică a
rulării (`firma_e2e`).

Asistentul „numai Poate pregăti” (ca Ana) e un cont PROPRIU al rulării (`ana`, `ana2`), creat pe drumul aplicației
(`repo_utilizatori.creeaza_cont_asistent` + `asistenti_api.atribuie_firma`) și scos la final: contul comun
`asistent@prisma-cont.test` are bifele pe care le schimbă alte rulări, deci nu se atinge.

Fiecare test își pune singur starea de care are nevoie (helperii `_asigura_*` sunt idempotenți), ca să poată rula și singur (mutația).
Excepția declarată: 45 și 36 cer metoda de stoc NEDECLARATĂ, care există numai pe o firmă nouă (odată declarată nu se mai șterge) —
de aceea stau înaintea testelor care o declară, iar fiecare sare explicit (skip cu motiv) dacă o găsește declarată."""
import datetime as _dt
import re
import time as _t

import pytest

from conftest import _ecran, cui_cu_control, sql

AZI = _dt.date.today()
LUNA = (AZI.year, AZI.month)


# ── date pe drumul aplicației ──────────────────────────────────────────────────────────────────────────────────────────────
def _patron():
    return sql("SELECT id, nume, COALESCE(prenume, '') FROM public.users WHERE email = 'patron@prisma-cont.test'")[0]


def _profil(firma, date):
    """Date firmă salvate pe drumul ecranului (`firma_profil_api.salveaza_date`, cu autorul — jurnalul îl cere)."""
    from core import db, firma_profil_api
    with db.get_conn(firma["schema"]) as c:
        r = firma_profil_api.salveaza_date(c, date, tenant_id=firma["tenant_id"], user_id=_patron()[0])
        c.commit()
    assert r.get("ok"), r
    return r


def _firma_gata(firma):
    """Profilul complet (câmpurile obligatorii din Date firmă) și vectorul fiscal — ca formularul Date firmă să se poată salva și
    emiterea să nu fie blocată de lipsuri. Pe drumul aplicației: `salveaza_date` + `vector_fiscal_api.salveaza`."""
    if firma.get("_gata"):
        return
    from core import db, vector_fiscal_api
    _profil(firma, {"reg_com": "J40/1/2020", "caen": "4711", "adresa": "Str. Probei 1", "oras": "București", "judet": "B",
                    "cod_postal": "010101", "banca": "Banca Probă", "iban": "RO49AAAA1B31007593840000", "telefon": "0700000000",
                    "declarant_nume": "Popescu", "declarant_prenume": "Ion", "declarant_functie": "Administrator",
                    "forma_juridica": "SRL", "capital_subscris": "200", "capital_varsat": "200", "cont_venit_implicit": "704"})
    with db.get_conn(firma["schema"]) as c:
        r = vector_fiscal_api.salveaza(c, "micro", True, "lunar", False, inreg_art317=False, user_id=_patron()[0])
        c.commit()
    assert r.get("ok", True) is not False, r
    firma["_gata"] = True


def _metoda(firma):
    return sql('SELECT metoda_stoc FROM "%s".firma_profil WHERE id = 1' % firma["schema"])[0][0]


def _asigura_cv(firma):
    _firma_gata(firma)
    if _metoda(firma) != "cantitativ_valoric":
        _profil(firma, {"metoda_stoc": "cantitativ_valoric"})


def _asigura_serie(firma, serie="ZB"):
    """Numerotare configurată cu serie (drumul ecranului de configurare: `facturi_api.seteaza_numerotare`)."""
    from core import db, facturi_api
    _firma_gata(firma)
    with db.get_conn(firma["schema"]) as c:
        if not facturi_api.serie_facturi(c):
            assert facturi_api.seteaza_numerotare(c, serie=serie).get("ok"), "seria nu s-a putut stabili"
        c.commit()


def _fara_serie(firma):
    """Starea unei firme configurate ÎNAINTE de 06.10 (seria era opțională): numerotare configurată, serie goală. Aplicația de acum
    nu mai poate produce starea asta (exact reparația 34), deci se pune direct în profil — e premisa deficienței, nu o scurtătură."""
    _firma_gata(firma)
    sql('UPDATE "%s".firma_profil SET serie_factura = \'\', numerotare_configurata = true WHERE id = 1' % firma["schema"])


def _articol_cu_stoc(firma, denumire="Marfă E2E făină", cant="50", pret="4.00"):
    """Un articol de stoc cu cantitate (fișa de magazie, `stocuri_cv_api.intrare` — drumul butonului „Intrare”)."""
    from core import db, stocuri_cv_api
    _asigura_cv(firma)
    r = sql('SELECT id FROM "%s".articole WHERE denumire = %%s' % firma["schema"], (denumire,))
    if r:
        return r[0][0]
    with db.get_conn(firma["schema"]) as c:
        x = stocuri_cv_api.intrare(c, firma["schema"], {"denumire": denumire, "um": "kg", "cantitate": cant, "pret_unitar": pret,
                                                        "data": AZI.isoformat(), "document": "NIR E2E 1"})
        c.commit()
    assert "eroare" not in x, x
    return x["articol_id"]


def _cont_asistent(firma, eticheta):
    from core import asistenti_api, db, repo_utilizatori
    email = "%s-e2e-b-%d@prisma-cont.test" % (eticheta, int(_t.time() * 1000) % 10000000)
    with db.get_conn() as c, c.cursor() as cur:
        uid = repo_utilizatori.creeaza_cont_asistent(cur, email, "!", "Ana Probă %s" % eticheta, firma["cabinet_id"], True, False)[0]
        cur.execute("UPDATE public.users SET bun_venit_vazut_la = now() WHERE id = %s", (uid,))   # bun venit deja văzut
        asistenti_api.atribuie_firma(c, firma["cabinet_id"], uid, firma["tenant_id"])
        c.commit()
    return {"id": uid, "email": email}


def _scoate_cont(uid):
    for t, col in (("declaratii_coada", "creat_de_id"), ("declaratii_coada", "aprobat_de_id"), ("declaratii_coada", "respins_de_id"),
                   ("notificari", "user_id")):
        sql('DELETE FROM public."%s" WHERE %s = %%s' % (t, col), (uid,))
    sql("DELETE FROM public.users WHERE id = %s", (uid,))


@pytest.fixture(scope="module")
def ana_cont(firma_e2e):
    c = _cont_asistent(firma_e2e, "ana")
    yield c
    _scoate_cont(c["id"])


@pytest.fixture(scope="module")
def ana2_cont(firma_e2e):
    c = _cont_asistent(firma_e2e, "ana2")
    yield c
    _scoate_cont(c["id"])


@pytest.fixture()
def ana(browser, request, ana_cont):
    yield from _ecran(browser, request, ana_cont["email"])


@pytest.fixture()
def ana2(browser, request, ana2_cont):
    yield from _ecran(browser, request, ana2_cont["email"])


# ── navigare ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _deschide_firma(e, nume):
    """Firma din lista „Firme” — și pentru patron (grila cabinetului), și pentru asistent (arborele)."""
    pg = e.pg
    e.acasa()
    if pg.query_selector(".asi-nod[data-nod='firme']"):
        pg.click(".asi-nod[data-nod='firme']")
    else:
        pg.click("button.cab-card:has([data-cheie='firme'])")
        pg.wait_for_timeout(400)
        if pg.query_selector("#opt-existente"):
            pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
    pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=20000)


def _emitere(e, firma):
    _deschide_firma(e, firma["nume"])
    e.pg.click("#fa-facturi")
    e.pg.wait_for_selector("#fac-emite", timeout=20000)
    e.pg.click("#fac-emite")
    e.pg.wait_for_selector("#em-cui, #em-nu", timeout=20000)


def _client(pg):
    pg.fill("#em-cui", cui_cu_control(30000017))   # CUI cu cifra de control verificată (conftest)
    pg.fill("#em-nume", "Client Probă E2E SRL")
    pg.fill("#em-adresa", "Str. Clientului 2, București")


def _linie(pg, i, descriere, cant, pret, articol_id=None):
    """O linie a facturii, ca omul: denumirea (sau articolul din stoc), cantitatea, prețul; cota se alege din listă după ce
    propunerea automată a răspuns (altfel răspunsul întârziat ar suprascrie alegerea)."""
    with pg.expect_response(lambda r: "/produse/potriveste" in r.url, timeout=60000):
        if articol_id:
            pg.select_option("#em-l%d-articol" % i, str(articol_id))
        else:
            pg.fill("#em-l%d-descriere" % i, descriere)
    pg.wait_for_timeout(300)
    pg.fill("#em-l%d-cantitate" % i, str(cant))
    pg.fill("#em-l%d-pret_unitar" % i, str(pret))
    pg.select_option("#em-l%d-cota" % i, "21")


def _rezultat(pg):
    return pg.inner_text("#em-rezultat")


def _fereastra_firmei(e):
    """Din orice fereastră deschisă peste firmă: înapoi până la fereastra firmei."""
    for _ in range(5):
        if e.pg.query_selector("#fa-facturi"):
            return
        e.pg.click(".fereastra .nav-inapoi")
        e.pg.wait_for_timeout(500)
    assert e.pg.query_selector("#fa-facturi"), "n-am ajuns înapoi la fereastra firmei"


def _jurnal(e, firma, luna=None):
    _deschide_firma(e, firma["nume"])
    e.pg.click("#fa-jurnal")
    e.pg.wait_for_selector("#j-nota-noua", timeout=20000)
    if luna:
        _mergi_la_luna(e, *luna)


def _mergi_la_luna(e, an, luna):
    pg = e.pg
    for _ in range(14):
        txt = pg.inner_text(".fereastra p.pf-intro")
        if "%02d.%d" % (luna, an) in txt or "%02d/%d" % (luna, an) in txt:
            return
        cur = re.search(r"(\d{2})[./](\d{4})", txt)
        inainte = cur and (int(cur.group(2)), int(cur.group(1))) > (an, luna)
        pg.click("#j-prev" if inainte else "#j-next")
        pg.wait_for_function("(t) => !document.querySelector('.fereastra p.pf-intro') || "
                             "document.querySelector('.fereastra p.pf-intro').innerText !== t", arg=txt, timeout=20000)
        pg.wait_for_selector("#j-nota-noua", timeout=20000)
    raise AssertionError("luna %02d/%d nu s-a deschis în jurnal" % (luna, an))


def _nota_prin_ecran(e, firma, descriere, data, luna=None, doc="Contract E2E nr 1 din 01.10.2026", suma="100"):
    """Nota manuală scrisă din Registrul jurnal (+ Notă nouă -> Salvează). Întoarce id-ul ei."""
    pg = e.pg
    _jurnal(e, firma, luna)
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-desc", timeout=10000)
    pg.fill("#je-data", data)
    pg.fill("#je-desc", descriere)
    pg.fill("#je-doc", doc)
    pg.fill("#je-linii .je-deb", "612")
    pg.fill("#je-linii .je-cre", "401")
    pg.fill("#je-linii .je-sum", suma)
    with pg.expect_response(lambda r: r.url.split("?")[0].endswith("/jurnal") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#je-salveaza")
    assert rr.value.status < 400, rr.value.text()
    pg.wait_for_selector(".pf-frand:has-text('%s')" % descriere, timeout=20000)
    r = sql('SELECT id FROM "%s".inregistrari WHERE descriere = %%s ORDER BY id DESC LIMIT 1' % firma["schema"], (descriere,))
    assert r, "nota %r nu e în bază" % descriere
    return r[0][0]


def _coada_nota(firma, nota_id):
    """(id, stare) — ultimul element din coada cabinetului pentru nota dată."""
    r = sql("SELECT id, stare FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND perioada = %s "
            "ORDER BY id DESC LIMIT 1", (firma["tenant_id"], "nota-%d" % nota_id))
    return r[0] if r else None


def _de_validat(e):
    """Fereastra coadă a cabinetului (cardul „De validat” / „De depus” de pe desktop)."""
    pg = e.pg
    e.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    pg.wait_for_selector("#val-titlu", timeout=20000)
    pg.wait_for_timeout(500)


def _card_nota(e, firma, text):
    return e.pg.locator("#val-note .val-card").filter(has_text=firma["nume"]).filter(has_text=text)


def _card_element(e, coada_id):
    """Cardul din „De validat” care poartă elementul de coadă dat (după `data-coada-ids`, nu după text)."""
    pg = e.pg
    pg.wait_for_function("(i) => [...document.querySelectorAll('#val-note .val-card')].some(c => "
                         "c.dataset.coadaIds.split(',').includes(String(i)))", arg=coada_id, timeout=20000)
    idx = pg.evaluate("(i) => [...document.querySelectorAll('#val-note .val-card')].findIndex(c => "
                      "c.dataset.coadaIds.split(',').includes(String(i)))", coada_id)
    return pg.locator("#val-note .val-card").nth(idx)


def _nota_salarii(firma):
    r = sql('SELECT id FROM "%s".inregistrari WHERE sursa = \'salarii\' ORDER BY id DESC LIMIT 1' % firma["schema"])
    return r[0][0] if r else None


def _respinge_din_coada(e, firma, text, motiv, coada_id=None):
    pg = e.pg
    _de_validat(e)
    card = _card_element(e, coada_id) if coada_id else _card_nota(e, firma, text).first
    card.wait_for(timeout=20000)
    card.locator(".val-respinge").click()
    camp = pg.locator(".fereastra-corp textarea, .fereastra-corp input.camp-input").last
    camp.wait_for(timeout=10000)
    camp.fill(motiv)
    pg.locator(".fereastra-corp button.val-respinge").last.click()
    pg.wait_for_function("(m) => document.body.innerText.includes(m)", arg=motiv, timeout=20000)


def _valideaza_din_coada(e, firma, text):
    pg = e.pg
    _de_validat(e)
    card = _card_nota(e, firma, text).first
    card.wait_for(timeout=20000)
    card.locator(".val-aproba").click()
    if pg.query_selector("#caseta-atentie-activa #ca-ok"):
        pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('Ai validat')", timeout=20000)


def _in_vedere(pg, sel):
    """Elementul e în zona vizibilă a ferestrei (nu sub ea, nu deasupra)?"""
    return pg.evaluate("""(s) => { const e = document.querySelector(s); if (!e) return null;
        const r = e.getBoundingClientRect(); const c = e.closest('.fereastra-corp');
        const sus = Math.max(0, c ? c.getBoundingClientRect().top : 0);
        const jos = Math.min(innerHeight, c ? c.getBoundingClientRect().bottom : innerHeight);
        return r.top >= sus - 1 && r.bottom <= jos + 1; }""", sel)


def _cerere(pg, metoda, cale, corp=None):
    """Cererea pe care ar trimite-o ecranul, cu sesiunea omului (pentru refuzurile serverului)."""
    return pg.evaluate("""([m, c, b]) => fetch(c, {method: m, headers: {'Authorization': 'Bearer ' + sessionStorage.getItem('iconta_token'),
        'Content-Type': 'application/json'}, body: b ? JSON.stringify(b) : undefined}).then(r => r.status)""", [metoda, cale, corp])


# ═══ FACTURA ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_def_34_seria_ceruta_la_emitere_si_setata_din_refuz(patron, firma_e2e):
    """34. Factură: seria obligatorie la emitere, setabilă din mesajul de refuz.
    Pașii contabilului: firma configurată fără serie (cum permitea aplicația înainte de 06.10) -> Facturi -> „Emite factură” ->
    completează clientul și o linie de servicii -> „Emite factură”. Refuzul spune că firma n-are serie (CF art.319 alin.(20) lit.a)
    și cere seria chiar acolo; scrie „ZB” -> „Stabilește seria și emite” -> factura iese „ZB1”, cu formularul păstrat."""
    _fara_serie(firma_e2e)
    pg = patron.pg
    _emitere(patron, firma_e2e)
    assert "fără serie (se cere la emitere)" in pg.inner_text("#em-serie-nr")
    _client(pg)
    _linie(pg, 0, "Servicii de consultanță contabilă", 1, 100)
    pg.click("#em-emite")
    pg.wait_for_selector("#em-serie-noua", timeout=30000)
    refuz = _rezultat(pg)
    assert "n-are serie de facturare" in refuz and "319" in refuz, refuz
    assert pg.input_value("#em-nume") == "Client Probă E2E SRL", "formularul nu mai e cel scris"
    patron.captura("refuz")
    pg.fill("#em-serie-noua", "ZB")
    pg.click("#em-serie-si-emite")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    ok = _rezultat(pg)
    patron.captura("emisa")
    f = sql('SELECT serie, numar::text, total::text FROM "%s".facturi ORDER BY id DESC LIMIT 1' % firma_e2e["schema"])[0]
    assert f[0] == "ZB", f
    assert ("Factura %s%s emisă" % (f[0], f[1])) in ok or ("Factura %s" % f[1]) in ok, ok
    assert "121,00" in ok, ok          # 100 + TVA 21% = 121,00 lei pe ecran
    assert sql('SELECT serie_factura FROM "%s".firma_profil WHERE id = 1' % firma_e2e["schema"])[0][0] == "ZB"


def test_def_45_mesajul_de_dupa_buton_vine_in_vedere(patron, firma_e2e):
    """45. General: mesajele apărute după apăsarea unui buton cad sub zona vizibilă.
    Pașii contabilului: ecran mic (520 px înălțime) -> „Emite factură” cu o linie de marfă pe o firmă fără metodă de stoc ->
    „Emite factură” apăsat cu butonul la marginea de jos a ferestrei. Refuzul apare SUB buton; ecranul îl aduce în vedere."""
    if _metoda(firma_e2e):
        pytest.skip("metoda de stoc e deja declarată pe firma rulării (cazul cere o firmă fără metodă)")
    _asigura_serie(firma_e2e)
    pg = patron.pg
    pg.set_viewport_size({"width": 1700, "height": 520})
    _emitere(patron, firma_e2e)
    _client(pg)
    _linie(pg, 0, "Vânzare marfă: făină", 2, 150)
    pg.evaluate("() => document.querySelector('#em-emite').scrollIntoView({block: 'end'})")
    pg.wait_for_timeout(400)
    bb = pg.locator("#em-emite").bounding_box()
    pg.mouse.click(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)   # clic de om, fără derularea automată
    pg.wait_for_selector("#em-rezultat .em-curs-box", timeout=30000)
    assert "metoda de stoc" in _rezultat(pg)
    pg.wait_for_timeout(1500)                                              # derularea lină se termină
    patron.captura("refuz_in_vedere")
    assert _in_vedere(pg, "#em-rezultat .em-curs-box"), "refuzul de după „Emite” a rămas sub zona vizibilă"


def test_def_36_metoda_de_stoc_explicita_fara_implicit(patron, firma_e2e):
    """36. Stoc: metoda de stoc setare explicită pe firmă, fără valoare implicită tăcută.
    Pașii contabilului: firma nouă -> factura cu marfă -> „Emite factură”: refuz numit („metoda de stoc a firmei nu e declarată”),
    cu butonul spre Date firmă; acolo câmpul „Metoda de stoc” arată „— nedeclarată —” (nicio metodă aleasă în locul lui); alege
    global-valoric -> Salvează -> „Înapoi la factură” -> „Emite factură” -> factura se emite."""
    if _metoda(firma_e2e):
        pytest.skip("metoda de stoc e deja declarată pe firma rulării (cazul cere o firmă fără metodă)")
    _asigura_serie(firma_e2e)
    pg = patron.pg
    _emitere(patron, firma_e2e)
    _client(pg)
    _linie(pg, 0, "Vânzare marfă: făină", 2, 150)
    pg.click("#em-emite")
    pg.wait_for_selector("#em-deschide-date-firma", timeout=30000)
    refuz = _rezultat(pg)
    assert "metoda de stoc a firmei nu e declarată" in refuz, refuz
    assert not sql('SELECT 1 FROM "%s".facturi WHERE tert_nume = %%s AND total = 363' % firma_e2e["schema"], ("Client Probă E2E SRL",))
    patron.captura("refuz")
    pg.click("#em-deschide-date-firma")
    pg.wait_for_selector("#df-metoda_stoc", timeout=20000)
    assert pg.input_value("#df-metoda_stoc") == "", "metoda apare aleasă fără ca omul s-o fi ales"
    assert "nedeclarată" in pg.eval_on_selector("#df-metoda_stoc", "s => s.selectedOptions[0].textContent")
    patron.captura("date_firma_nedeclarata")
    pg.select_option("#df-metoda_stoc", "global_valoric")
    pg.click("#df-salveaza")
    pg.wait_for_selector("#df-inapoi-la", timeout=20000)
    pg.click("#df-inapoi-la")
    pg.wait_for_selector("#em-emite", timeout=20000)
    assert pg.input_value("#em-nume") == "Client Probă E2E SRL"
    pg.click("#em-emite")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    patron.captura("emisa")
    assert "363,00" in _rezultat(pg), _rezultat(pg)              # 2 × 150 + TVA 21% = 363,00
    assert _metoda(firma_e2e) == "global_valoric"


def test_def_44_factura_pastrata_dupa_date_firma(patron, firma_e2e):
    """44. Factură: pierdută a treia oară (fereastra firmei → Date firmă → înapoi).
    Pașii contabilului: „Emite factură” -> completează clientul și o linie -> înapoi la fereastra firmei -> „Date firmă” -> înapoi
    -> Facturi -> „Emite factură”: formularul e cum l-a lăsat, cu anunțul „Factura începută … a fost păstrată”."""
    _asigura_serie(firma_e2e)
    pg = patron.pg
    _emitere(patron, firma_e2e)
    _client(pg)
    _linie(pg, 0, "Servicii de consultanță fiscală", 3, 250)
    pg.wait_for_timeout(300)
    _fereastra_firmei(patron)
    pg.click("#fa-datefirma")
    pg.wait_for_selector("#df-salveaza", timeout=20000)
    _fereastra_firmei(patron)
    pg.click("#fa-facturi")
    pg.wait_for_selector("#fac-emite", timeout=20000)
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-cui", timeout=20000)
    patron.captura("reluata")
    assert pg.input_value("#em-nume") == "Client Probă E2E SRL"
    assert pg.input_value("#em-l0-descriere") == "Servicii de consultanță fiscală"
    assert pg.input_value("#em-l0-cantitate") == "3" and pg.input_value("#em-l0-pret_unitar") == "250"
    assert "a fost păstrată" in pg.inner_text("#em-ciorna")
    assert "907,50" in pg.inner_text("#em-total"), pg.inner_text("#em-total")   # 750 + 21% = 907,50
    pg.click("#em-renunta")
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => !document.querySelector('#em-nume') || document.querySelector('#em-nume').value === ''", timeout=20000)


def test_def_60_scadenta_propusa_editabila(patron, firma_e2e):
    """60. Factură: scadența goală implicit; trebuie propusă, editabilă.
    Pașii contabilului: „Emite factură”. „Data scadenței” vine completată cu data emiterii + 30 de zile (Legea 72/2013 art.3
    alin.(3) lit.a, termenul fără contract), cu explicația; schimbă data emiterii -> scadența o urmează; scrie altă scadență ->
    rămâne a lui când mai schimbă data emiterii."""
    _asigura_serie(firma_e2e)
    pg = patron.pg
    _emitere(patron, firma_e2e)
    assert pg.input_value("#em-data") == AZI.isoformat()
    assert pg.input_value("#em-scadenta") == (AZI + _dt.timedelta(days=30)).isoformat(), pg.input_value("#em-scadenta")
    assert "30 de zile" in pg.inner_text("#em-scadenta-ajutor")
    patron.captura("propusa")
    pg.fill("#em-data", "2026-10-01")
    pg.dispatch_event("#em-data", "change")
    assert pg.input_value("#em-scadenta") == "2026-10-31"
    pg.fill("#em-scadenta", "2026-12-15")
    pg.dispatch_event("#em-scadenta", "change")
    pg.fill("#em-data", "2026-10-02")
    pg.dispatch_event("#em-data", "change")
    assert pg.input_value("#em-scadenta") == "2026-12-15"
    patron.captura("editata")


# ═══ DATE FIRMĂ ═════════════════════════════════════════════════════════════════════════════════════════════════════════════
def _date_firma(e, firma):
    _deschide_firma(e, firma["nume"])
    e.pg.click("#fa-datefirma")
    e.pg.wait_for_selector("#df-salveaza", timeout=20000)


def _randuri_jurnal_df(pg):
    return pg.eval_on_selector_all("#df-jurnal tbody tr", "rs => rs.map(r => [...r.cells].map(c => c.innerText.trim()))")


def test_def_37_modificarea_din_date_firma_se_jurnalizeaza(patron, firma_e2e):
    """37. Date firmă: orice modificare se jurnalizează, vizibil cabinetului.
    Pașii contabilului: Date firmă -> schimbă telefonul și seria chitanțelor -> Salvează. „Istoricul modificărilor” arată, pentru
    fiecare câmp, cine, când, valoarea veche și cea nouă."""
    _firma_gata(firma_e2e)
    pg = patron.pg
    _date_firma(patron, firma_e2e)
    vechi = pg.input_value("#df-telefon")
    nou = "0711%06d" % (int(_t.time()) % 1000000)
    pg.fill("#df-telefon", nou)
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {}).innerText && "
                         "document.querySelector('#df-msg').innerText.includes('salvate')", timeout=20000)
    pg.wait_for_selector("#df-jurnal", timeout=20000)
    randuri = _randuri_jurnal_df(pg)
    patron.captura("istoric", intreaga=True)
    tel = [r for r in randuri if r[2] == "Telefon" and r[4] == nou]
    assert tel, "schimbarea telefonului nu e în istoric: %s" % randuri[:5]
    assert tel[0][3] == (vechi or "—"), tel[0]
    assert tel[0][0][:10] == AZI.strftime("%d.%m.%Y"), tel[0]
    assert _patron()[1] in tel[0][1], tel[0]


def test_def_61_istoricul_date_firma_lizibil(patron, firma_e2e):
    """61. Date firmă: istoricul arăta „cantitativ_valoric” și emailul; derulare laterală.
    Pașii contabilului: Date firmă -> Metoda de stoc: cantitativ-valoric -> Salvează. În „Istoricul modificărilor” rândul spune
    valorile cu eticheta din listă (nu cheia tehnică), „cine” e numele persoanei (nu emailul), iar tabelul încape în fereastră și pe
    un ecran îngust (420 px) — fără derulare laterală."""
    _firma_gata(firma_e2e)
    pg = patron.pg
    if _metoda(firma_e2e) == "cantitativ_valoric":
        _profil(firma_e2e, {"metoda_stoc": "global_valoric"})
    _date_firma(patron, firma_e2e)
    pg.select_option("#df-metoda_stoc", "cantitativ_valoric")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {}).innerText && "
                         "document.querySelector('#df-msg').innerText.includes('salvate')", timeout=20000)
    pg.wait_for_selector("#df-jurnal", timeout=20000)
    randuri = _randuri_jurnal_df(pg)
    metoda = [r for r in randuri if r[2] == "Metoda de stoc"]
    assert metoda, randuri[:5]
    r0 = metoda[0]
    assert r0[4].startswith("cantitativ-valoric (fișe de magazie"), r0
    assert "_" not in r0[3] + r0[4], "cheia tehnică pe ecran: %s" % r0
    assert "@" not in r0[1] and _patron()[1] in r0[1], "„cine” nu e numele persoanei: %s" % r0
    pg.set_viewport_size({"width": 420, "height": 900})
    pg.wait_for_timeout(600)
    lat = pg.evaluate("""() => { const t = document.querySelector('#df-jurnal'); const c = t.closest('.df-jurnal-cadru');
        return {tabel: t.scrollWidth, cadru: c ? c.clientWidth : null, cadruDerulare: c ? c.scrollWidth > c.clientWidth + 1 : null,
                pagina: document.documentElement.scrollWidth > innerWidth + 1}; }""")
    pg.locator("#df-jurnal").scroll_into_view_if_needed()
    patron.captura("istoric_ingust")
    assert not lat["pagina"] and not lat["cadruDerulare"], "derulare laterală la 420 px: %s" % lat


# ═══ STOCURI ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_def_62_nir_nou_nu_se_deschide_singur(patron, firma_e2e):
    """62. Stocuri: formularul „NIR nou” se deschidea singur.
    Pașii contabilului: firma -> Stocuri. Ecranul arată situația stocului; formularul „NIR nou” e închis până apasă „+ NIR nou”."""
    _firma_gata(firma_e2e)
    pg = patron.pg
    _deschide_firma(patron, firma_e2e["nume"])
    pg.click("#fa-stocuri")
    pg.wait_for_selector("#sn-toggle", timeout=20000)
    pg.wait_for_selector("#sn-zona", state="attached", timeout=20000)
    patron.captura("la_deschidere")
    assert not pg.is_visible("#sn-zona"), "formularul NIR nou e deschis fără să fi fost cerut"
    assert not pg.is_visible("#sn-salveaza")
    pg.click("#sn-toggle")
    pg.wait_for_selector("#sn-salveaza", state="visible", timeout=10000)


def test_def_35_iesirea_fara_document_primeste_bon_de_consum(patron, firma_e2e):
    """35. Note automate: notele fără document extern primesc un document intern generat.
    Pașii contabilului: Stocuri -> „Mișcări, fișe de magazie…” -> articolul -> cantitate 2, fără document -> „Ieșire la CMP”.
    Nota 607=371 din Registrul jurnal are documentul justificativ „Bon de consum nr N din <azi>” (Legea 82/1991 art.6 alin.(1)),
    nu „nederivat”."""
    aid = _articol_cu_stoc(firma_e2e)
    pg = patron.pg
    _deschide_firma(patron, firma_e2e["nume"])
    pg.click("#fa-stocuri")
    pg.wait_for_selector("#cv-toggle", timeout=20000)
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-iesire", state="visible", timeout=20000)
    pg.select_option("#cv-art", str(aid))
    pg.fill("#cv-data", AZI.isoformat())
    pg.fill("#cv-cant", "2")
    pg.fill("#cv-doc", "")
    pg.click("#cv-iesire")
    pg.wait_for_function("() => document.body.innerText.includes('Ieșire la CMP')", timeout=20000)
    n = sql('SELECT id, document_ref FROM "%s".inregistrari WHERE sursa = \'stocuri\' ORDER BY id DESC LIMIT 1' % firma_e2e["schema"])[0]
    _fereastra_firmei(patron)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    rand = pg.locator(".pf-frand[data-nota-id='%d']" % n[0])
    rand.wait_for(timeout=20000)
    rand.scroll_into_view_if_needed()
    txt = rand.inner_text()
    patron.captura("jurnal")
    assert "607 = 371" in txt and "8,00" in txt, txt                     # 2 kg × CMP 4,00 = 8,00 lei
    assert re.search(r"Document justificativ: Bon de consum nr \d+ din %s" % re.escape(AZI.strftime("%d.%m.%Y")), txt), txt
    assert "nederivat" not in txt


def test_def_59_pleaca_marfa_nu_se_repune_dupa_serie(patron, firma_e2e):
    """59. Factură: „Pleacă marfa acum?” se repunea după „Stabilește seria și emite”.
    Pașii contabilului: firmă cantitativ-valorică fără serie -> factura cu un articol din stoc -> „Emite factură” -> „Pleacă marfa
    acum?” -> „Nu, doar factură” -> refuzul seriei -> scrie seria -> „Stabilește seria și emite”: factura se emite direct, fără
    să mai întrebe a doua oară, și fără descărcare de gestiune (răspunsul dat a rămas)."""
    aid = _articol_cu_stoc(firma_e2e)
    _fara_serie(firma_e2e)
    pg = patron.pg
    _emitere(patron, firma_e2e)
    _client(pg)
    _linie(pg, 0, None, 1, 9, articol_id=aid)
    pg.click("#em-emite")
    pg.wait_for_selector("#em-poarta-nu", timeout=20000)
    pg.click("#em-poarta-nu")
    pg.wait_for_selector("#em-serie-noua", timeout=30000)
    patron.captura("refuz_serie")
    pg.fill("#em-serie-noua", "ZB")
    pg.click("#em-serie-si-emite")
    pg.wait_for_selector("#em-rezultat.em-bun, #em-poarta-nu", timeout=30000)
    patron.captura("dupa_serie")
    assert not pg.query_selector("#em-poarta-nu"), "„Pleacă marfa acum?” s-a pus din nou după stabilirea seriei"
    ok = _rezultat(pg)
    assert "10,89" in ok and "descărcat" not in ok, ok                   # 9 + 21% = 10,89; „Nu, doar factură” -> fără descărcare
    fid = sql('SELECT id FROM "%s".facturi ORDER BY id DESC LIMIT 1' % firma_e2e["schema"])[0][0]
    assert not sql('SELECT 1 FROM "%s".miscari_stoc WHERE factura_id = %%s' % firma_e2e["schema"], (fid,))


def test_def_51_o_factura_un_singur_element_de_validat(ana, patron, firma_e2e):
    """51. Coadă: o factură producea două note de validat separat.
    Pașii: Ana (numai „Poate pregăti”) emite o factură cu un articol din stoc, „Da, pleacă marfa” -> două note (contarea și ieșirea
    din stoc). Contabilul-șef deschide „De validat”: factura e UN element („Vezi notele →”), cu ambele note în el."""
    aid = _articol_cu_stoc(firma_e2e)
    _asigura_serie(firma_e2e)
    pg = ana.pg
    _emitere(ana, firma_e2e)
    _client(pg)
    _linie(pg, 0, None, 3, 10, articol_id=aid)
    pg.click("#em-emite")
    pg.wait_for_selector("#em-poarta-da", timeout=20000)
    pg.click("#em-poarta-da")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    ana.captura("emisa")
    f = sql('SELECT id, numar FROM "%s".facturi ORDER BY id DESC LIMIT 1' % firma_e2e["schema"])[0]
    note = sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s OR id IN (SELECT inregistrare_id FROM "%s".miscari_stoc '
               'WHERE factura_id = %%s)' % (firma_e2e["schema"], firma_e2e["schema"]), (f[0], f[0]))
    assert len(note) == 2, note
    _de_validat(patron)
    carduri = patron.pg.locator("#val-note .val-card").filter(has_text=firma_e2e["nume"]).filter(has_text=f[1])
    carduri.first.wait_for(timeout=20000)
    carduri.first.scroll_into_view_if_needed()
    patron.captura("de_validat")
    assert carduri.count() == 1, "factura %s apare în %d elemente de validat" % (f[1], carduri.count())
    ids = carduri.first.get_attribute("data-coada-ids").split(",")
    assert len(ids) == 2, ids
    assert "Vezi notele" in carduri.first.inner_text()


# ═══ NOTE ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_def_47_editorul_notei_are_data(patron, firma_e2e):
    """47. Note: formularul de editare nu avea dată.
    Pașii contabilului: Registru jurnal -> „+ Notă nouă” -> câmpul „Data notei” -> 03.10 -> Salvează; apoi „Editează” pe ea ->
    data 07.10 -> Salvează. Rândul notei arată 07.10.2026, iar nota din bază are data nouă."""
    _firma_gata(firma_e2e)
    pg = patron.pg
    desc = "E2E 47 chirie %d" % (int(_t.time()) % 100000)
    nid = _nota_prin_ecran(patron, firma_e2e, desc, "2026-10-03", luna=(2026, 10))
    rand = pg.locator(".pf-frand[data-nota-id='%d']" % nid)
    assert "03.10.2026" in rand.inner_text()
    rand.locator("[data-edit]").click()
    pg.wait_for_selector("#je-data", timeout=10000)
    assert pg.input_value("#je-data") == "2026-10-03", "editorul nu arată data notei"
    pg.fill("#je-data", "2026-10-07")
    patron.captura("editor")
    with pg.expect_response(lambda r: ("/jurnal/%d" % nid) in r.url and r.request.method == "PUT", timeout=30000) as rr:
        pg.click("#je-salveaza")
    assert rr.value.status < 400, rr.value.text()
    pg.wait_for_function("(i) => { const r = document.querySelector(`.pf-frand[data-nota-id='${i}']`); "
                         "return r && r.innerText.includes('07.10.2026'); }", arg=nid, timeout=20000)
    patron.captura("dupa")
    assert str(sql('SELECT data FROM "%s".inregistrari WHERE id = %%s' % firma_e2e["schema"], (nid,))[0][0]) == "2026-10-07"


def test_def_48_nota_la_validare_nu_se_editeaza_nici_nu_se_sterge(ana, firma_e2e):
    """48. Note: nota aflată la validare putea fi editată sau ștearsă de asistent.
    Pașii: Ana scrie o notă (intră la validare) -> pe rândul ei nu mai are „Editează” și „Șterge”, ci „La validare în cabinet: nu
    se modifică…”; iar serverul refuză modificarea și ștergerea trimise direct."""
    _firma_gata(firma_e2e)
    pg = ana.pg
    desc = "E2E 48 consumabile %d" % (int(_t.time()) % 100000)
    nid = _nota_prin_ecran(ana, firma_e2e, desc, "2026-10-06", luna=(2026, 10))
    assert (_coada_nota(firma_e2e, nid) or (None, None))[1] == "la_senior"
    rand = pg.locator(".pf-frand[data-nota-id='%d']" % nid)
    txt = rand.inner_text()
    ana.captura("la_validare")
    assert "La validare în cabinet: nu se modifică" in txt, txt
    assert rand.locator("[data-edit]").count() == 0 and rand.locator("[data-del]").count() == 0, "butoanele de modificare sunt pe rând"
    put = _cerere(pg, "PUT", "/tenants/%d/jurnal/%d" % (firma_e2e["tenant_id"], nid),
                  {"descriere": desc + " schimbat", "linii": [{"debit": "612", "credit": "401", "suma": 999}]})
    dele = _cerere(pg, "DELETE", "/tenants/%d/jurnal/%d" % (firma_e2e["tenant_id"], nid))
    assert put >= 400 and dele >= 400, (put, dele)
    r = sql('SELECT descriere, (SELECT sum(suma) FROM "%s".inregistrari_linii WHERE inregistrare_id = i.id)::text '
            'FROM "%s".inregistrari i WHERE id = %%s' % (firma_e2e["schema"], firma_e2e["schema"]), (nid,))
    assert r == [(desc, "100.00")], r


def test_def_54_notificarea_numeste_firma(ana, patron, firma_e2e):
    """54. Notificări: notificările despre note individuale nu numeau firma.
    Pașii: Ana scrie o notă -> contabilul-șef deschide clopoțelul: notificarea „Notă pregătită, de validat” numește firma."""
    _firma_gata(firma_e2e)
    desc = "E2E 54 telefonie %d" % (int(_t.time()) % 100000)
    _nota_prin_ecran(ana, firma_e2e, desc, "2026-10-06", luna=(2026, 10))
    pg = patron.pg
    patron.acasa()
    pg.click("#nav-clopot")
    pg.wait_for_selector(".clopot-item, .clopot-gol", timeout=20000)
    it = pg.locator(".clopot-item", has_text=desc).first
    it.wait_for(timeout=20000)
    txt = it.inner_text()
    patron.captura("clopot")
    assert "Notă pregătită, de validat" in txt and firma_e2e["nume"] in txt, txt


def test_def_50_notificarea_duce_la_nota(ana, patron, firma_e2e):
    """50. Notificări: click pe „Notă pregătită, de validat” doar închidea lista.
    Pașii: Ana scrie o notă -> contabilul-șef: clopoțel -> clic pe notificare -> se deschide „De validat” cu nota ei marcată."""
    _firma_gata(firma_e2e)
    desc = "E2E 50 transport %d" % (int(_t.time()) % 100000)
    nid = _nota_prin_ecran(ana, firma_e2e, desc, "2026-10-06", luna=(2026, 10))
    cid = _coada_nota(firma_e2e, nid)[0]
    pg = patron.pg
    patron.acasa()
    pg.click("#nav-clopot")
    pg.wait_for_selector(".clopot-item, .clopot-gol", timeout=20000)
    pg.locator(".clopot-item", has_text=desc).first.click()
    pg.wait_for_selector(".val-card.val-evidentiat", timeout=20000)
    patron.captura("dupa_clic")
    ev = pg.locator(".val-card.val-evidentiat")
    assert ev.count() == 1 and str(cid) in ev.first.get_attribute("data-coada-ids").split(","), "alt element marcat"
    assert desc in ev.first.inner_text()


def test_def_53_notele_de_validat_deasupra_textului_declaratiilor(ana, patron, firma_e2e):
    """53. Coadă: notele de validat stăteau sub textul „Patru-ochi e dezactivat…”.
    Pașii: Ana scrie o notă -> contabilul-șef deschide „De validat”: „Note de validat (N)” e primul lucru din fereastră, deasupra
    textului despre declarații, iar fereastra nu mai folosește termenul intern „Patru-ochi”."""
    _firma_gata(firma_e2e)
    desc = "E2E 53 energie %d" % (int(_t.time()) % 100000)
    _nota_prin_ecran(ana, firma_e2e, desc, "2026-10-06", luna=(2026, 10))
    pg = patron.pg
    _de_validat(patron)
    _card_nota(patron, firma_e2e, desc).first.wait_for(timeout=20000)
    patron.captura("fereastra")
    ordine = pg.evaluate("""() => { const n = document.querySelector('#val-note .cf-grup-titlu');
        const i = [...document.querySelectorAll('.fereastra-corp p.mig-intro')].find(p => !p.closest('#val-note') && !p.closest('#val-ciorne'));
        return {note: n ? n.getBoundingClientRect().top : null, intro: i ? i.getBoundingClientRect().top : null}; }""")
    assert ordine["note"] is not None and ordine["intro"] is not None, ordine
    assert ordine["note"] < ordine["intro"], "notele de validat stau sub textul despre declarații: %s" % ordine
    assert "patru-ochi" not in patron.fereastra().lower()


def test_def_52_cardul_numara_notele_ca_fereastra(ana, patron, firma_e2e):
    """52. Coadă: cardul „De depus” arăta 3, fereastra 2.
    Pașii: Ana scrie o notă -> contabilul-șef: pe desktop cardul spune „N note de validat”; deschide cardul: fereastra spune „Note de
    validat (N)” — același N. (Coada e a cabinetului întreg, scrisă și de alte rulări: comparația se repetă până două citiri
    consecutive cad pe aceeași stare a cozii.)"""
    _firma_gata(firma_e2e)
    desc = "E2E 52 chirie %d" % (int(_t.time()) % 100000)
    _nota_prin_ecran(ana, firma_e2e, desc, "2026-10-06", luna=(2026, 10))
    pg = patron.pg
    vazut = []
    for _ in range(4):
        patron.acasa()
        pg.wait_for_function("() => /not[ăe] de validat/.test((document.querySelector(\".cab-card-sinteza[data-cheie='validat']\") || {}).innerText || '')",
                             timeout=20000)
        card = pg.inner_text(".cab-card-sinteza[data-cheie='validat']")
        n_card = int(re.search(r"(\d+)\s+not[ăe] de validat", card).group(1))
        patron.captura("card")
        pg.click("button.cab-card:has([data-cheie='validat'])")
        pg.wait_for_selector("#val-note .cf-grup-titlu", timeout=20000)
        n_fer = int(re.search(r"Note de validat \((\d+)\)", pg.inner_text("#val-note .cf-grup-titlu"), re.I).group(1))
        vazut.append((n_card, n_fer))
        if n_card == n_fer:
            break
    patron.captura("fereastra")
    assert vazut[-1][0] == vazut[-1][1], "cardul și fereastra numără diferit: %s" % vazut


def test_def_56_jurnalul_nu_numara_nota_respinsa_de_validat(ana, patron, firma_e2e):
    """56. Registru jurnal: „1 de validat” pentru o notă respinsă.
    Pașii: Ana scrie o notă în septembrie -> contabilul-șef o respinge cu motiv -> Registrul jurnal al lunii: antetul spune „1
    respinsă, de corectat” (nu „1 de validat”), la contabil și la Ana, iar rândul arată motivul."""
    _firma_gata(firma_e2e)
    desc = "E2E 56 reparatii %d" % (int(_t.time()) % 100000)
    _nota_prin_ecran(ana, firma_e2e, desc, "2026-09-15", luna=(2026, 9))
    motiv = "Lipsește factura furnizorului %d" % (int(_t.time()) % 1000)
    _respinge_din_coada(patron, firma_e2e, desc, motiv)
    for e, cine in ((patron, "contabil"), (ana, "asistent")):
        _jurnal(e, firma_e2e, (2026, 9))
        antet = e.pg.inner_text(".fereastra p.pf-intro")
        e.captura(cine)
        assert "1 respinsă, de corectat" in antet, antet
        assert "de validat" not in antet and "netrimis" not in antet, "nota respinsă e numărată ca nevalidată: %s" % antet
        assert motiv in e.pg.locator(".pf-frand", has_text=desc).first.inner_text()


def test_def_58_ciorna_din_afara_cozii_se_trimite_la_validare(ana, patron, firma_e2e):
    """58. Coadă: ciornele de dinainte de mecanism apăreau „de validat”, dar nu erau în coadă.
    Pașii: o ciornă care nu e în coadă (scrisă de cine validează singur — contabilul-șef, în august) -> Ana deschide Registrul
    jurnal pe august: antetul spune „1 netrimisă la validare”, rândul are „Trimite la validare”; apasă -> nota e „la validare în
    cabinet” și chiar e în coadă."""
    _firma_gata(firma_e2e)
    desc = "E2E 58 abonament %d" % (int(_t.time()) % 100000)
    nid = _nota_prin_ecran(patron, firma_e2e, desc, "2026-08-20", luna=(2026, 8))
    assert _coada_nota(firma_e2e, nid) is None
    pg = ana.pg
    _jurnal(ana, firma_e2e, (2026, 8))
    antet = pg.inner_text(".fereastra p.pf-intro")
    rand = pg.locator(".pf-frand[data-nota-id='%d']" % nid)
    ana.captura("inainte")
    assert "1 netrimisă la validare" in antet and "de validat" not in antet, antet
    rand.locator("[data-retrimite]").click()
    pg.wait_for_function("() => ((document.querySelector('.fereastra p.pf-intro') || {}).innerText || '').includes('la validare în cabinet')",
                         timeout=20000)
    ana.captura("dupa")
    assert (_coada_nota(firma_e2e, nid) or (None, None))[1] == "la_senior"


def test_def_46_retrimiterea_nu_e_pregatire_noua(ana2, patron, firma_e2e):
    """46. Asistenți: „Acceptate din prima” număra retrimiterea ca pregătire nouă.
    Pașii: asistentul nou scrie o notă -> contabilul-șef o respinge -> asistentul o retrimite -> contabilul-șef o validează. Bara
    asistentului: „1 pregătite luna aceasta · 0% acceptate din prima” (nu 2 pregătite, 50%)."""
    _firma_gata(firma_e2e)
    desc = "E2E 46 curatenie %d" % (int(_t.time()) % 100000)
    nid = _nota_prin_ecran(ana2, firma_e2e, desc, "2026-10-06", luna=(2026, 10))
    _respinge_din_coada(patron, firma_e2e, desc, "Document greșit")
    pg = ana2.pg
    _jurnal(ana2, firma_e2e, (2026, 10))
    pg.locator(".pf-frand[data-nota-id='%d'] [data-retrimite]" % nid).click()
    pg.wait_for_function("(i) => document.querySelector('#caseta-atentie-activa #ca-ok') || (document.querySelector("
                         "`.pf-frand[data-nota-id='${i}']`) || {innerText: ''}).innerText.includes('La validare în cabinet')", arg=nid,
                         timeout=20000)
    if pg.query_selector("#caseta-atentie-activa #ca-ok"):   # retrimisă neschimbată: aplicația cere confirmarea explicită
        pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("(i) => (document.querySelector(`.pf-frand[data-nota-id='${i}']`) || {innerText: ''}).innerText"
                         ".includes('La validare în cabinet')", arg=nid, timeout=20000)
    _valideaza_din_coada(patron, firma_e2e, desc)
    ana2.acasa()
    pg.wait_for_function("() => /pregătite/.test((document.querySelector('.bara3') || {}).innerText || '')", timeout=20000)
    bara = pg.inner_text(".bara3")
    ana2.captura("bara")
    assert re.search(r"\b1\s+pregătite luna aceasta", bara), bara
    assert re.search(r"\b0%\s+acceptate din prima", bara), bara


# ═══ SALARII ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def _cnp(baza12):
    """CNP cu cifra de control din algoritmul oficial (CLAUDE.md „Date de test”), verificat și de validatorul aplicației."""
    from core.salariati_import_api import valideaza_cnp
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    cnp = baza12 + str(1 if c == 10 else c)
    assert valideaza_cnp(cnp)[0], cnp
    return cnp


def _salariat(firma, brut="4650"):
    """Un salariat cu normă întreagă din 01.09.2026, brut 4.650 lei (peste salariul minim; CAS 25% = 1.162,50 — exact cazul de rotunjire la leu) (drumul „+ Salariat nou”: `salariati_api.creeaza_salariat`)."""
    from core import db, salariati_api
    _firma_gata(firma)
    r = sql('SELECT id FROM "%s".salariati WHERE nume = %%s' % firma["schema"], ("Ionescu",))
    if r:
        return r[0][0]
    with db.get_conn(firma["schema"]) as c:
        x = salariati_api.creeaza_salariat(c, nume="Ionescu", prenume="Elena", cnp=_cnp("2850615400" + "12"),
                                           data_angajare="2026-09-01", salariu_brut=brut, cor="522101", tip_norma="intreaga",
                                           functie_baza=True, scutit_contrib_minim=False, persoane_intretinere=0)
        c.commit()
    return x["salariat_id"]


def _stat(e, firma):
    _deschide_firma(e, firma["nume"])
    e.pg.click("#fa-salariati")
    e.pg.wait_for_selector("#sp-contare", timeout=30000)


def _propunere(e):
    pg = e.pg
    with pg.expect_response(lambda x: "/salarii-contare/propunere" in x.url, timeout=90000) as rr:
        pg.click("#sp-contare")
    assert rr.value.status < 400, rr.value.text()
    pg.wait_for_selector("#sp-contare-zona table", timeout=20000)
    return rr.value.json()


def _linii_nota(pg):
    return pg.eval_on_selector_all("#sp-contare-zona table.fd-tabel:last-of-type tbody tr",
                                   "rs => rs.map(r => [...r.cells].map(c => c.innerText.trim()))")


def _lei(t):
    return float(t.replace(".", "").replace(",", ".").replace("lei", "").strip())


def test_def_38_fluturasul_nota_si_d112_aceleasi_sume(patron, firma_e2e):
    """38. Salarii: netul de pe fluturaș ≠ nota și D112; 421 nesoldat cu 0,79 lei.
    Pașii contabilului: salariata cu brut 4.050 lei -> Salariați (statul lunii) -> „Contabilizează statul”. CAS, CASS și impozitul
    de pe rândul salariatei sunt în lei întregi (rotunjite o dată, aritmetic — cum le declară D112) și sunt EXACT sumele din notă;
    netul = brut − ele; contul 421 se soldează la ban cu netul fluturașului."""
    _salariat(firma_e2e)
    pg = patron.pg
    _stat(patron, firma_e2e)
    sub = pg.locator(".pf-frand", has_text="Ionescu").first.locator(".pf-frand-sub").last.inner_text()
    m = {k: _lei(v) for k, v in re.findall(r"(brut|CAS|CASS|impozit|net)\s+([\d.]+,\d{2})", sub)}
    _propunere(patron)
    linii = _linii_nota(pg)
    patron.captura("propunere", intreaga=True)
    pe = lambda d, c: sum(_lei(x[2]) for x in linii if x[0] == d and x[1] == c)   # noqa: E731
    for k in ("CAS", "CASS", "impozit"):
        assert m[k] == int(m[k]), "%s cu bani pe fluturaș: %s" % (k, sub)
    assert pe("421", "4315") == m["CAS"] and pe("421", "4316") == m["CASS"] and pe("421", "444") == m["impozit"], (m, linii)
    assert round(m["brut"] - m["CAS"] - m["CASS"] - m["impozit"], 2) == m["net"], m
    credit_421 = sum(_lei(x[2]) for x in linii if x[1] == "421")
    debit_421 = sum(_lei(x[2]) for x in linii if x[0] == "421")
    assert round(credit_421 - debit_421, 2) == m["net"], (credit_421, debit_421, m)
    assert "Contul 421 se soldează exact cu netul fluturașilor (%s lei)" % sub.split("net ")[1].split(" ")[0] in patron.fereastra()


def test_def_39_mesajul_spune_ce_a_verificat_fara_toleranta(patron, firma_e2e):
    """39. Salarii: mesajul „coincide în limita de toleranță” acoperea fals diferența.
    Pașii contabilului: „Contabilizează statul” pe o lună care se soldează: mesajul spune ce s-a verificat („Contul 421 se soldează
    exact cu netul fluturașilor (X lei)”, X = netul de pe rândul salariatei), fără „toleranță”."""
    _salariat(firma_e2e)
    pg = patron.pg
    _stat(patron, firma_e2e)
    net = re.search(r"net\s+([\d.]+,\d{2})", pg.locator(".pf-frand", has_text="Ionescu").first.inner_text()).group(1)
    p = _propunere(patron)
    zona = pg.inner_text("#sp-contare-zona")
    patron.captura("mesaj")
    assert not p.get("divergente"), p.get("divergente")
    assert ("Contul 421 se soldează exact cu netul fluturașilor (%s lei)" % net) in zona, zona[:600]
    assert "toleran" not in zona.lower(), zona[:600]


def test_def_49_nota_de_salarii_pe_ultima_zi_a_lunii(ana, firma_e2e):
    """49. Salarii: nota datată în ziua 28; trebuie ultima zi a lunii.
    Pașii: Ana -> Salariați -> „Contabilizează statul” -> „Scrie nota ciornă”. În Registrul jurnal nota „Salariile lunii LL/AAAA”
    are data ultimei zile a lunii (31.10.2026 pentru octombrie)."""
    import calendar
    _salariat(firma_e2e)
    pg = ana.pg
    _stat(ana, firma_e2e)
    p = _propunere(ana)
    if not p.get("deja_contata"):
        with pg.expect_response(lambda x: re.search(r"/salarii-contare\?", x.url) is not None, timeout=90000):
            pg.click("#sp-contare-scrie")
        pg.wait_for_selector("#sp-contare-zona table", timeout=20000)
    ultima = _dt.date(LUNA[0], LUNA[1], calendar.monthrange(*LUNA)[1])
    _fereastra_firmei(ana)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    rand = pg.locator(".pf-frand", has_text="Salariile lunii %02d/%d" % (LUNA[1], LUNA[0])).first
    rand.wait_for(timeout=20000)
    rand.scroll_into_view_if_needed()
    ana.captura("jurnal")
    assert ultima.strftime("%d.%m.%Y") in rand.inner_text(), rand.inner_text()
    assert str(sql('SELECT data FROM "%s".inregistrari WHERE sursa = \'salarii\' ORDER BY id DESC LIMIT 1'
                   % firma_e2e["schema"])[0][0]) == ultima.isoformat()


def test_def_55_titlul_notei_de_salarii_fara_repetitie(ana, patron, firma_e2e):
    """55. Salarii: titlul notei se repeta („Stat de plata · Stat de plată”).
    Pașii: nota de salarii scrisă de Ana (49) -> contabilul-șef deschide „De validat”: titlul ei e „Notă · Salariile lunii LL/AAAA
    · Stat de plată nr … din …” — statul de plată apare o singură dată."""
    _salariat(firma_e2e)
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE sursa = \'salarii\'' % firma_e2e["schema"]):
        pg = ana.pg
        _stat(ana, firma_e2e)
        _propunere(ana)
        with pg.expect_response(lambda x: re.search(r"/salarii-contare\?", x.url) is not None, timeout=90000):
            pg.click("#sp-contare-scrie")
    _de_validat(patron)
    card = _card_element(patron, _coada_nota(firma_e2e, _nota_salarii(firma_e2e))[0])
    card.scroll_into_view_if_needed()
    titlu = card.locator(".val-titlu").inner_text()
    patron.captura("titlu")
    assert ("Salariile lunii %02d/%d" % (LUNA[1], LUNA[0])) in titlu, titlu
    norm = titlu.lower().replace("ă", "a").replace("ț", "t")
    assert norm.count("stat de plata") == 1, titlu


def test_def_40_ciorna_de_salarii_a_anei_ajunge_la_validare(ana, patron, firma_e2e):
    """40. Salarii: ciorna Anei invizibilă (contor 0, fără notificare, fără buton de validare).
    Pașii: Ana scrie nota de salarii din stat -> statul îi spune „e la validare în cabinet”. Contabilul-șef: cardul numără „note de
    validat”, clopoțelul are „Notă pregătită, de validat: … Salariile lunii …”, iar „De validat” arată nota cu „Validează” și
    „Respinge”."""
    _salariat(firma_e2e)
    pg = ana.pg
    _stat(ana, firma_e2e)
    p = _propunere(ana)
    if not p.get("deja_contata"):
        with pg.expect_response(lambda x: re.search(r"/salarii-contare\?", x.url) is not None, timeout=90000):
            pg.click("#sp-contare-scrie")
        pg.wait_for_function("() => document.querySelector('#sp-contare-zona').innerText.includes('la validare în cabinet')",
                             timeout=20000)
    assert "la validare în cabinet" in pg.inner_text("#sp-contare-zona")
    ana.captura("stat")
    nid = sql('SELECT id FROM "%s".inregistrari WHERE sursa = \'salarii\' ORDER BY id DESC LIMIT 1' % firma_e2e["schema"])[0][0]
    assert (_coada_nota(firma_e2e, nid) or (None, None))[1] == "la_senior"
    pp = patron.pg
    patron.acasa()
    pp.wait_for_function("() => /not[ăe] de validat/.test((document.querySelector(\".cab-card-sinteza[data-cheie='validat']\") || {}).innerText || '')",
                         timeout=20000)
    pp.click("#nav-clopot")
    pp.wait_for_selector(".clopot-item, .clopot-gol", timeout=20000)
    notif = pp.locator(".clopot-item").filter(has_text=firma_e2e["nume"]).filter(has_text="Salariile lunii")
    notif.first.wait_for(timeout=20000)
    assert "de validat" in notif.first.inner_text()
    patron.captura("clopot")
    pp.click("#nav-clopot")
    _de_validat(patron)
    card = _card_nota(patron, firma_e2e, "Salariile lunii").first
    card.wait_for(timeout=20000)
    card.scroll_into_view_if_needed()
    patron.captura("de_validat")
    assert card.locator(".val-aproba").count() == 1 and card.locator(".val-respinge").count() == 1


def test_def_63_fraza_despre_diferente_numai_cu_diferente(patron, firma_e2e):
    """63. Salarii: textul „Semnalul… cât timp cifrele diferă” apărea și când nu difereau.
    Pașii contabilului: nota de salarii a lunii există -> „Contabilizează statul”: nota și declarația au aceleași cifre, deci nu
    apare nicio frază despre diferențe care „rămân afișate”."""
    _salariat(firma_e2e)
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE sursa = \'salarii\'' % firma_e2e["schema"]):
        pg = patron.pg
        _stat(patron, firma_e2e)
        _propunere(patron)
        with pg.expect_response(lambda x: re.search(r"/salarii-contare\?", x.url) is not None, timeout=90000):
            pg.click("#sp-contare-scrie")
    pg = patron.pg
    _stat(patron, firma_e2e)
    p = _propunere(patron)
    zona = pg.inner_text("#sp-contare-zona")
    patron.captura("fara_diferente")
    assert p.get("deja_contata") and not p.get("divergente"), (p.get("deja_contata"), p.get("divergente"))
    assert "Diferențele de mai sus" not in zona and "Semnalul" not in zona and "diferă" not in zona, zona[:600]


def test_def_57_respingerea_se_vede_pe_stat_la_deschidere(ana, patron, firma_e2e):
    """57. Salarii: respingerea apărea pe stat abia după „Contabilizează statul”.
    Pașii: nota de salarii a Anei la validare -> contabilul-șef o respinge cu motiv -> Ana deschide Salariați: statul arată, fără
    niciun clic, „Nota de salarii #N a fost respinsă la validare: <motiv>”."""
    _salariat(firma_e2e)
    nid = sql('SELECT id FROM "%s".inregistrari WHERE sursa = \'salarii\' ORDER BY id DESC LIMIT 1' % firma_e2e["schema"])
    if not nid or (_coada_nota(firma_e2e, nid[0][0]) or (None, None))[1] != "la_senior":
        pg = ana.pg
        _stat(ana, firma_e2e)
        p = _propunere(ana)
        btn = pg.query_selector("#sp-contare-scrie")
        assert btn or p.get("deja_contata"), "nici notă, nici buton de scriere"
        if btn:
            with pg.expect_response(lambda x: re.search(r"/salarii-contare\?", x.url) is not None, timeout=90000):
                pg.click("#sp-contare-scrie")
        nid = sql('SELECT id FROM "%s".inregistrari WHERE sursa = \'salarii\' ORDER BY id DESC LIMIT 1' % firma_e2e["schema"])
    nid = nid[0][0]
    motiv = "Lipsește un salariat %d" % (int(_t.time()) % 1000)
    _respinge_din_coada(patron, firma_e2e, None, motiv, coada_id=_coada_nota(firma_e2e, nid)[0])
    _stat(ana, firma_e2e)
    zona = ana.pg.inner_text("#sp-contare-zona")
    ana.captura("stat_la_deschidere")
    assert ("Nota de salarii #%d a fost respinsă la validare: %s" % (nid, motiv)) in zona, zona[:400]


def test_def_42_concediul_medical_intra_in_nota_de_salarii(patron):
    """42. Salarii: concediul medical nu intra în nota de salarii.
    Pașii contabilului (citire, nu scrie nimic: propunerea doar calculează): firma de test „Panificatie Salarii Speciale”, care are în
    10/2026 un certificat de concediu medical -> Salariați -> statul lunii 10/2026 -> „Contabilizează statul”. Nota propusă are
    indemnizația pe 423 (6458 = 423 partea angajatorului / 4382 = 423 partea FNUASS — OUG 158/2005 art.12), iar contul 423 se
    soldează exact cu netul indemnizațiilor de pe fluturași (suma din mesaj = creditul 423 − debitul 423 din tabel)."""
    pg = patron.pg
    _deschide_firma(patron, "Panificatie Salarii Speciale")
    pg.click("#fa-salariati")
    pg.wait_for_selector("#sp-contare", timeout=30000)
    pasi = (AZI.year - 2026) * 12 + AZI.month - 10
    for _ in range(abs(pasi)):
        pg.click("#sp-prev" if pasi > 0 else "#sp-next")
        pg.wait_for_selector("#sp-contare", timeout=30000)
    _propunere(patron)
    linii = _linii_nota(pg)
    zona = pg.inner_text("#sp-contare-zona")
    patron.captura("propunere", intreaga=True)
    cm = [x for x in linii if x[1] == "423" and x[0] in ("6458", "4382")]
    assert cm, "indemnizația CM lipsește din notă: %s" % linii
    m = re.search(r"Contul 423 se soldează exact cu netul indemnizațiilor de concediu medical \(([\d.]+,\d{2}) lei\)", zona)
    assert m, zona[:700]
    sold = sum(_lei(x[2]) for x in linii if x[1] == "423") - sum(_lei(x[2]) for x in linii if x[0] == "423")
    assert round(sold, 2) == _lei(m.group(1)), (sold, m.group(1), linii)
