# -*- coding: utf-8 -*-
"""[lotul 10, comanda Costin 10.2 pct.7h, 7i și 7k] Registrul jurnal — „Notă nouă” și nota fără document.

  7h. „Notă nouă în Registru jurnal: câmpul Sumă vine precompletat cu «0,00»; câmpurile de sumă sunt goale.”
      Cauza: linia implicită a notei noi avea `suma: 0`, iar editorul scria `value="${l.suma.toFixed(2)}"` -> „0.00” (afișat „0,00”).
      Acum suma notei noi e goală (placeholder „sumă”, ca „debit” / „credit”), iar „Salvează” cu suma goală o cere lângă câmp, în loc
      s-o trimită drept 0 (serverul ar fi spus „linia 1 are suma 0”, o sumă pe care omul n-a scris-o).
  7i. 394: „fereastra «Notă nouă» din Registru jurnal încă se derulează vertical.” Cauza: formularul notei noi stătea deasupra listei
      notelor lunii, în aceeași fereastră (cu tabel, înaltă cât ecranul — DS cap.9 v2.96); cu note în lună, fereastra derula. Proba din
      lotul 9 (`e2e_lot91::test_def_394_*`) folosea o firmă FĂRĂ note, deci n-a văzut cazul. Acum, cât se scrie nota nouă, fereastra
      arată antetul registrului și formularul — lista și totalurile revin după „Salvează” / „Renunță”.
  7k. 386: „în Registru jurnal, la nota fără document, același mesaj apare de două ori (stânga și dreapta).” Caseta de pe rând (stânga)
      și confirmarea de la „Validează” (dreapta). Acum un singur mesaj, pe rând; „Validează” inactiv, legat de el (gard în
      `core/test_jurnal_fara_document.py`; aici: numărul mesajelor de pe rând după clic).

Temei: N/A — UI (DS cap.9 „Ferestre de lucru”: „Nicio fereastră nu iese din ecran”, v2.92 285: „nicio fereastră nu are derulare;
acțiunea principală […] se vede mereu”; cap.1 „Butonul dezactivat arată dezactivat”).

Pe COMPORTAMENT (`core/test_garzi_pe_text.py`): `firme.ecranJurnal` real, montat în Chromium într-o fereastră cu tabel (`fer-tabel`) cu
stil.css real, la 1366×768, rutele simulate.
MUTAȚII: `suma: null` -> `suma: 0` (7h pică: „0.00”); lista notelor afișată și sub nota nouă (7i pică: corpul derulează).
"""
import functools
import http.server
import json
import os
import socketserver
import threading

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _nota(i, document=None):
    return {"id": 100 + i, "nr_curent": i, "data": "2026-09-%02d" % (i + 1), "numar": None, "descriere": "Notă de probă %d" % i,
            "sursa": "manual", "status": "ciorna", "factura_id": None, "document_ref": document, "document": document,
            "linii": [{"debit": "627", "credit": "5121", "suma": 12.5 + i, "centru_cost_id": None, "centru_nume": None},
                      {"debit": "4111", "credit": "704", "suma": 121.0, "centru_cost_id": None, "centru_nume": None}]}


NOTE = [_nota(i, None if i == 1 else "Extras bancar nr. %d" % i) for i in range(1, 9)]   # 8 note: lista derulează singură

MOUNT = """async ([modUrl, an, luna, regim]) => {
  document.head.innerHTML = '<link rel="stylesheet" href="/static/stil.css">';
  await new Promise((gata) => { document.head.querySelector('link').onload = gata; });
  document.body.innerHTML = `<div class="fereastra-overlay"><div class="fereastra fer-tabel" role="dialog">
    <div class="fereastra-antet"><button class="nav-sageata nav-inapoi">←</button><span class="fereastra-fir">Firme</span>
      <span class="fereastra-spatiu"></span><button class="nav-x">✕</button></div>
    <div class="fereastra-corp" tabindex="0"></div></div></div>`;
  const m = await import(modUrl);
  await m.ecranJurnal(document.querySelector('.fereastra-corp'), { deschide(){}, inapoi(){}, setInapoi(){} },
                      { id: 1, nume: "Firma", regim_contabil: regim || "dubla" }, { an: an || 2026, luna: luna || 9 });
  return true;
}"""


@pytest.fixture(scope="module")
def pagina():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    br = _lanseaza_chromium(pw)
    if br is None:
        pw.stop()
        srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    cereri = []

    def h(route, request):
        url = request.url.split("?")[0]
        if request.method == "POST" and url.endswith("/jurnal"):
            cereri.append(json.loads(request.post_data or "{}"))
            return route.fulfill(status=200, content_type="application/json", body='{"id": 999}')
        corp = {"note": NOTE, "total_debit": 0, "total_credit": 0, "note_fara_document": 1, "ciorne": {"note": 8, "total": 1000}} \
            if url.endswith("/jurnal") else {"centre": []} if url.endswith("/centre-cost") else {"blocate": []}
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(corp))

    pg = br.new_page(viewport={"width": 1366, "height": 768})
    pg.route("**/tenants/**", h)
    pg.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    try:
        yield pg, cereri
    finally:
        br.close()
        pw.stop()
        srv.shutdown()


def _deschide_nota_noua(pg, an=None, luna=None, regim=None):
    pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js", an, luna, regim])
    pg.wait_for_selector("#j-nota-noua", timeout=15000)
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-salveaza", timeout=5000)
    pg.wait_for_timeout(200)


def test_7h_suma_notei_noi_e_goala(pagina):
    pg, _ = pagina
    _deschide_nota_noua(pg)
    # 10.2 pct.7h: „câmpul Sumă vine precompletat cu «0,00»; câmpurile de sumă sunt goale.”
    assert pg.input_value("#je-linii .je-sum") == ""
    pg.click("#je-plus")
    assert [pg.eval_on_selector_all("#je-linii .je-sum", "e => e.map((x) => x.value)")][0] == ["", ""]
    # nimic din formular nu arată „0,00” (nici ca valoare, nici ca text de sugestie)
    assert "0,00" not in pg.eval_on_selector_all("#je-linii .je-sum", "e => e.map((x) => x.value + '|' + x.placeholder).join(' ')")


def test_7h_suma_goala_e_ceruta_langa_camp_nu_trimisa_drept_zero(pagina):
    pg, cereri = pagina
    _deschide_nota_noua(pg)
    pg.fill("#je-doc", "Chitanță nr. 5 din 01.09.2026")
    pg.fill("#je-linii .je-deb", "6022")
    pg.fill("#je-linii .je-cre", "5311")
    n0 = len(cereri)
    pg.click("#je-salveaza")
    pg.wait_for_timeout(300)
    # suma necompletată nu pleacă drept 0: refuzul stă lângă câmpul ei, iar nicio cerere nu pleacă
    assert len(cereri) == n0, cereri[n0:]
    assert pg.eval_on_selector("#je-linii .je-sum", "e => e.classList.contains('camp-invalid')")
    # mesajul stă lângă câmpul sumei (`eroareCamp`: `.msg-eroare` legat de câmp prin `data-camp`), numai pe linia cu suma goală
    assert pg.eval_on_selector_all("#je-linii .msg-eroare", "e => e.map((x) => [x.dataset.camp, x.textContent.trim() !== ''])") == [
        ["je-sum-0", True]]
    pg.fill("#je-linii .je-sum", "45")
    pg.click("#je-salveaza")
    pg.wait_for_timeout(300)
    assert len(cereri) == n0 + 1 and cereri[-1]["linii"][0]["suma"] == 45, cereri[n0:]


@pytest.mark.parametrize("luna_curenta, regim", [(False, "dubla"), (True, "simpla")])
def test_7i_394_fereastra_notei_noi_nu_deruleaza(pagina, luna_curenta, regim):
    """Cazul cel mai înalt: luna în curs (rândul „Amortizarea lunii se generează după ce luna se încheie.”) și partida simplă (rândul
    „notele sunt interne”)."""
    import datetime
    pg, _ = pagina
    azi = datetime.date.today()
    _deschide_nota_noua(pg, azi.year if luna_curenta else None, azi.month if luna_curenta else None, regim)
    m = pg.evaluate("""() => { const c = document.querySelector('.fereastra-corp'), s = document.querySelector('#je-salveaza');
      return {sh: c.scrollHeight, ch: c.clientHeight, jos_salveaza: s.getBoundingClientRect().bottom, jos_corp: c.getBoundingClientRect().bottom,
              note: document.querySelectorAll('[data-nota-id]').length}; }""")
    # 10.2 pct.7i (394): „fereastra «Notă nouă» din Registru jurnal încă se derulează vertical.” — cu 8 note în lună, la 1366×768
    assert m["sh"] <= m["ch"] + 1 and m["jos_salveaza"] <= m["jos_corp"], m
    # linia notei stă pe un rând (debit = credit · sumă · centru · partener · −), nu pe trei, cum o rupea lista îngustă (640 px)
    assert len(set(pg.eval_on_selector_all("#je-linii > div > *", "e => e.map((x) => Math.round(x.getBoundingClientRect().top + x.getBoundingClientRect().height / 2))"))) == 1
    pg.click("#je-renunta")
    pg.wait_for_selector("[data-nota-id]", timeout=5000)
    # după „Renunță” registrul arată din nou notele lunii (și derulează: lista e lungă)
    assert pg.eval_on_selector_all("[data-nota-id]", "e => e.length") == 8


def test_7k_386_un_singur_mesaj_dupa_clic_pe_validare(pagina):
    pg, _ = pagina
    pg.evaluate(MOUNT, ["/static/js/ecrane/firme.js", None, None, None])
    pg.wait_for_selector("[data-nota-id='101'] [data-val]", timeout=15000)
    pg.eval_on_selector("[data-nota-id='101'] [data-val]", "b => b.click()")
    pg.wait_for_timeout(300)
    t = pg.inner_text(".fereastra-corp")   # [lotul 12, 617] explicația o dată, deasupra tabelului de note
    # 10.2 pct.7k: „același mesaj apare de două ori (stânga și dreapta)” — după clic, tot un singur mesaj
    assert t.count("nu se validează fără documentul din care provine") == 1 and pg.query_selector("#caseta-atentie-activa") is None, t
