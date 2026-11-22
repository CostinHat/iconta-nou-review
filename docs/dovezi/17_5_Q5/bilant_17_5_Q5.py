"""Utilizare: python bilant_17_5_Q3.py REPER_R62.csv BAZA_Q2.csv DUPA_Q3.csv.

CSV-urile au schema exportului Pilot. Identitatea, data și probele se atașează
separat exporturilor. Calculează scorul efectiv și publică inclusiv lipsurile.
"""
import csv
import sys

CRITERII = ("Funcțional", "Aspect", "Design", "Simplitate", "Conformitate", "Stabilitate")


def citeste(cale):
    with open(cale, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        if not set(("Cod", *CRITERII)).issubset(lector.fieldnames or []):
            raise ValueError(f"Antet incomplet în {cale}")
        pozitii = {}
        for r in lector:
            cod = r["Cod"].strip()
            valori = tuple(r[c].strip() for c in CRITERII)
            if not cod or cod in pozitii or not set(valori) <= {"0", "1", "-"}:
                raise ValueError(f"Rând nevalid: {cod} {valori}")
            pozitii[cod] = valori
    if len(pozitii) != 45:
        raise ValueError(f"{cale}: {len(pozitii)} poziții în loc de 45")
    return pozitii


def bilant(reper, baza, dupa):
    if set(reper) != set(baza) or set(reper) != set(dupa):
        raise ValueError("Pozițiile diferă de cele 45 din exportul Pilot")
    ok = lambda r: {cod for cod, v in r.items() if v == ("1",) * len(CRITERII)}
    a, b = ok(baza), ok(dupa)
    return {"inchise": sorted(b-a), "redeschise": sorted(a-b), "net":len(b)-len(a),
            "inainte":len(a), "dupa":len(b), "total":len(reper),
            "tinta_10": len(b)>=10, "tinta_pozitii":{cod:cod in b for cod in ("F081","F089","F122")},
            "criterii_nejudecate_dupa": {cod:[c for c,x in zip(CRITERII,v) if x=="-"]
                                        for cod,v in dupa.items() if "-" in v}}


if __name__ == "__main__":
    import json
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    print(json.dumps(bilant(*(citeste(p) for p in sys.argv[1:])), ensure_ascii=False, indent=2))
