# -*- coding: utf-8 -*-
"""GARD ÎN BROWSER — Registrul jurnal: o ciornă fără document justificativ se vede ÎNAINTE de validare, iar „Validează” pe ea
nu trimite validarea (comanda Costin 05.10.2026 pct.6: „validatorul trebuie să vadă lipsa înainte să apese”; din lotul 9, 386: regula
de fond R3 din bază refuză validarea fără document; din lotul 10, 10.2 pct.7k: un singur mesaj, pe rând, iar „Validează” e inactiv).

Pe COMPORTAMENT, nu pe sursă (`core/test_garzi_pe_text.py`): ecranul real (`firme.ecranJurnal`) montat în Chromium, cu
rutele simulate; se numără cererile de validare trimise. MUTAȚIE: „Validează” activ pe nota fără document -> pică.
"""
import functools
import http.server
import json
import os
import re
import socketserver
import threading

import pytest

from core.test_emitere_randuri_dinamice import _lanseaza_chromium

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = [
    {"id": 7, "nr_curent": 1, "data": "2026-10-05", "numar": None, "descriere": "Comision bancar", "sursa": "banca",
     "status": "ciorna", "factura_id": None, "document_ref": None, "document": None,
     "linii": [{"debit": "627", "credit": "5121", "suma": 12.5, "centru_cost_id": None, "centru_nume": None}]},
    {"id": 8, "nr_curent": 2, "data": "2026-10-05", "numar": None, "descriere": "Încasare", "sursa": "banca",
     "status": "ciorna", "factura_id": 3, "document_ref": "Extras bancar x.csv din 05.10.2026", "document": "Extras bancar x.csv din 05.10.2026",
     "linii": [{"debit": "5121", "credit": "4111", "suma": 121.0, "centru_cost_id": None, "centru_nume": None}]},
]

MOUNT = """async ([modUrl]) => {
  const m = await import(modUrl);
  document.body.innerHTML = '<div id="mount"></div>';
  await m.ecranJurnal(document.getElementById('mount'), { deschide(){}, inapoi(){}, setInapoi(){} }, { id: 1, nume: "Firma" });
  return true;
}"""


@pytest.fixture(scope="module")
def pagina():
    from playwright.sync_api import sync_playwright
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    br = _lanseaza_chromium(pw)
    if br is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    validari = []

    def h(route, request):
        url = request.url.split("?")[0]
        if url.endswith("/valideaza"):
            validari.append(url)
            return route.fulfill(status=200, content_type="application/json", body='{"ok": true}')
        corp = {"note": NOTE, "total_debit": 133.5, "total_credit": 133.5, "note_fara_document": 1} if url.endswith("/jurnal") \
            else {"centre": []} if url.endswith("/centre-cost") else {"blocate": []}
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(corp))

    pg = br.new_page()
    pg.route("**/tenants/**", h)
    pg.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js"])
    pg.wait_for_selector('[data-val="7"]', timeout=15000)
    try:
        yield pg, validari
    finally:
        br.close(); pw.stop(); srv.shutdown()


def test_lipsa_documentului_se_vede_pe_rand_inainte_de_validare(pagina):
    pg, _ = pagina
    # exact o casetă de avertizare, în detaliul notei fără document (nota 8 are extrasul) — [lotul 12, 617] tabelul de note: rândul e
    # `tbody[data-nota-id]`, explicația stă o dată deasupra tabelului (`#jn-expl-fara_doc`), iar pe rând semnul „fără document”
    assert pg.eval_on_selector_all(".jn-fara-doc", "e => e.length") == 1
    assert pg.eval_on_selector('[data-val="7"]', "b => !!b.closest('[data-nota-id]').querySelector('.jn-fara-doc')")
    assert not pg.eval_on_selector('[data-val="8"]', "b => !!b.closest('[data-nota-id]').querySelector('.jn-fara-doc')")
    assert pg.eval_on_selector_all("#jn-expl-fara_doc", "e => e.length") == 1


def test_validarea_fara_document_nu_se_ofera_iar_cu_document_pleaca(pagina):
    """PIVOT [386, lotul 9, retestul Costin 19.10.2026]: confirmarea „Validează fără document” (05.10.2026) promitea o validare pe care
    regula de fond R3 din bază (comanda Costin 09.10.2026 pct.11) o refuză.
    PIVOT [386, lotul 10, comanda 10.2 pct.7k]: „la nota fără document, același mesaj apare de două ori (stânga și dreapta)” — caseta de pe
    rând și confirmarea de la „Validează”. Acum: UN mesaj, pe rând, cu pasul care o face validabilă („Editează”); „Validează” e inactiv și
    legat de el (aria-describedby); clicul nu deschide nimic și nu trimite nimic. Nota cu document se validează direct."""
    pg, validari = pagina
    b = '[data-val="7"]'
    # [lotul 13, 675] inactiv cu motivul (`api.atributeInactiv`: aria-disabled + titlul), nu ascuns și nu `disabled` fără explicație
    assert pg.eval_on_selector(b, "b => b.getAttribute('aria-disabled') === 'true' && !!b.title"), "„Validează” se oferă pe nota fără document (R3 o refuză)"
    leg = pg.eval_on_selector(b, "b => b.getAttribute('aria-describedby')")
    # [lotul 12, 617] legat de pasul notei (din detaliul ei) și de explicația de deasupra tabelului
    # (că explicația poartă mesajul „nu se validează fără documentul din care provine” o arată, pe elemente, verificarea de mai jos)
    assert (leg or "").split() == ["jn-fara-doc-7", "jn-expl-fara_doc"], leg
    mesaj = " ".join(pg.eval_on_selector("#" + i, "e => e.textContent") for i in leg.split())
    # pasul numit în mesaj e chiar butonul de pe rândul notei: eticheta citată („…”) = textul butonului „Editează” al aceleiași note
    buton = pg.eval_on_selector(b, "b => { const e = b.closest('[data-nota-id]').querySelector('[data-edit=\"7\"]'); return e ? e.textContent.trim() : null; }")
    assert buton is not None and re.findall(r"\u201e([^\u201d]+)\u201d", mesaj) == [buton], (mesaj, buton)
    pg.eval_on_selector(b, "b => b.click()")   # clicul pe butonul inactiv: nimic nu se deschide, nimic nu pleacă
    pg.wait_for_timeout(300)
    # 10.2 pct.7k: „același mesaj apare de două ori (stânga și dreapta)” — pe rând e un singur mesaj, iar caseta de confirmare nu apare
    # [lotul 12, 617] „explicațiile o singură dată”: în toată fereastra, nu numai pe rând — mesajul stă, VIZIBIL, într-un singur element,
    # explicația de deasupra tabelului (se compară elementele care-l poartă, nu numărul de apariții în textul randat)
    locuri = pg.eval_on_selector_all("#mount *", """es => es.filter((e) => e.getClientRects().length && [...e.childNodes].some((n) =>
        n.nodeType === 3 && n.textContent.includes('nu se validează fără documentul'))).map((e) => e.id)""")
    assert locuri == ["jn-expl-fara_doc"], locuri
    assert pg.query_selector("#caseta-atentie-activa") is None
    assert validari == [], "validarea notei fără document a plecat (regula de fond R3 din bază o refuză)"
    pg.click('[data-val="8"]')
    pg.wait_for_timeout(300)
    assert len(validari) == 1 and validari[0].endswith("/jurnal/8/valideaza"), "nota cu document nu cere confirmare"
