# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL A — lanțul până în DECONTUL DE TVA (D300), pe date VALIDE.

Comanda (Costin, 05.09.2026): *„Pentru fiecare lanț: scrie așteptarea înainte de probă — ce rând,
ce sumă. Apoi probezi: valoarea intră, se înregistrează, ajunge în declarație în rândul corect și
cu suma corectă, declarația se generează și se validează. DUK verde nu e proba — el confirmă forma;
o cifră în rândul greșit trece la fel de bine."*

**AȘTEPTAREA E SCRISĂ AICI, ÎN COD, ÎNAINTE DE PROBĂ** — nu se derivă din ce a ieșit. Regula fiecărui
lanț e citită din generator (`core/d300.py`, antet) și din structura ANAF
(`anaf_surse/d300_struct_anaf.txt`), nu din memorie:

| lanț | intrarea | rândul | regula |
|---|---|---|---|
| 1 | factură EMISĂ, cotă 21% | `R9_1` bază, `R9_2` TVA | `_LIVRARE_RAND = {21: "R9", ...}` |
| 2 | factură EMISĂ, cotă 11% | `R10_1`, `R10_2` | `_LIVRARE_RAND = {11: "R10", ...}` |
| 3 | factură PRIMITĂ, cotă 21% | `R22_1`, `R22_2` (Rd.24) | `_ACHIZ_RAND = {21: "R22", ...}` |
| 4 | rând MANUAL D300 | rândul cerut, exact | `d300_manual_api.adauga` |
| 5 | totalurile calculate | `R17`, `R27`, `R32`, `R34_2` | formulele din `calcul_d300` |

`totalPlata_A` NU e o sumă de plată, ci **sumă de control**: `totalPlata_A = suma(camp 27 la 124)`
— citit la sursă în `anaf_surse/d300_struct_anaf.txt`, poziția 26. Se verifică ca atare.

SCENARIUL, DECLARAT: firma «Comert Micro TVA SRL» (`tenant_003`), plătitor de TVA cu perioadă
TRIMESTRIALĂ, trimestrul **III/2026**. Sumele sunt alese rotunde ca TVA-ul să nu depindă de
rotunjire: 1.000 × 21% = 210, 200 × 11% = 22, 500 × 21% = 105.

CE NU DEMONSTREAZĂ, declarat: că rândul e cel cerut de LEGE pentru operațiunea aia — asta e o
întrebare de temei, nu de lanț. Aici se probează că valoarea introdusă de om **ajunge unde spune
codul că ajunge**, cu suma exactă, și că nu se așază și în altă parte.
"""
import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Comert Micro TVA SRL"
AN, TRIM, LUNA = 2026, 3, 9
MARCA = "PROBA-E2-A"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_d300.json"

# ── INTRĂRILE, cu sumele lor ────────────────────────────────────────────────
EMISA_21 = Decimal("1000.00")
EMISA_11 = Decimal("200.00")
PRIMITA_21 = Decimal("500.00")
MANUAL_RAND, MANUAL_BAZA, MANUAL_TVA = "R14", Decimal("300.00"), Decimal("0")

# CUI-uri de test care trec cifra de control ANAF (cerința `core/test_cui_cnp_test_valid.py`)
CUI_CLIENT = "95275466"      # Distributie Profit IC SRL, firmă a portofoliului
CUI_FURNIZOR = "95141537"    # chiar firma probată — furnizor fictiv, dar CUI valid


def _tva(baza, cota):
    return (baza * Decimal(cota) / Decimal(100)).quantize(Decimal("1"))


#: Cheia prin care proba își recunoaște propriile intrări: dată + total, pe direcție. Fără ea,
#: a doua rulare ar mai adăuga un set de facturi, iar scenariul declarat s-ar dubla tăcut —
#: *o probă de lanț care nu se poate rula de două ori nu e o probă, e o singură lovitură.*
def deja_intrat(facturi, directie, data, total):
    return any(f.get("directie") == directie and str(f.get("data_emitere")) == data
               and abs(float(f.get("total") or 0) - float(total)) < 0.005
               for f in (facturi or []))


def asteptarea(baza, adaug):
    """Rândurile așteptate DUPĂ intrări, calculate din baza citită ÎNAINTE. Scrisă ca formulă.

    `adaug` spune care intrări chiar se adaugă în rularea asta (la a doua rulare, cele deja
    intrate au delta ZERO — dar rândul rămâne în așteptare, cu valoarea lui, deci confruntarea
    nu se golește: se cere aceeași cifră, doar că nu se mai adaugă încă o dată)."""
    b = {k: U.numar(v) for k, v in baza.items() if k.startswith("R") and "_" in k}
    a = dict(b)
    a["R9_1"] = b.get("R9_1", 0) + (int(EMISA_21) if adaug["e21"] else 0)
    a["R9_2"] = b.get("R9_2", 0) + (int(_tva(EMISA_21, 21)) if adaug["e21"] else 0)
    a["R10_1"] = b.get("R10_1", 0) + (int(EMISA_11) if adaug["e11"] else 0)
    a["R10_2"] = b.get("R10_2", 0) + (int(_tva(EMISA_11, 11)) if adaug["e11"] else 0)
    a["R22_1"] = b.get("R22_1", 0) + (int(PRIMITA_21) if adaug["p21"] else 0)
    a["R22_2"] = b.get("R22_2", 0) + (int(_tva(PRIMITA_21, 21)) if adaug["p21"] else 0)
    # [corectat după a doua rulare] Rândul manual e UPSERT pe `UNIQUE(an, luna, rand)` — citit la
    # sursă în `d300_manual_api.adauga` („face upsert pe UNIQUE(an,luna,rand)"). Deci SETEAZĂ
    # valoarea, nu o adaugă la ce era. Prima formă a așteptării o socotea aditivă și cerea 600 pe
    # a doua rulare; aplicația a răspuns 300, și avea dreptate. *Așteptarea trebuie să poarte
    # SEMANTICA intrării — adaugă vs. înlocuiește —, nu doar cifra.*
    a["R14_1"] = int(MANUAL_BAZA)
    # totalurile CALCULATE, nu copiate: baza colectată include și scutitul R14 (rd.1-18)
    a["R17_1"] = a["R9_1"] + a["R10_1"] + a["R14_1"]
    a["R17_2"] = a["R9_2"] + a["R10_2"]
    a["R27_1"] = a["R22_1"]
    a["R27_2"] = a["R22_2"]
    # [adăugate după prima rulare, cu motivul scris] AȘTEPTAREA MEA ERA INCOMPLETĂ, nu greșită:
    # nu numisem cele două totaluri intermediare de taxă dedusă, deci ieșeau „nepotrivite" cu 0.
    # Citite în generator: R28 = total dedus din R27; R32 = R28+R29+R30+R31 (`calcul_d300`, l.533).
    # Se scriu ca FORMULĂ, nu ca cifra care a ieșit — altfel n-ar mai fi o așteptare.
    a["R28_2"] = a["R27_2"]
    a["R32_2"] = a["R28_2"] + b.get("R29_2", 0) + b.get("R30_2", 0) + b.get("R31_2", 0)
    a["R34_2"] = a["R17_2"] - a["R32_2"]
    a["R37_2"] = a["R34_2"]
    a["R41_2"] = a["R34_2"]
    return a


def main():
    tok, tid, schema = U.context(FIRMA)
    jurnal = {"firma": FIRMA, "tenant_id": tid, "schema": schema,
              "perioada": {"an": AN, "trim": TRIM}, "pasi": []}

    def pas(nume, **kw):
        jurnal["pasi"].append(dict(nume=nume, **kw))
        print("· %-42s %s" % (nume, json.dumps(kw, ensure_ascii=False, default=str)[:170]))

    # 1. BAZA — ce e în decont ÎNAINTE de orice intrare
    st, r = U.cere("POST", "/declaratii/d300", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
    if st != 200:
        raise SystemExit("generarea de bază a picat: %s %s" % (st, r))
    baza = U.randuri_xml(r["xml"].split("?>", 1)[-1])
    jurnal["baza"] = baza
    pas("bază: rânduri nenule", randuri={k: v for k, v in baza.items()
                                         if k.startswith("R") and v not in ("", "0")})

    # 2. AȘTEPTAREA — scrisă ÎNAINTE de a atinge ceva
    _st, _fl = U.cere("GET", "/tenants/%d/facturi" % tid, None, tok)
    fs = (_fl or {}).get("facturi") if isinstance(_fl, dict) else _fl
    D = "%d-0%d-" % (AN, LUNA - 1)
    adaug = {"e21": not deja_intrat(fs, "emisa", D + "15", EMISA_21 * Decimal("1.21")),
             "e11": not deja_intrat(fs, "emisa", D + "16", EMISA_11 * Decimal("1.11")),
             "p21": not deja_intrat(fs, "primita", D + "17", PRIMITA_21 * Decimal("1.21"))}
    pas("intrări de adăugat în rularea asta", adaug=adaug)
    astept = asteptarea(baza, adaug)
    jurnal["asteptare"] = astept
    pas("AȘTEPTARE (scrisă înainte de probă)",
        randuri={k: astept[k] for k in ("R9_1", "R9_2", "R10_1", "R10_2", "R22_1", "R22_2",
                                        "R14_1", "R17_1", "R17_2", "R34_2")})

    # 3. INTRĂRILE, prin lanțul aplicației
    st, r = (U.cere("POST", "/tenants/%d/facturi/emite" % tid, {
        "tip": "factura", "tert_nume": "Distributie Profit IC SRL", "tert_cui": CUI_CLIENT,
        "data_emitere": "%d-0%d-15" % (AN, LUNA - 1),
        "linii": [{"descriere": MARCA + " livrare 21%", "cantitate": 1,
                   "pret_unitar": float(EMISA_21), "cota_tva": 21}],
    }, tok) if adaug["e21"] else (0, "deja intrată la o rulare anterioară"))
    pas("intrare 1 — factură emisă 21%%, bază %s" % EMISA_21, cod=st, raspuns=r)

    st, r = (U.cere("POST", "/tenants/%d/facturi/emite" % tid, {
        "tip": "factura", "tert_nume": "Distributie Profit IC SRL", "tert_cui": CUI_CLIENT,
        "data_emitere": "%d-0%d-16" % (AN, LUNA - 1),
        "linii": [{"descriere": MARCA + " livrare 11%", "cantitate": 1,
                   "pret_unitar": float(EMISA_11), "cota_tva": 11}],
    }, tok) if adaug["e11"] else (0, "deja intrată la o rulare anterioară"))
    pas("intrare 2 — factură emisă 11%%, bază %s" % EMISA_11, cod=st, raspuns=r)

    st, r = (U.cere("POST", "/tenants/%d/facturi" % tid, {
        "numar": MARCA + "-P1", "data_emitere": "%d-0%d-17" % (AN, LUNA - 1),
        "directie": "primita", "tert_nume": "Furnizor Proba E2 SRL", "tert_cui": CUI_FURNIZOR,
        "linii": [{"descriere": MARCA + " achiziție 21%", "cantitate": 1,
                   "pret_unitar": float(PRIMITA_21), "cota_tva": 21}],
    }, tok) if adaug["p21"] else (0, "deja intrată la o rulare anterioară"))
    pas("intrare 3 — factură primită 21%%, bază %s" % PRIMITA_21, cod=st, raspuns=r)

    st, r = U.cere("POST", "/tenants/%d/d300-manual" % tid, {
        "an": AN, "luna": LUNA, "rand": MANUAL_RAND,
        "baza": float(MANUAL_BAZA), "tva": float(MANUAL_TVA),
        "descriere": MARCA + " scutit cu drept de deducere",
    }, tok)
    pas("intrare 4 — rând manual %s, bază %s" % (MANUAL_RAND, MANUAL_BAZA), cod=st, raspuns=r)

    # 4. O SINGURĂ generare, cu toate așteptările verificate deodată
    st, r = U.cere("POST", "/declaratii/d300", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
    if st != 200:
        raise SystemExit("generarea de după intrări a picat: %s %s" % (st, r))
    dupa = U.randuri_xml(r["xml"].split("?>", 1)[-1])
    jurnal["dupa"] = dupa
    jurnal["avertismente"] = r.get("avertismente")
    pas("generare după intrări", avertismente=r.get("avertismente"),
        randuri={k: v for k, v in dupa.items() if k.startswith("R") and v not in ("", "0")})

    # 5. CONFRUNTAREA — pe rând și pe sumă
    rele, bune = [], []
    for k in sorted(set(astept) | {x for x in dupa if x.startswith("R")}):
        vrut = astept.get(k, 0)
        avut = U.numar(dupa.get(k, "0"))
        (bune if vrut == avut else rele).append((k, vrut, avut))
    jurnal["confruntare"] = {"potrivite": len(bune), "nepotrivite": rele}
    print("\nCONFRUNTARE: %d rânduri potrivite, %d nepotrivite" % (len(bune), len(rele)))
    for k, vrut, avut in rele:
        print("   NEPOTRIVIT %-8s așteptat %-10s obținut %s" % (k, vrut, avut))

    # suma de control, verificată ca sumă de control (poziția 26 din structura ANAF)
    suma = sum(U.numar(v) or 0 for k, v in dupa.items() if k.startswith("R") and "_" in k)
    tot = U.numar(dupa.get("totalPlata_A", "0"))
    jurnal["suma_control"] = {"calculata": suma, "din_xml": tot, "coincid": suma == tot}
    print("SUMA DE CONTROL: calculată %d · din XML %d · %s"
          % (suma, tot, "coincid" if suma == tot else "NU COINCID"))

    # 6. CICLUL COMPLET AL RÂNDULUI MANUAL: se vede în listă, iar ștergerea îl scoate DIN DECONT.
    #    Fără capătul ăsta, lanțul e probat doar într-un sens — iar „intră" fără „iese" nu spune
    #    dacă rândul e legat de declarație sau doar adăugat lângă ea.
    st, lst = U.cere("GET", "/tenants/%d/d300-manual?an=%d&luna=%d" % (tid, AN, LUNA), None, tok)
    randuri_m = (lst or {}).get("randuri") if isinstance(lst, dict) else lst
    pas("intrare 4b — rândul manual, citit din listă", cod=st, randuri=randuri_m)
    rid = None
    for x in (randuri_m or []):
        if x.get("rand") == MANUAL_RAND and MARCA in (x.get("descriere") or ""):
            rid = x.get("id")
    st, r = U.cere("DELETE", "/tenants/%d/d300-manual/%s" % (tid, rid), None, tok)
    pas("intrare 4c — rândul manual, șters", cod=st, id=rid, raspuns=r)
    st, r = U.cere("POST", "/declaratii/d300", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
    fara_manual = U.randuri_xml(r["xml"].split("?>", 1)[-1])
    r14 = U.numar(fara_manual.get("R14_1", "0"))
    # AȘTEPTARE, scrisă din generator: R14 (scutit CU drept de deducere) NU are sursă automată —
    # `calcul_d300` clasifică automat doar cotele 21/11/9, iar avertismentul lui spune explicit
    # „Clasific-o manual la R14/R15 (altfel nu apare în decont)". Deci după ștergerea singurului
    # rând manual R14, rândul trebuie să fie ZERO. (Prima formă compara cu baza rulării, care la a
    # doua rulare purta chiar rândul de șters — o așteptare care se compară cu ea însăși.)
    jurnal["dupa_stergere"] = {"R14_1": r14, "asteptat": 0, "gol_dupa_stergere": r14 == 0}
    print("DUPĂ ȘTERGERE: R14_1 = %s (așteptat 0) · %s"
          % (r14, "rândul a dispărut" if r14 == 0 else "RÂNDUL A RĂMAS"))
    if r14 != 0:
        rele.append(("R14_1 după ștergere", 0, r14))

    # 7. DUK — confirmă FORMA, nu conținutul. Se rulează, dar NU e proba.
    st, rv = U.cere("POST", "/declaratii/d300/valideaza",
                    {"tenant_id": tid, "an": AN, "trim": TRIM}, tok, timeout=300)
    duk = {"cod": st, "stare": (rv or {}).get("stare"), "erori": (rv or {}).get("erori"),
           "severitate": (rv or {}).get("severitate")} if isinstance(rv, dict) else {"cod": st, "brut": rv}
    jurnal["duk"] = duk
    print("DUK: %s" % json.dumps(duk, ensure_ascii=False, default=str)[:400])

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(jurnal, f, ensure_ascii=False, indent=1, default=str)
    print("\nartefact: %s" % os.path.basename(OUT))
    return 1 if rele else 0


if __name__ == "__main__":
    raise SystemExit(main())
