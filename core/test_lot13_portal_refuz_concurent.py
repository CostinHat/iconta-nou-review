# -*- coding: utf-8 -*-
"""[lotul 13, valul 5, zona portal] Refuzul unei scrieri pornite de un clic nu e șters de REUȘITA altei scrieri pornite de ACELAȘI clic.

Găsit pe plasa e2e completă (59896e5c): `e2e_lot13_portal_p3.py::test_def_526` și `e2e_lot11_w3a.py::test_def_440_date_firma…` — în
Date firmă, „Salvează” trimite deodată datele firmei, vectorul fiscal și asociații; asociații cu CNP greșit sunt refuzați (CNP-ul marcat
lângă câmp, caseta „NU s-a salvat.”), iar REUȘITA datelor firmei, venită după refuz, ștergea marcajele și caseta (`_dupaScriereReusita`
din `api.js`, 654): pe ecran rămânea „Restul NU — vezi câmpurile marcate”, fără niciun câmp marcat (captura din plasă).

Regula (654, DS cap.6, comanda 13.1: „Mesajele de eroare vechi […] rămân pe ecran după acțiunea următoare”): refuzurile de DINAINTE pleacă
la apăsarea următorului buton care scrie; ce refuză clicul de acum rămâne, oricare ar fi ordinea în care se întorc cererile lui.
Codul REAL din `api.js`, în Chromium (aceeași pagină ca `core/test_lot13_ds_mesaje.py`); serverul e `fetch` înlocuit în pagină.

Temei: N/A — regulă de interfață (DS cap.6, v2.104).
"""
from core.test_lot13_ds_mesaje import _APASA, _FORMULAR, pg  # noqa: F401 — fixtura paginii cu `api.js`

_SERVER = """() => {
  window.fetch = (url) => url === '/rau'
    ? Promise.resolve(new Response(JSON.stringify({ detail: { mesaj: 'Contul 9999 nu există în planul de conturi.',
        erori_campuri: [{ camp: 'cont', mesaj: 'Contul 9999 nu există în planul de conturi.' }] } }),
        { status: 422, headers: { 'Content-Type': 'application/json' } }))
    : new Promise((r) => setTimeout(() => r(new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } })), 200));
}"""

_STARE = """() => ({ marcat: document.getElementById('cont').getAttribute('aria-invalid'),
  langa: (document.querySelector('.msg-eroare[data-camp="cont"]') || {}).textContent || null,
  caseta: document.querySelectorAll('.refuz-salvare').length,
  vechi: document.getElementById('s').getAttribute('aria-invalid') })"""


def test_reusita_unei_parti_nu_sterge_refuzul_altei_parti_a_aceluiasi_clic(pg):
    """Un clic, două scrieri: refuzul (câmpul „Cont”) se întoarce ÎNTÂI, reușita DUPĂ el. Câmpul rămâne marcat, cu textul lângă el.
    MUTAȚIE: `curataEroriCamp(scop)` pus înapoi după reușita cererii pornite de clic (forma de dinainte) -> marcajul dispare -> ROȘU."""
    pg.evaluate(_FORMULAR)
    pg.evaluate(_SERVER)
    pg.evaluate("""() => document.getElementById('salv').addEventListener('click', () => {
      A.api.post('/rau', {}).catch(() => {});
      A.api.post('/bun', {});
    })""")
    pg.evaluate(_APASA, "salv")
    pg.wait_for_timeout(700)
    r = pg.evaluate(_STARE)
    assert r["marcat"] == "true" and r["langa"] == "Contul 9999 nu există în planul de conturi.", r
    assert r["caseta"] == 1, r


def test_marcajul_de_dinainte_pleaca_la_apasarea_urmatoare(pg):
    """654 rămâne: marcajul unui refuz VECHI („Suma”) pleacă la următoarea apăsare a unui buton care scrie, chiar dacă scrierea ei reușește.
    MUTAȚIE: ștergerea marcajelor vechi scoasă din ascultătorul clicului -> „Suma” rămâne marcată -> ROȘU."""
    pg.evaluate(_FORMULAR)
    pg.evaluate(_SERVER)
    pg.evaluate("() => A.eroareCamp(document.querySelector('.fereastra'), 's', 'Suma trebuie să fie un număr.')")
    assert pg.evaluate(_STARE)["vechi"] == "true"
    pg.evaluate("() => document.getElementById('salv').addEventListener('click', () => { A.api.post('/bun', {}); })")
    pg.evaluate(_APASA, "salv")
    pg.wait_for_timeout(500)
    r = pg.evaluate(_STARE)
    assert r["vechi"] is None and r["marcat"] is None and r["caseta"] == 0, r
