# -*- coding: utf-8 -*-
"""Clasificarea P6, cu contabilitate inchisa mecanic.

Tabelul de mai jos e singura parte MANUALA a diagnosticului, si e manuala din motivul scris in
`scan_stare_proces`: «business / autoritativa» nu se poate citi din AST. Restul — populatia,
caile, exclusiile — vine din detector.

Ca sa nu poata imbatrani tacut, fisierul asta NU e o lista alaturata detectorului: el se
CONFRUNTA cu detectorul la fiecare rulare. Un nume mutabil nou, neclasificat, opreste programul;
un nume clasificat care nu mai e mutabil, la fel. Asta e diferenta dintre o clasificare si o
amintire despre o clasificare.

Cele trei categorii sunt cele cerute de comanda. `fel` spune CE fel de actiune cere un
ACTION_REQUIRED — nu e o a patra categorie, e un atribut al celei existente:
  `muta`     starea trebuie sa iasa din memoria procesului (sursa autoritativa in afara lui);
  `declara`  cache admis de textul canonic, dar caruia ii lipsesc din cele CINCI lucruri cerute.
"""
import collections
import sys

sys.path.insert(0, "/home/costin/iconta_nou/scripts")
sys.path.insert(0, "/home/costin/iconta_nou")
import scan_stare_proces as S  # noqa: E402

AR, ABD, FP = "ACTION_REQUIRED", "ACCEPTABLE_BY_DESIGN", "FALSE_POSITIVE"
V = collections.namedtuple("V", "categorie fel regula de_ce")

#: Cele CINCI lucruri cerute de PLAN_HARDENING.md:704-707 pentru un cache admis.
CINCI = ("rol", "sursa_autoritativa", "motiv", "invalidare", "dovada_reconstructie")

TABEL = {
    # ---------------------------------------------------------------- ACTION_REQUIRED / muta
    ("main", "_login_fail"): V(
        AR, "muta",
        "PLAN_HARDENING.md:699-701 — numit EXPLICIT ca stare business",
        "Blocarea contului dupa 5 esecuri e o decizie de securitate luata pe o cifra care traieste "
        "doar aici. Masurat: doua procese diverg (A blocat, B neblocat), iar sub concurenta "
        "sustinuta 86% din esecuri se pierd la k=10 — `_login_blocat` citeste-filtreaza-SCRIE "
        "peste dictionar si inlocuieste lista pe care `_login_esec` tocmai a crescut-o."),
    ("main", "_alerte_ultima_trimitere"): V(
        AR, "muta",
        "PLAN_HARDENING.md:699-701 — numit EXPLICIT ca stare business",
        "Cooldown-ul de 3600 s decide DACA se trimite o alerta. Cu N procese, fiecare isi tine "
        "propriul ultim-trimis, deci pragul se aplica de N ori: aceeasi alerta pleaca de N ori. "
        "Criteriul canonic cere literal «cooldown-ul alertelor nu trimite dublu»."),
    ("core.curs_bnr", "_ULTIMA_EROARE"): V(
        AR, "declara",
        "PLAN_HARDENING.md:704-707 — cache admis numai DECLARAT",
        "Poarta intre cereri ce a aflat o descarcare BNR, si alimenteaza mesajul de refuz pe care "
        "il vede utilizatorul. Scris pe o cale (`asigura_cursul` ajunge la retea), citit pe alta "
        "(`curs_pentru`), niciodata golit, nemarginit. L-am introdus eu in valul 3 P5 ca sa pastrez "
        "mesajele de refuz identice — deci e datorie proprie, nu mostenita."),
    ("core.curs_bnr", "_COTATE"): V(
        AR, "declara",
        "PLAN_HARDENING.md:704-707 — cache admis numai DECLARAT",
        "Aceeasi pereche si aceeasi origine ca `_ULTIMA_EROARE`."),
    ("core.ajutor", "_CACHE"): V(
        AR, "declara",
        "PLAN_HARDENING.md:704-707 — cache admis numai DECLARAT",
        "Cache al `FUNCTIONALITATI.csv`, fisier din repo. Are rol, sursa si motiv scrise in "
        "docstring si spune «invalidat la restart»; ii lipseste a cincea — nicio proba nu goleste "
        "cache-ul ca sa arate ca raspunsul reconstruit e identic."),
    ("core.raportari_ai", "_BAZA"): V(
        AR, "declara",
        "PLAN_HARDENING.md:704-707 — cache admis numai DECLARAT",
        "Cache al aceluiasi CSV, filtrat pe LIVE. Aceeasi lipsa: fara dovada de reconstructie."),
    ("core.d112", "_ENUM_XSD_CACHE"): V(
        AR, "declara",
        "PLAN_HARDENING.md:704-707 — cache admis numai DECLARAT",
        "Cache al enumerarilor din `anaf_surse/d112_06082026.xsd`. Sursa e in repo si nu se schimba "
        "la rulare, deci reconstructia E identica — dar asta e o afirmatie, si n-are proba."),
    ("core.scadente", "_cache_sarb"): V(
        AR, "declara",
        "PLAN_HARDENING.md:704-707 — cache admis numai DECLARAT",
        "Memo pur pe an: `sarbatori_legale(an)` e o functie deterministica, marginita la 2024-2099, "
        "deci cel mult 76 de chei. Cel mai curat cache din casa — si tot fara a cincea."),
    ("core.firma_rezumat", "_SANATATE"): V(
        AR, "declara",
        "PLAN_HARDENING.md:704-707 — cache admis numai DECLARAT",
        "Instantaneul de drift, scris de bucla de 5 minute si citit de `/admin/sanatate`. Cu N "
        "procese sunt N instantanee, iar ecranul raspunde din cel care se nimereste sa serveasca: "
        "acelasi URL, doua adevaruri, fara ca vreunul sa minta."),
    ("main", "_TENANT_TEMPLATE"): V(
        AR, "declara",
        "PLAN_HARDENING.md:704-707 — cache admis numai DECLARAT",
        "Sablonul SQL citit o data din `tenant_template.sql`. Identic pe orice proces, deci "
        "inofensiv la scalare; intra pentru ca regula canonica nu cere sa fie periculos, cere sa "
        "fie declarat."),

    # ---------------------------------------------------------------- ACCEPTABLE_BY_DESIGN
    ("core.db", "_pool"): V(
        ABD, None,
        "PLAN_HARDENING.md:697 — cerinta priveste starea BUSINESS",
        "Un pool de conexiuni e o resursa a procesului prin definitie; nu poarta nicio decizie de "
        "business si nu poate fi partajat intre procese. EXCEPTIA NU GOLESTE DETECTORUL: detectorul "
        "l-a GASIT si l-a numit (S1, doua cai, `init_pool`/`inchide_pool`) — regula il accepta dupa "
        "ce a fost vazut, nu il ascunde de masuratoare."),
    ("core.firma_rezumat", "_LOG"): V(
        ABD, None,
        "PLAN_HARDENING.md:697 — cerinta priveste starea BUSINESS",
        "Logger memoizat lenes. Valoarea lui nu intra in nicio decizie; doua procese cu doua "
        "obiecte de log se comporta identic."),
    ("core.pdf_fonturi", "_INIT"): V(
        ABD, None,
        "PLAN_HARDENING.md:697 — cerinta priveste starea BUSINESS",
        "Flag de initializare idempotenta a fonturilor reportlab — o resursa care TREBUIE "
        "inregistrata o data in fiecare proces. Partajarea lui ar fi gresita, nu utila."),
    ("core.versiune", "RUNNING_COMMIT"): V(
        ABD, None,
        "PLAN_HARDENING.md:718-720 — intra in criteriile de acceptare, nu in remediere",
        "E chiar «ce cod poarta ACEST proces», deci trebuie sa fie per proces. Textul canonic nu "
        "cere sa fie mutat, cere ca bratul four-way sa fie redefinit din «procesul viu poarta HEAD» "
        "in «TOATE procesele poarta HEAD» — o schimbare in POARTA, nu in cod."),
    ("main", "_TASKURI_FUNDAL_PORNITE"): V(
        ABD, None,
        "PLAN_HARDENING.md:697 — cerinta priveste starea BUSINESS",
        "Contor de observabilitate, scris o data in `lifespan` si citit de o proba care verifica "
        "ordinea pornirii. Nu poarta decizie. *Dar faptul pe care il numara e o constatare de "
        "infrastructura, raportata separat:* cu `--workers N` ar porni N bucle de alerte."),
}


def main():
    inv = S.inventar()
    mutabile = set(inv["nume_mutabile"])
    clasificate = set(TABEL)

    neclasificate = sorted(mutabile - clasificate)
    fantoma = sorted(clasificate - mutabile)

    print("CONTABILITATE P6")
    print("  P6_RAW_ITEMS (nume la nivel de modul, in proces) : %d"
          % len({(m, n) for m, _c, n, _l in inv["raw"]}))
    print("    din care E4 legat-dar-neschimbat               : %d" % inv["excluse"]["E4_legat_dar_neschimbat"])
    print("    din care MUTABILE la rulare  <- unitatea       : %d" % len(mutabile))
    print("  P6_RAW_PATHS                                     : %d" % len(inv["cai"]))
    print("  P6_CLASSIFIED_ITEMS                              : %d" % len(mutabile & clasificate))
    print("  P6_UNCLASSIFIED_ITEMS                            : %d" % len(neclasificate))
    print("  clasificari fara obiect (fantoma)                : %d" % len(fantoma))
    for m, n in neclasificate:
        print("    NECLASIFICAT: %s::%s" % (m, n))
    for m, n in fantoma:
        print("    FANTOMA:      %s::%s" % (m, n))

    pe_cat = collections.Counter(TABEL[x].categorie for x in sorted(mutabile & clasificate))
    print()
    for cat in (AR, ABD, FP):
        print("  %-22s %d" % (cat, pe_cat.get(cat, 0)))
    pe_fel = collections.Counter(TABEL[x].fel for x in mutabile & clasificate
                                 if TABEL[x].categorie == AR)
    print("    din ACTION_REQUIRED: muta=%d  declara=%d"
          % (pe_fel.get("muta", 0), pe_fel.get("declara", 0)))

    print()
    print("TABELUL, pe categorii")
    for cat in (AR, ABD, FP):
        for m, n in sorted(mutabile & clasificate):
            v = TABEL[(m, n)]
            if v.categorie != cat:
                continue
            print("  [%s%s] %s::%s" % (cat, ("/" + v.fel) if v.fel else "", m, n))
            print("        regula: %s" % v.regula)
            print("        de ce : %s" % v.de_ce)

    return 2 if (neclasificate or fantoma) else 0


if __name__ == "__main__":
    sys.exit(main())
