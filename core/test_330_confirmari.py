# -*- coding: utf-8 -*-
"""[deficiența 330, comanda Costin 8.1, 18.10.2026, verbatim în DECIZII „Comanda 8.1”] „Confirmarea renunțării are «Renunță la factură» și
«Renunță» alăturate.” Refuzul implicit al casetei de confirmare (`api.js::confirmaCaseta`) e „Renunță”: o confirmare a cărei acțiune
începe cu „Renunț…” trebuie să-și numească refuzul altfel (`textNu`), altfel două butoane alăturate spun „Renunță” cu sensuri opuse.
Garda parcurge TOATE apelurile `confirmaCaseta(` din static."""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _apeluri(text):
    """(linie, argumentele apelului) pentru fiecare `confirmaCaseta(` — parantezele echilibrate, șirurile sărite."""
    for m in re.finditer(r"\bconfirmaCaseta\(", text):
        i, n, sir = m.end(), 1, None
        while i < len(text) and n:
            c = text[i]
            if sir:
                if c == "\\":
                    i += 1
                elif c == sir:
                    sir = None
            elif c in "\"'`":
                sir = c
            elif c == "(":
                n += 1
            elif c == ")":
                n -= 1
            i += 1
        yield text[:m.start()].count("\n") + 1, text[m.end():i - 1]


def _js():
    for d, _s, fs in os.walk(os.path.join(RAD, "static", "js")):
        for f in fs:
            if f.endswith(".js"):
                cale = os.path.join(d, f)
                yield os.path.relpath(cale, RAD), open(cale, encoding="utf-8").read()


def rele(fisiere=None):
    out = []
    for cale, t in (fisiere or _js()):
        for ln, arg in _apeluri(t):
            ok = re.search(r"textOk\s*:\s*[\"'`]\s*(Renun\S*)", arg)
            if ok and "textNu" not in arg:
                out.append("%s:%d textOk „%s…” fără textNu" % (cale, ln, ok.group(1)))
    return out


def test_330_nicio_confirmare_cu_doua_renunta():
    toate = list(_js())
    assert sum(1 for _c, t in toate for _ in _apeluri(t)) >= 40, "anti-vacuu: apelurile confirmaCaseta nu mai sunt găsite"
    assert not rele(toate), rele(toate)


def test_330_CALIBRARE_forma_veche_e_prinsa():
    rau = [("static/js/x.js", 'confirmaCaseta(b, "Renunți?", () => { f(); }, { textOk: "Renunță la factură" });')]
    assert rele(rau), "garda nu vede forma veche (deficiența 330)"
    bun = [("static/js/x.js", 'confirmaCaseta(b, "Renunți?", () => { f(); }, { textOk: "Da, renunț", textNu: "Continui" });')]
    assert not rele(bun)
