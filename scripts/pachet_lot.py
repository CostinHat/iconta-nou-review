# -*- coding: utf-8 -*-
"""PACHETUL UNUI LOT — ZIP-ul cu tot ce s-a schimbat, cu amprenta lui și cu duratele măsurate.

CERUT (Costin, 15.09.2026, punctul 4): *„La închiderea fiecărui lot: ZIP cu tot ce s-a schimbat
(cod, probe, registre, artefacte de măsurare), calea exactă și SHA-256 în raport, plus durata
măsurată a fiecărei operații."*

DE CE E UN INSTRUMENT, nu o comandă `zip` scrisă de mână la fiecare lot. Trei motive, fiecare cu
felul lui de eșec:

  1. **ce intră în pachet se DERIVĂ din git**, nu se enumeră din memorie — un fișier uitat face
     pachetul să mintă tocmai despre ce a lipsit;
  2. **amprenta se calculează ȘI se verifică**: după scriere, ZIP-ul se recitește de pe disc și i se
     recalculează SHA-256. *O amprentă calculată din ce am vrut să scriu, nu din ce e pe disc, e o
     afirmație despre intenție;*
  3. **duratele nu se estimează**: intră în pachet numai dacă lotul le-a măsurat și le-a scris
     într-un fișier. Fără fișier, `DURATE.json` lipsește din pachet și manifestul o SPUNE — o durată
     inventată e mai rea decât una absentă.

ANTI-VACUU: un pachet gol, sau unul din care lipsește un fișier numit explicit, e o EROARE, nu un
pachet mic. Un instrument de împachetare care reușește pe zero fișiere raportează verde despre
o muncă pe care n-a văzut-o.

CUM SE RULEAZĂ:
    ./venv/bin/python scripts/pachet_lot.py --nume lot_f_d300 --de-la <sha> \\
        [--durate /tmp/durate_lot_f.json] [--in-plus frontend_test/proba_e2_lot_f_d300.json]
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSAR = os.path.join(RAD, "pachete_loturi")


def _git(*a):
    return subprocess.run(["git"] + list(a), cwd=RAD, capture_output=True, text=True).stdout


def amprenta(cale):
    """SHA-256 al unui fișier, citit de pe DISC."""
    h = hashlib.sha256()
    with open(cale, "rb") as f:
        for buc in iter(lambda: f.read(1 << 20), b""):
            h.update(buc)
    return h.hexdigest()


def fisiere_lotului(de_la, in_plus):
    """Ce s-a schimbat de la `de_la` încoace — comise ȘI necomise —, plus ce s-a cerut explicit.

    Se iau amândouă: un lot se închide cu un commit, dar artefactele de măsurare (JSON-urile
    probelor) sunt adesea netracked, iar ele sunt chiar dovada. Ce e numit în `--in-plus` și
    lipsește de pe disc OPREȘTE pachetul.
    """
    out = []
    for linie in _git("diff", "--name-only", de_la, "HEAD").splitlines():
        if linie.strip():
            out.append(linie.strip())
    for linie in _git("status", "--porcelain").splitlines():
        nume = linie[3:].strip()
        if nume and not nume.endswith("/"):
            out.append(nume)
    for nume in in_plus or []:
        out.append(nume)
    vazute, curat = set(), []
    for n in out:
        if n in vazute:
            continue
        vazute.add(n)
        if os.path.exists(os.path.join(RAD, n)):
            curat.append(n)
        elif n in (in_plus or []):
            raise SystemExit("cerut explicit dar inexistent pe disc: %s" % n)
    return sorted(curat)


def construieste(nume, de_la, durate, in_plus):
    fisiere = fisiere_lotului(de_la, in_plus)
    if not fisiere:
        raise SystemExit("ANTI-VACUU: niciun fișier schimbat de la %s — un pachet gol nu e un "
                         "pachet mic, e o măsurătoare greșită a ce s-a lucrat" % de_la)
    if not os.path.isdir(DOSAR):
        os.makedirs(DOSAR)
    cale_zip = os.path.join(DOSAR, "%s.zip" % nume)

    rand = []
    for f in fisiere:
        p = os.path.join(RAD, f)
        rand.append({"fisier": f, "octeti": os.path.getsize(p), "sha256": amprenta(p)})

    d = None
    if durate:
        if not os.path.exists(durate):
            raise SystemExit("fișierul de durate nu există: %s (nu se inventează)" % durate)
        d = json.loads(io.open(durate, encoding="utf-8").read())

    manifest = ["# PACHETUL LOTULUI `%s`" % nume, "",
                "HEAD: `%s`" % _git("rev-parse", "HEAD").strip(),
                "de la: `%s`" % de_la, "",
                "## Fișiere (%d)" % len(rand), "",
                "| fișier | octeți | SHA-256 |", "|---|---:|---|"]
    for r in rand:
        manifest.append("| `%s` | %d | `%s` |" % (r["fisier"], r["octeti"], r["sha256"]))
    manifest += ["", "## Durate măsurate", ""]
    if d:
        manifest += ["| operația | secunde |", "|---|---:|"]
        for k, v in d.items():
            manifest.append("| %s | %s |" % (k, v))
    else:
        manifest.append("**absente** — lotul n-a scris un fișier de durate. Nu se estimează.")
    text_manifest = "\n".join(manifest) + "\n"

    with zipfile.ZipFile(cale_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for r in rand:
            z.write(os.path.join(RAD, r["fisier"]), r["fisier"])
        z.writestr("MANIFEST.md", text_manifest)
        z.writestr("FISIERE.json", json.dumps(rand, indent=1, ensure_ascii=False))
        if d:
            z.writestr("DURATE.json", json.dumps(d, indent=1, ensure_ascii=False))

    # amprenta se recalculează DE PE DISC, după închiderea arhivei
    sha = amprenta(cale_zip)
    with zipfile.ZipFile(cale_zip) as z:
        stricat = z.testzip()
    if stricat:
        raise SystemExit("arhiva e coruptă la %s" % stricat)
    return {"cale": cale_zip, "sha256": sha, "octeti": os.path.getsize(cale_zip),
            "fisiere": len(rand), "durate": bool(d), "manifest": text_manifest}


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--nume", required=True)
    p.add_argument("--de-la", required=True, help="SHA de la care se ia diferența")
    p.add_argument("--durate", default=None)
    p.add_argument("--in-plus", action="append", default=[])
    a = p.parse_args(argv)
    r = construieste(a.nume, a.de_la, a.durate, a.in_plus)
    print(r["manifest"])
    print("=" * 70)
    print("CALEA EXACTĂ : %s" % r["cale"])
    print("SHA-256      : %s" % r["sha256"])
    print("OCTEȚI       : %d · FIȘIERE: %d · DURATE: %s"
          % (r["octeti"], r["fisiere"], "da" if r["durate"] else "NU"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
