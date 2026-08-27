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
    print("[anti-vacuu] rute cu ancora discriminanta: %d" % len(vazute))
    print("[anti-vacuu] `tenants` in JS: %d aparitii" % js.count("tenants"))


if __name__ == "__main__":
    main()
