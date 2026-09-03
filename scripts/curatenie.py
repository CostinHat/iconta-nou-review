# -*- coding: utf-8 -*-
"""scripts/curatenie.py — CE E UN COMMIT DE CURATENIE, derivat din INDEX, nu declarat.

**Regula pe care o executa** (`PLAN_LUCRU.md`, regula 7 de conducere a lucrului, Costin 03.09.2026):

  > *„Operatiunile de curatenie — stergeri de fisiere, `.gitignore`, mutari — nu ruleaza teste
  > deloc. Nu exista cale prin care ele sa strice o declaratie."*

  > *„Conditie: eticheta e ignorata daca commitul atinge vreun fisier executabil sau vreun registru.
  > Se aplica doar la stergeri, `.gitignore` si mutari. Altfel devine cheia care deschide tot."*

**DE CE DECIDE INDEXUL, SI NU ETICHETA — nu e o alegere de stil, e ordinea hook-urilor.**
La `pre-commit`, mesajul commitului **inca nu exista**: cu `git commit -F`, `.git/COMMIT_EDITMSG`
poarta mesajul commitului **PRECEDENT** — dovedit pe 23.08.2026, scris in chiar antetul lui
`scripts/githooks/pre-commit`. Deci poarta nu POATE fi sarita de o eticheta; singurul lucru pe care
il vede e **ce e in index**. Eticheta `# doar-curatenie:` ramane obligatorie, dar rolul ei e altul,
si il verifica `commit-msg`: **marturia scrisa** ca poarta a fost sarita, si de ce. *O poarta sarita
in tacere n-ar lasa nicio urma in istorie.* Efectul cerut de conditie e insa exact cel scris: pe un
commit care atinge un executabil sau un registru, eticheta nu deschide nimic.

**CELE TREI CONDITII, toate obligatorii.** Prima e de FORMA, a doua de CLASA, a treia de REFERINTA.

1. **Forma.** Fiecare intrare din index e ori o **stergere** (`D`), ori o **mutare pura**
   (`R100` — similaritate 100%; una cu continut schimbat apare ca `D`+`A` si cade aici), ori o
   **modificare de `.gitignore`**. Orice adaugare, orice alta modificare, orice schimbare de tip:
   nu e curatenie.

2. **Clasa.** Nicio cale atinsa (nici cea veche, nici cea noua) nu e **executabil** sau **registru**.
   Amandoua definitiile sunt **imprumutate de la `scripts/perimetru.py`**, nu rescrise:
   `EXT_EXECUTABILE` = `.py`, `.js` (*„Costin le-a numit explicit; nu se deduc si nu se largesc
   tacit"*), iar registru = `.md` din **radacina** repo-ului plus cele doua JSON-uri de provenienta.
   *A doua definitie a aceluiasi lucru ar fi inceputul unei divergente tacute:* daca maine un
   registru nou intra in `perimetru.py`, intra si aici, in acelasi moment.

3. **Referinta.** Niciun nume sters sau mutat nu e **numit in ce se comite**. Asta acopera gaura pe
   care primele doua o lasa deschisa: un `.xsd`, o fixtura `.json` sau o captura sunt, dupa clasa,
   „curatenie" — dar daca un test le deschide, stergerea lor e o **modificare de cod prin absenta**,
   iar suita ar cadea la urmatorul commit, pe capul altcuiva. Cautarea se face cu
   `git grep --cached -F`, peste continutul care intra in commit.

**CE NU FACE, declarat.**
  * Nu judeca daca stergerea e o idee buna — spune doar daca poate strica ceva mecanic.
  * Cautarea de referinta e pe **sir**, nu pe structura: un nume care apare intr-un comentariu, sau
    un nume scurt care e sub-sir in altul (`a.txt` in `data.txt`), produce un **refuz**. Greseala e
    deliberat pusa in directia asta: un refuz costa 22 de minute de poarta completa, o trecere
    gresita costa o suita rosie in bratele urmatorului.
  * Nu vede un nume construit din bucati (`"cap" + "turi.png"`). N-am intalnit niciunul; cand apare,
    scapa in tacere — de-aia conditia 3 e a treia, nu singura.
  * Un `.md` **din afara radacinii** nu e registru prin definitia lui `perimetru.py`, deci stergerea
    lui trece de conditia 2. Trece de 3 numai daca nu-l numeste nimic.

**FAIL CLOSED.** Orice esec — git care nu raspunde, index necitibil, cautare care crapa — inseamna
**nu e curatenie**, deci poarta completa. Un instrument de scurtat care greseste spre „da" nu e un
instrument, e o portita.

Folosire:
    ./venv/bin/python scripts/curatenie.py           # verdict citibil; iese 0 daca E curatenie
    ./venv/bin/python scripts/curatenie.py --tacut   # doar codul de iesire (pentru hook-uri)
"""
import os
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from scripts import perimetru as P  # noqa: E402

#: Aceeasi definitie ca in `perimetru.py`, prin REFERINTA — nu o copie. Vezi conditia 2 din antet.
EXT_EXECUTABILE = P.EXT_EXECUTABILE

#: Singurul fisier care poate fi MODIFICAT intr-un commit de curatenie.
IGNORE = ".gitignore"


def registre():
    """Registrele, imprumutate de la `perimetru.py`: `.md` din radacina + cele doua JSON-uri de
    provenienta, plus numele lor de baza. Un registru nou intra singur, in amandoua instrumentele."""
    return P._documente_urmarite()


def intrari_stagiate():
    """`[(stare, cale_veche, cale_noua)]` din index, sau `None` daca git n-a raspuns.

    `--find-renames=100%`: numai mutarile IDENTICE se raporteaza ca `R100`. O mutare cu continut
    schimbat se descompune in `D`+`A`, iar `A` cade la conditia de forma — exact ce trebuie, fiindca
    acolo s-a schimbat cod, nu s-a mutat un fisier."""
    try:
        r = subprocess.run(["git", "diff", "--cached", "--name-status", "--find-renames=100%"],
                           cwd=RAD, capture_output=True, text=True, timeout=60)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    out = []
    for linie in r.stdout.splitlines():
        campuri = linie.rstrip("\n").split("\t")
        if not campuri or not campuri[0].strip():
            continue
        stare = campuri[0].strip()
        vechi = campuri[1].strip() if len(campuri) > 1 else ""
        nou = campuri[2].strip() if len(campuri) > 2 else ""
        out.append((stare, vechi, nou))
    return out


def numite_in_arbore(cai):
    """Care dintre NUMELE date apar, ca sir, in continutul care se comite (`git grep --cached`).

    Se cauta pe numele de baza, nu pe calea intreaga: o garda scrie de obicei
    `os.path.join(DIR, "x.json")`, deci calea completa n-ar aparea nicaieri. Ridica `RuntimeError`
    daca git raspunde altfel decat „am gasit" / „n-am gasit" — apelantul trateaza asta ca refuz."""
    nume = sorted({os.path.basename(c) for c in cai if c})
    if not nume:
        return set()
    cmd = ["git", "grep", "--cached", "-F", "-I", "-h", "-o"]
    for n in nume:
        cmd += ["-e", n]
    r = subprocess.run(cmd, cwd=RAD, capture_output=True, text=True, timeout=120)
    if r.returncode not in (0, 1):          # 0 = gasit, 1 = negasit; restul = eroare
        raise RuntimeError("git grep a iesit cu %d: %s" % (r.returncode, r.stderr.strip()[:200]))
    gasite = {x.strip() for x in r.stdout.splitlines() if x.strip()}
    return gasite & set(nume)


def clasifica(intrari, reg, numite):
    """MOTIVELE pentru care commitul NU e curatenie. Lista goala = e curatenie.

    Se intorc motive, nu un `False`: un refuz fara motiv scris devine, la a treia oara, o
    superstitie — acelasi principiu ca `--motiv-incert` din `perimetru.py`."""
    if intrari is None:
        return ["git n-a putut citi indexul — poarta ramane cea completa"]
    if not intrari:
        return ["indexul e gol — nu e nimic de comis, deci nimic de sarit"]
    motive = []
    for stare, vechi, nou in intrari:
        if stare == "D":
            cai = [vechi]
        elif stare == "R100":
            cai = [vechi, nou]
        elif stare == "M" and os.path.basename(vechi) == IGNORE:
            cai = []
        else:
            motive.append("%s %s — nu e nici stergere, nici mutare pura (R100), nici %s"
                          % (stare, nou or vechi, IGNORE))
            continue
        for c in cai:
            if c.endswith(EXT_EXECUTABILE):
                motive.append("%s — fisier EXECUTABIL (%s)" % (c, "/".join(EXT_EXECUTABILE)))
            if c in reg or os.path.basename(c) in reg:
                motive.append("%s — REGISTRU (.md din radacina, sau provenienta)" % c)
            if os.path.basename(c) in numite:
                motive.append("%s — e NUMIT in ce se comite: ceva il citeste, deci stergerea lui "
                              "e o modificare prin absenta" % c)
    return motive


def verdict():
    """`(e_curatenie, motive, intrari)`. Fail closed: orice esec da `False` cu motivul scris."""
    intrari = intrari_stagiate()
    if not intrari:
        return False, clasifica(intrari, set(), set()), intrari or []
    cai = [v for (_s, v, _n) in intrari] + [n for (_s, _v, n) in intrari if n]
    try:
        numite = numite_in_arbore(cai)
    except Exception as e:
        return False, ["cautarea referintelor n-a putut fi facuta (%s) — poarta ramane cea "
                       "completa" % e], intrari
    motive = clasifica(intrari, registre(), numite)
    return (not motive), motive, intrari


def main(argv):
    tacut = "--tacut" in argv
    e_curatenie, motive, intrari = verdict()
    if tacut:
        return 0 if e_curatenie else 2
    print("INDEX (%d intrari):" % len(intrari))
    for stare, vechi, nou in intrari[:20]:
        print("    %-5s %s%s" % (stare, vechi, (" -> " + nou) if nou else ""))
    if len(intrari) > 20:
        print("    ... si inca %d" % (len(intrari) - 20))
    if e_curatenie:
        print("\nCOMMIT NUMAI DE CURATENIE — stergeri / mutari pure / %s, fara executabile, fara "
              "registre, si nimic din ce se sterge nu e numit in ce se comite." % IGNORE)
        return 0
    print("\nNU E CURATENIE — poarta completa. Motive:")
    for m in motive:
        print("   -", m)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
