# -*- coding: utf-8 -*-
"""core/ghid_titluri.py — lista de bază pentru producția de ghiduri.

`index_titluri_ghid.csv` (rădăcina repo) e registrul canonic al TITLURILOR candidate — 8.713
întrebări indexate/categorizate din care se produc ghiduri. Aici doar CITIREA lui, ca redactarea
(pasul 3) și rapoartele să nu re-parseze CSV-ul cu presupuneri despre coloane.

Coloane (verificat la sursă 21.09.2026): id, titlu, categorie, status, functionalitate_iconta,
posibil_duplicat_sens, slug_publicat.

[29.09.2026] Coloana slug_publicat + statusul publicat: un titlu cu ghid LIVE (potrivire pe titlu EXACT sau NORMALIZAT - fara diacritice, punctuatie, anul 2026) trece pe status=publicat, cu slug-ul ghidului in slug_publicat. Cazurile doar asemanatoare raman candidat (nemarcate). [29.09.2026] Statusul asemanator + coloana slug_asemanator: titlurile doar ASEMANATOARE cu un ghid live (nu identice dupa normalizare) se marcheaza status=asemanator, cu slug-ul celui mai apropiat ghid in slug_asemanator. Ca si publicat, statusul asemanator se EXCLUDE din orice lista de titluri de propus (v. de_propus()).

Nu produce ghiduri și nu leagă titlu↔funcționalitate — legarea se face PER PAGINĂ la redactare,
verificată pe cod real (poarta din core/ghid_poarta.py). Aici e strict inventarul de intrare.
"""
import csv
import io
import os

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALE = os.path.join(RADACINA, "index_titluri_ghid.csv")

COLOANE = ("id", "titlu", "categorie", "status", "functionalitate_iconta", "posibil_duplicat_sens", "slug_publicat", "slug_asemanator")


def incarca(cale=None):
    """[dict] cu toate titlurile candidate, în ordinea din fișier. Cheile = COLOANE."""
    p = cale or CALE
    with io.open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


STATUSURI_EXCLUSE_PROPUNERE = ("publicat", "asemanator")


def de_propus(cale=None):
    """[dict] titlurile inca de propus: status == 'candidat'. Exclude publicat si asemanator
    (au deja un ghid live, identic sau apropiat)."""
    return [r for r in incarca(cale) if r.get("status") == "candidat"]


def categorii(cale=None):
    """{categorie: număr} — distribuția pe categorii a listei de bază."""
    out = {}
    for r in incarca(cale):
        out[r["categorie"]] = out.get(r["categorie"], 0) + 1
    return out


if __name__ == "__main__":
    rows = incarca()
    print("Listă de bază ghiduri: %d titluri (%s)" % (len(rows), CALE))
    cat = categorii()
    for k in sorted(cat, key=lambda x: -cat[x]):
        print("  %-24s %d" % (k, cat[k]))
