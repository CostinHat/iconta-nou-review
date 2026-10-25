# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 (verbatim în `~/ghid_incoming/comanda_12_2.txt`), pachetul `ui2` — ecranele contabilului, de capăt la
capăt, pe aplicația din index, pe baza de TEST, pe o firmă nouă a fișierului (`firma_e2e`).

  * 617 (pct.9): „Registru jurnal: fără căutare. Un câmp (cont, document, partener, sumă, nr. crt.) și filtru de stare; tabel cu un rând pe
    notă, detaliul la clic, explicațiile o singură dată. După «Validează» pagina sare sus fără confirmare.”
  * 622 (pct.12): „De validat: trei forme diferite, note afișate de două ori. Trei secțiuni cu număr, același tabel ca la 617,
    Validează/Respinge pe rând, căutare.”
  * 621 (pct.11): „Balanța: casetele de sus ocupă jumătate din fereastră, se văd 2–3 rânduri de tabel; caseta «Importă…» nu are buton spre
    import.”
  * 459.1 (pct.5): „la schimbarea CUI-ului denumirea adusă de la CUI-ul anterior (DANTE INTERNATIONAL SA) rămâne completată. Tot aici:
    textul «— verifică.» după denumire.”

DATE DE PORNIRE fără ecran (declarate): notele lunii se scriu pe drumul Registrului jurnal (`jurnal_api.creeaza` / `valideaza`, ca
`e2e_bloc_e._nota`); nota asistentei, din ecranul ei (`e2e_bloc_b._nota_prin_ecran`); balanța de deschidere fără rulaje, ca la 425
(`e2e_lot10_balanta`); răspunsul ANAF e al plasei (`ICONTA_ANAF_SIMULAT`). CUI-uri: `cui_cu_control` (cifra de control calculată).

Temei: N/A — reguli de interfață (DS cap.9 v2.102 „Tabelul de note”, „Rezumatul nu mănâncă tabelul”, „După o acțiune pe un rând”; DS cap.6
v2.102 „Datele aduse de la ANAF țin de CUI-ul lor”; CLAUDE.md §9)."""
import datetime as _dt
import time as _t

import pytest

from conftest import cui_cu_control, sql
from e2e_bloc_a import _api, _deschide_firme, _ok
from e2e_bloc_b import _de_validat, _jurnal, _nota_prin_ecran, ana, ana_cont  # noqa: F401 — fixture (ana, ana_cont)
from e2e_bloc_e import _balanta, _nota
from e2e_lot10_balanta import AN, _scrie_balanta, firma_preluata  # noqa: F401 — fixture (firma_preluata)
from e2e_lot11_a459 import _anaf_pune, _anaf_scoate
from e2e_lot81 import _cont

AZI = _dt.date.today()
LUNA = (AZI.year, AZI.month)
_CORP = "() => [...document.querySelectorAll('.fereastra-corp')].pop()"


def _tag():
    return int(_t.time() * 1000) % 1000000


def _linii(suma, deb="627", cre="5121"):
    return [{"debit": deb, "credit": cre, "suma": str(suma)}]


# ── 617 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_617_registrul_jurnal_tabel_cautare_detaliu_si_validare_pe_loc(patron, firma_e2e):
    """617. Pașii: luna curentă cu 25 de note validate (627 = 5121), o ciornă cu document și una fără document -> Registru jurnal: un tabel,
    un rând pe notă, detaliile închise; explicația notei fără document o dată, deasupra tabelului -> clic pe rândul ciornei: liniile ei
    -> căutarea „5121” / suma ciornei / starea „Ciorne” -> fereastra derulată la ciornă -> „Validează”: fereastra rămâne unde era, rândul
    spune „Validată”, iar sus „Ai validat nota nr. crt. …”."""
    tag = _tag()
    zi = AZI.replace(day=min(AZI.day, 20)).isoformat()
    ids = [_nota(firma_e2e, zi, _linii(10 + i), "E2E 617 validată %d-%d" % (tag, i), valideaza=True) for i in range(25)]
    cu_doc = _nota(firma_e2e, zi, _linii("617.17"), "E2E 617 ciornă cu document %d" % tag)
    fara_doc = _nota(firma_e2e, zi, _linii("61.70"), "E2E 617 ciornă fără document %d" % tag, document_ref=None)
    pg = patron.pg
    _jurnal(patron, firma_e2e, LUNA)
    pg.wait_for_selector("table.tn-tabel tbody[data-nota-id='%d']" % cu_doc, timeout=30000)
    patron.captura("tabelul_notelor")
    m = pg.evaluate("""(ids) => { const c = (%s)();
      const tb = [...c.querySelectorAll('table.tn-tabel > tbody[data-nota-id]')];
      return {randuri: tb.filter((t) => ids.includes(Number(t.dataset.notaId))).map((t) => t.querySelectorAll(':scope > tr.tn-rand').length),
              deschise: tb.filter((t) => !t.querySelector('.tn-detaliu').hidden).length,
              explicatie: (c.innerText.match(/nu se validează fără documentul din care provine/g) || []).length}; }""" % _CORP,
                    ids + [cu_doc, fara_doc])
    assert m["randuri"] == [1] * 27, m                     # „tabel cu un rând pe notă”
    assert m["deschise"] == 0, m                           # „detaliul la clic”
    assert m["explicatie"] == 1, m                         # „explicațiile o singură dată”
    assert pg.is_disabled("[data-val='%d']" % fara_doc)
    pg.click("tbody[data-nota-id='%d'] .tn-deschide" % cu_doc)
    pg.wait_for_selector("#jn-det-%d" % cu_doc, state="visible", timeout=5000)
    celule = pg.evaluate("(i) => [...document.querySelectorAll('#jn-det-' + i + ' table.tn-linii tbody tr')].map((r) => [...r.cells].map((c) => c.textContent.trim()))",
                         cu_doc)
    assert celule == [["627", "5121", "617,17"]], celule
    patron.captura("detaliul_notei")
    vazute = lambda: pg.evaluate("() => [...(%s)().querySelectorAll('tbody[data-nota-id]')].filter((t) => !t.hidden).map((t) => Number(t.dataset.notaId))" % _CORP)
    pg.fill("#jn-cauta", "617,17")                                    # „sumă”
    pg.wait_for_timeout(200)
    assert vazute() == [cu_doc], vazute()
    pg.fill("#jn-cauta", "")
    pg.select_option("#jn-stare", "fara_doc")                         # „filtru de stare”
    pg.wait_for_timeout(200)
    assert fara_doc in vazute() and cu_doc not in vazute(), vazute()
    patron.captura("filtrul_fara_document")
    pg.select_option("#jn-stare", "")
    pg.wait_for_timeout(200)
    inainte = pg.evaluate("""(i) => { const c = (%s)(), r = c.querySelector("tbody[data-nota-id='" + i + "']");
      c.scrollTop += r.getBoundingClientRect().top - c.getBoundingClientRect().top - c.clientHeight / 2; return c.scrollTop; }""" % _CORP, cu_doc)
    pg.evaluate("(i) => document.querySelector(\"[data-val='\" + i + \"']\").click()", cu_doc)
    pg.wait_for_function("() => ((document.querySelector('#j-mesaj') || {}).textContent || '').startsWith('Ai validat nota nr. crt.')", timeout=30000)
    m = pg.evaluate("""(i) => { const c = (%s)(), r = c.querySelector("tbody[data-nota-id='" + i + "']");
      return {sus: c.scrollTop, stare: r.querySelector('.tn-rand td:nth-child(7)').innerText.trim()}; }""" % _CORP, cu_doc)
    patron.captura("dupa_valideaza")
    assert abs(m["sus"] - inainte) <= 40, (inainte, m)               # „pagina sare sus” -> rămâne pe loc
    assert m["stare"].startswith("● Validată"), m
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % firma_e2e["schema"], (cu_doc,)) == [("validata",)]


# ── 622 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _titluri(e):
    return e.pg.evaluate("() => [...(%s)().querySelectorAll('section > .cf-grup-titlu')].map((x) => x.textContent)" % _CORP)


def test_def_622_de_validat_trei_sectiuni_un_tabel_nota_o_data_si_cautare(ana, patron, firma_e2e, browser, request, ana_cont):
    """622. Pașii: Ana („Poate pregăti”) scrie o notă (intră la validare) -> Ana primește și „Poate valida” și intră din nou -> „De
    validat”: trei secțiuni cu număr; nota ei apare O DATĂ (în „Note de validat”, nu și în „Notele tale în ciornă”) -> contabilul-șef:
    „De validat”: aceeași formă (tabelul Registrului jurnal), „Validează” / „Respinge” pe rândul notei Anei; căutarea după descriere lasă
    numai rândul ei -> „Validează”: confirmarea sus, nota a intrat în evidență.
    [triajul plasei 1, 12.2] Ana „Poate pregăti” n-are cardul „De validat” (`asistent.js`: `cere: "poate_valida"`), iar nota unui
    validator nu intră în coadă (`coada_api.e_validator`): ciorna proprie trimisă la validare ajunge în „De validat” al autorului numai
    când autorul a primit dreptul de validare DUPĂ ce nota a plecat — cazul de mai jos. Drepturile se citesc la intrare (sesiunea), deci
    Ana intră din nou; la final își recapătă drepturile de dinainte."""
    desc = "E2E 622 servicii %d" % _tag()
    nid = _nota_prin_ecran(ana, firma_e2e, desc, AZI.isoformat(), luna=LUNA)
    uid = ana_cont["id"]
    (drepturi,) = sql("SELECT poate_pregati, poate_valida, poate_depune FROM public.users WHERE id = %s", (uid,))
    _ok(_api(patron, "POST", "/asistenti/%d/permisiuni" % uid, {"poate_pregati": True, "poate_valida": True,
                                                              "poate_depune": bool(drepturi[2])}), "Ana primește „Poate valida”")
    try:
        with _cont(browser, request, ana_cont["email"]) as ana_v:   # Ana intră din nou: sesiunea are acum dreptul de validare
            _de_validat(ana_v)
            t_ana = _titluri(ana_v)
            assert [x.split(" (")[0] for x in t_ana] == ["Note de validat", "Declarații", "Notele tale în ciornă"], t_ana   # „Trei secțiuni cu număr”
            pe_ecran = ana_v.pg.evaluate("(d) => [...document.querySelectorAll('tbody.tn-nota')].filter((t) => t.innerText.includes(d)).length",
                                         desc)
            in_note = ana_v.pg.locator("#val-note tbody.tn-nota", has_text=desc).count()
            ana_v.captura("de_validat_asistenta")
            assert pe_ecran == 1 and in_note == 1, (pe_ecran, in_note)   # „note afișate de două ori” -> o dată, în „Note de validat”
    finally:
        _ok(_api(patron, "POST", "/asistenti/%d/permisiuni" % uid, {"poate_pregati": bool(drepturi[0]), "poate_valida": bool(drepturi[1]),
                                                                  "poate_depune": bool(drepturi[2])}), "drepturile Anei, la loc")
    _de_validat(patron)
    pg = patron.pg
    rand = pg.locator("#val-note tbody.tn-nota", has_text=desc).first
    rand.wait_for(timeout=20000)
    assert rand.locator(".tn-rand .val-aproba").count() == 1 and rand.locator(".tn-rand .val-respinge").count() == 1
    assert pg.locator("#val-note .val-card, #val-ciorne .val-card, .sa-jurnal").count() == 0   # „trei forme diferite” -> tabelul comun
    pg.fill("#val-cauta", desc)                                     # „căutare”
    pg.wait_for_timeout(400)
    vazute = pg.evaluate("() => [...document.querySelectorAll('#val-note tbody.tn-nota')].filter((t) => !t.hidden).length")
    assert vazute == 1, vazute
    patron.captura("de_validat_cautare")
    rand.locator(".val-aproba").click()
    if pg.query_selector("#caseta-atentie-activa #ca-ok"):
        pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => ((document.querySelector('#val-confirmare') || {}).textContent || '').includes('Ai validat')", timeout=30000)
    patron.captura("de_validat_confirmare")
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % firma_e2e["schema"], (nid,)) == [("validata",)]


# ── 621 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_621_balanta_rezumatul_nu_mananca_tabelul_si_importul_are_buton(patron, firma_preluata):
    """621. Pașii: firma cu balanța de deschidere numai cu soldurile finale (rulajele anului lipsesc) -> Balanță 10/<AN>, la 1280×720:
    rezumatul lipit sus ia cel mult un sfert din fereastră (caseta rulajelor stă sub el); sub caseta rulajelor, „Deschide Import date ›
    Solduri inițiale” -> Import date al firmei, cu „Solduri inițiale”."""
    _scrie_balanta(firma_preluata["schema"], False)
    pg = patron.pg
    vechi = pg.viewport_size
    pg.set_viewport_size({"width": 1280, "height": 720})
    try:
        _balanta(patron, firma_preluata, AN, 10)
        pg.wait_for_selector("#b-rulaje-import", timeout=30000)
        pg.wait_for_timeout(400)
        m = pg.evaluate("() => { const c = (%s)(), r = c.querySelector('.rezumat-fix'); return {rez: r.offsetHeight, corp: c.clientHeight,"
                        " rulaje_in_rezumat: !!r.querySelector('#b-rulaje')}; }" % _CORP)
        patron.captura("balanta_1280")
        assert m["rez"] <= 0.25 * m["corp"] and not m["rulaje_in_rezumat"], m     # „Casetele nu mănâncă tabelul”
        pg.click("#b-rulaje-import")
        pg.wait_for_selector("#mig-pasi .mig-frand", timeout=20000)
        pasi = [x.strip() for x in pg.locator("#mig-pasi .mig-frand-nume").all_inner_texts()]
        patron.captura("importul_firmei")
        assert pasi.count("Solduri inițiale") == 1, pasi                          # „«Importă…» are butonul spre import”
    finally:
        pg.set_viewport_size(vechi)


# ── 459.1 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_459_1_denumirea_de_la_anaf_dispare_cand_se_schimba_cui_ul(patron):
    """459.1. Pașii: Firme -> „+ Adaugă firmă” -> CUI-ul A: „Denumire firmă” = denumirea de la ANAF, rândul de sub CUI fără „— verifică.”
    -> CUI-ul schimbat: denumirea dispare -> CUI-ul A din nou, denumirea corectată de om -> alt CUI: denumirea scrisă de om rămâne. Nimic nu
    se salvează."""
    a = cui_cu_control(96000000 + _tag() % 999999)
    den = "E2E 459.1 ANAF %s SRL" % a
    chei = _anaf_pune({a: {"denumire": den, "platitor_tva": False, "cod_caen": "6920", "adresa": "Str. Probei 1", "nr_reg_com": "J40/1/2020",
                          "inactiv": False}})
    try:
        pg = patron.pg
        _deschide_firme(patron)
        pg.click("#firme-adauga")
        pg.wait_for_selector("#fn-cui", timeout=10000)
        pg.fill("#fn-cui", a)
        pg.wait_for_function("(d) => document.querySelector('#fn-nume').value === d", arg=den, timeout=30000)
        info = pg.inner_text("#fn-cui-info")
        assert info.startswith("Din ANAF: %s." % den) and info.count("verifică") == 0, info
        patron.captura("denumirea_de_la_anaf")
        pg.fill("#fn-cui", a[:-1])                                        # CUI-ul schimbat
        assert pg.input_value("#fn-nume") == ""                           # denumirea CUI-ului anterior nu mai rămâne
        patron.captura("cui_schimbat")
        pg.fill("#fn-cui", a)
        pg.wait_for_function("(d) => document.querySelector('#fn-nume').value === d", arg=den, timeout=30000)
        pg.fill("#fn-nume", den + " (corectat)")
        pg.fill("#fn-cui", cui_cu_control(95000000 + _tag() % 999999))
        pg.wait_for_timeout(1200)
        assert pg.input_value("#fn-nume") == den + " (corectat)"          # ce a scris omul rămâne (F188)
    finally:
        _anaf_scoate(chei)
