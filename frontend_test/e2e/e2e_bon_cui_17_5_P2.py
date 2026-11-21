# -*- coding: utf-8 -*-
"""BONUL CU CODUL CUMPĂRĂTORULUI ȘI TEMEIUL FISCAL LÂNGĂ TVA — lotul 17.5-P2 (AC153, AC154 din constatari_audit_complet.tsv; decizii_17_5_P2.txt și «De ce» din comanda_17_5_P2.txt).
Probă de acceptare GPT-6, revizie după N4. Rezultatele așteptate sunt roșu pe bază și verde pe C.

La 1366×768, ceas înghețat 03.11.2026, cu contul administratorului (dovada.71507), pe F1 Comert Stoc (tenant_9049). Snapshotul n-are niciun bon în F1: testul pune bonul martor
cu docs/dovezi/17_5_P2/semana_bon.py (cod cumpărător citit și absent, articol pe contul 6022, total 60,50, TVA 10,50) și îl scoate la sfârșit (finally). NU apasă «Certifică și contează»
(aprobarea se probează în core/test_bon_cui_cumparator_17_5_P2.py, pe schemă efemeră). Fiecare mesaj de eșec începe cu AC și cu un id e.1–e.5 propriu testului (distinct de ids din pasi_17_5_P2):
  e.1 AC153: fereastra bonului are rândul «CUI cumpărător pe bon: niciun cod înscris pe bon»;
  e.2 AC153: blocul #d-fiscal (imediat sub titlu, înaintea ferestrei împărțite poză/câmpuri) are clasa caseta-atentie și conține fraza întreagă «TVA nedeductibil: pe bon nu este înscris codul fiscal ...»;
  e.3 AC154: același bloc conține nota contului 6022 întreagă, cu art. 25 alin. (3) lit. l și art. 298 alin. (1);
  e.4 AC153: ruta /tenants/105779/bonuri/de-verificat (105779 = public.tenants.id al lui F1; 9049 e numai sufixul schemei) dă bonului cui_cumparator = «» , tva_deductibil = «nu» și avertismentele în ordinea: verdictul, apoi nota 6022;
  e.5: nicio cerere POST către /aproba nu a plecat (testul nu certifică nimic).
Un singur test."""
import hashlib
import importlib.util
import os
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
F1_ID = 105779   # public.tenants.id al lui F1 (core/auth_api.py:368–375 caută după el); tenant_9049 e numai numele schemei
TOP = ".fereastra-overlay:not(.fundal) "
TEXT_FARA_COD = ("TVA nedeductibil: pe bon nu este înscris codul fiscal al firmei cumpărătoare. Un bon fiscal ține loc de factură simplificată, deci justifică deducerea TVA, "
                 "numai dacă poartă codul de înregistrare în scopuri de TVA al beneficiarului (HG 1/2016 pct. 69 alin. (6); Cod fiscal art. 319 alin. (12) și (21)). "
                 "TVA intră în cheltuială. Verifică pe poză dacă codul chiar lipsește.")
NOTA_6022 = ("Combustibil: deductibilitatea cheltuielii e limitată la 50% pentru vehiculele care nu sunt folosite exclusiv în activitatea economică (Cod fiscal art. 25 alin. (3) lit. l), "
             "iar deducerea TVA aferentă tot la 50% (art. 298 alin. (1)); excepțiile din aceleași articole nu se verifică aici. Verifică folosirea vehiculului înainte de a certifica.")
RAND_CUI = "CUI cumpărător pe bon: niciun cod înscris pe bon"
JS_FISCAL = """(fen) => {
    const box = fen.querySelector('#d-fiscal');
    const split = fen.querySelector('.doc-split');
    const title = fen.querySelector('h2.pf-titlu');
    if (!box || !box.checkVisibility({opacityProperty:true, visibilityProperty:true})) return null;
    const rect = box.getBoundingClientRect();
    let top = 0, bottom = innerHeight, left = 0, right = innerWidth;
    for (let parent = box.parentElement; parent; parent = parent.parentElement) {
        const css = getComputedStyle(parent), r = parent.getBoundingClientRect();
        if (css.overflowY !== 'visible') { top = Math.max(top,r.top); bottom = Math.min(bottom,r.bottom); }
        if (css.overflowX !== 'visible') { left = Math.max(left,r.left); right = Math.min(right,r.right); }
    }
    return {text: box.innerText.replace(/\\s+/g, ' ').trim(),
            atentie: box.classList.contains('caseta-atentie'),
            pozitie: !!title && !!split && title.getBoundingClientRect().bottom <= rect.top + 1
                && rect.bottom <= split.getBoundingClientRect().top + 1
                && rect.top >= top - 1 && rect.top + 1 < bottom && rect.width > 0
                && rect.left >= left - 1 && rect.right <= right + 1};
}"""


def _incarca(cale, nume):
    spec = importlib.util.spec_from_file_location(nume, cale)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _api(pg, cale):
    return pg.evaluate("""async (c) => { const t = sessionStorage.getItem('iconta_token');
      const r = await fetch(c, { headers: { 'Authorization': 'Bearer ' + t } }); let j = null; try { j = await r.json(); } catch (e) {} return [r.status, j]; }""", cale)


def verdicte(text, bloc, bon, posturi):
    bloc = bloc or {}
    return {
        "e.1": RAND_CUI in text,
        "e.2": bool(bloc.get("atentie") and bloc.get("pozitie") and TEXT_FARA_COD in bloc.get("text", "")),
        "e.3": NOTA_6022 in bloc.get("text", ""),
        "e.4": (bon.get("cui_cumparator") == "" and bon.get("tva_deductibil") == "nu"
                and (bon.get("avertismente") or [])[:2] == [TEXT_FARA_COD, NOTA_6022]),
        "e.5": not posturi,
    }


def test_bon_cui_cumparator_17_5_P2(browser, capsys):
    from pathlib import Path
    from urllib.parse import urlsplit
    from conftest import _db, CAPTURI
    from core import ceas_proba

    port = int(os.environ.get("E2E_PORT", "8019"))
    if BAZA.rstrip("/") != "http://127.0.0.1:%d" % port:
        raise RuntimeError("E2E P cere adresa locală a serverului oficial de test")
    with _db().get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT current_database()")
        if cur.fetchone() != ("iconta_test",):
            raise RuntimeError("Fixture P: sesiunea nu este pe baza de test")

    parcurs = _incarca(os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"), "parcurs_17_1")
    local = Path(RAD) / "docs" / "dovezi" / "17_5_P2" / "semana_bon.py"
    sursa = local if local.is_file() else Path.home() / "ghid_incoming" / "semana_bon_17_5_P2.py"
    if hashlib.sha256(sursa.read_bytes()).hexdigest() != "7bb87547681db17bba68e767a95769000811a2cd8e8ceab117d1955611e23b55":
        raise RuntimeError("Fixture P: amprenta semănătorului diferă")
    semana = _incarca(str(sursa), "semana_bon")
    b = browser.new_context(viewport={"width":1366, "height":768})
    posturi = []
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        def protejeaza(route):
            if route.request.method == "POST" and urlsplit(route.request.url).path.endswith("/aproba"):
                posturi.append(urlsplit(route.request.url).path)
                route.abort()
            else:
                route.continue_()
        b.route("**/*", protejeaza)
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        status, corp = _api(pg, "/tenants")
        if status != 200 or not isinstance(corp, dict):
            raise RuntimeError("Fixture P: lista firmelor nu s-a încărcat")
        potriviri = [t for t in corp["tenants"] if t["nume"] == semana.F1]
        if len(potriviri) != 1 or potriviri[0]["id"] != F1_ID:
            raise RuntimeError("Fixture P: F1 din lista sesiunii diferă de F1 din snapshot")
        with semana.martor(potriviri[0]["id"]) as bon_id:
            parcurs.firma(pg, semana.F1)
            buton = pg.locator(TOP + "#fa-bonuri")
            if not buton.is_visible():
                grup = buton.locator("xpath=ancestor::*[starts-with(@id,'fgc-')][1]")
                ident = grup.get_attribute("id", timeout=5000)
                pg.locator(TOP + '[aria-controls="' + ident + '"]').click(timeout=5000)
            cale = "/tenants/%d/bonuri/de-verificat" % F1_ID
            with pg.expect_response(lambda r: urlsplit(r.url).path == cale and r.request.method == "GET",
                                    timeout=30000) as raspuns:
                buton.click(timeout=10000)
            if raspuns.value.status != 200:
                raise RuntimeError("Fixture P: lista de bonuri nu s-a încărcat")
            bonuri = [x for x in raspuns.value.json()["bonuri"] if x.get("id") == bon_id]
            if len(bonuri) != 1 or bonuri[0].get("comerciant") != semana.COMERCIANT or bonuri[0].get("numar_document") != semana.DOCUMENT:
                raise RuntimeError("Fixture P: lista nu identifică bonul tocmai creat")
            pg.locator(TOP + "[data-doc]", has_text=semana.COMERCIANT).click(timeout=15000)
            pg.locator(TOP + "#d-certifica").wait_for(state="attached", timeout=15000)
            fereastra = pg.locator(TOP + ".fereastra")
            titlu = pg.locator(TOP + "h2.pf-titlu").inner_text()
            if "Bon fiscal" not in titlu or semana.DOCUMENT not in titlu:
                raise RuntimeError("Fixture P: nu s-a deschis detaliul bonului martor")
            text = " ".join(fereastra.inner_text().split())
            bloc = fereastra.evaluate(JS_FISCAL)
            captura = Path(CAPTURI)
            captura.mkdir(exist_ok=True, parents=True)
            pg.screenshot(path=str(captura / "17_5_P2_detaliu_P1.png"))
            rezultate = verdicte(text, bloc, bonuri[0], posturi)
    finally:
        b.close()
    # Numai după navigare, măsurare și curățare. O excepție tehnică nu produce martori.
    with capsys.disabled():
        for ident, ok in rezultate.items():
            print("VERDICT %s %s" % (ident, "trece" if ok else "pica"), flush=True)
    assert all(rezultate.values()), {"rezultate": rezultate, "titlu": titlu, "bloc": bloc,
                                    "campuri_martor": sorted(bonuri[0]), "posturi": posturi}
