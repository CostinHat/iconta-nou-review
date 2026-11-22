"""Exportă numai din obiectele Git ale ramurii Q. Scrie în directorul nou indicat."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

E = "b0e9821cde199ca03bb15385b9d42d461eb87cea"
P0 = "55ca882a7f923616a0ebbd208135a2a3c5102426"
P = "1eb4c52df1e7f8668803f1c179e857346f2ea726"
URME = "70378b86c47ec3894815832d9ccddfe9633e478a"
CORE = ("core/d110.py", "core/uc_declaratii.py")
ECRANE = ("migrare", "firme", "control_verdict", "declaratii")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", type=Path)
    ap.add_argument("director_nou", type=Path)
    a = ap.parse_args()

    def git(*args):
        return subprocess.run(["git", "-C", str(a.repo), *args], stdout=subprocess.PIPE, check=True).stdout

    for copil, parinte in ((URME, P), (P, P0), (P0, E)):
        if git("rev-parse", copil + "^").decode().strip() != parinte:
            raise ValueError("Lanțul Q diferă la " + copil)
    cai = git("diff", "--name-only", "--no-renames", "-z", E, P, "--", "static", *CORE).decode().split("\0")[:-1]
    if not set(CORE).union(f"static/js/ecrane/{s}.js" for s in ECRANE).issubset(cai):
        raise ValueError("Lipsesc surse ale implementării Q")
    for cale in cai:
        if cale not in CORE and not cale.startswith("static/js/") and cale not in ("static/index.html", "static/spv_callback.html"):
            raise ValueError("Cale în afara perimetrului: " + cale)
    produs = git("diff", "--no-color", "--src-prefix=a/", "--dst-prefix=b/",
                 "--no-ext-diff", "--no-textconv", "--no-renames", "--binary", "--full-index", E, P, "--", *cai)
    if not produs.startswith(b"diff --git a/"):
        raise ValueError("Prefix de patch neașteptat")
    corectie = json.loads(Path(__file__).with_name("corectie_626_17_5_Q2.json").read_text())
    vechi = git("show", P + ":core/d110.py").decode()
    litera = '"626": "' + corectie["vechi"] + '"'
    comentariu = "semnul de notă «^1)» (626) și notele editoriale"
    if vechi.count(litera) != 1 or vechi.count(comentariu) != 1:
        raise ValueError("Textul 626 ori comentariul de pe P diferă")
    nou = vechi.replace(litera, '"626": "' + corectie["nou"] + '"').replace(comentariu, "litera k¹) se păstrează la 626, iar notele editoriale")
    delta = "".join(difflib.unified_diff(vechi.splitlines(True), nou.splitlines(True), "a/core/d110.py", "b/core/d110.py"))
    fisiere = {"produs_din_Q.patch": produs, "corectie_626.patch": delta.encode()}
    inventar = []
    for cale in cai:
        original = git("show", P + ":" + cale)
        final = nou.encode() if cale == "core/d110.py" else original
        inventar.append("\t".join((cale, hashlib.sha256(original).hexdigest(), hashlib.sha256(final).hexdigest())))
    fisiere["identitati_produs.tsv"] = ("cale\tsha_P\tsha_Q2\n" + "\n".join(inventar) + "\n").encode()
    a.director_nou.mkdir()
    for nume, continut in fisiere.items():
        (a.director_nou / nume).write_bytes(continut)
        print(hashlib.sha256(continut).hexdigest(), nume)


if __name__ == "__main__":
    main()
