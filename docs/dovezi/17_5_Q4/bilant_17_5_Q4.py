"""Utilizare: python bilant_17_5_Q4.py REPER_R62.csv BAZA_Q5.csv DUPA_Q4.csv.

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
    degradate = sorted(cod for cod in a - b if "0" in dupa[cod])
    acoperire_pierduta = sorted((a - b) - set(degradate))
    modificari = []
    for cod in sorted(baza):
        for criteriu, x, y in zip(CRITERII, baza[cod], dupa[cod]):
            if x != y:
                modificari.append({"cod": cod, "criteriu": criteriu, "inainte": x, "dupa": y})
    return {"inchise": sorted(b - a), "redeschise": degradate,
            "net_inchise_minus_redeschise": len(b - a) - len(degradate),
            "pierdute_din_acoperire": acoperire_pierduta, "variatie_scor": len(b) - len(a),
            "inainte": len(a), "dupa": len(b), "total": len(reper), "tinta_45": len(b) == 45,
            "criterii_masurate": sum(x != "-" for v in dupa.values() for x in v),
            "criterii_totale": len(dupa) * len(CRITERII), "modificari_criterii": modificari,
            "criterii_nejudecate_dupa": {cod: [c for c, x in zip(CRITERII,v) if x == "-"]
                                         for cod,v in dupa.items() if "-" in v}}


if __name__ == "__main__":
    import json
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    print(json.dumps(bilant(*(citeste(p) for p in sys.argv[1:])), ensure_ascii=False, indent=2))
