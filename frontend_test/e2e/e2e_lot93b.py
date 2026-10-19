# -*- coding: utf-8 -*-
"""Lotul 9, închiderea lotului (Costin 19.10.2026, verbatim în DECIZII „Închiderea lotului 9”): deficiențele 404 și 405 după deciziile lui —
pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`, prin `firma_cv_noua` din `e2e_lot92`).
CUI 14399840 (DANTE INTERNATIONAL SA): cifra de control verificată (algoritmul din CLAUDE.md).
  405 „Avans 409x = 5311”: plata în numerar a unui NIR fără factură e avans acordat furnizorului, compensat la sosirea facturii (401 = 409x).
  404 „Da, automat”: lipsa neimputabilă de la inventar trece singură la ajustările fiscale ale impozitului pe profit (CF art.25 alin.(4) lit.c).
"""
import re

from e2e_lot92 import AZI, _lei, _nir_form, _numerar, firma_cv, firma_cv_noua   # noqa: F401 — fixturile modulului

CUI_DANTE = "14399840"


# ── 405 — plata NIR-ului fără factură ───────────────────────────────────────────────────────────────────────────────────────────
def _nir_dante(patron, firma, numar):
    """NIR fără factură de la DANTE: 2 buc × 25 lei, 21%, transport 5 lei cu 21% -> 371 = 408 50 + 5, 4428.01 = 408 10,50 + 1,05: 66,55 lei."""
    pg = _nir_form(patron, firma, numar)
    pg.fill("#sn-furn", "DANTE INTERNATIONAL SA")
    pg.fill("#sn-cui", CUI_DANTE)
    pg.select_option("#sn-factura-sosita", "false")
    pg.select_option("#sn-transport-cota", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('NIR salvat')", timeout=30000)


def _plata_dante(patron, firma, suma):
    from e2e_bloc_a import _card
    patron.firma(firma["nume"])
    _card(patron, "casa", "#c-toggle")
    pg = patron.pg
    pg.click("#c-toggle")
    pg.select_option("#c-cat", "plata_furnizor")
    pg.fill("#c-suma", suma)
    pg.fill("#c-part", "DANTE INTERNATIONAL SA")
    pg.fill("#c-cui", CUI_DANTE)
    pg.fill("#c-doc", "DP405")
    return pg


def test_def_405_platile_nirului_fara_factura_sunt_oferite_si_nota_e_4091(patron, firma_cv):
    """405. Pașii: numerar în casă; NIR N405 de la DANTE, factura nesosită (66,55 lei pe 408) -> Casă -> „+ Dispoziție nouă” -> plată furnizor
    66,55 lei, CUI DANTE: sub „Factura plătită” apare „NIR fără factură plătit” cu „NIR nr N405 din <azi> · DANTE INTERNATIONAL SA · rămas
    66,55 lei” (nu „Nicio factură primită neplătită” singur) -> bifat -> Adaugă -> „Dispoziția a fost salvată”, nota 4091=5311, rândul din
    registru spune „avans pentru NIR nr N405 din <azi>” -> o dispoziție nouă către DANTE nu mai oferă NIR-ul plătit."""
    _numerar(patron, firma_cv)
    _nir_dante(patron, firma_cv, "N405")
    pg = _plata_dante(patron, firma_cv, "66.55")
    eticheta = "NIR nr N405 din %s" % AZI.strftime("%d.%m.%Y")
    pg.wait_for_selector("#c-niruri", timeout=15000)
    rand = " ".join(pg.inner_text("#c-facturi").split())
    patron.captura("nir_oferit")
    assert "%s · DANTE INTERNATIONAL SA · rămas %s lei" % (eticheta, _lei(66.55)) in rand, rand
    pg.check("#c-facturi [data-cn]")
    pg.wait_for_timeout(600)   # previzualizarea (250 ms) cu NIR-ul ales: niciun avans fără document, nicio destinație cerută
    assert not pg.query_selector("#c-avans-dest"), pg.inner_text("#c-previz")
    pg.click("#c-adauga")
    pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=20000)
    t = " ".join(pg.inner_text("body").split())
    patron.captura()
    assert "4091=5311" in t and ("avans pentru %s" % eticheta) in t, t[:2000]
    # NIR-ul plătit integral nu se mai oferă
    pg.click("#c-toggle")
    pg.select_option("#c-cat", "plata_furnizor")
    pg.fill("#c-suma", "10")
    pg.fill("#c-cui", CUI_DANTE)
    pg.wait_for_selector("#c-avans", timeout=15000)
    pg.wait_for_timeout(600)
    patron.captura("nir_platit")
    assert not pg.query_selector("#c-niruri") and eticheta not in pg.inner_text("#c-facturi"), pg.inner_text("#c-facturi")


# ── 404 — lipsa neimputabilă la ajustările fiscale ─────────────────────────────────────────────────────────────────────────────────
def test_def_404_lipsa_neimputabila_trece_la_ajustarile_fiscale(patron, firma_cv):
    """404. Pașii: firma pe impozit pe profit; Stocuri -> „Mișcări, fișe…” -> Inventar: faptic 0 sub scriptic -> „neimputabilă” -> Salvează:
    mesajul spune „Suma de X lei a trecut la ajustările fiscale (Registrul de evidență fiscală, rd.33 — alte cheltuieli nedeductibile,
    T<n>/<an>)” -> fereastra firmei -> „Registrul de evidență fiscală”, anul curent -> sub „Ajustări fiscale”: rândul T<n>/<an>,
    „rd.33 — alte cheltuieli nedeductibile”, X lei, „Lipsă neimputabilă la inventarul din <azi> — <articol> … (CF art.25 alin.(4) lit.c)”,
    document „Inventarul din <azi>”."""
    from e2e_bloc_a import ARTICOL, _api, _card, _ok, articol_in_stoc
    _ok(_api(patron, "POST", "/tenants/%d/vector" % firma_cv["tenant_id"],
             {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False, "inreg_art317": False,
              "tva_data_inceput": "2026-01-01"}), "vector profit")
    aid = articol_in_stoc(patron, firma_cv)
    patron.firma(firma_cv["nume"])
    _card(patron, "stocuri", "#cv-toggle")
    pg = patron.pg
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-inv", timeout=20000)
    pg.click("#cv-inv")
    pg.fill("#cvi-a%d-faptic" % aid, "0")
    pg.wait_for_selector("#cvi-a%d-lipsa" % aid, state="visible", timeout=5000)
    pg.select_option("#cvi-a%d-lipsa" % aid, "neimputabila")
    pg.click("#cvi-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('a trecut la ajustările fiscale')", timeout=20000)
    t = " ".join(pg.inner_text("body").split())
    trim = "T%d/%d" % ((AZI.month - 1) // 3 + 1, AZI.year)
    m = re.search(r"Suma de ([\d.]+,\d\d) lei a trecut la ajustările fiscale \(Registrul de evidență fiscală, rd\.33 — alte cheltuieli "
                  r"nedeductibile, %s\)" % re.escape(trim), t)
    patron.captura("inventar")
    assert m, t[-1500:]
    suma = m.group(1)
    patron.firma(firma_cv["nume"])
    pg.click("#fa-regfiscal")
    pg.wait_for_selector("#rf-an", timeout=60000)
    pg.fill("#rf-an", str(AZI.year))
    pg.dispatch_event("#rf-an", "change")
    pg.wait_for_selector("#rf-ajustari table.fd-tabel tbody tr", timeout=60000)
    randuri = pg.eval_on_selector_all("#rf-ajustari table.fd-tabel tbody tr", "trs => trs.map(t => [...t.cells].map(c => c.innerText.trim()))")
    patron.captura()
    zi = AZI.strftime("%d.%m.%Y")
    lipsa = [r for r in randuri if len(r) > 4 and "Lipsă neimputabilă" in r[3]]
    assert len(lipsa) == 1 and lipsa[0][:3] == [trim, "rd.33 — alte cheltuieli nedeductibile", "%s lei" % suma], randuri
    assert lipsa[0][3].startswith("Lipsă neimputabilă la inventarul din %s — %s: cheltuiala" % (zi, ARTICOL)), lipsa
    assert lipsa[0][3].endswith("(CF art.25 alin.(4) lit.c)") and lipsa[0][4] == "Inventarul din %s" % zi, lipsa
