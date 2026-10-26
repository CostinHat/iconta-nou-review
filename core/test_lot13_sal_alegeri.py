# -*- coding: utf-8 -*-
"""GARD lotul 13 (676 + cap.17 „fapte fiscale fără default tacit”): listele scurte din ferestrele salarizării folosesc mecanismul COMUN al
aplicației — un `<select data-butoane>` (`selectScurt` în firme.js, `selectDaNu` din api.js) pe care `api.alegereButoane` îl arată ca
butoane alăturate — și fiecare listă care poartă un fapt al salariatului se CERE la salvare (`cereAlegerile`).

Decizia sesiunii principale (26.10.2026): `sal_alegeri.js`, care dubla mecanismul din api.js cu un al doilea (grup de butoane + câmp
ascuns), e logică dublată (CLAUDE.md „Reparație reală, nu patch”) — scos; grupurile salarizării trec pe mecanismul comun.

CE FACE IMPOSIBIL: (1) o listă nouă a salarizării pe care salvarea nu o cere — omul ar trimite fără să aleagă, iar serverul ar primi
„nimic ales” ca „Nu”; listele care nu poartă un fapt (marcajul pontajului, câmpurile opționale) stau în `NECERUTE`, cu motivul; o excepție
fără obiect pică; (2) întoarcerea unui al doilea mecanism de butoane alăturate în afara api.js.
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FISIERE = ("static/js/ecrane/firme.js", "static/js/ecrane/flux_concediu.js")

#: listele care NU se cer la salvare, cu motivul (cheia: fișier:id)
NECERUTE = {
    "firme.js:pj-marcaj": "modul de lucru al calendarului (ce se marchează la apăsarea unei zile) — nu se trimite; o zi apăsată fără marcaj "
                          "primește refuzul „Alege întâi ce marchezi”",
    "firme.js:sn-tip_contract": "tipul contractului e opțional pe fișă (Codul muncii art.12; adeverința îl cere când se generează)",
    "firme.js:ed-tipcim": "idem, la „Corectează datele” (CIM-ul e opțional pe fișă)",
}

_SCURT = re.compile(r"""selectScurt\(\s*["`]([\w${}-]+)["`]""")
_DANU = re.compile(r"""selectDaNu\(\s*['`]id="([\w${}-]+)\"""")
#: „Salariat nou” își face câmpurile prin helperul `camp(id, eticheta, "select" | "danu", …)` -> lista `sn-<id>`
_CAMP_SN = re.compile(r'camp\("(\w+)", "[^"]*", "(?:select|danu)"')
#: motivul scutirii: `campMotivScutire("<id>")` -> `selectScurt(id, MOTIVE_EXCEPTARE, …)`
_MOTIV = re.compile(r'campMotivScutire\("([\w-]+)"\)')
_CERUTE = re.compile(r"""cereAlegerile\(\s*\w+\s*,\s*(\[[^\]]*\]|model\.map\([^\n]*?`#[^`]*`\))""")


def _surse(fisiere=None):
    return fisiere or [(f, io.open(os.path.join(RAD, f), encoding="utf-8").read()) for f in FISIERE]


def necerute(fisiere=None):
    out, vazute = [], set()
    for cale, s in _surse(fisiere):
        nume = os.path.basename(cale)
        cerute = set()
        for m in _CERUTE.finditer(s):
            cerute |= set(re.findall(r'["`]#([\w${}-]+)["`]', m.group(1)))
        ids = [m.group(1) for m in _SCURT.finditer(s)] + [m.group(1) for m in _DANU.finditer(s)]
        ids += ["sn-" + m.group(1) for m in _CAMP_SN.finditer(s)] + [m.group(1) for m in _MOTIV.finditer(s)]
        for i in ids:
            if "${" in i and i != "susp${i}-tip":
                continue   # helperii (`sn-${id}`, `${id}`) se văd prin chemările lor de mai sus
            cheie = "%s:%s" % (nume, i)
            vazute.add(cheie)
            if i not in cerute and cheie not in NECERUTE:
                out.append(cheie)
    return out, vazute


def test_fiecare_lista_care_poarta_un_fapt_se_cere_la_salvare():
    rele, vazute = necerute()
    assert len(vazute) >= 20, "ANTI-VACUU: doar %d liste găsite: %s" % (len(vazute), sorted(vazute))
    assert not rele, "liste scurte ale salarizării (676) pe care salvarea nu le cere (`cereAlegerile`): %s" % rele


def test_exceptiile_au_obiect():
    _rele, vazute = necerute()
    assert set(NECERUTE) <= vazute, "excepții fără obiect: %s" % sorted(set(NECERUTE) - vazute)


def test_un_singur_mecanism_de_butoane_alaturate():
    """Mecanismul listei scurte e unul, în api.js (`alegereButoane`, `select[data-butoane]`): niciun ecran nu-și face al lui."""
    assert not os.path.exists(os.path.join(RAD, "static/js/ecrane/sal_alegeri.js")), "sal_alegeri.js dubla mecanismul comun"
    for cale, s in _surse():
        assert "sal_alegeri" not in s, cale
        assert not re.search(r"function\s+(alegereButoane|alegereDaNu|cereButoane|legaAlegeri)\b", s), cale
        assert "data-butoane" in s or "selectDaNu(" in s, cale


def test_CALIBRARE_lista_necerute_e_prinsa():
    """MUTAȚIE (pe text): „#ed-fbaza” scos din lista cerută a „Date de calcul” -> prins."""
    cale = FISIERE[0]
    s = io.open(os.path.join(RAD, cale), encoding="utf-8").read()
    a = 'cereAlegerile(corp, ["#ed-norma", "#ed-fbaza", "#ed-declcopii", "#ed-scutit", "#ed-motiv"])'
    assert s.count(a) == 1
    rele, _v = necerute([(cale, s.replace(a, 'cereAlegerile(corp, ["#ed-norma", "#ed-declcopii", "#ed-scutit", "#ed-motiv"])'))])
    assert "firme.js:ed-fbaza" in rele, rele


def test_sumele_scrise_romaneste():
    """[655] `sumaRo` (sal_sume.js) citește suma cu regula unică a aplicației, `numarRo` din api.js (DS cap.6 „Numerele scrise de om”,
    oglinda `core/numere.numar_ro`), și o adaptează ferestrelor salarizării: gol -> null, refuzat -> NaN, altfel numărul. „1.000” = o mie;
    „1.000,50”; „12,5”; „2000.41” (punct + zecimale = zecimal); ce nu se poate citi fără ghicit -> NaN. Rulat în Node pe textul funcțiilor
    (aceleași pe care le folosesc ferestrele). MUTAȚIE: un parsator local în loc de `numarRo` -> garda de mai jos pică."""
    import json
    import subprocess
    import tempfile
    src = io.open(os.path.join(RAD, "static/js/ecrane/sal_sume.js"), encoding="utf-8").read()
    corp = src[src.index("export function sumaRo"):]
    corp = corp[:corp.index("\n}\n") + 3].replace("export function", "function")
    assert "numarRo(" in corp and ".replace(" not in corp, "sumaRo trebuie să citească prin `numarRo` (api.js), nu cu un parsator local"
    api = io.open(os.path.join(RAD, "static/js/api.js"), encoding="utf-8").read()
    regula = api[api.index("export const MESAJ_NUMAR_RO"):]
    regula = regula[:regula.index("\n}\n", regula.index("export function numarRo")) + 3].replace("export ", "")
    cazuri = ["1.000", "1.500", "1.000,50", "12,5", "2000.41", "1000", "1.000.000", "", "1.00.0", "abc", " 4 325 "]
    js = regula + "\nconst textCamp = (x) => x.value;\n" + corp + \
        "\nconsole.log(JSON.stringify(%s.map((t) => { const v = sumaRo(t); return v === null ? null : (Number.isNaN(v) ? 'NaN' : v); })));" \
        % json.dumps(cazuri)
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as f:
        f.write(js)
    try:
        out = json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout)
    finally:
        os.unlink(f.name)
    assert out == [1000, 1500, 1000.5, 12.5, 2000.41, 1000, 1000000, None, "NaN", "NaN", 4325], out
