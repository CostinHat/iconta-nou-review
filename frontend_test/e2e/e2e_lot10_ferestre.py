# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.1 pct.5 (Costin 20.10.2026, verbatim în DECIZII): deficiențele 421 și 424 — aceeași clasă, toată aplicația.

„Deficiența 421 și 424 (clasă, toată aplicația) — ferestrele cu tabele cer multe derulări: ocupă cam jumătate din lățimea ecranului,
tabelul de import salariați are derulare laterală, butonul de salvare și mesajele de blocare sunt la capătul conținutului (regula 285
nerespectată aici). Regula: ferestrele cu tabele se deschid aproape pe tot ecranul (cum e deja Balanța de verificare); rezumatul stă fix
sus și acțiunea principală fix jos; se derulează doar tabelul din mijloc, niciodată lateral.”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`), la 1366×768 (laptopul obișnuit al unui
contabil): Balanța de verificare, Registrul-inventar, statul de plată (Salariați) și previzualizarea importului de salariați (fișierul SAGA
din `core/test_import_saga.py::SALARIATI_SAGA`, CNP cu cifra de control verificată acolo). Pe fiecare: fereastra are cel puțin 90% din
lățimea ecranului, nimic nu derulează lateral și nimic nu e tăiat în dreapta, acțiunea principală se vede fără derulare, iar rezumatul se
vede și după derularea tabelului la capăt. Regula are și garda fără browser: `core/test_lot10_fereastra_tabel.py` + verificatorul
(`FEREASTRA_TABEL`, `DERULARE_INLINE`, `ACTIUNE_TABEL_NEFIXATA`)."""
import datetime as _dt

import pytest

from conftest import firma_noua

AZI = _dt.date.today()
LAPTOP = {"width": 1366, "height": 768}

# Măsurătoarea ferestrei din față, cum o vede contabilul (`buton` = selectorul acțiunii principale a ecranului).
_MASOARA = """(buton) => {
  const f = [...document.querySelectorAll('.fereastra')].pop(), c = f.querySelector('.fereastra-corp');
  const rc = c.getBoundingClientRect(), nume = (e) => e.tagName + (e.id ? '#' + e.id : '') + '.' + String(e.className).slice(0, 40);
  // derulare laterală: orice element care derulează pe orizontală și are mai mult conținut decât lățimea lui
  const laterale = [...f.querySelectorAll('*')].filter((e) => ['auto', 'scroll'].includes(getComputedStyle(e).overflowX)
                                                         && e.scrollWidth > e.clientWidth + 1).map(nume);
  // nimic tăiat în dreapta: corpul nu are conținut mai lat decât el, iar niciun tabel nu trece de marginea lui
  const taiate = [...c.querySelectorAll('table')].filter((t) => t.getBoundingClientRect().right > rc.right + 1).map(nume);
  const b = document.querySelector(buton), rb = b && b.getBoundingClientRect();
  const o = {lat_fereastra: Math.round(f.getBoundingClientRect().width), ecran: innerWidth, clase: f.className, laterale, taiate,
             corp_lat: c.scrollWidth, corp_vizibil: c.clientWidth, are_tabel: !!c.querySelector('table, .mig-sold-tabel'),
             buton_vizibil: !!rb && rb.width > 0 && rb.top >= rc.top - 1 && rb.bottom <= rc.bottom + 1 && rb.bottom <= innerHeight,
             derulare_inainte: c.scrollTop};
  const rez = c.querySelector('.rezumat-fix');
  c.scrollTop = c.scrollHeight;   // tabelul derulat la capăt
  const rr = rez && rez.getBoundingClientRect();
  o.rezumat_dupa_derulare = !!rr && rr.height > 0 && rr.top >= rc.top - 1 && rr.bottom <= rc.bottom + 1;
  o.derulabil = c.scrollHeight > c.clientHeight + 1;
  c.scrollTop = 0;
  return o; }"""


def _verifica(patron, unde, buton):
    """Lista abaterilor de la regula ferestrei cu tabel pe fereastra din față (goală = respectată)."""
    pg = patron.pg
    pg.wait_for_timeout(600)
    o = pg.evaluate(_MASOARA, buton)
    rele = []
    if not o["are_tabel"]:
        rele.append("%s: fereastra n-are tabel (ecranul nu s-a încărcat?) %s" % (unde, o))
    if o["lat_fereastra"] < 0.9 * o["ecran"]:      # „se deschid aproape pe tot ecranul”
        rele.append("%s: fereastra are %d px din %d" % (unde, o["lat_fereastra"], o["ecran"]))
    if o["laterale"] or o["taiate"] or o["corp_lat"] > o["corp_vizibil"] + 1:   # „niciodată lateral”
        rele.append("%s: derulare laterală %s, tăiate %s, corp %d > %d" % (unde, o["laterale"], o["taiate"], o["corp_lat"], o["corp_vizibil"]))
    if not o["buton_vizibil"]:                      # „acțiunea principală fix jos”
        rele.append("%s: %s nu se vede fără derulare" % (unde, buton))
    if not o["rezumat_dupa_derulare"]:              # „rezumatul stă fix sus”
        rele.append("%s: rezumatul (.rezumat-fix) nu se vede după derularea tabelului la capăt" % unde)
    return rele, o


@pytest.fixture(scope="module")
def firma_ferestre():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_421(patron, firma_ferestre):
    """Firma nouă, pregătită (Date firmă, vector fiscal, serie), cu o notă VALIDATĂ în luna curentă pe 14 conturi și sume de 7 cifre
    (Balanța: 14 coloane — la 1366 px tabelul are 1.654 px cu sume de 7 cifre, fără strângere) și cu un salariat (statul de plată).
    Conturile sunt cele deja folosite de notele celorlalte teste e2e (existente în planul șablonului). O singură dată pe firmă."""
    from e2e_bloc_a import pregateste_firma
    from e2e_bloc_e import _nota
    from e2e_lot92 import _salariat_cu_cm
    from conftest import sql
    f = firma_ferestre
    pregateste_firma(patron, f)
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE descriere = %%s' % f["schema"], ("Probă fereastra cu tabel 421",)):
        perechi = [("5311", "1012"), ("5311", "704"), ("5311", "4111"), ("6022", "5311"), ("6581", "5311"), ("612", "401"),
                   ("626", "401"), ("624", "401"), ("401", "5121"), ("6811", "2813"), ("5311", "581")]
        from conftest import linie_nota   # [381] linia pe 401 / 4111 cere partenerul la introducere
        _nota(f, AZI.isoformat(), [linie_nota(d, c, "1234567.89") for d, c in perechi], "Probă fereastra cu tabel 421",
              valideaza=True, document_ref="PV 421")
    _salariat_cu_cm(f)
    return f


def test_def_421_ferestrele_cu_tabele_iau_ecranul_rezumatul_sus_actiunea_jos(patron, firma_421):
    """421 (clasă, toată aplicația). Pașii, la 1366×768: fereastra firmei -> „Balanță de verificare” (luna curentă, 14 conturi) ->
    „Registrul-inventar” -> „Adu soldurile din balanță” (tabelul soldurilor) -> „Salariați” (statul de plată). Pe fiecare: fereastra are cel
    puțin 90% din lățimea ecranului (înainte: ~jumătate), nimic nu derulează lateral și nimic nu e tăiat în dreapta, acțiunea principală
    se vede fără derulare, iar rezumatul (luna, cifrele) se vede și cu tabelul derulat la capăt."""
    from e2e_bloc_a import _card
    pg = patron.pg
    vp = pg.viewport_size
    pg.set_viewport_size(LAPTOP)
    rele = []
    try:
        patron.firma(firma_421["nume"])
        _card(patron, "balanta", "#b-pdf")
        r, o = _verifica(patron, "Balanța", "#b-pdf")
        rele += r
        patron.captura("balanta")
        assert "fer-tabel" in o["clase"], o   # fereastra cu tabel o face navigatorul (DS cap.9 v2.96)

        patron.firma(firma_421["nume"])
        _card(patron, "reginventar", "#ri-propune")
        pg.click("#ri-propune")
        pg.wait_for_selector(".fereastra:last-of-type .ri-ia", timeout=30000)
        r, _o = _verifica(patron, "Registrul-inventar", "#ri-adauga")
        rele += r
        patron.captura("registrul_inventar")

        patron.firma(firma_421["nume"])
        _card(patron, "salariati", "#sp-contare")
        r, _o = _verifica(patron, "Statul de plată", "#sp-contare")
        rele += r
        patron.captura("stat_de_plata")
    finally:
        pg.set_viewport_size(vp)
    assert rele == [], rele


def test_def_424_importul_salariatilor_nu_deruleaza_lateral_iar_salvarea_se_vede(patron, firma_ferestre):
    """424. Pașii, la 1366×768: fereastra firmei -> „Import date” -> „Salariați” -> fișierul SAGA (antetul și rândurile lui
    `SALARIATI_SAGA`: 17 coloane — cod, nume, punct de lucru, funcție, contract, normă, salariu, CNP, casa de sănătate, cont card…), cu
    încă 25 de salariați, ca tabelul să fie mai înalt decât fereastra -> previzualizarea: fereastra are cel puțin 90% din lățimea
    ecranului, tabelul nu derulează lateral (înainte: „Persoane în întreținere” ieșea din cutie) și nimic nu e tăiat în dreapta,
    „Salvează” și mesajele lui se văd fără derulare (înainte: la capătul tabelului), rezumatul fișierului se vede și cu tabelul derulat
    la capăt."""
    from e2e_import_saga import _cp1250, _incarca, _pas
    from e2e_lot82 import cnp_cu_control
    from core.test_import_saga import SALARIATI_SAGA
    # 25 de salariați în plus, cu CNP-ul calculat după algoritmul oficial (CLAUDE.md): 1 960101 07 NNN + cifra de control
    randuri = ["%06d;Popescu%s;Ana;Sediu;Economist;15.01.2024;Permanent;Da;8;168;6000;0;%s;Bihor;CAS Cluj;;Nu"
               % (100 + i, chr(65 + i), cnp_cu_control("196010107%03d" % (100 + i))) for i in range(25)]
    fisier = SALARIATI_SAGA + "\n".join(randuri) + "\n"
    pg = patron.pg
    vp = pg.viewport_size
    pg.set_viewport_size(LAPTOP)
    try:
        _pas(patron, firma_ferestre, "Salaria")
        _incarca(patron, "salariati_saga.csv", _cp1250(fisier), "#mig-salveaza-sal")
        rele, o = _verifica(patron, "Import salariați", "#mig-salveaza-sal")
        patron.captura()
    finally:
        pg.set_viewport_size(vp)
    assert "fer-tabel" in o["clase"] and rele == [], (rele, o)


def test_def_421_cartea_mare_contul_si_perioada_raman_sus(patron, firma_421):
    """421 (clasă — rezumatul fix pe orice ecran cu tabel, DS cap.9 v2.97 pct.5). Pașii, la 1366×768: fereastra firmei -> „Cartea mare” ->
    contul 5311. Contabilul derulează fișa până la capăt și vede încă anul, perioada și contul ales (înainte: urcau odată cu tabelul)."""
    from e2e_bloc_a import _card
    pg = patron.pg
    vp = pg.viewport_size
    pg.set_viewport_size(LAPTOP)
    try:
        patron.firma(firma_421["nume"])
        _card(patron, "fisacont", "#fc-cont")
        pg.select_option("#fc-cont", "5311")
        pg.wait_for_selector(".fereastra:last-of-type .fd-tabel", timeout=30000)
        rele, o = _verifica(patron, "Cartea mare", "#fc-cont")
        sus = pg.evaluate("""() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), s = c.querySelector('#fc-cont');
          c.scrollTop = c.scrollHeight; const rc = c.getBoundingClientRect(), r = s.getBoundingClientRect();
          return {in_rezumat: !!s.closest('.rezumat-fix'), vizibil: r.top >= rc.top - 1 && r.bottom <= rc.bottom + 1, valoare: s.value}; }""")
        patron.captura("cartea_mare_derulata")
    finally:
        pg.set_viewport_size(vp)
    assert rele == [], rele
    # „rezumatul stă fix sus”: contul ales rămâne în vedere cu fișa derulată la capăt
    assert sus == {"in_rezumat": True, "vizibil": True, "valoare": "5311"}, sus
