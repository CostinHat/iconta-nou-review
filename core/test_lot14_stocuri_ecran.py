# -*- coding: utf-8 -*-
"""[lotul 14, deficiența 696 + 687] Ecranul Stocuri (real, `firme.ecranStocuri`) arată stocul VALIDAT, ciorna separat, gestiunea articolului și
reconcilierea cu balanța în carduri-rezumat (comanda Costin 14.1: „Fereastra arată stocul validat (egal cu 371 …) și separat ce e în ciornă, cu
reconcilierea față de balanță. Tot aici: articol dublat („grau” 200 kg și 10 kg) fără coloana de gestiune; fracțiune la UM „buc”; nume de articol
fără diacritice și cu literă mică.”). Rutele simulate; cifrele sunt cele ale serverului (`test_lot14_stocuri_validat.py`).
MUTAȚII: cardurile scoase din `ecranStocuri` -> pică; tabelul pe valoarea întreagă (cu ciorna) în loc de cea validată -> pică.
"""
import json

import pytest

from core.test_stocuri_situatie import MOUNT, br  # noqa: F401 — harness-ul ecranului Stocuri

ARTS = [
    {"id": 1, "denumire": "Grâu", "um": "kg", "stoc": "210.000", "valoare": "420.00", "cmp": "2.0000", "stoc_validat": "200.000", "valoare_validata": "400.00",
     "cmp_validat": "2.0000", "valoare_ciorna": "20.00", "miscari_ciorna": 1, "locatii": ["Depozit 1"], "observatii": []},
    {"id": 2, "denumire": "grau", "um": "kg", "stoc": "10.000", "valoare": "20.00", "cmp": "2.0000", "stoc_validat": "0.000", "valoare_validata": "0.00",
     "cmp_validat": None, "valoare_ciorna": "20.00", "miscari_ciorna": 1, "locatii": ["Depozit 2"],
     "observatii": [{"fel": "litera_mica", "text": "denumirea începe cu literă mică"}, {"fel": "fara_diacritice", "text": "fără diacritice: grau → grâu"}]},
    {"id": 3, "denumire": "Cafea boabe", "um": "buc", "stoc": "2.500", "valoare": "25.00", "cmp": "10.0000", "stoc_validat": "2.500", "valoare_validata": "25.00",
     "cmp_validat": "10.0000", "valoare_ciorna": "0.00", "miscari_ciorna": 0, "locatii": [],
     "observatii": [{"fel": "fractie_um", "text": "cantitate cu zecimale (2,5) la unitatea „buc”, care nu se fracționează"}]},
]
REC = [{"cont": "371", "sold_contabil": "400.00", "valoare_validata": "425.00", "valoare_ciorna": "40.00", "diferenta": "-25.00", "ok": False, "necalculat": 0}]


def _pagina(b, port, rec):
    def h(route, request):
        url = request.url.split("?")[0]
        if url.endswith("/stocuri/articole"):
            corp = {"articole": ARTS, "retete_vizibile": False, "reconciliere": rec,
                    "dubluri": [{"denumire": "Grâu", "articole": [1, 2]}]}
        elif url.endswith("/stocuri/nir"):
            corp = {"nir": [{"id": 5, "numar": "N1", "data": "2026-10-03", "furnizor": "Furnizor SRL", "cost_total": "100", "metoda_stoc": "cantitativ_valoric"}]}
        elif url.endswith("/firma-profil/date"):
            corp = {"profil": {"metoda_stoc": "cantitativ_valoric"}}
        else:
            corp = {}
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(corp))
    pg = b.new_page(viewport={"width": 1366, "height": 768})
    pg.route("**/tenants/**", h)
    pg.goto("http://127.0.0.1:%d/static/" % port)
    pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js"])
    pg.wait_for_selector("#s-situatie-tabel", timeout=15000)
    pg.wait_for_selector("#s-carduri .card-rezumat", timeout=15000)
    return pg


def test_tabelul_arata_stocul_validat_ciorna_separat_si_gestiunea(br):
    """Grâu: 200 kg validat (400,00), 20,00 în ciornă; „grau” (alt rând, altă gestiune): 0 validat, 20,00 în ciornă; Cafea: 2,5 buc. Totalul e
    al valorii validate (425,00), ciorna (40,00) alături, nu în total."""
    b, port = br
    pg = _pagina(b, port, REC)
    randuri = pg.eval_on_selector_all("#s-situatie-tabel tbody tr", "e => e.map(r => [...r.cells].map(c => c.innerText.trim()))")
    assert randuri[0] == ["Grâu", "kg", "Depozit 1", "200", "2,00", "400,00", "20,00"], randuri
    assert randuri[1][:3] == ["grau", "kg", "Depozit 2"] and randuri[1][5] == "0,00" and randuri[1][6] == "20,00", randuri
    assert pg.eval_on_selector("#s-situatie-tabel tfoot", "e => e.innerText.replace(/\\s+/g, ' ').trim()") == "Total valoare stoc validat 425,00 40,00"


def test_cardurile_spun_reconcilierea_ciornele_si_articolele_de_verificat(br):
    """Reconcilierea cu balanța (diferență: fișele cu 25,00 lei mai mult), ciornele (2 mișcări, 40,00 lei), articolele de verificat și NIR-urile
    lunii: fiecare un card-rezumat (buton), iar cel al reconcilierii se deschide în fereastra lui, cu tabelul pe cont. Când reconcilierea
    se potrivește, cardul spune „=” cu cifra. MUTAȚIE: `carduriStocuri` scos din `ecranStocuri` -> nu există carduri -> pică."""
    b, port = br
    pg = _pagina(b, port, REC)
    carduri = pg.eval_on_selector_all("#s-carduri .card-rezumat", "e => e.map(x => [x.tagName, x.dataset.card, x.innerText.trim()])")
    assert [c[:2] for c in carduri] == [["BUTTON", "reconciliere"], ["BUTTON", "ciorne"], ["BUTTON", "articole"], ["BUTTON", "nir"]], carduri
    assert "cont 371, fișele cu 25,00 lei mai mult" in carduri[0][2], carduri
    assert "2 mișcări de stoc în ciornă" in carduri[1][2] and "40,00 lei" in carduri[1][2], carduri
    assert "2 articole de verificat" in carduri[2][2] or "3 articole de verificat" in carduri[2][2], carduri
    pg.click("[data-card='reconciliere']")
    pg.wait_for_selector(".fer-proba .fd-tabel", timeout=5000)
    assert "Sold în balanță" in pg.inner_text(".fer-proba") and "25,00" in pg.inner_text(".fer-proba")
    pg.close()
    pg = _pagina(b, port, [{"cont": "371", "sold_contabil": "425.00", "valoare_validata": "425.00", "valoare_ciorna": "40.00", "diferenta": "0.00", "ok": True, "necalculat": 0}])
    c0 = pg.inner_text("[data-card='reconciliere']")
    assert "425,00" in c0 and "balanța 371" in c0 and "✓" in c0, c0
