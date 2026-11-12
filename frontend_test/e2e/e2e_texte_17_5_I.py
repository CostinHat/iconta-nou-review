# -*- coding: utf-8 -*-
"""TEXTELE — lotul 17.5-I (rândurile AC013, AC018, AC026, AC029, AC030, AC031, AC032, AC033, AC038, AC042, AC044, AC048, AC054, AC056, AC064, AC066, AC075,
AC078, AC079, AC089, AC100, AC101, AC105, AC112 din auditul complet; decizii_17_5_I.txt). Scris de arhitect; Code nu îl modifică.

La 1366×768, ceas înghețat 03.11.2026, cu contul administratorului (dovada.71507), pe cabinet, pe F1 Comert Stoc și pe F5 SRL Salariati:
  1. acorduri: Sinteza zilei spune «1 sesizare nouă» (nu «1 sesizări noi», nu «de de validat»); în Bancă F1 fiecare număr din cardul semnelor are forma exactă a celor 5 titluri (singular la 1, plural, «de» de la 20; «fără potrivire» fără «de»);
  2. texte care spun ce e pe ecran: Termene numește restanțele; Consolidare spune că luna în curs e cuprinsă («inclusiv (luna în curs»); Registrul-inventar
     începe cu majusculă și nu repetă mesajul registrului gol; Import date spune «balanța de deschidere (fără data de referință): 6 conturi», nu «balanța la —»;
     Istoric facturi spune «Arată încă 10 facturi ale lunii»; Rapoarte comerciale: cardul «Ce nu apare în aceste rapoarte»; Produse: «Temeiul cotei: …»;
  3. un singur limbaj: fără «preview live» (Model factură), fără «landed cost» (NIR nou), «AIC — achiziție intracomunitară» cu linie de pauză (e-Transport),
     «TVA transport 0%: fără TVA …» (în rândul-etichetă), placeholderul «Scrie un mesaj către client…» (U+2026) și aria-label «Mesaj către client», culorile de accent cu nume (aria-label);
  4. numele ferestrei = numele butonului / cardului: «Activitatea echipei», «Tipare de erori», «Bilanț anual», «Solicitări client» (h2), «Salariați» (h2),
     «Datele certificatului» (secțiunea din Certificat nou, nu numele ferestrei repetat);
  5. drepturile în cuvinte: «Nu poate valida» în loc de «· Poate valida»; «Deschide Asistenți» în Capacitate;
  6. motivele barei: Declarații pasul 1 «Completează: Tip declarație»; Leasing «Primire bun»: primele trei câmpuri și «și încă N câmpuri»;
     Leasing «Cod din catalog» 2.3.2.1.1: «în afară de excepțiile înscrise sub acest cod în catalog», nu «în afară de ·»;
  7. numele firmei nu e lipit de text la Import date › Solduri inițiale («F1 Comert Stoc SRL · Încarcă …»).
Nu salvează nimic; nu alege niciun fișier; singurul câmp completat e «Cod din catalog» (GET). Un singur test."""
import importlib.util
import os
import re
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
F5 = "F5 SRL Salariati"
TOP = ".fereastra-overlay:not(.fundal) "
CORP = TOP + ".fereastra .fereastra-corp"
MOTIV = TOP + ".fereastra .fj-motiv"
NUME = TOP + ".fereastra .fereastra-antet .fir-acum"
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _norm(t):
    return " ".join((t or "").split())


def _text(pg, sel=CORP):
    loc = pg.locator(sel)
    return _norm(loc.first.inner_text()) if loc.count() else ""


def _text_brut(pg, sel=CORP):
    """textContent (fără spațiile pe care le pune afișarea): așa se vede un <br> fără spațiu — «SRLÎncarcă»."""
    return pg.evaluate("(s) => { const e = document.querySelector('.fereastra-overlay:not(.fundal) ' + s); return e ? (e.textContent || '').replace(/\\s+/g, ' ').trim() : ''; }", sel.replace(TOP, ""))


def _acasa(pg):
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(BAZA + "/", wait_until="load", timeout=30000)
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    pg.wait_for_timeout(800)


def _card_cabinet(pg, cheie, asteapta=None):
    _acasa(pg)
    try:
        pg.click("button.cab-card:has([data-cheie='%s'])" % cheie, timeout=10000)
        pg.wait_for_selector(TOP + ".fereastra-corp", timeout=20000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=20000)
        pg.wait_for_function("() => { const f = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); return f && !/se încarcă|Se încarcă/.test(f.innerText); }", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2000)


def _card(pg, parcurs, firma, sel, asteapta=None):
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return False
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector(TOP + "#fa-facturi", state="detached", timeout=20000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2000)
    return True


def _apasa(pg, sel, asteapta=None, timp=1500):
    try:
        pg.click(TOP + sel, timeout=10000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(timp)


def _apasa_text(pg, text, asteapta=None, timp=1500):
    try:
        pg.locator(TOP + "button", has_text=text).first.click(timeout=10000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(timp)


def _motiv(pg):
    return _text(pg, MOTIV)


def _fisa(pg, parcurs):
    _card(pg, parcurs, F5, "#fa-salariati")
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
        pg.locator(TOP + "#sp-tabel tbody tr.sp-rand").first.locator(".sp-deschide").click(timeout=10000)
        pg.wait_for_selector(TOP + "#ss-butoane", timeout=30000)
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(1500)
    return True


def _cere(rele, unde, text, contine=(), lipseste=()):
    for t in contine:
        if t not in text:
            rele.append("%s: lipsește «%s» (text: «%s…»)" % (unde, t, text[:160]))
    for t in lipseste:
        if t in text:
            rele.append("%s: încă apare «%s»" % (unde, t))


def test_texte_17_5_I(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)

        # 1. Sinteza zilei: acordul numeralului la fiecare cifră (snapshot: 1 sesizare necitită -> «1 sesizare nouă»)
        _card_cabinet(pg, "brief", ".sa-cifra")
        cifre = pg.locator(TOP + ".sa-cifra")
        if not cifre.count():
            rele.append("Sinteza zilei: rândul cifrelor (.sa-cifra) lipsește")
        for i in range(cifre.count()):
            t = _norm(cifre.nth(i).inner_text())
            if re.match(r"^1 (sesizări noi|pregătite|validate|respinse|depuse)$", t):
                rele.append("Sinteza zilei: acord greșit la singular: «%s»" % t)
        _cere(rele, "Sinteza zilei", _text(pg), contine=["1 sesizare nouă"], lipseste=["1 sesizări noi", "de de validat"])

        # 2. Termene: introducerea numește restanțele
        _card_cabinet(pg, "termene", ".mig-intro")
        _cere(rele, "Termene", _text(pg), contine=["Restanțele (termen depășit, nedepuse) și scadențele din următoarele 60 de zile, pe dată."],
              lipseste=["Scadențele care urmează"])

        # 2. Consolidare: luna în curs e cuprinsă
        _card_cabinet(pg, "consolidare", ".pf-intro")
        _cere(rele, "Consolidare", _text(pg), contine=["inclusiv (luna în curs"], lipseste=["anului, până la"])

        # 5. Asistenți: drepturile în cuvinte
        _card_cabinet(pg, "asistenti", ".asi-perm")
        pastile = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .asi-perm')].map((e) => [e.className, e.textContent.trim()])")
        if not pastile:
            rele.append("Asistenți: nicio pastilă de drept (.asi-perm)")
        for cls, t in pastile:
            if "asi-perm-off" in cls and not t.startswith("Nu poate "):
                rele.append("Asistenți: dreptul lipsă nu e spus în cuvinte: «%s»" % t)
            if "asi-perm-on" in cls and not t.startswith("✓ Poate "):
                rele.append("Asistenți: dreptul prezent nu mai e «✓ Poate …»: «%s»" % t)
        _cere(rele, "Asistenți", _text(pg), contine=["Nu poate valida", "✓ Poate pregăti", "Adaugă asistent"], lipseste=["· Poate valida", "· Poate depune"])

        # 5. Capacitate: butonul poartă numele ferestrei pe care o deschide
        _card_cabinet(pg, "capacitate", ".stare-goala")
        _cere(rele, "Capacitate", _text(pg), contine=["Deschide Asistenți"], lipseste=["Adaugă asistenți"])

        # 4. Activitate › Activitatea echipei și Tipare de erori: numele ferestrei = numele butonului
        _card_cabinet(pg, "activitate", "#opt-tipare")
        _cere(rele, "meniul Activitate", _text(pg), contine=["Activitatea echipei", "Tipare de erori"])
        _apasa(pg, "#opt-jurnal", ".fereastra-corp", 2500)
        if _text(pg, NUME) != "Activitatea echipei":
            rele.append("Activitatea echipei: numele ferestrei e «%s», așteptat «Activitatea echipei»" % _text(pg, NUME))
        _card_cabinet(pg, "activitate", "#opt-tipare")
        _apasa(pg, "#opt-tipare", ".fereastra-corp", 2500)
        if _text(pg, NUME) != "Tipare de erori":
            rele.append("Tipare de erori: numele ferestrei e «%s», așteptat «Tipare de erori»" % _text(pg, NUME))

        # 4 + 3. Solicitări client F1: h2 = numele cardului; placeholderul cu «…» și fără «răspuns» la nimic
        _card(pg, parcurs, F1, "#fa-solicitari", "#sol-input")
        _cere(rele, "Solicitări client", _text(pg), contine=["Solicitări client", "Niciun mesaj încă."])
        ph = pg.locator(TOP + "#sol-input").first.get_attribute("placeholder") if pg.locator(TOP + "#sol-input").count() else None
        if ph != "Scrie un mesaj către client…":
            rele.append("Solicitări client: placeholderul e «%s», așteptat «Scrie un mesaj către client…»" % ph)
        al = pg.locator(TOP + "#sol-input").first.get_attribute("aria-label") if pg.locator(TOP + "#sol-input").count() else None
        if al != "Mesaj către client":
            rele.append("Solicitări client: aria-label-ul câmpului e «%s», așteptat «Mesaj către client»" % al)

        # 3. e-Transport F1: linia de pauză la toate opțiunile de tip
        _card(pg, parcurs, F1, "#fa-etransport", "#et-tip")
        optiuni = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #et-tip option')].map((o) => o.textContent.trim())")
        if not optiuni:
            rele.append("e-Transport: lista «Tip operațiune» (#et-tip) lipsește")
        for o in optiuni:
            if " - " in o:
                rele.append("e-Transport: cratimă cu spații în opțiunea «%s»" % o)
        if "AIC — achiziție intracomunitară" not in optiuni:
            rele.append("e-Transport: opțiunea «AIC — achiziție intracomunitară» lipsește (%s)" % optiuni)

        # 2. Registrul-inventar F1 (gol): majusculă, fără repetarea mesajului registrului gol
        _card(pg, parcurs, F1, "#fa-reginventar", "#ri-adauga")
        _cere(rele, "Registrul-inventar", _text(pg), contine=["Toate rândurile înscrise în registru", "Niciun rând înscris."],
              lipseste=["toate rândurile înscrise în registru", "un registru gol nu înseamnă"])

        # 2. Rapoarte comerciale F1: cardul poartă numele ferestrei
        _card(pg, parcurs, F1, "#fa-rapoarte", "#r-carduri")
        _cere(rele, "Rapoarte comerciale", _text(pg), contine=["Ce nu apare în aceste rapoarte"], lipseste=["nu apar aici"])

        # 2. Produse F1: justificarea pe rândul ei, introdusă
        _card(pg, parcurs, F1, "#fa-produse", ".pr-rand")
        _cere(rele, "Produse", _text(pg), contine=["Temeiul cotei:", "cota de pe NIR nr 4 din 20.10.2026"])
        if "· cota de pe NIR" in _text(pg):
            rele.append("Produse: justificarea e încă lipită după « · » pe rândul prețului")

        # 2. Istoric facturi F1 (luna 10/2026, după «← luna»): butonul spune câte facturi aduce
        _card(pg, parcurs, F1, "#fa-facturi")
        _apasa(pg, "#fac-istoric", "#fac-prev", 2500)
        _apasa(pg, "#fac-prev", ".fac-frand-btn", 2500)   # 11/2026 n-are facturi; 10/2026 are 25: butonul spune «Arată încă 10 facturi ale lunii»
        _cere(rele, "Istoric facturi", _text(pg), contine=["Arată încă 10 facturi ale lunii"], lipseste=["Vezi și facturile mai vechi"])

        # 3. Model factură F1: previzualizare, culorile cu nume
        _card(pg, parcurs, F1, "#fa-facturi")
        _apasa(pg, "#fac-model", "#mf-preview", 2500)
        _cere(rele, "Model factură", _text(pg), contine=["previzualizare în timp real"], lipseste=["preview live"])
        culori = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .mf-culoare-opt')].map((b) => (b.getAttribute('aria-label') || '').trim())")
        if len(culori) != 7:
            rele.append("Model factură: %d butoane de culoare, așteptat 7" % len(culori))
        for c in culori:
            if not c.startswith("Culoare de accent: ") or len(c) <= len("Culoare de accent: "):
                rele.append("Model factură: buton de culoare fără nume (aria-label «%s», așteptat «Culoare de accent: <nume>»)" % c)

        # 3. NIR nou F1: cost accesoriu fără englezism, TVA transport 0% explicat
        _card(pg, parcurs, F1, "#fa-stocuri", "#sn-toggle")
        _apasa(pg, "#sn-toggle", "#sn-transport-cota", 2500)
        _cere(rele, "NIR nou", _text_brut(pg), contine=["Cost accesoriu — se repartizează", "TVA transport 0%: fără TVA pe factura transportatorului"],
              lipseste=["landed cost"])

        # 2 + 7. Import date F1: rândul «Solduri inițiale» al meniului; pasul Solduri inițiale: numele firmei pe un rând cu textul
        _card(pg, parcurs, F1, "#fa-import", "#mig-pasi")
        _cere(rele, "Import date (meniul)", _text(pg), contine=["balanța de deschidere (fără data de referință): 6 conturi"], lipseste=["balanța la —"])
        _apasa(pg, "#mig-pasi button.mig-frand[data-strat='solduri']", ".mig-intro", 2500)
        brut = _text_brut(pg)
        _cere(rele, "Import date › Solduri inițiale", brut, contine=["F1 Comert Stoc SRL · Încarcă balanța de deschidere"], lipseste=["SRLÎncarcă", "balanța la —"])

        # 4. Bilanț anual F1: numele ferestrei = numele cardului
        _card(pg, parcurs, F1, "#fa-bilant", "#bl-tip")
        if _text(pg, NUME) != "Bilanț anual":
            rele.append("Bilanț anual: numele ferestrei e «%s», așteptat «Bilanț anual»" % _text(pg, NUME))
        t = _text(pg)
        if "alege tipul mai jos" in t:
            rele.append("Bilanț anual: mesajul spune «alege tipul mai jos», dar tipul se alege deasupra")
        if "Categoria de mărime nu se poate determina" in t and "alege tipul în câmpul «Tip» de sus" not in t:
            rele.append("Bilanț anual: mesajul categoriei nedeterminate nu trimite la câmpul «Tip» de sus")

        # 6. Declarații F1 pasul 1: motivul numește câmpul
        _card(pg, parcurs, F1, "#fa-declaratii", "#dec-continua")
        if not _motiv(pg).startswith("Completează: Tip declarație"):
            rele.append("Declarații pasul 1: motivul e «%s», așteptat «Completează: Tip declarație»" % _motiv(pg))

        # 6. Leasing F1: «Primire bun (financiar)» -> primele trei câmpuri și restul numărate; codul 2.3.2.1.1 din catalog
        _card(pg, parcurs, F1, "#fa-operatiuni", "button[data-op='leasing']")
        _apasa(pg, "button[data-op='leasing']", "#op-tip", 2000)
        _apasa_text(pg, "Primire bun (financiar)", "#op-cod_catalog", 2000)
        m = _motiv(pg)
        if not re.match(r"^Completează: [^,]+, [^,]+, [^,]+ și încă \d+( de)? câmpuri$", m):
            rele.append("Leasing «Primire bun»: motivul e «%s», așteptat «Completează: <3 câmpuri> și încă N câmpuri»" % m)
        try:
            pg.fill(TOP + "#op-cod_catalog", "2.3.2.1.1", timeout=10000)
            pg.dispatch_event(TOP + "#op-cod_catalog", "change")
            pg.wait_for_function("() => { const s = document.querySelector('.fereastra-overlay:not(.fundal) #op-cod_catalog-stare'); return s && s.textContent.trim().length > 0; }", timeout=20000)
        except Exception:   # noqa: BLE001
            pass
        pg.wait_for_timeout(1000)
        st = _text(pg, TOP + "#op-cod_catalog-stare")
        _cere(rele, "Leasing «Cod din catalog» 2.3.2.1.1", st, contine=["în afară de excepțiile înscrise sub acest cod în catalog · durata între 48 și 72 de luni"],
              lipseste=["în afară de ·"])

        # 1. Bancă F1: acordul la plural pe cardul semnelor («N contate, note nevalidate»)
        _card(pg, parcurs, F1, "#fa-banca", "#bk-carduri")
        t = _text(pg)
        # formele exacte (singular la 1; plural; «de» de la 20 în sus și la ...00, ca dupaNumar(); «fără potrivire» e invariabil, fără «de»)
        for sg, pl, invar in (("fără potrivire", "fără potrivire", True), ("potrivire de verificat", "potriviri de verificat", False),
                              ("potrivire parțială", "potriviri parțiale", False), ("operațiune a băncii", "operațiuni ale băncii", False),
                              ("contată, notă nevalidată", "contate, note nevalidate", False)):
            for mt in re.finditer(r"\b(\d+) ((?:de )?(?:%s|%s))(?![\w])" % (re.escape(pl), re.escape(sg)), t):
                n = int(mt.group(1))
                r = n % 100
                asteptat = sg if n == 1 else (("de " if (not invar and n and (r == 0 or r >= 20)) else "") + pl)
                if mt.group(2) != asteptat:
                    rele.append("Bancă: acord greșit pe cardul semnelor: «%s», așteptat «%d %s»" % (mt.group(0), n, asteptat))

        # 4. Salariați F5: h2 = numele cardului
        _card(pg, parcurs, F5, "#fa-salariati", "#sp-contare")
        h2 = _text(pg, TOP + ".fereastra .fereastra-corp h2.pf-titlu")
        if "Salariați" not in h2 or "Stat de plată" in h2:
            rele.append("Salariați F5: titlul din corp e «%s», așteptat «Salariați»" % h2)

        # 4. Certificat nou F5: secțiunea nu repetă numele ferestrei
        if _fisa(pg, parcurs):
            _apasa_text(pg, "Concediu medical", "#cm-nou", 2000)
            _apasa(pg, "#cm-nou", "#cm-calc", 2500)
            _cere(rele, "Certificat nou", _text(pg), contine=["Datele certificatului"], lipseste=["Certificat nou"])
        else:
            rele.append("Fișa salariatului F5 nu s-a deschis (Certificat nou nevizitat)")
    finally:
        b.close()
    assert not rele, "textele 17.5-I: %s" % "; ".join(rele)
