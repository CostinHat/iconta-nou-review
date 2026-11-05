# -*- coding: utf-8 -*-
"""scripts/oracol_pasi.py — oracolul pașilor (comanda 16.1-C3, pct.1): fișierul arhitectului `pasi_<lot>.txt` din ~/ghid_incoming (un rând pe aserțiune: „aserțiune | pas | ecran | operator |
valoare | descriere | sursă”) față de `docs/dovezi/<lot>/pasi.json` al lui Code (pe fiecare aserțiune: „id”, „operator” și „valoare” copiate literal, „cheie” a lui Code). Singurele coloane comparate
sunt operator + valoare; „descriere” nu. Funcțiile sunt pure; publica_lot.py le cheamă la publicare (STOP „oracol modificat”).
  oracol_pasi.py schelet <pasi_lot.txt> <pasi.json>   scrie pasi.json cu operator și valoare copiate literal și „cheie” goală, de completat de Code"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verifica_pas as VP  # noqa: E402

CAMPURI = ("id", "pas", "ecran", "operator", "valoare", "descriere", "sursa")


def parseaza(text):
    """-> ([rânduri {id, pas, ecran, operator, valoare, descriere, sursa}], [erori]). Antetul (primul rând și „Format:”) se sare; un rând cu alt număr de câmpuri sau cu operator
    necunoscut e eroare, nu e ghicit."""
    rez, erori = [], []
    for n, ln in enumerate(text.splitlines(), 1):
        if n == 1 or not ln.strip() or ln.startswith("Format:") or " | " not in ln:
            continue
        p = [x.strip() for x in ln.split(" | ")]
        if len(p) != len(CAMPURI):
            erori.append("rândul %d: %d câmpuri în loc de %d" % (n, len(p), len(CAMPURI)))
        elif p[3] not in VP.OPERATORI:
            erori.append("rândul %d (%s): operator necunoscut %r" % (n, p[0], p[3]))
        else:
            rez.append(dict(zip(CAMPURI, p)))
    return rez, erori


def refuzuri(text_arhitect, pasi_json):
    """Mesajele „oracol modificat” (listă goală = pasi.json copiază literal operator + valoare pentru fiecare aserțiune a arhitectului și nu are altele în plus)."""
    arh, erori = parseaza(text_arhitect)
    ref = ["fișierul arhitectului: " + e for e in erori]
    cod = {a.get("id"): a for a in (pasi_json or {}).get("asertiuni", [])}
    for a in arh:
        c = cod.get(a["id"])
        if c is None:
            ref.append("aserțiunea %s lipsește din pasi.json" % a["id"])
        elif c.get("operator") != a["operator"] or str(c.get("valoare")) != a["valoare"]:
            ref.append("aserțiunea %s: operator/valoare diferă de fișierul arhitectului (%s %r în pasi.json, %s %r la arhitect)" % (
                a["id"], c.get("operator"), c.get("valoare"), a["operator"], a["valoare"]))
        elif not str(c.get("cheie") or "").strip():
            ref.append("aserțiunea %s: fără cheie" % a["id"])
    ref += ["aserțiunea %s e în pasi.json, dar nu în fișierul arhitectului" % i for i in sorted(set(cod) - {a["id"] for a in arh})]
    return ref


def schelet(cale_txt, cale_json):
    arh, erori = parseaza(open(cale_txt, encoding="utf-8").read())
    if erori:
        print("\n".join(erori))
        return 1
    json.dump({"asertiuni": [{"id": a["id"], "pas": a["pas"], "operator": a["operator"], "valoare": a["valoare"], "cheie": ""} for a in arh]}, open(cale_json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("[oracol_pasi] %d aserțiuni -> %s" % (len(arh), cale_json))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "schelet":
        sys.exit(schelet(sys.argv[2], sys.argv[3]))
    print(__doc__)
    sys.exit(2)
