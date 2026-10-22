# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 459 — CLASA „normalizare locală a CUI” (subagentul CF; decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda
10.3”: „CUI-ul se păstrează fără «RO» și fără spații; «RO» apare doar la afișare, după starea de plătitor de TVA.”).

Importul soldurilor pe parteneri avea normalizarea lui (`_curata_cui`: scotea numai spațiul obișnuit), iar triggerul bazei (`\\s` din
PostgreSQL) nu vede spațiul nedespărțitor (U+00A0) — cel care vine dintr-un fișier copiat de pe o pagină web / din Word („RO 185 47290”
cu NBSP). Codul ajungea în bază „185<NBSP>47290”: alt partener decât facturile lui „18547290”. Acum importul trece prin forma unică
(`cui_forma.stocare`).

Pașii: firma NOUĂ (`firma_noua`, pe baza de TEST) -> fereastra firmei -> Import date -> Solduri parteneri -> fișierul -> ecranul arată
codul „18547290” -> salvează -> în evidență, „18547290”. Date de PORNIRE scrise direct (aplicația le-ar produce la pasul „Balanță”, alt
import, deja probat în `e2e_lot10_migrare.py`): soldul contului 4111 la 31.12.2025, cu care importul partenerilor se confruntă. CUI-ul
18547290 are cifra de control verificată (algoritmul din CLAUDE.md; `core/test_lot11_cf_cui_forma_unica.py::test_cui_urile_de_test_sunt_valide`).
"""
import pytest

from conftest import firma_noua, sql

NBSP = " "


@pytest.fixture
def firma_cf():
    for f in firma_noua():
        yield f


def test_def_459_importul_partenerilor_pastreaza_cui_ul_fara_ro_si_fara_spatiu_nedespartitor(patron, firma_cf):
    pg, s = patron.pg, firma_cf["schema"]
    # date-de-pornire: balanța de deschidere (soldurile partenerilor se importă peste ea; testul e despre importul partenerilor)
    sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES '
        "('4111', 'Clienți', 250, 0, '2025-12-31'), ('1012', 'Capital', 0, 250, '2025-12-31')" % s)
    patron.firma(firma_cf["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand", has_text="Solduri parteneri").first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)
    continut = "cont;cui;denumire;sold debitor;sold creditor\n4111;RO 185%s47290;CLIENT NBSP SRL;250;0\n" % NBSP
    pg.set_input_files("#mig-file", files=[{"name": "parteneri.csv", "mimeType": "text/csv", "buffer": continut.encode("utf-8")}])
    pg.wait_for_selector("#mig-salveaza-part", timeout=30000)
    patron.captura("previzualizare")
    text = pg.inner_text("body")
    assert "18547290" in text, "ecranul nu arată codul în forma păstrată (18547290)"
    assert "185" + NBSP + "47290" not in text and "RO 185" not in text, "ecranul arată codul cu prefixul / spațiul din fișier"
    pg.click("#mig-salveaza-part")
    if pg.locator("#ca-ok").count():
        pg.click("#ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('salvat')", timeout=30000)
    patron.captura("salvat")
    assert sql('SELECT cui, sold_debitor FROM "%s".solduri_parteneri' % s) == [("18547290", 250)]
