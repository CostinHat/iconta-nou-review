"""Verifică identitățile și fișierele celor 55 de rânduri. Examinarea conținutului rămâne separată."""
import argparse
import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


def tabel(cale):
    with cale.open(encoding="utf-8", newline="") as stream:
        rows = csv.DictReader(stream, delimiter="\t")
        cols = rows.fieldnames or []
        if len(cols) != len(set(cols)):
            raise ValueError(f"Coloane duplicate: {cale}")
        result = {}
        for row in rows:
            if None in row or None in row.values():
                raise ValueError(f"Linie incompletă în {cale}")
            key = tuple(row[col] for col in ("cod", "criteriu", "rezolutie"))
            if key in result:
                raise ValueError(f"Cheie repetată: {key}")
            result[key] = row
    return result


def verifica(cale, dosar, sha):
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Commit întreg obligatoriu")
    contract = tabel(Path(__file__).with_name("celule_17_5_Q12.tsv"))
    if Counter(r["E11"] for r in contract.values()) != {"0": 45, "-": 10}:
        raise ValueError("Contract de bază incomplet")
    rows = tabel(cale)
    if rows.keys() != contract.keys():
        raise ValueError("Chei străine sau lipsă")
    counts = Counter()
    root = dosar.resolve(strict=True)
    for key, r in rows.items():
        stare = r["rezultat"]
        if r["commit"] != sha or stare not in {"1", "0", "-"} or not r["observatie"].strip():
            raise ValueError(f"Commit, stare sau observație greșită: {key}")
        if stare == "-" and (r["martor"], r["sha256"]) == ("", ""):
            counts[(contract[key]["E11"], stare)] += 1
            continue
        rel = Path(r["martor"])
        if rel.is_absolute() or ".." in rel.parts or not rel.parts:
            raise ValueError(f"Cale neadmisă: {key}")
        path = (root / rel).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Martor lipsă: {key}")
        with path.open("rb") as f:
            actual = hashlib.file_digest(f, "sha256").hexdigest()
        if actual != r["sha256"]:
            raise ValueError(f"SHA-256 diferit: {key}")
        counts[(contract[key]["E11"], stare)] += 1
    return counts


def proba():
    import tempfile

    contract = tabel(Path(__file__).with_name("celule_17_5_Q12.tsv"))
    sha = "a" * 40
    fields = ["cod", "criteriu", "rezolutie", "commit", "rezultat", "observatie", "martor", "sha256"]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "eveniment").write_bytes(b"proba")
        digest = hashlib.sha256(b"proba").hexdigest()
        rows = [dict(zip(fields, (*key, sha, "1", "probă controlată", "eveniment", digest)))
                for key in contract]
        def masura(date):
            f = root / "raport.tsv"
            with f.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
                writer.writeheader()
                writer.writerows(date)
            return verifica(f, root, sha)
        if masura(rows) != {("0", "1"): 45, ("-", "1"): 10}:
            raise RuntimeError("Inventar pozitiv greșit")
        for invalid in [
            rows[:-1], rows + [rows[0]],
            [dict(rows[0], commit="b"*40), *rows[1:]],
            [dict(rows[0], martor="../strain"), *rows[1:]],
            [dict(rows[0], sha256="0"*64), *rows[1:]],
            [dict(rows[0], rezultat="da"), *rows[1:]],
            [dict(rows[0], observatie=""), *rows[1:]],
        ]:
            try:
                masura(invalid)
            except ValueError:
                continue
            raise RuntimeError("Verificatorul a acceptat un raport alterat")
    print("PROBE OK: control pozitiv și 7 refuzuri")


if __name__ == "__main__":
    if sys.argv[1:] == ["--proba"]:
        proba()
        raise SystemExit(0)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rezultate", type=Path)
    parser.add_argument("director_dovezi", type=Path)
    parser.add_argument("commit")
    parser.add_argument("--faza", choices=("inventar", "candidat", "inchidere"), required=True)
    a = parser.parse_args()
    total = verifica(a.rezultate, a.director_dovezi, a.commit)
    for (baza, acum), nr in sorted(total.items()):
        print(f"E11 {baza} -> {acum}: {nr}")
    if a.faza == "candidat" and (total["0", "1"] != 45 or total["-", "0"]):
        raise SystemExit("Candidat cu reparații lipsă sau dependență măsurată roșie")
    if a.faza == "inchidere" and sum(n for (_, stare), n in total.items() if stare == "1") != 55:
        raise SystemExit("Pilot încă deschis în cele 55 de celule")
    print("Inventar verificat. Conținutul martorilor se judecă pe criteriile fiecărui rând.")
