# -*- coding: utf-8 -*-
"""GARD lotul 13 (676 + cap.17 „fapte fiscale fără default tacit”): listele scurte din ferestrele salarizării sunt butoane alăturate
(`static/js/ecrane/sal_alegeri.js`), iar fiecare grup care poartă un fapt al salariatului se CERE la salvare (`cereButoane`), ca
DA/NU-urile de dinainte (`cereAlegerile` pe `selectDaNu`, păzite de `scripts/scan_selecturi_ecrane.danu_necerute`).

CE FACE IMPOSIBIL: un grup nou (`alegereDaNu("x", …)` / `alegereButoane("x", …)`) pe care salvarea nu-l cere — omul ar putea trimite
fără să aleagă, iar serverul ar primi „nimic ales” ca „Nu”. Grupurile care nu poartă un fapt (marcajul pontajului, câmpurile opționale)
stau în `NECERUTE`, cu motivul; o excepție fără obiect pică.
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FISIERE = ("static/js/ecrane/firme.js", "static/js/ecrane/flux_concediu.js")

#: grupurile care NU se cer la salvare, cu motivul (cheia: fișier:id)
NECERUTE = {
    "firme.js:pj-marcaj": "modul de lucru al calendarului (ce se marchează la apăsarea unei zile) — nu se trimite; o zi apăsată fără marcaj "
                          "primește mesajul „Alege întâi ce marchezi”",
    "firme.js:sn-tip_contract": "tipul contractului e opțional pe fișă (Codul muncii art.12; adeverința îl cere când se generează)",
    "firme.js:ed-tipcim": "idem, la „Corectează datele” (CIM-ul e opțional pe fișă)",
}

_GRUP = re.compile(r"""alegere(?:DaNu|Butoane)\(\s*["`]([\w-]+)["`]""")
_GRUP_RAND = re.compile(r"""alegereButoane\(\s*`susp\$\{i\}-tip`""")
#: „Salariat nou” își face câmpurile prin helperul `camp(id, eticheta, "select" | "danu", …)` -> grupul `sn-<id>`
_GRUP_SN = re.compile(r'camp\("(\w+)", "[^"]*", "(?:select|danu)"')
_CERUTE = re.compile(r"""cereButoane\(\s*\w+\s*,\s*\[([^\]]*)\]""")


def _surse(fisiere=None):
    return fisiere or [(f, io.open(os.path.join(RAD, f), encoding="utf-8").read()) for f in FISIERE]


def necerute(fisiere=None):
    out, vazute = [], set()
    for cale, s in _surse(fisiere):
        nume = os.path.basename(cale)
        cerute = set()
        for m in _CERUTE.finditer(s):
            cerute |= set(re.findall(r'["`]([\w-]+)["`]', m.group(1)))
        ids = [m.group(1) for m in _GRUP.finditer(s)] + ["sn-" + m.group(1) for m in _GRUP_SN.finditer(s)]
        for i in ids:
            cheie = "%s:%s" % (nume, i)
            vazute.add(cheie)
            if i not in cerute and cheie not in NECERUTE:
                out.append(cheie)
        # rândurile suspendărilor: `susp${i}-tip`, cerute prin `model.map((_x, i) => \`susp${i}-tip\`)`
        if _GRUP_RAND.search(s) and "cereButoane(corp, model.map((_x, i) => `susp${i}-tip`))" not in s:
            out.append("%s:susp${i}-tip" % nume)
    return out, vazute


def test_fiecare_grup_care_poarta_un_fapt_se_cere_la_salvare():
    rele, vazute = necerute()
    assert len(vazute) >= 15, "ANTI-VACUU: doar %d grupuri găsite" % len(vazute)
    assert not rele, "grupuri de butoane (676) pe care salvarea nu le cere (`cereButoane`): %s" % rele


def test_exceptiile_au_obiect():
    _rele, vazute = necerute()
    assert set(NECERUTE) <= vazute, "excepții fără obiect: %s" % sorted(set(NECERUTE) - vazute)


def test_CALIBRARE_grupul_necerut_e_prins():
    """MUTAȚIE (pe text): „Funcția de bază” scoasă din lista cerută a „Date de calcul” -> prinsă."""
    cale = FISIERE[0]
    s = io.open(os.path.join(RAD, cale), encoding="utf-8").read()
    a = 'cereButoane(corp, ["ed-norma", "ed-fbaza", "ed-declcopii", "ed-scutit", "ed-motiv"])'
    assert s.count(a) == 1
    rele, _v = necerute([(cale, s.replace(a, 'cereButoane(corp, ["ed-norma", "ed-declcopii", "ed-scutit", "ed-motiv"])'))])
    # „ed-fbaza” e și în „De verificat”? nu: acolo e `dv-fbaza`; deci grupul „Date de calcul” iese necerut
    assert "firme.js:ed-fbaza" in rele, rele


def test_sumele_scrise_romaneste():
    """[655] `sumaRo` (sal_alegeri.js): „1.000” = o mie; „1.000,50”; „12,5”; „2000.41” (punct + 1–2 cifre = zecimal); ce nu se poate
    citi fără ghicit -> NaN. Pe textul funcției, rulat în Node (aceeași funcție pe care o folosesc ferestrele)."""
    import json
    import subprocess
    import tempfile
    src = io.open(os.path.join(RAD, "static/js/ecrane/sal_alegeri.js"), encoding="utf-8").read()
    corp = src[src.index("export function sumaRo"):]
    corp = corp[:corp.index("\n}\n") + 3].replace("export function", "function")
    cazuri = ["1.000", "1.500", "1.000,50", "12,5", "2000.41", "1000", "1.000.000", "", "1.00.0", "1,000.5", "abc", " 4 325 "]
    js = corp + "\nconsole.log(JSON.stringify(%s.map((t) => { const v = sumaRo(t); return v === null ? null : (Number.isNaN(v) ? 'NaN' : v); })));" \
        % json.dumps(cazuri)
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as f:
        f.write(js)
    try:
        out = json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout)
    finally:
        os.unlink(f.name)
    assert out == [1000, 1500, 1000.5, 12.5, 2000.41, 1000, 1000000, None, "NaN", "NaN", "NaN", 4325], out
