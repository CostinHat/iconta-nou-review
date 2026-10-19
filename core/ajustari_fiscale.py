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

#: [deficiența 378, lotul 9 — retestul 19.10.2026: „Rândul există pe ecran, dar nu se umple din conturi.”] Rândurile care se iau din
#: CONTABILITATE cât timp contabilul nu le scrie el în registru: rândul D101 -> (contul, cum se numește pe ecran). Rulajul net debitor al
#: contului, pe notele validate ale ferestrei (aceeași fereastră ca rd.1–7). Dacă omul scrie rândul în registru (oricare trimestru al
#: anului), cifra lui înlocuiește contul pe tot rândul — aceeași regulă ca rezerva legală (rd.13), derivată numai cât nu e dată.
#: Temeiul: CF art.25 alin.(4) lit.b („dobânzile/majorările de întârziere, amenzile, confiscările și penalitățile, datorate către
#: autoritățile române/străine, potrivit prevederilor legale, cu excepția celor aferente contractelor încheiate cu aceste autorități”);
#: contul: OMFP 1802/2014, 6581 „Despăgubiri, amenzi și penalități”.
#: INTERPRETARE CU TEMEI: 6581 ține și despăgubirile / penalitățile contractuale (deductibile). Implicitul ia tot contul ca nedeductibil,
#: fiindcă omisiunea lui SUBEVALUEAZĂ impozitul (direcția care costă la control); partea deductibilă se scoate scriind rândul 25 cu
#: suma nedeductibilă reală. Alternativa respinsă: rândul gol până îl scrie omul (retestul 19.10 arată exact ce produce: amenda intră ca
#: deductibilă, fără niciun semn). De reconfirmat dacă apare o normă care transează.
DIN_CONTURI = {"P25": ("amenzi", "contul 6581 — despăgubiri, amenzi și penalități")}


def din_conturi(rulaje):
    """{rand D101: suma} — rândurile `DIN_CONTURI`, din rulajele întoarse de `repo_d101.select_inregistrari_linii`."""
    return {rand: Decimal(str(rulaje.get(cheie) or 0)) for rand, (cheie, _) in DIN_CONTURI.items()
            if Decimal(str(rulaje.get(cheie) or 0)) > 0}


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
    """Ajustările anului. `automata` = scrisă de aplicație dintr-o notă (`inregistrare_id`); `in_calcul` = intră în D100 / D101 acum
    (cea scrisă de om, mereu; cea automată, numai cu nota validată — `repo_ajustari_fiscale.cumulat`)."""
    return [{"id": r[0], "an": r[1], "trim": r[2], "rand": r[3], "eticheta": RANDURI.get(r[3], (r[3],))[0], "suma": str(r[4]),
             "descriere": r[5], "document": r[6], "automata": r[7] is not None, "in_calcul": r[7] is None or bool(r[8])}
            for r in _repo.lista(cur, schema, an)]


def adauga(cur, schema, an, trim, rand, suma, descriere=None, document=None, user_id=None, inregistrare_id=None):
    motiv = valideaza(an, trim, rand, suma)
    if motiv:
        raise ValueError(motiv)
    return _repo.adauga(cur, schema, int(an), None if rand in ANUALE else int(trim), rand, Decimal(str(suma)), descriere or None,
                        document or None, user_id, inregistrare_id)


#: [deficiența 404, lotul 9, decizia Costin 19.10.2026 „Da, automat”, verbatim în DECIZII „Închiderea lotului 9”] lipsa NEIMPUTABILĂ de la
#: inventar trece singură la ajustări, pe rândul D101 al „altor cheltuieli nedeductibile”. Temeiul:
#:   CF art.25 alin.(4) lit.c (`anaf_surse/cod_fiscal_227_2015_consolidat.txt`:1367): „(4) Următoarele cheltuieli nu sunt deductibile: [...]
#:   c) cheltuielile privind bunurile de natura stocurilor sau a mijloacelor fixe amortizabile constatate lipsă din gestiune ori degradate,
#:   neimputabile, precum și taxa pe valoarea adăugată aferentă, dacă aceasta este datorată potrivit prevederilor titlului VII”;
#:   OPANAF 206/2025, instrucțiunile D101 (`anaf_surse/opanaf_206_2025_d101.txt`:693–699): „Rândul 33 se completează cu sumele reprezentând
#:   alte cheltuieli nedeductibile, cum sunt: [...] cheltuielile prevăzute la art. 25 alin. (4) din Legea nr. 227/2015 [...], cu excepţia
#:   celor menţionate la lit. a), b), e) şi i)” — lit.c nu e exceptată, deci rândul 33.
RAND_LIPSA_NEIMPUTABILA = "P33"


def trimestrul(data):
    """Trimestrul (1–4) datei AAAA-LL-ZZ."""
    return (int(str(data)[5:7]) - 1) // 3 + 1


def din_lipsa_neimputabila(cur, schema, data, articol, cheltuiala, tva, inregistrare_id, document=None):
    """Ajustarea automată a lipsei neimputabile: cheltuiala + TVA-ul ajustat (CF art.25 alin.(4) lit.c), pe trimestrul inventarului, legată
    de nota lui (în calcul numai cu nota validată; ștearsă odată cu nota). Întoarce (id, suma, trimestrul)."""
    from core.pdf_util import bani, data_ro
    suma = Decimal(str(cheltuiala)) + Decimal(str(tva or 0))
    trim = trimestrul(data)
    descriere = ("Lipsă neimputabilă la inventarul din %s — %s: cheltuiala %s lei%s (CF art.25 alin.(4) lit.c)" % (
        data_ro(data), articol, bani(cheltuiala), (" + TVA ajustat %s lei" % bani(tva)) if Decimal(str(tva or 0)) else ""))[:500]
    aid = adauga(cur, schema, int(str(data)[:4]), trim, RAND_LIPSA_NEIMPUTABILA, suma, descriere, document, None, inregistrare_id)
    return aid, suma, trim


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
