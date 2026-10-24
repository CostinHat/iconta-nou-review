# -*- coding: utf-8 -*-
"""Lotul 12, pachetul `inapoi` — C140 (găsită de Code la 485): săgeata înapoi a aplicației sărea peste pașii interni ai unui ecran
(`nav.setInapoi`) când ecranul era a doua fereastră sau era deschis într-un pas. Regula: DESIGN_SYSTEM.md cap.3 — „Săgeata portocalie duce
MEREU exact un pas înapoi în ierarhia ecranului.”

  * Contracte (a doua fereastră, peste fereastra firmei): „+ Șablon nou” -> editorul -> „←” = lista șabloanelor, nu fereastra firmei;
  * Migrare cabinet -> Firme (a treia fereastră): CUI-urile lipite -> „Validează la ANAF” -> „←” = lista lipită; încă un „←” = meniul
    Migrare cabinet, cu drumul „Firme” (nu „Firme › Migrare cabinet”: meniul nu se desenează în fereastra „Firme”);
  * fereastra firmei -> Import date -> Solduri inițiale (pas) -> balanța -> previzualizarea -> „←” = alegerea fișierului, în același pas;
    „←” = meniul „Import date” al firmei (nu lista firmelor din Migrare cabinet); „←” = fereastra firmei.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`). CUI-ul de probă 14399841 are cifra de control
GREȘITĂ, verificată cu algoritmul din CLAUDE.md (corect: 14399840, DANTE INTERNATIONAL SA) — nu pleacă la ANAF. Temei fiscal: N/A — regulă
de produs (DS cap.3). Balanța de probă e echilibrată (debit 11.000,00 = credit 11.000,00) și nu se salvează."""
import pytest

from conftest import firma_noua, sql
from e2e_lot5_migrare import _migrare

SAGEATA = ".fereastra .nav-inapoi"
BALANTA = ("cont;denumire;sold debitor;sold creditor\n1012;Capital subscris vărsat;0;10000\n121;Profit sau pierdere;1000;0\n"
           "401;Furnizori;0;1000\n5121;Conturi la bănci în lei;9500;0\n5311;Casa în lei;500;0\n").encode("utf-8")


def balanta():
    """Balanța de probă (octeți), și pentru dovezile pe firmele de test (`frontend_test/dovada/dovezi_lot12_inapoi.json`)."""
    return BALANTA


@pytest.fixture(scope="module")
def firma_c140():
    for f in firma_noua():
        yield f


def _fereastra(pg):
    """(titlul ferestrei din față, drumul ei) — ce vede contabilul în antet."""
    return pg.evaluate("() => { const f = document.querySelector('.fereastra'); return f ? [f.getAttribute('aria-label'), "
                       "[...f.querySelectorAll('.fereastra-fir .fir-veriga')].map((b) => b.innerText.trim())] : null; }")


def _inapoi(pg, asteapta, stare="visible"):
    pg.click(SAGEATA)
    pg.wait_for_selector(asteapta, state=stare, timeout=30000)
    pg.wait_for_timeout(300)


def test_def_c140_contracte_sageata_din_editor_intoarce_la_lista_sabloanelor(patron, firma_c140):
    """C140 pe Contracte. Pașii: fereastra firmei -> Contracte -> „+ Șablon nou” -> numele tastat -> „←”: lista șabloanelor („+ Șablon
    nou”), tot în fereastra Contracte, fără șablon salvat; „←”: fereastra firmei."""
    pg = patron.pg
    patron.firma(firma_c140["nume"])
    pg.click("#fa-contracte")
    pg.wait_for_selector("#c-nou", timeout=25000)
    pg.click("#c-nou")
    pg.wait_for_selector("#c-salveaza", timeout=25000)
    pg.fill("#c-nume", "Șablon C140")
    patron.captura("editor")
    assert _fereastra(pg)[0] == "Contracte"
    _inapoi(pg, "#c-nou")
    patron.captura("inapoi_lista")
    titlu, _drum = _fereastra(pg)
    assert titlu == "Contracte", titlu                                      # DS cap.3: un pas înapoi, în fereastra Contracte
    assert pg.locator("#c-salveaza").count() == 0 and "Contracte" in patron.fereastra()
    assert sql('SELECT count(*) FROM "%s".contracte_sabloane' % firma_c140["schema"])[0][0] == 0   # „←” nu salvează
    _inapoi(pg, "#fa-facturi")
    patron.captura("inapoi_firma")


def test_def_c140_migrare_firme_sageata_din_rezultate_intoarce_la_lista_lipita(patron):
    """C140 în Migrare cabinet -> Firme. Pașii: CUI 14399841 lipit -> „Validează la ANAF” -> lista rezultatelor -> „←”: ecranul cu lista
    lipită („Validează la ANAF”), în fereastra „Firme”; „←”: meniul Migrare cabinet, cu drumul „Firme” (fără o fereastră în plus)."""
    pg = patron.pg
    _migrare(patron)
    drum_meniu = _fereastra(pg)
    pg.locator("#mig-meniu .mig-op", has_text="Firme").first.click()
    pg.wait_for_selector("#mig-text", timeout=20000)
    pg.fill("#mig-text", "14399841")
    pg.click("#mig-valideaza")
    pg.wait_for_selector("#mig-lista .mig-rand", timeout=60000)
    patron.captura("rezultate")
    _inapoi(pg, "#mig-valideaza")
    patron.captura("inapoi_lista_lipita")
    assert _fereastra(pg)[0] == "Firme" and pg.locator("#mig-lista").count() == 0
    _inapoi(pg, "#mig-meniu")
    patron.captura("inapoi_meniu")
    assert _fereastra(pg) == drum_meniu == ["Migrare cabinet", ["Firme"]], (_fereastra(pg), drum_meniu)


def test_def_c140_migrare_pe_firma_sageata_din_previzualizare_intoarce_la_alegerea_fisierului(patron, firma_c140):
    """C140 în asistenții migrării pe firmă. Pașii: fereastra firmei -> Import date -> Solduri inițiale -> balanța (CSV) -> previzualizarea
    („Salvează soldurile”) -> „←”: alegerea fișierului („Încarcă balanța”), în pasul „Solduri inițiale”; „←”: meniul „Import date” al
    firmei („Alege ce vrei să aduci pentru această firmă.”), nu lista firmelor din Migrare cabinet; „←”: fereastra firmei."""
    pg = patron.pg
    patron.firma(firma_c140["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand", has_text="Solduri inițiale").first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)
    pg.set_input_files("#mig-file", files=[{"name": "balanta_c140.csv", "mimeType": "text/csv", "buffer": balanta()}])
    pg.wait_for_selector("#mig-salveaza-sold", timeout=30000)
    patron.captura("previzualizare")
    _inapoi(pg, "#mig-file", stare="attached")
    patron.captura("inapoi_alegere_fisier")
    assert _fereastra(pg)[0] == "Solduri inițiale" and pg.locator("#mig-salveaza-sold").count() == 0
    assert "Încarcă balanța" in patron.fereastra() and firma_c140["nume"] in patron.fereastra()
    _inapoi(pg, ".mig-frand")
    patron.captura("inapoi_import_date")
    assert _fereastra(pg)[0] == "Import date", _fereastra(pg)
    assert "Alege ce vrei să aduci pentru această firmă." in patron.fereastra()
    _inapoi(pg, "#fa-facturi")
    patron.captura("inapoi_firma")


@pytest.mark.parametrize("card, lista, formular, deschide, titlu", [
    ("acces", "#ac-btn-invita", "#ac-email", "#ac-btn-invita", "Acces client"),
    ("magazin", "#wc-btn-config", "#wc-url", "#wc-btn-config", "Magazin online"),
])
def test_def_c140_acces_client_si_magazin_sageata_din_formular_intoarce_la_ecranul_ferestrei(patron, firma_c140, card, lista, formular,
                                                                                                deschide, titlu):
    """C140, aceeași clasă (ecran care se redesenează pe loc, pe a doua fereastră). Pașii: fereastra firmei -> „Acces client” -> „Invită client
    nou” (formularul) -> „←”: ecranul Acces client; „Magazin online” -> „Configurează magazinul” -> „←”: ecranul Magazin online; încă un
    „←”: fereastra firmei."""
    pg = patron.pg
    patron.firma(firma_c140["nume"])
    pg.click("#fa-" + card)
    pg.wait_for_selector(lista, timeout=25000)
    pg.click(deschide)
    pg.wait_for_selector(formular, timeout=25000)
    patron.captura(card + "_formular")
    _inapoi(pg, lista)
    patron.captura(card + "_inapoi")
    assert _fereastra(pg)[0] == titlu and pg.locator(formular).count() == 0, _fereastra(pg)
    _inapoi(pg, "#fa-facturi")
