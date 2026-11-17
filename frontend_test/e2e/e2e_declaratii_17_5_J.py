# -*- coding: utf-8 -*-
"""DECLARAȚIILE ȘI CERTIFICATUL CM CU DATELE DIN APLICAȚIE — lotul 17.5-J (rândurile AC052, AC053, AC103, AC109, AC129, AC130, AC134, AC135, AC137, AC139, AC141 din
auditul complet; decizii_17_5_J.txt și «De ce» din comanda_17_5_J.txt). Scris de arhitect; Code nu îl modifică.

La 1366×768, ceas înghețat 03.11.2026, cu contul administratorului (dovada.71507), pe F1 Comert Stoc (micro), F3 Intracomunitar, F5 SRL Salariati și F6 Migrare Test (profit):
  1. AC052: Registrul de evidență fiscală F6 pe 2025 spune cauza refuzului (evidența începe după 30.09.2026, rulajele anului lipsesc) și are butonul «Deschide Import date»; selectorul anului rămâne;
  2. AC053: Registrul F1 (micro) are deasupra nota «Firma e pe impozitul pe veniturile microîntreprinderilor …», varianta pornită rămâne «profit»; la F6 (profit) nota nu apare;
  3. AC135: în lista «Tip declarație» a lui F1 rândul D177 poartă motivul (art. 56 alin. (2^5)) și nu se poate alege;
  4. AC103: alegerea oricărui rând de perioadă din listă (D112, D300, D394, D406, înainte de preluare) pune în An/Lună/Trimestru perioada RÂNDULUI ales (martor: «D300 · 10/2026» → octombrie);
  5. AC129: intrarea prin căutarea globală («D104») propune T3 (iul-sep), nu trimestrul în curs; perioada aleasă de contabil rămâne la întoarcerea din pasul 2;
  6. AC134: D114 pasul 2 (F1): CIF declarant 401002001, denumirea și adresa precompletate;
  7. AC137: D398 «de lămurit» are butonul «Deschide Date firmă», «Continuă →» rămâne activ;
  8. AC130: D104 pasul 2 (F1) are deasupra formularului declarantului nota asociatului desemnat;
  9. AC139 + AC141: D301 pasul 2 (F3, 06/2026) nu mai spune «nu automat din facturi» (facturile IC ale lunii au operațiune legată); câmpul Valută: EUR primul și preselectat, apoi RON, apoi restul
     în ordine alfabetică, 130 px lățime, pe un singur rând;
 10. AC109: Certificat nou (F5, Ionescu Vasile): Data început 19.10.2026 → «Propus din statele de plată: 30.000,00 lei brut, 127 de zile lucrătoare (aprilie–septembrie 2026). Poți modifica.», câmpurile
     bazei precompletate (127 de zile), editabile, o singură dată propoziția; Data început 20.01.2026 (angajat 05.01.2026) → «Nu există state de plată pentru cele 6 luni; introdu baza de mână.», câmpuri goale;
     la «Calculează și salvează» cererea poartă defalcarea lunară (venituri_lunare, 6 luni aprilie–septembrie 2026, 30.000 lei și 127 de zile) — cererea e oprită în browser, nimic nu se salvează.
Nu salvează nimic; nu alege niciun fișier. Un singur test."""
import importlib.util
import json
import os
import re
import sys

from conftest import BAZA, alege_perioada, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
F3 = "F3 Intracomunitar"
F5 = "F5 SRL Salariati"
F6 = "F6 Migrare Test"
TOP = ".fereastra-overlay:not(.fundal) "
FER = TOP + ".fereastra"
NOTA_MICRO = "Firma e pe impozitul pe veniturile microîntreprinderilor (Regimul fiscal din Date firmă); registrul de mai jos calculează rezultatul fiscal pentru impozitul pe profit."
TEXT_D177 = ("D177 nu se datorează — Regimul fiscal declară firma pe micro, iar D177 e redirecționarea impozitului pe profit (redirecționarea de la micro e abrogată din 2024, "
             "art. 56 alin. (2^5)). Dacă firma a ieșit din regimul micro, corectează Regimul fiscal la Date firmă.")
NOTA_D104 = "D104 se depune de asociatul desemnat al unei asocieri fără personalitate juridică, în numele asocierii. Completează numai dacă firma are această calitate."
PROPOZITIE_CM = "Propus din statele de plată: 30.000,00 lei brut, 127 de zile lucrătoare (aprilie–septembrie 2026). Poți modifica."
FARA_STATE_CM = "Nu există state de plată pentru cele 6 luni; introdu baza de mână."
AVERT_VECHI = "nu automat din facturi"
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""
# rândurile de perioadă ale listei «Tip declarație» (nu cele din «Alte declarații», care n-au perioadă în nume): textul întreg al fiecărui rând activ
JS_RANDURI_PERIOADA = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) li.ds-lista-rand:not(.ds-lista-inactiv) .ds-lista-nume')].map((e) => (e.textContent || '').trim())"""
# perioada afișată în pasul 1: anul, luna (valoarea și textul opțiunii alese), trimestrul (valoarea și textul)
JS_PERIOADA = """() => {
  const q = (s) => document.querySelector('.fereastra-overlay:not(.fundal) ' + s);
  const an = q('#dec-an'), luna = q('#dec-luna'), trim = q('#dec-trim');
  const ales = (s) => (s && s.selectedOptions && s.selectedOptions[0]) ? s.selectedOptions[0] : null;
  return { an: an ? an.value : null, luna: luna ? luna.value : null, luna_text: ales(luna) ? ales(luna).textContent.trim() : null,
           trim: trim ? trim.value : null, trim_text: ales(trim) ? ales(trim).textContent.trim() : null };
}"""
# câmpul Valută din D301: lista de valori, valoarea aleasă, lățimea și înălțimea etichetei lui față de cea a câmpului «Nr. document», depășirea orizontală a controlului vizibil
JS_VALUTA = """() => {
  const q = (s) => document.querySelector('.fereastra-overlay:not(.fundal) ' + s);
  const v = q('#d301-valuta'), n = q('#d301-nrdoc'); if (!v || !n) return null;
  const eV = v.closest('label'), eN = n.closest('label');
  const optiuni = [...v.options].map((o) => o.value).filter((x) => x !== '');
  const vizibil = eV.querySelector('.ds-lista-titlu') || v;
  return { optiuni, valoare: v.value, latime: Math.round(eV.getBoundingClientRect().width * 10) / 10, inaltime: Math.round(eV.getBoundingClientRect().height * 10) / 10,
           inaltime_nrdoc: Math.round(eN.getBoundingClientRect().height * 10) / 10, depasire: vizibil.scrollWidth > vizibil.clientWidth + 1 };
}"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _norm(t):
    return " ".join((t or "").split())


def _text(pg, sel=FER):
    loc = pg.locator(sel)
    return _norm(loc.first.inner_text()) if loc.count() else ""


def _text_brut(pg):
    """textContent al ferestrei de sus (inclusiv ce stă în elemente ascunse sau pliate): așa măsoară oracolul pasi_17_5_J cheia dom:…|text."""
    return pg.evaluate("() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); return e ? (e.textContent || '').replace(/\\s+/g, ' ').trim() : ''; }")


def _card(pg, parcurs, firma, sel, asteapta=None):
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return False
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector(TOP + "#fa-facturi", state="detached", timeout=20000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2000)
    return True


def _declaratii(pg, parcurs, firma):
    """Fereastra Declarații, pasul 1, a firmei `firma`."""
    return _card(pg, parcurs, firma, "#fa-declaratii", "#dec-continua")


def _rand(pg, text, timp=1000):
    """Clic pe primul rând al listei «Tip declarație» al cărui text conține `text`; fals dacă nu există."""
    loc = pg.locator(TOP + "li.ds-lista-rand", has_text=text)
    if not loc.count():
        return False
    try:
        loc.first.click(timeout=10000)
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(timp)
    return True


def _la_pasul_2(pg, asteapta, timp=1800):
    try:
        pg.click(TOP + "#dec-continua", timeout=10000)
        pg.wait_for_selector(TOP + asteapta, state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(timp)
    return True


def _val(pg, sel):
    loc = pg.locator(TOP + sel)
    return loc.first.input_value() if loc.count() else None


def _cere(rele, unde, text, contine=(), lipseste=()):
    for t in contine:
        if t not in text:
            rele.append("%s: lipsește «%s» (text: «%s…»)" % (unde, t, text[:160]))
    for t in lipseste:
        if t in text:
            rele.append("%s: încă apare «%s»" % (unde, t))


def _fisa(pg, parcurs):
    """F5 › Salariați (dacă luna ceasului nu are rânduri, «← luna» de cel mult 3 ori) › rândul lui Ionescu › fișa."""
    _card(pg, parcurs, F5, "#fa-salariati", "#sp-contare")
    for incercare in range(4):
        try:
            pg.wait_for_selector(TOP + "#sp-tabel tbody tr.sp-rand", timeout=12000)
            break
        except Exception:   # noqa: BLE001
            if incercare == 3:
                return False
            try:
                pg.click(TOP + "#sp-prev", timeout=5000)
            except Exception:   # noqa: BLE001
                return False
            pg.wait_for_timeout(1500)
    try:
        randuri = pg.locator(TOP + "#sp-tabel tbody tr.sp-rand")
        rand = randuri.filter(has_text="Ionescu")
        if not rand.count():
            return False
        rand.first.locator(".sp-deschide").click(timeout=10000)
        pg.wait_for_selector(TOP + "#ss-butoane", timeout=30000)
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(1500)
    return True


def _formular_cm(pg, parcurs):
    """Fișa lui Ionescu › Concediu medical › «+ Certificat nou»: formularul gol."""
    if not _fisa(pg, parcurs):
        return False
    try:
        pg.locator(TOP + "#ss-butoane button", has_text="Concediu medical").first.click(timeout=10000)
        pg.wait_for_selector(TOP + "#cm-nou", timeout=20000)
        pg.click(TOP + "#cm-nou", timeout=10000)
        pg.wait_for_selector(TOP + "#cm-calc", state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(1500)
    return True


def _data_inceput_cm(pg, iso):
    pg.fill(TOP + "#cm-inceput", iso, timeout=10000)
    pg.dispatch_event(TOP + "#cm-inceput", "change")


def _asteapta_text(pg, text, timp=12000):
    try:
        pg.wait_for_function("(t) => ((document.querySelector('.fereastra-overlay:not(.fundal) .fereastra') || {textContent: ''}).textContent || '').replace(/\\s+/g, ' ').includes(t)", arg=text, timeout=timp)
        return True
    except Exception:   # noqa: BLE001
        return False


def test_declaratii_17_5_J(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)

        # 1. AC052 — F6 (profit), registrul pe 2025: cauza refuzului + «Deschide Import date»; selectorul anului rămâne
        if _card(pg, parcurs, F6, "#fa-regfiscal", "#rf-an"):
            pg.wait_for_timeout(2500)
            selector_ok = pg.locator("#rf-an").count() > 0   # se măsoară pe fereastra registrului, ÎNAINTE de deschiderea detaliului cardului (ferestrele se înlocuiesc în DOM)
            if "Deschide Import date" not in _text(pg):   # butonul poate sta în cardul de eroare deschis
                try:
                    pg.click(TOP + "#rf-carduri button[data-card='eroare']", timeout=10000)
                    pg.wait_for_timeout(2000)
                except Exception:   # noqa: BLE001
                    pass
            t = _text(pg)
            _cere(rele, "Registru F6 2025", t, contine=["Nu s-a putut întocmi registrul pe 2025", "evidența începe după 30.09.2026", "Deschide Import date"])
            if not selector_ok:
                rele.append("Registru F6 2025: selectorul anului (#rf-an) lipsește")
            butoane = pg.locator(TOP + "button", has_text="Deschide Import date")
            if butoane.count():
                try:
                    butoane.first.click(timeout=10000)
                    pg.wait_for_selector(TOP + "#mig-pasi", timeout=20000)
                except Exception:   # noqa: BLE001
                    rele.append("Registru F6 2025: «Deschide Import date» nu deschide Import date (meniul #mig-pasi)")
        else:
            rele.append("Registru F6: cardul «Registrul de evidență fiscală» nu s-a deschis")

        # 2. AC053 — F1 (micro): nota regimului deasupra registrului; varianta pornită rămâne «profit»; la F6 (profit) nota nu apare
        if _card(pg, parcurs, F6, "#fa-regfiscal", "#rf-an"):
            pg.wait_for_timeout(2500)
            if "Firma e pe impozitul pe veniturile microîntreprinderilor" in _text(pg):
                rele.append("Registru F6 (profit): nota regimului micro apare la o firmă pe profit")
        if _card(pg, parcurs, F1, "#fa-regfiscal", "#rf-an"):
            pg.wait_for_timeout(2500)
            t = _text(pg)
            _cere(rele, "Registru F1 (micro)", t, contine=[NOTA_MICRO, "Impozit pe profit · art. 19 alin. (7)"])
            if t.find(NOTA_MICRO) >= 0 and t.find("Varianta") >= 0 and t.find(NOTA_MICRO) > t.find("Categoria cerută de normă") >= 0:
                rele.append("Registru F1 (micro): nota stă sub registru, așteptat deasupra lui")
            if _val(pg, "#rf-var") != "profit":
                rele.append("Registru F1 (micro): varianta pornită nu mai e «profit» (#rf-var = %r)" % _val(pg, "#rf-var"))
        else:
            rele.append("Registru F1: cardul «Registrul de evidență fiscală» nu s-a deschis")

        # 3. AC135 — F1 (micro): rândul D177 din lista «Tip declarație» poartă motivul și nu se poate alege
        if _declaratii(pg, parcurs, F1):
            if _rand(pg, "D177", 1200):
                _cere(rele, "Lista «Tip declarație» F1, rândul D177", _text(pg), contine=[TEXT_D177])
                if pg.eval_on_selector(TOP + "#dec-tip", "s => s.value") != "":
                    rele.append("Lista «Tip declarație» F1: D177 s-a putut alege (#dec-tip = %r)" % pg.eval_on_selector(TOP + "#dec-tip", "s => s.value"))
                if not pg.locator(TOP + "#dec-continua").is_disabled():
                    rele.append("Lista «Tip declarație» F1: «Continuă →» e activ după atingerea rândului D177")
            else:
                rele.append("Lista «Tip declarație» F1: rândul D177 lipsește din listă")
            # 4. AC103 — fiecare rând de perioadă pune în An/Lună/Trimestru perioada RÂNDULUI ales
            _declaratii(pg, parcurs, F1)
            nume = pg.evaluate(JS_RANDURI_PERIOADA)
            verificate = 0
            for n in nume:
                m = re.match(r"^(D\d+) · (?:T(\d)/(\d{4})|(\d{2})/(\d{4})|(\d{4}))(?!\d)", n)
                if not m:
                    continue
                loc = pg.locator(TOP + "li.ds-lista-rand:not(.ds-lista-inactiv)", has_text=n)
                if not loc.count():
                    rele.append("Perioade F1: rândul «%s» nu mai e în listă după o alegere anterioară" % n)
                    continue
                try:
                    loc.first.click(timeout=10000)
                except Exception:   # noqa: BLE001
                    rele.append("Perioade F1: rândul «%s» nu se poate apăsa" % n)
                    continue
                pg.wait_for_timeout(700)
                p = pg.evaluate(JS_PERIOADA)
                tip = m.group(1)
                if m.group(2):          # trimestru: T<n>/<an>
                    ok = p["trim"] == m.group(2) and p["an"] == m.group(3)
                    asteptat = "T%s/%s" % (m.group(2), m.group(3))
                elif m.group(4):        # lună: LL/AAAA
                    ok = p["luna"] == str(int(m.group(4))) and p["an"] == m.group(5)
                    asteptat = "%s/%s" % (m.group(4), m.group(5))
                else:                   # an
                    ok = p["an"] == m.group(6)
                    asteptat = m.group(6)
                verificate += 1
                if not ok:
                    rele.append("Perioade F1: rândul «%s %s» a pus în perioadă %s (așteptat %s)" % (tip, asteptat, p, asteptat))
            if verificate < 2:
                rele.append("Perioade F1: sub 2 rânduri de perioadă verificate (%d din %d rânduri): martorul «D300 · 10/2026» lipsește" % (verificate, len(nume)))
            # martorul: «D300 · 10/2026» → octombrie
            _declaratii(pg, parcurs, F1)
            if _rand(pg, "D300 · 10/2026", 1200):
                p = pg.evaluate(JS_PERIOADA)
                if p["luna_text"] != "octombrie" or p["an"] != "2026":
                    rele.append("D300 · 10/2026: perioada după clic e %s (așteptat octombrie 2026)" % p)
            else:
                rele.append("D300 · 10/2026: rândul lipsește din lista «Tip declarație» a lui F1")
        else:
            rele.append("Declarații F1: pasul 1 nu s-a deschis (D177 și perioadele nevizitate)")

        # 5. AC129 — F1, căutarea globală «D104»: perioada propusă T3 (iul-sep); perioada aleasă de contabil rămâne la întoarcerea din pasul 2
        parcurs.firma(pg, F1)
        try:
            pg.fill(TOP + "#cautare-fereastra", "D104", timeout=10000)
            pg.wait_for_selector(TOP + "#cautare-fereastra-rez .cautare-item", timeout=15000)
            pg.locator(TOP + "#cautare-fereastra-rez .cautare-item", has_text="D104 —").first.click(timeout=10000)
            pg.wait_for_selector(TOP + "#dec-trim", state="attached", timeout=30000)
        except Exception:   # noqa: BLE001
            rele.append("Căutare «D104» F1: Declarațiile nu s-au deschis cu D104 ales (#dec-trim lipsește)")
        pg.wait_for_timeout(1500)
        p = pg.evaluate(JS_PERIOADA)
        if p["trim_text"] != "T3 (iul-sep)":
            rele.append("Căutare «D104» F1: trimestrul propus e %r (așteptat «T3 (iul-sep)»)" % p["trim_text"])
        if pg.locator(TOP + "#dec-trim").count():
            alege_perioada(pg, 2026, trim=2, zona=TOP)   # contabilul alege T2/2026
            if _la_pasul_2(pg, "#d104-dnume"):
                try:
                    pg.click(TOP + ".nav-inapoi", timeout=10000)
                    pg.wait_for_selector(TOP + "#dec-trim", state="attached", timeout=20000)
                except Exception:   # noqa: BLE001
                    rele.append("Căutare «D104» F1: întoarcerea din pasul 2 (←) nu a readus pasul 1")
                pg.wait_for_timeout(1000)
                p = pg.evaluate(JS_PERIOADA)
                if p["trim"] != "2" or p["an"] != "2026":
                    rele.append("Căutare «D104» F1: după întoarcerea din pasul 2 perioada e %s (aleasă de contabil: T2/2026)" % p)
            else:
                rele.append("Căutare «D104» F1: pasul 2 al D104 nu s-a deschis")

        # 6. AC134 — F1, D114 pasul 2: CIF declarant, denumire și adresă precompletate
        if _declaratii(pg, parcurs, F1) and _rand(pg, "D114") and _la_pasul_2(pg, "#d114-cif"):
            if _val(pg, "#d114-cif") != "401002001":
                rele.append("D114 pasul 2 F1: «CIF declarant» = %r (așteptat «401002001»)" % _val(pg, "#d114-cif"))
            for camp, nume_camp in (("#d114-den", "Denumire"), ("#d114-adr", "Adresă")):
                if not (_val(pg, camp) or "").strip():
                    rele.append("D114 pasul 2 F1: «%s» (%s) gol la deschidere (așteptat precompletat din Date firmă)" % (nume_camp, camp))
        else:
            rele.append("D114 pasul 2 F1: formularul (#d114-cif) nu s-a deschis")

        # 7. AC137 — F1, D398 «de lămurit»: butonul «Deschide Date firmă», «Continuă →» rămâne activ
        if _declaratii(pg, parcurs, F1) and _rand(pg, "D398", 1200):
            if pg.eval_on_selector(TOP + "#dec-tip", "s => s.value") != "d398":
                rele.append("D398 F1: nu s-a ales (#dec-tip = %r)" % pg.eval_on_selector(TOP + "#dec-tip", "s => s.value"))
            buton = pg.locator(TOP + "button", has_text="Deschide Date firmă")
            if not buton.count():
                rele.append("D398 F1: butonul «Deschide Date firmă» lipsește sub listă")
            else:
                if not buton.first.is_visible():
                    rele.append("D398 F1: butonul «Deschide Date firmă» nu e vizibil")
                if not pg.locator(TOP + "#dec-continua").is_enabled():
                    rele.append("D398 F1: «Continuă →» e blocat (D398 «de lămurit» trebuie să rămână selectabilă)")
                try:
                    buton.first.click(timeout=10000)
                    pg.wait_for_function("() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-antet .fir-acum'); return !!e && e.textContent.includes('Date firmă'); }", timeout=20000)
                except Exception:   # noqa: BLE001
                    rele.append("D398 F1: «Deschide Date firmă» nu deschide fereastra Date firmă")
        else:
            rele.append("D398 F1: Declarațiile sau rândul D398 nu s-au deschis")

        # 8. AC130 — F1, D104 pasul 2: nota deasupra formularului declarantului
        if _declaratii(pg, parcurs, F1) and _rand(pg, "D104") and _la_pasul_2(pg, "#d104-dnume"):
            t = _text(pg)
            _cere(rele, "D104 pasul 2 F1", t, contine=[NOTA_D104, "Declarantul (reprezentantul asocierii)"])
            if NOTA_D104 in t and "Declarantul (reprezentantul asocierii)" in t and t.index(NOTA_D104) > t.index("Declarantul (reprezentantul asocierii)"):
                rele.append("D104 pasul 2 F1: nota stă sub formularul declarantului, așteptat deasupra lui")
        else:
            rele.append("D104 pasul 2 F1: formularul (#d104-dnume) nu s-a deschis")

        # 9. AC139 + AC141 — F3, D301 pasul 2 pe 06/2026
        if _declaratii(pg, parcurs, F3) and _rand(pg, "D301"):
            alege_perioada(pg, 2026, 6, zona=TOP)
            pg.wait_for_timeout(600)
            if _la_pasul_2(pg, "#d301-regen", 2500):
                _cere(rele, "D301 pasul 2 F3 (06/2026)", _text_brut(pg), lipseste=[AVERT_VECHI])
                v = pg.evaluate(JS_VALUTA)
                if not v:
                    rele.append("D301 pasul 2 F3: câmpul Valută (#d301-valuta) sau «Nr. document» lipsește")
                else:
                    if v["valoare"] != "EUR":
                        rele.append("D301 pasul 2 F3: Valută preselectată = %r (așteptat «EUR»)" % v["valoare"])
                    opt = v["optiuni"]
                    rest = sorted(x for x in opt if x not in ("EUR", "RON"))
                    if opt[:2] != ["EUR", "RON"] or opt[2:] != rest or "EUR" not in opt or "RON" not in opt:
                        rele.append("D301 pasul 2 F3: lista valutelor începe cu %s (așteptat EUR, RON, apoi alfabetic)" % opt[:4])
                    if abs(v["latime"] - 130) > 1:
                        rele.append("D301 pasul 2 F3: câmpul Valută are lățimea %s px (așteptat 130)" % v["latime"])
                    if abs(v["inaltime"] - v["inaltime_nrdoc"]) > 2:
                        rele.append("D301 pasul 2 F3: câmpul Valută are înălțimea %s px, «Nr. document» are %s px (textul se rupe pe mai multe rânduri)" % (v["inaltime"], v["inaltime_nrdoc"]))
                    if v["depasire"]:
                        rele.append("D301 pasul 2 F3: textul câmpului Valută depășește lățimea controlului")
            else:
                rele.append("D301 pasul 2 F3: pasul 2 (#d301-regen) nu s-a deschis")
        else:
            rele.append("D301 F3: Declarațiile sau rândul D301 nu s-au deschis")

        # 10. AC109 — F5, Ionescu: Certificat nou
        if _formular_cm(pg, parcurs):
            # fără state de plată în cele 6 luni: Data început 20.01.2026 (angajat 05.01.2026) → luni iulie–decembrie 2025
            _data_inceput_cm(pg, "2026-01-20")
            if not _asteapta_text(pg, FARA_STATE_CM):
                rele.append("Certificat nou, Data început 20.01.2026: «%s» lipsește" % FARA_STATE_CM)
            if _val(pg, "#cm-ven6") != "" or _val(pg, "#cm-zile6") != "":
                rele.append("Certificat nou, Data început 20.01.2026: câmpurile bazei nu sunt goale (#cm-ven6 = %r, #cm-zile6 = %r)" % (_val(pg, "#cm-ven6"), _val(pg, "#cm-zile6")))
            # martorul: Data început 19.10.2026 → 30.000,00 lei brut, 127 de zile lucrătoare (aprilie–septembrie 2026)
            _data_inceput_cm(pg, "2026-10-19")
            if not _asteapta_text(pg, PROPOZITIE_CM):
                rele.append("Certificat nou, Data început 19.10.2026: propoziția «%s» lipsește (text: «%s…»)" % (PROPOZITIE_CM, _text(pg, FER + " .fereastra-corp")[-200:]))
            pg.wait_for_timeout(800)
            t = _text(pg)
            if t.count("Propus din statele de plată") != 1:
                rele.append("Certificat nou: propoziția «Propus din statele de plată» apare de %d ori (așteptat o dată)" % t.count("Propus din statele de plată"))
            if _val(pg, "#cm-zile6") != "127":
                rele.append("Certificat nou: #cm-zile6 = %r (așteptat «127»)" % _val(pg, "#cm-zile6"))
            ven = (_val(pg, "#cm-ven6") or "").strip()
            if ven not in ("30000", "30000.00", "30000,00", "30.000,00", "30.000"):
                rele.append("Certificat nou: #cm-ven6 = %r (așteptat 30.000 lei, în forma pe care o citește sumaRo)" % ven)
            for camp in ("#cm-ven6", "#cm-zile6"):
                if not pg.locator(TOP + camp).first.is_editable():
                    rele.append("Certificat nou: %s nu mai e editabil" % camp)
            # cererea poartă defalcarea lunară; se oprește în browser (nimic nu se salvează)
            capturat = []

            def _opreste(ruta, cerere):
                if cerere.method == "POST":
                    capturat.append(cerere.post_data or "")
                    ruta.abort()
                else:
                    ruta.continue_()
            pg.route("**/concedii", _opreste)
            try:
                pg.fill(TOP + "#cm-serie", "AB")
                pg.fill(TOP + "#cm-numar", "1234567")
                pg.select_option(TOP + "#cm-cod", "01")
                pg.fill(TOP + "#cm-acord", "2026-10-19")
                pg.fill(TOP + "#cm-sfarsit", "2026-10-23")
                pg.dispatch_event(TOP + "#cm-sfarsit", "change")
                pg.wait_for_timeout(1500)
                pg.fill(TOP + "#cm-zile", "5")
                for camp in ("cm-continuare", "cm-spital", "cm-program-national"):
                    pg.click(TOP + ".alegere-butoane:has(+ #%s) button[data-valoare='false']" % camp, timeout=10000)
                pg.click(TOP + "#cm-calc", timeout=10000)
                pg.wait_for_timeout(2500)
            except Exception as e:   # noqa: BLE001
                rele.append("Certificat nou: completarea formularului pentru cerere a eșuat (%s)" % type(e).__name__)
            finally:
                pg.unroute("**/concedii")
            if not capturat:
                rele.append("Certificat nou: «Calculează și salvează» n-a trimis nicio cerere POST (nimic de verificat în defalcare)")
            else:
                try:
                    corp = json.loads(capturat[0])
                    luni = corp.get("venituri_lunare")
                    if not isinstance(luni, list) or len(luni) != 6:
                        rele.append("Certificat nou: cererea nu poartă defalcarea lunară «venituri_lunare» cu 6 luni (găsit %r)" % (luni,))
                    else:
                        suma = round(sum(float(e[0]) for e in luni), 2)
                        zile = sum(int(e[1]) for e in luni)
                        luna_iso = [str(e[2])[:7] for e in luni]
                        if suma != 30000 or zile != 127 or luna_iso != ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]:
                            rele.append("Certificat nou: defalcarea lunară are suma %s, %s zile, lunile %s (așteptat 30000, 127, 2026-04…2026-09)" % (suma, zile, luna_iso))
                except (ValueError, TypeError, IndexError, KeyError) as e:
                    rele.append("Certificat nou: cererea oprită nu s-a putut citi (%s: %s)" % (type(e).__name__, e))
        else:
            rele.append("Certificat nou F5 (Ionescu): formularul nu s-a deschis")
    finally:
        b.close()
    assert not rele, "declarațiile și certificatul CM 17.5-J: %s" % "; ".join(rele)
