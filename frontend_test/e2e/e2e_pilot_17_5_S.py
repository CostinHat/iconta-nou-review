# -*- coding: utf-8 -*-
"""POZIȚII PILOT DESCHISE PE ECRAN — lotul 17.5-S (constatările S01–S06, S09–S14 din constatari_S_cercetare.txt și «De ce» din comanda_17_5_S.txt).
Scris de arhitect (redactor); Code nu îl modifică. Probă pe bază: pică; pe C: trece. S07 (619) și S08 (609) sunt stări din date, nu cod: nu au aserțiune aici.

La 1366×768 (S14 la 643×590), ceas înghețat 03.11.2026, cu contul administratorului (dovada.71507), baza de test restaurată din snapshot. Fiecare mesaj de eșec începe cu id-ul S.. și cu id-ul e.N al testului
(distinct de ids din oracolul pasi_17_5_S), urmat de martorul de pe snapshot. Numai citire: nu salvează, nu depune, nu adaugă nimic.
  e.1  S01: «De validat»: tabelul notelor de validat are coloana «Pregătit de» (și «Notele tale în ciornă» nu o primește);
  e.2  S02: «Mișcări, fișe de magazie»: fără tabel cu înregistrări, bara de jos NU are butonul «Descarcă PDF» (nici activ, nici inactiv);
  e.3  S03: fișa partenerului DANTE: o casetă «Fișa de client și de furnizor: …», adresa o singură dată;
  e.4  S04: clopoțelul: insigna e vizibilă (necitite + de validat) și panoul are rândul cu notele de validat;
  e.5  S05: Scadențar: numărul din pastila «fără scadență» = numărul rândurilor «fără scadență în sistem» din listă;
  e.6  S06: stat de plată (F5): coloanele «Brut salarial» și «Diurnă peste plafon»; Ionescu: 4.815,34 și 885,00;
  e.7  S09: Control fiscal pe F2: eticheta «D205» nu mai e dublată în semnal;
  e.8  S10: fișa articolului arată «sold inițial (import)» (cheia din baza de date rămâne «sold initial (import)»);
  e.9  S11: Registrul jurnal 10/2026: nota Z-0050 apare ca «Vânzări din raportul Z nr 0050 din 22.10.2026, casa 8000000001», fără data ISO, iar în baza de date textul rămâne cel scris;
  e.10 S12: Bancă: fiecare buton inactiv din rândurile liniilor are motivul scris pe ecran, nu numai în title;
  e.11 S13: Emite factură pe FISCALOS ICONTA: cardul numește de la început capitalul social, regimul fiscal și operațiunile intracomunitare, iar «Date firmă» deschisă din «Deschide Date firmă» arată de la deschidere mesajele regimului și operațiunilor;
  e.12 S14: Emite factură pe F1 la 643×590: niciun text mai lat decât elementul lui, cotele pe un singur rând, textul de îndrumare al căutării încape, «buc» are margine.
Un singur test."""
import importlib.util
import os
import sys

from conftest import BAZA, sesiune, sql

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1, F2, F5, FISCALOS = "F1 Comert Stoc", "F2 Profit Amortizare", "F5", "FISCALOS"
SCHEMA = "tenant_9049"
TOP = ".fereastra-overlay:not(.fundal) "
T_FISA = "Fișa de client și de furnizor: DANTE INTERNATIONAL SA"
T_Z50 = "Vânzări din raportul Z nr 0050 din 22.10.2026, casa 8000000001"
T_PREG = "La salvarea în Date firmă se cer și: regimul fiscal (micro sau profit), operațiunile intracomunitare (Da sau Nu)."

ASISTENT = "dovada.71508@sesiuneab.test"   # Ana Asistent: nu validează, deci notele ei intră în coada de validare a administratorului
MARTOR_DESC = "Martor 17.5-S: nota pregătită de asistent"


_PESTE_COADA = None


def _pune_martor_coada():
    """Baza restaurată nu are nicio notă în «De validat» (S01, S04 n-ar avea ce afișa). Martorul: o notă-ciornă a asistentului Ana pe F1,
    pusă în coadă cu funcția aplicației (`coada_api.pune_notele_in_coada`: pune în coadă toate ciornele lui Ana, deci și cele 7 deja existente
    pe F1), apoi ștearsă în `_scoate_martor_coada` împreună cu elementele de coadă create acum (id peste `_PESTE_COADA`). -> id-ul notei."""
    from core import coada_api, db
    uid = sql("SELECT id FROM public.users WHERE email = %s", (ASISTENT,))[0][0]
    tid, cab = sql("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name = %s", (SCHEMA,))[0]
    _scoate_martor_coada()
    global _PESTE_COADA
    _PESTE_COADA = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    nid = sql("INSERT INTO %s.inregistrari (data, descriere, sursa, status, creat_de_id) VALUES ('2026-11-02', %%s, 'manual', 'ciorna', %%s) RETURNING id" % SCHEMA,
              (MARTOR_DESC, uid))[0][0]
    sql("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, '5311', '7588', 10.00)" % SCHEMA, (nid,))
    with db.get_conn(SCHEMA) as c:
        coada_api.pune_notele_in_coada(c, cab, tid, uid)
        c.commit()
    if not sql("SELECT 1 FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND stare = 'la_senior' AND perioada = %s",
               (tid, "nota-%d" % nid)):
        raise AssertionError("martorul nu a intrat în coadă")
    return nid


SERIE_MARTOR = "MARTOR17S-"


def _schema_fiscalos():
    return sql("SELECT schema_name FROM public.tenants WHERE nume ILIKE %s ORDER BY id LIMIT 1", (FISCALOS + "%",))[0][0]


def _pune_martor_fiscalos():
    """FISCALOS n-a emis niciodată: «Emite factură» deschide întâi «Configurare emitere» (emitere_ecran.js:46–49), iar formularul cu cardul
    «Înainte de a emite» (:556) apare numai după ea. Martorul: numerotarea marcată ca făcută (serie de probă), ștearsă în `_scoate_martor_fiscalos`;
    capitalul, regimul și operațiunile lui FISCALOS rămân necompletate (de ele depinde cardul)."""
    sql('UPDATE "%s".firma_profil SET serie_factura = %%s, urmator_numar_factura = 1, numerotare_configurata = true '
        "WHERE COALESCE(serie_factura, '') = '' AND numerotare_configurata = false" % _schema_fiscalos(), (SERIE_MARTOR,))
    if not sql('SELECT 1 FROM "%s".firma_profil WHERE serie_factura = %%s' % _schema_fiscalos(), (SERIE_MARTOR,)):
        raise AssertionError("FISCALOS are deja numerotarea configurată: martorul nu mai e necesar, dar nici starea așteptată nu e")


def _scoate_martor_fiscalos():
    sql('UPDATE "%s".firma_profil SET serie_factura = NULL, urmator_numar_factura = 1, numerotare_configurata = false WHERE serie_factura = %%s'
        % _schema_fiscalos(), (SERIE_MARTOR,))


def _scoate_martor_coada():
    """Curăță martorul (și orice rest al unei rulări întrerupte)."""
    if _PESTE_COADA is not None:
        sql("DELETE FROM public.declaratii_coada WHERE id > %s AND fel = 'nota' AND creat_de = (SELECT id::text FROM public.users WHERE email = %s)",
            (_PESTE_COADA, ASISTENT))
    for (nid,) in sql("SELECT id FROM %s.inregistrari WHERE descriere = %%s" % SCHEMA, (MARTOR_DESC,)) or []:
        sql("DELETE FROM public.declaratii_coada WHERE fel = 'nota' AND perioada = %s", ("nota-%d" % nid,))
        sql("DELETE FROM %s.inregistrari WHERE id = %%s" % SCHEMA, (nid,))


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _norm(t):
    return " ".join(str(t or "").split())


def _api(pg, cale, metoda="GET", corp=None):
    """Cerere către server cu sesiunea paginii; -> (status, json)."""
    return pg.evaluate("""async ([c, m, b]) => { const t = sessionStorage.getItem('iconta_token');
      const r = await fetch(c, { method: m, headers: Object.assign({ 'Authorization': 'Bearer ' + t }, b ? { 'Content-Type': 'application/json' } : {}), body: b ? JSON.stringify(b) : undefined });
      let j = null; try { j = await r.json(); } catch (e) {} return [r.status, j]; }""", [cale, metoda, corp])


def _sectiune(rele, nume, fn, *argumente):
    """O secțiune care aruncă excepție nu oprește celelalte: eșecul ei intră în listă."""
    try:
        fn(rele, *argumente)
    except Exception as e:   # noqa: BLE001
        rele.append("%s: secțiunea a căzut (%s: %s)" % (nume, type(e).__name__, str(e)[:200]))


def _acasa(pg):
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(BAZA + "/", wait_until="load", timeout=30000)
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    pg.wait_for_timeout(1500)


def _card(pg, parcurs, firma, id_card, asteapta):
    """Firma `firma` › cardul `id_card` › așteaptă `asteapta`."""
    parcurs.firma(pg, firma)
    # grupurile ferestrei firmei se deschid toate (implicit numai «Zi de zi», static/js/ecrane/firme.js:473–477), ca în parcurs_17_5_S.firma
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_timeout(400)
    pg.click(TOP + "#" + id_card, timeout=10000)
    pg.wait_for_selector(TOP + asteapta, state="attached", timeout=40000)
    pg.wait_for_timeout(1500)


def _text(pg, sel):
    return _norm(pg.inner_text(TOP + sel)) if pg.locator(TOP + sel).count() else ""


def _validat(rele, pg):
    _acasa(pg)
    pg.click("button.cab-card:has([data-cheie='validat'])", timeout=10000)
    pg.wait_for_selector("#val-note", state="attached", timeout=40000)
    pg.wait_for_timeout(1500)
    antete = pg.evaluate("() => [...document.querySelectorAll('#val-note thead th')].map((t) => t.textContent.trim())")
    if "Pregătit de" not in antete:
        rele.append("S01 / e.1: tabelul «Note de validat» nu are coloana «Pregătit de» (antete: %s)" % antete)
    antete_c = pg.evaluate("() => [...document.querySelectorAll('#val-ciorne thead th')].map((t) => t.textContent.trim())")
    if "Pregătit de" in antete_c:
        rele.append("S01 / e.1: «Notele tale în ciornă» a primit coloana «Pregătit de» (nu trebuie: coloana e numai la notele de validat)")
    celule = pg.evaluate("""() => { const t = document.querySelector('#val-note'); if (!t) return [];
      const i = [...t.querySelectorAll('thead th')].findIndex((h) => h.textContent.trim() === 'Pregătit de'); if (i < 0) return [];
      return [...t.querySelectorAll('tbody.tn-nota')].map((b) => (b.querySelector('tr').children[i] || {}).textContent || '').map((x) => x.trim()); }""")
    if celule and any(not c for c in celule):
        rele.append("S01 / e.1: rânduri cu «Pregătit de» gol (se scrie «—» când numele lipsește): %s" % celule)


def _miscari(rele, pg, parcurs):
    _card(pg, parcurs, F1, "fa-stocuri", "#cv-toggle")
    pg.click(TOP + "#cv-toggle", timeout=10000)
    pg.wait_for_timeout(2500)
    bara = TOP + ".fereastra .fj-butoane"
    tabele = pg.locator(TOP + ".fereastra table tbody tr").count()
    text_bara = _norm(pg.inner_text(bara)) if pg.locator(bara).count() else ""
    if not tabele and "Descarcă PDF" in text_bara:
        rele.append("S02 / e.2: fereastra «Mișcări…» nu are tabel cu înregistrări, iar bara ei are încă «Descarcă PDF» (bara: %s)" % text_bara[:120])


def _fisa_partener(rele, pg, parcurs):
    _card(pg, parcurs, F1, "fa-parteneri", "#pt-rezumat")
    pg.locator(TOP + "tr", has_text="DANTE").locator(".pt-deschide").first.click(timeout=10000)
    pg.wait_for_timeout(2500)
    t = _text(pg, ".fereastra")
    if T_FISA not in t:
        rele.append("S03 / e.3: fișa lui DANTE nu are caseta «%s»" % T_FISA)
    # numai zona de date (antetul și «Datele partenerului»), până la «Soldul din contabilitate»: mai jos, descrierile liniilor de bancă ale lui DANTE
    # conțin ele însele «CUI 14399840» (de 3 ori pe F1), așa că numărătoarea pe toată fișa ar pica și după reparație
    zona = t.split("Soldul din contabilitate")[0]
    if "Soldul din contabilitate" not in t:
        rele.append("S03 / e.3: fișa lui DANTE nu are secțiunea «Soldul din contabilitate» (fișa nu s-a deschis cum trebuie)")
    if zona.count("Sector 2") > 1 or zona.count("14399840") > 2:
        rele.append("S03 / e.3: adresa/codul fiscal al lui DANTE apar de mai multe ori în fișă (Sector 2: %d, cod fiscal: %d)" % (zona.count("Sector 2"), zona.count("14399840")))


def _clopot(rele, pg):
    _acasa(pg)
    insigna = pg.evaluate("() => { const b = document.querySelector('#nav-clopot-badge'); return b ? [getComputedStyle(b).display, b.textContent.trim()] : null; }")
    if not insigna or insigna[0] == "none" or not insigna[1]:
        rele.append("S04 / e.4: insigna clopoțelului nu e vizibilă cu notele de validat în coadă (insigna: %s)" % (insigna,))
    pg.click("#nav-clopot", timeout=10000)
    pg.wait_for_selector("#nav-clopot-panou", timeout=10000)
    pg.wait_for_timeout(1500)
    t = _norm(pg.inner_text("#nav-clopot-panou"))
    if "deschide fereastra „De validat”" not in t:
        rele.append("S04 / e.4: panoul clopoțelului nu are rândul «N note de validat — deschide fereastra „De validat”» (text: %s)" % t[:200])


def _scadentar(rele, pg, parcurs):
    _card(pg, parcurs, F1, "fa-facturi", "#fac-scadentar")
    pg.click(TOP + "#fac-scadentar", timeout=10000)
    pg.wait_for_selector(TOP + "#sc-lista", state="attached", timeout=30000)
    pg.wait_for_timeout(1500)
    import re
    sumar = _text(pg, ".cf-sumar")
    m = re.search(r"(\d+)\s+fără scadență", sumar)
    n_lista = _text(pg, "#sc-lista").count("fără scadență în sistem")
    if not m:
        rele.append("S05 / e.5: sumarul Scadențarului nu are pastila «N fără scadență» (sumar: %s)" % sumar[:200])
    elif int(m.group(1)) != n_lista:
        rele.append("S05 / e.5: pastila spune %s fără scadență, lista are %d rânduri «fără scadență în sistem»" % (m.group(1), n_lista))


def _stat(rele, pg, parcurs):
    _card(pg, parcurs, F5, "fa-salariati", "#sp-tabel")
    # luna cu diurna peste plafon a lui Ionescu e 10/2026 (public/tenant_9053.diurna_excedent, 885,00): se merge la ea după etichetă, nu după valorile
    # lotului (pe baza fără reparație ele lipsesc, iar căutarea după ele ar fi trecut de lună și ar fi pierdut martorul)
    import re
    for _ in range(8):
        m = re.search(r"Luna (\d+)/(\d+)", _text(pg, ".rezumat-fix"))
        if m and (int(m.group(1)), int(m.group(2))) == (10, 2026):
            break
        pg.click(TOP + ("#sp-prev" if not m or (int(m.group(2)), int(m.group(1))) > (2026, 10) else "#sp-next"), timeout=10000)
        pg.wait_for_timeout(1500)
    else:
        rele.append("S06 / e.6: martorul lipsește: statul lunii 10/2026 nu s-a putut deschide pe F5")
    antete = pg.evaluate("(s) => [...document.querySelectorAll(s + ' #sp-tabel thead th')].map((t) => t.textContent.trim())", TOP.strip())
    for a in ("Brut salarial", "Diurnă peste plafon"):
        if a not in antete:
            rele.append("S06 / e.6: statul nu are coloana «%s» (antete: %s)" % (a, antete))
    rand = pg.locator(TOP + "#sp-tabel tbody tr", has_text="Ionescu").first
    t = _norm(rand.inner_text()) if rand.count() else ""
    for v in ("4.815,34", "885,00"):
        if v not in t:
            rele.append("S06 / e.6: rândul lui Ionescu nu conține %s (rând: %s)" % (v, t[:200]))


def _control_f2(rele, pg, parcurs):
    _card(pg, parcurs, F2, "fa-control", "#cf-incrucisat")
    t = _text(pg, ".fereastra")
    if "D205 — D205" in t or "D205 - D205" in t:
        rele.append("S09 / e.7: semnalul D205 are eticheta dublată")


def _sold_initial(rele, pg):
    # S10: cheia din baza de date rămâne neschimbată; afișarea (fișa articolului) o arată cu diacritice
    n = sql("SELECT count(*) FROM %s.miscari_stoc WHERE document = 'sold initial (import)'" % SCHEMA)[0][0]
    if n < 1:
        rele.append("S10 / e.8: martorul lipsește: nicio mișcare cu cheia «sold initial (import)» în %s" % SCHEMA)
    cod = ""
    for f in ("static/js/ecrane/firme.js",):
        cod += open(os.path.join(RAD, f), encoding="utf-8").read()
    if "sold inițial (import)" not in cod:
        rele.append("S10 / e.8: afișarea fișei de magazie nu are transformarea «sold initial (import)» → «sold inițial (import)» în static/js/ecrane/firme.js")


def _z0050(rele, pg):
    _acasa(pg)
    st, j = _api(pg, "/tenants/105779/jurnal?an=2026&luna=10")
    import json
    t = json.dumps(j, ensure_ascii=False) if st == 200 else ""
    if st != 200:
        rele.append("S11 / e.9: GET jurnal 10/2026 a dat %s" % st)
        return
    if T_Z50 not in t:
        rele.append("S11 / e.9: Registrul jurnal 10/2026 nu arată «%s»" % T_Z50)
    if "Raport Z 2026-10-22" in t:
        rele.append("S11 / e.9: Registrul jurnal 10/2026 arată încă «Raport Z 2026-10-22 …» (data ISO)")
    ds = sql("SELECT descriere FROM %s.inregistrari WHERE numar = 'Z-8000000001-0050'" % SCHEMA)
    if not ds or "Raport Z 2026-10-22" not in ds[0][0]:
        rele.append("S11 / e.9: textul din baza de date al notei Z-0050 s-a schimbat (nota validată nu se rescrie): %s" % ds)


def _banca(rele, pg, parcurs):
    _card(pg, parcurs, F1, "fa-banca", "#bk-fisier")
    gasite = []
    for _ in range(3):
        gasite = pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #bk-lista tbody.tn-nota .tn-actiuni button')]
          .filter((b) => b.disabled || b.getAttribute('aria-disabled') === 'true')
          .map((b) => { const motiv = b.getAttribute('data-motiv-inactiv') || b.title || ''; const celula = b.closest('.tn-actiuni');
            return [b.textContent.trim(), motiv, (celula ? celula.innerText : '')]; })""")
        if gasite:
            break
        if pg.locator(TOP + "#bk-prev").count():
            pg.click(TOP + "#bk-prev", timeout=10000)
            pg.wait_for_timeout(1500)
        else:
            break
    if not gasite:
        rele.append("S12 / e.10: martorul lipsește: niciun buton inactiv în rândurile liniilor băncii pe F1 (luna afișată și cele două dinainte)")
    for eticheta, motiv, celula in gasite:
        if motiv and _norm(motiv) not in _norm(celula):
            rele.append("S12 / e.10: butonul «%s» inactiv are motivul «%s» numai în title, nu scris în celulă" % (eticheta, motiv[:80]))
            break


def _emitere_fiscalos(rele, pg, parcurs):
    _card(pg, parcurs, FISCALOS, "fa-facturi", "#fac-emite")
    pg.click(TOP + "#fac-emite", timeout=10000)
    pg.wait_for_selector("#em-cui", state="attached", timeout=30000)
    pg.wait_for_timeout(1500)
    t = _text(pg, ".fereastra")
    if T_PREG not in t:
        rele.append("S13 / e.11: cardul «Înainte de a emite» nu spune de la început «%s» (text: %s)" % (T_PREG, t[:300]))
    pg.locator(TOP + "button", has_text="Deschide Date firmă").first.click(timeout=10000)
    pg.wait_for_timeout(2500)
    # textContent, nu text vizibil: Date firmă se deschide pe fila câmpului lipsă (capitalul social, «Bilanț»), iar mesajele regimului și ale
    # operațiunilor pot sta în alte file; la deschidere ele trebuie să fie în pagină (pe baza de azi nu sunt nicăieri în ea)
    t2 = _norm(pg.evaluate("() => { const f = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); return f ? f.textContent : ''; }"))
    for m in ("Alege regimul fiscal (micro sau profit)", "Alege dacă firma are operațiuni intracomunitare"):
        if m not in t2:
            rele.append("S13 / e.11: «Date firmă» deschisă din card nu arată de la deschidere mesajul «%s…»" % m)


def _ingust_f1(rele, b, parcurs):
    pg = b.new_page()
    pg.set_viewport_size({"width": 643, "height": 590})
    try:
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _card(pg, parcurs, F1, "fa-facturi", "#fac-emite")
        pg.click(TOP + "#fac-emite", timeout=10000)
        pg.wait_for_selector("#em-cui", state="attached", timeout=30000)
        pg.wait_for_timeout(1500)
        masuri = pg.evaluate("""() => {
          const out = { taiate: [], cote_rupte: [], cauta: null, um: null };
          const R = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra');
          R.querySelectorAll('.alegere-butoane > button, .em-linie button').forEach((b) => { if (b.scrollWidth > b.clientWidth + 1) out.taiate.push([b.textContent.trim(), b.scrollWidth, b.clientWidth]); });
          R.querySelectorAll('.em-linie .alegere-butoane').forEach((g) => { const t = new Set([...g.querySelectorAll('button')].map((b) => Math.round(b.getBoundingClientRect().top))); if (t.size > 1) out.cote_rupte.push([g.textContent.trim().slice(0, 40), [...t]]); });
          const c = R.querySelector('.em-l-cauta-articol');
          if (c) { const s = getComputedStyle(c); const cv = document.createElement('canvas').getContext('2d'); cv.font = s.fontStyle + ' ' + s.fontWeight + ' ' + s.fontSize + ' ' + s.fontFamily;
            out.cauta = [Math.ceil(cv.measureText(c.placeholder).width), c.clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight), c.placeholder]; }
          const u = R.querySelector('.em-l-um');
          if (u) { const s = getComputedStyle(u); const cv = document.createElement('canvas').getContext('2d'); cv.font = s.fontStyle + ' ' + s.fontWeight + ' ' + s.fontSize + ' ' + s.fontFamily;
            out.um = [Math.ceil(cv.measureText(u.value || 'buc').width), u.clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight)]; }
          return out; }""")
        if masuri["taiate"]:
            rele.append("S14 / e.12: la 643×590 texte mai late decât butonul lor (text, scrollWidth, clientWidth): %s" % masuri["taiate"])
        if masuri["cote_rupte"]:
            rele.append("S14 / e.12: la 643×590 un grup de butoane se rupe pe mai multe rânduri: %s" % masuri["cote_rupte"])
        if masuri["cauta"] is None:
            rele.append("S14 / e.12: câmpul «Caută articolul în stoc» (.em-l-cauta-articol) lipsește pe linia de factură a firmei F1")
        elif masuri["cauta"][0] > masuri["cauta"][1]:
            rele.append("S14 / e.12: textul de îndrumare al căutării (%d px) nu încape în câmp (%d px): %r" % (masuri["cauta"][0], masuri["cauta"][1], masuri["cauta"][2]))
        if masuri["um"] is None:
            rele.append("S14 / e.12: câmpul UM (.em-l-um) lipsește")
        elif masuri["um"][1] - masuri["um"][0] < 8:
            rele.append("S14 / e.12: «buc» are margine de %d px în câmpul UM (cel puțin 8 px: text %d px, loc %d px)" % (masuri["um"][1] - masuri["um"][0], masuri["um"][0], masuri["um"][1]))
    finally:
        pg.close()


def test_pozitii_pilot_17_5_S(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        _pune_martor_coada()
        _pune_martor_fiscalos()
    except Exception as e:   # noqa: BLE001
        rele.append("martorul «notă în coadă» nu s-a putut pune (%s: %s)" % (type(e).__name__, str(e)[:200]))
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _sectiune(rele, "De validat (S01)", _validat, pg)
        _sectiune(rele, "Mișcări (S02)", _miscari, pg, parcurs)
        _sectiune(rele, "Fișa partenerului (S03)", _fisa_partener, pg, parcurs)
        _sectiune(rele, "Clopoțelul (S04)", _clopot, pg)
        _sectiune(rele, "Scadențar (S05)", _scadentar, pg, parcurs)
        _sectiune(rele, "Stat de plată (S06)", _stat, pg, parcurs)
        _sectiune(rele, "Control fiscal F2 (S09)", _control_f2, pg, parcurs)
        _sectiune(rele, "Sold inițial (S10)", _sold_initial, pg)
        _sectiune(rele, "Raport Z 0050 (S11)", _z0050, pg)
        _sectiune(rele, "Bancă (S12)", _banca, pg, parcurs)
        _sectiune(rele, "Emite factură, firmă nouă (S13)", _emitere_fiscalos, pg, parcurs)
        _sectiune(rele, "Emite factură la 643×590 (S14)", _ingust_f1, b, parcurs)
    finally:
        b.close()
        _scoate_martor_coada()
        _scoate_martor_fiscalos()
    assert not rele, "poziții Pilot 17.5-S: " + "; ".join(rele)
