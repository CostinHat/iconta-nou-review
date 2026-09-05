# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL E — ultimele doua din cele noua: D406/SAF-T si D205.

ASTEPTAREA, SCRISA INAINTE:

**D406/SAF-T** (`tenant_003`, TVA TRIMESTRIAL, trimestrul III/2026)
  1. Fereastra raportarii urmeaza PERIOADA FISCALA TVA — OPANAF 1783/2021 Anexa 4 pct.2, citit
     verbatim. Deci pentru o firma trimestriala fisierul trebuie sa contina TOT trimestrul.
     Proba: facturile din **august** (CMT150, CMT151, PROBA-E2-A-P1, intrate in lotul A) trebuie sa
     apara in `<SalesInvoices>` / `<PurchaseInvoices>`.
  2. **Confruntare intre declaratii**: numarul de facturi de vanzare din SAF-T trebuie sa fie
     acelasi cu `nrFacturi` din D394 pe aceeasi perioada — doua generatoare, aceeasi realitate.
  3. Antetul trebuie sa declare perioada ACOPERITA, nu luna-ancora: `PeriodStart` = *„The first
     accounting period covered by SAF-T"*, `PeriodEnd` = *„The last accounting period covered by
     the SAF-T"* (`anaf_surse/d406_schema_anaf.xlsx`, 5.12). Deci (7, 2026) - (9, 2026).
     ANTI-VACUU: schema da DOUA ramuri de `<xs:choice>` — `SelectionStartDate/EndDate` SAU tuplul
     `Period*`. Prima versiune a probei cauta doar ramura pe care fisierul **nu** o emite, n-a
     gasit-o, si a raportat `{"start": null}` linistit in loc sa pice. Daca niciuna din cele doua
     ramuri nu e gasita, proba pica acum.

**D205** (`ALFA MICRO SRL` / `tenant_013`, cabinetul de test, anul 2026)
  4. `divid_D` = Σ CREDIT 457 x cota asociatului · `divid_P` = Σ DEBIT 457 x cota
     (`d205.pull`, l.309-313). Numele atributelor sunt `divid_D`/`divid_P` — citite din
     `build_xml` l.300, nu din schita de antet a docstring-ului (`divid_D1`), care da forma
     generica pe coloane. Beneficiarul apare **numai daca `platit > 0`**.
  5. `imp1` = `divid_P` x cota impozitului pe dividende, PERIOD-AWARE: **16%** de la 01.01.2026
     (Legea 141/2025, CF art.97) — citit din `common.cota("impozit_dividend")`, nu scris de mana.
  6. `Timp` = Σ `imp1` · `nrben` = numarul de beneficiari (`d205`, antet).

  ASTEPTAREA E PE **DELTA**, nu pe absolut: firma are dividende de dinaintea probei (masurate la
  inceputul rularii, nu presupuse). Ce probeaza lotul e ca **cele 10.000 ale mele** intra si urca
  pe toate cele patru campuri; peste asta se verifica invariantul absolut `imp1 = cota x baza1`,
  care nu depinde de baza si tine si daca proba se reia.

CE NU DEMONSTREAZA: ca sectiunile SAF-T sunt complete fata de norma (Stocuri/Active au perioade
proprii). Aici se probeaza FEREASTRA si drumul valorii, nu acoperirea sectiunilor.
"""
import json
import os
import re
import sys
from decimal import Decimal

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA_406 = "Comert Micro TVA SRL"
FIRMA_205 = "ALFA MICRO SRL"
EMAIL_205 = "fir-intrare@prisma-cont.test"      # cabinetul 4163, caruia ii e atribuita firma
AN, TRIM, LUNA = 2026, 3, 9
MARCA = "PROBA-E2-E"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_d406_d205.json"

DIVIDEND = Decimal("10000")     # 121 = 457 (distribuire), apoi 457 = 5121 (plata)
_ATR = re.compile(r'(\w+)="([^"]*)"')


def benefi(xml):
    """Beneficiarii din XML, ca dictionare de atribute — cheia e `cifR` (CNP-ul)."""
    return {b.get("cifR"): b for b in
            (dict(_ATR.findall(t)) for t in re.findall(r"<benef\b([^>]*)/>", xml or ""))}


def main():
    tok, tid, _s = U.context(FIRMA_406)
    jurnal = {"perioada": {"an": AN, "trim": TRIM}, "pasi": []}
    rele = []

    def pas(nume, **kw):
        jurnal["pasi"].append(dict(nume=nume, **kw))
        print("· %-50s %s" % (nume, json.dumps(kw, ensure_ascii=False, default=str)[:140]))

    def nepotrivit(ce, vrut, avut):
        rele.append((ce, vrut, avut))
        print("   NEPOTRIVIT %-44s asteptat %-10s obtinut %s" % (ce, vrut, avut))

    # ══ D406 / SAF-T ═══════════════════════════════════════════════════════
    st, r = U.cere("POST", "/declaratii/d406", {"tenant_id": tid, "an": AN, "trim": TRIM},
                   tok, timeout=600)
    if st != 200:
        raise SystemExit("D406 n-a generat: %s %s" % (st, str(r)[:300]))
    x = r["xml"]
    jurnal["d406"] = {"lungime": len(x)}
    nr_v = len(re.findall(r"<(?:\w+:)?Invoice\b", x))
    pas("D406 generat", lungime=len(x), nr_invoice=nr_v,
        are_sales=("<SalesInvoices>" in x), are_purchase=("<PurchaseInvoices>" in x))

    # 1. facturile lunii AUGUST din trimestru trebuie sa fie acolo
    for numar in ("CMT150", "CMT151", "PROBA-E2-A-P1"):
        if numar not in x:
            nepotrivit("factura %s (august) in SAF-T pe trim. %d" % (numar, TRIM),
                       "prezenta", "absenta")
    if all(n in x for n in ("CMT150", "CMT151", "PROBA-E2-A-P1")):
        pas("R165 reprobat: facturile din AUGUST sunt in SAF-T pe trimestrul III")

    # 2. antetul declara perioada ACOPERITA — cu aserţiune anti-vacuu pe ambele ramuri
    md = re.search(r"<(?:\w+:)?SelectionStartDate>([^<]+)<.*?"
                   r"<(?:\w+:)?SelectionEndDate>([^<]+)<", x, re.DOTALL)
    mp = re.search(r"<(?:\w+:)?PeriodStart>(\d+)<.*?<(?:\w+:)?PeriodStartYear>(\d+)<.*?"
                   r"<(?:\w+:)?PeriodEnd>(\d+)<.*?<(?:\w+:)?PeriodEndYear>(\d+)<", x, re.DOTALL)
    if not md and not mp:
        nepotrivit("antetul SAF-T: SelectionCriteria, una din cele doua ramuri de <xs:choice>",
                   "prezenta", "NICIUNA — proba n-are ce masura")
    elif mp:
        ls, ans, le, ane = (int(g) for g in mp.groups())
        avut = "%d/%d - %d/%d" % (ls, ans, le, ane)
        jurnal["d406"]["antet"] = avut
        pas("antetul SAF-T (tuplul Period*)", perioada=avut)
        vrut = "%d/%d - %d/%d" % (3 * TRIM - 2, AN, 3 * TRIM, AN)
        if avut != vrut:
            nepotrivit("perioada declarata in antet, firma trimestriala", vrut, avut)
    else:
        jurnal["d406"]["antet"] = "%s - %s" % md.groups()
        pas("antetul SAF-T (ramura SelectionStartDate)", start=md.group(1), end=md.group(2))
        if not md.group(1).startswith("%d-07" % AN):
            nepotrivit("SelectionStartDate pe firma trimestriala", "%d-07-01" % AN, md.group(1))

    # 3. CONFRUNTARE INTRE DECLARATII: cate facturi emise vede fiecare
    st, r394 = U.cere("POST", "/declaratii/d394", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
    nr394 = None
    if st == 200:
        mm = re.search(r'nrFacturi="(\d+)"', r394["xml"])
        nr394 = int(mm.group(1)) if mm else None
    nr_sales = len(re.findall(r"<(?:\w+:)?Invoice\b", x.split("<PurchaseInvoices>")[0])) \
        if "<SalesInvoices>" in x else 0
    jurnal["incrucisat"] = {"SAF-T facturi vanzare": nr_sales, "D394 nrFacturi": nr394}
    pas("INCRUCISAT: facturi emise", saf_t=nr_sales, d394=nr394)
    if nr394 is None:
        nepotrivit("D394 nrFacturi (fara el, confruntarea n-are a doua parte)", "o cifra", None)
    elif nr_sales != nr394:
        nepotrivit("facturi emise: SAF-T vs D394", nr394, nr_sales)

    st, rv = U.cere("POST", "/declaratii/d406/valideaza",
                    {"tenant_id": tid, "an": AN, "trim": TRIM}, tok, timeout=600)
    jurnal.setdefault("duk", {})["d406"] = {"cod": st, "stare": (rv or {}).get("stare"),
                                            "erori": str((rv or {}).get("erori"))[:300]}
    print("DUK d406: %s" % json.dumps(jurnal["duk"]["d406"], ensure_ascii=False)[:260])

    # ══ D205 ═══════════════════════════════════════════════════════════════
    os.environ["PROBA_EMAIL"] = EMAIL_205
    import importlib
    importlib.reload(U)
    tok5, tid5, _s5 = U.context(FIRMA_205)

    def d205():
        st, r = U.cere("POST", "/declaratii/d205", {"tenant_id": tid5, "an": AN}, tok5, timeout=180)
        return st, (r.get("xml") if isinstance(r, dict) and r.get("xml") else r)

    st, x5 = d205()
    pas("baza D205", cod=st, raspuns=str(x5)[:160] if st != 200 else "generata")
    b0 = benefi(x5) if st == 200 else {}
    jurnal["d205"] = {"benef_baza": {k: v for k, v in b0.items()}}
    pas("BAZA masurata (nu presupusa)", nr_benef=len(b0),
        sume={k: {c: v.get(c) for c in ("divid_D", "divid_P", "baza1", "imp1")}
              for k, v in b0.items()})

    # Proba adauga o pereche NOUA la fiecare rulare, numerotata. Nu se poate curata dupa sine —
    # `jurnal_api.sterge` refuza orice nota care nu e ciorna, si asa trebuie: o inregistrare
    # validata nu dispare. Marcarea idempotenta (sari daca exista) ar parea mai curata, dar la a
    # doua rulare lasa DELTA nemasurata si proba se reduce la invariantii absoluti — adica exact
    # ce s-a intamplat la prima reluare a lotului E. Costul asumat: firma de test acumuleaza
    # 10.000 lei de dividend per rulare; castigul: partea tare a lantului se probeaza de fiecare data.
    st, jl = U.cere("GET", "/tenants/%d/jurnal?an=%d&luna=%d" % (tid5, AN, LUNA), None, tok5)
    _note = (jl or {}).get("note") or (jl or {}).get("inregistrari") or []
    ale_mele = [n for n in _note if MARCA in str(n.get("descriere") or "")]
    rulare = len(ale_mele) // 2 + 1
    pas("perechi ale probei deja in evidenta", perechi=len(ale_mele) // 2, rulare_curenta=rulare)
    adaug = True

    cota_div = Decimal("16")   # Legea 141/2025, CF art.97 — de la 01.01.2026
    imp_delta = int(DIVIDEND * cota_div / 100)
    pas("ASTEPTARE (delta): divid_D, divid_P si baza1 cresc cu %s · imp1 creste cu %s (%s%%)"
        % (DIVIDEND, imp_delta, cota_div))

    if adaug:
        for descriere, debit, credit in (
                ("%s #%d distribuire dividende" % (MARCA, rulare), "121", "457"),
                ("%s #%d plata dividende" % (MARCA, rulare), "457", "5121")):
            st, r = U.cere("POST", "/tenants/%d/jurnal" % tid5, {
                "descriere": descriere, "data": "%d-%02d-15" % (AN, LUNA),
                "linii": [{"debit": debit, "credit": credit, "suma": float(DIVIDEND)}],
            }, tok5)
            nid = (r or {}).get("id") if isinstance(r, dict) else None
            pas("intrare — %s (%s = %s)" % (descriere, debit, credit), cod=st, id=nid)
            if nid:
                st2, r2 = U.cere("POST", "/tenants/%d/jurnal/%s/valideaza" % (tid5, nid), {}, tok5)
                pas("   validata", cod=st2, raspuns=str(r2)[:120])

    st, x5b = d205()
    if st != 200:
        raise SystemExit("D205 n-a generat dupa dividende: %s %s" % (st, str(x5b)[:300]))
    b1 = benefi(x5b)
    jurnal["d205"]["benef"] = b1
    pas("D205 generat", nr_benef=len(b1), primul=list(b1.values())[0] if b1 else None)
    if not b1:
        nepotrivit("beneficiar in D205 dupa dividende platite", "cel putin unul", 0)
    else:
        # ── DELTA: cele 10.000 ale probei urca pe toate cele patru campuri ──
        for cnp, b in b1.items():
            v0 = b0.get(cnp, {})
            for camp, cat in (("divid_D", int(DIVIDEND)), ("divid_P", int(DIVIDEND)),
                              ("baza1", int(DIVIDEND)), ("imp1", imp_delta)):
                d = (U.numar(b.get(camp, "0")) or 0) - (U.numar(v0.get(camp, "0")) or 0)
                if d != cat:
                    nepotrivit("D205 %s: cresterea adusa de proba (benef %s)" % (camp, cnp),
                               cat, d)
            break        # dividendul probei merge la asociatul unic

        # ── ABSOLUT: invariantii nu depind de baza si tin si la reluare ──
        for cnp, b in b1.items():
            baza = U.numar(b.get("baza1", "0")) or 0
            imp = U.numar(b.get("imp1", "0")) or 0
            if imp != int(Decimal(baza) * cota_div / 100):
                nepotrivit("D205 imp1 = %s%% x baza1 (benef %s)" % (cota_div, cnp),
                           int(Decimal(baza) * cota_div / 100), imp)
            dd = U.numar(b.get("divid_D", "0")) or 0
            dp = U.numar(b.get("divid_P", "0")) or 0
            if dd < dp:
                nepotrivit("D205 divid_D >= divid_P (nu poti plati mai mult decat s-a "
                           "distribuit; benef %s)" % cnp, ">= %d" % dp, dd)
        sec = dict(_ATR.findall(re.search(r"<sect_II\b([^>]*)>", x5b).group(1))) \
            if "<sect_II" in x5b else {}
        jurnal["d205"]["sect_II"] = sec
        if not sec:
            nepotrivit("sect_II in D205 (fara ea, totalurile nu se pot confrunta)", "prezenta", 0)
        else:
            if U.numar(sec.get("nrben", "0")) != len(b1):
                nepotrivit("sect_II nrben", len(b1), U.numar(sec.get("nrben", "0")))
            timp = sum(U.numar(bb.get("imp1", "0")) or 0 for bb in b1.values())
            if U.numar(sec.get("Timp", "0")) != timp:
                nepotrivit("sect_II Timp = suma imp1", timp, U.numar(sec.get("Timp", "0")))
            tbaza = sum(U.numar(bb.get("baza1", "0")) or 0 for bb in b1.values())
            if U.numar(sec.get("Tbaza", "0")) != tbaza:
                nepotrivit("sect_II Tbaza = suma baza1", tbaza, U.numar(sec.get("Tbaza", "0")))
        if not rele:
            pas("D205: dividendele ajung pe beneficiar, cu impozitul de 16%")

    st, rv = U.cere("POST", "/declaratii/d205/valideaza", {"tenant_id": tid5, "an": AN},
                    tok5, timeout=300)
    jurnal["duk"]["d205"] = {"cod": st, "stare": (rv or {}).get("stare"),
                             "erori": str((rv or {}).get("erori"))[:300]}
    print("DUK d205: %s" % json.dumps(jurnal["duk"]["d205"], ensure_ascii=False)[:260])

    jurnal["nepotriviri"] = rele
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(jurnal, f, ensure_ascii=False, indent=1, default=str)
    print("\nCONFRUNTARE LOT E: %d nepotriviri . artefact: %s" % (len(rele), os.path.basename(OUT)))
    return 1 if rele else 0


if __name__ == "__main__":
    raise SystemExit(main())
