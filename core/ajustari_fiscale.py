# -*- coding: utf-8 -*-
"""core/ajustari_fiscale.py — ajustările fiscale ale rezultatului (Registrul de evidență fiscală, varianta pe profit): sursa UNICĂ pentru
D100 trimestrial (cumulat de la 01.01) și pentru D101 (anul).

[deficiența 378, comanda Costin 8.2, 18.10.2026, verbatim în DECIZII „Comanda 8.2”] „D100 trimestrial pornește de la rezultatul fiscal
cumulat din Registrul de evidență fiscală (cheltuieli nedeductibile, venituri neimpozabile, credit fiscal din sponsorizări, recuperarea
pierderii fiscale din anii anteriori în limitele legale).”

Temeiul (citat în `anaf_surse/cod_fiscal_227_2015_consolidat.html`, forma din 08.08.2026):
- CF art.19 alin.(1): „Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor
  contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile.
  La stabilirea rezultatului fiscal se iau în calcul și elemente similare veniturilor și cheltuielilor [...] precum și pierderile fiscale
  care se recuperează în conformitate cu prevederile art. 31.”
- HG 1/2016 pct.8 (registrul de evidență fiscală, totalizare „pe trimestru și/sau an fiscal”).

Până azi ajustările intrau numai în D101, prin `date_extra` trimis la generare — fără niciun ecran care să le scrie —, iar D100 pe profit
nu le vedea deloc. Acum omul le scrie o dată, pe trimestrul în care s-au produs, și le citesc amândouă declarațiile.

Fiecare ajustare stă pe rândul OFICIAL al formularului D101 (OPANAF 206/2025, `anaf_surse/opanaf_206_2025_d101.txt`), deci aceeași cifră
intră în D101 la rândul ei și în D100 în rezultatul fiscal cumulat. Rândurile acceptate sunt cele de mai jos (nomenclator închis); cele pe
care aplicația le derivă singură (rd.1–7 din contabilitate, rd.13 rezerva legală, rd.43.1 creditul de sponsorizare) nu se scriu aici.
"""
from decimal import ROUND_DOWN, Decimal

from core import common as c
from core import repo_ajustari_fiscale as _repo

#: rândul D101 -> (denumirea scurtă, grupa). Denumirile urmează instrucțiunile OPANAF 206/2025 (rândul X „se completează cu …”).
RANDURI = {
    "P8": ("rd.8 — elemente similare veniturilor", "similare"),
    "P9": ("rd.9 — elemente similare cheltuielilor", "similare"),
    "P11": ("rd.11 — amortizarea fiscală", "deduceri"),
    "P14": ("rd.14 — provizioane / ajustări pentru depreciere deductibile", "deduceri"),
    "P15": ("rd.15 — alte deduceri", "deduceri"),
    "P17": ("rd.17 — dividende primite", "neimpozabile"),
    "P18": ("rd.18 — venituri financiare neimpozabile", "neimpozabile"),
    "P19": ("rd.19 — venituri din lichidarea altei persoane juridice", "neimpozabile"),
    "P20": ("rd.20 — alte venituri neimpozabile", "neimpozabile"),
    "P23": ("rd.23 — cheltuieli cu impozitul pe profit", "nedeductibile"),
    "P24": ("rd.24 — impozitul pe profit / venit plătit în străinătate", "nedeductibile"),
    "P25": ("rd.25 — amenzi, majorări și penalități (art.25 alin.(4) lit.b)", "nedeductibile"),
    "P26": ("rd.26 — protocol peste limita legală", "nedeductibile"),
    "P27": ("rd.27 — sponsorizare și mecenat", "nedeductibile"),
    "P28": ("rd.28 — amortizarea contabilă", "nedeductibile"),
    "P29": ("rd.29 — provizioane / ajustări nedeductibile", "nedeductibile"),
    "P30": ("rd.30 — pierderea netă nedeductibilă (art.25 alin.(10))", "nedeductibile"),
    "P31": ("rd.31 — dobânzi și costuri echivalente nedeductibile", "nedeductibile"),
    "P32": ("rd.32 — cheltuieli aferente veniturilor neimpozabile", "nedeductibile"),
    "P33": ("rd.33 — alte cheltuieli nedeductibile", "nedeductibile"),
    "P39": ("rd.39 — pierderi fiscale de recuperat din anii anteriori", "pierdere"),
}

#: pierderea din anii anteriori e o cifră a ANULUI (stabilită prin D101-urile anterioare), nu a unui trimestru
ANUALE = ("P39",)

#: CF art.31 alin.(1) (forma Legii 296/2023, de la 01.01.2024): pierderea se recuperează în limita a 70%, la fiecare termen de plată.
#: Procent, în forma din lege („70%”), ca citatul să-și poarte valoarea.
PRAG_RECUPERARE_PIERDERE = c.ancoreaza("ajustari_fiscale.PRAG_RECUPERARE_PIERDERE", Decimal("70"), c.Temei(
    "CF", art="31", alin="1", data_in="2024-01-01", nivel_sursa="MO", de_cine="Code", verificat_la="2026-10-18",
    url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="Pierderile fiscale anuale stabilite prin declarația de impozit pe profit, începând cu anul 2024 [...] se recuperează din "
               "profiturile impozabile realizate, în limita a 70% inclusiv, în următorii 5 ani consecutivi. Recuperarea pierderilor se va "
               "efectua în ordinea înregistrării acestora, la fiecare termen de plată a impozitului pe profit."))


def valideaza(an, trim, rand, suma):
    """Motivul refuzului (text pentru om) sau None."""
    if rand not in RANDURI:
        return "Rândul %r nu e o ajustare fiscală acceptată; alege unul din listă." % (rand,)
    try:
        an = int(an)
    except (TypeError, ValueError):
        return "Anul lipsește sau nu e un număr."
    if not 2000 <= an <= 2100:
        return "Anul %d nu e plauzibil." % an
    if rand in ANUALE:
        if trim not in (None, "", 0):
            return "Pierderea de recuperat din anii anteriori e o cifră a anului: nu se scrie pe trimestru."
    elif trim not in (1, 2, 3, 4):
        return "Alege trimestrul în care s-a produs ajustarea (1–4)."
    try:
        s = Decimal(str(suma))
    except Exception:  # noqa: BLE001 — orice intrare nenumerică are același răspuns
        return "Suma trebuie să fie un număr."
    if s <= 0:
        return "Suma trebuie să fie mai mare ca 0; ajustarea greșită se șterge, nu se scade cu o sumă negativă."
    return None


def lista(cur, schema, an):
    return [{"id": r[0], "an": r[1], "trim": r[2], "rand": r[3], "eticheta": RANDURI.get(r[3], (r[3],))[0], "suma": str(r[4]),
             "descriere": r[5], "document": r[6]} for r in _repo.lista(cur, schema, an)]


def adauga(cur, schema, an, trim, rand, suma, descriere=None, document=None, user_id=None):
    motiv = valideaza(an, trim, rand, suma)
    if motiv:
        raise ValueError(motiv)
    return _repo.adauga(cur, schema, int(an), None if rand in ANUALE else int(trim), rand, Decimal(str(suma)), descriere or None,
                        document or None, user_id)


def sterge(cur, schema, ajustare_id):
    return _repo.sterge(cur, schema, int(ajustare_id))


def cumulat(cur, schema, an, pana_la_trim):
    """{rand D101: suma} — ajustările anului de la T1 până la `pana_la_trim` inclusiv, plus cele anuale (pierderea de recuperat).
    Aceeași funcție pentru D100 (trimestrul de raportare) și pentru D101 (tot anul: trimestrul IV)."""
    return {r: Decimal(str(s)) for r, s in _repo.cumulat(cur, schema, int(an), int(pana_la_trim))}


def recuperare_pierdere(pierdere, rezultat_inainte):
    """Pierderea recuperată în perioadă (rd.39.1): cel mult 70% din profitul impozabil dinaintea recuperării (CF art.31 alin.(1)) și
    cel mult pierderea de recuperat. Pe pierdere fiscală, nimic."""
    pierdere, rezultat_inainte = Decimal(str(pierdere or 0)), Decimal(str(rezultat_inainte or 0))
    if pierdere <= 0 or rezultat_inainte <= 0:
        return Decimal(0)
    # „în limita a 70% inclusiv”: plafonul nu se depășește nici prin rotunjire — în jos, la leu
    return min(pierdere, (rezultat_inainte * PRAG_RECUPERARE_PIERDERE / Decimal(100)).quantize(Decimal(1), rounding=ROUND_DOWN))
