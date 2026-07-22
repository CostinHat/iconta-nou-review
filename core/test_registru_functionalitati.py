# -*- coding: utf-8 -*-
"""Garda de integritate a FUNCTIONALITATI.csv (registrul canonic al functionalitatilor).

DE CE E TEST, NU verificator_conformitate.py (DECIZII 22.07): verificatorul iese mereu 0
(raportor de nits DS, nu gate); suita e verde-obligatoriu -> un rand malformat RUPE suita
INAINTE de commit. Integritatea structurii registrului e un INVARIANT, nu o conventie de stil.

DE CE CONTEAZA: core/raportari_ai.py (F152) citeste registrul ca baza de cunostinte a AI-ului
care raspunde clientilor. Filtreaza pe r[7].startswith("LIVE") si scoate r[0]/r[1]/r[4]. Un rand
malformat (ex. virgula neescapata intr-un camp -> campuri decalate) face ca r[7] sa nu mai fie
Starea reala -> functionalitatea devine INVIZIBILA pentru AI (dovada: F183, 22.07 - Acces UI
neescapat spargea randul, F183 nu aparea ca LIVE).

Citim cu csv.reader (NU split pe virgula) exact ca raportari_ai.py, ca sa validam ce vede EL.
Doua checkuri, ambele zero-mentenanta si zero fals-pozitive:
  1. fiecare rand are exact len(header) campuri  (checkul de aur - prinde clasa F183);
  2. ID (coloana 2) = F\\d+                        (prinde decalaje care totalizeaza fortuit N).
NU validam vocabularul de Stare (coloana 7): cupleaza la o lista extensibila -> o stare noua
legitima ar da rosu fals; nu normalizam un rosu fragil (lectia 22.07)."""
import csv
import pathlib
import re

_CALE = pathlib.Path(__file__).resolve().parent.parent / "FUNCTIONALITATI.csv"


def _randuri():
    """Toate randurile, citite exact ca raportari_ai.py (csv.reader, utf-8-sig)."""
    with open(_CALE, encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def test_fiecare_rand_are_numarul_corect_de_campuri():
    randuri = _randuri()
    n = len(randuri[0])  # header = numarul canonic de coloane
    rele = [(i + 1, len(r)) for i, r in enumerate(randuri) if len(r) != n]
    assert not rele, (
        "FUNCTIONALITATI.csv: randuri cu numar gresit de campuri (asteptat %d, dupa header):\n"
        % n
        + "\n".join("  linia %d: %d campuri" % (linia, nr) for linia, nr in rele)
        + "\n-> registrul e baza de cunostinte F152 (raportari_ai.py): un rand decalat face "
          "functionalitatea INVIZIBILA pentru AI (Starea nu mai e pe coloana 7). Cauza tipica: "
          "virgula neescapata intr-un camp descriptiv -> pune campul intre ghilimele."
    )


def test_fiecare_id_este_valid():
    randuri = _randuri()
    idx_id = randuri[0].index("ID")
    rele = [(i + 1, r[idx_id]) for i, r in enumerate(randuri[1:], start=1)
            if not re.fullmatch(r"F\d+", (r[idx_id] or "").strip())]
    assert not rele, (
        "FUNCTIONALITATI.csv: ID-uri ne-conforme pe coloana %d (asteptat F<numar>):\n" % idx_id
        + "\n".join("  linia %d: ID=%r" % (linia, val) for linia, val in rele)
        + "\n-> un ID care nu e F\\d+ semnaleaza un rand decalat care totalizeaza fortuit "
          "numarul corect de campuri (checkul de numar-campuri nu l-ar prinde)."
    )
