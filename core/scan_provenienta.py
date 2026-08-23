# -*- coding: utf-8 -*-
"""core/scan_provenienta.py — de unde vine fiecare fisier din corpus. (23.08.2026)

DE CE EXISTA. Interdictia 52 masura „cate acte s-au schimbat dupa aducere" si raspundea
0 din 177 de perechi amprenta/fisier - dar pe disc erau 339 de acte, deci raspunsul era
despre jumatate. Prima reactie a fost „se amprenteaza si restul, e mecanic". Masurand
INAINTE de a amprenta, s-a vazut ca amprentarea oarba ar fi fost gresita in doua feluri:

  1. Cele mai multe fisiere fara amprenta sunt TEXT DERIVAT dintr-un pdf/html/xsd care
     ARE amprenta. A le amprenta separat nu adauga nimic despre act - sursa e deja pinata.
  2. O parte sunt NOTE SCRISE DE NOI (cercetare, istoric de cote). O amprenta pe ele
     raspunde la „nu l-am editat", pe care git il raspunde deja - NU la „actul s-a
     schimbat sub noi", care e intrebarea interdictiei. Ar fi fost o cifra care creste
     fara ca acoperirea reala sa creasca.

Deci intrebarea nu e „are amprenta?", ci „ce e fisierul asta?". Clasa se stabileste
MECANIC unde se poate, si DECLARAT in `anaf_surse/PROVENIENTA.json` unde nu.

CE FACE IMPOSIBIL: un fisier in corpus fara clasa · un fisier declarat ADUS fara
amprenta · un artefact GOL nou, care arata ca un act prezent si tacut · o declaratie
pentru un fisier care nu mai exista.

CE NU VEDE: nu verifica daca textul DECLARAT ca adus chiar coincide cu sursa - pentru
asta ar trebui re-descarcat (limita mostenita de la 52). Nu deosebeste o nota scrisa
corect de una scrisa gresit. Clasa DERIVAT se stabileste dupa NUME (acelasi trunchi),
nu dupa continut: un `x.txt` care nu provine din `x.pdf` ar fi clasat gresit. Iar clasa
declarata e o AFIRMATIE DE OM: instrumentul verifica doar ca e scrisa si consecventa cu
faptele mecanice, nu ca e adevarata.
"""
import hashlib
import io
import json
import os

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(RADACINA, "anaf_surse")
NUME_DECLARATII = "PROVENIENTA.json"

EXTENSII = (".html", ".txt", ".pdf", ".xsd")
SURSE_POSIBILE = (".pdf", ".html", ".xsd", ".zip")
PRAG_GOL = 2  # un fisier de 1 octet e o linie goala, nu un act

AMPRENTAT = "AMPRENTAT"              # are .sha256 propriu
DERIVAT = "DERIVAT"                  # text extras dintr-un fisier de corpus amprentat
DERIVAT_NEPINAT = "DERIVAT_NEPINAT"  # extras dintr-unul care NU are amprenta
ADUS = "ADUS"
ADUS_ADNOTAT = "ADUS_ADNOTAT"
SCRIS = "SCRIS"
DERIVAT_MANUAL = "DERIVAT_MANUAL"
NEDECLARAT = "NEDECLARAT"

DECLARABILE = (ADUS, ADUS_ADNOTAT, SCRIS, DERIVAT_MANUAL)
CER_AMPRENTA = (ADUS, ADUS_ADNOTAT)


def _fisiere(corpus=None):
    c = corpus or CORPUS
    return [f for f in sorted(os.listdir(c))
            if f.lower().endswith(EXTENSII) and os.path.isfile(os.path.join(c, f))]


def declaratii(corpus=None):
    p = os.path.join(corpus or CORPUS, NUME_DECLARATII)
    if not os.path.exists(p):
        return {}
    return json.load(io.open(p, encoding="utf-8"))


def goale_cunoscute(corpus=None):
    return set(declaratii(corpus).get("goale_cunoscute", {}).get("lista", []))


def sursa_derivarii(fisier, corpus=None):
    """Fisierul de corpus din care pare extras `fisier`, sau None."""
    c = corpus or CORPUS
    baza, ext = os.path.splitext(fisier)
    if ext != ".txt":
        return None
    for e in SURSE_POSIBILE:
        if os.path.exists(os.path.join(c, baza + e)):
            return baza + e
    return None


def clasifica(corpus=None):
    """{fisier: (clasa, detaliu)} pentru tot corpusul."""
    c = corpus or CORPUS
    decl = declaratii(c).get("fisiere", {})
    out = {}
    for f in _fisiere(c):
        d = decl.get(f)
        if isinstance(d, dict) and d.get("clasa") in DECLARABILE:
            out[f] = (d["clasa"], d.get("motiv", ""))
            continue
        if os.path.exists(os.path.join(c, f + ".sha256")):
            out[f] = (AMPRENTAT, "amprenta proprie")
            continue
        s = sursa_derivarii(f, c)
        if s:
            pinat = os.path.exists(os.path.join(c, s + ".sha256"))
            out[f] = ((DERIVAT if pinat else DERIVAT_NEPINAT), "din %s" % s)
            continue
        out[f] = (NEDECLARAT, "nici amprenta, nici sursa pe disc, nici declaratie")
    return out


def goale(corpus=None):
    """[(fisier, octeti)] pentru artefactele care exista dar nu spun nimic."""
    c = corpus or CORPUS
    return [(f, os.path.getsize(os.path.join(c, f)))
            for f in _fisiere(c) if os.path.getsize(os.path.join(c, f)) <= PRAG_GOL]


def goale_noi(corpus=None):
    """Goale care NU sunt pe lista cunoscuta. Clichetul: una noua pica poarta."""
    cun = goale_cunoscute(corpus)
    return [(f, n) for f, n in goale(corpus) if f not in cun]


def adus_fara_amprenta(corpus=None):
    """Un act declarat ADUS fara amprenta e chiar gaura pe care 52 o masoara."""
    c = corpus or CORPUS
    return sorted(f for f, (cl, _) in clasifica(c).items()
                  if cl in CER_AMPRENTA and not os.path.exists(os.path.join(c, f + ".sha256")))


def declaratii_orfane(corpus=None):
    """Declaratii pentru fisiere care nu mai exista - apara o lume care a plecat."""
    c = corpus or CORPUS
    pe_disc = set(_fisiere(c))
    orf = [f for f in declaratii(c).get("fisiere", {}) if f not in pe_disc]
    orf += [f for f in goale_cunoscute(c) if f not in pe_disc]
    return sorted(set(orf))


def amprenta(cale):
    return hashlib.sha256(io.open(cale, "rb").read()).hexdigest()


def statistici(corpus=None):
    st = {}
    for _f, (c, _d) in clasifica(corpus).items():
        st[c] = st.get(c, 0) + 1
    st["TOTAL"] = sum(v for k, v in st.items())
    return st


if __name__ == "__main__":
    cl = clasifica()
    st = statistici()
    print("CORPUS: %d fisiere\n" % st["TOTAL"])
    for k in (AMPRENTAT, DERIVAT, DERIVAT_NEPINAT, ADUS, ADUS_ADNOTAT, SCRIS,
              DERIVAT_MANUAL, NEDECLARAT):
        print("  %-18s %d" % (k, st.get(k, 0)))
    print("\nADUS fara amprenta : %s" % (adus_fara_amprenta() or "niciunul"))
    print("declaratii orfane  : %s" % (declaratii_orfane() or "niciuna"))
    g, gn = goale(), goale_noi()
    print("goale              : %d (dintre care NOI, nedeclarate: %d)" % (len(g), len(gn)))
    for f, n in gn:
        print("   NOU  %-34s %d octeti" % (f, n))
    nd = sorted(f for f, (c, _) in cl.items() if c == NEDECLARAT)
    if nd:
        print("\nNEDECLARATE: %d" % len(nd))
        for f in nd:
            print("  " + f)
