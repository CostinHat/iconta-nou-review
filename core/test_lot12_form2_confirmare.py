# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 446.1 — comanda Costin 12.2 pct.3, verbatim: „Avertismentul apare acum o singură dată, corect, dar tabelul se
strânge la un rând tăiat, iar întrebarea stă într-o casetă roșie.”]

CAUZA (măsurată aici, în Chromium, la 1280×720, pe codul de dinainte): întrebarea de confirmare (`api.confirmaCaseta`) era o
`.caseta-atentie` — roșul refuzului — urmată de un rând separat de butoane (margini 14 + 10 + 14 px); pusă în bara de jos a
previzualizării, în locul butonului principal, creștea bara cu ~91 px. Cu rezumatul de sus (cifrele + avertismentul firmei din fișier +
avertismentul înlocuirii), tabelului îi rămâneau, după derulare, -26 px la balanță (niciun rând), 45 px la parteneri, 0 rânduri întregi la
salariați. CLASA: toate apelurile `confirmaCaseta(` (48, în 23 de ecrane) desenau întrebarea roșie, oricare ar fi fost ea.

REPARAȚIA: `confirmaCaseta` desenează întrebarea într-o casetă NEUTRĂ (`.caseta-intrebare`, DS cap.5), cu întrebarea și cele două
butoane pe un rând (se rup pe ecran îngust): bara crește cu câțiva pixeli față de butonul pe care îl înlocuiește.

Ce păzește:
  1. pe fiecare import care înlocuiește date (balanță, parteneri, salariați, asociați, mijloace fixe, istoric declarații), cu și fără
     avertismentul firmei din fișier: întrebarea nu e roșie (nici clasa refuzului, nici culoarea lui), apare o dată, bara crește cu cel
     mult `CRESTERE_MAX` px față de butonul ascuns, iar tabelul păstrează cel puțin `LOC_TABEL_MIN` px vizibili după derulare;
  2. sursa: `confirmaCaseta` nu mai scrie `.caseta-atentie`, iar nimeni nu-și face o copie locală a ei;
  3. stil.css: `.caseta-intrebare` există și nu are fundalul / bordura roșie a refuzului.

Temei: N/A — regulă de UI (DS cap.5 „Casete de atenționare, confirmări”; roșul rămâne al refuzului și al erorii, cap.6).
"""
import os
import re

import pytest

from core import import_tabel
import core.test_lot11_m_ferestre_import as M
from core.test_lot11_m_ferestre_import import browser, _deschide, PASI, AVERT  # noqa: F401  (fixture-ul `browser`)

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRESTERE_MAX = 32      # px: cât poate crește bara de jos când întrebarea ia locul butonului principal (înainte: ~91 px)
LOC_TABEL_MIN = 150    # px de tabel vizibil cu întrebarea deschisă (≈ 4 rânduri de 37 px; înainte: -26 px la balanță)
ROSU = {"rgb(253, 243, 243)", "rgb(217, 140, 140)", "rgb(252, 232, 230)", "rgb(179, 38, 30)"}   # #fdf3f3, #d98c8c, --rosu-fundal, --rosu

MASOARA = """() => {
  const c = [...document.querySelectorAll('.fereastra-corp')].pop();
  const rez = c.querySelector('.rezumat-fix'), bara = c.querySelector('.bara-fixa'), th = c.querySelector('table thead');
  const r = (e) => e.getBoundingClientRect();
  c.scrollTop = 1e7;
  const sus = Math.max(r(rez).bottom, th ? r(th).bottom : 0), jos = Math.min(r(bara).top, r(c).bottom);
  const tb = c.querySelector('table tbody'), tot = tb ? r(tb).height : 0;
  const cas = document.querySelector('#caseta-atentie-activa');
  const cutie = cas && cas.firstElementChild, st = cutie && getComputedStyle(cutie);
  return {bara: Math.round(bara.offsetHeight), loc: Math.round(jos - sus), tot: Math.round(tot),
          clase: cas ? [...cas.querySelectorAll('[class]')].map((e) => e.className) : [],
          culori: st ? [st.backgroundColor, st.borderTopColor, st.borderLeftColor] : [],
          text: c.closest('.fereastra').innerText};
}"""


def _cu_firma_straina(fn):
    """Datele previzualizării + avertismentul firmei din fișier (599), făcut de funcția reală `import_tabel.confrunta_firma`."""
    def date():
        d = fn()
        d["firma_fisier"] = import_tabel.confrunta_firma({"denumire": "ALTA FIRMA SRL"}, "Firmă Probă Migrare SRL", None)
        return d
    return date


@pytest.mark.parametrize("firma_straina", [False, True], ids=["aceeasi_firma", "firma_straina"])
@pytest.mark.parametrize("pas", sorted(p for p in PASI if PASI[p][5]))
def test_def_446_1_intrebarea_nu_e_rosie_si_tabelul_ramane_citibil(browser, monkeypatch, pas, firma_straina):  # noqa: F811
    """ROȘU înainte: clasa `caseta-atentie`, fundal #fdf3f3; bara +91 px; balanța cu firma străină: loc -26 px. MUTAȚIA: markupul vechi
    al `confirmaCaseta` (caseta roșie + rândul de butoane separat) -> pică pe culoare și pe creștere."""
    if firma_straina:
        monkeypatch.setitem(M.PASI, pas, PASI[pas][:3] + (_cu_firma_straina(PASI[pas][3]),) + PASI[pas][4:])
    pg = _deschide(browser, pas, cu_existenta=True)
    try:
        a = pg.evaluate(MASOARA)
        if pg.query_selector("#mig-metoda-stoc"):
            pg.select_option("#mig-metoda-stoc", "cantitativ_valoric")
        pg.click(M.PASI[pas][2])
        pg.wait_for_selector("#ca-ok", timeout=5000)
        b = pg.evaluate(MASOARA)
    finally:
        pg.close()
    assert b["clase"] and "caseta-atentie" not in " ".join(b["clase"]) and "caseta-intrebare" in b["clase"], (pas, b["clase"])
    assert not (set(b["culori"]) & ROSU), (pas, b["culori"])                      # „întrebarea stă într-o casetă roșie”
    assert b["text"].count(AVERT[:60]) == 1, pas                                  # avertismentul, tot o singură dată (446)
    assert b["bara"] - a["bara"] <= CRESTERE_MAX, (pas, a["bara"], b["bara"])       # întrebarea ia locul butonului, nu mai mult
    assert b["loc"] >= min(LOC_TABEL_MIN, b["tot"]), (pas, b["loc"], b["tot"])     # „tabelul se strânge la un rând tăiat”


def _apeluri():
    for d, _, ff in os.walk(os.path.join(RAD, "static", "js")):
        for f in ff:
            if f.endswith(".js"):
                p = os.path.join(d, f)
                yield os.path.relpath(p, RAD), open(p, encoding="utf-8").read()


def test_def_446_1_confirmacaseta_are_o_singura_implementare_si_nu_e_rosie():
    """Clasa: toate întrebările trec prin `api.confirmaCaseta`, iar ea nu scrie caseta refuzului. MUTAȚIA: `caseta-intrebare` ->
    `caseta-atentie` în api.js, sau o `function confirmaCaseta(` copiată într-un ecran -> pică."""
    surse = dict(_apeluri())
    definitii = [p for p, t in surse.items() if re.search(r"function\s+confirmaCaseta\s*\(", t)]
    assert definitii == ["static/js/api.js"], definitii
    t = surse["static/js/api.js"]
    corp = t[t.index("export function confirmaCaseta("):]
    corp = corp[:corp.index("\n}\n")]
    assert 'class="caseta-intrebare"' in corp and "caseta-atentie\"" not in corp and "class=\"caseta-atentie" not in corp, corp
    apeluri = sum(len(re.findall(r"\bconfirmaCaseta\(", x)) for p, x in surse.items() if p != "static/js/api.js")
    assert apeluri >= 40, "anti-vacuu: apelurile confirmaCaseta nu mai sunt găsite (%d)" % apeluri


def test_def_446_1_stilul_intrebarii_e_neutru_in_stil_css():
    """`.caseta-intrebare` există în stil.css și nu folosește culorile refuzului. MUTAȚIA: regula ștearsă sau fundalul #fdf3f3 -> pică."""
    css = open(os.path.join(RAD, "static", "stil.css"), encoding="utf-8").read()
    reguli = re.findall(r"(?m)^\s*\.caseta-intrebare\s*\{([^}]*)\}", css)
    assert reguli, "lipsește regula .caseta-intrebare din stil.css"
    decl = " ".join(reguli).lower()
    props = dict(tuple(x.strip() for x in d.split(":", 1)) for d in decl.split(";") if ":" in d)   # proprietățile regulii
    assert (props.get("display"), props.get("flex-wrap")) == ("flex", "wrap"), props  # întrebarea și butoanele pe un rând, rupt pe telefon
    for rosu in ("#fdf3f3", "#d98c8c", "--rosu", "#fce8e6"):
        assert rosu not in decl, (rosu, decl)
