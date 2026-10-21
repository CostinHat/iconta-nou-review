# -*- coding: utf-8 -*-
"""[lotul 10, C73 / U3, clasa 410] Un refuz numit al serverului nu se înghite în ecran: „Setări cont -> Date cabinet” prindea orice
eroare și arăta „Eroare la salvare.”, deci refuzul C73 („CUI-ul … e deja înregistrat pe iConta.eu pentru alt cabinet”) nu ajungea la om.
GARD: niciun `catch (x) { … }` din `static/js` nu arată (prin `arataMesaj(…, "eroare")`) un text fix fără să folosească eroarea prinsă
(`x.mesaj`). Textul fix rămâne permis ca rezervă (`(e && e.mesaj) || "…"`).
MUTAȚIE: un catch din `setari.js` readus la forma veche -> pică."""
import glob
import io
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CATCH = re.compile(r"catch\s*\((\w+)\)\s*\{")


def _corp(s, i):
    """Corpul blocului care începe la `{` de la poziția i (acoladele numărate; șirurile simple, suficient pentru șabloanele noastre)."""
    adanc, j = 0, i
    while j < len(s):
        if s[j] == "{":
            adanc += 1
        elif s[j] == "}":
            adanc -= 1
            if adanc == 0:
                return s[i + 1:j]
        j += 1
    return s[i + 1:]


def inghitite(s):
    out = []
    for m in _CATCH.finditer(s):
        var, corp = m.group(1), _corp(s, m.end() - 1)
        if re.search(r'arataMesaj\([^;]*?,\s*"eroare"\)', corp) and not re.search(r"\b%s\b" % re.escape(var), corp):
            out.append(s[:m.start()].count("\n") + 1)
    return out


def test_niciun_catch_nu_inlocuieste_refuzul_serverului_cu_un_text_fix():
    rele = []
    for f in sorted(glob.glob(os.path.join(_RAD, "static", "js", "**", "*.js"), recursive=True)):
        for ln in inghitite(io.open(f, encoding="utf-8").read()):
            rele.append("%s:%d" % (os.path.relpath(f, _RAD), ln))
    assert rele == [], rele


def test_scanul_vede_forma_veche_si_lasa_rezerva():
    """Anti-vacuu."""
    assert inghitite('} catch (e) { arataMesaj(msg, "Eroare la salvare.", "eroare"); }') == [1]
    assert inghitite('} catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la salvare.", "eroare"); }') == []
    assert inghitite('} catch (err) {\n  arataMesaj(z, "Nu s-a putut.", "eroare");\n}') == [1]
