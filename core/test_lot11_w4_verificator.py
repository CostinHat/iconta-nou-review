# -*- coding: utf-8 -*-
"""[lotul 11, W4] Regulile verificatorului pentru decizia Costin 10.3 (verbatim în DECIZII „Comanda 10.3” pct.4: „Totalurile și rezumatul
fix, mesajele lângă buton, 394 la 1280×720: da, reorganizezi ecranele; totul încape într-un ecran, fără derulare.”):

  TOTAL_NEFIXAT   — rândul „Total” lăsat în `<tbody>` (se lipește jos numai din `<tfoot>`); caseta `.fd-totaluri` după tabel, în afara
                    `.bara-fixa`; regula `tfoot` lipită din stil.css; `--bara-h` pus de navigator (altfel totalul lipit stă sub bară).
  MESAJ_SUB_TABEL — zona de mesaj a ecranului (`id="…-mesaj|-msg|-eroare"`) după tabel, în afara `.rezumat-fix` / `.bara-fixa`.

Logica REALĂ (`verificator_conformitate.analiza_fereastra_tabel`, scoasă cu `ast` — fixturile `regula` / `reale` din
`core/test_lot10_fereastra_tabel.py`), pe fișierele de acum, pe mutații ale lor și pe fragmente sintetice. Proba în browser:
`core/test_lot11_w4_ecrane.py`. Temei: N/A — regulă de UI (DS cap.9 v2.100 pct.7–8).
"""
import pytest

from core.test_lot10_fereastra_tabel import _cod_lateste, pagina, regula, reale  # noqa: F401  (fixturi)

_CODURI = ("TOTAL_NEFIXAT", "MESAJ_SUB_TABEL")


def _r(rez):
    return sorted((r[0], r[2], r[3]) for r in rez if r[2] in _CODURI)


def test_fisierele_de_acum_au_totalurile_fixe_si_mesajele_langa_buton(regula, reale):
    css, nav, fis = reale
    # 10.3: „Totalurile […] fix, mesajele lângă buton” — nicio abatere pe ecranele de acum
    assert _r(regula(css, nav, fis)) == []


@pytest.mark.parametrize("fisier, ancora, inlocuire, cod", [
    # Cartea mare: caseta de totaluri scoasă din bară -> iese din vedere cât derulezi fișa
    ("firme.js", r'<div class="bara-fixa"><div class="fd-totaluri">   <!-- [lotul 11, decizia Costin 10.3: \u201eTotalurile \u2026 fix\u201d] totalurile fi',
     r'<div><div class="fd-totaluri">   <!-- [lotul 11, decizia Costin 10.3: \u201eTotalurile \u2026 fix\u201d] totalurile fi', "TOTAL_NEFIXAT"),
    # Balanța: rândul de total înapoi în <tbody>
    ("firme.js", '<tbody>${randuri.map(randCont).join("")}</tbody>\n          <tfoot><tr><td></td><td><b>Total</b></td>',
     '<tbody>${randuri.map(randCont).join("")}\n          <tr><td></td><td><b>Total</b></td>', "TOTAL_NEFIXAT"),
    # Registrul fiscal: zona de mesaj a ajustărilor înapoi sub tabel
    ("firme.js", "${dinConturi}${lista}\n", '${dinConturi}${lista}\n      <div id="aj2-mesaj"></div>\n', "MESAJ_SUB_TABEL"),
])
def test_mutatia_pe_fisierele_reale_e_prinsa(regula, reale, fisier, ancora, inlocuire, cod):
    css, nav, fis = reale
    assert fis[fisier].count(ancora) == 1, "ANTI-VACUU: ancora %r lipsește din %s" % (ancora[:60], fisier)
    rez = _r(regula(css, nav, dict(fis, **{fisier: fis[fisier].replace(ancora, inlocuire)})))
    assert [(f, c) for f, c, _t in rez] == [(fisier, cod)], rez


def test_stilul_si_navigatorul_fara_lipirea_totalului_sunt_prinse(regula, reale):
    css, nav, fis = reale
    ancora_css = "  position: sticky; bottom: calc(var(--bara-h, 0px) - 24px); z-index: 1; box-shadow: 0 -1px 0 var(--linie); }"
    assert css.count(ancora_css) == 1, "ANTI-VACUU: regula `tfoot` lipită lipsește din stil.css"
    assert [c for _f, c, _t in _r(regula(css.replace(ancora_css, "  z-index: 1; }"), nav, fis))] == ["TOTAL_NEFIXAT"]
    ancora_nav = 'if (bara) _corp.style.setProperty("--bara-h", bara.offsetHeight + "px");'
    assert nav.count(ancora_nav) == 1, "ANTI-VACUU: navigatorul nu pune `--bara-h` (patch-ul W4 neaplicat?)"
    # fără `--bara-h`, rândul de total lipit jos stă SUB bara de acțiune (măsurat: Balanța, „acoperit”)
    assert [(f, c) for f, c, _t in _r(regula(css, nav.replace(ancora_nav, "if (bara) {}"), fis))] == [("navigator.js", "TOTAL_NEFIXAT")]


def test_exceptia_mesajului_fara_obiect_e_prinsa(regula, reale):
    css, nav, fis = reale
    ancora = '<div id="el-msg"></div></div>`;'
    assert fis["firme.js"].count(ancora) == 1, "ANTI-VACUU: zona `el-msg` lipsește din firme.js"
    rez = _r(regula(css, nav, dict(fis, **{"firme.js": fis["firme.js"].replace(ancora, '<div id="el-nou-msg"></div></div>`;')})))
    assert [t for _f, _c, t in rez] == [
        "excepția „el-msg” nu mai are obiect: zona nu mai stă sub un tabel",
        "zona de mesaj „el-nou-msg” stă sub tabel, departe de butonul ei: în .rezumat-fix (lângă butoanele de sus) sau .bara-fixa "
        "(lângă acțiunea de jos) — DS cap.9 v2.100"], rez


_TAB = '<table class="fd-tabel"><tbody>${r}</tbody></table>'


@pytest.mark.parametrize("nume, sablon, asteptat", [
    ("total în tbody", '<table class="fd-tabel"><tbody>${r}<tr><td><b>Total</b></td><td>1</td></tr></tbody></table>', ["TOTAL_NEFIXAT"]),
    ("total în tbody, după o celulă goală", '<table class="fd-tabel"><tbody>${r}<tr><td></td><td><b>Total</b></td></tr></tbody></table>',
     ["TOTAL_NEFIXAT"]),
    ("total în tfoot", '<table class="fd-tabel"><tbody>${r}</tbody><tfoot><tr><td><b>Total</b></td></tr></tfoot></table>', []),
    ("caseta după tabel", _TAB + '<div class="fd-totaluri">x</div>', ["TOTAL_NEFIXAT"]),
    ("caseta în bară", _TAB + '<div class="bara-fixa"><div class="fd-totaluri">x</div></div>', []),
    ("caseta deasupra tabelului", '<div class="fd-totaluri">x</div>' + _TAB, []),
    ("mesaj sub tabel", _TAB + '<div id="pr-mesaj"></div>', ["MESAJ_SUB_TABEL"]),
    ("mesaj sub tabel (-msg)", _TAB + '<div id="pr-msg" style="margin-top:8px"></div>', ["MESAJ_SUB_TABEL"]),
    ("mesaj în bară", _TAB + '<div class="bara-fixa"><button>Salvează</button><div id="pr-mesaj"></div></div>', []),
    ("mesaj în rezumat", '<div class="rezumat-fix"><div id="pr-mesaj"></div></div>' + _TAB, []),
    ("mesaj deasupra tabelului", '<div id="pr-mesaj"></div>' + _TAB, []),
    ("mesaj pe rând", '<table class="fd-tabel"><tbody><tr><td><div id="pr-mesaj"></div></td></tr></tbody></table>', []),
])
def test_regula_pe_fragmente(regula, reale, nume, sablon, asteptat):
    css, nav, _fis = reale
    sursa = "async function ecranProba(corp) {\n  corp.innerHTML = `<div class=\"rezumat-fix\"><p>Luna</p></div>%s`;\n}\n" % sablon
    # DS cap.9 v2.100 pct.7–8: totalul în vedere, mesajul lângă butonul lui — prins unde lipsește, tăcut unde e
    assert [c for _f, c, _t in _r(regula(css, nav, {"proba.js": sursa}))] == asteptat, nume
