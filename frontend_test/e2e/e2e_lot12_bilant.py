# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1, grupa 3 („pot da cifre greșite”) — pachetul „bilant”: C143, 72, 187 (proba pe ecran pentru 151).

  * C143 (găsită de pachetul `decl` la C119): cifra de afaceri din bilanț includea TVA-ul din Raportul Z — F20 / F30 citeau numai creditul
    conturilor de venituri, iar nota Z face 5311 = 707 pe brut și 707 = 4427 pe TVA. Acum rulajul NET (credit − debit, fără închiderea în
    121). TEMEI: OMFP 1802/2014 pct.8 pct.5 — „cifră de afaceri netă înseamnă sumele obținute din vânzarea de produse și prestarea de
    servicii după deducerea reducerilor comerciale și a taxei pe valoarea adăugată”; DUK regula F10_0432 = F20_0082.
  * 72: „Bilanț: nu trecea prin coada pregătit → validat → depus.” — testul vechi (`e2e_bloc_c.py::test_def_72_bilantul_intra_in_coada`)
    se oprea la intrarea în coadă; aici bilanțul merge până la „— depusă.”, cu rândul lui în declarațiile depuse.
  * 187: „Probe: probă pe ecran pentru 151” — rândurile bilanțului PE ECRAN („Ce se depune”): rd.05 stocuri fără TVA-ul din prețul de raft
    (550), rd.13 datorii fără el (666); testul vechi (`e2e_bloc_e.py::test_def_151_bilant_4428_numai_la_stocuri`) citea XML-ul descărcat.

DATE DE PORNIRE fără ecran (declarate): nota Raportului Z se scrie direct în schema firmei noi (SQL, ciornă -> rânduri -> validată), în forma
pe care o scrie aplicația la „Raport Z” (5311 = 707 brutul, 707 = 4427 TVA-ul — ca `e2e_lot12_decl.py::test_def_c119_…`): ecranul probat
e Bilanțul, nu încărcarea Z-ului. Celelalte note pe ruta Registrului jurnal (`_nota_validata`), NIR-ul pe ruta Stocuri (`e2e_bloc_e._nir`).
Firmele sunt NOI (`firma_noua`), cu CUI-ul generat cu cifra de control (`conftest.cui_cu_control`); furnizorul NIR-ului la fel."""
import datetime as _dt

import pytest

from conftest import cui_cu_control, firma_noua, sql
from e2e_bloc_d import PATRON, _api, _date_firma, _deschide, _nota_validata
from e2e_comanda_1010 import _alege_bilant, _valideaza_bilant

_F = ".fereastra:last-of-type"


def _infiintata_2025(f):
    """Primul exercițiu (înființată pe 10.01.2025): coloana „An precedent” e legal goală, deci bilanțul 2025 se validează fără ea."""
    _date_firma(f)
    st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"data_infiintare": "2025-01-10"})
    assert st == 200 and r.get("ok") is not False, (st, r)


def _nota_z(f, zi, brut, tva):
    """Nota Raportului Z, în forma aplicației: 5311 = 707 brutul încasat, 707 = 4427 TVA-ul colectat (date de pornire, vezi antetul)."""
    s = f["schema"]
    # date-de-pornire: Z-ul din 30.09.2025 cu 5.826,00 brut și numai 126,00 TVA — formularul „Raport Z” (cote 11% / 21%) nu dă perechea asta
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, document_ref, status, sursa) VALUES (%%s, %%s, %%s, %%s, %%s) RETURNING id' % s,
              (zi, "Raport Z 1", "Raport Z 1", "ciorna", "raport_z"))[0][0]
    # date-de-pornire: rândurile aceluiași Z (5311 = 707 brutul, 707 = 4427 TVA-ul), în forma pe care o scrie „Raport Z”
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, %%s), (%%s, %%s, %%s, %%s)'
        % s, (nid, "5311", "707", brut, nid, "707", "4427", tva))
    # date-de-pornire: validarea aceluiași Z (ciornă -> rânduri -> validată), ca după „Validează raportul Z”
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))   # ciornă -> rânduri -> validată (regula_linii_nota)
    return nid


@pytest.fixture()
def firma_z_2025():
    """Primul exercițiu 2025: Raportul Z din 30.09.2025 (5311 = 707 5.826,00; 707 = 4427 126,00), mărfurile 3.000 (607 = 401), regularizarea
    TVA la 31.12 (4427 = 4423 126) și închiderea pe sold la 31.12 (707 = 121 5.700; 121 = 607 3.000 — OMFP 1802/2014, contul 121)."""
    for f in firma_noua():
        _infiintata_2025(f)
        _nota_z(f, "2025-09-30", 5826, 126)
        _nota_validata(f, "2025-09-30", "607", "401", 3000, "Marfa C143")
        _nota_validata(f, "2025-12-31", "4427", "4423", 126, "Regularizarea TVA C143")
        _nota_validata(f, "2025-12-31", "707", "121", 5700, "Inchidere 707")
        _nota_validata(f, "2025-12-31", "121", "607", 3000, "Inchidere 607")
        yield f


def test_def_c143_cifra_de_afaceri_din_bilant_fara_tva_ul_din_raportul_z(patron, firma_z_2025):
    """C143. Pașii: firma cu Raportul Z din 09/2025 (5311 = 707 5.826,00 și 707 = 4427 126,00), mărfuri 3.000, anul închis în 121 -> Bilanț
    anual -> 2025, S1005 -> „Validează”: „Validare fără erori”; „Ce se depune”: F20 rândul 01 cifra de afaceri netă = 5.700,00 (până la
    C143: 5.826,00 — cu TVA-ul), rândul 08 profit = 2.700,00 = F10 rândul 43 (profitul din 121); F30 cap.XIX rândul 169 (vânzarea mărfurilor)
    = 5.700,00. MUTAȚIA din plasă: ramura rulajului net scoasă din `bilant._valoare_termen` -> F20 rândul 01 = 5.826,00 și DUK respinge
    („F10_0432 = F20_0082”) -> ROȘU.
    TEMEI: OMFP 1802/2014 pct.8 pct.5 (cifra de afaceri netă, „după deducerea [...] taxei pe valoarea adăugată”)."""
    f = firma_z_2025
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, 2025)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura()
    patron.pg.locator(_F + " #bl-randuri tbody tr", has_text="rândul 169").scroll_into_view_if_needed()
    patron.captura("cap_xix")
    assert "Validare fără erori" in text, text[:800]                                   # DUK regula F10_0432 = F20_0082
    assert rand[("F20", 1)][1] == "5.700,00", sorted(rand.items())                     # OMFP 1802/2014 pct.8 pct.5: fără TVA
    assert (rand[("F20", 8)][1], rand[("F10", 43)][1]) == ("2.700,00", "2.700,00"), sorted(rand.items())
    assert (rand[("F30", 169)][1], rand[("F30", 167)][1]) == ("5.700,00", "5.700,00"), sorted(rand.items())


@pytest.fixture()
def firma_bilant_de_depus():
    """Primul exercițiu 2025: aport 1.000 (5121 = 1012), vânzări 1.000 (5121 = 707), mărfuri 300 (607 = 5121), închise în 121 la 31.12."""
    for f in firma_noua():
        _infiintata_2025(f)
        _nota_validata(f, "2025-01-15", "5121", "1012", 1000, "Aport 72")
        _nota_validata(f, "2025-03-10", "5121", "707", 1000, "Vanzare marfa 72")
        _nota_validata(f, "2025-03-11", "607", "5121", 300, "Marfa descarcata 72")
        _nota_validata(f, "2025-12-31", "707", "121", 1000, "Inchidere 707")
        _nota_validata(f, "2025-12-31", "121", "607", 300, "Inchidere 607")
        yield f


def test_def_72_bilantul_trece_prin_coada_pana_la_depus(patron, firma_bilant_de_depus):
    """72. „Bilanț: nu trecea prin coada pregătit → validat → depus.” Pașii: firma cu anul 2025 închis -> Bilanț anual -> 2025, S1005 ->
    „Trimite în coadă →”: „a intrat în coada de validare” (PREGĂTIT; validarea în doi e oprită pe cabinetul de test, deci declarația
    trimisă de contabilul-șef e aprobată — VALIDAT) -> De validat -> rândul „S1005” al firmei -> „Confirmă depunerea” -> indexul SPV ->
    „— depusă.” (DEPUS): elementul cozii e „depusa”, iar bilanțul 2025 stă în declarațiile depuse ale firmei, cu indexul.
    MUTAȚIA din plasă: „s1005” scos din `declaratii_api.SITUATII_FINANCIARE` -> nu mai intră în coadă -> ROȘU."""
    f = firma_bilant_de_depus
    pg = patron.pg
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, 2025)
    pg.evaluate("() => { const m = document.querySelector('.fereastra:last-of-type #bl-coada-mesaj'); if (m) m.innerHTML = ''; }")
    pg.click(_F + " #bl-coada")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #bl-coada-mesaj') || {innerText: ''}).innerText.trim() "
                         "!== ''", timeout=90000)
    msg = pg.inner_text(_F + " #bl-coada-mesaj")
    patron.captura("pregatit")
    assert "a intrat în coada de validare" in msg, msg
    r = sql("SELECT id, stare FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 's1005'", (f["tenant_id"],))
    assert len(r) == 1 and r[0][1] in ("la_senior", "aprobata"), r
    cid = r[0][0]
    # De validat -> „Confirmă depunerea” pe rândul bilanțului firmei -> indexul SPV
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    pg.wait_for_selector(_F + " .cf-grup-titlu", timeout=60000)
    rand = pg.locator(_F + " .val-info", has_text=f["nume"]).filter(has_text="S1005").first.locator("xpath=..")
    rand.locator(".val-depune").wait_for(timeout=30000)
    patron.captura("de_validat")
    rand.locator(".val-depune").click()
    pg.wait_for_selector(_F + " #dlg-input", timeout=20000)
    index = "72%d" % (int(_dt.datetime.now().timestamp()) % 1000000)
    pg.fill(_F + " #dlg-input", index)
    pg.click(_F + " #dlg-ok")
    pg.wait_for_function("() => { const t = [...document.querySelectorAll('.fereastra')].pop().innerText; "
                         "return t.includes('— depusă.') || !!document.querySelector('#val-conf-ok'); }", timeout=60000)
    if pg.locator("#val-conf-ok").count():   # constatări certe de confirmat: un motiv pe fiecare, ca orice contabil
        for i in range(pg.locator(".val-conf-motiv").count()):
            pg.locator(".val-conf-motiv").nth(i).fill("bilanțul 2025 al firmei de probă")
        pg.click("#val-conf-ok")
        pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('— depusă.')", timeout=60000)
    patron.captura("depus")
    assert sql("SELECT stare FROM public.declaratii_coada WHERE id = %s", (cid,)) == [("depusa",)]
    dep = sql("SELECT tip, an FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 's1005'", (f["tenant_id"],))
    assert dep == [("s1005", 2025)], dep


@pytest.fixture()
def firma_gv_2025():
    """Firmă nouă, global-valorică (Date firmă pe drumul ecranului, `e2e_bloc_e._completeaza`), cu evidența din 01/2024."""
    from e2e_bloc_e import _completeaza
    for f in firma_noua():
        yield _completeaza(f, "global_valoric")


def test_def_187_proba_pe_ecran_pentru_151(patron, firma_gv_2025):
    """187 („probă pe ecran pentru 151”) / 151 („Bilanț: 4428 (preț de raft) apărea și la datorii; analitic propriu, doar la stocuri
    rd.05”). Pașii contabilului (global-valoric): NIR fără factură din 11/2025, 10 buc × 55 lei, preț de raft 80 lei, validat (371 = 800,00;
    378 = 111,16; 4428.02 = 138,84; 408 = 665,50; 4428.01 = 115,50) -> Bilanț anual -> 2025, S1005 -> „Validează” -> PE ECRAN, „Ce se
    depune”: F10 rândul 05 (stocuri) „An curent” = 550,00 (371 − 378 − 4428.02), rândul 13 (datorii) = 666,00 (numai 408): TVA-ul din
    prețul de raft nu apare la datorii. MUTAȚIA din plasă: 4428.02 lăsat și la datorii -> rândul 13 = 804,00 -> ROȘU.
    TEMEI: OMFP 1802/2014 pct.451 (bilanțul prescurtat), rândul 05 al formularului ANAF 2025: „… 371 +/- 378 … − din ct. 4428”."""
    from e2e_bloc_e import _bilant, _nir
    f = firma_gv_2025
    _nir(f, "E187", "2025-11-12", "Furnizor 187 SRL", cui_cu_control(37000187), 10, 55, pret_vanzare=80)
    pg = patron.pg
    _bilant(patron, f, 2025, "s1005")
    pg.click("#bl-val")
    pg.wait_for_selector("#bl-randuri tbody tr", timeout=120000)
    ecran = pg.evaluate("""() => [...document.querySelectorAll('#bl-randuri tbody tr')].map(tr =>
      [...tr.querySelectorAll('td')].map(td => td.innerText.trim()))""")
    nr = lambda r: int(r.split("(")[-1].rstrip(")")) if "(" in r else int(r.split()[-1])   # noqa: E731  („rândul 06a (301)”, 234)
    rand = {(fo, nr(r)): c for fo, r, _den, _p, c in ecran}
    pg.locator("#bl-randuri tbody tr", has_text="rândul 05").first.scroll_into_view_if_needed()
    patron.captura("randurile_pe_ecran")
    assert rand.get(("F10", 5)) == "550,00", sorted(rand.items())    # rd.05: „− din ct. 4428” (4428.02)
    assert rand.get(("F10", 13)) == "666,00", sorted(rand.items())   # rd.13: 408, fără 4428.02
