# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.3 pct.6 — pachetul „decl3”: C19, rectificativa D394 pe o perioadă deja depusă, pe aplicația din index, pe
baza de TEST, pe o firmă NOUĂ (`firma_noua`).

Verbatim (DECIZII „Comanda 12.3”): „C19: rectificativa D394 pentru o perioadă deja depusă se generează doar la cererea contabilului, cu
diferențele față de cea depusă arătate înainte; niciodată automat.”

DATE DE PORNIRE fără ecran (declarate, `# date-de-pornire` pe linie): facturile se scriu în schema firmei noi (SQL, ca `e2e_lot12_decl.py`
— ecranul probat e Declarații, nu emiterea), iar depunerea la ANAF a declarației inițiale e rândul ei din `public.declaratii_depuse`, cu
XML-ul generat chiar pe ecran la pasul 1 (o depunere la ANAF nu se poate produce din plasă). CUI-uri cu cifra de control verificată
(algoritmul din CLAUDE.md): 2864518, 1590082.

Temei (citat pe linia aserțiunii): OPANAF 2194/2025 anexa nr.2 pct.3 — declarația nouă „înlocuieşte declaraţia informativă depusă
iniţial”; D394 n-are marcaj de rectificativă în XML (D394Validator v5)."""
import pytest

from conftest import firma_noua, sql
from core.common import cate
from e2e_lot12_decl import _factura, _pasul2, _profil, _validat_duk, _xml

_F = ".fereastra:last-of-type "


@pytest.fixture()
def firma_c19():
    for f in firma_noua():
        try:
            yield f
        finally:
            sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd394'", (f["tenant_id"],))


def _pasul2_d394(patron, firma):
    """Firma -> Declarații -> D394 -> 06/2026 -> „Continuă →”: pasul 2 — declarația generată SAU ecranul perioadei deja depuse."""
    from conftest import alege_perioada, alege_tipul
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(firma["nume"])
    _card(patron, "declaratii", "#dec-tip")
    alege_tipul(pg, "d394", zona=_F)
    alege_perioada(pg, 2026, 6, zona=_F)
    pg.click(_F + "#dec-continua")
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && f.innerText.includes("
                         "'Pasul 2 din 3') && !!f.querySelector('#dec-rect-depusa, .dec-ok, .dec-avert, .dec-eroare, #dec-trimite'); }",
                         timeout=120000)
    return pg


def _text(pg, sel):
    return " ".join(pg.inner_text(_F + sel).split()) if pg.locator(_F + sel).count() else ""


def _coada_d394(firma):
    return sql("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd394'", (firma["tenant_id"],))[0][0]


def test_def_c19_rectificativa_d394_numai_la_cerere_dupa_diferente(patron, firma_c19):
    """C19. Pașii contabilului: firma are în 06/2026 o vânzare către ALTEX -> Declarații -> D394, 06/2026 -> „Continuă”: declarația inițială
    (validată de DUK, fără mențiune de rectificativă); ea e depusă la ANAF (20.07.2026).
      1. Declarații -> D394, 06/2026 -> „Continuă”, fără nicio schimbare: „declarația generată acum din datele firmei e identică cu
         declarația depusă …: nu se generează nicio declarație” — fără tabel, fără „Generează declarația rectificativă”, fără „Trimite în coadă”.
      2. Se emite în iunie o factură către CLIENT DOI SRL (500 lei + TVA 21%) -> D394, 06/2026 -> „Continuă”: ecranul spune că perioada e
         depusă, arată diferențele (secțiune / rând / câmp: depus -> nou; rândul nou al lui CLIENT DOI în lista C) și NU generează nimic:
         nici XML, nici „Trimite în coadă”, nimic în coadă.
      3. „Generează declarația rectificativă →”: declarația se generează (mențiunea „Rectificativă: înlocuiește declarația depusă prin iConta.eu pe
         20.07.2026.”), conține factura nouă și trece validatorul ANAF; nimic n-a intrat singur în coadă."""
    pg = patron.pg
    tid = firma_c19["tenant_id"]
    _profil(patron, firma_c19)
    _factura(firma_c19, "E19", "1", "2026-06-10", "emisa", "RO2864518", "ALTEX ROMANIA SRL", [(1000, 21)], oras="Voluntari")
    pg = _pasul2(patron, firma_c19, "d394", 2026, 6)
    xml0 = _xml(pg)
    patron.captura("c19_initiala")
    assert "Validat cu DUKIntegrator" in _validat_duk(pg), patron.fereastra()[:2000]   # DUK D394 — judecătorul
    assert pg.locator(_F + "#dec-rectificativa").count() == 0 and 'denP="ALTEX ROMANIA SRL"' in xml0, xml0[:1500]
    # date-de-pornire: depunerea la ANAF a declarației inițiale (XML-ul de pe ecran) — o depunere nu se poate produce din plasă
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, sursa, data_depunere, nr_depunere) "
        "VALUES (%s, 2026, 6, 'd394', %s, 'iconta', '2026-07-20 10:00+03', 1)", (tid, xml0))
    coada0 = _coada_d394(firma_c19)

    # 1. fără diferențe: nu se generează nimic
    pg = _pasul2_d394(patron, firma_c19)
    patron.captura("c19_fara_diferente")
    assert _text(pg, "#dec-rect-depusa") == (
        "D394 pe 06/2026: declarația generată acum din datele firmei e identică cu declarația depusă prin iConta.eu pe 20.07.2026. Nu e "
        "nimic de rectificat, deci nu se generează nicio declarație."), patron.fereastra()[:2000]
    assert pg.locator(_F + "#dec-rect-genereaza, " + _F + "#dec-trimite, " + _F + "#dec-rect-diferente, " + _F + "details.dec-xml").count() == 0

    # 2. o factură nouă în iunie: diferențele, arătate înainte; nimic generat
    _factura(firma_c19, "E19", "2", "2026-06-20", "emisa", "RO1590082", "CLIENT DOI SRL", [(500, 21)], oras="Cluj-Napoca")
    pg = _pasul2_d394(patron, firma_c19)
    patron.captura("c19_diferente")
    caseta = _text(pg, "#dec-rect-depusa")
    # OPANAF 2194/2025 anexa nr.2 pct.3: declarația nouă „înlocuieşte declaraţia informativă depusă iniţial” — o cere contabilul
    assert caseta.startswith(
        "D394 pe 06/2026 e deja depusă (declarația depusă prin iConta.eu pe 20.07.2026). O rectificativă o înlocuiește integral (OPANAF "
        "2194/2025 anexa nr.2 pct.3) și se generează numai la cererea ta, din Declarații, după ce vezi diferențele față de cea depusă. "
        "Diferențele față de declarația depusă: "), caseta
    randuri = pg.eval_on_selector_all(_F + "#dec-rect-diferente tbody tr",
                                      "trs => trs.map(t => [...t.cells].map(c => c.innerText.replace(/\\s+/g, ' ').trim()))")
    assert caseta.endswith("Diferențele față de declarația depusă: %s." % cate(len(randuri), "rând", "rânduri")), (caseta, len(randuri))
    lista = "Secțiunea a 2-a, lista C — partener înregistrat în scopuri de TVA în România"
    rand = "L · CLIENT DOI SRL (1590082) · cota 21%"
    assert [lista, rand, "baza impozabilă (baza)", "—", "500"] in randuri, randuri
    assert [lista, rand, "TVA (tva)", "—", "105"] in randuri, randuri
    assert ["C. Rezumat — partener înregistrat în scopuri de TVA în România", "cota 21%", "baza impozabilă — livrări (bazaL)", "1000", "1500"] in randuri, randuri
    assert not [r for r in randuri if "ALTEX" in r[1]], randuri   # partenerul neschimbat nu apare
    assert pg.locator(_F + "#dec-trimite, " + _F + "details.dec-xml").count() == 0 and _coada_d394(firma_c19) == coada0

    # 3. la cererea contabilului: rectificativa
    pg.click(_F + "#dec-rect-genereaza")
    pg.wait_for_selector(_F + "#dec-rectificativa", timeout=120000)
    patron.captura("c19_rectificativa")
    assert _text(pg, "#dec-rectificativa") == "Rectificativă: înlocuiește declarația depusă prin iConta.eu pe 20.07.2026."
    xml1 = _xml(pg)
    assert 'denP="CLIENT DOI SRL"' in xml1 and 'denP="ALTEX ROMANIA SRL"' in xml1, xml1[:2000]   # declarația completă (pct.3)
    assert "Validat cu DUKIntegrator" in _validat_duk(pg), patron.fereastra()[:2000]
    assert pg.locator(_F + "#dec-trimite").count() == 1 and _coada_d394(firma_c19) == coada0   # niciodată automat: coada o cere omul
