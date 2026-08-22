# -*- coding: utf-8 -*-
"""core/registru_exceptii.py — ce NU e o afirmatie despre datele firmei, si de ce. (P8, 22.08.2026)

DE CE EXISTA (decis de Costin): „Un plafon care nu poate ajunge la zero isi pierde functia."
Cateva locuri poarta cheia `mesaj` fara sa fie afirmatii despre datele firmei. Ele nu se pot converti:
n-au ce tipa. Fara un registru, ar sta pe vecie in clichet si numarul n-ar mai putea ajunge la zero -
adica n-ar mai putea spune „gata".

DE CE E PERICULOS, si ce-l tine onest. Intrebarea lui Costin: ce impiedica o intrare noua sa fie
ADAUGATA aici in loc sa fie REPARATA? Trei zavoare, in `core/test_registru_exceptii.py`:
  1. registrul nu poate CRESTE (dimensiunea lui e clichet);
  2. fiecare intrare trebuie sa fie VIE - situl numit trebuie sa existe si sa fie inca netipat, deci
     cine converteste trebuie sa scoata intrarea (echivalentul lui „exceptia trebuie sa fie folosita");
  3. motivul se alege din setul INCHIS de mai jos.

AL TREILEA E CEL REAL. „Rezultat de operatie" NU e in set, deliberat: e o FORMA, nu o natura, si s-ar
umple pe masura ce clichetul strange. Cand am spus „vreo cinci, rezultate de operatie", Costin a
intrebat daca sunt de aceeasi natura. Masurate, erau ~11, de PATRU naturi - iar doua dintre ele erau
afirmatii adevarate pe care le-as fi ascuns aici. Alea doua s-au reparat.
"""

# Setul INCHIS de ratiuni. Fiecare descrie o NATURA, nu o forma: ceva ce nu poate deveni afirmatie
# despre datele firmei oricat ai lucra la el.
RATIUNI = {
    "nu_despre_firma": "Subiectul nu sunt datele firmei (disponibilitatea unei unelte, o sesizare "
                       "de suport, un cont de utilizator). Nu exista firma despre care sa afirme.",
    "raspuns_extern_verbatim": "Textul e produs de ALTCINEVA (ANAF/SPV) si se reda neatins. A-l "
                               "tipa ar insemna sa pretindem ca e afirmatia noastra - iar daca il "
                               "reformulam ca sa incapa intr-un tip, contabilul nu mai vede ce a "
                               "spus autoritatea.",
    "trecere_prin_tipat": "Locul doar RE-IMPACHETEAZA o afirmatie deja tipata in alta parte. A o "
                          "tipa a doua oara ar crea o a doua sursa a aceluiasi text.",
    "avertisment_de_actiune": "Text despre ce URMEAZA sa faca utilizatorul (ireversibilitate, "
                              "confirmare ceruta), nu despre ce ESTE in datele firmei.",
}

# Fiecare intrare: unde e, ce ratiune, si argumentul propriu. Ratiunea e categoria; `de_ce` e motivul.
EXCEPTII = [
    {"fisier": "core/raportari_ai.py", "functie": "triaj", "motiv": "nu_despre_firma",
     "de_ce": "triajul unei sesizari de suport: `motiv` spune de ce asistentul AI nu poate raspunde "
              "(AI indisponibil / raspuns fara continut / eroare de apel - trei ramuri, aceeasi "
              "natura). Nu exista firma despre care sa afirme ceva."},
    {"fisier": "core/tipare_api.py", "functie": "tipare", "motiv": "raspuns_extern_verbatim",
     "de_ce": "motivele de respingere sunt textul ANAF, citit din `declaratii_coada.motiv_respingere` "
              "si GRUPAT ca sa se vada tiparele. Le tipam = pretindem ca sunt afirmatiile noastre."},
    {"fisier": "main.py", "functie": "factura_trimite_spv", "motiv": "raspuns_extern_verbatim",
     "de_ce": "raspunsul SPV la trimiterea unei facturi (index_incarcare, execution_status, erori de "
              "validare ANAF). Se reda neatins - o reformulare ar ascunde ce a spus autoritatea."},
    {"fisier": "core/gdpr_sterge.py", "functie": "previzualizare", "motiv": "avertisment_de_actiune",
     "de_ce": "previzualizarea stergerii unui cabinet: campul `avertisment` spune ca operatiunea e "
              "IREVERSIBILA si ce NU se sterge. E despre ce urmeaza sa faca omul, nu despre ce e in "
              "datele firmei. Cifrele de alaturi (nr_tenanti, nr_useri) sunt fapte, dar ele nu poarta "
              "cheia de revendicare - avertismentul o poarta."},
    {"fisier": "main.py", "functie": "portal_acasa", "motiv": "trecere_prin_tipat",
     "de_ce": "portalul re-impacheteaza pentru client verdictul deja produs de "
              "`control_fiscal_api.evalueaza_firma`. Tiparea aici ar face a doua sursa a aceluiasi text."},
]


def _cheie(x):
    """Cheia unei intrari de inventar: (fisier, functie). NU linia - vezi capul lui `EXCEPTII`."""
    return (x[0], x[1])


def datorie_reala(inventar=None):
    """Cifra care POATE ajunge la zero: netipatele MINUS excepțiile declarate.

    UNITATEA e INTRAREA din inventar, nu poziția (fișier, linie) — aceeași unitate ca baseline-ul
    clichetului. Prima formă primea o MULȚIME de poziții și le număra pe alea: pe 22.08 asta a dat
    17 acolo unde clichetul număra 18, fiindcă `control_fiscal_api:960` are DOUĂ dicționare pe
    aceeași linie. Două cifre în două unități, prezentate ca aceeași măsură — exact felul de
    nepotrivire tăcută pe care campania asta o vânează.

    Fără argument citește singură inventarul, ca să nu se mai poată da unitatea greșită din afară."""
    from core import scan_afirmatii as _scan
    lst = _scan.netipate_in_scop() if inventar is None else list(inventar)
    ex = {(e["fisier"], e["functie"]) for e in EXCEPTII}
    return len([x for x in lst if _cheie(x) not in ex])


if __name__ == "__main__":
    from collections import Counter
    print("excepții declarate: %d | rațiuni: %s"
          % (len(EXCEPTII), dict(Counter(e["motiv"] for e in EXCEPTII))))
