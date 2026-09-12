# -*- coding: utf-8 -*-
"""Clasificarea P6, cu contabilitate inchisa mecanic.

Tabelul de mai jos e singura parte MANUALA a diagnosticului, si e manuala din motivul scris in
`scan_stare_proces`: «business / autoritativa» nu se poate citi din AST. Restul — populatia,
caile, exclusiile — vine din detector.

Ca sa nu poata imbatrani tacut, fisierul asta NU e o lista alaturata detectorului: el se
CONFRUNTA cu detectorul la fiecare rulare. Un nume mutabil nou, neclasificat, opreste programul;
un nume clasificat care nu mai e mutabil, la fel.

CELE DOUA TABELE, si de ce sunt doua.

`TABEL` priveste numele din cod, si se confrunta cu AST-ul. `TABEL_INFRA` priveste ce nu se vede
in niciun AST: **cate procese servesc**. Textul canonic cere amandoua — `PLAN_HARDENING.md:709-711`
spune literal «Include infrastructura, nu doar codul». Fara al doilea tabel, `P6_ACTION_REQUIRED`
ar ajunge la zero dupa valul 2 si s-ar citi ca «P6 gata», desi partea cea mai grea a etapei —
trecerea la mai multe instante — n-ar fi inceputa. *O cifra care atinge zero cat timp etapa e
deschisa e o cifra care minte.*
"""
import collections
import sys

sys.path.insert(0, "/home/costin/iconta_nou/scripts")
sys.path.insert(0, "/home/costin/iconta_nou")
import scan_stare_proces as S  # noqa: E402

AR, ABD, FP = "ACTION_REQUIRED", "ACCEPTABLE_BY_DESIGN", "FALSE_POSITIVE"
V = collections.namedtuple("V", "categorie fel regula de_ce")

#: Cele CINCI lucruri cerute de PLAN_HARDENING.md:704-707 pentru un cache admis.
CINCI = ("rol", "sursa", "motiv", "invalidare", "dovada")

#: Regula care accepta un cache DUPA valul 2. Nu e o tolerare: e conditionata, iar conditia e
#: verificata mecanic de `core/test_cache_declarat.py` — cele cinci campuri exista si sunt pline,
#: iar testul numit in `dovada` EXISTA cu adevarat si goleste chiar cache-ul acela.
REGULA_DECLARAT = ("PLAN_HARDENING.md:704-707 — cache local admis, DECLARAT cu cele cinci lucruri, "
                   "cu declaratia verificata structural si dovada de reconstructie rulata")

TABEL = {
    # ---------------------------------------------------------------- CACHE DECLARAT (valul 2)
    ("core.ajutor", "_CACHE"): V(
        ABD, "declarat", REGULA_DECLARAT,
        "Cache al `FUNCTIONALITATI.csv`, fisier versionat. EXCEPTIA NU GOLESTE DETECTORUL: "
        "detectorul l-a gasit si l-a numit (S1), iar regula il accepta numai fiindca "
        "`_CACHE_DECLARATIE` exista, are toate cinci campurile si trimite la o proba care chiar "
        "goleste cache-ul si compara raspunsul."),
    ("core.raportari_ai", "_BAZA"): V(
        ABD, "declarat", REGULA_DECLARAT,
        "Acelasi CSV versionat, filtrat pe LIVE. Aceeasi conditie, verificata la fel."),
    ("core.d112", "_ENUM_XSD_CACHE"): V(
        ABD, "declarat", REGULA_DECLARAT,
        "Enumerarile din XSD-ul D112. Sursa e un artefact ADUS, cu amprenta in registrul de "
        "provenienta; un XSD nou intra ca FISIER NOU, deci cheia veche nu-si poate schimba "
        "raspunsul sub cache."),
    ("core.scadente", "_cache_sarb"): V(
        ABD, "declarat", REGULA_DECLARAT,
        "Memo pe o functie PURA, marginit prin `_AN_MIN`/`_AN_MAX` la cel mult 76 de chei. "
        "«Invalidare: niciodata» e aici un raspuns, nu o lipsa — si e scris ca atare."),
    ("core.curs_bnr", "_PREDARE"): V(
        ABD, "declarat", REGULA_DECLARAT,
        "Predarea de la `asigura_cursul` la `curs_pentru`. La valul 2 a primit chiar lucrul care "
        "ii lipsea: o INVALIDARE — termen de 60 s plus plafon de 256 de chei. Erau doua "
        "dictionare cheiate identic (`_ULTIMA_EROARE`, `_COTATE`); contopite, fiindca erau un "
        "singur lucru tinut in doua locuri. Nu e cache-ul CURSULUI: acela e in baza si ramane "
        "singura sursa a deciziei."),
    ("core.firma_rezumat", "_SANATATE"): V(
        ABD, "declarat", REGULA_DECLARAT,
        "Instantaneul de drift, rescris integral la fiecare rulare a buclei de 5 minute. "
        "DIVERGE intre procese, si asta e declarat: cu N instante, `/admin/sanatate` raspunde din "
        "cea care serveste. Nu e stare autoritativa — autoritatea e catalogul PostgreSQL, si el e "
        "unul singur —, deci raspunsurile difera prin VECHIME, nu prin adevar."),
    ("main", "_TENANT_TEMPLATE"): V(
        ABD, "declarat", REGULA_DECLARAT,
        "Sablonul SQL citit o data la pornire. Identic pe orice numar de instante, fiindca toate "
        "pornesc din acelasi commit."),

    # ---------------------------------------------------------------- RESURSE DE PROCES
    ("core.db", "_pool"): V(
        ABD, "resursa", "PLAN_HARDENING.md:697 — cerinta priveste starea BUSINESS",
        "Un pool de conexiuni e o resursa a procesului prin definitie; nu poarta nicio decizie de "
        "business si nu poate fi partajat intre procese. EXCEPTIA NU GOLESTE DETECTORUL: "
        "detectorul l-a GASIT si l-a numit (S1, doua cai, `init_pool`/`inchide_pool`) — regula il "
        "accepta dupa ce a fost vazut, nu il ascunde de masuratoare."),
    ("core.firma_rezumat", "_LOG"): V(
        ABD, "resursa", "PLAN_HARDENING.md:697 — cerinta priveste starea BUSINESS",
        "Logger memoizat lenes. Valoarea lui nu intra in nicio decizie; doua procese cu doua "
        "obiecte de log se comporta identic."),
    ("core.pdf_fonturi", "_INIT"): V(
        ABD, "resursa", "PLAN_HARDENING.md:697 — cerinta priveste starea BUSINESS",
        "Flag de initializare idempotenta a fonturilor reportlab — o resursa care TREBUIE "
        "inregistrata o data in fiecare proces. Partajarea lui ar fi gresita, nu utila."),
    ("core.versiune", "RUNNING_COMMIT"): V(
        ABD, "resursa", "PLAN_HARDENING.md:718-720 — intra in criteriile de acceptare, nu in cod",
        "E chiar «ce cod poarta ACEST proces», deci trebuie sa fie per proces. Textul canonic nu "
        "cere sa fie mutat, cere ca bratul four-way sa fie redefinit din «procesul viu poarta "
        "HEAD» in «TOATE procesele poarta HEAD» — o schimbare in POARTA, si ea e la valul 3."),
    ("main", "_TASKURI_FUNDAL_PORNITE"): V(
        ABD, "resursa", "PLAN_HARDENING.md:697 — cerinta priveste starea BUSINESS",
        "Contor de observabilitate, scris o data in `lifespan` si citit de o proba care verifica "
        "ordinea pornirii. Nu poarta decizie. *Faptul pe care il numara* — ca fiecare proces isi "
        "porneste propriile bucle — e datorie de INFRASTRUCTURA, si e in `TABEL_INFRA`, nu aici."),
}

#: Ce nu se vede in niciun AST. Fiecare intrare are o stare si o proba care o va inchide.
I = collections.namedtuple("I", "stare cerinta de_ce inchis_de")
TABEL_INFRA = {
    "un_singur_proces": I(
        AR,
        "PLAN_HARDENING.md:709-711 — «Include infrastructura, nu doar codul»: trecerea de la un "
        "singur proces la mai multe instante",
        "`ExecStart` e fara `--workers` si serveste un singur PID. Cat timp e asa, criteriile "
        "canonice de acceptare (doua instante identice · fault-check cu o instanta oprita in "
        "timpul unei cereri · four-way redefinit la «TOATE procesele poarta HEAD») nu se pot "
        "indeplini, oricat de curat ar fi codul. Valul 1 si valul 2 sunt PRECONDITIILE ei: "
        "pornirea multi-proces peste starea din memorie ar fi activat chiar defectele inchise.",
        "valul 3"),
}


def numaratori():
    """Cifrele, intr-un singur loc, ca raportul sa nu le recalculeze cu alta definitie."""
    inv = S.inventar()
    mutabile = set(inv["nume_mutabile"])
    clasificate = set(TABEL)
    scanate = len({(m, n) for m, _c, n, _l in inv["raw"]})
    pe_cat = collections.Counter(TABEL[x].categorie for x in mutabile & clasificate)
    infra_ar = sum(1 for x in TABEL_INFRA.values() if x.stare == AR)
    return {
        "P6_SCANNED_NAMES": scanate,
        "P6_EXCLUDED_E4_IMMUTABLE": inv["excluse"]["P6_EXCLUDED_E4_IMMUTABLE"],
        "P6_RAW_ITEMS": len(mutabile),
        "P6_RAW_PATHS": len(inv["cai"]),
        "P6_CLASSIFIED_ITEMS": len(mutabile & clasificate),
        "P6_ACTION_REQUIRED": pe_cat.get(AR, 0),
        "P6_ACCEPTABLE_BY_DESIGN": pe_cat.get(ABD, 0),
        "P6_FALSE_POSITIVES": pe_cat.get(FP, 0),
        "P6_UNCLASSIFIED_ITEMS": len(mutabile - clasificate),
        "P6_CLASIFICARI_FARA_OBIECT": len(clasificate - mutabile),
        "P6_INFRA_ACTION_REQUIRED": infra_ar,
        "neclasificate": sorted(mutabile - clasificate),
        "fantoma": sorted(clasificate - mutabile),
    }


def main():
    n = numaratori()
    print("CONTABILITATE P6 — COD")
    print("  P6_SCANNED_NAMES         : %d   (populatia parcursa, nu unitatea)" % n["P6_SCANNED_NAMES"])
    print("  P6_EXCLUDED_E4_IMMUTABLE : %d   (legate o data, niciodata schimbate)"
          % n["P6_EXCLUDED_E4_IMMUTABLE"])
    print("  P6_RAW_ITEMS             : %d   <- UNITATEA: se schimba la rulare" % n["P6_RAW_ITEMS"])
    print("  P6_RAW_PATHS             : %d   (locuri de mutatie)" % n["P6_RAW_PATHS"])
    print("  P6_CLASSIFIED_ITEMS      : %d" % n["P6_CLASSIFIED_ITEMS"])
    print("  P6_UNCLASSIFIED_ITEMS    : %d" % n["P6_UNCLASSIFIED_ITEMS"])
    print("  clasificari fara obiect  : %d" % n["P6_CLASIFICARI_FARA_OBIECT"])
    for m, x in n["neclasificate"]:
        print("    NECLASIFICAT: %s::%s" % (m, x))
    for m, x in n["fantoma"]:
        print("    FANTOMA:      %s::%s" % (m, x))
    assert n["P6_SCANNED_NAMES"] == n["P6_EXCLUDED_E4_IMMUTABLE"] + n["P6_RAW_ITEMS"], (
        "contabilitatea nu inchide")
    print()
    for k in ("P6_ACTION_REQUIRED", "P6_ACCEPTABLE_BY_DESIGN", "P6_FALSE_POSITIVES"):
        print("  %-26s %d" % (k, n[k]))
    pe_fel = collections.Counter(TABEL[x].fel for x in set(S.inventar()["nume_mutabile"]) & set(TABEL))
    print("    din care: %s" % dict(pe_fel))
    print()
    print("CONTABILITATE P6 — INFRASTRUCTURA (ce nu se vede in AST)")
    print("  P6_INFRA_ACTION_REQUIRED : %d" % n["P6_INFRA_ACTION_REQUIRED"])
    for k, x in sorted(TABEL_INFRA.items()):
        print("    [%s] %s  -> se inchide la %s" % (x.stare, k, x.inchis_de))
    print()
    print("  P6_STATUS = %s" % ("OPEN" if (n["P6_ACTION_REQUIRED"] or n["P6_INFRA_ACTION_REQUIRED"])
                                else "CANDIDATE_FOR_CLOSE"))
    return 2 if (n["neclasificate"] or n["fantoma"]) else 0


if __name__ == "__main__":
    sys.exit(main())
