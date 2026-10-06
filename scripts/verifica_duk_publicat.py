# -*- coding: utf-8 -*-
"""scripts/verifica_duk_publicat.py — validatoarele DUK instalate sunt cele PUBLICATE de ANAF?

[comanda Costin 07.10.2026, C3] „Verifică întâi dacă validatorul D112 instalat e ultima versiune publicată de ANAF.” Măsurat:
D112 instalat = J27.0.1 (08.08.2026), publicat = J27.0.6 (14.09.2026); diferența era chiar regula salariului minim (J27.0.2,
„corectie regula salmin”), iar validatorul vechi semnala drept atenționare un D112 corect. Încă 4 validatoare erau în urmă
(D100, D101, D710, B230). Validatorul e judecătorul final (CLAUDE.md) — un judecător vechi judecă după altă lege.

CE FACE:
  ./venv/bin/python scripts/verifica_duk_publicat.py            # descarcă versiuni.xml de la ANAF, compară cu manifestul
                                                                 # (anaf_surse/duk_instalat.json); exit 1 dacă vreunul e în urmă
  ./venv/bin/python scripts/verifica_duk_publicat.py --scrie    # DUPĂ instalare: scrie anaf_surse/versiuni.xml (copia oficială)
                                                                 # și manifestul (versiunea publicată + sha256 al jarului instalat)
Garda din poartă (`core/test_duk_instalat.py`) nu are rețea: cere ca jarurile instalate să fie cele din manifest, manifestul să
spună aceleași versiuni ca `anaf_surse/versiuni.xml`, iar verificarea online să nu fie mai veche de ZILE_MAX.
"""
import datetime
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_VERSIUNI = "https://static.anaf.ro/static/10/Anaf/update5/versiuni.xml"   # = urlVersiuni din ~/duk/dist/config/config.properties
LIB = os.path.expanduser("~/duk/dist/lib")
VERSIUNI_LOCAL = os.path.join(RAD, "anaf_surse", "versiuni.xml")
MANIFEST = os.path.join(RAD, "anaf_surse", "duk_instalat.json")
#: Cât de veche poate fi ultima comparație cu ANAF până când poarta o cere din nou. Nu e o valoare fiscală, e o CADENȚĂ: ANAF a
#: publicat D112 de patru ori în august 2026; 30 de zile înseamnă că un validator nu poate rămâne în urmă mai mult de o lună.
ZILE_MAX = 30


def versiuni(xml_text):
    """{declaratie: (versiuneJ, jar)} din versiuni.xml."""
    out = {}
    for m in re.finditer(r"<(\w+)>\s*<versiuneJ>([^<]*)</versiuneJ>.*?<JURL>([^<]*)</JURL>", xml_text, re.S):
        out[m.group(1)] = (m.group(2).strip(), m.group(3).strip().rsplit("/", 1)[-1])
    return out


def sha(cale):
    return hashlib.sha256(open(cale, "rb").read()).hexdigest()


def instalate():
    return sorted(f for f in os.listdir(LIB) if f.endswith("Validator.jar") and f != "Validator.jar")


def main():
    publicat = urllib.request.urlopen(URL_VERSIUNI, timeout=60).read().decode("utf-8", "replace")
    pv = versiuni(publicat)
    if "--scrie" in sys.argv:
        io.open(VERSIUNI_LOCAL, "w", encoding="utf-8").write(publicat)
        man = {"verificat_la": datetime.date.today().isoformat(), "sursa": URL_VERSIUNI, "validatoare": {}}
        for tip, (ver, jar) in sorted(pv.items()):
            if jar in instalate():
                man["validatoare"][tip] = {"jar": jar, "versiuneJ": ver, "sha256": sha(os.path.join(LIB, jar))}
        json.dump(man, io.open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        print("scris: %d validatoare, verificat_la %s" % (len(man["validatoare"]), man["verificat_la"]))
        return 0
    man = json.load(io.open(MANIFEST, encoding="utf-8"))
    in_urma = [(tip, v["versiuneJ"], pv.get(tip, ("?",))[0]) for tip, v in sorted(man["validatoare"].items())
               if pv.get(tip, (v["versiuneJ"],))[0] != v["versiuneJ"]]
    for t in in_urma:
        print("ÎN URMĂ: %s instalat %s, publicat %s" % t)
    print("comparate %d · în urmă %d" % (len(man["validatoare"]), len(in_urma)))
    return 1 if in_urma else 0


if __name__ == "__main__":
    sys.exit(main())
