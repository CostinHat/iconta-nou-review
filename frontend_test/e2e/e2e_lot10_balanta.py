# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.1 (Costin, verbatim în DECIZII „Comanda 10.1”) — 425, partea de EFECT: datele balanței de deschidere preluate
ajung în balanță și în D101. „Când fișierul are soldurile inițiale ale anului și rulajele, ele intră ca sold inițial și sume precedente,
cu toate conturile care au rulaj. Când are doar solduri finale, comportamentul de acum rămâne, dar aplicația spune clar că rulajele anului
lipsesc și ce afectează.”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`), pe profit, cu balanța de deschidere SAGA la
30.09 a unei firme (2025 în e2e: D101 numai pe an încheiat) care închide lunar 6 / 7 în 121 (`core/test_lot10_rulaje_preluate.BALANTA_SAGA`: 707 rulaj 180.000 / 180.000,
sold final 0; 371 sold la 1 ianuarie 30.000) și notele validate din octombrie (707 10.000, 607 6.000, 641 3.000). CUI-ul firmei:
`cui_cu_control` (cifra de control verificată)."""
import os
import sys
from decimal import Decimal

import pytest

from conftest import firma_noua, sql
from e2e_bloc_c import _declaratie_pas1
from e2e_bloc_e import _balanta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.test_lot10_rulaje_preluate import BALANTA_SAGA, NOTE_OCTOMBRIE, REF   # noqa: E402

# Scenariul pytest (preluare la 30.09.2026) mutat cu un an înapoi: D101 se generează numai pe un an ÎNCHEIAT (383, comanda 10.2 pct.1:
# „O declarație pe o perioadă neîncheiată se refuză la generare”), deci firma e preluată la 30.09.2025 și D101 e pe 2025.
AN = REF.year - 1
REF_E2E = REF.replace(year=AN)
NOTE_E2E = tuple((str(AN) + data[4:], deb, cre, suma) for data, deb, cre, suma in NOTE_OCTOMBRIE)
FRAZA_LIPSA = "Rulajele de la 01.01.%d până la 30.09.%d lipsesc" % (AN, AN)


def _scrie_balanta(s, cu_rulaje):
    sql('DELETE FROM "%s".solduri_initiale' % s)
    for cont, den, sid, sic, rd, rc in BALANTA_SAGA:
        net = Decimal(sid) - Decimal(sic) + Decimal(rd) - Decimal(rc)
        if not cu_rulaje and net == 0:          # numai soldurile finale: conturile cu sold final 0 nu au rând
            continue
        sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta, si_an_debit, si_an_credit, '
            "rulaj_an_debit, rulaj_an_credit) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)" % s,
            (cont, den, max(net, 0), max(-net, 0), REF_E2E, *((sid, sic, rd, rc) if cu_rulaje else (None, None, None, None))))


@pytest.fixture(scope="module")
def firma_preluata():
    for f in firma_noua():
        s = f["schema"]
        sql('UPDATE "%s".firma_profil SET reg_com = %%s, caen = %%s, adresa = %%s, oras = %%s, judet = %%s, declarant_nume = %%s, '
            "declarant_prenume = %%s, declarant_functie = %%s, regim_fiscal = 'profit', platitor_tva = true, tip_decont = 'L', "
            "metoda_stoc = 'cantitativ_valoric' WHERE id = 1" % s,
            ("J40/1234/2020", "4719", "Str. Probei nr. 1", "București", "București", "Popescu", "Ion", "Administrator"))
        for data, deb, cre, suma in NOTE_E2E:
            nid = sql('INSERT INTO "%s".inregistrari (data, numar, descriere, status, sursa, document_ref) VALUES '
                      "(%%s, 'E2E-425', 'probă 425', 'ciorna', 'manual', 'NC E2E-425') RETURNING id" % s, (data,))[0][0]
            sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, %%s)' % s,
                (nid, deb, cre, suma))
            sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))   # [lotul 10] ciornă -> linii -> validată
        yield f


def _celule(pg, cont):
    rand = pg.locator("table.fd-tabel tr", has=pg.locator("td:text-is('%s')" % cont)).first
    return [" ".join(x.split()) for x in rand.locator("td").all_inner_texts()]


def test_def_425_balanta_preluata_arata_sold_initial_an_si_sume_precedente(patron, firma_preluata):
    """425: „ele intră ca sold inițial și sume precedente, cu toate conturile care au rulaj”. Pașii: firma -> Balanță -> 10/<AN> ->
    707: sold inițial 0, sume precedente 180.000,00 / 180.000,00, rulaj lună C 10.000,00, sold final C 10.000,00; 371: sold inițial D
    30.000,00 (cel de la 1 ianuarie), sold final D 24.000,00; 641 (sold final 0 la preluare) are rând, cu sumele precedente 30.000,00;
    caseta: „Balanța se închide pe toate cinci”; nicio casetă despre rulaje lipsă."""
    _scrie_balanta(firma_preluata["schema"], True)
    pg = patron.pg
    _balanta(patron, firma_preluata, AN, 10)
    # [lotul 12, 621] tabelul perechilor închiderii stă pliat în verdictul „Balanța se închide pe toate cinci” (`details#b-inchidere`):
    # primul `table.fd-tabel` nu se mai vede; se așteaptă tabelul balanței, cel vizibil
    pg.wait_for_selector("table.fd-tabel >> visible=true", timeout=30000)
    patron.captura("balanta_10_cu_rulaje")
    assert _celule(pg, "707")[2:] == ["0,00", "0,00", "180.000,00", "180.000,00", "0,00", "10.000,00", "180.000,00", "190.000,00",
                                      "0,00", "10.000,00"], _celule(pg, "707")
    c371 = _celule(pg, "371")
    assert (c371[2], c371[4], c371[5], c371[10]) == ("30.000,00", "100.000,00", "100.000,00", "24.000,00"), c371
    assert _celule(pg, "641")[4] == "30.000,00", _celule(pg, "641")
    t = " ".join(patron.fereastra().split())
    assert "Balanța se închide pe toate cinci" in t, t[:1500]
    assert FRAZA_LIPSA not in t


def test_def_425_d101_cuprinde_cifra_de_afaceri_preluata(patron, firma_preluata):
    """425: „Cifra de afaceri a anului (707 = 180.000 lei) și cheltuielile dispar, deci D101 [...] ies greșite.” Pașii: Declarații ->
    D101, anul <AN> -> Continuă: veniturile din exploatare 190.000 (180.000 preluate + 10.000 octombrie) și cheltuielile 145.675 în XML (P1 / P2), fără eroare și fără
    avertismentul de rulaje lipsă."""
    _scrie_balanta(firma_preluata["schema"], True)
    pg = patron.pg
    _declaratie_pas1(patron, firma_preluata["nume"], "d101", AN)
    pg.wait_for_selector("#dec-trimite, #dec-gol-da, .dec-eroare", timeout=90000)
    patron.captura("d101_cu_rulaje")
    t = " ".join(patron.fereastra().split())
    assert pg.locator(".dec-eroare").count() == 0, t[:2000]
    # cifrele D101 stau în XML-ul generat („Vezi XML-ul generat”, pliat): P1 = venituri din exploatare, P2 = cheltuieli din exploatare
    xml = pg.locator("details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre").text_content()
    assert 'P1="190000"' in xml and 'P2="145675"' in xml, xml[:3000]
    assert FRAZA_LIPSA not in t


def test_def_425_numai_solduri_finale_balanta_si_d101_spun_ce_lipseste(patron, firma_preluata):
    """425: „Când are doar solduri finale, comportamentul de acum rămâne, dar aplicația spune clar că rulajele anului lipsesc și ce
    afectează.” Pașii: aceeași firmă, balanța de deschidere numai cu soldurile finale -> Balanță 10/<AN>: caseta `#b-rulaje`
    („Rulajele de la 01.01.<AN> până la 30.09.<AN> lipsesc …«Sold inițial» arată soldul de la data preluării …”), iar 371 are sold
    inițial 30.000,00 (soldul de la 30.09, ca înainte) -> Declarații -> D101 <AN>: avertismentul spune că cifra de afaceri, veniturile și
    cheltuielile anului cuprind numai notele de după preluare."""
    _scrie_balanta(firma_preluata["schema"], False)
    pg = patron.pg
    _balanta(patron, firma_preluata, AN, 10)
    pg.wait_for_selector("#b-rulaje", timeout=30000)
    patron.captura("balanta_fara_rulaje")
    av = " ".join(pg.inner_text("#b-rulaje").split())
    assert av.startswith(FRAZA_LIPSA) and "«Sold inițial» arată soldul de la data preluării" in av, av
    assert _celule(pg, "371")[2] == "30.000,00"
    _declaratie_pas1(patron, firma_preluata["nume"], "d101", AN)
    pg.wait_for_selector("#dec-trimite, #dec-gol-da, .dec-eroare", timeout=90000)
    patron.captura("d101_fara_rulaje")
    t = " ".join(patron.fereastra().split())
    assert FRAZA_LIPSA in t and "cifra de afaceri, veniturile și cheltuielile anului" in t, t[:3000]
