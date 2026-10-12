# -*- coding: utf-8 -*-
"""Deficiențele 220–225 din comanda Costin 10.10.2026 seara (verbatim în DECIZII), probate în browser, pe firme noi ale rulării și pe
firmele de test ale cabinetului. Pașii contabilului sunt în docstringul fiecărui test."""
import datetime as _dt
import re

import pytest

from conftest import _db, firma_noua, sql
from e2e_bloc_a import ORDINE_CABINET, cont_asistent, ecran_cont   # noqa: F401 — ORDINE_CABINET: aceeași ordine a cardurilor
from e2e_bloc_d import PATRON, _api, _date_firma, _deschide, _nota_validata

AZI = _dt.date.today()
_ROSU = re.compile(r"#ff8a80|rosu-semafor|cf-rosu|pct-rosu")


def _fereastra_html(pg):
    return pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f ? f.innerHTML : ''; }")


def _rezumate_la_zi():
    """Tura lucrătorului de rezumate (pe producție: cronul de la 5 minute, `python -m core.firma_rezumat`), pe baza de TEST. Pe
    instanța plasei cronul nu rulează, iar recalcularea în fundal pornește numai după o scriere: pe o versiune nouă de cod, o listă
    deschisă înaintea oricărei scrieri arată toate firmele „în recalculare” (gri) — prins la mutațiile e2e ale lotului 220–225."""
    from core import firma_rezumat
    _db()
    for _ in range(50):
        if not firma_rezumat.recalculeaza_lot().get("ramase"):
            return
    raise AssertionError("rezumatele nu s-au recalculat în 50 de ture")


def _lista_control(ecran):
    """Rândurile listei Control fiscal, cu rezumatele firmelor la zi (starea reală, nu „în recalculare”)."""
    pg = ecran.pg
    _rezumate_la_zi()
    ecran.acasa()
    pg.click("button.cab-card:has([data-cheie='control'])")
    pg.wait_for_selector("#cf-lista .mig-frand", timeout=120000)
    assert not pg.locator("#cf-lista .mig-frand-sub", has_text="în recalculare").count(), "rezumatele nu sunt la zi după tura lucrătorului"
    return pg.eval_on_selector_all("#cf-lista .mig-frand", """es => es.map(e => ({nume: e.querySelector('.mig-frand-nume').innerText,
        eticheta: e.querySelector('.cf-stare').innerText.trim(), dot: e.querySelector('.cf-stare .cf-dot').getAttribute('style'),
        sub: e.querySelector('.mig-frand-sub').innerText}))""")


# ── 220 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_220_rosu_numai_cu_termen_depasit(patron):
    """220. Control fiscal: declarațiile apar cu roșu încă dinainte de termen. Roșu înseamnă termen depășit.
    Pașii contabilului: Control fiscal -> lista firmelor: o firmă e roșie numai cu restanțe („restanță”, cu numărul lor), oricâte
    neconcordanțe ar avea -> o firmă a cabinetului cu „TVA nedeclarat” / „Salarii nedeclarate” (controlul încrucișat, roșu până azi)
    -> detaliul ei: constatarea nu e roșie; roșul stă numai pe „Restanțe”."""
    pg = patron.pg
    randuri = _lista_control(patron)
    patron.captura("lista")
    assert len(randuri) >= 5, randuri
    for r in randuri:
        rosu = bool(_ROSU.search(r["dot"] or ""))
        assert rosu == (r["eticheta"] == "restanță"), r
        assert not rosu or re.search(r"\d+ restanț", r["sub"]), r
    assert any(r["eticheta"] == "restanță" for r in randuri), "anti-vacuu: firmele de test au restanțe reale"
    cu_neconcordanta = [r for r in randuri if "nedeclarat" in r["sub"]]
    assert cu_neconcordanta, "anti-vacuu: firmele de test au constatări încrucișate"
    pg.locator("#cf-lista .mig-frand", has_text=cu_neconcordanta[0]["nume"]).first.click()
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && f.querySelector('#cf-audit-run'); }",
                         timeout=120000)
    pg.wait_for_timeout(500)
    html = _fereastra_html(pg)
    patron.captura("detaliu")
    assert "nedeclarat" in html, html[:1500]          # anti-vacuu: constatarea e pe ecran
    rosii = pg.evaluate("""() => {
      const f = [...document.querySelectorAll('.fereastra')].pop();
      const titlu = [...f.querySelectorAll('.cf-grup-titlu')].find((t) => /^restanțe/i.test(t.innerText.trim()));   // titlul e cu majuscule din CSS
      const grup = titlu ? titlu.nextElementSibling : null;
      const rosu = (e) => /cf-rosu|pct-rosu|cf-termen-rosu/.test(e.className || '') || /#ff8a80|rosu-semafor/.test(e.getAttribute('style') || '');
      return [...f.querySelectorAll('*')].filter((e) => rosu(e) && e !== titlu && !(grup && grup.contains(e)) && !e.closest('.mig-intro'))   // antetul = starea firmei
        .map((e) => (e.className || e.tagName) + ': ' + (e.parentElement.innerText || '').slice(0, 80)); }""")
    assert rosii == [], rosii


# ── 223 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#: funcțiile pe care serverul le refuză unui asistent cu numai „Poate pregăti” (core/ansamblu.RUTA_FUNCTIONALITATE) + cea cu ecran numai
#: la cabinet; câteva, numite, ca probă pe ecran
NU_PENTRU_ANA = {"Panoul de capacitate", "Tiparele de respingere ale declarațiilor", "Analiza AI a tiparelor de respingere",
                 "Export GDPR complet cabinet (portabilitate)", "Blocare perioade", "Starea migrării pe straturi",
                 "Sinteza zilnică pe email", "Chei API publice per cabinet", "Contabilii și asistenții cabinetului",
                 "Conexiunea cu registrul REGES"}


def _catalog(ecran, ascunse=False):
    ecran.acasa()
    ecran.pg.click("#nav-ghid")
    ecran.pg.wait_for_selector(".fereastra .ans-grupa-lista li", timeout=20000)
    return set(ecran.pg.eval_on_selector_all(".fereastra .ans-grupa-lista li", "(els, a) => els.filter(x => (x.offsetParent === null) === a)"
                                             ".map(x => x.childNodes[0].textContent.trim())", ascunse))


def test_def_223_catalogul_lui_ana_arata_doar_ce_poate_folosi(browser, request, patron):
    """223. Utilizatorul junior (Ana Asistent) vede în catalog funcții de administrator; catalogul arată doar ce poate folosi rolul lui
    (parțialul nr. 5). Pașii: Ana (asistent, numai „Poate pregăti”, o firmă alocată) -> „?” -> „Ce cuprinde aplicația”: nicio funcție
    a administratorului, nici a validării / depunerii pe care nu le are; munca ei zilnică e acolo (și portalul clientului, pe care îl
    vede prin previzualizare) -> contabilul-șef, același „?”: vede tot catalogul, nimic ascuns."""
    with cont_asistent(firme=(4838,)) as a, ecran_cont(browser, request, a["email"]) as e:
        ana = _catalog(e)
        e.captura("catalog_ana")
    admin = _catalog(patron)
    patron.captura("catalog_admin")
    assert _catalog(patron, ascunse=True) == set(), "contabilul-șef vede tot catalogul"   # filtrul e al rolului, nu al portalului
    assert len(ana) > 100 and {"Generare contracte", "Declarația D300", "Editor note contabile"} <= ana, "anti-vacuu"
    assert not NU_PENTRU_ANA & ana, sorted(NU_PENTRU_ANA & ana)
    assert {"Panoul de capacitate", "Contabilii și asistenții cabinetului", "Blocare perioade", "Sinteza zilnică pe email"} <= admin, \
        sorted({"Panoul de capacitate", "Contabilii și asistenții cabinetului", "Blocare perioade", "Sinteza zilnică pe email"} - admin)


# ── 222 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def firma_bilant():
    """Firmă nouă cu datele cerute de ANAF completate în Date firmă și luna preluării 01/2024 (evidența în iConta.eu de la 01.01.2024):
    bilanțul 2025 se poate întocmi, iar „An precedent” vine din evidența întregului 2024 (deficiența 221, decizia Costin 11.10.2026 —
    fără anul precedent în aplicație coloana s-ar cere manual, iar 222 nu e despre ea)."""
    gen = firma_noua()
    f = next(gen)
    _date_firma(f)
    st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"luna_preluare": "2024-01"})
    assert st == 200 and r.get("ok") is not False, (st, r)
    yield f
    try:
        next(gen)
    except StopIteration:
        pass


_ACTIUNI_BILANT = "() => ['#bl-val', '#bl-xml', '#bl-coada'].map((s) => { const b = document.querySelector('.fereastra:last-of-type ' + s); " \
                  "const c = getComputedStyle(b); return {id: s, inactiv: b.disabled, aspect: c.opacity + ' ' + c.backgroundColor}; })"


def test_def_222_bilantul_fara_tip_nu_trimite_si_confirma_ca_declaratiile(patron, firma_bilant):
    """222. „Trimite în coadă” e activ fără tip de declarație ales; mesajul de confirmare apare ca o casetă brută „ok”.
    Pașii contabilului: firma -> Bilanț anual: tipul e „— alege —”, iar „Validează (ANAF)”, „Descarcă XML” și „Trimite în coadă →”
    sunt inactive și ARATĂ inactive -> anul 2025, S1005: toate trei devin active (și arată altfel) -> „Validează (ANAF)”: „Validare
    fără erori”, fără caseta brută „ok” dedesubt (ieșirea validatorului trimisă ca „erori”) -> „Trimite în coadă →”:
    confirmarea e caseta „Trimisă în coada de validare” a declarațiilor, cu bilanțul și anul — nu un rând de text — iar în coada
    cabinetului apare S1005 2025 al firmei."""
    pg = patron.pg
    patron.firma(firma_bilant["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    pg.wait_for_selector(".fereastra:last-of-type #bl-coada", timeout=20000)
    assert pg.input_value(".fereastra:last-of-type #bl-tip") == ""
    pg.wait_for_timeout(400)
    inainte = pg.evaluate(_ACTIUNI_BILANT)
    patron.captura("fara_tip")
    assert all(b["inactiv"] for b in inainte), inainte
    pg.fill(".fereastra:last-of-type #bl-an", "2025")
    pg.dispatch_event(".fereastra:last-of-type #bl-an", "change")
    pg.wait_for_function("() => { const z = document.querySelector('.fereastra:last-of-type #bl-categorie'); return z && "
                         "!z.hasAttribute('aria-busy') && z.innerText.trim() !== '' && !z.innerText.includes('Se calculează'); }", timeout=90000)
    pg.select_option(".fereastra:last-of-type #bl-tip", "s1005")
    pg.wait_for_timeout(400)                                                       # tranziția fundalului (0,15 s) s-a încheiat
    dupa = pg.evaluate(_ACTIUNI_BILANT)
    assert not any(b["inactiv"] for b in dupa), dupa
    assert all(a["aspect"] != d["aspect"] for a, d in zip(inainte, dupa)), (inainte, dupa)   # inactivul se vede, nu doar e
    pg.click(".fereastra:last-of-type #bl-val")                                  # „Validează”: verdictul, fără caseta brută „ok”
    pg.wait_for_function("() => /Validare fără erori|Erori la validare/.test(document.querySelector('.fereastra:last-of-type #bl-rez').innerText)",
                         timeout=120000)
    rez = pg.evaluate("() => [...document.querySelectorAll('.fereastra:last-of-type #bl-rez pre')].map((p) => p.innerText.trim())")
    patron.captura("validat")
    assert "Validare fără erori" in pg.inner_text(".fereastra:last-of-type #bl-rez") and rez == [], rez
    pg.click(".fereastra:last-of-type #bl-coada")
    pg.wait_for_selector(".fereastra:last-of-type #bl-coada-mesaj .dec-gata, .fereastra:last-of-type #coada-confirmare", timeout=120000)
    if pg.locator(".fereastra:last-of-type #coada-confirmare").count():           # atenționări DUK: confirmarea scrisă, apoi trimiterea
        patron.captura("atentionari")
        pg.fill(".fereastra:last-of-type #coada-confirmare", "Bilanț de probă D222: atenționările sunt cunoscute.")
        pg.click(".fereastra:last-of-type #coada-confirma")
    pg.wait_for_selector(".fereastra:last-of-type #bl-coada-mesaj .dec-gata", timeout=120000)
    zona = pg.inner_text(".fereastra:last-of-type #bl-coada-mesaj")
    patron.captura("trimis")
    assert "Trimisă în coada de validare" in zona and "S1005" in zona and "2025" in zona, zona
    assert pg.locator(".fereastra:last-of-type #bl-coada-mesaj #coada-confirmare").count() == 0, zona   # caseta atenționărilor a plecat
    r = sql("SELECT tip, payload->>'_an' FROM public.declaratii_coada WHERE tenant_id = %s", (firma_bilant["tenant_id"],))
    assert r == [("s1005", "2025")], r                         # `perioada` e scadența (02.06.2026); anul = `_an` (perioada_din_payload)


# ── 221 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _solduri(f, data_referinta):
    """Soldurile de preluare, pe ruta aplicației (Migrare -> Solduri inițiale): bancă 10.000 = capital 10.000, la data lor."""
    st, r = _api(PATRON, "POST", "/tenants/%d/solduri" % f["tenant_id"],
                 {"data_referinta": data_referinta, "randuri": [{"cont": "5121", "denumire": "Conturi la bănci în lei", "debit": 10000},
                                                                {"cont": "1012", "denumire": "Capital subscris vărsat", "credit": 10000}]})
    assert st == 200 and r.get("ok") is not False, (st, r)


def _alege_bilant(ecran, an):
    pg = ecran.pg
    pg.fill(".fereastra:last-of-type #bl-an", str(an))
    pg.dispatch_event(".fereastra:last-of-type #bl-an", "change")
    pg.wait_for_function("() => { const z = document.querySelector('.fereastra:last-of-type #bl-categorie'); return z && "
                         "!z.hasAttribute('aria-busy') && !z.innerText.includes('Se calculează'); }", timeout=90000)
    pg.select_option(".fereastra:last-of-type #bl-tip", "s1005")
    pg.wait_for_function("(an) => { const z = document.querySelector('.fereastra:last-of-type #bl-precedent'); "
                         "return z && z.dataset.pentru === an + '|s1005' && z.innerText.trim(); }", arg=str(an), timeout=60000)
    return pg.inner_text(".fereastra:last-of-type #bl-precedent")


def _valideaza_bilant(ecran, an, alege=True):
    pg = ecran.pg
    if alege:
        _alege_bilant(ecran, an)
    pg.click(".fereastra:last-of-type #bl-val")
    pg.wait_for_function("() => { const r = document.querySelector('.fereastra:last-of-type #bl-rez'); return r && r.innerText.trim() "
                         "&& !r.innerText.includes('Se validează'); }", timeout=120000)
    randuri = pg.evaluate("""() => [...document.querySelectorAll('.fereastra:last-of-type #bl-randuri tbody tr')].map(tr =>
      [...tr.querySelectorAll('td')].map(td => td.innerText.trim()))""")
    # „rândul 08” / „rândul 06a (301)” (codul formularului, 234): numărul rândului e cel din paranteză, altfel codul
    nr = lambda r: int(r.split("(")[-1].rstrip(")")) if "(" in r else int(r.split()[-1])   # noqa: E731
    return pg.inner_text(".fereastra:last-of-type #bl-rez"), {(f, nr(r)): (p, c) for f, r, _den, p, c in randuri}


def test_def_221_an_precedent_e_soldul_anului_precedent(patron, firma_e2e):
    """221. Bilanț: coloana „An precedent” e copiată din anul curent (grav, cifre greșite în declarație).
    [Decizia Costin 11.10.2026] „coloana «An precedent» din bilanț se completează din bilanțul anului anterior, dacă firma îl are în
    aplicație. Dacă nu îl are, se completează manual, cu avertisment vizibil. Bilanțul nu poate fi generat cu coloana goală.”
    Pașii contabilului: firma cu soldurile de preluare la 31.12.2024 (bancă 10.000) și un aport validat în 03/2025 (+2.000) -> Bilanț
    anual 2025, S1005: ecranul spune că F10 vine din evidența pe 2024 și cere, cu avertisment, F20 (anul 2024 nu e în aplicație) ->
    „Validează” e inactiv fără F20 (228: motivul lângă el) -> completează F20 (zero pe toate rândurile) și salvează: avertismentul
    rămâne, „completată manual” -> „Validează”: rândul băncilor „An precedent” 10.000, „An curent” 12.000, validare fără erori, cu
    avertismentul în rezultat -> Bilanț 2026: „An precedent” vine din bilanțul pe 2025 validat în aplicație (12.000 pe rândul băncilor), fără
    formular manual -> 2024: acțiunile inactive, coloana „An precedent” goală (2023 nu e în aplicație) -> 2023: acțiunile inactive, cu
    motivul „nu se poate întocmi” (soldurile de la 31.12.2023 sunt dinaintea preluării).
    MUTAȚIILE din plasă: refuzul coloanei goale scos; bilanțul anului precedent ignorat."""
    f = firma_e2e
    pg = patron.pg
    _date_firma(f)
    _solduri(f, "2024-12-31")
    _nota_validata(f, "2025-03-10", "5121", "1012", 2000, "Aport capital D221")
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    zona = _alege_bilant(patron, 2025)
    patron.captura("an_precedent_de_completat")
    assert "F10: evidența pe 2024 din aplicație" in zona, zona
    assert pg.locator(".fereastra:last-of-type #bl-precedent .caseta-atentie").is_visible(), zona
    assert "goală (F20)" in zona and pg.locator(".fereastra:last-of-type .bl-prec-tabel").count() == 1, zona
    assert pg.locator(".fereastra:last-of-type #bl-val").is_disabled(), "„Validează” activ cu coloana „An precedent” goală"   # 228
    assert "(F20)" in pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv"), pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv")
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")                  # câmpurile goale = 0 lei, pe toate rândurile F20
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #bl-prec-mesaj') || {}).innerText === "
                         "'Coloana „An precedent” a fost salvată.'", timeout=60000)
    zona = pg.inner_text(".fereastra:last-of-type #bl-precedent")
    patron.captura("completata_manual")
    assert "completată manual de" in zona and pg.locator(".fereastra:last-of-type #bl-precedent .caseta-atentie").is_visible(), zona
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura("an_precedent_din_evidenta")
    assert "Validare fără erori" in text, text[:800]
    assert "completată manual" in text, text[:800]                          # avertismentul ajunge și în rezultatul validării
    assert rand.get(("F10", 8)) == ("10.000,00", "12.000,00"), (rand, text[:600])   # rd.08 „Casa și conturi la bănci”
    assert any(p != c for p, c in rand.values()), rand          # anti-copie: nu toate rândurile au coloanele egale
    zona = _alege_bilant(patron, 2026)
    patron.captura("an_precedent_din_bilantul_2025")
    assert "F10: bilanțul pe 2025 validat în aplicație; F20: bilanțul pe 2025 validat în aplicație" in zona, zona
    assert pg.locator(".fereastra:last-of-type .bl-prec-tabel").count() == 0, zona
    text, rand = _valideaza_bilant(patron, 2026, alege=False)
    assert rand.get(("F10", 8), ("?", "?"))[0] == "12.000,00", (rand, text[:600])
    zona = _alege_bilant(patron, 2024)
    patron.captura("an_preluarii_fara_precedent")
    motiv = pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv")
    assert pg.locator(".fereastra:last-of-type #bl-val").is_disabled() and "(F10, F20)" in motiv, (motiv, zona[:300])   # 2023 nu e în aplicație
    pg.fill(".fereastra:last-of-type #bl-an", "2023")
    pg.dispatch_event(".fereastra:last-of-type #bl-an", "change")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #bl-actiuni-motiv') || {}).innerText.includes('nu se poate întocmi')",
                         timeout=60000)
    patron.captura("an_dinaintea_preluarii")
    motiv = pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv")
    assert pg.locator(".fereastra:last-of-type #bl-val").is_disabled() and "31.12.2024" in motiv, motiv


# ── C8 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#: butoanele barelor aplicației (bara de sus, bara de stare, a treia bară), vizibile, cu ținta lor: atingerea din mijlocul fiecăruia
#: ajunge la el, nu la un vecin care s-a revărsat peste el
_BUTOANE_BARE = """() => [...document.querySelectorAll('.bara-antet button, .bara-antet a[href], .subbara button, .bara3 button')]
  .filter((b) => b.offsetParent !== null).map((b) => { const r = b.getBoundingClientRect();
    const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return {buton: b.id || b.className, lovit: e ? (e.id || e.className) : null, ok: !!e && (e === b || b.contains(e))}; })"""


def test_def_c8_pe_telefon_bara_de_stare_nu_acopera_butoanele(patron):
    """C8. Pe telefon (393 px), mesajul lung din bara de stare („Poți activa validarea în doi (patru ochi) … Activează · Nu acum”) se
    rupea pe mai multe rânduri, ieșea din bara de înălțime fixă și acoperea bara de sus: atingerea pe „?” (prezentarea aplicației)
    ajungea la mesaj, deci prezentarea nu se putea deschide. Găsită de uneltele vizuale ale lotului 220–225 (navigarea la prezentare,
    pe profilul de telefon: „#edu-4ochi … intercepts pointer events”).
    Pașii contabilului: telefon -> pagina principală, cu mesajul despre validarea în doi -> fiecare buton din bare se poate atinge
    (atingerea ajunge la el) -> „?” deschide prezentarea."""
    pg = patron.pg
    pg.set_viewport_size({"width": 393, "height": 851})
    try:
        patron.acasa()
        pg.wait_for_selector("#edu-4ochi", timeout=20000)                       # anti-vacuu: mesajul lung e pe bară
        butoane = pg.evaluate(_BUTOANE_BARE)
        patron.captura("telefon")
        assert len(butoane) >= 4 and any(b["buton"] == "nav-ghid" for b in butoane), butoane
        assert [b for b in butoane if not b["ok"]] == [], butoane
        pg.click("#nav-ghid", timeout=8000)
        pg.wait_for_selector(".fereastra .ans-continut", timeout=15000)
    finally:
        pg.set_viewport_size({"width": 1700, "height": 1000})


# ── C9 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c9_pagina_principala_are_titlul_ei(browser, request, patron):
    """C9. Pagina principală (contabilul-șef și asistentul) n-avea niciun titlu de nivel 1: salutul „Salut, …” era un `div`, deci un
    cititor de ecran n-avea de unde ști ce pagină e (axe `page-has-heading-one`). Găsită de uneltele vizuale ale lotului 220–225, când
    pagina principală a intrat în lista ecranelor scanate.
    Pașii: contabilul-șef -> pagina principală: un singur titlu de nivel 1, salutul -> asistentul: la fel."""
    patron.acasa()
    h1 = patron.pg.eval_on_selector_all("h1", "els => els.filter(e => e.offsetParent !== null).map(e => e.innerText.trim())")
    patron.captura("cabinet")
    assert len(h1) == 1 and h1[0].startswith("Salut, "), h1
    with cont_asistent(firme=(4838,)) as a, ecran_cont(browser, request, a["email"]) as e:
        e.acasa()
        h1a = e.pg.eval_on_selector_all("h1", "els => els.filter(x => x.offsetParent !== null).map(x => x.innerText.trim())")
        e.captura("asistent")
        assert len(h1a) == 1 and h1a[0].startswith("Salut, "), h1a
