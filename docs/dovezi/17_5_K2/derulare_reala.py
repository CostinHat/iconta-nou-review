"""docs/dovezi/17_5_K2/derulare_reala.py — DERULAREA REALĂ a celor patru ferestre ale lui (5), la cele trei rezoluții (12 măsurări), lot 17.5-K.

Rulat prin `scripts/e2e_poarta.py [--arbore] --doar=e2e_derulare_17_5_K.py <ieșire>`, după copierea TEMPORARĂ a acestui fișier ca frontend_test/e2e/e2e_derulare_17_5_K.py (conftest-ul e2e se vede numai de acolo; copia se șterge după rulare, nu se comite) (mediul porții, 8019, ceas fix), cu UNA singură fereastră deschisă (cea măsurată).
Elementul derulat: zona `.zona-derulare` vizibilă, dacă ea derulează (overflow auto/scroll și scrollHeight > clientHeight + 2); altfel corpul ferestrei. Se derulează cu rotița mouse-ului
(mouse.wheel peste centrul elementului) până când scrollTop nu mai crește. Câte un rând pe fereastră și rezoluție:
  DERULARE <fereastra> <lățime>x<înălțime> element=<zonă|corp> scrollTop_inainte=<px> scrollTop_dupa=<px> ultimul_vizibil=<da|nu> depaseste=<da|nu>
Regula de verdict (pe C): când conținutul depășește locul (scrollHeight > clientHeight), scrollTop_dupa > scrollTop_inainte ȘI ultimul_vizibil=da. Nu scrie nimic în afara ieșirii."""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "frontend_test", "e2e"))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

from conftest import BAZA, browser, sesiune  # noqa: F401,E402 — `browser` e fixtura
import e2e_ferestre_17_5_K as t  # noqa: E402

JS_ELEMENT = """() => {
  const corp = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); if (!corp) return null;
  const vizibil = (e) => { const r = e.getBoundingClientRect(); return e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden' && r.width > 0 && r.height > 0; };
  const derula = (e) => { const o = getComputedStyle(e).overflowY; return (o === 'auto' || o === 'scroll') && e.scrollHeight > e.clientHeight + 2; };
  let el = [...corp.querySelectorAll('.zona-derulare')].find((z) => vizibil(z) && derula(z)) || null;
  let tip = 'zonă';
  if (!el) { el = corp; tip = 'corp'; }
  el.setAttribute('data-derulare-proba', '1');
  const r = el.getBoundingClientRect();
  return {tip, x: r.left + r.width / 2, y: r.top + Math.min(r.height / 2, 200), sh: el.scrollHeight, ch: el.clientHeight, st: el.scrollTop};
}"""
JS_STARE = """() => {
  const el = document.querySelector('[data-derulare-proba]'); if (!el) return null;
  const r = el.getBoundingClientRect();
  // marginea de jos vizibilă: bara de jos a ferestrei sau o bară fixă lipită acoperă partea de jos a elementului
  let jos = r.bottom;
  for (const b of document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra-jos, .fereastra-overlay:not(.fundal) .bara-fixa')) {
    const q = b.getBoundingClientRect(); const are = b.getClientRects().length > 0 && (b.innerText || '').trim() !== '' && !b.classList.contains('fj-gol'); // o bară goală (fj-gol) nu acoperă nimic
    if (are && q.top < jos && q.bottom > r.top) jos = Math.min(jos, q.top);
  }
  const arata = (e) => { for (let n = e; n && n !== el; n = n.parentElement) { const s = getComputedStyle(n); if (n.hidden || s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0) return false; } return true; };
  const frunze = [...el.querySelectorAll('*')].filter((e) => e.getClientRects().length > 0 && e.children.length === 0 && e.getBoundingClientRect().height > 0 && arata(e) && ((e.textContent || '').trim() !== '' || /^(INPUT|BUTTON|SELECT|IMG|TEXTAREA)$/.test(e.tagName)) && !e.closest('.bara-fixa, .fereastra-jos'));
  const ultim = frunze.length ? frunze[frunze.length - 1] : null;
  const q = ultim ? ultim.getBoundingClientRect() : null;
  return {st: el.scrollTop, sh: el.scrollHeight, ch: el.clientHeight, ultim_ok: q ? q.bottom <= jos + 2 && q.top >= r.top - 2 : false, detaliu: ultim ? ultim.tagName + '#' + ultim.id + '.' + ultim.className + ' bottom=' + Math.round(q.bottom) + ' jos=' + Math.round(jos) + ' top=' + Math.round(q.top) + ' elTop=' + Math.round(r.top) : 'fără frunză'};
}"""


def test_derulare_reala(browser, capsys):
    from core import ceas_proba
    parcurs = t._incarca_parcurs_17_1()
    rele = []

    def out(linie):
        with capsys.disabled():
            print(linie)

    ferestre = (("Rapoarte comerciale F1", t._w_rapoarte), ("Plan de conturi F1", t._w_plan), ("Analitică stoc F1", t._w_analitica), ("Import date — Solduri inițiale F1", t._w_solduri))
    b = browser.new_context(viewport={"width": t.R3[0], "height": t.R3[1]})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(t.ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        for nume, deschide in ferestre:
            for (w, h) in t.REZOLUTII:
                pg.set_viewport_size({"width": w, "height": h})
                if not deschide(pg, parcurs):
                    out("DERULARE %s %dx%d fereastra nu s-a deschis" % (nume, w, h))
                    rele.append("%s %dx%d: fereastra nu s-a deschis" % (nume, w, h))
                    continue
                pg.wait_for_timeout(900)
                e = pg.evaluate(JS_ELEMENT)
                if not e:
                    out("DERULARE %s %dx%d fără corp" % (nume, w, h))
                    rele.append("%s %dx%d: fără corp" % (nume, w, h))
                    continue
                inainte = pg.evaluate(JS_STARE)
                depaseste = inainte["sh"] > inainte["ch"] + 2
                pg.mouse.move(e["x"], e["y"])
                ultim_st, fara_schimbare = inainte["st"], 0
                for _ in range(400):
                    pg.mouse.wheel(0, 1500)
                    pg.wait_for_timeout(60)
                    st = pg.evaluate("() => document.querySelector('[data-derulare-proba]').scrollTop")
                    if st <= ultim_st:
                        fara_schimbare += 1
                        if fara_schimbare >= 3:
                            break
                    else:
                        fara_schimbare = 0
                    ultim_st = st
                dupa = pg.evaluate(JS_STARE)
                ok = (not depaseste) or (dupa["st"] > inainte["st"] and dupa["ultim_ok"])
                out("DERULARE %s %dx%d element=%s scrollTop_inainte=%s scrollTop_dupa=%s ultimul_vizibil=%s depaseste=%s" % (
                    nume, w, h, e["tip"], round(inainte["st"]), round(dupa["st"]), "da" if dupa["ultim_ok"] else "nu", "da" if depaseste else "nu"))
                if not dupa["ultim_ok"]:
                    out("  detaliu ultim: %s" % dupa["detaliu"])
                if not ok:
                    rele.append("derulare reală %s %dx%d" % (nume, w, h))
        assert not rele, "; ".join(rele)
    finally:
        b.close()
