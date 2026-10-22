# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 443 (comanda Costin 11.1 pct.19, verbatim): „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61).
«termen» din Istoric spune că e termenul SPV.”

Temei: N/A — regulă de afișare (DS cap.4 v2.99, „Seria și numărul, separat”). Forma „Seria X nr. Y” a facturii PDF vine din CF art.319
alin.(20) lit.a) („un număr secvențial, bazat pe una sau mai multe serii”, `factura_pdf.serie_si_numar`); aici e numai afișarea.

CE FACE IMPOSIBIL:
  1. `pdf_util.serie_nr` / `numarCuSerie` (api.js) lipind seria de număr („F61”) sau dublând seria din numărul facturii emise;
  2. cele două forme (Python și JS) diferite pe aceleași date;
  3. un text pentru om compus cu `numar_cu_serie` (identificatorul lipit) în afara locurilor de IDENTIFICATOR numite mai jos.
"""
import ast
import glob
import io
import json
import os
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: (serie, număr) -> afișarea; cazurile reale: seria F6 a firmei F6 (443), numărul facturii emise care poartă seria („F1A3”), seria cu
#: separator la capăt („KAI-”, exemplul din Configurare emitere), borderoul fără serie („BA-1”), fără serie, seria „-” a facturilor primite
_CAZURI = [("F6", "1", "F6 nr. 1"), ("F6", "F61", "F6 nr. 1"), ("F1A", "F1A3", "F1A nr. 3"), ("KAI-", "KAI-12", "KAI nr. 12"),
           (None, "BA-1", "BA-1"), ("", "12", "12"), ("-", "2", "2"), ("FCT", None, "FCT"), ("fct", "FCT7", "fct nr. 7")]

#: Locurile unde `numar_cu_serie` e IDENTIFICATORUL documentului, nu text pentru om (ANAF primește un singur șir): ID-ul facturii în
#: e-Factura (BT-1) și trimiterea la factura stornată (BT-25). Orice alt apel e afișare -> `serie_nr`.
_IDENTIFICATOR = {"pdf_util.py", "efactura_send.py"}


def test_serie_nr_python_separa_seria_de_numar():
    """1. MUTAȚIE: `return "%s nr. %s" % (s, nr)` -> `return s + nr` -> „F61” -> pică."""
    from core.pdf_util import serie_nr
    assert [serie_nr(s, n) for s, n, _ in _CAZURI] == [a for _, _, a in _CAZURI]   # 443: „F6 nr. 1, nu F61”


def test_numarCuSerie_js_da_aceeasi_forma_ca_python():
    """1 + 2. Funcția REALĂ din api.js, rulată cu node pe aceleași cazuri. MUTAȚIE: separatorul de la capătul seriei netăiat în JS
    -> „KAI- nr. 12” -> pică."""
    src = io.open(os.path.join(_RAD, "static", "js", "api.js"), encoding="utf-8").read()
    i = src.index("const _SEPARATORI_SERIE")
    j = src.index("\n}\n", src.index("export function numarCuSerie", i)) + 3
    cod = src[i:j].replace("export function", "function") + "\nconsole.log(JSON.stringify(%s.map(([s, n]) => numarCuSerie(s, n))));" % \
        json.dumps([[s, n] for s, n, _ in _CAZURI])
    iesire = subprocess.run(["node", "-e", cod], capture_output=True, text=True, timeout=30)
    assert iesire.returncode == 0, iesire.stderr
    assert json.loads(iesire.stdout) == [a for _, _, a in _CAZURI]


def _apeluri_numar_cu_serie():
    out = []
    for p in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))):
        nume = os.path.basename(p)
        if nume.startswith("test_") or nume in _IDENTIFICATOR:
            continue
        src = io.open(p, encoding="utf-8").read()
        if "numar_cu_serie" not in src:
            continue
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Call):
                f = n.func
                nume_f = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
                if nume_f == "numar_cu_serie":
                    out.append("%s:%d" % (nume, n.lineno))
            elif isinstance(n, ast.ImportFrom) and any(a.name == "numar_cu_serie" for a in n.names):
                out.append("%s:%d (import)" % (nume, n.lineno))
    return out


def _nume_in(n):
    """Numele (variabile, atribute, chei de dict constante) dintr-un subarbore — ca să se vadă dacă o parte a lipirii e „seria”."""
    for x in ast.walk(n):
        if isinstance(x, ast.Name):
            yield x.id
        elif isinstance(x, ast.Attribute):
            yield x.attr
        elif isinstance(x, ast.Constant) and isinstance(x.value, str) and len(x.value) < 30:
            yield x.value


def _e_serie(nume):
    """Numele (identificator / cheie) e „seria”: unul din cuvintele lui (despărțite prin „_”) e `serie` / `seria` — pe cuvinte, cu
    operator de mulțime, nu „sub-șirul apare în nume” (core/test_garzi_pe_text.py)."""
    return bool({"serie", "seria"} & set(str(nume).lower().split("_")))


def _lipiri_serie_numar():
    """`serie + numar` / f"{serie}{numar}" compuse de mână (Python), oriunde în core/. Excepția: numărul NOU al facturii emise,
    compus o dată, la emitere, din seria și contorul firmei (`numar_int`) — acela e identificatorul ei, nu un text."""
    fisiere = [p for p in sorted(glob.glob(os.path.join(_RAD, "core", "*.py")))
               if not os.path.basename(p).startswith("test_") and os.path.basename(p) != "pdf_util.py"]
    assert len(fisiere) > 100, "scanul vede %d module în core/ — domeniul s-a rupt (anti-vacuu)" % len(fisiere)
    out = []
    for p in fisiere:
        out += _lipiri_in(io.open(p, encoding="utf-8").read(), os.path.basename(p))
    return out


def _lipiri_in(src, nume):
    """Lipirile seriei de număr din sursa `src` (modulul `nume`)."""
    out = []
    if "serie" not in src:
        return out
    for n in ast.walk(ast.parse(src)):
        st = dr = None
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
            st, dr = n.left, n.right
        elif isinstance(n, ast.JoinedStr):
            v = [x for x in n.values if isinstance(x, ast.FormattedValue)]
            for a, b in zip(n.values, n.values[1:]):
                if isinstance(a, ast.FormattedValue) and isinstance(b, ast.FormattedValue):
                    st, dr = a, b
                    break
        if st is None:
            continue
        ns, nd = set(_nume_in(st)), set(_nume_in(dr))
        if any(_e_serie(x) for x in ns) and any(x.startswith("numar") or x.startswith("nr") for x in nd) and "numar_int" not in nd:
            out.append("%s:%d" % (nume, n.lineno))
    return out


def test_textele_pentru_om_nu_lipesc_seria_de_numar():
    """3. GARD DE CLASĂ (Python): seria lipită de număr (`numar_cu_serie`) numai unde e identificatorul trimis la ANAF; orice text pentru om
    trece prin `serie_nr`. MUTAȚIE: `pdf_util.numar_cu_serie(serie, numar)` repus în `jurnal_api.eticheta_factura` -> pică.
    Garda JS (`${…serie}${…numar}` în static/js) e regula verificatorului SERIE_LIPITA (`core/test_lot11_u0_verificator.py`)."""
    rele = _apeluri_numar_cu_serie()
    assert not rele, "seria lipită de număr într-un text pentru om (443: „F6 nr. 1, nu F61”) — folosește pdf_util.serie_nr: %s" % rele


def test_calibrare_lipirea_de_mana_e_prinsa_iar_serie_nr_nu():
    """Anti-vacuu al gărzii de mai jos: forma lipită e găsită (în ambele scrieri), `serie_nr` și numărul nou al facturii nu."""
    assert _lipiri_in('def f(f, serie, numar):\n    return "Factură " + (serie or "") + numar\n', "a.py") == ["a.py:2"]
    assert _lipiri_in('def f(f):\n    return f"{f[\'serie\']}{f[\'numar\']}"\n', "b.py") == ["b.py:2"]
    assert _lipiri_in('def f(serie, numar):\n    return serie_nr(serie, numar)\n', "c.py") == []
    assert _lipiri_in('def f(serie, numar_int):\n    return serie + str(numar_int)\n', "d.py") == []


def test_nicio_lipire_de_mana_a_seriei_de_numar():
    """3b. Aceeași clasă, scrisă de mână (`(f.get("serie") or "") + str(f.get("numar"))`, f"{serie}{numar}"). MUTAȚIE:
    `"Factură " + (serie or "") + numar` adăugat într-un modul din core/ -> pică."""
    rele = _lipiri_serie_numar()
    assert not rele, "seria lipită de număr de mână (443) — folosește pdf_util.serie_nr: %s" % rele
