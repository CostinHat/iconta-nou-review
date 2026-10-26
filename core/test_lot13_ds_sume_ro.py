# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1, grupa 1), deficiența 655 — sumele scrise în format românesc se citesc corect în TOATĂ aplicația.

Comanda, verbatim: „«1.000» scris în format românesc a fost înregistrat «bază 1,00 lei»: punctul de mii citit ca zecimal, fără
avertisment. De verificat în toată aplicația cum se citesc sumele cu punct de mii.” și „Aceeași eroare și în registrul de casă (F7,
dispoziție nouă): «1.500» scris în câmpul Suma e citit 1,50 lei […] Clasa e în formularele de zi cu zi, nu doar în D207: toate
câmpurile de sumă din aplicație.”

Cauza: `<input type="number">` al browserului citește punctul ca zecimală („1.000” = 1) și golește „1.000,50”; ecranele citeau `.value`
cu `parseFloat` / `Number`. Reparația (DS cap.6 „Numerele scrise de om”): regula unică `numarRo` (api.js) / `numere.numar_ro` (Python),
iar mecanismul din api.js face din orice câmp numeric un câmp românesc al cărui `.value` e numărul canonic.

CE FACE IMPOSIBIL (codul REAL, în Chromium pentru JS):
  1. cele două oglinzi ale regulii să spună altceva pe același text (aceleași exemple, mai jos);
  2. un câmp numeric desenat oricând (șablon, `createElement`) să citească „1.500” ca 1,5 sau să golească „1.000,50”;
  3. o valoare pusă din cod („4.975” — cursul, „10.000” — o cantitate NUMERIC(12,3) din server) să fie citită ca mii;
  4. un text care nu e număr să plece la server: câmpul se marchează, scrierea se oprește înainte de `fetch`;
  5. importurile (`numere.numar`) să citească „1.234.567” ca 0 (tăcut) sau „1.500” ca 1,5.

Temei: N/A — regulă de interfață (DS cap.6, „Numerele scrise de om”); nu e o valoare fiscală.
"""
import functools
import http.server
import os
import socketserver
import threading
from decimal import Decimal

import pytest

from core.numere import MESAJ_NUMAR_RO, numar, numar_ro
from core.test_emitere_randuri_dinamice import _lanseaza_chromium

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (textul scris de om, forma canonică așteptată; None = refuzat cu MESAJ_NUMAR_RO, "" = gol)
EXEMPLE = [
    ("1.000", "1000"),            # instanța D207: o mie, nu 1,00
    ("1.500", "1500"),            # instanța Casă: o mie cinci sute, nu 1,50
    ("1.000,50", "1000.50"),
    ("1500,5", "1500.5"),
    ("1 500,50", "1500.50"),
    ("-1.234,56", "-1234.56"),
    ("12.345.678,9", "12345678.9"),
    ("1.234.567", "1234567"),
    ("0,5", "0.5"),
    (",5", "0.5"),
    ("1.000,", "1000"),
    ("1234.56", "1234.56"),       # punct urmat de 2 cifre: nu poate fi separator de mii -> zecimală
    ("4.9750", "4.9750"),         # 4 cifre după punct -> zecimală (cursul copiat)
    ("0.500", "0.500"),           # „0.” nu începe un grup de mii -> zecimală
    ("1,234.56", "1234.56"),      # scrierea englezească, cu amândoi separatorii
    ("", ""),
    ("   ", ""),
    ("12a", None),
    ("1.23.4", None),
    ("1,2,3", None),
    ("1.2345,6", None),
    ("abc", None),
    ("--5", None),
]


@pytest.mark.parametrize("text,asteptat", EXEMPLE)
def test_regula_python(text, asteptat):
    """1. MUTAȚIE: ramura `_RE_MII` scoasă din `numar_ro` -> „1.000” = 1 -> pică."""
    if asteptat is None:
        with pytest.raises(ValueError) as e:
            numar_ro(text)
        assert str(e.value) == MESAJ_NUMAR_RO
    elif asteptat == "":
        assert numar_ro(text) is None
    else:
        assert numar_ro(text) == Decimal(asteptat), (text, numar_ro(text))


def test_importurile_citesc_aceeasi_regula():
    """5. `numere.numar` (importurile) — „1.234.567” era 0 (float pe „1.234.567” -> ValueError -> 0 tăcut), „1.500” era 1,5."""
    assert numar("1.234.567") == 1234567
    assert numar("1.500") == 1500
    assert numar("1.234,56 RON") == 1234.56
    assert numar("(1.500)") == -1500
    assert numar("1,234.56") == 1234.56


@pytest.fixture(scope="module")
def pg():
    from playwright.sync_api import sync_playwright
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    p = b.new_page()
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    p.evaluate("async () => { window.A = await import('/static/js/api.js'); }")
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


def test_regula_js_e_aceeasi_cu_python(pg):
    """1. Oglinda JS dă aceeași formă canonică pe fiecare exemplu. MUTAȚIE: `_RE_MII` scos din `numarRo` -> pică."""
    r = pg.evaluate("(ex) => ex.map(([t]) => { const x = A.numarRo(t); return x.eroare ? null : x.canonic; })", EXEMPLE)
    asteptat = [a for _t, a in EXEMPLE]
    assert r == asteptat, [(t, x, a) for (t, a), x in zip(EXEMPLE, r) if x != a]
    assert pg.evaluate("() => A.MESAJ_NUMAR_RO") == MESAJ_NUMAR_RO


_FORMULAR = """() => {
  document.body.innerHTML = `<div class="fereastra"><div class="fereastra-corp">
    <label class="camp"><span class="camp-eticheta">Suma</span><input type="number" step="0.01" id="s" class="camp-input"></label>
    <label class="camp"><span class="camp-eticheta">Curs</span><input type="number" step="0.0001" id="curs" class="camp-input" value="4.975"></label>
    <label class="camp"><span class="camp-eticheta">Cantitate</span><input type="number" id="cant" class="camp-input"></label>
    <label class="camp"><span class="camp-eticheta">Preț</span><input id="pret" class="camp-input" inputmode="decimal" value="12.50"></label>
    <p><button class="buton-primar" id="salveaza" data-actiune="POST /x">Salvează</button></p><div id="m"></div>
  </div></div>`;
  return new Promise((r) => setTimeout(r, 30));
}"""


def test_campul_numeric_citeste_romaneste(pg):
    """2 + 3. MUTAȚIE: `Object.defineProperty(inp, "value", …)` scos din `campNumericRo` -> „1.500” = 1,5 / „1.000,50” = gol -> pică.
    MUTAȚIE: `_canonicDinCod` -> `numarRo(s).canonic` -> cursul „4.975” din șablon citit 4975 -> pică."""
    pg.evaluate(_FORMULAR)
    pg.fill("#s", "1.500")
    pg.fill("#cant", "1.000,50")
    r = pg.evaluate("""() => {
      const s = document.getElementById('s'), curs = document.getElementById('curs'), cant = document.getElementById('cant');
      const pret = document.getElementById('pret');
      const dinCod = document.createElement('input'); dinCod.type = 'number'; dinCod.id = 'cod';
      document.querySelector('.fereastra-corp').appendChild(dinCod);
      return new Promise((rez) => setTimeout(() => {
        dinCod.value = '10.000';                     // cantitatea NUMERIC(12,3) venită din server
        rez({ s: s.value, sNr: parseFloat(s.value), sTip: s.type, sMod: s.getAttribute('inputmode'),
              curs: curs.value, cursText: curs.getAttribute('value'), cant: cant.value, pret: pret.value,
              cod: dinCod.value, codText: A.textCamp(dinCod), sText: A.textCamp(s) });
      }, 30));
    }""")
    assert r["s"] == "1500" and r["sNr"] == 1500 and r["sText"] == "1.500", r      # instanța Casă: 1.500 = o mie cinci sute
    assert r["sTip"] == "text" and r["sMod"] == "decimal", r                       # tastatura numerică rămâne pe telefon
    assert r["cant"] == "1000.50", r                                               # „1.000,50” nu mai e golit
    assert r["curs"] == "4.975" and r["cursText"] == "4,975", r                    # cursul din șablon: zecimală, arătat românește
    assert r["pret"] == "12.50", r
    assert r["cod"] == "10.000" and r["codText"] == "10,000", r                    # valoarea pusă din cod e un număr, nu mii


def test_textul_care_nu_e_numar_nu_pleaca_la_server(pg):
    """4. MUTAȚIE: `if (gresit) throw gresit;` scos din `cere` -> cererea pleacă (fetch apelat, cu suma goală) -> pică. MUTAȚIE:
    marcajul de la părăsire scos -> nicio eroare lângă câmp după `change` -> pică."""
    pg.evaluate(_FORMULAR)
    pg.fill("#s", "12a")
    pg.press("#s", "Tab")
    r1 = pg.evaluate("""() => { const sp = document.querySelector('.msg-eroare[data-camp="s"]');
      return { eroare: sp ? sp.textContent : null, invalid: document.getElementById('s').getAttribute('aria-invalid'),
               valoare: document.getElementById('s').value }; }""")
    assert r1["eroare"] == MESAJ_NUMAR_RO and r1["invalid"] == "true" and r1["valoare"] == "", r1
    r2 = pg.evaluate("""() => new Promise((rez) => {
      let trimise = 0; const f0 = window.fetch; window.fetch = (...a) => { trimise++; return f0(...a); };
      const b = document.getElementById('salveaza');
      b.addEventListener('click', async () => {
        try { await A.api.post('/x', { suma: document.getElementById('s').value }); rez({ trimise, refuz: null }); }
        catch (e) { rez({ trimise, refuz: e.mesaj, campuri: (e.erori_campuri || []).map((x) => x.camp) }); }
        finally { window.fetch = f0; }
      });
      b.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true })); b.click();
    })""")
    assert r2["trimise"] == 0, r2
    assert r2["refuz"] and "„Suma”" in r2["refuz"] and MESAJ_NUMAR_RO in r2["refuz"] and r2["campuri"] == ["s"], r2
