# -*- coding: utf-8 -*-
"""SECȚIUNEA B a raportului („UNDE SUNTEM"), DERIVATĂ din `CONFORMITATE.md`.

  scripts/raport_b.py

De ce nu se scrie de mână (Costin, 22.08.2026): *„dacă B s-ar scrie separat, ar deveni al doilea loc
unde trăiește aceeași stare — și s-ar învechi, exact clasa pe care o închidem."* Antetul e sursa;
raportul îl reproduce. Dacă cele două diverg, antetul are dreptate.

Ce se CITEȘTE din antet: etapa, pasul, criteriul, ce lipsește, deciziile, avertismentul.
Ce se NUMĂRĂ sau se DERIVĂ, la fiecare rulare: stările celor 75 de interdicții · cel mai vechi commit
dintre cifre · restanțele, cu **contorul lor derivat din git** — câte commituri au atins registrul de când
s-a deschis restanța. **Numără commituri, nu ture**: o tură poate produce mai multe, deci contorul
urcă mai repede decât ziua; e ce poate da git fără să inventez o noțiune de „tură". Un contor scris de mână ar fi exact defectul pe care restanțele îl
măsoară, mutat cu un rând mai jos.
"""
import os
import re
import subprocess

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF = os.path.join(RAD, "CONFORMITATE.md")
STARI = ("MĂSURATĂ", "PARȚIAL", "NEMĂSURABILĂ", "NEÎNCEPUTĂ")
FELURI = ("SURSĂ", "VERIFICARE", "ARTEFACT", "ORDINE")


def _camp(corp, nume):
    m = re.search(r"^[ \t]*[-*]?[ \t]*\*\*%s\*\*[ \t]*:[ \t]*(.*)$" % re.escape(nume),
                  corp, re.M | re.I)
    return None if m is None else m.group(1).strip()


def _git(*a):
    return subprocess.run(["git", "-C", RAD] + list(a), capture_output=True, text=True)


def _antet(t):
    m = re.search(r"^## ANTET DE ETAPĂ[ \t]*$(.*?)^---[ \t]*$", t, re.M | re.S)
    return None if m is None else m.group(1)


def _sectiuni(t):
    buc = re.split(r"^## (\d+)\s*[—-]\s*(.+)$", t, flags=re.M)
    return {int(buc[k]): buc[k + 2] for k in range(1, len(buc), 3)}


def _restante(t):
    m = re.search(r"^## RESTANȚE[ \t]*$(.*?)^## ", t, re.M | re.S)
    if m is None:
        return {}
    buc = re.split(r"^### (R\d+)\s*[—-]\s*(.+)$", m.group(1), flags=re.M)
    return {buc[k]: (buc[k + 1].strip(), buc[k + 2]) for k in range(1, len(buc), 3)}


def _contor(h):
    """Câte commituri au atins CONFORMITATE.md de când s-a deschis restanța. Derivat, nu scris."""
    r = _git("rev-list", "--count", "%s..HEAD" % h, "--", "CONFORMITATE.md")
    return int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def _locuri():
    """Cate locuri de verificare sunt scrise si cate mai sunt goale — NUMARAT, nu citit din proza.

    A stat deja o data in antet („192 goale" dupa ce 30 fusesera scrise), iar garda
    `test_pasul_curent_nu_devine_naratiune` a spus reparatia: o propozitie confruntabila cu o
    cifra apartine derivatorului. Daca fisierul lipseste, se SPUNE — nu se raporteaza zero."""
    import os as _os
    cale = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                         "TRASEE_VERIFICARI.md")
    if not _os.path.isfile(cale):
        return "TRASEE_VERIFICARI.md lipseste — nu se poate număra"
    d = open(cale, encoding="utf-8").read()
    scrise = sum(1 for l in d.splitlines() if l.startswith("- [x] "))
    # [29.08.2026] O casuta NEBIFATA e un loc nefacut — si cu text, si fara. Prima forma numara
    # gol numai randul `- [ ]` PUR, deci un rand `- [ ] <propozitie>` (o verificare scrisa, dar
    # neexercitata) nu intra nici la scrise, nici la goale: DISPAREA din numitor, iar procentul
    # sarea inapoi la „100%" peste locuri nefacute. Exact clasa pentru care exista functia asta.
    goale = sum(1 for l in d.splitlines()
                if l.rstrip() == "- [ ]" or l.startswith("- [ ] "))
    tot = scrise + goale
    if not tot:
        return "0 locuri — fisierul s-a golit?"
    return "**%d scrise / %d goale** din %d (%d%%)" % (scrise, goale, tot, round(100 * scrise / tot))


def main():
    with open(CONF, encoding="utf-8") as f:
        t = f.read()
    a = _antet(t)
    if a is None:
        raise SystemExit("CONFORMITATE.md n-are antet de etapă — secțiunea B n-are sursă")
    sec = _sectiuni(t)

    nr = {s: 0 for s in STARI}
    alta = 0
    for _n, corp in sec.items():
        v = (_camp(corp, "stare") or "").strip("*").split("—")[0].split("(")[0].split(",")[0].strip()
        if v in nr:
            nr[v] += 1
        else:
            alta += 1

    hashuri = []
    for n, corp in sec.items():
        h = (_camp(corp, "pe commit") or "—").strip("`*— ")
        if h:
            r = _git("log", "-1", "--format=%ct %h %cs", h)
            if r.returncode == 0 and r.stdout.strip():
                p = r.stdout.split()
                hashuri.append((int(p[0]), p[1], p[2], n))
    hashuri.sort()

    print("## B. UNDE SUNTEM")
    print()
    print("*Derivat din `CONFORMITATE.md` cu `scripts/raport_b.py` — nu scris de mână.*")
    print()
    print("- **etapa**: %s" % (_camp(a, "etapa") or "?"))
    print("- **pasul curent**: %s" % (_camp(a, "pasul curent") or "?"))
    print("- **locuri de verificare**: %s" % _locuri())
    print("- **criteriul de terminare**: %s" % (_camp(a, "criteriul de terminare") or "?"))
    print("- **ce mai lipsește**: %s" % (_camp(a, "ce lipsește") or "?"))
    print("- **interdicții, din %d**: MĂSURATE %d · PARȚIAL %d · NEMĂSURABILE %d · NEÎNCEPUTE %d%s"
          % (len(sec), nr["MĂSURATĂ"], nr["PARȚIAL"], nr["NEMĂSURABILĂ"], nr["NEÎNCEPUTĂ"],
             (" · alte stări %d" % alta) if alta else ""))
    av = _camp(a, "avertisment la cifre")
    if av:
        print("  - ⚠ %s" % av)
    if hashuri:
        _ct, h, zi, n = hashuri[0]
        print("- **cel mai vechi commit din registru**: `%s` (%s), de la secțiunea #%d" % (h, zi, n))
    else:
        print("- **cel mai vechi commit din registru**: — (nicio cifră ancorată)")
    print("- **decizii care blochează**: %s" % (_camp(a, "decizii care blochează") or "?"))

    # ── restanțele
    rest = _restante(t)
    deschise, rezolvate, vechi = {f: [] for f in FELURI}, [], []
    for cod, (titlu, corp) in sorted(rest.items()):
        st = (_camp(corp, "stare") or "").strip("* ").split("(")[0].strip()
        fel = (_camp(corp, "felul") or "?").strip("* ")
        h = (_camp(corp, "deschisă pe commit") or "").strip("`*— ")
        c = _contor(h) if h else None
        et = "%s — %s" % (cod, titlu)
        if st == "REZOLVATĂ":
            rezolvate.append(et)
            continue
        deschise.get(fel, deschise.setdefault(fel, [])).append(
            "%s (contor %s)" % (et, "?" if c is None else c))
        if c is not None and c > 1:
            vechi.append("%s — %d commituri pe registru" % (cod, c))

    total = sum(len(v) for v in deschise.values())
    et = re.match(r"\*{0,2}(E[1-5])", (_camp(a, "etapa") or "").strip())
    et = et.group(1) if et else None
    ale_etapei = [c for c, (_t, corp) in rest.items()
                  if "DESCHISĂ" in (_camp(corp, "stare") or "")
                  and et and re.search(r"\b%s\b" % et, _camp(corp, "unde intră") or "")]
    print("- **restanțe DESCHISE: %d** (din care ale etapei %s: **%d**)"
          % (total, et or "?", len(ale_etapei)))
    for f in FELURI:
        if deschise.get(f):
            print("  - **%s**: %s" % (f, " · ".join(deschise[f])))
    for f in sorted(set(deschise) - set(FELURI)):
        if deschise[f]:
            print("  - **%s (fel nedeclarat!)**: %s" % (f, " · ".join(deschise[f])))
    if vechi:
        print("  - ⚠ **a supraviețuit unei ture**: %s" % " · ".join(vechi))
    else:
        print("  - niciuna n-a trecut de un commit pe registru (contor ≤ 1)")
    if rezolvate:
        print("- **restanțe REZOLVATE**: %s" % " · ".join(rezolvate))

    print("- **antetul, actualizat la**: %s" % (_camp(a, "ultima actualizare") or "?"))


if __name__ == "__main__":
    main()
