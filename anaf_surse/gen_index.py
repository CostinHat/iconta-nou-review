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
    "cf_2015_forma_initiala.html": "forma_la_data",
    "oug_50_2015_consolidat.html": "forma_la_data",
    "hg_276_2013.html": "forma_la_data",
    "anaf_limite_2025.pdf": "forma_la_data",   # tabel de limite ANAF pt 2025 (valori la date fixe)
    "legea_201_2025.html": "forma_la_data",    # act punctual (tichet 45 de la noiembrie 2025)
    "oug_156_2024.pdf": "forma_la_data",       # act punctual (plafon facilitate 4300 pt 2025)
    "oug_8_2026.html": "forma_la_data",         # act punctual (plafon TVA incasare + mijloc fix 2026-2027)
    "oug_89_2025.html": "forma_la_data",
    "legea_207_2015_consolidat.html": "consolidat_la_zi",  # Cod procedura fiscala (consolidat la zi, OUG 38/2026)
    "omf_1235_2023.pdf": "forma_la_data",           # indemnizatie deplasare interna 23 lei de la 01.04.2023
        # act punctual (facilitate salariu minim + plafon 2026)
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


# --- sursa + forma pentru intrarile NOI (adaugate azi). "fara ele corpusul minte" (cerut 13.08.2026) ---
import datetime as _dt, time as _time

# Marcaje OBLIGATORII: override explicit (sursa, forma, nota) - au prioritate peste detectie.
_FORMA_OVR = {
    "omfp_1802_2014.pdf": ("static.anaf.ro", "initiala",
        "forma initiala 2014; NU include Ordinul 1239/2021, 4291/2022, 5378/2023, OMF 52/2024; "
        "planul de conturi e INCOMPLET (lipsesc 467, 6053, 694, 794)"),
    "legea_273_2006_fin_publice_locale.pdf": ("static.anaf.ro", "consolidata", "consolidare 2018, nu la zi"),
    "oug_8_2009_acordarea_tichetelor_vacanta.html": ("legex.ro", "necunoscuta", "sursa legex.ro, neoficiala"),
}

_AZI0 = _time.mktime(_dt.date.today().timetuple())  # inceputul zilei curente


def _forma_html(cale):
    """Forma CITITA din eticheta fisierului just.ro (nu presupusa): 'Forma consolidata' / 'forma de baza'."""
    try:
        low = io.open(cale, encoding="utf-8", errors="replace").read().lower()
    except Exception:
        return "necunoscuta", False
    e_justro = "portal legislativ" in low
    if "forma consolidat" in low or "forma actualizat" in low:
        return "consolidata", e_justro
    if "forma de baza" in low or "forma de bază" in low:
        return "initiala", e_justro
    return "necunoscuta", e_justro


def _sursa_forma(fname):
    """(sursa, forma, nota) pentru intrarile NOI de azi; (None, None, None) altfel. Override > detectie."""
    if fname in _FORMA_OVR:
        return _FORMA_OVR[fname]
    cale = os.path.join(SURSE, fname)
    try:
        nou = os.path.getmtime(cale) >= _AZI0
    except OSError:
        return None, None, None
    if not nou:
        return None, None, None          # doar intrarile noi primesc sursa/forma
    if fname.lower().endswith((".html", ".htm")):
        forma, e_justro = _forma_html(cale)
        if e_justro:
            return "legislatie.just.ro", forma, None
        # html de la ANAF (ex. coduri consolidate) sau alt static
        return "static.anaf.ro", ("consolidata" if "_consolidat" in fname or "cod_fiscal" in fname else forma), None
    # pdf/xsd fara sursa browser -> static.anaf.ro; forma de la publicare (initiala), exceptand consolidatele
    return "static.anaf.ro", ("consolidata" if "_consolidat" in fname else "initiala"), None



# A: fisiere cu text NEEXTRACTIBIL (formular XFA) - .txt-ul trunchiat a fost sters; INDEX o spune explicit.
_TEXT_FALSE = {
    "D112_XML_2026_0726_050826.pdf": "formular XFA neextractabil",
    "D311_XML_2021_290121.pdf": "formular XFA neextractabil",
}

fisiere = {}
for fname in sorted(fisiere_pe_disc):
    if fname in ("INDEX.json",):
        continue
    if fname.startswith("GRESIT_"):       # B: act gresit, in carantina - scos din INDEX (nu din disc)
        continue
    intr = sorted(per_fisier.get(fname, []), key=lambda x: (x["cota"], x["data_in"]))
    _srs, _frm, _nota = _sursa_forma(fname)
    _ent = {
        "exista": True,
        "tip_forma": TIP_FORMA.get(fname),
        "acopera": intr,
    }
    if _srs:
        _ent["sursa"] = _srs
    if _frm:
        _ent["forma"] = _frm
    if _nota:
        _ent["nota"] = _nota
    if fname in _TEXT_FALSE:
        _ent["text_extras"] = False
        _ent["motiv"] = _TEXT_FALSE[fname]
    fisiere[fname] = _ent

# fisiere citate in COTE dar lipsa pe disc (nu ar trebui sa existe dupa garda 1, dar il raportam)
citate_lipsa = sorted(set(per_fisier) - fisiere_pe_disc)

# Acte ABROGATE (fara fisier pe disc): marcaj explicit ca absenta NU e o gaura, ci un act inlocuit.
_ABROGATE = {
    "opanaf_394_2017_d390_anexa2_instructiuni.pdf": {"stare": "abrogat", "inlocuit_de": "opanaf_705_2020"},
    "hg_685_1999_norme_compensare_creante_datorii.html": {"stare": "abrogat", "inlocuit_de": "hg_773_2019",
        "nota": "abrogat de HG 773/2019 (in vigoare 01.01.2020); forma istorica adusa pt referinta - HG 773/2019 nu e in corpus"},
}
for _k, _v in _ABROGATE.items():
    fisiere.setdefault(_k, {}).update(_v)

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
