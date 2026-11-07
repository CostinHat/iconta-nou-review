# -*- coding: utf-8 -*-
"""Script de unică folosință (17.3, pct.2 d): pe cele 105 intrări din catalog, la 1366×768, starea ferestrei de sus: „←” activ? formular? „Renunță” în bară? al ecranului?
Uz: ./venv/bin/python docs/dovezi/17_3/proba_inapoi.py <director_ieșire>   (8019 pornit din acest arbore, baza restaurată)"""
import contextlib
import io
import json
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import verificator_design as VD  # noqa: E402

JS = os.path.join(RAD, "docs", "dovezi", "17_3", "proba_inapoi.js")


def main(iesire):
    os.makedirs(iesire, exist_ok=True)
    rez = []
    for e in VD.registru():
        nume = e["nume"]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                VD.ecran(nume, "1366x768", iesire, masuri_alt=JS, director_png=os.path.join(iesire, "png"))
            m = json.load(open(os.path.join(iesire, "%s_1366x768.json" % VD.slug(nume)), encoding="utf-8"))
            r = dict(m.get("masuri_alt") or {}, ecran=nume, eroare=m.get("eroare_deschidere"))
        except Exception as ex:  # noqa: BLE001
            r = {"ecran": nume, "eroare": str(ex)[:200]}
        rez.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
    json.dump(rez, open(os.path.join(iesire, "proba_inapoi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
