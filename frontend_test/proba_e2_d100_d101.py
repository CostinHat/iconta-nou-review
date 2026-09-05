# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL C — impozitul pe profit: D100 si D101, hranite de NOTA CONTABILA.

De ce sunt un lot: sunt singurele doua declaratii din cele noua cu **nucleu ZERO** — nicio ruta nu
scrie intr-un tabel care sa fie numai al lor. Se hranesc exclusiv prin periferie, adica prin
`inregistrari` / `inregistrari_linii`: **nota contabila**. Lantul lor e deci de alta forma decat al
loturilor A si B, si are un pas pe care celelalte nu-l au — VALIDAREA notei.

ASTEPTAREA, SCRISA INAINTE, cu formula citita din generator (nu din memorie):

  D101 (`core/d101.pull`, l.442):
    P1 = SUM(l.suma) unde `cont_credit LIKE '7%' AND NOT LIKE '76%'`   (venituri din exploatare)
    P2 = SUM(l.suma) unde `cont_debit  LIKE '6%' AND NOT LIKE '66%'`   (cheltuieli de exploatare)
    P3 = P1 - P2 · P7 = P3 + P6            (`calcul_d101`, l.248-254)
  D100 (`core/d100.pull`, l.299 + `deriva_obligatii`, l.322):
    venituri   = SUM unde `cont_credit LIKE '70%'`
    cheltuieli = SUM unde `cont_debit  LIKE '6%'`
    regim profit -> obligatia `103`, cu baza = venituri - cheltuieli

  **SI CONDITIA CARE NU EXISTA IN CELELALTE LOTURI**: amandoua citesc numai note cu
  `i.status = 'validata'`. O nota CIORNA nu are voie sa miste niciun rand — iar asta se probeaza
  explicit, generand INTRE creare si validare. *E singurul pas al lantului care poate esua tacut:
  o ciorna numarata ar umfla impozitul unei firme fara ca nimeni sa fi validat ceva.*

CELE PATRU MOMENTE ale probei, in ordine:
  0. baza — ce e in declaratii inainte de orice
  1. nota de VENIT creata (ciorna)      -> declaratiile NU se misca
  2. nota validata                       -> P1/P3/P7 si venituri/103 se misca EXACT cu suma ei
  3. nota de CHELTUIALA creata + validata-> P2 si cheltuielile se misca, impozitul SCADE

SCENARIUL: «Distributie Profit IC SRL» (`tenant_004`), regim **profit**. D100 pe trimestrul in care
cade data notelor; D101 pe anul lor. Firma e aleasa fiindca e pe profit si **nu poarta niciun
scenariu de supervizor** — spre deosebire de `tenant_005` si `tenant_014`, unde constatarile rosii
sunt puse deliberat si nu se ating.
"""
import json
import os
import re
import sys
from decimal import Decimal

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Distributie Profit IC SRL"
AN, LUNA, TRIM = 2026, 8, 3
DATA = "%d-%02d-21" % (AN, LUNA)
MARCA = "PROBA-E2-C"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_d100_d101.json"

VENIT = Decimal("10000")      # 4111 = 704 — venit din exploatare (cont 70x: intra si in D100)
CHELT = Decimal("4000")       # 6021 = 401 — cheltuiala de exploatare
# conturile sunt luate DIN PLANUL FIRMEI, nu inventate: `704 Venituri din servicii prestate` si
# `6021 Cheltuieli cu materialele auxiliare` exista in `tenant_004.plan_conturi`.
CONT_VENIT, CONT_CHELT = "704", "6021"
# contul PLAUZIBIL dar inexistent, cu care s-a gasit R163: seamana cu 701/704/705, deci
# `cont_valid.apropiate` intoarce vecini — chiar ramura care cadea cu 500.
CONT_INEXISTENT = "7015"
COTA_PROFIT = Decimal("16")   # `d101.COTA_STANDARD`

# elementul e `<obligatie ...>`, cu litera MICA. Prima forma il cauta cu majuscula, gasea zero
# obligatii si raporta `suma_dat = 0` pentru o declaratie care scria 960 — un DEFECT FALS pe o
# aplicatie corecta. De-aia verificarea de mai jos cere si ca obligatia sa FIE GASITA.
_OBLIG = re.compile(r"<obligatie\b([^>]*)/>", re.I)
_ATR = re.compile(r'(\w+)="([^"]*)"')


def obligatii(xml):
    return [dict(_ATR.findall(m.group(1))) for m in _OBLIG.finditer(xml)]


def main():
    tok, tid, _schema = U.context(FIRMA)
    jurnal = {"firma": FIRMA, "tenant_id": tid,
              "perioada": {"an": AN, "luna": LUNA, "trim": TRIM}, "pasi": []}
    rele = []

    def pas(nume, **kw):
        jurnal["pasi"].append(dict(nume=nume, **kw))
        print("· %-44s %s" % (nume, json.dumps(kw, ensure_ascii=False, default=str)[:150]))

    def nepotrivit(ce, vrut, avut):
        rele.append((ce, vrut, avut))
        print("   NEPOTRIVIT %-38s asteptat %-12s obtinut %s" % (ce, vrut, avut))

    def citeste():
        """(P-urile D101, obligatiile D100) — o singura generare a fiecareia."""
        st1, r1 = U.cere("POST", "/declaratii/d101", {"tenant_id": tid, "an": AN}, tok)
        p = U.randuri_xml(r1["xml"].split("?>", 1)[-1]) if st1 == 200 else {}
        # D100 se cere pe TRIMESTRU pentru firma asta — ruta o spune pe litere: «firma depune
        # d100 TRIMESTRIAL: trimite trimestrul (1-4), nu luna». Prima forma trimitea luna.
        st0, r0 = U.cere("POST", "/declaratii/d100",
                         {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
        o = obligatii(r0["xml"]) if st0 == 200 else []
        return (st1, p), (st0, o, (r0 if st0 != 200 else None))

    def o103(obl):
        for o in obl:
            if o.get("cod_oblig") == "103":
                return o
        return {}

    def verifica_d100(obl, p, cand):
        """D100 confruntat cu D101 — GENERATOR contra GENERATOR, nu cu o deltă.

        O verificare pe deltă trece ÎN GOL la a doua rulare (0 == 0) — exact ce s-a întâmplat
        prima dată, și ce era să transforme un parser greșit al meu într-un „defect" al
        aplicației. Aici se cere ca impozitul din D100 să fie 16% din rezultatul pe care îl
        calculează CELĂLALT generator (D101) — plus ca obligația să EXISTE în declarație.

        PRECONDIȚIA, verificată explicit: firma n-are venituri/cheltuieli FINANCIARE în perioadă
        (P4 = P5 = 0). Altfel baza D100 (`70%` credit, `6%` debit) și rezultatul D101 (`7%` fără
        `76%`, `6%` fără `66%`) n-ar mai fi același număr, iar egalitatea ar fi falsă fără ca
        aplicația să greșească."""
        o = o103(obl)
        if not o:
            nepotrivit("D100 %s: obligatia 103 lipseste din declaratie" % cand,
                       "prezenta", [x.get("cod_oblig") for x in obl] or "nicio obligatie")
            return
        if (U.numar(p.get("P4", "0")) or 0) or (U.numar(p.get("P5", "0")) or 0):
            pas("D100 %s: NEVERIFICAT — firma are rezultat financiar, bazele diferă legitim"
                % cand, P4=p.get("P4"), P5=p.get("P5"))
            return
        rez = (U.numar(p.get("P1", "0")) or 0) - (U.numar(p.get("P2", "0")) or 0)
        vrut = int(Decimal(rez) * COTA_PROFIT / 100)
        avut = U.numar(o.get("suma_dat", "0")) or 0
        if avut != vrut:
            nepotrivit("D100 %s: suma_dat 103 = 16%% din rezultatul D101 (%s)" % (cand, rez),
                       vrut, avut)
        else:
            pas("D100 %s: impozitul = 16%% din rezultatul calculat de D101" % cand,
                rezultat_d101=rez, suma_dat=avut)

    # ── 0. BAZA, si daca notele probei sunt deja acolo
    st, jl = U.cere("GET", "/tenants/%d/jurnal?an=%d&luna=%d" % (tid, AN, LUNA), None, tok)
    _note = (jl or {}).get("note") or (jl or {}).get("inregistrari") or []
    _ale_mele = [x for x in _note if MARCA in str(x.get("descriere") or "")]
    adaug = not _ale_mele
    # DE CE: notele sunt fapte reale, nu santinele care se sterg. A doua rulare ar mai adauga un
    # set, iar scenariul declarat s-ar dubla tacut — `DECIZII.md` 65.
    (st1, p0), (st0, o0, err0) = citeste()
    jurnal["baza"] = {"d101": {k: v for k, v in p0.items() if k.startswith("P")},
                      "d100": o0, "d100_eroare": err0}
    b_p1, b_p2 = U.numar(p0.get("P1", "0")) or 0, U.numar(p0.get("P2", "0")) or 0
    b_p3, b_p7 = U.numar(p0.get("P3", "0")) or 0, U.numar(p0.get("P7", "0")) or 0
    b_dat = U.numar(o103(o0).get("suma_dat", "0")) or 0
    pas("baza", d101_P1=b_p1, d101_P2=b_p2, d101_P3=b_p3, d101_P7=b_p7,
        d100_103_suma_dat=b_dat, d100_cod=st0,
        note_ale_probei_deja_prezente=[x.get("id") for x in _ale_mele])
    if not adaug:
        pas("intrarile sunt deja in evidenta dintr-o rulare anterioara — se VERIFICA starea, "
            "nu se mai adauga", note=[x.get("id") for x in _ale_mele])

    pas("ASTEPTARE 1: nota CIORNA nu misca nimic — nici P1, nici obligatia 103")
    pas("ASTEPTARE 2: dupa VALIDARE, P1 += %s · P3 += %s · P7 += %s · suma_dat 103 += %s"
        % (VENIT, VENIT, VENIT, int(VENIT * COTA_PROFIT / 100)))
    pas("ASTEPTARE 3: dupa nota de cheltuiala validata, P2 += %s · P3 -= %s · "
        "suma_dat 103 -= %s" % (CHELT, CHELT, int(CHELT * COTA_PROFIT / 100)))

    # ── 0b. REPROBAREA lui R163: un cont PLAUZIBIL dar inexistent primeste un REFUZ, nu un 500
    st, r = U.cere("POST", "/tenants/%d/jurnal" % tid, {
        "descriere": MARCA + " cont plauzibil inexistent",
        "data": DATA,
        "linii": [{"debit": "4111", "credit": CONT_INEXISTENT, "suma": float(VENIT)}],
    }, tok)
    txt = json.dumps(r, ensure_ascii=False, default=str)
    pas("0b — cont %s (plauzibil, inexistent): refuz, nu 500" % CONT_INEXISTENT,
        cod=st, raspuns=txt[:260])
    if st >= 500:
        nepotrivit("cont plauzibil inexistent -> cod HTTP", "<500 (refuz)", st)
    elif CONT_INEXISTENT not in txt or "apropiate" not in txt.lower():
        nepotrivit("refuzul numeste contul si conturile apropiate", "da", txt[:120])
    else:
        pas("R163 reprobat: refuzul numeste contul, campul si vecinii lui")

    # ── 1. NOTA DE VENIT, ca CIORNA
    st, r = (U.cere("POST", "/tenants/%d/jurnal" % tid, {
        "descriere": MARCA + " venit din exploatare",
        "data": DATA,
        "linii": [{"debit": "4111", "credit": CONT_VENIT, "suma": float(VENIT)}],
    }, tok) if adaug else (0, {"id": None, "sarit": "nota exista deja"}))
    pas("intrare 1 — nota de venit, creata (ciorna)", cod=st, raspuns=r)
    nota_v = (r or {}).get("id") or ((r or {}).get("nota") or {}).get("id")

    (st1, p1), (st0, o1, _e) = citeste()
    if (U.numar(p1.get("P1", "0")) or 0) != b_p1:
        nepotrivit("P1 dupa CIORNA (nu trebuia sa se miste)", b_p1, U.numar(p1.get("P1", "0")))
    elif (U.numar(o103(o1).get("suma_dat", "0")) or 0) != b_dat:
        nepotrivit("suma_dat 103 dupa CIORNA", b_dat, U.numar(o103(o1).get("suma_dat", "0")))
    else:
        pas("CIORNA nu misca declaratiile — corect", P1=U.numar(p1.get("P1", "0")),
            suma_dat=U.numar(o103(o1).get("suma_dat", "0")))

    # ── 2. VALIDAREA notei
    st, r = (U.cere("POST", "/tenants/%d/jurnal/%s/valideaza" % (tid, nota_v), {}, tok)
             if adaug else (0, {"sarit": "deja validata"}))
    pas("intrare 2 — nota de venit, VALIDATA", cod=st, raspuns=r)

    (st1, p2), (st0, o2, _e) = citeste()
    jurnal["dupa_venit"] = {"d101": {k: v for k, v in p2.items() if k.startswith("P")},
                            "d100": o2}
    dV = int(VENIT) if adaug else 0
    for camp, vrut in (("P1", b_p1 + dV), ("P3", b_p3 + dV), ("P7", b_p7 + dV)):
        avut = U.numar(p2.get(camp, "0")) or 0
        if avut != vrut:
            nepotrivit("D101 %s dupa venit validat" % camp, vrut, avut)
    verifica_d100(o2, p2, "dupa venit")

    # ── 3. NOTA DE CHELTUIALA, creata si validata
    st, r = (U.cere("POST", "/tenants/%d/jurnal" % tid, {
        "descriere": MARCA + " cheltuiala de exploatare",
        "data": DATA,
        "linii": [{"debit": CONT_CHELT, "credit": "401", "suma": float(CHELT)}],
    }, tok) if adaug else (0, {"id": None, "sarit": "nota exista deja"}))
    nota_c = (r or {}).get("id") or ((r or {}).get("nota") or {}).get("id")
    pas("intrare 3 — nota de cheltuiala, creata", cod=st, raspuns=r)
    st, r = (U.cere("POST", "/tenants/%d/jurnal/%s/valideaza" % (tid, nota_c), {}, tok)
             if adaug else (0, {"sarit": "deja validata"}))
    pas("intrare 3b — nota de cheltuiala, VALIDATA", cod=st, raspuns=r)

    (st1, p3), (st0, o3, _e) = citeste()
    jurnal["dupa_cheltuiala"] = {"d101": {k: v for k, v in p3.items() if k.startswith("P")},
                                 "d100": o3}
    dC = int(CHELT) if adaug else 0
    for camp, vrut in (("P1", b_p1 + dV), ("P2", b_p2 + dC),
                       ("P3", b_p3 + dV - dC), ("P7", b_p7 + dV - dC)):
        avut = U.numar(p3.get(camp, "0")) or 0
        if avut != vrut:
            nepotrivit("D101 %s dupa cheltuiala validata" % camp, vrut, avut)
    verifica_d100(o3, p3, "dupa cheltuiala")

    # ── 4. DUK pe amandoua
    for tip, corp in (("d101", {"tenant_id": tid, "an": AN}),
                      ("d100", {"tenant_id": tid, "an": AN, "trim": TRIM})):
        st, rv = U.cere("POST", "/declaratii/%s/valideaza" % tip, corp, tok, timeout=300)
        jurnal.setdefault("duk", {})[tip] = {"cod": st, "stare": (rv or {}).get("stare"),
                                             "erori": (rv or {}).get("erori")}
        print("DUK %s: %s" % (tip, json.dumps(jurnal["duk"][tip], ensure_ascii=False)[:220]))

    jurnal["nepotriviri"] = rele
    jurnal["note_lasate"] = {"venit": nota_v, "cheltuiala": nota_c}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(jurnal, f, ensure_ascii=False, indent=1, default=str)
    print("\nCONFRUNTARE LOT C: %d nepotriviri . artefact: %s"
          % (len(rele), os.path.basename(OUT)))
    return 1 if rele else 0


if __name__ == "__main__":
    raise SystemExit(main())
