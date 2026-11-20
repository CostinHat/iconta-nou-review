# -*- coding: utf-8 -*-
"""PROBA ARHITECTULUI — lotul 17.5-X (auditul Pilot din 13.11.2026, 45 de poziții, pe versiunea 17.5-I; comanda_17_5_X.txt, decizii_17_5_X.txt, pasi_17_5_X.txt).
Scris de arhitect; Code nu îl modifică. Probă pe bază: pică; pe C: trece.

NUMAI CITIRE: nu trimite, nu salvează, nu importă, nu contează, nu validează, nu șterge și nu adaugă nimic în coadă; formularele deschise (deblocare, «+ Client nou», nota nouă) se lasă nesalvate.
La 1366×768, ceas înghețat 03.11.2026 (ceas_proba.MOMENT_REF), cu contul administratorului (dovada.71507), pe F1 Comert Stoc (tenant_9049), baza de test restaurată din snapshot.
Cifrele sunt cele confirmate pe snapshot (cifre_snapshot_17_5_X.txt), nu cele de pe producție. Fiecare mesaj de eșec începe cu «pct.N / poziția din audit / id e.k» și numește textul așteptat și ce s-a găsit pe ecran.
Control fiscal (e.9–e.12) alege explicit luna 10/2026 în selectorul «Luna comparată» (pe bază, unde selectorul lipsește, citește luna implicită a DATEI SERVERULUI, 10/2026 până la 30.11.2026): pe C nu depinde de data serverului. Data propusă la nota nouă (e.23) vine din ceasul ferestrei (înghețat). Un singur test; o secțiune care nu găsește martorul pe ecran scrie «martorul lipsește», nu oprește celelalte.
  1. P1 (727.2), domeniul D112, D300, D394, D406: clic pe rândul «<TIP> · 09/2026» — rândul marcat și câmpul Lună spun septembrie (D300 e.1–e.2, D394 e.3–e.4, D112 e.25–e.26, D406 e.27–e.28), apoi «Continuă» — titlul pasului 2 numește «<TIP> · septembrie 2026» (D300 e.5, D394 e.29, D112 e.30, D406 e.31); sub două rânduri lunare pe un tip = «NEEXECUTAT», testul pică; D100 și D390 sunt în afara lotului (decizii pct.22);
  2. P2 (729.1, 763): Închidere lună: formularul de deblocare cu motivul gol nu are confirmarea activă (e.6); textul «Se citesc controalele lunii…» dispare pe 10/2026 (e.7);
  3. P3 (739): NIR nou: numărul propus e 8 (maximul 7 + 1; decizia 4) (e.8);
  4. P4 (484): Control fiscal: eticheta «Luna comparată» (e.9); «Diferență neexplicată: 1.341,00 lei» pe 4423 (e.10); lipsește «Recalculul … confirmă cifrele» pe D300 (e.11); D390 o singură dată, la «De urmărit», cu motivul care conține nepotrivirea cu profilul (e.12);
  5. P5 (F089): Verificări: lipsește comparația ciornelor ca «diferență» (e.13), apare «Ciorne de stoc: 3.251,90 lei» (e.14); Stocuri păstrează «Stoc validat 6.272,38 lei = balanța 371» (e.15);
  6. P6 (F011, 751) — SCOS din lot la auditul extern r1 (decizii pct.21), rămâne ca notă: Bancă: NU se poate judeca fără scriere (cele 11 linii de extras ale lui F1 sunt contate sau ignorate): limită declarată, fără aserțiune;
  7. P7 (F018, 640.1, 633.1) — SCOS din lot la auditul extern r1 (decizii pct.21); secțiunea rămâne numai ca paznic de regresie, cu aserțiuni invariante: se face în clienti_ecran.js (Clienți și Furnizori): «+ Client nou» (e.16), «Verifică la ANAF» pe formularul deschis (e.17), «+ Furnizor nou» (e.18); aserțiuni invariante (trec și pe bază);
  8. P8 (F054, 602.1, 781): antetul Verificărilor «Luna 10/2026 · N de note» (e.19); Registru jurnal: antetul (e.20: același număr ca în Verificări, nu 84 fix), motivul scris pe nota validată (e.21); nota nouă pe luna blocată: data 2026-10-31 (e.22) și textul (e.23);
  9. P9 (F015): Casă 10/2026: «Casa rămâne pe minus (−58,00 lei)» (e.24)"""
import importlib.util
import os
import re
import sys

from conftest import BAZA, sesiune, sql

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
TOP = ".fereastra-overlay:not(.fundal) "


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _norm(t):
    return " ".join(str(t or "").split())


def _scurt(e):
    """Prima linie a erorii, fără «Call log»: în mesaj intră numai ce lipsește, nu jurnalul Playwright."""
    return "%s: %s" % (type(e).__name__, _norm(str(e).split("\n")[0])[:160])


def _sectiune(rele, nume, fn, *argumente):
    """O secțiune care nu găsește un martor (element, timp) nu oprește celelalte: «martorul lipsește» intră în listă."""
    try:
        fn(rele, *argumente)
    except Exception as e:   # noqa: BLE001
        rele.append("%s: martorul lipsește, secțiunea nu a putut citi ecranul (%s)" % (nume, _scurt(e)))


def _text(pg, sel=""):
    """Textul vizibil al ferestrei de sus (sau al elementului `sel` din ea); gol dacă elementul nu există (fără așteptare, fără excepție)."""
    return _norm(pg.evaluate(
        """(s) => { const f = document.querySelector('.fereastra-overlay:not(.fundal)'); if (!f) return '';
        const els = s ? [...f.querySelectorAll(s)] : [f.querySelector('.fereastra') || f]; return els.map((e) => e.innerText).join(' || '); }""", sel))


def _valoare(pg, sel):
    """Valoarea câmpului `sel` din fereastra de sus; None dacă lipsește."""
    return pg.evaluate("""(s) => { const e = document.querySelector('.fereastra-overlay:not(.fundal) ' + s); return e ? e.value : null; }""", sel)


def _card(pg, parcurs, firma, sel, asteapta=None):
    parcurs.firma(pg, firma)
    pg.evaluate("""(sel) => { const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return;
      const cont = c.closest('.firme-optiuni'); if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); } }""", sel)
    pg.click(TOP + sel, timeout=10000)
    if asteapta:
        pg.wait_for_selector(TOP + asteapta, state="attached", timeout=30000)
    pg.wait_for_timeout(1500)


def _la_luna(pg, pref, luna, an):
    """Navighează cu #<pref>-prev / #<pref>-next până când textul ferestrei spune «LL/AAAA» (cel mult 14 pași)."""
    tinta = "%02d/%d" % (luna, an)
    for _ in range(14):
        m = re.search(r"(?:Luna\s+)?(\d{2})/(\d{4})", _text(pg))
        if not m or m.group(0).endswith(tinta):
            break
        buton = "#%s-prev" % pref if (int(m.group(2)), int(m.group(1))) > (an, luna) else "#%s-next" % pref
        if not pg.locator(TOP + buton).count():
            break
        pg.click(TOP + buton, timeout=10000)
        pg.wait_for_timeout(900)


def _rand_lista(pg, text):
    """Clic pe rândul din lista pasului 1 din Declarații care conține `text` («Alte declarații» se deschide dacă rândul nu se vede)."""
    rand = pg.locator(TOP + ".ds-lista-rand", has_text=text).first
    if not rand.count() and pg.locator(TOP + "#dec-alte").count():
        if pg.get_attribute(TOP + "#dec-alte", "aria-expanded") != "true":
            pg.click(TOP + "#dec-alte", timeout=10000)
        pg.wait_for_timeout(500)
    rand.click(timeout=10000)
    pg.wait_for_timeout(600)


LUNI = ("ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie")


def _p1(rele, pg, parcurs):
    # Rândul judecat = AL DOILEA rând lunar al tipului din listă (oricare lună): proba nu depinde de data serverului (lista vine din
    # control_fiscal_api.obligatii_datorate, cu data serverului). Domeniul P1 = exact aceste patru tipuri; D100 și D390 sunt în afara lotului.
    # Cu sub două rânduri lunare ale unui tip, martorul lipsește și testul PICĂ (P1 nerezolvat).
    for tip, e, e_titlu in (("D300", 1, 5), ("D394", 3, 29), ("D112", 25, 30), ("D406", 27, 31)):
        _card(pg, parcurs, F1, "#fa-declaratii", "#dec-tip")
        if pg.locator(TOP + "#dec-alte").count() and pg.get_attribute(TOP + "#dec-alte", "aria-expanded") != "true":
            pg.click(TOP + "#dec-alte", timeout=10000)
            pg.wait_for_timeout(500)
        randuri = [m.group(0) for m in (re.search(r"%s · (\d{2})/(\d{4})" % tip, x) for x in pg.locator(TOP + ".ds-lista-rand").all_inner_texts()) if m]
        randuri = list(dict.fromkeys(randuri))
        if len(randuri) < 2:   # auditul extern 17.5-X r2, C2: lipsa martorului pe un tip din domeniul P1 = P1 nerezolvat, nu avertisment
            rele.append("pct.1 / 727.2: NEEXECUTAT pe %s — sub două rânduri lunare în listă (%r), martorul lipsește: P1 nu se poate accepta" % (tip, randuri))
            continue
        rand = randuri[1]
        ll, an = int(rand[-7:-5]), rand[-4:]
        luna_txt = LUNI[ll - 1]
        _rand_lista(pg, rand)
        ales = _text(pg, ".ds-lista-ales-rand")
        if rand not in ales:
            rele.append("pct.1 / 727.2 / e.%d: după clic pe «%s» rândul marcat în listă nu e el (așteptat «%s»; găsit: %r; azi rămâne marcat primul rând %s, cel din 08/2026)" % (e, rand, rand, ales[:120], tip))
        luna = _text(pg, "#dec-luna option:checked")
        if luna_txt not in luna:
            rele.append("pct.1 / 727.2 / e.%d: după clic pe «%s» câmpul Lună nu spune %s (găsit: %r)" % (e + 1, rand, luna_txt, luna[:80]))
        # auditul extern r3, B1: pasul 2 se verifică la FIECARE tip din domeniu (nu numai D300). Stările pasului 2 din declaratii.js:
        # 506 «completează <T> · <perioada>», 572 «verifică <TIP> · <perioada>», 641 «<TIP> · <perioada> e deja depusă», 601 #dec-gol-da;
        # starea de refuz 525 («Pasul 2 din 3 — generare» + .dec-eroare) nu numește perioada: pică (verificarea nu se poate face = P1 nerezolvat).
        pg.click(TOP + "#dec-continua", timeout=10000)
        pg.wait_for_selector(TOP + "#dec-trimite, " + TOP + ".dec-eroare, " + TOP + "#dec-gol-da, " + TOP + "#dec-rect-depusa", state="attached", timeout=180000)   # cele patru stări finale ale pasului 2 (declaratii.js:525, 597/605, 601, 642)
        pg.wait_for_timeout(2500)
        titlu = _text(pg, ".rezumat-fix .mig-intro") or _text(pg)
        astept = "%s · %s %s" % (tip, luna_txt, an)
        if "Pasul 2 din 3" not in titlu or astept not in titlu:
            m = re.search(r"Pasul 2 din 3[^.]{0,80}", titlu)
            rele.append("pct.1 / 727.2 / e.%d: după clic pe «%s» și «Continuă», titlul pasului 2 nu numește «%s» (găsit: %r)" % (e_titlu, rand, astept, m.group(0) if m else titlu[:100]))


def _p2(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-inchidere", "#il-lock")
    _la_luna(pg, "il", 9, 2026)
    if not pg.locator(TOP + "#il-lock", has_text="Deblochează").count():
        rele.append("pct.2 / 729.1 / e.6: martorul lipsește: pe 09/2026 (blocată) nu e butonul «Deblochează luna» (text: %r)" % _text(pg, "#il-lock")[:80])
    else:
        pg.click(TOP + "#il-lock", timeout=10000)
        pg.wait_for_selector(TOP + "#bl-motiv", state="attached", timeout=20000)
        pg.wait_for_timeout(500)
        loc = pg.locator(TOP + "#bl-deblocheaza")
        active = sum(1 for i in range(loc.count()) if loc.nth(i).is_enabled())   # is_enabled: «disabled» și «aria-disabled» (mecanismul DS, api.js inactiv())
        if active:
            rele.append("pct.2 / 729.1 / e.6: cu motivul gol confirmarea «#bl-deblocheaza» e activă (așteptat: inactivă, 0 butoane active; găsit: %d)" % active)
    _card(pg, parcurs, F1, "#fa-inchidere", "#il-lock")
    _la_luna(pg, "il", 10, 2026)
    pg.wait_for_timeout(6000)   # controalele lunii se încarcă
    if "Se citesc controalele lunii" in _text(pg):
        rele.append("pct.2 / 763 / e.7: pe Închidere lună 10/2026, după încărcarea controalelor, pe ecran rămâne «Se citesc controalele lunii…» (așteptat: lipsește)")


def _p3(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-stocuri", "#sn-toggle")
    pg.wait_for_timeout(1500)
    if "Stoc validat 6.272,38 lei = balanța 371" not in _text(pg):
        rele.append("pct.5 / F089 / e.15: Stocuri nu spune «Stoc validat 6.272,38 lei = balanța 371» (găsit: %r)" % _text(pg)[:160])
    pg.click(TOP + "#sn-toggle", timeout=10000)
    pg.wait_for_selector(TOP + "#sn-numar", state="attached", timeout=20000)
    pg.wait_for_timeout(800)
    v = _valoare(pg, "#sn-numar")
    if v != "8":
        rele.append("pct.3 / 739 / e.8: numărul NIR din formularul «NIR nou» nu e propus (așteptat 8 = maximul 7 + 1 pe F1; găsit: %r)" % v)


def _p4(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-control", "#cf-incrucisat")
    pg.wait_for_timeout(2500)
    sel = pg.get_by_label("Luna comparată")
    if sel.count():   # selectorul nou: luna 10/2026 se alege explicit, deci proba nu depinde de data serverului
        sel.first.select_option(label="10/2026")
        pg.wait_for_timeout(2500)
    tot = _text(pg)
    incr = _text(pg, "#cf-incrucisat")
    if "Luna comparată" not in tot:
        rele.append("pct.4 / 484 / e.9: Control fiscal nu are selectorul de lună cu eticheta «Luna comparată» (azi compară numai luna curentă)")
    if "Diferență neexplicată: 1.341,00 lei" not in incr:
        rele.append("pct.4 / 484 / e.10: pe rândul contului 4423 nu e «Diferență neexplicată: 1.341,00 lei» (găsit în «Declarație vs contabilitate»: %r)" % incr[:200])
    if "D300 (decont TVA): Recalculul din documentele perioadei confirmă cifrele declarației generate." in incr:
        rele.append("pct.4 / 484 / e.11: la D300 apare «Recalculul din documentele perioadei confirmă cifrele» deși există diferență față de contabilitate (așteptat: lipsește)")
    if "Profilul firmei declară fără operațiuni intracomunitare, dar există facturi intracomunitare" in tot:
        rele.append("pct.4 / 484 / e.12: D390 apare și la «Nu se poate verifica» cu «Profilul firmei declară fără operațiuni intracomunitare, dar există facturi intracomunitare…», pe lângă «De urmărit» (așteptat: o singură dată, la «De urmărit»)")
    elif "operațiuni intracomunitare înregistrate în 10/2026; profilul firmei spune fără operațiuni intracomunitare — corectează în Date firmă" not in tot:
        rele.append("pct.4 / 484 / e.12: motivul D390 de la «De urmărit» nu conține nepotrivirea cu profilul (așteptat «operațiuni intracomunitare înregistrate în 10/2026; profilul firmei spune fără operațiuni intracomunitare — corectează în Date firmă»)")


def _p5(rele, pg, parcurs, memo):
    _card(pg, parcurs, F1, "#fa-verificari", ".vf-lista")
    _la_luna(pg, "vf", 10, 2026)
    pg.wait_for_timeout(2500)
    lista = _text(pg, ".vf-lista")
    if "contabil 6.272,38 vs fișe 9.524,29" in lista:
        rele.append("pct.5 / F089 / e.13: în Verificări comparația «contabil 6.272,38 vs fișe 9.524,29» încă produce diferență (așteptat: validat contra validat, ciornele nu mai produc «diferență»)")
    if "Ciorne de stoc: 3.251,90 lei" not in lista:
        rele.append("pct.5 / F089 / e.14: în Verificări nu e linia separată «Ciorne de stoc: 3.251,90 lei» (găsit în lista verificărilor: %r)" % lista[:200])
    t = _text(pg)
    m = re.search(r"Luna 10/2026 · (\d+) (?:de )?note(?! contabile)", t)
    if not m:
        g = re.search(r"Luna \d{2}/\d{4} · [^|]{0,40}", t)
        rele.append("pct.8 / 602.1 / e.19: antetul Verificărilor nu are forma Registrului jurnal «Luna 10/2026 · N de note» (găsit: %r; azi «N de note contabile»)" % (g.group(0) if g else "niciun antet de lună"))
    else:
        memo["verificari"] = m.group(1)


def _p7(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-clienti", "#cl-nou")
    if "+ Client nou" not in _text(pg):
        rele.append("paznic Clienți / e.16: fereastra Clienți nu are butonul «+ Client nou» (adăugarea de partener trebuie să fie în ecranul Clienți)")
    else:
        pg.click(TOP + "#cl-nou", timeout=10000)
        pg.wait_for_selector(TOP + "#cln-anaf", state="attached", timeout=20000)
        if "Verifică la ANAF" not in _text(pg):
            rele.append("paznic Clienți / e.17: formularul de adăugare din Clienți nu are «Verifică la ANAF»")
    _card(pg, parcurs, F1, "#fa-furnizori", "#fz-nou")
    if "+ Furnizor nou" not in _text(pg):
        rele.append("paznic Furnizori / e.18: fereastra Furnizori nu are butonul «+ Furnizor nou»")


def _p8(rele, pg, parcurs, memo):
    _card(pg, parcurs, F1, "#fa-jurnal", "#j-prev")
    _la_luna(pg, "j", 10, 2026)
    pg.wait_for_timeout(1500)
    m = re.search(r"Luna 10/2026 · (\d+) (?:de )?note\b", _text(pg))
    if not m:
        rele.append("pct.8 / 602.1 / e.20: antetul Registrului jurnal nu spune «Luna 10/2026 · N de note» (găsit: %r)" % _text(pg)[:120])
    else:
        memo["jurnal"] = m.group(1)
        # [17.5-T] actualizat la AC058 (core/uc_comun.py:1302): antetul Verificărilor numără NOTELE VALIDATE ale lunii («32 de note validate în lună»),
        # Registrul jurnal toate notele lunii (84 = 32 validate + 52 ciorne pe snapshot); fiecare citire se compară cu numărarea ei independentă din
        # tabela de note, pe aceeași firmă (F1, tenant_9049) și lună (10/2026), în locul egalității vechi dintre cele două antete
        luna_note = ("2026-10-01", "2026-11-01")
        total = sql('SELECT count(*) FROM tenant_9049.inregistrari WHERE data >= %s AND data < %s', luna_note)[0][0]
        validate = sql("SELECT count(*) FROM tenant_9049.inregistrari WHERE status = 'validata' AND data >= %s AND data < %s", luna_note)[0][0]
        if int(m.group(1)) != total:
            rele.append("pct.8 / 602.1 / e.20: antetul Registrului jurnal numără %s note, iar tabela de note are %s înregistrări în 10/2026 (așteptat: același număr)" % (m.group(1), total))
        if memo.get("verificari") and int(memo["verificari"]) != validate:
            rele.append("pct.8 / 602.1 / e.20: Verificările numără %s note validate, iar tabela de note are %s înregistrări validate în 10/2026 (așteptat: același număr)" % (memo["verificari"], validate))
    for sel in (".jn-lista :text('Stornare')", ".jn-lista :text('validată')"):   # rândurile se desfac (dacă au detalii)
        try:
            if pg.locator(TOP + sel).count():
                pg.click(TOP + sel, timeout=3000)
                pg.wait_for_timeout(800)
        except Exception:   # noqa: BLE001 — rândul nu se desface: textul se judecă pe ce e pe ecran
            pass
    if "Nota e deja validată: nu se mai validează." not in _text(pg):
        rele.append("pct.8 / 602.1 / e.21: pe nota validată nu e scris motivul «Nota e deja validată: nu se mai validează.» (butonul «Validează» e inactiv, dar cu alt text)")
    _card(pg, parcurs, F1, "#fa-jurnal", "#j-prev")
    _la_luna(pg, "j", 9, 2026)
    pg.click(TOP + "#j-nota-noua", timeout=10000)
    pg.wait_for_selector(TOP + "#je-data", state="attached", timeout=20000)
    pg.wait_for_timeout(800)
    v = _valoare(pg, "#je-data")
    if v != "2026-10-31":
        rele.append("pct.8 / 781 / e.22: nota nouă pe luna blocată 09/2026 propune data %r (așteptat 2026-10-31, ultima zi a ultimei luni deschise)" % v)
    if "Luna 09/2026 e blocată: s-a propus 31.10.2026, ultima zi a ultimei luni deschise." not in _text(pg):
        rele.append("pct.8 / 781 / e.23: lângă data notei lipsește textul «Luna 09/2026 e blocată: s-a propus 31.10.2026, ultima zi a ultimei luni deschise.»")


def _p9(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-casa", "#c-tabel")
    _la_luna(pg, "c", 10, 2026)
    pg.wait_for_timeout(1200)
    tabel = _text(pg, "#c-tabel")
    if "Casa rămâne pe minus (−58,00 lei)" not in tabel:
        rele.append("pct.9 / F015 / e.24: pe rândul cu sold negativ din registrul de casă 10/2026 nu e semnalul «Casa rămâne pe minus (−58,00 lei)» (găsit în tabel: %r)" % tabel[:160])


def test_pilot_17_5_X(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    memo = {}   # numerele din cele două antete, comparate între ele (e.20)
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _sectiune(rele, "P1 Declarații pasul 1 (727.2)", _p1, pg, parcurs)
        _sectiune(rele, "P2 Închidere lună (729.1, 763)", _p2, pg, parcurs)
        _sectiune(rele, "P3 Stocuri și NIR nou (739, F089)", _p3, pg, parcurs)
        _sectiune(rele, "P4 Control fiscal (484)", _p4, pg, parcurs)
        _sectiune(rele, "P5 Verificări (F089, 602.1)", _p5, pg, parcurs, memo)
        _sectiune(rele, "P7 Clienți și Furnizori (640.1, 633.1)", _p7, pg, parcurs)
        _sectiune(rele, "P8 Registru jurnal (602.1, 781)", _p8, pg, parcurs, memo)
        _sectiune(rele, "P9 Casă (F015)", _p9, pg, parcurs)
    finally:
        b.close()
    assert not rele, "lotul 17.5-X, proba arhitectului: " + "; ".join(rele)
