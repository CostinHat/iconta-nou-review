# -*- coding: utf-8 -*-
"""PIESELE CADRULUI — lotul 17.5-H2 (rândurile AC072, AC085, AC086, AC096, AC107, AC110, AC115, AC125, AC126, AC128, AC131, AC140, AC144, AC160, AC168, AC174 din
auditul complet; decizii_17_5_H2.txt pct.1–7). Scris de arhitect; Code nu îl modifică.

La 1366×768, ceas înghețat 03.11.2026, cu contul administratorului (dovada.71507) pe F1 Comert Stoc și F5 SRL Salariati și cu contul clientului F1 (dovada.71511) în portal:
  1. lista goală nu devine tabel: Istoric facturi F1 (luna 11/2026, fără facturi) și Contracte F1 (fără șabloane) nu au capul «Înregistrare», nici contorul «1 rând»;
  2. meniul Import date F1 nu are contor de rânduri; portalul «Cifrele firmei» nu are «Înregistrare» și nici contor;
  3. capul tabelului dintr-o cutie nu acoperă rândurile: Detaliu factură F1A19 (primul rând e sub cap), Fișa salariatului F5 (fiecare tabel din «Compoziția netului» are capul la începutul lui);
     în Registru jurnal F1 capul rămâne lipit la derularea zonei (invariantă);
  4. exportul de rezervă nu e acțiune principală fără tabel cu înregistrări: Istoric facturi gol («Descarcă PDF» principal inactiv), meniul Import date și portal «Cifrele firmei» — niciun buton principal;
  5. eticheta principalului e verbul, motivul stă în fj-motiv: Casă — dispoziție nouă («Adaugă»), Registru jurnal — notă nouă («Salvează»);
  6. principalul inactiv cu motiv cât formularul e incomplet: Ore suplimentare, Certificat nou (CM), Firmă nouă (CUI și Tip firmă cu «*»; cu CUI completat și tipul «— alege —» principalul rămâne inactiv, cu motivul care numește «Tip firmă»), D104 pasul 2; confirmarea storno are butonul inactiv până la alegerea Da/Nu;
  7. o singură acțiune cu aspect de principală pe fereastră: pe fiecare fereastră vizitată exact un buton cu data-actiune-principala, în bara de jos, și niciun .buton-verde vizibil în conținut;
     D301 F3 pasul 2: «Regenerează D301» e secundar. (Portal «Solicitări» nu e martor: AC174 e falsă pe snapshot; se reverifică pe producție de arhitect.)
Nu salvează nimic; nu alege niciun fișier; singurul câmp completat e CUI-ul din «Firmă nouă» (firma nu se adaugă). Un singur test."""
import importlib.util
import os
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
CLIENT = "dovada.71511@sesiuneab.test"   # contul de client al firmei F1 (public.user_tenants: 71511 -> 105779 = tenant_9049) din dump-ul iconta_test
F1 = "F1 Comert Stoc"
F5 = "F5 SRL Salariati"
TOP = ".fereastra-overlay:not(.fundal) "
PRINCIPAL = TOP + ".fereastra .fj-butoane .fj-principal"
MOTIV = TOP + ".fereastra .fj-motiv"
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""
# starea barei de jos și a conținutului ferestrei de sus: câte butoane poartă data-actiune-principala (vizibile), câte sunt în bara de jos, câte .buton-verde vizibile stau în conținut
JS_BARA = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return null;
  const viz = (e) => !!(e.offsetParent || e.getClientRects().length);
  const bara = F.querySelector('.fereastra-jos');
  const marcate = [...F.querySelectorAll('[data-actiune-principala]')].filter(viz);
  const inBara = marcate.filter((e) => bara && bara.contains(e));
  const verzi = [...F.querySelectorAll('.fereastra-corp .buton-verde')].filter((e) => viz(e) && !(bara && bara.contains(e)) && !e.closest('table, template, details:not([open])'));
  return { marcate: marcate.length, in_bara: inBara.length, verzi: verzi.map((e) => e.innerText.trim()), text: (F.querySelector('.fereastra-corp') || F).innerText,
           subsoluri: [...F.querySelectorAll('.ds-tabel-subsol')].map((e) => e.innerText.trim()) };
}"""
# capul tabelului față de tabelul lui, pentru fiecare tabel cu <thead> din cutiile .ds-tabel-cutie ale ferestrei de sus: diferența top(th) - top(table), în px
JS_CAPETE = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return [];
  return [...F.querySelectorAll('.ds-tabel-cutie table')].filter((t) => t.tHead && t.offsetParent).map((t) => {
    const th = t.tHead.querySelector('th'); return th ? Math.round(th.getBoundingClientRect().top - t.getBoundingClientRect().top) : null; });
}"""
# ce element stă în centrul primului rând al tabelului liniilor facturii (TD = rândul se vede; TH = capul lipit îl acoperă)
JS_PRIMUL_RAND = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return 'fara fereastra';
  const tr = F.querySelector('table.fd-tabel tbody tr'); if (!tr) return 'fara rand';
  const r = tr.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  return e ? e.tagName + (e.closest('thead') ? '/thead' : e.closest('tbody') ? '/tbody' : '') : 'nimic';
}"""
# derularea zonei Registrului jurnal cu 300 px: capul tabelului rămâne la marginea de sus a zonei (lipit) — invariantă față de lot
JS_JURNAL_LIPIT = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return 'fara fereastra';
  const z = F.querySelector('.zona-derulare'); const t = z && z.querySelector('table'); if (!z || !t || !t.tHead) return 'fara zona cu tabel';
  if (z.scrollHeight <= z.clientHeight + 300) return 'zona fara derulare';
  z.scrollTop = 300; const th = t.tHead.querySelector('th'); const dif = Math.round(th.getBoundingClientRect().top - z.getBoundingClientRect().top);
  return String(dif);
}"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _card(pg, parcurs, firma, sel):
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return False
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector(TOP + "#fa-facturi", state="detached", timeout=20000)
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


def _principal(pg):
    loc = pg.locator(PRINCIPAL)
    n = loc.count()
    return n, (" ".join(loc.first.inner_text().split()) if n else "")


def _motiv(pg):
    loc = pg.locator(MOTIV)
    return " ".join(loc.first.inner_text().split()) if loc.count() else ""


def _norm(t):
    return " ".join((t or "").split())


def _bara(pg):
    return pg.evaluate(JS_BARA) or {"marcate": -1, "in_bara": -1, "verzi": ["fara fereastra"], "text": "", "subsoluri": []}


def _o_singura_principala(rele, nume, b):
    """Pct.7: exact un buton cu data-actiune-principala, în bara de jos, și niciun .buton-verde vizibil în conținut."""
    if b["marcate"] != 1 or b["in_bara"] != 1:
        rele.append("%s: %d buton(e) cu data-actiune-principala (%d în bară), așteptat exact unul, în bară" % (nume, b["marcate"], b["in_bara"]))
    if b["verzi"]:
        rele.append("%s: buton-verde în conținut, cu aspect de principală: %s" % (nume, ", ".join("«%s»" % v for v in b["verzi"])))


def _fara_tabel_gol(rele, nume, b):
    """Pct.1/2: textul ferestrei fără «Înregistrare» și fără «1 rând»; niciun subsol cu contor."""
    if "Înregistrare" in b["text"]:
        rele.append("%s: capul «Înregistrare» pe listă fără înregistrări" % nume)
    if "1 rând" in b["text"]:
        rele.append("%s: contorul «1 rând» pe listă fără înregistrări" % nume)
    contoare = [s for s in b["subsoluri"] if "rând" in s]
    if contoare:
        rele.append("%s: subsol cu contor pe listă fără înregistrări: %s" % (nume, ", ".join(contoare)))


def _fisa(pg, parcurs):
    """F5 › Salariați › (dacă luna ceasului nu are rânduri, «← luna» de cel mult 3 ori) › primul salariat › fișa."""
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


def _eticheta(pg, for_id):
    loc = pg.locator(TOP + "label[for='%s']" % for_id)
    return _norm(loc.first.inner_text()) if loc.count() else ""


def _inactiv(pg, sel):
    loc = pg.locator(TOP + sel)
    if not loc.count():
        return None
    return bool(pg.evaluate("(s) => { const e = document.querySelector('.fereastra-overlay:not(.fundal) ' + s); return !!(e.disabled || e.getAttribute('aria-disabled') === 'true' || e.dataset.cadruInactiv); }", sel))


def test_piese_17_5_H2(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)

        # 1 + 4. Istoric facturi F1, luna ceasului (11/2026): fără facturi -> fără tabel, fără contor, fără PDF de rezervă
        _card(pg, parcurs, F1, "#fa-facturi")
        _apasa(pg, "#fac-istoric", "#fac-prev", 2500)
        st = _bara(pg)
        if "Nicio factură în luna aceasta." not in st["text"]:
            rele.append("Istoric facturi 11/2026: mesajul listei goale lipsește (luna nu e goală sau fereastra nu s-a deschis)")
        _fara_tabel_gol(rele, "Istoric facturi 11/2026", st)
        n, text = _principal(pg)
        if n != 1 or "Descarcă PDF" not in text:
            rele.append("Istoric facturi 11/2026: așteptat un singur buton principal «Descarcă PDF», am găsit %d: «%s»" % (n, text))
        elif _inactiv(pg, ".fj-butoane .fj-principal") is not True:
            rele.append("Istoric facturi 11/2026: «Descarcă PDF» fără tabel cu înregistrări trebuie să fie inactiv")
        if st["marcate"] != 1:
            rele.append("Istoric facturi 11/2026: %d buton(e) cu data-actiune-principala, așteptat exact 1" % st["marcate"])

        # 3. Detaliu factură F1A19 (Istoric › «← luna» › rândul F1A19): primul rând al tabelului liniilor nu e acoperit de cap
        _apasa(pg, "#fac-prev", "button.fac-frand-btn", 1500)
        _apasa(pg, "button.fac-frand-btn[data-doc='F1A19']", ".fd-tabel", 2500)
        st = _bara(pg)
        if "Marfa A" not in st["text"]:
            rele.append("Detaliu factură F1A19: rândul «Marfa A» lipsește din fereastră (factura nu s-a deschis)")
        peste = pg.evaluate(JS_PRIMUL_RAND)
        if not peste.startswith("TD"):
            rele.append("Detaliu factură F1A19: în centrul primului rând stă %s, așteptat celula rândului (TD/tbody)" % peste)
        capete = pg.evaluate(JS_CAPETE)
        if any(c is None or abs(c) > 1 for c in capete):
            rele.append("Detaliu factură F1A19: capul tabelului din cutie e deplasat față de tabel cu %s px, așteptat 0" % capete)
        _o_singura_principala(rele, "Detaliu factură F1A19", st)

        # 6. confirmarea storno (fereastră mică): «Confirm stornarea» inactiv cât alegerea Da/Nu e goală; nu se apasă
        _apasa(pg, "#fd-storno", "#fd-storno-ok", 1500)
        if pg.locator(TOP + "#fd-storno-retur").count():
            if pg.locator(TOP + "#fd-storno-retur").first.input_value() == "":
                if _inactiv(pg, "#fd-storno-ok") is not True:
                    rele.append("confirmare storno F1A19: «Confirm stornarea» activ cu alegerea «se întoarce în stoc?» goală")
            else:
                rele.append("confirmare storno F1A19: alegerea Da/Nu are deja o valoare (așteptat goală la deschidere)")
        else:
            rele.append("confirmare storno F1A19: întrebarea «se întoarce în stoc?» (#fd-storno-retur) lipsește")

        # 1 + 4. Contracte F1 (fără șabloane): fără tabel, fără contor; principalul rămâne «+ Șablon nou»
        _card(pg, parcurs, F1, "#fa-contracte")
        st = _bara(pg)
        _fara_tabel_gol(rele, "Contracte F1", st)
        n, text = _principal(pg)
        if (n, text) != (1, "+ Șablon nou"):
            rele.append("Contracte F1: %d buton(e) principal(e) «%s», așteptat «+ Șablon nou»" % (n, text))
        _o_singura_principala(rele, "Contracte F1", st)

        # 2 + 4. Import date F1 (meniul straturilor): fără contor de rânduri, fără buton principal
        _card(pg, parcurs, F1, "#fa-import")
        try:
            pg.wait_for_selector(TOP + "#mig-pasi", timeout=20000)
            pg.wait_for_timeout(1000)
        except Exception:   # noqa: BLE001
            pass
        st = _bara(pg)
        contoare = [s for s in st["subsoluri"] if "rând" in s]
        if contoare:
            rele.append("Import date F1 (meniul): contor de tabel sub meniu: %s" % ", ".join(contoare))
        n, text = _principal(pg)
        if n != 0:
            rele.append("Import date F1 (meniul): buton principal «%s», așteptat niciunul" % text)

        # 5. Casă — dispoziție nouă F1: eticheta «Adaugă», motivul în fj-motiv
        _card(pg, parcurs, F1, "#fa-casa")
        _apasa(pg, "#c-toggle", "#c-adauga", 1500)
        n, text = _principal(pg)
        if (n, text) != (1, "Adaugă"):
            rele.append("Casă — dispoziție nouă: %d buton(e) principal(e) «%s», așteptat «Adaugă»" % (n, text))
        if not _motiv(pg).startswith("Completează:"):
            rele.append("Casă — dispoziție nouă: motivul «Completează: …» lipsește din fj-motiv (găsit «%s»)" % _motiv(pg))
        _o_singura_principala(rele, "Casă — dispoziție nouă", _bara(pg))

        # 5. Registru jurnal — notă nouă F1: eticheta «Salvează», motivul în fj-motiv; 3. Registru jurnal: capul rămâne lipit la derulare (invariantă)
        _card(pg, parcurs, F1, "#fa-jurnal")
        try:
            pg.wait_for_selector(TOP + "#j-nota-noua", timeout=20000)
            pg.wait_for_timeout(1500)
        except Exception:   # noqa: BLE001
            pass
        lipit = pg.evaluate(JS_JURNAL_LIPIT)
        if lipit not in ("zona fara derulare",) and not (lipit.lstrip("-").isdigit() and abs(int(lipit)) <= 1):
            rele.append("Registru jurnal F1: după derularea zonei cu 300 px capul tabelului e la %s px de marginea zonei, așteptat lipit (0)" % lipit)
        _apasa(pg, "#j-nota-noua", "#je-salveaza", 1500)
        n, text = _principal(pg)
        if (n, text) != (1, "Salvează"):
            rele.append("Registru jurnal — notă nouă: %d buton(e) principal(e) «%s», așteptat «Salvează»" % (n, text))
        if not _motiv(pg).startswith("Completează:"):
            rele.append("Registru jurnal — notă nouă: motivul «Completează: …» lipsește din fj-motiv (găsit «%s»)" % _motiv(pg))

        # 6. D104 F1 pasul 2: «Generează D104» inactiv cu motiv, câmpurile «*» goale
        _card(pg, parcurs, F1, "#fa-declaratii")
        try:
            pg.locator(TOP + "li.ds-lista-rand", has_text="D104").first.click(timeout=10000)
            pg.wait_for_selector(TOP + "#dec-continua", timeout=20000)
            pg.wait_for_timeout(800)
            pg.click(TOP + "#dec-continua", timeout=10000)
            pg.wait_for_selector(TOP + "#d104-dnume", state="attached", timeout=20000)
        except Exception:   # noqa: BLE001
            pass
        pg.wait_for_timeout(1500)
        n, text = _principal(pg)
        if (n, text) != (1, "Generează D104"):
            rele.append("D104 pasul 2: %d buton(e) principal(e) «%s», așteptat «Generează D104»" % (n, text))
        if pg.locator(TOP + "#d104-dnume").count() and pg.locator(TOP + "#d104-dnume").first.input_value() == "" and not _motiv(pg).startswith("Completează:"):
            rele.append("D104 pasul 2: «Generează D104» fără motivul «Completează: …» cu câmpurile «*» goale (fj-motiv: «%s»)" % _motiv(pg))

        # 6. Firmă nouă (cabinet): CUI cu «*», «Adaugă firma» inactiv cu motiv
        try:
            parcurs._la_meniul_firme(pg)   # cabinet › Firme (docs/dovezi/17_1/parcurs_17_1.py)
            pg.click("#opt-existente")
            pg.wait_for_selector("#firme-adauga", timeout=20000)
            pg.click(TOP + "#firme-adauga", timeout=10000)   # «+ Adaugă firmă» (static/js/ecrane/firme.js:75) deschide fereastra «Adaugă firmă»
            pg.wait_for_selector(TOP + "#fn-cui", timeout=20000)
        except Exception:   # noqa: BLE001
            pass
        pg.wait_for_timeout(1500)
        if "*" not in _eticheta(pg, "fn-cui"):
            rele.append("Firmă nouă: eticheta CUI nu poartă «*» (găsit «%s»)" % _eticheta(pg, "fn-cui"))
        if "*" not in _eticheta(pg, "fn-tip"):
            rele.append("Firmă nouă: eticheta Tip firmă nu poartă «*» (găsit «%s»)" % _eticheta(pg, "fn-tip"))
        n, text = _principal(pg)
        if (n, text) != (1, "Adaugă firma"):
            rele.append("Firmă nouă: %d buton(e) principal(e) «%s», așteptat «Adaugă firma»" % (n, text))
        if not _motiv(pg).startswith("Completează:"):
            rele.append("Firmă nouă: motivul «Completează: …» lipsește din fj-motiv (găsit «%s»)" % _motiv(pg))
        # AC128: CUI completat (DANTE INTERNATIONAL SA, 14399840, clientul F1 din snapshot), Tip firmă rămâne «— alege —» -> principalul inactiv, motivul numește «Tip firmă»
        try:
            pg.fill(TOP + "#fn-cui", "14399840")
            pg.wait_for_timeout(2500)   # răspunsul ANAF / completarea denumirii (dacă vine); se judecă starea, nu denumirea
        except Exception:   # noqa: BLE001
            pass
        if pg.locator(TOP + "#fn-tip").count() and pg.locator(TOP + "#fn-tip").first.input_value() == "":
            if _inactiv(pg, ".fj-butoane .fj-principal") is not True:
                rele.append("Firmă nouă: cu CUI completat și Tip firmă «— alege —», «Adaugă firma» e activ (așteptat inactiv, cu motiv)")
            if "Tip firmă" not in _motiv(pg):
                rele.append("Firmă nouă: cu CUI completat motivul nu numește «Tip firmă» (fj-motiv: «%s»)" % _motiv(pg))
        else:
            rele.append("Firmă nouă: #fn-tip lipsește sau are deja o valoare la deschidere")

        # 3. Fișa salariatului F5: capetele tabelelor din cutii la începutul tabelelor
        if _fisa(pg, parcurs):
            st = _bara(pg)
            if "Compoziția netului" not in st["text"]:
                rele.append("Fișa salariatului F5: «Compoziția netului» lipsește")
            capete = pg.evaluate(JS_CAPETE)
            # la 1366x768 Fisa nu are tabele in cutie (vd_dupa 17.5-E2: tabele_ds=0): se masoara numai unde exista cutii
            if any(c is None or abs(c) > 1 for c in capete):
                rele.append("Fișa salariatului F5: capete deplasate față de tabelele lor cu %s px, așteptat 0" % capete)
            # 3b. la 1920x1080 Fisa are tabele in cutie (vd_dupa 17.5-E2: tabele_ds=3): aici se dovedeste lipirea capului
            pg.set_viewport_size({"width": 1920, "height": 1080})
            if _fisa(pg, parcurs):
                capete = pg.evaluate(JS_CAPETE)
                if not capete:
                    rele.append("Fișa salariatului F5 la 1920×1080: niciun tabel cu cap în cutie")
                elif any(c is None or abs(c) > 1 for c in capete):
                    rele.append("Fișa salariatului F5 la 1920×1080: capete deplasate față de tabelele lor cu %s px, așteptat 0" % capete)
            else:
                rele.append("Fișa salariatului F5 nu s-a deschis la 1920×1080")
            pg.set_viewport_size({"width": 1366, "height": 768})
            _fisa(pg, parcurs)
            # 6. Ore suplimentare: «Adaugă» inactiv cu motiv cât «Tipul*» și «Denumirea*» sunt goale
            try:
                pg.locator(TOP + "#ss-butoane button", has_text="Prime, sporuri").first.click(timeout=10000)
                pg.wait_for_selector(TOP + "#el-adauga", state="attached", timeout=20000)
            except Exception:   # noqa: BLE001
                pass
            pg.wait_for_timeout(1500)
            n, text = _principal(pg)
            if (n, text) != (1, "Adaugă"):
                rele.append("Ore suplimentare F5: %d buton(e) principal(e) «%s», așteptat «Adaugă»" % (n, text))
            if not _motiv(pg).startswith("Completează:"):
                rele.append("Ore suplimentare F5: motivul «Completează: …» lipsește din fj-motiv (găsit «%s»)" % _motiv(pg))
            # 6. Certificat nou (CM): «Calculează și salvează» inactiv cu motiv
            if _fisa(pg, parcurs):
                try:
                    pg.locator(TOP + "#ss-butoane button", has_text="Concediu medical").first.click(timeout=10000)
                    pg.wait_for_selector(TOP + "#cm-nou", timeout=20000)
                    pg.click(TOP + "#cm-nou", timeout=10000)
                    pg.wait_for_selector(TOP + "#cm-calc", state="attached", timeout=20000)
                except Exception:   # noqa: BLE001
                    pass
                pg.wait_for_timeout(1500)
                n, text = _principal(pg)
                if (n, text) != (1, "Calculează și salvează"):
                    rele.append("Certificat nou F5: %d buton(e) principal(e) «%s», așteptat «Calculează și salvează»" % (n, text))
                if not _motiv(pg).startswith("Completează:"):
                    rele.append("Certificat nou F5: motivul «Completează: …» lipsește din fj-motiv (găsit «%s»)" % _motiv(pg))
            else:
                rele.append("Fișa salariatului F5 nu s-a deschis a doua oară (Certificat nou nevizitat)")
            # 7. Pontaj F5 (din fișă, butonul «Pontaj», firme.js:1498): un singur buton cu aspect de principală (fără .buton-verde în conținut)
            if _fisa(pg, parcurs):
                try:
                    pg.locator(TOP + "#ss-butoane button", has_text="Pontaj").first.click(timeout=10000)
                    pg.wait_for_selector(TOP + "#pj-calendar", state="attached", timeout=20000)
                except Exception:   # noqa: BLE001
                    pass
                pg.wait_for_timeout(1500)
                st = _bara(pg)
                if "pontaj" not in st["text"].lower():
                    rele.append("Pontaj F5: fereastra nu s-a deschis")
                _o_singura_principala(rele, "Pontaj F5", st)
            else:
                rele.append("Fișa salariatului F5 nu s-a deschis a treia oară (Pontaj nevizitat)")
        else:
            rele.append("Fișa salariatului F5 nu s-a deschis (Fișa, Ore suplimentare, Certificat nou nevizitate)")

        # 7. D301 F3 pasul 2: «Regenerează D301» e buton secundar, o singură acțiune principală
        _card(pg, parcurs, "F3 Intracomunitar", "#fa-declaratii")
        try:
            pg.locator(TOP + "li.ds-lista-rand", has_text="D301").first.click(timeout=10000)
            pg.wait_for_selector(TOP + "#dec-continua", timeout=20000)
            pg.wait_for_timeout(800)
            pg.click(TOP + "#dec-continua", timeout=10000)
            pg.wait_for_selector(TOP + "#d301-regen", state="attached", timeout=20000)
        except Exception:   # noqa: BLE001
            pass
        pg.wait_for_timeout(1500)
        if pg.locator(TOP + "#d301-regen").count():
            clase = pg.locator(TOP + "#d301-regen").first.get_attribute("class") or ""
            if "buton-primar" in clase.split() or "buton-secundar" not in clase.split():
                rele.append("D301 pasul 2: «Regenerează D301» are clasele «%s», așteptat buton secundar" % clase)
        else:
            rele.append("D301 pasul 2: #d301-regen lipsește (pasul 2 nu s-a deschis)")
        _o_singura_principala(rele, "D301 F3 pasul 2", _bara(pg))
    finally:
        b.close()

    # portalul clientului F1: «Cifrele firmei» fără tabel/contor/PDF de rezervă
    c = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        c.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        c.add_init_script(sesiune(CLIENT))
        pc = c.new_page()
        pc.goto(BAZA + "/", wait_until="load", timeout=30000)
        try:
            pc.wait_for_selector("button.cab-card", timeout=30000)
            pc.wait_for_timeout(1000)
            pc.locator("button.cab-card", has_text="Cifrele firmei").first.click(timeout=10000)
            pc.wait_for_selector(TOP + ".fereastra-corp", timeout=20000)
            pc.wait_for_function("() => { const f = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); return f && !f.innerText.includes('Se încarcă'); }", timeout=20000)
        except Exception:   # noqa: BLE001
            pass
        pc.wait_for_timeout(2000)
        st = pc.evaluate(JS_BARA) or {"marcate": -1, "in_bara": -1, "verzi": [], "text": "", "subsoluri": []}
        if "Cifrele firmei" not in st["text"]:
            rele.append("portal Cifrele firmei: fereastra nu s-a deschis")
        if "Înregistrare" in st["text"]:
            rele.append("portal Cifrele firmei: capul «Înregistrare» pe panoul de cifre")
        contoare = [s for s in st["subsoluri"] if "rând" in s]
        if contoare:
            rele.append("portal Cifrele firmei: contor de tabel pe panoul de cifre: %s" % ", ".join(contoare))
        loc = pc.locator(PRINCIPAL)
        if loc.count():
            rele.append("portal Cifrele firmei: buton principal «%s», așteptat niciunul (fără tabel de exportat)" % " ".join(loc.first.inner_text().split()))
    finally:
        c.close()
    assert not rele, "piesele cadrului 17.5-H2: %s" % "; ".join(rele)
