# -*- coding: utf-8 -*-
"""scripts/genereaza_declaratii_lista.py — cele 50 de declaratii, DERIVATE, pentru ecranul public.

DE UNDE VINE TEXTUL, si de ce nu l-am scris eu. Fiecare `core/dNNN.py` are pe primul rand al
docstringului denumirea OFICIALA a declaratiei — „D205 (Declaratie informativa privind impozitul
retinut la sursa...)". Cincizeci din cincizeci. Aia e sursa: e langa cod, se schimba odata cu el, si
a fost scrisa cand s-a implementat generatorul, nu azi, de mine, ca sa umplu un ecran.

*Un text scris de mana aici ar fi a doua descriere a aceluiasi lucru — si prima care imbatraneste.*

Lista tipurilor vine din `declaratii_api.DECLARATII`, nu dintr-o enumerare: o declaratie noua intra
singura, iar garda cere ca ecranul sa le arate pe toate cate sunt.

Blocul se scrie in `static/js/ecrane/login.js`, intre ancore, exact ca `GRUPE_FUNC`.
"""
import io
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

from core import declaratii_api as da  # noqa: E402

TINTA = os.path.join(RAD, "static", "js", "ecrane", "login.js")
START = "// <DECLARATII_AUTO> generat de genereaza_declaratii_lista.py --scrie; NU edita manual intre ancore"
STOP = "// </DECLARATII_AUTO>"

#: Prefixele tehnice ale docstringului, care nu spun nimic unui contabil.
_PREFIX = re.compile(r"^(core/d\d+[a-z]*\.py\s*[—-]+\s*|Modul\s+D\d+[A-Z]*\s*[—-]+\s*)", re.I)
#: „D205 (Declaratie ...", „D205: Declaratie ...", „D205 - Declaratie ..."
_COD = re.compile(r"^D\d+[A-Za-z]*\s*[(:—-]\s*", re.I)


def _denumire(tip):
    """Denumirea oficiala, din constanta modulului. NU din docstring.

    Prima forma citea proza docstringului si o curata cu doua expresii regulate. Mergea, dar avea
    doua defecte: textul iesea FARA diacritice (docstringurile vechi sunt ASCII), iar „prima
    propozitie a unui docstring" nu e un contract — se schimba la orice rescriere de comentariu.
    Acum fiecare `core/dNNN.py` poarta `DENUMIRE_OFICIALA`, si aia e sursa: un camp, nu o proza."""
    import importlib
    m = importlib.import_module("core." + tip)
    return (getattr(m, "DENUMIRE_OFICIALA", "") or "").strip()


def lista():
    out = []
    for tip in sorted(da.DECLARATII):
        per = da.DECLARATII[tip][0]
        out.append({"tip": tip.upper(), "per": per, "ce_e": _denumire(tip)})
    return out


def main(argv):
    date = lista()
    goale = [d["tip"] for d in date if not d["ce_e"]]
    if goale:
        print("REFUZ: %d declaratii fara DENUMIRE_OFICIALA: %s" % (len(goale), goale))
        print("  Se completeaza in , langa generatorul ei — nu aici.")
        print("  (Altfel o declaratie noua ar aparea pe ecranul public fara nume.)")
        return 2

    bloc = "%s\nconst DECLARATII_50 = %s;\n%s" % (
        START, json.dumps(date, ensure_ascii=False), STOP)

    if "--scrie" not in argv:
        print("%d declaratii; primele trei:" % len(date))
        for d in date[:3]:
            print("   %-6s %-13s %s" % (d["tip"], d["per"], d["ce_e"][:80]))
        print("\n(--scrie ca sa il pui in login.js)")
        return 0

    s = io.open(TINTA, encoding="utf-8").read()
    if START in s:
        a = s.index(START)
        b = s.index(STOP) + len(STOP)
        s = s[:a] + bloc + s[b:]
    else:
        ancora = "// <GRUPE_FUNC_AUTO>"
        i = s.index(ancora)
        s = s[:i] + bloc + "\n" + s[i:]
    io.open(TINTA, "w", encoding="utf-8", newline="").write(s)
    print("scris in %s: %d declaratii" % (os.path.relpath(TINTA, RAD), len(date)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
