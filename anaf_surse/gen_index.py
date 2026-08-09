# -*- coding: utf-8 -*-
"""Corpus (2): genereaza manifestul anaf_surse/INDEX.json din COTE (temeiuri MO cu url local) + tabela
tip_forma per fisier. INDEX = harta fisier -> {tip_forma, cote acoperite}. Deterministic (sortare stabila)."""
import io, json, os
from core.common import COTE

# tabela manuala: tipul formei fiecarui fisier-sursa local.
#   consolidat_la_zi  = forma consolidata la zi -> contine DOAR valoarea in vigoare acum (garda 2 refuza
#                       daca valoarea citata are un succesor mai nou -> forma la zi n-o mai contine).
#   forma_la_data     = forma la o data fixa (forma initiala / HG punctual / ordin) -> contine valoarea
#                       de la acea data chiar daca exista valori mai noi in alte acte.
TIP_FORMA = {
    "cod_fiscal_227_2015_consolidat.html": "consolidat_la_zi",
    "legea_141_2025_consolidat.html": "consolidat_la_zi",
    "cf_art291_2016_forma_initiala.txt": "forma_la_data",
    "hg_1506_2024_salariu_minim.html": "forma_la_data",
    "hg_146_2026_salariu_minim.html": "forma_la_data",
    "legea_296_2020_consolidat.html": "forma_la_data",
    "oug_115_2023_consolidat.html": "forma_la_data",
    "og_16_2022_consolidat.html": "forma_la_data",
    "legea_70_2015_consolidat.html": "forma_la_data",
    "anaf_limite_2025.pdf": "forma_la_data",   # tabel de limite ANAF pt 2025 (valori la date fixe)
    "legea_201_2025.html": "forma_la_data",    # act punctual (tichet 45 de la noiembrie 2025)
    "oug_156_2024.pdf": "forma_la_data",       # act punctual (plafon facilitate 4300 pt 2025)
    "oug_8_2026.html": "forma_la_data",         # act punctual (plafon TVA incasare + mijloc fix 2026-2027)
    "oug_89_2025.html": "forma_la_data",        # act punctual (facilitate salariu minim + plafon 2026)
}

SURSE = "anaf_surse"
fisiere_pe_disc = set(os.listdir(SURSE))

per_fisier = {}
for nume, intrari in COTE.items():
    for d, v, t in intrari:
        url = getattr(t, "url", None)
        ns = getattr(t, "nivel_sursa", None)
        if not (url and url.startswith(SURSE + "/")):
            continue
        fname = url.split("/", 1)[1]
        per_fisier.setdefault(fname, []).append({
            "cota": nume, "data_in": str(d), "valoare": str(v), "nivel_sursa": ns,
            "temei": "%s %s/%s art.%s" % (t.tip, t.nr or "", t.an or "", t.art or ""),
        })

fisiere = {}
for fname in sorted(fisiere_pe_disc):
    if fname in ("INDEX.json",):
        continue
    intr = sorted(per_fisier.get(fname, []), key=lambda x: (x["cota"], x["data_in"]))
    fisiere[fname] = {
        "exista": True,
        "tip_forma": TIP_FORMA.get(fname),
        "acopera": intr,
    }

# fisiere citate in COTE dar lipsa pe disc (nu ar trebui sa existe dupa garda 1, dar il raportam)
citate_lipsa = sorted(set(per_fisier) - fisiere_pe_disc)

manifest = {
    "_generat_de": "gen_index.py (Corpus 2)",
    "_nota": "Regenereaza cu: venv/bin/python gen_index.py. tip_forma e declarat manual in TIP_FORMA.",
    "fisiere": fisiere,
    "citate_dar_lipsa_pe_disc": citate_lipsa,
    "fisiere_fara_tip_forma_declarat": sorted(
        f for f, m in fisiere.items() if m["acopera"] and m["tip_forma"] is None),
}
io.open(os.path.join(SURSE, "INDEX.json"), "w", encoding="utf-8").write(
    json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n")
print("INDEX.json scris: %d fisiere-sursa mapate, %d cu cote legate" % (
    len(fisiere), sum(1 for m in fisiere.values() if m["acopera"])))
for f, m in fisiere.items():
    if m["acopera"]:
        print("  %-42s [%s] %d cote" % (f, m["tip_forma"], len(m["acopera"])))
