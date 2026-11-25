"""Grila personală Claude. Bază: grila.tsv. După publicare: grila_E_Q9.tsv grila_E_Q10.tsv manifest.json.
Cheile grilei originale rămân identice, inclusiv când o observație rămâne nemăsurată."""

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

P = Path(__file__).resolve().parent
PIN_F126 = "ae0e2d50eba76aa0d33c77c99059a0b00130369a4e227c4ab289a27147587d93"
CRIT = ("Funcțional", "Aspect", "Design", "Simplitate", "Conformitate", "Stabilitate")
DIM = ("1366x768", "603x590")


def citeste(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verifica(cond, motiv):
    if not cond:
        raise ValueError(motiv)


def seturi():
    rows = citeste(P / "inventar_Q10.tsv")
    coduri = {r["cod"] for r in rows}
    noi = {r["cod"] for r in rows if r["rol"] == "obiectiv"}
    verifica(len(rows) == len(coduri) == 45 and len(noi) == 28, "Inventar Pilot")
    return coduri, noi, coduri


def grila(path):
    inventar, _, _ = seturi()
    rows = citeste(path)
    d = {(r["cod"], r["criteriu"], r["rezolutie"]): r for r in rows}
    verifica(
        len(rows) == len(d) == 540
        and set(d) == {(c, k, z) for c in inventar for k in CRIT for z in DIM},
        "Grilă incompletă, cheie duplicată sau străină",
    )
    for key, r in d.items():
        verifica(
            r["valoare"] in {"1", "0", "-"} and bool(r["observatie"].strip()),
            "Valoare sau observație lipsă " + str(key),
        )
    return d


def bilant(d):
    inventar, _, _ = seturi()
    inchise = sorted(
        c
        for c in inventar
        if all(d[c, k, z]["valoare"] == "1" for k in CRIT for z in DIM)
    )
    return dict(
        inchise=inchise,
        scor=len(inchise),
        numitor=45,
        celule=dict(Counter(x["valoare"] for x in d.values())),
    )


def martor(root, r, interzise):
    rel = Path(r["dovada"])
    f = (root / rel).resolve()
    verifica(
        not rel.is_absolute()
        and f.is_relative_to(root)
        and f not in interzise
        and f.is_file()
        and f.stat().st_size
        and sha(f) == r["sha256"]
        and isinstance(r["localizare"], str)
        and r["localizare"].strip(),
        "Martor absent sau alterat",
    )
    return f


def moment(iso):
    value = datetime.fromisoformat(iso)
    verifica(
        value.tzinfo is not None and value.utcoffset() is not None,
        "Marcaj temporal fără fus",
    )
    return value


def confirma_actiune(r, publicare):
    cand = moment(r["moment_actiune"])
    verifica(cand >= publicare, "Acțiune înaintea publicării Q10")
    if r["cod"] == "F126":
        return (
            bool(r["index_spv"].strip())
            and r["stare_istoric"] == r["stare_detaliu"]
            and r["stare_istoric"] in ("trimisă", "acceptată")
        )
    if r["cod"] == "F179":
        interval = moment(r["intrare_ciorna"]) - cand
        return (
            r["cui_destinatar"] == "55229657"
            and bool(r["index_spv"].strip())
            and timedelta(0) <= interval <= timedelta(minutes=30)
            and r["stare_la_intrare"] == "ciornă"
        )
    return (
        r["rol"] == "asistent junior"
        and r["bun_venit_prima_intrare"] is True
        and r["deschidere_prezentare"] == "?"
        and r["poarta_configurata_in_prima_sesiune"] is True
        and r["prezentare_automata_prima"] is False
        and r["prezentare_automata_a_doua"] is False
        and moment(r["a_doua_intrare"]) > cand
    )


def dupa(before, after, manifest):
    b = grila(before)
    a = grila(after)
    v = bilant(a)
    baz = bilant(b)
    m = json.loads(manifest.read_text())
    for k in ("E_Q9", "E_Q10"):
        verifica(
            re.fullmatch(r"[0-9a-f]{40}", m[k]) is not None, "Commit incomplet " + k
        )
    verifica(
        m["E_Q9"] == "830d7c55845a90a1b911e54470b1c9e9863e32b5"
        and sha(before)
        == "d73dbd5198a8c64b195c7655918b9a1326505246551eb7e8d31da6c3fc2d93dd",
        "Baza oficială E_Q9 sau grila sa diferă",
    )
    verifica(
        m["E_Q9"] != m["E_Q10"] and m["autor"] == "Claude", "Autor sau versiune greșită"
    )
    verifica(
        m["sha256_inainte"] == sha(before) and m["sha256_dupa"] == sha(after),
        "Identitate tabele",
    )
    inventar, noi, atinse = seturi()
    root = manifest.resolve().parent
    interzise = {before.resolve(), after.resolve(), manifest.resolve()}
    observate = set()
    for r in m["remasurari"]:
        key = (r["cod"], r["criteriu"], r["rezolutie"])
        verifica(
            key in a and key not in observate and r["commit_servit"] == m["E_Q10"],
            "Identitate remăsurare " + str(key),
        )
        martor(root, r, interzise)
        verifica(
            r["valoare"] == a[key]["valoare"]
            and r["observatie"] == a[key]["observatie"],
            "Verdict diferit de tabel",
        )
        verifica(
            all(
                a[key].get(k) == r[k]
                for k in ("commit_servit", "dovada", "sha256", "localizare")
            ),
            "Trimitere diferită în tabel",
        )
        observate.add(key)
    verifica(observate == set(a), "Remăsurare incompletă")
    publicare = moment(m["publicat_la_Q10"])
    recipisa = martor(root, m["recipisa_publicare_Q10"], interzise)
    liniile = [l.split() for l in recipisa.read_text().splitlines()]
    verifica(
        any(
            len(l) >= 6
            and l[:3] == ["17.5-Q10", "publicare", "sfarsit"]
            and moment(l[3]) == publicare
            and 12 <= len(l[4]) <= 40
            and m["E_Q10"].startswith(l[4])
            and l[5] == "publicat"
            for l in liniile
            if len(l) >= 6 and l[:3] == ["17.5-Q10", "publicare", "sfarsit"]
        ),
        "Recipisa publicării Q10",
    )
    # Acțiunea F126 a fost acceptată pe E_Q9. Referința este fixată de autorul comenzii.
    anterior = json.loads((P / "actiune_F126_Q9.json").read_bytes())
    verifica(
        sha(P / "actiune_F126_Q9.json") == PIN_F126
        and anterior["cod"] == "F126"
        and anterior["commit_servit"] == m["E_Q9"]
        and anterior["actor"] == "Costin"
        and anterior["executat_de"].startswith("Claude"),
        "Martorul istoric F126 diferă",
    )
    gates = {"F126"}
    for r in m["actiuni_costin"]:
        c = r["cod"]
        verifica(
            c in {"F126", "F179", "X02"}
            and c not in gates
            and r["actor"] == "Costin"
            and r["commit_servit"] == m["E_Q10"]
            and r["document_sau_cont"].strip(),
            "Identitate acțiune externă",
        )
        martor(root, r, interzise)
        verifica(
            confirma_actiune(r, publicare),
            "Conținutul acțiunii externe nu confirmă scenariul " + c,
        )
        gates.add(c)
    dovezi_lipsa = []
    if "F026" in v["inchise"]:
        balanta = m.get("balanta_iulie_F1")
        if balanta is None:
            dovezi_lipsa.append("Balanța F1 la 31.07.2026 cu rulajul creditor 707")
            v["inchise"].remove("F026")
            v["scor"] = len(v["inchise"])
        else:
            from decimal import Decimal

            martor(root, balanta, interzise)
            verifica(
                balanta["cui"] == "401002001"
                and balanta["perioada"] == "2026-07"
                and balanta["data_balanta"] == "2026-07-31"
                and balanta["cont"] == "707"
                and Decimal(str(balanta["rulaj_creditor"])) == Decimal(1000),
                "Balanța sursă diferă de firma, luna, contul sau suma scenariului F026",
            )
    if "F019" in v["inchise"]:
        coada = m.get("coada_validare_F019", {})
        if not coada:
            dovezi_lipsa.append(
                "F019: coada Note de validat populată, la ambele rezoluții"
            )
            v["inchise"].remove("F019")
            v["scor"] = len(v["inchise"])
        else:
            verifica(set(coada) == set(DIM), "F019: lipsă sau surplus de rezoluții")
            for dim, proba in coada.items():
                f = martor(root, proba, interzise)
                date = json.loads(f.read_text(encoding="utf-8"))
                verifica(
                    date.get("sectiune") == "val-note"
                    and date.get("rezolutie") == dim
                    and date.get("commit_servit") == m["E_Q10"]
                    and isinstance(date.get("rol"), str)
                    and date["rol"].strip()
                    and type(date.get("id_nota")) is int
                    and date["id_nota"] > 0
                    and type(date.get("tenant_id")) is int
                    and date["tenant_id"] > 0
                    and type(date.get("id_coada")) is int
                    and date["id_coada"] > 0,
                    "F019: martor din altă secțiune, firmă de probă neidentificată sau rând absent",
                )
                for cheie in ("raspuns", "captura"):
                    original = martor(root, date[cheie], interzise | {f})
                    if cheie == "raspuns":
                        continut = json.loads(original.read_text(encoding="utf-8"))
                        elemente = continut.get("coada", [])
                        verifica(
                            any(
                                str(x.get("id")) == str(date["id_coada"])
                                and x.get("fel") == "nota"
                                and x.get("stare") == "la_senior"
                                and x.get("tenant_id") == date["tenant_id"]
                                and (x.get("nota") or {}).get("inregistrare_id")
                                == date["id_nota"]
                                for x in elemente
                            ),
                            "F019: elementul nu apare în răspunsul cozii",
                        )
                    else:
                        from citeste_rezultat_Q10 import png

                        png(original, tuple(map(int, dim.split("x"))))
    v["dovezi_lipsa"] = dovezi_lipsa
    lipsesc = sorted({"F126", "F179", "X02"} - gates)
    v["inchise"] = [cod for cod in v["inchise"] if cod not in lipsesc]
    v["scor"] = len(v["inchise"])
    pierdute = sorted(k for k in a if b[k]["valoare"] == "1" and a[k]["valoare"] != "1")
    v.update(
        tinta=45,
        regresii=pierdute,
        pozitii_neinchise=sorted(inventar - set(v["inchise"])),
        actiuni_lipsa=lipsesc,
        acceptat=v["scor"] == 45 and not lipsesc,
    )
    return v


def confrunta_rezumat(detaliat, rezumat):
    d = grila(detaliat)
    inventar, _, _ = seturi()
    with rezumat.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    verifica(
        len(rows) == 45 and {r["Cod"] for r in rows} == inventar,
        "Inventar sintetic diferit",
    )
    for r in rows:
        cod = r["Cod"]
        for k in CRIT:
            valori = [d[cod, k, z]["valoare"] for z in DIM]
            asteptat = "-" if "-" in valori else min(valori)
            verifica(r[k] == asteptat, "Criteriu agregat diferit " + cod + " " + k)
        asteptat_functie = (
            "nemăsurat"
            if any(r[k] == "-" for k in CRIT)
            else "ok"
            if all(r[k] == "1" for k in CRIT)
            else "nu merge"
        )
        verifica(r["Verdict"] == asteptat_functie, "Verdict sintetic diferit " + cod)
        for z, nume in zip(DIM, ("Scor laptop 1366×768", "Scor ecran mic 603×590")):
            valori = [d[cod, k, z]["valoare"] for k in CRIT[:-1]]
            if "-" not in valori:
                verifica(
                    r[nume] == f"{valori.count('1')}/5",
                    "Subtotal diferit " + cod + " " + z,
                )
            elif all(v == "-" for v in valori):
                verifica(r[nume] == "-", "Subtotal nemăsurat diferit " + cod + " " + z)
    return bilant(d)


def proba():
    """Exercită parserul aceleiași grile și identificarea martorilor pe copii temporare."""
    from tempfile import TemporaryDirectory

    baza = P / "grila_E_Q9.tsv"
    originale = citeste(baza)
    grila(baza)
    with TemporaryDirectory() as temp:
        rad = Path(temp)
        fisier = rad / "grila.tsv"
        for nume, randuri in (
            ("lipsă", originale[:-1]),
            ("dublură", [originale[0], *originale[:-1]]),
            ("criteriu străin", [dict(originale[0], criteriu="Altul"), *originale[1:]]),
            ("observație goală", [dict(originale[0], observatie=" "), *originale[1:]]),
            ("valoare străină", [dict(originale[0], valoare="2"), *originale[1:]]),
        ):
            with fisier.open("w", newline="", encoding="utf8") as flux:
                writer = csv.DictWriter(flux, fieldnames=originale[0], delimiter="\t")
                writer.writeheader()
                writer.writerows(randuri)
            try:
                grila(fisier)
            except ValueError:
                continue
            raise AssertionError("Grilă acceptată cu " + nume)
        referinta = dict(dovada="grila.tsv", sha256=sha(fisier), localizare="rând 2")
        assert martor(rad, referinta, set()) == fisier
        for caz in (
            dict(referinta, sha256="0" * 64),
            dict(referinta, localizare=""),
            dict(referinta, dovada="../absent"),
        ):
            try:
                martor(rad, caz, set())
            except ValueError:
                continue
            raise AssertionError("Martor invalid acceptat")
    print("PROBE OK: 5 grile negative, 3 martori negativi, grilă și martor valabile")


if __name__ == "__main__":
    if sys.argv[1:] == ["--proba"]:
        proba()
        raise SystemExit(0)
    if len(sys.argv) == 2:
        rezultat = bilant(grila(Path(sys.argv[1])))
    elif len(sys.argv) == 4 and sys.argv[1] == "--rezumat":
        rezultat = confrunta_rezumat(Path(sys.argv[2]), Path(sys.argv[3]))
    elif len(sys.argv) == 4:
        rezultat = dupa(*(Path(v) for v in sys.argv[1:]))
    else:
        raise SystemExit(__doc__)
    print(json.dumps(rezultat, ensure_ascii=False, indent=2))
    raise SystemExit(0 if rezultat.get("acceptat", True) else 1)
