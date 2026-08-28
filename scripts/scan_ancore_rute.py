# -*- coding: utf-8 -*-
"""Pentru cate rute e ORB PRIN CONSTRUCTIE detectorul de apelanti din R70.

DE UNDE VINE. Pe 27.08.2026 am mutat butonul de divergenta de denumire de pe
`PUT /tenants/{id}` pe `POST /tenants/{id}/nume-ales`. Ruta veche a ramas cu **zero** apelanti in
`static/` — masurat direct, cu anti-vacuu. Gardul R70, facut exact pentru clasa asta, **nu a
raportat-o**, si nu din neatentie: regula lui cauta bucatile literale ale caii (fara `/`), iar
singura bucata literala a rutei e `tenants` — care apare de 235 de ori in JS.

CE MASOARA. Pentru fiecare ruta, frecventa celei mai RARE ancore literale a ei in tot `static/`.
Daca si cea mai rara ancora apare de multe ori, ancora nu mai identifica ruta: detectorul va
raspunde INTOTDEAUNA „are apelant", indiferent de adevar.

CE NU MASOARA, si se scrie ca sa nu fie confundat: **nu spune care rute chiar n-au apelant.**
Spune doar despre care dintre ele detectorul nu poate afirma nimic. O ruta din lista poate fi
chemata de zece ecrane; ce lipseste e capacitatea de a afla.

Ruleaza: ./venv/bin/python scripts/scan_ancore_rute.py [--prag N]
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PRAG_IMPLICIT = 40


def bucati(cale):
    """Regula 4 a detectorului din R70: bucatile literale, fara `/`, fara parametri."""
    return [b for b in re.split(r"/", cale) if b and not b.startswith("{")]


def masoara(prag=PRAG_IMPLICIT):
    import core.test_ruta_fara_apelant as r70
    rute = r70._scan().citeste_rute()
    js = r70._static()
    # `_static()` intoarce un SIR. Prima versiune a masuratorii facea `"\n".join(js)` — adica
    # spargea sirul in caractere. Toate frecventele ieseau 0 si concluzia era „doar o ruta e
    # oarba", falsa si in directia comoda. A prins-o cazul cunoscut, nu recitirea.
    if not isinstance(js, str):
        js = "\n".join(js.values() if hasattr(js, "values") else js)
    orbi, vazute = [], []
    for r in rute:
        bs = bucati(r["cale"])
        if not bs:
            orbi.append((r["metoda"], r["cale"], 0, "nicio bucata literala"))
            continue
        rara = min(bs, key=js.count)
        f = js.count(rara)
        if f > prag:
            orbi.append((r["metoda"], r["cale"], f, rara))
        else:
            vazute.append((r["metoda"], r["cale"], f))
    return rute, js, orbi, vazute


# ─────────────────────────────────────────────────────────────────────────────
# [S1, 28.08.2026 — decizia (c) la R80] VERDICTUL, in patru stari, si de ce nu in doua.
#
# Pana azi masuratoarea spunea cate rute sunt oarbe, dar gardul care o consuma avea doua raspunsuri:
# „are apelant" si „n-are". Cele 51 de rute mute cadeau, prin constructie, in PRIMUL — fiindca
# ancora lor apare peste tot, deci `all(b in js ...)` e mereu adevarat. Adica orbirea se citea ca
# VERDE, tacut.
#
# Principiul, scris in DECIZII pe 15.07.2026: **gri nu se falsifica in verde.** Un „nu stiu" pus in
# aceeasi galeata cu un „da" nu e o simplificare, e o afirmatie falsa despre acoperire.
#
# CELE PATRU STARI, cu acelasi vocabular ca verificatorul (`ACCEPTAT / GRI / ROSU / EXCLUS`):
#   ACCEPTAT — ancora discrimineaza SI se gaseste in `static/`  -> ruta e chemata
#   ROSU     — ancora discrimineaza SI nu se gaseste            -> ruta nu e chemata de nimic
#   GRI      — ancora NU discrimineaza                          -> detectorul nu poate afirma nimic
#   EXCLUS   — ruta isi declara in cod lipsa ecranului, sau e un artefact cunoscut al detectorului
#
# ORDINEA CONTEAZA: EXCLUS se decide inaintea lui GRI, fiindca o ruta declarata ramane declarata
# indiferent daca detectorul ar fi putut-o vedea. GRI se decide inaintea lui ACCEPTAT — asta e chiar
# reparatia: o ruta despre care nu se poate afirma nimic nu are voie sa cada in verde.
STARI = ("ACCEPTAT", "GRI", "ROSU", "EXCLUS")


def verdicte(prag=PRAG_IMPLICIT):
    """{(metoda, cale): stare} — cate un verdict pentru FIECARE ruta, fara rest."""
    import core.test_ruta_fara_apelant as r70
    rute, js, orbi, _vazute = masoara(prag)
    oarbe = {(m, c) for m, c, _f, _a in orbi}
    acceptate = r70.acceptate()
    out = {}
    for r in rute:
        cheie = (r["metoda"], r["cale"])
        bs = r70.bucati(r["cale"])
        if cheie in acceptate:
            out[cheie] = "EXCLUS"
        elif cheie in oarbe or not bs:
            out[cheie] = "GRI"
        elif all(b in js for b in bs):
            out[cheie] = "ACCEPTAT"
        else:
            out[cheie] = "ROSU"
    return out


def rezumat(prag=PRAG_IMPLICIT):
    """(total, {stare: n}) — forma in care il citesc verificatorul si raportul portii."""
    v = verdicte(prag)
    return len(v), {s: sum(1 for x in v.values() if x == s) for s in STARI}


def main():
    prag = PRAG_IMPLICIT
    if "--prag" in sys.argv:
        prag = int(sys.argv[sys.argv.index("--prag") + 1])
    rute, js, orbi, vazute = masoara(prag)
    print("rute: %d · JS citit: %d caractere · prag: %d aparitii"
          % (len(rute), len(js), prag))
    print()
    print("ORBI PRIN CONSTRUCTIE: %d din %d" % (len(orbi), len(rute)))
    for metoda, cale, f, rara in sorted(orbi, key=lambda x: (x[1], x[0])):
        print("   %-7s %-46s ancora %r x%d" % (metoda, cale, rara, f))
    print()
    total, r = rezumat(prag)
    print("VERDICT: %d rute = ACCEPTAT %d + GRI %d + ROSU %d + EXCLUS %d"
          % (total, r["ACCEPTAT"], r["GRI"], r["ROSU"], r["EXCLUS"]))
    print("         GRI = detectorul nu poate afirma nimic. NU e verde.")
    print()
    print("[anti-vacuu] rute cu ancora discriminanta: %d" % len(vazute))
    print("[anti-vacuu] `tenants` in JS: %d aparitii" % js.count("tenants"))


if __name__ == "__main__":
    main()
