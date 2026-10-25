# -*- coding: utf-8 -*-
"""Lotul 12, pachetul cx6: testele de capăt la capăt pentru C160 și C162 — drumurile rămase deschise după C154 / C155 la firma NEPLĂTITOARE
de TVA înregistrată în scopuri de TVA după CF art.317 (forma firmei de test F3).

  · C160 — factura RECURENTĂ către clientul din DE se emitea cu țara „RO”: șablonul n-avea țara clientului, deci factura lunară ieșea fără
    axa „servicii” și intra în D390 ca livrare de bunuri (L), nu ca prestare (P). Acum șablonul are „Țara beneficiarului” (dedusă din
    codul fiscal, ca la „Emite factură”), iar factura lunară o poartă — CF art.325 alin.(1) lit.c.
  · C162 — selectorul Declarații („Datorate de firmă”, același calcul ca ecranul „Termene”) arăta D390 pe toate lunile neplătitorului
    art.317, nu numai pe luna cu prestarea: motorul termenelor nu primea calendarul lui (`control_incrucisat.d390_luni_neplatitor`, sursa
    lui Control fiscal din C155) — CF art.325 alin.(2).
  · C161 (importul XML al facturii emise) n-are ecran: ruta `import-efactura` n-are buton (încărcarea manuală, `main.py`); proba e în
    `core/test_lot12_c160_c162_tara_axa.py`.

Pașii pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`), pregătite pe drumul ecranelor (`pregateste_firma` +
Date firmă + Vector fiscal, `e2e_lot12_cx3._neplatitor_art317`). Factura lunară se emite de tura cronului (`facturi_recurente.emite_scadente`,
ce rulează cronul zilnic), cu ziua din luna încheiată (`conftest.perioada_incheiata`): D390 se generează numai pe o lună încheiată (383).
VIES e servit de plasă (`<ICONTA_ANAF_SIMULAT>/vies.json`, codul DE811907980 al probei R187 / C78 / C110). Nicio scriere SQL: `sql` doar
citește."""
import datetime as _dt

import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, perioada_incheiata, sql

COD_CLIENT_IC = "DE811907980"
LUNA = perioada_incheiata("lunar")
ZI = LUNA.inceput.replace(day=10)
SERVICIU = "Servicii de consultanta IT E2E C160"   # felul din denumire („servici” -> contul 704), cum îl scrie contabilul


@pytest.fixture()
def firma_cx6():
    for f in firma_noua():
        yield f


def _d390_clasificare(patron, f):
    """Declarații -> D390, luna încheiată -> „Continuă” -> rândurile din „Clasificare intracomunitară”."""
    from e2e_bloc_c import _deschide
    pg = patron.pg
    _deschide(patron, f["nume"], "declaratii", "#dec-tip")
    alege_tipul(pg, "d390")
    pg.wait_for_selector("#dec-an", timeout=10000)
    alege_perioada(pg, LUNA.an, LUNA.luna)
    pg.click("#dec-continua")
    pg.wait_for_selector("#dec-d390-clasif .dec-recl-rand", timeout=90000)
    patron.captura("d390_clasificare")
    return pg.locator("#dec-d390-clasif .dec-recl-rand")


def test_def_c160_factura_recurenta_catre_clientul_ue_poarta_tara_clientului(patron, firma_cx6):
    """C160. Pașii: firmă neplătitoare de TVA, înregistrată art.317 -> Facturi -> Facturi recurente -> „+ Șablon nou” -> CUI beneficiar
    DE811907980: „Țara beneficiarului” devine Germania (DE) -> denumirea, linia „Servicii de consultanta IT …” 1 × 500 lei (scutit), ziua 5
    -> „Salvează șablonul”: în listă rândul spune „client din DE” -> tura cronului emite factura lunară -> Declarații -> D390, luna facturii
    -> „Continuă”: operațiunea e „Servicii prestate (P)”, 500 lei; factura are țara DE și axa „servicii”. Înainte: șablonul fără țară,
    factura cu țara RO și fără axă -> „Livrare bunuri (L)”.
    MUTAȚIILE (`mut_lot12_cx6.json`): țara scoasă din emiterea cronului (`facturi_recurente.emite_scadente`) -> operațiunea iese L -> ROȘU;
    țara netrimisă de ecran -> șablonul refuzat lângă „CUI beneficiar” -> ROȘU."""
    from conftest import _db
    from core import facturi_recurente
    from e2e_bloc_a import _card
    from e2e_lot12_cx3 import _neplatitor_art317
    f = firma_cx6
    s = f["schema"]
    _neplatitor_art317(patron, f)
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-recurente")
    pg.click("#fac-recurente")
    pg.wait_for_selector("#fr-add", timeout=20000)
    pg.click("#fr-add")
    pg.wait_for_selector("#fr-l0-descriere", timeout=20000)
    assert pg.input_value("#fr-tara") == "RO"
    pg.fill("#fr-cui", COD_CLIENT_IC)
    pg.dispatch_event("#fr-cui", "change")
    pg.wait_for_function("() => document.querySelector('#fr-tara').value === 'DE'", timeout=10000)
    pg.fill("#fr-nume", "KUNDE E2E GMBH")
    pg.fill("#fr-l0-descriere", SERVICIU)
    pg.dispatch_event("#fr-l0-descriere", "input")
    # [lotul 12, 12.3 pct.9] cota liniei ca la „Emite factură”: la neplătitor „0%” fix (CF art.310 alin.(10) lit.b), nu „scutit”
    pg.wait_for_function("() => (document.querySelector('#fr-l0-cota') || {textContent: ''}).textContent.trim() === '0%'", timeout=20000)
    pg.fill("#fr-l0-cantitate", "1")
    pg.dispatch_event("#fr-l0-cantitate", "input")
    pg.fill("#fr-l0-pret_unitar", "500")
    pg.dispatch_event("#fr-l0-pret_unitar", "input")
    pg.fill("#fr-zi", "5")
    patron.captura("sablon")
    pg.click("#fr-salveaza")
    pg.wait_for_selector("#fr-add", timeout=30000)                         # salvat: înapoi la lista șabloanelor
    rand = pg.locator(".pf-frand", has_text="KUNDE E2E GMBH")
    rand.wait_for(timeout=10000)
    assert "client din DE" in " ".join(rand.inner_text().split()), rand.inner_text()
    patron.captura("lista_sabloane")
    assert sql('SELECT tert_tara, zi_emitere FROM "%s".facturi_recurente' % s) == [("DE", 5)]
    _db()
    emise = facturi_recurente.emite_scadente(s, ZI)                       # tura cronului zilnic, în ziua emiterii
    assert [bool(e.get("factura")) for e in emise if "sablon" in e] == [True], emise
    # CF art.325 alin.(1) lit.c: prestarea art.278 alin.(2) a înregistratului art.317 intră în D390 — axa „servicii” de pe document (P)
    assert sql('SELECT tert_tara, axa_ic FROM "%s".facturi' % s) == [("DE", "servicii")]
    randuri = _d390_clasificare(patron, f)
    assert randuri.count() == 1, randuri.count()
    assert pg.input_value("#dec-d390-clasif select.dec-recl") == "P"
    assert pg.get_attribute("#dec-d390-clasif select.dec-recl", "data-cod") == COD_CLIENT_IC[2:]
    assert " ".join(pg.inner_text("#dec-d390-clasif .dec-recl-suma").split()) == "500,00 lei"


def test_def_c162_declaratii_arata_d390_numai_pe_luna_cu_prestarea(patron, firma_cx6):
    """C162. Pașii: firmă neplătitoare de TVA, înregistrată art.317 -> Emite factură: prestarea de servicii către clientul din DE în luna
    încheiată -> Declarații: în „Datorate de firmă” D390 apare numai pe luna facturii (cât termenul ei, 25 ale lunii de azi, n-a trecut),
    niciodată pe luna în curs, fără nicio operațiune intracomunitară (CF art.325 alin.(2)). Înainte: D390 și pe luna în curs — motorul
    termenelor punea D390 pe toate lunile neplătitorului art.317.
    MUTAȚIA (`mut_lot12_cx6.json`): calendarul neplătitorului netrimis motorului (`termene_api.termene_firma`) -> D390 pe luna în curs
    apare -> ROȘU."""
    from e2e_bloc_c import _deschide
    from e2e_lot12_cx3 import _neplatitor_art317
    from e2e_lot12_cx5 import _emite_prestarea_ic
    f = firma_cx6
    _neplatitor_art317(patron, f)
    _emite_prestarea_ic(patron, f)
    pg = patron.pg
    _deschide(patron, f["nume"], "declaratii", "#dec-tip")
    datorate = pg.eval_on_selector_all("#dec-tip optgroup option", "(os) => os.map((o) => o.textContent)")
    patron.captura("datorate")
    azi = _dt.date.today()
    d390 = sorted(t.split(" · ")[1] for t in datorate if t.startswith("D390 · "))
    asteptat = ["%02d/%d" % (LUNA.luna, LUNA.an)] if azi.day <= 25 else []   # termenul D390 al lunii încheiate: 25 ale lunii de azi
    assert d390 == asteptat, datorate
    assert not any(t.startswith("D390 · %02d/%d" % (azi.month, azi.year)) for t in datorate), datorate
