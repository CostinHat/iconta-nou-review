# -*- coding: utf-8 -*-
"""Corpus (2): cele TREI garzi peste registrul de temeiuri COTE + manifestul anaf_surse/INDEX.json.

  G1 test_temei_mo_are_sursa_locala      - un Temei MO trebuie sa pointeze la un fisier local existent.
  G2 test_forma_consolidata_are_succesor - o forma 'consolidat_la_zi' nu poate fi sursa pt o valoare care
                                           a fost ULTERIOR schimbata (are un succesor mai nou) - forma la zi
                                           n-o mai contine. Formele 'forma_la_data' (istorice) sunt exceptate.
  G3 test_cote_volatile_fara_mo_set_fix  - pragul de avertizare la generare selecteaza EXACT setul asteptat
                                           (volatile/recente fara MO); nu devine zgomot pe REDARE stabile.
Plus: manifestul INDEX.json e coerent cu COTE (fara fisiere lipsa, fara tip_forma nedeclarat)."""
import json
import os
from datetime import date

from core.common import COTE, cote_volatile_fara_mo

SURSE = "anaf_surse"
INDEX = os.path.join(SURSE, "INDEX.json")


def _index():
    with open(INDEX, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- G1
def test_temei_mo_are_sursa_locala():
    """REGULA: nivel_sursa='MO' inseamna 'verificat verbatim intr-un fisier local' -> url obligatoriu, catre
    anaf_surse/, fisier care EXISTA pe disc. Fara asta, 'MO' e o eticheta fara acoperire."""
    pe_disc = set(os.listdir(SURSE))
    lipsa = []
    for nume, intrari in COTE.items():
        for d, v, t in intrari:
            if getattr(t, "nivel_sursa", None) != "MO":
                continue
            url = getattr(t, "url", None)
            if not (url and url.startswith(SURSE + "/") and url.split("/", 1)[1] in pe_disc):
                lipsa.append("%s@%s url=%r" % (nume, d, url))
    assert not lipsa, "temeiuri MO fara sursa locala existenta:\n  " + "\n  ".join(lipsa)


# ---------------------------------------------------------------- G2
def test_forma_consolidata_nu_e_sursa_pentru_valoare_cu_succesor():
    """O forma CONSOLIDATA LA ZI contine doar valoarea in vigoare acum. Daca un Temei MO citeaza o astfel de
    forma pentru o valoare care are un SUCCESOR (o intrare mai noua in aceeasi cota), forma la zi nu mai
    contine valoarea citata -> eroare de sursa. Formele istorice (forma_la_data) sunt exceptate."""
    idx = _index()["fisiere"]
    gresite = []
    for nume, intrari in COTE.items():
        # data cea mai noua din cota
        data_max = max(d for d, v, t in intrari)
        for d, v, t in intrari:
            if getattr(t, "nivel_sursa", None) != "MO":
                continue
            url = getattr(t, "url", None)
            if not (url and url.startswith(SURSE + "/")):
                continue
            fname = url.split("/", 1)[1]
            tip = idx.get(fname, {}).get("tip_forma")
            if tip == "consolidat_la_zi" and d < data_max:
                gresite.append("%s@%s cita forma la zi %s dar are succesor @%s" % (nume, d, fname, data_max))
    assert not gresite, "forma consolidata folosita pt valoare depasita:\n  " + "\n  ".join(gresite)


# ---------------------------------------------------------------- INDEX coerent
def test_index_coerent_cu_cote():
    """Manifestul nu citeaza fisiere lipsa pe disc si declara tip_forma pt orice fisier cu cote legate."""
    m = _index()
    assert not m["citate_dar_lipsa_pe_disc"], "INDEX citeaza fisiere absente: %s" % m["citate_dar_lipsa_pe_disc"]
    assert not m["fisiere_fara_tip_forma_declarat"], (
        "fisiere cu cote legate dar fara tip_forma in TIP_FORMA: %s" % m["fisiere_fara_tip_forma_declarat"])


# ---------------------------------------------------------------- G3
# Setul de referinta MASURAT la 2026-08-07 (nu ghicit). Sunt exact cotele a caror valoare curenta e non-MO
# si volatila/recenta. Dupa aducerea OUG 8/2026 + OUG 89/2025 (07.08) ramane doar tva_redusa_5 (de decis).
# Daca lista se schimba: ori ai adaugat o cota volatila fara sursa (leag-o la MO / adu actul), ori ai legat
# una (scoate-o de aici). Gardul te forteaza sa fii constient - nu e zgomot pasiv.
SET_VOLATIL_FARA_MO_20260807 = [
    # 07.08: cele 4 plafoane legate MO. 09.08 (tura 7): tva_redusa_5 rezolvat verbatim (Legea 141 pct.42 art.291
    # alin.2 lit.g carti + lit.h cultural = 11%; locuinte sociale -> 21%) -> legat MO. Set gol: nicio cota vie
    # fara sursa. Daca reapare ceva aici: leag-o la MO / adu actul, sau scoate-o dupa legare.
]


def test_cote_volatile_fara_mo_set_fix():
    """G3 la data de referinta fixa (determinist): pragul selecteaza EXACT setul asteptat, nici mai mult
    (zgomot pe stabile), nici mai putin (a scapat o cota vie fara sursa)."""
    obtinut = cote_volatile_fara_mo(la_data=date(2026, 8, 7))
    assert obtinut == SET_VOLATIL_FARA_MO_20260807, (
        "set volatil-fara-MO schimbat:\n  asteptat %s\n  obtinut  %s" % (
            SET_VOLATIL_FARA_MO_20260807, obtinut))


def test_g3_nu_semnaleaza_valori_mo_sau_stabile():
    """Contra-proba: nicio cota din set nu are valoarea curenta MO; nicio cota MO-curenta nu e in set."""
    set_v = set(cote_volatile_fara_mo(la_data=date(2026, 8, 7)))
    for nume, intrari in COTE.items():
        curent_mo = getattr(max(intrari, key=lambda iv: iv[0])[2], "nivel_sursa", None) == "MO"
        if curent_mo:
            assert nume not in set_v, "%s are valoarea curenta MO dar e semnalata" % nume


# ────────────────────────────────────────────────────────────────────────────
#  G4 — TIP_FORMA se verifica DIRECT contra COTE, nu contra manifestului
#
#  DE CE (22.08.2026, dupa un commit respins de poarta): G1..G3 si
#  `test_index_coerent_cu_cote` citesc `INDEX.json`, care e GENERAT. Un Temei nou, adaugat pe 16.08 cu
#  `url=anaf_surse/oug_156_2024.txt`, n-a fost vazut de niciunul dintre ele pana cand cineva a
#  regenerat manifestul — sase zile mai tarziu, si din intamplare. Manifestul stale nu minte: pur si
#  simplu descrie o lume mai veche.
#
#  CE FACE IMPOSIBIL: un fisier legat de o cota, fara `tip_forma` declarat in `TIP_FORMA`, indiferent
#  de cand a fost regenerat `INDEX.json`.
#
#  CE NU FACE, declarat: nu verifica daca `tip_forma` e CORECT (consolidat_la_zi vs forma_la_data) —
#  aia o face G2, pe succesori. Verifica doar ca declaratia EXISTA.
# ────────────────────────────────────────────────────────────────────────────

def _tip_forma_din_sursa():
    """`TIP_FORMA` citit cu `ast` din `anaf_surse/gen_index.py`.

    NU prin import: modulul acela SCRIE `INDEX.json` la incarcare, iar un test care scrie in repo e
    exact sonda care nu e read-only. `ast` citeste litera, fara sa execute nimic."""
    import ast
    cale = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "anaf_surse", "gen_index.py")
    with open(cale, encoding="utf-8") as f:
        arbore = ast.parse(f.read())
    for nod in arbore.body:
        if isinstance(nod, ast.Assign) and any(
                getattr(t, "id", None) == "TIP_FORMA" for t in nod.targets):
            return ast.literal_eval(nod.value)
    raise AssertionError("TIP_FORMA nu s-a gasit in anaf_surse/gen_index.py — gardul nu are ce citi")


def test_tip_forma_se_citeste_din_sursa():
    """ANTI-VACUU pe instrument: daca parsarea se rupe, G4 ar trece pe zero fisiere."""
    tf = _tip_forma_din_sursa()
    assert len(tf) >= 15, "doar %d intrari in TIP_FORMA — parsarea s-a rupt, nu tabela s-a golit" % len(tf)
    assert "cod_fiscal_227_2015_consolidat.html" in tf


def test_orice_fisier_legat_de_o_cota_are_tip_forma():
    """G4. Direct contra COTE — nu contra `INDEX.json`, care e generat si poate fi stale."""
    tf = _tip_forma_din_sursa()
    lipsa = {}
    for nume, intrari in COTE.items():
        for d, _v, t in intrari:
            url = getattr(t, "url", None) or ""
            if not url.startswith(SURSE + "/"):
                continue
            f = url.split("/", 1)[1]
            if f not in tf:
                lipsa.setdefault(f, []).append("%s@%s" % (nume, d))
    assert not lipsa, (
        "fisiere legate de cote, fara tip_forma declarat in gen_index.TIP_FORMA:\n  "
        + "\n  ".join("%s  <- %s" % (f, ", ".join(c[:3])) for f, c in sorted(lipsa.items())))
