"""e2e_cursa_luna_17_5_X2.py — testul arhitectului pentru 17.5-X2, pct.3(vi.a) (auditul extern 17.5-X2 r1, X2-B1).

Control fiscal (F169/F022), selectorul «Luna comparată»: cursa reală dintre două cereri GET /control-fiscal/{id}?an=&luna=,
ținute pe loc cu page.route și eliberate în ordinea aleasă de test. Nu se scrie nimic în bază (numai cereri GET).
  (1) ordine normală: A apoi B aleasă înainte de răspuns; A se eliberează întâi, B după. Ecranul final trebuie să fie al lui B.
      (Pe S pică: răspunsul lui B găsește corpul vechi deja înlocuit de A și nu mai ajunge pe ecran.)
  (2) ordine inversă: B se eliberează întâi, A după. Ecranul final rămâne al lui B (răspunsul vechi al lui A nu-l acoperă).
  (3) eroare întârziată: A primește 500 după ce B a ajuns pe ecran. Ecranul rămâne al lui B, fără mesajul de eroare al lui A.
  (4) câmpul activ: selectorul are focusul când alege o lună; după redesenare focusul e tot pe «Luna comparată» (pastreazaCampulActiv).
      (Pe S pică: corpul e înlocuit și focusul cade pe pagină.)
«Ecranul lui X» = exact un corp .cf-corp în fereastra de sus, al cărui selector are valoarea X. Lunile A și B sunt primele două opțiuni
ale selectorului diferite de luna arătată la deschidere (snapshot-ul are luni cu note din 2026; nicio lună nu e scrisă de mână).
"""
import os
import re
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
import importlib.util  # noqa: E402

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
TOP = ".fereastra-overlay:not(.fundal) "
SEL = TOP + "select.cf-luna-comparata"


def _parcurs():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _marcheaza(pg):
    """Marchează corpul de dinaintea cursei: un corp redesenat din răspunsul serverului nu poartă marcajul (auditul intern r2: valoarea selectorului
    rămâne cea aleasă și fără redesenare, deci singură nu dovedește că răspunsul lui B a ajuns pe ecran)."""
    pg.evaluate("""() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) .cf-corp'); if (c) c.dataset.inainteDeCursa = '1'; }""")


def _stare(pg):
    """(numărul corpurilor .cf-corp din fereastra de sus, valoarea selectorului lor, textul zonei selectorului, corpul e cel de dinainte de cursă)."""
    return pg.evaluate("""() => { const f = document.querySelector('.fereastra-overlay:not(.fundal)'); if (!f) return [0, null, '', true];
      const c = [...f.querySelectorAll('.cf-corp')]; const s = f.querySelector('select.cf-luna-comparata');
      const er = [...f.querySelectorAll('.cf-luna-comp')].map((e) => e.innerText).join(' | ');
      return [c.length, s ? s.value : null, er, !!(c[0] && c[0].dataset.inainteDeCursa)]; }""")


def _asteapta(pg, cond, ms=15000):
    for _ in range(ms // 250):
        if cond():
            return True
        pg.wait_for_timeout(250)
    return False


class Tinute:
    """Ține pe loc cererile GET ale lunii comparate; testul le eliberează (continue) sau le răspunde cu eroare (fulfill 500)."""

    def __init__(self):
        self.cereri = []

    def __call__(self, route):
        r = route.request
        if r.method == "GET" and "/control-fiscal/" in r.url and "luna=" in r.url and "/audit-preluare" not in r.url:
            self.cereri.append(route)
        else:
            route.continue_()

    def a_lunii(self, val):
        an, luna = val.split("-")
        for rt in self.cereri:
            u = rt.request.url
            if re.search(r"[?&]an=%s(&|$)" % an, u) and re.search(r"[?&]luna=%s(&|$)" % luna, u):
                return rt
        return None


def _deschide(pg, parcurs):
    parcurs.firma(pg, F1)
    pg.evaluate("""() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) #fa-control'); if (!c) return;
      const cont = c.closest('.firme-optiuni'); if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); } }""")
    pg.click(TOP + "#fa-control", timeout=10000)
    pg.wait_for_selector(SEL, state="attached", timeout=30000)
    pg.wait_for_timeout(1500)


def _alege_doua(pg):
    curent = pg.input_value(SEL)
    vals = [v for v in pg.eval_on_selector_all(SEL + " option", "os => os.map(o => o.value)") if v and v != curent]
    assert len(vals) >= 2, "martorul lipsește: selectorul «Luna comparată» are mai puțin de două alte luni pe snapshot (%r)" % vals
    return vals[0], vals[1]


def _cursa(pg, tin, a, b, ordine, rele, caz, a_eroare=False):
    tin.cereri.clear()
    _marcheaza(pg)
    pg.select_option(SEL, a)
    if not _asteapta(pg, lambda: tin.a_lunii(a) is not None):
        rele.append("%s: cererea lunii %s nu a plecat" % (caz, a))
        return
    pg.select_option(SEL, b)   # înainte de răspunsul lui A: același selector, încă pe ecran
    if not _asteapta(pg, lambda: tin.a_lunii(b) is not None):
        rele.append("%s: cererea lunii %s nu a plecat" % (caz, b))
        return
    ra, rb = tin.a_lunii(a), tin.a_lunii(b)
    for v in ordine:
        if v == a:
            if a_eroare:
                ra.fulfill(status=500, content_type="application/json", body='{"detail": "eroare de proba 17.5-X2 (luna veche)"}')
            else:
                ra.continue_()
        else:
            rb.continue_()
        pg.wait_for_timeout(2500)
    n, val, er, vechi = _stare(pg)
    if vechi:
        rele.append("%s: corpul Control fiscal nu a fost redesenat din răspunsul lunii %s (a rămas corpul de dinainte de cursă)" % (caz, b))
    if n != 1:
        rele.append("%s: în fereastră sunt %d corpuri Control fiscal (așteptat 1)" % (caz, n))
    if val != b:
        rele.append("%s: ecranul final arată luna %s, deși ultima lună aleasă e %s (răspunsul lunii %s a acoperit alegerea)" % (caz, val, b, a))
    if a_eroare and "luna veche" in er:
        rele.append("%s: eroarea întârziată a lunii %s apare lângă luna %s: %r" % (caz, a, b, er))


def _focus(pg, tin, a, rele):
    tin.cereri.clear()
    _marcheaza(pg)
    pg.focus(SEL)
    pg.select_option(SEL, a)
    if not _asteapta(pg, lambda: tin.a_lunii(a) is not None):
        rele.append("(4) câmpul activ: cererea lunii %s nu a plecat" % a)
        return
    tin.a_lunii(a).continue_()
    pg.wait_for_timeout(2500)
    activ = pg.evaluate("() => document.activeElement ? (document.activeElement.id || document.activeElement.tagName) : null")
    if activ != "cf-luna-comparata":
        rele.append("(4) câmpul activ: după redesenare focusul e pe %r, nu pe «Luna comparată»" % activ)
    if _stare(pg)[3]:
        rele.append("(4) câmpul activ: corpul nu a fost redesenat din răspunsul lunii %s" % a)
    if pg.input_value(SEL) != a:
        rele.append("(4) câmpul activ: selectorul arată %s după redesenare (așteptat %s)" % (pg.input_value(SEL), a))


def test_cursa_luna_comparata_17_5_X2(browser):
    from core import ceas_proba
    parcurs = _parcurs()
    rele = []
    ctx = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        ctx.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        ctx.add_init_script(sesiune(ADMIN))
        pg = ctx.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _deschide(pg, parcurs)
        a, b = _alege_doua(pg)
        tin = Tinute()
        pg.route("**/control-fiscal/**", tin)
        _cursa(pg, tin, a, b, (a, b), rele, "(1) ordine normală")
        _cursa(pg, tin, a, b, (b, a), rele, "(2) ordine inversă")
        _cursa(pg, tin, a, b, (b, a), rele, "(3) eroare întârziată", a_eroare=True)
        _focus(pg, tin, a, rele)
        pg.unroute("**/control-fiscal/**")
    finally:
        ctx.close()
    assert not rele, "17.5-X2, cursa «Luna comparată» (pct.3(vi.a)): " + "; ".join(rele)
