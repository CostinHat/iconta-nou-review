# -*- coding: utf-8 -*-
"""scripts/publica_static.py — CE SE SERVESTE nu mai e CE E IN LUCRU. (R118)

**DEFECTUL, si de ce a devenit incident.** Serviciul ruleaza cu `WorkingDirectory` in arborele de
lucru, iar `/static` se monta direct de acolo. Un `.js` scris pe server era **live in aceeasi
secunda** — fara commit, fara poarta, fara restart. *Poarta verde apara Python-ul, fiindca procesul
il incarca la pornire; JS-ul nu trecea prin ea deloc.* Instanta masurata (01.09.2026): o ghilimea
romaneasca inchisa cu `"` ASCII in `supervizor.js` a oprit **tot desktopul** — 15 ecrane —, fiindca
`cabinet.js` importa modulul. Pe productie, pe fisierul viu.

**CE FACE INSTRUMENTUL ASTA.** Materializeaza `static/` intr-un director **din afara arborelui de
lucru** (`../iconta_publicat/static`), pe care il serveste aplicatia. Sursa e, implicit, **HEAD** —
deci publicarea JS trece obligatoriu prin commit, adica prin poarta.

**POARTA DE SINTAXA, pe amandoua caile.** Inainte de a inlocui ce se serveste, fiecare `.js` trece
prin `node --check`. Asa, nici macar publicarea DELIBERATA din arbore nu poate duce la un browser un
modul care nu se parseaza. *Condiția lui R118 cerea „fie una, fie alta"; costa doua zeci de linii sa
fie amandoua, iar clasa merita.*

**CALEA DE DEZVOLTARE nu dispare, devine un ACT.** `--din-arbore` publica arborele de lucru, cu
motivul scris in amprenta. Diferenta fata de inainte nu e ca se poate sau nu — e ca **se vede**:
`.publicat.json` spune din ce s-a publicat, de pe ce commit si cand. *Inainte, „ce se serveste" nu
era o intrebare care sa aiba raspuns.*

**`raportari/` NU se atinge.** Aplicatia scrie acolo, la rulare, imaginile rapoartelor
(`main.py`, `_STATIC_DIR/raportari`). Sunt artefacte de RULARE, nu cod: publicarea le **protejeaza**
de stergere (`rsync --filter='P raportari/***'`), altfel fiecare publicare ar sterge rapoartele
generate intre timp.

Folosire:
    ./venv/bin/python scripts/publica_static.py              # din HEAD (calea din post-commit)
    ./venv/bin/python scripts/publica_static.py --din-arbore # din arborele de lucru, DELIBERAT
    ./venv/bin/python scripts/publica_static.py --stare      # ce se serveste acum
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Directorul SERVIT. Deliberat **in afara** arborelui de lucru: daca ar fi inauntru, un `git clean`
#: sau o editare gresita l-ar putea atinge, iar separarea ar fi doar de nume.
PUBLICAT = os.path.join(os.path.dirname(RAD), "iconta_publicat", "static")

#: Amprenta publicarii. Fara ea, „ce se serveste" ramane o intrebare fara raspuns — iar `main.py`
#: REFUZA sa porneasca pe un director publicat fara amprenta citibila (o publicare intrerupta la
#: jumatate nu are voie sa fie servita ca si cum ar fi intreaga).
AMPRENTA = ".publicat.json"

#: Ce nu se sterge niciodata la publicare: artefactele scrise de aplicatie la RULARE.
PROTEJATE = ("raportari",)


def _ruleaza(cmd, **kw):
    return subprocess.run(cmd, cwd=RAD, capture_output=True, text=True, timeout=300, **kw)


def verifica_js(radacina):
    """Fiecare `.js` trebuie sa se parseze. Intoarce lista de (cale, mesaj) pentru cele care nu.

    `node --check` cere extensia `.mjs` pentru module ES (ce folosim peste tot), deci fisierul se
    copiaza intr-un temporar cu extensia aia. *Verificarea e pe SINTAXA, nu pe comportament: nu
    inlocuieste poarta vizuala, o precede.*"""
    rele = []
    for dirpath, _d, fisiere in os.walk(radacina):
        for f in sorted(fisiere):
            if not f.endswith(".js"):
                continue
            cale = os.path.join(dirpath, f)
            with tempfile.NamedTemporaryFile(suffix=".mjs", delete=False) as t:
                t.write(io.open(cale, "rb").read())
                tmp = t.name
            try:
                r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True,
                                   timeout=60)
                if r.returncode != 0:
                    rel = os.path.relpath(cale, radacina)
                    prima = (r.stderr or "").strip().splitlines()
                    rele.append((rel, prima[-1] if prima else "node --check a esuat"))
            finally:
                os.unlink(tmp)
    return rele


def _materializeaza(din_arbore, dest):
    """Scrie in `dest` continutul lui `static/`, din HEAD sau din arborele de lucru."""
    if din_arbore:
        shutil.copytree(os.path.join(RAD, "static"), dest)
        return {"sursa": "arbore de lucru", "commit": None}
    r = _ruleaza(["git", "rev-parse", "HEAD"])
    if r.returncode != 0:
        raise SystemExit("nu pot citi HEAD: %s" % (r.stderr or "").strip())
    commit = r.stdout.strip()
    os.makedirs(dest, exist_ok=True)
    # `git archive` scoate ARBORELE COMMITULUI, nu ce e pe disc — asta e chiar separarea ceruta.
    arh = subprocess.run(["git", "archive", "--format=tar", commit, "static"],
                         cwd=RAD, stdout=subprocess.PIPE, timeout=300)
    if arh.returncode != 0:
        raise SystemExit("git archive a esuat pentru %s" % commit[:8])
    parinte = os.path.dirname(dest)
    tar = subprocess.run(["tar", "-x", "-C", parinte], input=arh.stdout, timeout=300)
    if tar.returncode != 0:
        raise SystemExit("dezarhivarea a esuat")
    return {"sursa": "commit", "commit": commit}


def stare():
    """Ce se serveste acum: dictul din amprenta, sau `None` daca nu s-a publicat niciodata."""
    cale = os.path.join(PUBLICAT, AMPRENTA)
    if not os.path.isfile(cale):
        return None
    try:
        return json.loads(io.open(cale, encoding="utf-8").read())
    except Exception as e:
        return {"sursa": "AMPRENTA ILIZIBILA", "eroare": str(e)}


def publica(din_arbore=False, acum=None):
    """Publica, cu poarta de sintaxa. Intoarce amprenta scrisa. Ridica daca vreun `.js` nu se parseaza.

    `acum` se INJECTEAZA (nu se ia din ceas) ca o proba sa poata verifica amprenta fara sa depinda
    de momentul rularii. Fara injectie, singura aserttiune posibila ar fi „exista o data", care nu
    spune nimic."""
    tmp = tempfile.mkdtemp(prefix="iconta_publicare_")
    try:
        dest = os.path.join(tmp, "static")
        info = _materializeaza(din_arbore, dest)
        rele = verifica_js(dest)
        if rele:
            raise SystemExit(
                "PUBLICARE REFUZATA: %d fisier(e) .js nu se parseaza. Ce se serveste NU s-a atins.\n"
                % len(rele) + "\n".join("  %s: %s" % x for x in rele))
        if acum is None:
            import datetime
            acum = datetime.datetime.now().isoformat(timespec="seconds")
        info["la"] = acum
        info["fisiere"] = sum(len(f) for _d, _s, f in os.walk(dest))
        io.open(os.path.join(dest, AMPRENTA), "w", encoding="utf-8").write(
            json.dumps(info, ensure_ascii=False, indent=2) + "\n")

        os.makedirs(PUBLICAT, exist_ok=True)
        # `P` = protect: rsync COPIAZA in continuare ce vine, dar nu STERGE ce e protejat pe
        # destinatie. Fara filtrul asta, fiecare publicare ar sterge rapoartele generate intre timp.
        filtre = ["--filter=P %s/***" % p for p in PROTEJATE]
        r = subprocess.run(["rsync", "-a", "--delete"] + filtre + [dest + "/", PUBLICAT + "/"],
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise SystemExit("rsync a esuat: %s" % (r.stderr or "").strip())
        return info
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if "--stare" in argv:
        s = stare()
        print("SERVIT DIN:", PUBLICAT)
        print(json.dumps(s, ensure_ascii=False, indent=2) if s else "  (nepublicat inca)")
        return 0
    info = publica(din_arbore="--din-arbore" in argv)
    print("publicat in %s <- %s%s (%d fisiere)"
          % (PUBLICAT, info["sursa"],
             (" " + (info["commit"] or "")[:8]) if info.get("commit") else "", info["fisiere"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
