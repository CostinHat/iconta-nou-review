# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL A (a doua declarație) — lanțul până în D394, și confruntarea lui cu D300.

Aceleași facturi, altă declarație. Aici așteptarea NU se scrie ca delta față de o bază, ci se
**derivă din faptele-sursă**: lista de facturi a firmei, citită prin aplicație. Forma e mai tare
decât „înainte/după" — spune ce TREBUIE să conțină declarația, nu doar cât ar trebui să se miște:

  · fiecare factură intră în `<rezumat1>` pe perechea (tip_partener, cotă), cu numărul ei;
  · emisă → coloanele `L` (livrări), primită → coloanele `A` (achiziții);
  · `tip_partener = 1` pentru partener cu CUI românesc valid, `2` pentru cel fără
    (`core/d394.py`: `P_TVA_RO = 1`, `P_NEINREG = 2`);
  · `informatii/nrFacturi` = numărul de facturi din perioadă.

ȘI O CONFRUNTARE ÎNTRE DOUĂ DECLARAȚII, care e chiar felul de defect pe care etapa 2 îl caută:
**TVA-ul colectat din D394 trebuie să fie egal cu `R17_2` din D300**, pe aceeași firmă și aceeași
perioadă. O cifră așezată în rândul greșit trece de DUK în amândouă, dar nu trece de egalitatea
asta. *Perechea e cea din supervizor (`EFACTURA_VS_D394`), aplicată aici pe lanțul de intrare.*

SCENARIUL: același ca la D300 — «Comert Micro TVA SRL» (`tenant_003`), trimestrul III/2026.
"""
import json
import os
import re
import sys
from decimal import Decimal

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Comert Micro TVA SRL"
AN, TRIM, LUNA = 2026, 3, 9
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_d394.json"
LUNI_TRIM = {1: (1, 2, 3), 2: (4, 5, 6), 3: (7, 8, 9), 4: (10, 11, 12)}

_REZ1 = re.compile(r"<rezumat1\b([^>]*)/>")
_ATR = re.compile(r'(\w+)="([^"]*)"')


def rezumat1(xml):
    """{(tip_partener, cotă): {câmp: valoare}} — citit din XML, nu din obiectul intern."""
    out = {}
    for m in _REZ1.finditer(xml):
        a = dict(_ATR.findall(m.group(1)))
        out[(a.get("tip_partener"), a.get("cota"))] = a
    return out


def main():
    tok, tid, schema = U.context(FIRMA)
    jurnal = {"firma": FIRMA, "tenant_id": tid, "perioada": {"an": AN, "trim": TRIM}}

    # 1. FAPTELE-SURSĂ: facturile perioadei, citite prin aplicație
    st, fl = U.cere("GET", "/tenants/%d/facturi" % tid, None, tok)
    fs = [f for f in ((fl or {}).get("facturi") or [])
          if str(f.get("data_emitere", ""))[:4] == str(AN)
          and int(str(f.get("data_emitere", "0-0"))[5:7] or 0) in LUNI_TRIM[TRIM]
          and (f.get("status") or "") != "anulata"]
    jurnal["facturi_sursa"] = fs
    print("facturi în trimestrul %d/%d: %d" % (TRIM, AN, len(fs)))
    for f in fs:
        print("   %-16s %-8s cui=%-12s total=%-9s tva=%s"
              % (f.get("numar"), f.get("directie"), f.get("tert_cui") or "—",
                 f.get("total"), f.get("tva")))

    # 2. AȘTEPTAREA, derivată din fapte — scrisă înainte de a citi declarația
    astept = {}
    for f in fs:
        cui = (f.get("tert_cui") or "").strip()
        tp = "1" if cui else "2"          # P_TVA_RO / P_NEINREG (core/d394.py)
        tva = Decimal(str(f.get("tva") or 0))
        total = Decimal(str(f.get("total") or 0))
        baza = total - tva
        cota = int((tva / baza * 100).quantize(Decimal("1"))) if baza else 0
        lat = "L" if f.get("directie") == "emisa" else "A"
        k = (tp, str(cota))
        c = astept.setdefault(k, {"baza": Decimal(0), "tva": Decimal(0), "nr": 0,
                                  "bazaA": Decimal(0), "tvaA": Decimal(0), "nrA": 0})
        if lat == "L":
            c["baza"] += baza
            c["tva"] += tva
            c["nr"] += 1
        else:
            c["bazaA"] += baza
            c["tvaA"] += tva
            c["nrA"] += 1
    jurnal["asteptare"] = {"%s/%s" % k: {kk: str(vv) for kk, vv in v.items()}
                           for k, v in astept.items()}
    print("\nAȘTEPTARE (din facturi, înainte de a citi declarația):")
    for k, v in sorted(astept.items()):
        print("   tip_partener=%s cotă=%-3s → L: %s facturi, bază %s, TVA %s · A: %s facturi, "
              "bază %s, TVA %s" % (k[0], k[1], v["nr"], v["baza"], v["tva"],
                                   v["nrA"], v["bazaA"], v["tvaA"]))

    # 3. O SINGURĂ generare
    st, r = U.cere("POST", "/declaratii/d394", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
    if st != 200:
        raise SystemExit("generarea D394 a picat: %s %s" % (st, r))
    xml = r["xml"]
    obt = rezumat1(xml)
    jurnal["rezumat1"] = {"%s/%s" % k: v for k, v in obt.items()}
    jurnal["avertismente"] = r.get("avertismente")

    # 4. CONFRUNTAREA, pe rând și pe sumă
    rele = []
    for k, v in sorted(astept.items()):
        a = obt.get(k)
        if not a:
            rele.append(("rezumat1 %s/%s lipsește cu totul" % k, "prezent", "absent"))
            continue
        for camp, vrut in (("bazaL", v["baza"]), ("tvaL", v["tva"]), ("facturiL", v["nr"]),
                           ("bazaA", v["bazaA"]), ("tvaA", v["tvaA"]), ("facturiA", v["nrA"])):
            avut = U.numar(a.get(camp, "0"))
            if avut != int(vrut):
                rele.append(("rezumat1 %s/%s %s" % (k[0], k[1], camp), int(vrut), avut))
    cap = U.randuri_xml(xml.split("?>", 1)[-1])
    # [corectat după prima rulare, citit la sursă] `nrFacturi` NU e numărul tuturor facturilor
    # perioadei: structura ANAF (`anaf_surse/d394_struct_anaf.txt`, poziția `nrFacturi`) îl
    # definește ca **„Nr total facturi EMISE în perioadă"**, iar `d394.nr_facturi_emise` îl
    # numără exact așa — emise, de tip `factura`, cu parte numerică în număr. Prima formă a
    # așteptării cerea 5 (toate facturile) și a numit „nepotrivire" un 4 corect.
    # *A doua oară în lotul ăsta când așteptarea mea a fost cea greșită — și a doua oară când
    # citirea la sursă a oprit un defect fals.*
    nr_emise = sum(1 for f in fs if f.get("directie") == "emisa"
                   and (f.get("tip") or "factura") == "factura"
                   and re.sub(r"\D", "", str(f.get("numar") or "")))
    nr_decl = U.numar(re.search(r'nrFacturi="(\d+)"', xml).group(1)) if 'nrFacturi="' in xml else None
    if nr_decl != nr_emise:
        rele.append(("informatii/nrFacturi (emise, tip factura, cu cifre)", nr_emise, nr_decl))
    print("\nCONFRUNTARE D394: %d nepotriviri" % len(rele))
    for nume, vrut, avut in rele:
        print("   NEPOTRIVIT %-34s așteptat %-10s obținut %s" % (nume, vrut, avut))

    # 5. CONFRUNTAREA ÎNTRE DECLARAȚII: TVA colectată D394 == R17_2 din D300
    st, rd = U.cere("POST", "/declaratii/d300", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
    d300 = U.randuri_xml(rd["xml"].split("?>", 1)[-1])
    r17_2 = U.numar(d300.get("R17_2", "0"))
    tva_l = sum(U.numar(v.get("tvaL", "0")) or 0 for v in obt.values())
    jurnal["incrucisat"] = {"D394_tvaL_total": tva_l, "D300_R17_2": r17_2, "coincid": tva_l == r17_2}
    print("ÎNCRUCIȘAT: TVA colectată D394 = %s · D300 R17_2 = %s · %s"
          % (tva_l, r17_2, "coincid" if tva_l == r17_2 else "NU COINCID"))
    if tva_l != r17_2:
        rele.append(("D394 tvaL total vs D300 R17_2", r17_2, tva_l))

    # 6. DUK — confirmă forma, nu conținutul
    st, rv = U.cere("POST", "/declaratii/d394/valideaza",
                    {"tenant_id": tid, "an": AN, "trim": TRIM}, tok, timeout=300)
    duk = {"cod": st, "stare": (rv or {}).get("stare"), "erori": (rv or {}).get("erori")} \
        if isinstance(rv, dict) else {"cod": st, "brut": rv}
    jurnal["duk"] = duk
    print("DUK: %s" % json.dumps(duk, ensure_ascii=False, default=str)[:400])

    jurnal["nepotriviri"] = rele
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(jurnal, f, ensure_ascii=False, indent=1, default=str)
    print("\nartefact: %s" % os.path.basename(OUT))
    return 1 if rele else 0


if __name__ == "__main__":
    raise SystemExit(main())
