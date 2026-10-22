# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.3 (Costin 22.10.2026, verbatim în DECIZII „Comanda 11.3”) — subagentul A453: 453 (pct.8, „verifică la sursă
rotunjirea deducerii personale (fluturașul arată 562,25) și aplic-o în calcul, fluturaș și D112.”) și 454 (pct.7, „la salariat nou erorile
apar pe rând, în trei salvări; CNP și Tip normă nu sunt marcate obligatorii.”). Pașii contabilului pe aplicația din index, pe baza de TEST.

Date de pornire scrise direct: niciuna. 453: firma și salariatul (5.000 lei brut, normă întreagă, funcția de bază, 0 persoane în
întreținere) vin din fixtura `firma_sal` (ruta salariaților, `POST /tenants/{id}/salariati`). 454: salariatul existent (cel cu CNP-ul
dublat) se adaugă pe aceeași rută, restul pe ecranul „+ Salariat nou”. CNP-urile au cifra de control calculată cu algoritmul din
CLAUDE.md (`e2e_bloc_b._cnp`, verificat și de validatorul aplicației); greșit = aceeași bază cu ultima cifră schimbată."""
import base64
import io as _io
import re

from conftest import sql
from e2e_bloc_a import _card
from e2e_bloc_b import _cnp
from e2e_bloc_d import _date_firma, firma_sal  # noqa: F401 — firma_sal: fixtura
from e2e_bloc_d import _stat as _stat_luna

_F = ".fereastra:last-of-type "


def _pdf_fluturas(patron):
    """„Fluturaș” pe rândul salariatului -> textul PDF-ului (citit întreg, din același URL, cu tokenul sesiunii)."""
    from pypdf import PdfReader
    pg = patron.pg
    with pg.expect_response(lambda r: "/fluturas/" in r.url, timeout=30000) as rr:
        pg.click(_F + "[data-flut] >> nth=0")
    assert rr.value.status == 200, rr.value.status
    b64 = pg.evaluate("""async (u) => { const t = sessionStorage.getItem('iconta_token');
      const x = await fetch(u, {headers: {'Authorization': 'Bearer ' + t}}); const b = new Uint8Array(await x.arrayBuffer());
      let s = ''; for (const c of b) s += String.fromCharCode(c); return btoa(s); }""", rr.value.url)
    return "\n".join(p.extract_text() for p in PdfReader(_io.BytesIO(base64.b64decode(b64))).pages)


# ── 453 — deducerea personală: aceeași cifră, rotunjită la leu, pe ecran, pe fluturaș și în D112 ─────────────────────────────────
def test_def_453_deducerea_rotunjita_pe_stat_fluturas_si_d112(patron, firma_sal):
    """453. Pașii: salariatul cu 5.000 lei brut -> Salariați -> statul lunii trecute -> „Compoziția netului”: „… deducere personală 562,00
    lei” (13% × 4.325 = 562,25, rotunjit la leu), nu 562,25 -> „Fluturaș”: PDF-ul are aceeași deducere, 562,00 -> Declarații -> D112 pe
    luna trecută -> pasul 2: „fără erori” la DUKIntegrator, iar „Vezi XML-ul generat” arată deducerea declarată 562 (E3_12 / E3_121 /
    E1_4 / E1_41) și venitul bază de calcul 2.688 = 5.000 − 1.750 − 562 (E3_14 / E1_6). Înainte: 562,25 pe ecran și pe fluturaș, iar
    D112 declara deducerea 0 (E1_4="0") și impozitul în locul bazei (E3_14).
    Temeiul rotunjirii: structura D112 (antet) — „Campurile calculate cu ajutorul parametrilor vor avea valori intregi, pozitive
    obtinute prin rotunjire matematica”; CF art.77 alin.(4) dă procentul, fără să spună cum se rotunjește suma."""
    pg = patron.pg
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    pg.click(_F + ".pf-frand details.dec-xml summary")
    comp = pg.inner_text(_F + ".pf-frand details.dec-xml")
    patron.captura("compozitia_netului")
    # [deficiența 411, lotul 9] rândul deducerii stă sub impozit, cu eticheta „în calculul impozitului, scade baza (nu se reține): deducere
    # personală” (`stat_plata_api.compozitie_fluturas`); valoarea e cea rotunjită la leu (453)
    from e2e_lot11_s9 import _ETICHETA_DEDUCERE, _bani, _d112_xml, _int, _randuri_compozitie, _singurul, _un
    assert _randuri_compozitie(comp).get(_ETICHETA_DEDUCERE) == _bani("562,00"), comp
    text = _pdf_fluturas(patron)
    patron.captura("fluturas")
    # fluturașul tipărește aceleași rânduri; 562,25 (forma veche, nerotunjită) nu apare nicăieri pe el
    assert re.search(r"deducere personală\s+562,00\b", text) and not re.search(r"562,25", text), text[:1500]
    _date_firma(firma_sal)
    a = _singurul(_d112_xml(patron, firma_sal))
    assert _int(_un(a, "asiguratE3"), "E3_12", "E3_121", "E3_122", "E3_9", "E3_14", "E3_15") == [562, 562, 0, 1750, 2688, 269], a
    assert _int(_un(a, "asiguratE1"), "E1_4", "E1_41", "E1_2", "E1_6", "E1_7") == [562, 562, 1750, 2688, 269], a


# ── 454 — „Salariat nou”: toate erorile la aceeași salvare; CNP și Tip normă marcate obligatorii ──────────────────────────────────
def test_def_454_salariat_nou_toate_erorile_deodata_cnp_si_norma_obligatorii(patron, firma_sal):
    """454. Pașii: Salariați -> „+ Salariat nou”: lângă „CNP” și „Tip normă” stă asteriscul câmpului obligatoriu. (a) „Salvează” cu numele
    scris, CNP-ul cu cifra de control greșită, fără Tip normă, fără salariu și fără ocupație: TOATE se spun la aceeași apăsare — CNP-ul
    greșit, Tip normă, salariul, ocupația — fiecare lângă câmpul lui și în caseta „NU s-a salvat.”; nimic salvat. (b) CNP-ul corectat cu
    al unui salariat care există deja la firmă, restul completat, dar data încetării înaintea angajării și un IBAN greșit: refuzul
    serverului spune DEODATĂ CNP-ul dublat, data încetării și IBAN-ul, fiecare lângă câmpul lui (înainte: data încetării rupea refuzul —
    eroare de server —, iar CNP-ul dublat venea abia la salvarea de după). (c) Corectate: salvat."""
    existent = _cnp("185010140123")    # salariatul fixturii `firma_sal` (CNP-ul lui, deja la firmă)
    pg = patron.pg
    patron.firma(firma_sal["nume"])
    _card(patron, "salariati", "#sp-salariat-nou")
    pg.click("#sp-salariat-nou")
    pg.wait_for_selector("#sn-salveaza", timeout=20000)
    for camp in ("sn-cnp", "sn-tip_norma"):
        assert pg.locator('label[for="%s"] .oblig' % camp).count() == 1, "„%s” fără asteriscul de obligatoriu" % camp
    gresit = _cnp("190030541007")[:12] + str((int(_cnp("190030541007")[12]) + 1) % 10)
    pg.fill("#sn-nume", "Marinescu")
    pg.fill("#sn-cnp", gresit)
    pg.click("#sn-salveaza")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    patron.captura("toate_deodata")
    for i in ("sn-cnp", "sn-tip_norma", "sn-salariu_brut", "sn-cor-cauta"):
        assert pg.get_attribute("#" + i, "aria-invalid") == "true", i
    assert pg.inner_text('.msg-eroare[data-camp="sn-cnp"]').strip() == "CNP invalid (13 cifre, cifră de control greșită)."
    caseta = pg.eval_on_selector_all(".refuz-salvare .refuz-salvare-lista > li", "lis => lis.filter(li => !li.hidden).map(li => li.textContent.trim())")
    assert any("CNP invalid" in t for t in caseta) and any("Salariul brut" in t for t in caseta), caseta
    assert not sql('SELECT 1 FROM "%s".salariati WHERE nume = %%s' % firma_sal["schema"], ("Marinescu",))
    # (b) CNP-ul altui salariat al firmei + data încetării înaintea angajării + IBAN greșit: refuzul serverului, cu toate trei
    pg.fill("#sn-cnp", existent)
    pg.select_option("#sn-tip_norma", "intreaga")
    pg.fill("#sn-salariu_brut", "4500")
    pg.fill("#sn-data_angajare", "2026-05-01")
    pg.fill("#sn-data_incetare", "2026-04-01")
    pg.fill("#sn-iban", "RO00BANK0000000000000001")
    for sel, v in (("#sn-functie_baza", "true"), ("#sn-scutit_contrib_minim", "false"), ("#sn-declaratie_copii", "false")):
        pg.select_option(sel, v)
    pg.fill("#sn-cor-cauta", "241107")
    pg.wait_for_selector("#sn-cor-rez [data-cod='241107']", timeout=20000)
    pg.click("#sn-cor-rez [data-cod='241107']")
    pg.click("#sn-salveaza")
    pg.wait_for_selector('.msg-eroare[data-camp="sn-iban"]', timeout=20000)
    patron.captura("server_deodata")
    assert "Există deja un salariat cu CNP-ul %s" % existent in pg.inner_text('.msg-eroare[data-camp="sn-cnp"]')
    assert pg.inner_text('.msg-eroare[data-camp="sn-data_incetare"]').strip() == "Data încetării nu poate fi înainte de data angajării."
    assert pg.inner_text('.msg-eroare[data-camp="sn-iban"]').startswith("IBAN invalid")
    assert not sql('SELECT 1 FROM "%s".salariati WHERE nume = %%s' % firma_sal["schema"], ("Marinescu",))
    # (c) corectate: CNP nou, fără data încetării, fără IBAN -> salvat
    pg.fill("#sn-cnp", _cnp("190030541007"))
    pg.fill("#sn-data_incetare", "")
    pg.fill("#sn-iban", "")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => !(document.querySelector('#sn-nume') || {}).value", timeout=30000)
    patron.captura("salvat")
    assert sql('SELECT cnp, cor FROM "%s".salariati WHERE nume = %%s' % firma_sal["schema"], ("Marinescu",)) == [(_cnp("190030541007"), "241107")]
