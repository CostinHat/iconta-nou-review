# -*- coding: utf-8 -*-
"""17.5-Q6 — colectorul martorilor E/C pentru matricea probelor (protocol §2). Rulat cu rulatorul nativ pe iconta_test:8019, sub lacătul oficial:
    sh docs/dovezi/17_5_Q6/rulare_8019.sh --restaureaza <iesire> --doar=<cale absolută la acest fișier>
Mediul: COLECTOR_IESIRE (director absolut nou), COLECTOR_COMMIT (sha-ul servit), COLECTOR_SCENARII (listă: datorate, cif).
Pentru fiecare (scenariu, caz, rezoluție) scrie: original_*.json (extrasul brut citit ÎNAINTE de acțiune, independent de UI), sursa_*.json
(commit, scenariu, caz, rezoluție, original + sha256, localizare, valori, extrageri), masuri_*.json (cheile din campuri_oracol_17_5_Q6.tsv)
și captura_*.png (prima vedere). Nu judecă nimic: predicatul e oracol_reparatii_17_5_Q6.py, comparația e verifica_matrice_17_5_Q6.py."""
import hashlib
import json
import os
import sys
from pathlib import Path

_ARB = os.environ.get("PYTHONPATH", "").split(":")[0]
sys.path.insert(0, os.path.join(_ARB, "frontend_test", "e2e"))
from conftest import BAZA, browser, sesiune  # noqa: E402,F401  — `browser` = fixture-ul sesiunii, importat ca să fie al acestui modul

IES = Path(os.environ.get("COLECTOR_IESIRE", "/tmp/colector_q6"))
COMMIT = os.environ.get("COLECTOR_COMMIT", "")
SCENARII = set(os.environ.get("COLECTOR_SCENARII", "datorate,cif").split(","))
REL = os.environ.get("COLECTOR_REL", "")   # calea lui IES relativă la directorul dovezilor (verifica_matrice rezolvă «original» față de el)
TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc SRL"
CONT_DEC = "dovada.71507@sesiuneab.test"
CONT_ADMIN = "patron@prisma-cont.test"
REZ = {"603x590": (603, 590), "1366x768": (1366, 768)}


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _scrie(nume, obj):
    p = IES / nume
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return p


def _depune(scenariu, caz, rez, original, localizare, valori, extrageri, masuri, pagina):
    """Scrie cele patru artefacte ale unei observații; întoarce căile relative la IES."""
    IES.mkdir(parents=True, exist_ok=True)
    k = f"{scenariu}_{caz}_{rez}"
    po = _scrie(f"original_{k}.json", original)
    ps = _scrie(f"sursa_{k}.json", {"commit": COMMIT, "scenariu": scenariu, "caz": caz, "rezolutie": rez, "original": f"{REL}/{po.name}" if REL else po.name,
                                     "sha256_original": _sha(po), "localizare": localizare, "valori": valori, "extrageri": extrageri})
    pm = _scrie(f"masuri_{k}.json", masuri)
    return po, ps, pm


def _context(browser, email, rez):
    from core.ceas_proba import MOMENT_REF
    ctx = browser.new_context(viewport={"width": REZ[rez][0], "height": REZ[rez][1]})
    ctx.clock.set_fixed_time(MOMENT_REF)
    ctx.add_init_script(sesiune(email))
    return ctx


def _firma(pg, nume, control):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.locator("button.cab-card:has([data-cheie='firme'])").click()
    pg.locator(TOP + "#opt-existente").click()
    pg.locator(TOP + "#firme-lista button.firme-rand").filter(has=pg.get_by_text(nume, exact=True)).click()
    tinta = pg.locator(TOP + control)
    tinta.wait_for(state="attached")
    grup = tinta.locator("xpath=ancestor::*[contains(concat(' ',normalize-space(@class),' '),' firme-optiuni ')][1]")
    if grup.count() and not grup.is_visible():
        pg.locator(TOP + f'button[aria-controls="{grup.get_attribute("id")}"]').click()
    tinta.click()


# proprietarii de derulare verticală pe drumul listă → document (inclusiv lista), ca în testul înghețat (MESURE)
JS_PROPRIETARI = """el => { const o = []; for (let n = el; n; n = n.parentElement) { const s = getComputedStyle(n);
  if (/auto|scroll/.test(s.overflowY) && n.scrollHeight > n.clientHeight + 1) o.push(n.id || n.className || n.tagName); } return o; }"""
JS_OPTIUNI = """s => [...s.options].map((o, i) => ({ index: i, value: o.value, an: o.dataset.an || null, luna: o.dataset.luna || null,
  eticheta: (o.dataset.nume || o.textContent).trim(), grup: o.parentElement.tagName === 'OPTGROUP' ? o.parentElement.label : '', inactiv: o.disabled }))"""


def test_datorate(browser):
    """726 (scenariul «datorate», F1, 603×590): ultima datorată activă din opțiunile-sursă, aleasă după derularea corpului; perioada la destinație."""
    if "datorate" not in SCENARII:
        return
    rez = "603x590"
    ctx = _context(browser, CONT_DEC, rez)
    try:
        pg = ctx.new_page()
        _firma(pg, F1, "#fa-declaratii")
        panou = pg.locator(TOP + "#dec-tip + .ds-lista")
        panou.locator("[role=option]").filter(has_text="D300 · 10/2026").first.wait_for(state="attached")
        pg.evaluate("document.fonts.ready")
        optiuni = pg.locator(TOP + "#dec-tip").evaluate(JS_OPTIUNI)
        datorate = [o for o in optiuni if o["grup"].startswith("Datorate") and not o["inactiv"] and o["value"]]
        assert datorate, "F1 nu are datorate în lista-sursă"
        ultima = datorate[-1]
        id_ultim = f"{ultima['value']}:{ultima['an']}-{ultima['luna']}"
        perioada_sursa = f"{int(ultima['luna']):02d}/{ultima['an']}"
        original = {"localizare": "select #dec-tip (opțiunile-sursă), citit înainte de orice derulare sau clic", "optiuni": optiuni,
                    "datorate_active": [{"id": f"{o['value']}:{o['an']}-{o['luna']}", "perioada": f"{int(o['luna']):02d}/{o['an']}", "eticheta": o["eticheta"]} for o in datorate]}
        n = len(original["datorate_active"]) - 1
        cap = IES / f"captura_datorate_F1_{rez}.png"
        IES.mkdir(parents=True, exist_ok=True)
        pg.screenshot(path=str(cap))
        lista = panou.locator("[role=listbox]")
        proprietari = lista.evaluate(JS_PROPRIETARI)
        lista_proprie = lista.evaluate("el => { const s = getComputedStyle(el); return /auto|scroll/.test(s.overflowY) && el.scrollHeight > el.clientHeight + 1 ? 1 : 0; }")
        rand = lista.locator("[role=option]:not(.ds-lista-inactiv)").filter(has=pg.get_by_text(ultima["eticheta"], exact=True)).last
        rand.scroll_into_view_if_needed()
        rand.click()
        sel = pg.locator(TOP + "#dec-tip").evaluate("s => ({value: s.value, index: s.selectedIndex})")
        an = pg.locator(TOP + "#dec-an").input_value()
        luna = pg.locator(TOP + "#dec-luna").input_value() if pg.locator(TOP + "#dec-luna").count() else ""
        masuri = {"id_selectat": f"{sel['value']}:{an}-{luna}", "id_ultim_sursa": id_ultim, "perioada_destinatie": f"{int(luna):02d}/{an}" if luna else an,
                  "perioada_sursa": perioada_sursa, "scrolluri_lista": lista_proprie, "scrolluri_traseu": len(proprietari),
                  "proprietari": proprietari, "index_selectat": sel["index"], "index_sursa": ultima["index"], "viewport": list(REZ[rez])}
        _depune("datorate", "F1", rez, original, "Declarații pasul 1, F1 Comert Stoc SRL, select #dec-tip; destinația: #dec-tip/#dec-an/#dec-luna după clic",
                {"id_ultim_sursa": id_ultim, "perioada_sursa": perioada_sursa},
                {"id_ultim_sursa": {"format": "json", "cale": ["datorate_active", n, "id"]},
                 "perioada_sursa": {"format": "json", "cale": ["datorate_active", n, "perioada"]}}, masuri, pg)
    finally:
        ctx.close()


def test_e12(browser):
    """e.1 (603×590) și e.2 (1366×768): originalul independent al ancorelor testului înghețat — etichetele native ale select-ului #dec-tip, în ordinea lor
    (fără opțiunea «alege» și fără valoarea goală), ultima opțiune activă și etichetele care conțin «d300», citite înainte de orice interacțiune."""
    if "e12" not in SCENARII:
        return
    for ident, rez in (("e.1", "603x590"), ("e.2", "1366x768")):
        ctx = _context(browser, CONT_DEC, rez)
        try:
            pg = ctx.new_page()
            _firma(pg, F1, "#fa-declaratii")
            pg.locator(TOP + "#dec-tip + .ds-lista [role=option]").filter(has_text="D300 · 10/2026").first.wait_for(state="attached")
            optiuni = pg.locator(TOP + "#dec-tip").evaluate("""s => [...s.options].filter(o => o.value && !o.hasAttribute('data-alege'))
              .map(o => ({ value: o.value, eticheta: (o.dataset.nume || o.textContent).trim(), motiv: o.dataset.motiv || '', inactiv: o.disabled }))""")
            active = [o for o in optiuni if not o["inactiv"]]
            original = {"localizare": "select #dec-tip al ferestrei Declarații (F1), opțiunile native în ordine, înainte de orice interacțiune",
                        "optiuni": optiuni, "labels": [o["eticheta"] for o in optiuni], "ultim_sursa": active[-1]["value"] if active else "",
                        "asteptate_filtru": [o["eticheta"] for o in optiuni if "d300" in (o["eticheta"] + " " + o["motiv"]).lower()]}
            IES.mkdir(parents=True, exist_ok=True)
            k = f"{ident}_F1_{rez}"
            po = _scrie(f"original_{k}.json", original)
            chei = ["labels", "ultim_sursa"] if ident == "e.1" else ["labels", "asteptate_filtru"]
            _scrie(f"original_meta_{k}.json", {"commit": COMMIT, "original": f"{REL}/{po.name}" if REL else po.name, "sha256_original": _sha(po),
                                                "valori": {c: original[c] for c in chei}, "extrageri": {c: {"format": "json", "cale": [c]} for c in chei}})
        finally:
            ctx.close()


def test_cif(browser):
    """867 (scenariul «cif», respingeri, 603×590 și 1366×768): răspunsul /spv/stare redat din fixture_867 (transport local, fără ANAF)."""
    if "cif" not in SCENARII:
        return
    fx = json.loads((Path(__file__).with_name("fixture_867_17_5_Q6.json")).read_text(encoding="utf-8"))
    corp = json.dumps(fx["raspuns"], ensure_ascii=False)
    for rez in ("603x590", "1366x768"):
        ctx = _context(browser, CONT_ADMIN, rez)
        try:
            pg = ctx.new_page()
            primit = {}

            def _reda(route):
                primit["url"] = route.request.url
                route.fulfill(status=200, content_type="application/json", body=corp)
            pg.route("**/spv/stare", _reda)
            pg.goto(BAZA + "/", wait_until="domcontentloaded")
            pg.locator("button.cab-card:has([data-cheie='setari'])").click()
            pg.locator("button.meniu-card", has_text="Conectare SPV").first.click()
            pg.wait_for_selector(TOP + "#spv-cuiuri", timeout=20000)
            pg.evaluate("document.fonts.ready")
            IES.mkdir(parents=True, exist_ok=True)
            brut = IES / f"raspuns_spv_stare_{rez}.json"
            brut.write_text(corp, encoding="utf-8")
            respingeri = [c["eroare"] for c in fx["raspuns"]["cuiuri"] if c.get("are_drept") is False]
            original = {"brut": brut.name, "sha256_brut": _sha(brut), "ruta": "/spv/stare", "provenienta": fx["provenienta"],
                        "respingeri": respingeri}
            pg.screenshot(path=str(IES / f"captura_cif_respingeri_{rez}.png"))
            JS_MOTIVE = """(m) => { const z = document.querySelector('.fereastra-overlay:not(.fundal) #spv-cuiuri'); if (!z) return [];
              const vazut = (e) => !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
              return m.filter((t) => [...z.querySelectorAll('li.spv-cui')].some((li) => vazut(li) && li.innerText.includes(t))); }"""
            initial = pg.evaluate(JS_MOTIVE, respingeri)
            sumare = pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #spv-cuiuri .ds-rezumat')]
              .filter((e) => e.offsetWidth || e.offsetHeight).map((e) => e.innerText.trim())""")
            import re
            numar = int(re.match(r"(\d+)", sumare[0]).group(1)) if sumare and re.match(r"(\d+)", sumare[0]) else None
            clicuri = 0
            plie = pg.locator(TOP + "#spv-cuiuri .ds-rezumat-plie")
            if plie.count():
                plie.first.click(); clicuri += 1
            deschise = pg.evaluate(JS_MOTIVE, respingeri)
            pg.screenshot(path=str(IES / f"captura_cif_respingeri_{rez}_deschis.png"))
            if plie.count():
                plie.first.click()
            dupa = pg.evaluate(JS_MOTIVE, respingeri)
            masuri = {"clicuri_deschidere": clicuri, "detalii_deschise": deschise, "initial_siruri_motiv": len(initial),
                      "motive_dupa_pliere": len(dupa), "numar_sumar": numar, "respingeri_sursa": respingeri, "sumare_initiale": len(sumare),
                      "text_sumar": sumare, "viewport": list(REZ[rez])}
            _depune("cif", "respingeri", rez, original, "Setări cont → Conectare SPV, #spv-cuiuri; răspunsul GET /spv/stare redat local din fixture_867_17_5_Q6.json",
                    {"respingeri_sursa": respingeri}, {"respingeri_sursa": {"format": "json", "cale": ["respingeri"]}}, masuri, pg)
        finally:
            ctx.close()


# ---------------------------------------------------------------- fixture-urile F172 / F179 / X02 și martorii «poarta» și «primita»
def _cod(obj):
    """Codul refuzului din corpul răspunsului (oricât de adânc), fără să presupună forma."""
    if isinstance(obj, dict):
        if isinstance(obj.get("cod"), str):
            return obj["cod"]
        for v in obj.values():
            c = _cod(v)
            if c:
                return c
    if isinstance(obj, list):
        for v in obj:
            c = _cod(v)
            if c:
                return c
    return None


def _suma_text(t):
    """«121,00 RON» / «1.234,56 lei» -> («121.00», «RON»): aceeași formă ca TaxInclusiveAmount din UBL (punct zecimal, două zecimale)."""
    import re
    m = re.search(r"(-?[\d.]+,\d{2})\s*([A-Za-z]{3}|lei)?", t or "")
    if not m:
        return None, None
    return m.group(1).replace(".", "").replace(",", "."), ("RON" if (m.group(2) or "lei").lower() == "lei" else m.group(2).upper())


def test_fixture(browser):
    """Pregătirea fixture-urilor (protocol §1, invocarea literală a scriptului arhitectului din rădăcina checkout-ului servit), confirmarea celor trei
    scenarii, apoi martorii «poarta» (P-F172) și «primita» (P-F179) la 1366×768 și 603×590, pe aceeași stare."""
    if "fixture" not in SCENARII:
        return
    import subprocess
    from conftest import Ecran, sql
    IES.mkdir(parents=True, exist_ok=True)
    out = IES / "fixture"
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("pregateste_fixture_17_5_Q6.py")), str(out)], cwd=_ARB, env=os.environ,
                       capture_output=True, text=True)
    (IES / "fixture_stdout.txt").write_text(r.stdout, encoding="utf-8")
    (IES / "fixture_stderr.txt").write_text(r.stderr[-20000:], encoding="utf-8")
    (IES / "fixture_rc.txt").write_text(str(r.returncode), encoding="utf-8")
    assert r.returncode == 0, r.stderr[-2000:]
    fx = json.loads((out / "fixture.json").read_text(encoding="utf-8"))
    firma = fx["firma"]
    schema = firma["schema"]
    # confirmarea celor trei scenarii pe copie (fără secrete): ciorna, factura SPV, două invitații neconsumate
    ciorne = sql("SELECT count(*) FROM public.ciorne_formular c JOIN public.users u ON u.id = c.user_id WHERE c.tenant_id = %s AND c.formular = 'factura' AND u.email = %s",
                 (firma["tenant_id"], CONT_ADMIN))[0][0]
    primite = sql(f'SELECT id, status FROM "{schema}".efactura_primite WHERE id_mesaj_anaf = %s', (fx["P-F179"]["id_mesaj"],))
    invitati = {w: sql("SELECT count(*) FROM public.users WHERE id = %s", (v["user_id"],))[0][0] for w, v in fx["P-X02"].items()}
    _scrie("fixture_confirmare.json", {"P-F172": {"ciorne_factura": ciorne}, "P-F179": {"randuri": [list(x) for x in primite]},
                                       "P-X02": invitati, "firma": firma["nume"]})
    assert ciorne >= 1 and len(primite) == 1 and all(invitati.values())
    for rez in ("1366x768", "603x590"):
        _poarta(browser, fx, rez, sql, Ecran)
        _primita(browser, fx, rez, out)


def _poarta(browser, fx, rez, sql, Ecran):
    from e2e_lot12_emit import _emiterea
    firma = fx["firma"]
    schema = firma["schema"]
    ctx = _context(browser, CONT_ADMIN, rez)
    try:
        pg = ctx.new_page()
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        ec = Ecran(pg, "colector_q6")
        initiale = [x[0] for x in sql(f'SELECT id FROM "{schema}".facturi ORDER BY id')]
        _emiterea(ec, firma)
        pg.wait_for_function("(a) => (document.querySelector('#em-l0-descriere') || {}).value === a", arg=fx["P-F172"]["articol"], timeout=20000)
        with pg.expect_response(lambda x: x.url.split("?")[0].endswith("/facturi/emite"), timeout=60000) as rr:
            pg.click(TOP + "#em-emite")
        resp = rr.value
        try:
            corp_r = resp.json()
        except Exception:  # noqa: BLE001
            corp_r = {"text": resp.text()}
        pg.wait_for_selector(TOP + ".caseta-poarta", timeout=20000)
        k = f"poarta_stoc_{rez}"
        pg.screenshot(path=str(IES / f"captura_{k}.png"))
        alegeri = pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .caseta-poarta button')]
          .filter((b) => !b.disabled && b.getAttribute('aria-disabled') !== 'true' && (b.offsetWidth || b.offsetHeight)).map((b) => b.innerText.trim())""")
        emite = pg.evaluate("""() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) #em-emite'); if (!b) return null;
          const motiv = b.getAttribute('data-motiv-inactiv') || '';
          const vazut = motiv && [...document.querySelectorAll('.fereastra-overlay:not(.fundal) *')].some((e) => e.children.length === 0 && (e.offsetWidth || e.offsetHeight) && (e.innerText || '').includes(motiv));
          return { activ: !(b.disabled || b.getAttribute('aria-disabled') === 'true'), motiv, motiv_vizibil: vazut ? motiv : '' }; }""")
        pg.locator(".fereastra-overlay:not(.fundal) .nav-x").first.click()   # abandon: fereastra se închide fără niciun răspuns la poartă
        pg.wait_for_timeout(1500)
        finale = [x[0] for x in sql(f'SELECT id FROM "{schema}".facturi ORDER BY id')]
        original = {"raspuns_emite": {"status": resp.status, "url": resp.url.split("?")[0].replace(BAZA, ""), "corp": corp_r},
                    "cod_raspuns": _cod(corp_r), "facturi_initiale": initiale, "inventar": f'SELECT id FROM "{schema}".facturi ORDER BY id (înainte de deschiderea emiterii)'}
        masuri = {"alegeri_active": alegeri, "cod_raspuns": _cod(corp_r), "emite_activ": bool(emite and emite["activ"]),
                  "facturi_finale": finale, "facturi_initiale": initiale, "motiv_vizibil": (emite or {}).get("motiv_vizibil", ""), "viewport": list(REZ[rez])}
        _depune("poarta", "stoc", rez, original, f"Emite factură pe firma fixture-ului ({firma['nume']}), ciorna reluată; POST /tenants/{firma['tenant_id']}/facturi/emite; inventarul: tabela facturi a schemei",
                {"cod_raspuns": original["cod_raspuns"], "facturi_initiale": initiale},
                {"cod_raspuns": {"format": "json", "cale": ["cod_raspuns"]}, "facturi_initiale": {"format": "json", "cale": ["facturi_initiale"]}}, masuri, pg)
    finally:
        ctx.close()


def _primita(browser, fx, rez, out):
    from conftest import Ecran
    firma = fx["firma"]
    numar = fx["P-F179"]["numar"]
    ctx = _context(browser, CONT_ADMIN, rez)
    try:
        pg = ctx.new_page()
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        ec = Ecran(pg, "colector_q6")
        ec.firma(firma["nume"])
        pg.evaluate("""() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) #fac-primite') ||
          document.querySelector('.fereastra-overlay:not(.fundal) [data-cheie="facturi"]'); return !!c; }""")
        from e2e_bloc_a import _card
        _card(ec, "facturi", "#fac-primite")
        pg.click(TOP + "#fac-primite")
        pg.wait_for_selector(TOP + "#fp-lista", timeout=25000)
        rand = pg.locator(TOP + ".fac-primita-btn").filter(has_text=numar).first
        rand.wait_for(timeout=20000)
        k = f"primita_SPV_local_{rez}"
        pg.screenshot(path=str(IES / f"captura_{k}.png"))
        txt_lista = rand.inner_text()
        id_lista = numar if numar in txt_lista else ""
        rand.click()
        pg.wait_for_selector(TOP + "#pr-total", timeout=20000)
        titlu = pg.locator(TOP + "h2.pf-titlu").first.inner_text()
        furnizor = pg.locator(TOP + "input[aria-label='Furnizor']").first.input_value().split(" · ")[0].strip()
        total, moneda = _suma_text(pg.locator(TOP + "#pr-total").input_value())
        detaliu = {"id": titlu.split("·")[-1].strip(), "furnizor": furnizor, "total": total, "moneda": moneda}
        pg.locator(".fereastra-overlay:not(.fundal) .nav-inapoi, .fereastra-overlay:not(.fundal) [aria-label^='Înapoi']").first.click()
        pg.wait_for_selector(TOP + "#fp-lista", timeout=20000)
        rev = pg.locator(TOP + ".fac-primita-btn").filter(has_text=numar)
        id_revenire = numar if rev.count() else ""
        xml = out / "factura_sursa.xml"
        rel_xml = f"{REL}/fixture/factura_sursa.xml" if REL else "fixture/factura_sursa.xml"
        import xml.etree.ElementTree as ET
        ns = {"b": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2", "a": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}
        root = ET.parse(xml).getroot()
        sursa_ubl = {"id": root.findtext("b:ID", namespaces=ns).strip(), "moneda": root.findtext("b:DocumentCurrencyCode", namespaces=ns).strip(),
                     "total": root.findtext("a:LegalMonetaryTotal/b:TaxInclusiveAmount", namespaces=ns).strip(),
                     "furnizor": root.findtext("a:AccountingSupplierParty/a:Party/a:PartyLegalEntity/b:RegistrationName", namespaces=ns).strip()}
        masuri = {"factura_detaliu": detaliu, "factura_sursa": sursa_ubl, "id_lista": id_lista, "id_revenire": id_revenire, "provenienta": "SPV simulat",
                  "text_lista": txt_lista, "viewport": list(REZ[rez])}
        original = {"factura_sursa_xml": rel_xml, "sha256_xml": _sha(xml), "provenienta": "SPV simulat", "id_mesaj": fx["P-F179"]["id_mesaj"],
                    "id_intern": fx["P-F179"]["id_intern"]}
        po, ps, pm = _depune("primita", "SPV_local", rez, original, f"Facturi → Facturi primite pe {firma['nume']}; factura UBL importată prin spv_receive.importa_mesaj (transport local)",
                             {"factura_sursa": sursa_ubl, "provenienta": "SPV simulat"},
                             {"factura_sursa": {"format": "ubl_factura", "original": rel_xml, "sha256_original": _sha(xml)},
                              "provenienta": {"format": "json", "cale": ["provenienta"]}}, masuri, pg)
    finally:
        ctx.close()


# ---------------------------------------------------------------- F025-S (scenariul «f025s»): cele trei cazuri căutate pe copia de test
JS_GET = """async (cale) => { const t = sessionStorage.getItem('iconta_token');
  const r = await fetch(cale, { headers: { Authorization: 'Bearer ' + t } }); return { status: r.status, text: await r.text() }; }"""


def _caz_f025(coduri):
    if "REEVALUARE_VALUTA" not in coduri:
        return "fara_blocaj"
    if coduri == ["REEVALUARE_VALUTA"]:
        return "cu_blocaj"
    if coduri.count("REEVALUARE_VALUTA") == 1 and coduri.index("REEVALUARE_VALUTA") > 0:
        return "cu_blocaj_anterior"
    return None


def test_f025s(browser):
    if "f025s" not in SCENARII:
        return
    from conftest import Ecran, la_luna_ceruta
    IES.mkdir(parents=True, exist_ok=True)
    # 1. căutarea cazurilor (răspunsul brut al controalelor lunii, pe firmele cabinetului de test, lunile 08–11/2026)
    ctx = _context(browser, CONT_ADMIN, "1366x768")
    gasite, cautare = {}, []
    try:
        pg = ctx.new_page()
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        firme = json.loads(pg.evaluate(JS_GET, "/tenants")["text"]).get("tenants", [])
        for f in firme:
            for luna in (8, 9, 10, 11):
                r = pg.evaluate(JS_GET, f"/tenants/{f['id']}/perioade-blocate?an=2026&luna={luna}")
                if r["status"] != 200:
                    continue
                corp = json.loads(r["text"])
                bl = ((corp.get("controale") or {}).get("blocaje"))
                if not isinstance(bl, list):
                    continue
                coduri = [b.get("cod") for b in bl]
                caz = _caz_f025(coduri)
                cautare.append({"tenant_id": f["id"], "nume": f.get("nume") or f.get("denumire"), "luna": luna, "coduri": coduri, "caz": caz})
                if caz and caz not in gasite:
                    gasite[caz] = {"tenant_id": f["id"], "nume": f.get("nume") or f.get("denumire"), "an": 2026, "luna": luna, "text": r["text"]}
    finally:
        ctx.close()
    _scrie("f025s_cautare.json", {"cautate": cautare, "gasite": {k: {x: v[x] for x in ("tenant_id", "nume", "an", "luna")} for k, v in gasite.items()}})
    martor = Path(__file__).with_name("martor_f025_17_5_Q6.js").read_text(encoding="utf-8")
    # 2. fiecare caz găsit, la ambele rezoluții
    for caz, g in gasite.items():
        for rez in ("603x590", "1366x768"):
            k = f"f025s_{caz}_{rez}"
            brut = IES / f"brut_{k}.json"
            brut.write_text(g["text"], encoding="utf-8")   # corpul integral primit de la GET /tenants/{id}/perioade-blocate?an=&luna= (originalul primar)
            raspuns = json.loads(g["text"])
            ctx = _context(browser, CONT_ADMIN, rez)
            try:
                pg = ctx.new_page()
                pg.goto(BAZA + "/", wait_until="domcontentloaded")
                ec = Ecran(pg, "colector_q6")
                ec.firma(g["nume"])
                pg.click(TOP + "#fa-inchidere")
                pg.wait_for_selector(TOP + "#il-prev", timeout=30000)
                la_luna_ceruta(ec, "#il-prev", g["an"], g["luna"])
                pg.wait_for_function("(l) => (document.querySelector('.fereastra-overlay:not(.fundal) .pf-intro') || {innerText: ''}).innerText.includes(l)",
                                     arg="%02d/%d" % (g["luna"], g["an"]), timeout=60000)
                pg.wait_for_selector(TOP + "#il-sem-blocaje", state="attached", timeout=60000)
                pg.wait_for_timeout(800)
                pg.evaluate("document.fonts.ready")
                m = pg.evaluate(martor, raspuns["controale"]["blocaje"])
                pg.screenshot(path=str(IES / f"captura_{k}.png"))
                intrare = {"tenant_id": g["tenant_id"], "luna": "%02d/%d" % (g["luna"], g["an"])}
                dest = {}
                clic = 0
                if m["butoane_total"] == 1:
                    pg.locator(TOP + "#il-reevaluare").click(); clic = 1
                    pg.wait_for_selector(".fereastra-overlay:not(.fundal) .fir-acum[aria-current='page']", timeout=30000)
                    pg.wait_for_timeout(1500)
                    dest = pg.evaluate("""() => { const f = document.querySelector('.fereastra-overlay:not(.fundal)'); const q = (s) => f.querySelector(s);
                      return { destinatie: (q('.fir-acum[aria-current="page"]') || {innerText: ''}).innerText.trim(), titlu: (q('h2.pf-titlu') || {innerText: ''}).innerText.trim(),
                               intro: (q('.pf-intro') || {innerText: ''}).innerText.trim(), text: (q('.fereastra-corp') || {innerText: ''}).innerText.trim().slice(0, 2000) }; }""")
                    pg.screenshot(path=str(IES / f"captura_{k}_destinatie.png"))
                import re
                lunad = re.search(r"(\d{2})/(\d{4})", (dest.get("intro") or "") + " " + (dest.get("titlu") or ""))
                # contextul intrării (firma și luna alese de colector) și suma (răspunsul controalelor nu poartă o sumă: null), într-un original separat, cu SHA
                pctx = IES / f"context_{k}.json"
                pctx.write_text(json.dumps({"intrare": intrare, "suma": None, "ruta": f"/tenants/{g['tenant_id']}/perioade-blocate?an={g['an']}&luna={g['luna']}"},
                                           ensure_ascii=False, sort_keys=True), encoding="utf-8")
                ctx_regula = {"format": "json", "original": f"{REL}/{pctx.name}" if REL else pctx.name, "sha256_original": _sha(pctx)}
                masuri = dict(m, blocaj="REEVALUARE_VALUTA" in [b.get("cod") for b in raspuns["controale"]["blocaje"]],
                              coduri_blocaje_sursa=[b.get("cod") for b in raspuns["controale"]["blocaje"]], clicuri_desfasurare=0, clicuri_deschidere=clic,
                              destinatie=dest.get("destinatie", ""), explicatie_ui=dest.get("intro", ""),
                              firma_luna_intrare=intrare, firma_luna_destinatie={"tenant_id": g["tenant_id"], "luna": lunad.group(0) if lunad else ""},
                              suma_sursa=None, suma_ui=None, destinatie_detalii=dest)
                _depune("f025s", caz, rez, {"brut": brut.name}, f"Închidere lună, {g['nume']} {intrare['luna']}; originalul primar = corpul GET /tenants/{g['tenant_id']}/perioade-blocate?an={g['an']}&luna={g['luna']}",
                        {"blocaj": masuri["blocaj"], "coduri_blocaje_sursa": masuri["coduri_blocaje_sursa"], "firma_luna_intrare": intrare, "suma_sursa": None},
                        {"blocaj": {"format": "are_reevaluare", "cale": ["controale", "blocaje"]},
                         "coduri_blocaje_sursa": {"format": "coduri_blocaje", "cale": ["controale", "blocaje"]},
                         "firma_luna_intrare": dict(ctx_regula, cale=["intrare"]), "suma_sursa": dict(ctx_regula, cale=["suma"])}, masuri, pg)
                # sursa trebuie să trimită la originalul primar (corpul integral), nu la un document compus: rescriu «original» spre el
                ps = IES / f"sursa_{k}.json"
                s = json.loads(ps.read_text(encoding="utf-8"))
                s["original"] = f"{REL}/{brut.name}" if REL else brut.name
                s["sha256_original"] = _sha(brut)
                ps.write_text(json.dumps(s, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
            finally:
                ctx.close()


# ---------------------------------------------------------------- P-F019-S (scenariul «pagini»): De validat cu 11 documente redate local
def _coada_q6(tenant_id, n=11):
    """n note de validat fictive (aceeași formă ca _note_fictive din e2e_de_validat_17_5_G.py), fiecare cu documentul ei: ultima pagină parțială (8 + 3)."""
    def nota(k):
        return {"id": 991000 + k, "tenant_id": tenant_id, "tip": "nota", "fel": "nota", "perioada": "nota-%d" % (991000 + k),
                "stare": "la_senior", "creat_de": "0", "creat_de_nume": "Coleg probă", "eticheta": "Notă Q6 %02d" % k,
                "nota": {"inregistrare_id": 991000 + k, "data": "2026-11-02", "descriere": "Notă Q6 %02d" % k, "document_ref": "Q6DOC-%02d" % k,
                         "total": "%d.00" % (10 + k), "rulaj": "%d.00" % (10 + k), "rulaj_storno": "0", "_an": 2026, "_luna": 11}}
    return {"coada": [nota(k) for k in range(1, n + 1)]}


JS_PAG = """() => { const f = document.querySelector('.fereastra-overlay:not(.fundal)'); const vazut = (e) => !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
  return [...f.querySelectorAll('#val-note tbody.tn-nota')].filter(vazut).map((tb) => tb.dataset.coadaIds || tb.dataset.tn); }"""


def test_pagini(browser):
    if "pagini" not in SCENARII:
        return
    import re
    from conftest import sql
    tid = sql("SELECT u.id FROM public.users u WHERE u.email = %s", (CONT_DEC,))[0][0]   # numai ca să existe contul; firma notelor e una a cabinetului
    for rez in ("603x590", "1366x768"):
        ctx = _context(browser, CONT_DEC, rez)
        try:
            pg = ctx.new_page()
            pg.goto(BAZA + "/", wait_until="domcontentloaded")
            firme = json.loads(pg.evaluate(JS_GET, "/tenants")["text"]).get("tenants", [])
            corp = _coada_q6(firme[0]["id"] if firme else 0)
            corp_txt = json.dumps(corp, ensure_ascii=False)

            def _reda(route):
                if route.request.method != "GET":
                    route.continue_()
                    return
                route.fulfill(status=200, content_type="application/json", body=corp_txt)
            pg.route(re.compile(r"^https?://[^/]+/coada(\?.*)?$"), _reda)
            pg.route(re.compile(r"^https?://[^/]+/coada/\d+/continut(\?.*)?$"), lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({"nota": {}, "linii": []})))
            k = f"pagini_lista_{rez}"
            IES.mkdir(parents=True, exist_ok=True)
            brut = IES / f"brut_{k}.json"
            brut.write_text(corp_txt, encoding="utf-8")
            ids = [str(x["id"]) for x in corp["coada"]]
            termen = "Q6DOC-1"
            asteptat = [str(x["id"]) for x in corp["coada"] if termen.lower() in (x["nota"]["document_ref"] + " " + x["nota"]["descriere"]).lower()]
            pg.goto(BAZA + "/", wait_until="domcontentloaded")
            pg.locator("button.cab-card:has([data-cheie='validat'])").click()
            pg.wait_for_selector(TOP + "#val-note tbody.tn-nota", timeout=30000)
            pg.wait_for_timeout(800)
            pg.screenshot(path=str(IES / f"captura_{k}.png"))
            titlu = pg.locator(TOP + "#val-note-titlu").inner_text()
            m_t = re.search(r"\((\d+)\)", titlu)
            vazut = """(s) => { const e = document.querySelector('.fereastra-overlay:not(.fundal) ' + s); if (!e) return false; const r = e.getBoundingClientRect();
              return r.width > 0 && r.height > 0 && r.top >= 0 && r.bottom <= innerHeight && r.left >= 0 && r.right <= innerWidth; }"""
            sumar_vizibil = pg.evaluate(vazut, "#val-note-titlu") and pg.evaluate(vazut, "#val-titlu")
            filtru_vizibil = pg.evaluate(vazut, "#val-cauta")
            proprietari = pg.locator(TOP + "#val-note").evaluate(JS_PROPRIETARI)
            pagini = [pg.evaluate(JS_PAG)]
            urm = pg.locator(TOP + "#val-n-pag-urm")
            while urm.count() and urm.get_attribute("aria-disabled") != "true" and len(pagini) < 10:
                urm.click()
                pg.wait_for_timeout(300)
                pagini.append(pg.evaluate(JS_PAG))
            # ultimul document: deschis din ultima pagină, apoi închis (revenire); pagina rămâne
            ultim = pagini[-1][-1] if pagini and pagini[-1] else None
            pagina_dinainte = len(pagini)
            filtru_initial = pg.locator(TOP + "#val-cauta").input_value()
            if ultim:
                tb = pg.locator(TOP + f'#val-note tbody.tn-nota[data-coada-ids="{ultim}"] .tn-deschide').first
                if not tb.count():
                    tb = pg.locator(TOP + "#val-note tbody.tn-nota .tn-deschide").last
                tb.click(); pg.wait_for_timeout(500); tb.click(); pg.wait_for_timeout(300)
            pagina_dupa = pg.evaluate("() => { const t = document.querySelector('.fereastra-overlay:not(.fundal) #val-n-pag-text'); const m = t && t.innerText.match(/Pagina (\\d+)/); return m ? Number(m[1]) : 1; }")
            filtru_dupa_revenire = pg.locator(TOP + "#val-cauta").input_value()
            pg.fill(TOP + "#val-cauta", termen)
            pg.wait_for_timeout(800)
            observat = pg.evaluate(JS_PAG)
            pagina_dupa_filtru = pg.evaluate("() => { const t = document.querySelector('.fereastra-overlay:not(.fundal) #val-n-pag-text'); const m = t && t.innerText.match(/Pagina (\\d+)/); return m ? Number(m[1]) : 1; }")
            pg.fill(TOP + "#val-cauta", "ZZQ6NIMIC")
            pg.wait_for_timeout(800)
            fara = pg.evaluate(JS_PAG)
            masuri = {"filtru_asteptat": asteptat, "filtru_dupa_revenire": filtru_dupa_revenire, "filtru_fara_rezultat": fara, "filtru_initial": filtru_initial,
                      "filtru_observat": observat, "filtru_vizibil": bool(filtru_vizibil), "id_sursa": ids, "pagina_dinainte": pagina_dinainte,
                      "pagina_dupa_filtru": pagina_dupa_filtru, "pagina_dupa_revenire": pagina_dupa, "pagini": pagini, "scrolluri_verticale": len(proprietari),
                      "sumar_vizibil": bool(sumar_vizibil), "total_sumar": int(m_t.group(1)) if m_t else None, "ultim_deschis": ultim,
                      "titlu_sumar": titlu, "viewport": list(REZ[rez])}
            pctx = IES / f"context_{k}.json"
            pctx.write_text(json.dumps({"termen": termen, "regula": "documentele al căror document_ref sau descriere conțin termenul (fără diferență de majuscule)",
                                        "filtru_asteptat": asteptat, "brut": brut.name, "sha256_brut": _sha(brut)}, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            n = len(corp["coada"])
            _depune("pagini", "lista", rez, {"brut": brut.name}, "De validat (cardul de pe pagina principală), «Note de validat»; GET /coada redat local cu 11 note fictive (forma _note_fictive, 17.5-G)",
                    {"id_sursa": ids, "filtru_asteptat": asteptat},
                    {"id_sursa": {"format": "json", "cale": ["ids"]}, "filtru_asteptat": {"format": "json", "original": f"{REL}/{pctx.name}" if REL else pctx.name, "sha256_original": _sha(pctx), "cale": ["filtru_asteptat"]}},
                    masuri, pg)
            # originalul primar: un extras cu id-urile, în ordinea răspunsului, cu referința la corpul brut
            pids = IES / f"ids_{k}.json"
            pids.write_text(json.dumps({"ids": ids, "brut": brut.name, "sha256_brut": _sha(brut), "n": n}, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            ps = IES / f"sursa_{k}.json"
            s = json.loads(ps.read_text(encoding="utf-8"))
            s["original"] = f"{REL}/{pids.name}" if REL else pids.name
            s["sha256_original"] = _sha(pids)
            ps.write_text(json.dumps(s, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
            # cazul «filtru» (aceeași sarcină; matricea are cazurile lista,filtru): aceleași martori, alt nume de rând
            for nume in ("masuri", "sursa"):
                src = IES / f"{nume}_{k}.json"
                d = json.loads(src.read_text(encoding="utf-8"))
                if nume == "sursa":
                    d["caz"] = "filtru"
                (IES / f"{nume}_pagini_filtru_{rez}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
            import shutil
            shutil.copy(IES / f"captura_{k}.png", IES / f"captura_pagini_filtru_{rez}.png")
        finally:
            ctx.close()
