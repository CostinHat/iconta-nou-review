# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL I — cele opt unități-nucleu ale D406/SAF-T rămase neprobate individual.

Comanda (Costin, 15.09.2026), ordinea cerută: d300 → d394 → d112 → **d406** → restul.

**Ce a probat lotul E (05.09) și ce rămâne aici.** Lotul E a probat **fereastra** (ce perioadă intră
în fișier) și **antetul** (ce perioadă declară fișierul despre sine) — și a scris explicit că cele 34
de unități de atunci *nu* s-au probat una câte una. Lotul I ia cele opt care au rămas, și ele sunt
altceva: **imobilizările și planul de conturi**, adică secțiunile pe care D300/D394 nu le ating.

**AȘTEPTAREA, SCRISĂ ÎNAINTE:**

| # | unitatea | intrarea | așteptat | de unde |
|---|---|---|---|---|
| 1 | `POST /tenants/{}/plan-conturi` | un cont analitic nou | apare în planul firmei; **rolul e cerut** (R55) | `main.py:1805` |
| 2 | `POST /tenants/{}/solduri` | sold inițial pe contul nou | rezumatul soldurilor îl arată | `SolduriIn` |
| 3 | `POST /tenants/{}/nota-inventariere` (`plus_mf`) | plus de inventar ca imobilizare, 3.000 lei | apare un **mijloc fix** | `main.py:6014` |
| 4 | `GET /tenants/{}/mijloace-fixe` | — | îl conține, cu valoarea lui | citire |
| 5 | `GET /tenants/{}/d406-active` | — | secțiunea Assets îl conține | `d406_active_xml` |
| 6 | `POST /tenants/{}/amortizare` | luna curentă | nota de amortizare **validată** (nu ciornă, R55) · amortizarea cumulată crește · Assets se schimbă | `main.py:3233` |
| 7 | `POST /tenants/{}/reevaluare-imobilizare` | valoare justă nouă | valoarea din Assets se schimbă | `main.py:5848` |
| 8 | `GET /tenants/{}/d406-stocuri` | perioada trimestrului | secțiunea se generează, nu cade | `d406_stocuri_xml` |

**Lanțurile 4, 5 și 8 sunt CITIRI** — ele nu introduc nimic, dar sunt unități-nucleu fiindcă scriu…
nu, fiindcă **sunt singura cale prin care se vede** ce au scris celelalte. Se probează ca **martori**:
fără ele, „mijlocul fix a intrat" ar fi o afirmație despre baza de date, nu despre declarație.

SCENARIUL, DECLARAT: «Comert Micro TVA SRL» (`tenant_003`), trimestrul **III/2026**. Contul analitic
și mijlocul fix poartă marca `PROBA-E2-I-<rulare>`. Mijlocul fix **rămâne** (casarea e un act separat,
cu consecințe fiscale) — costul se scrie: firma acumulează un mijloc fix per rulare.

CE NU DEMONSTREAZĂ, declarat: corectitudinea cuantumului amortizării pe metodă (aia e `core/
test_d406_amortizare.py`, cu golden pe fiecare metodă) — aici se probează că valoarea introdusă
**ajunge** în secțiunea declarației.
"""
import json
import re
import sys

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Comert Micro TVA SRL"
AN, LUNA, TRIM = 2026, 9, 3
MARCA = "PROBA-E2-I"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_lot_i_d406.json"
VALOARE_MF = 3000


def _xml_din(r):
    if isinstance(r, str):
        return r
    if isinstance(r, dict):
        import base64
        if r.get("xml"):
            return r["xml"]
        if r.get("xml_b64"):
            return base64.b64decode(r["xml_b64"]).decode("utf-8", "replace")
    return ""


def active(tok, tid):
    """(xml, meta) pentru secțiunea Assets. Cade dacă nu găsește nicio imobilizare — ANTI-VACUU."""
    st, r = U.cere("GET", "/tenants/%d/d406-active?an=%d" % (tid, AN), None, tok, timeout=180)
    xml = _xml_din(r)
    return xml, {"stare": st, "octeti": len(xml),
                 "raspuns": None if xml else str(r)[:300]}


def main():
    tok, tid, schema = U.context(FIRMA)
    st_mf, r_mf = U.cere("GET", "/tenants/%d/mijloace-fixe" % tid, None, tok)
    lst = (r_mf.get("mijloace") if isinstance(r_mf, dict) else r_mf) or []
    rul = 1 + len([m for m in lst if MARCA in str(m.get("denumire") or "")]) \
        if isinstance(lst, list) else 1
    rez = {"firma": FIRMA, "tenant_id": tid, "schema": schema,
           "perioada": "%d-T%d" % (AN, TRIM), "rulare": rul, "lanturi": []}
    cont_nou = "208.%d" % (90 + rul)
    den_mf = "%s Imobilizare %d" % (MARCA, rul)

    def scrie(i):
        rez["lanturi"].append(i)

    # ── 1. CONT ANALITIC NOU ────────────────────────────────────────────────
    i1 = {"lant": "1 · plan-conturi: cont analitic nou → apare în planul firmei",
          "ruta": "POST /tenants/{}/plan-conturi", "cont": cont_nou}
    # Câmpul e `simbol`, nu `cont`: prima formă a probei a trimis `cont`, iar ruta a refuzat cu
    # `422` și cu erori PER CÂMP — «simbol — lipsește». *Refuzul a fost cel care m-a corectat.*
    st, r = U.cere("POST", "/tenants/%d/plan-conturi" % tid,
                   {"simbol": cont_nou, "denumire": "%s cont analitic %d" % (MARCA, rul)}, tok)
    i1["raspuns"] = {"stare": st, "corp": str(r)[:250]}
    st_l, r_l = U.cere("GET", "/tenants/%d/plan-conturi?q=%s" % (tid, cont_nou), None, tok)
    gasite = (r_l.get("conturi") if isinstance(r_l, dict) else r_l) or []
    i1["in_plan"] = [c for c in gasite if str(c.get("simbol") or c.get("cont") or "") == cont_nou]
    i1["OK"] = st in (200, 201) and bool(i1["in_plan"])
    scrie(i1)

    # ── 2. SOLD INIȚIAL pe contul nou ───────────────────────────────────────
    i2 = {"lant": "2 · solduri: sold inițial pe contul nou → rezumatul îl arată",
          "ruta": "POST /tenants/{}/solduri"}
    st, r = U.cere("POST", "/tenants/%d/solduri" % tid,
                   {"randuri": [{"cont": cont_nou, "denumire": "%s sold" % MARCA,
                                 "debit": VALOARE_MF, "credit": 0},
                                {"cont": "1012", "denumire": "Capital subscris varsat",
                                 "debit": 0, "credit": VALOARE_MF}],
                    "data_referinta": "%d-01-01" % AN}, tok)
    i2["raspuns"] = {"stare": st, "corp": str(r)[:250]}
    st_r, r_r = U.cere("GET", "/tenants/%d/solduri" % tid, None, tok)
    i2["rezumat"] = str(r_r)[:300]
    i2["OK"] = st in (200, 201)
    scrie(i2)

    # ── 3+4. PLUS DE INVENTAR CA IMOBILIZARE, și martorul lui ───────────────
    i3 = {"lant": "3 · nota-inventariere `plus_mf` 3.000 → apare un mijloc fix",
          "ruta": "POST /tenants/{}/nota-inventariere"}
    # `valoare`, `dnf_luni` și `data_pif` stau la NIVELUL DE SUS, nu într-un obiect `plus_mf`.
    # Prima formă le-a pus înăuntru și ruta a refuzat: «Valoarea mijlocului fix trebuie sa fie un
    # numar pozitiv.» Iar `dnf_luni` e obligatoriu **cu motivul scris în cod**: fără el activul nu se
    # poate amortiza, deci e invizibil pentru `tenant_amortizare` și pentru `/d406-active`.
    st, r = U.cere("POST", "/tenants/%d/nota-inventariere" % tid,
                   {"data": "%d-%02d-25" % (AN, LUNA), "operatie": "plus_mf",
                    "descriere": den_mf, "denumire": den_mf, "cod": "%s-%d" % (MARCA, rul),
                    "valoare": VALOARE_MF, "dnf_luni": 60,
                    "data_pif": "%d-%02d-25" % (AN, LUNA),
                    "cont_imobilizare": "2131"}, tok)
    i3["raspuns"] = {"stare": st, "corp": str(r)[:300]}
    st_m, r_m2 = U.cere("GET", "/tenants/%d/mijloace-fixe" % tid, None, tok)
    lista2 = (r_m2.get("mijloace") if isinstance(r_m2, dict) else r_m2) or []
    i3["mijloace_fixe"] = {"inainte": len(lst) if isinstance(lst, list) else "?",
                           "dupa": len(lista2) if isinstance(lista2, list) else "?"}
    i3["OK"] = st in (200, 201)
    scrie(i3)

    i4 = {"lant": "4 · mijloace-fixe (MARTOR): citirea arată ce a scris lanțul 3",
          "ruta": "GET /tenants/{}/mijloace-fixe", "stare": st_m,
          "cate": len(lista2) if isinstance(lista2, list) else "?"}
    i4["OK"] = st_m == 200 and isinstance(lista2, list) and len(lista2) > 0
    scrie(i4)

    # ── 5. SECȚIUNEA ASSETS din SAF-T ───────────────────────────────────────
    xml5, meta5 = active(tok, tid)
    i5 = {"lant": "5 · d406-active (MARTOR): secțiunea Assets se generează și conține imobilizări",
          "ruta": "GET /tenants/{}/d406-active", "d406_active": meta5,
          # Elementele SAF-T poartă PREFIX de spațiu de nume: `<nsSAFT:Asset>`. Prima formă căuta
          # `<Asset` și găsea zero pe un XML de 8.682 de octeți plin de active. *A patra oară când
          # cel greșit e cititorul probei, nu aplicația.*
          "are_asset": bool(re.search(r"<(?:\w+:)?Asset\b", xml5 or "", re.I))}
    i5["OK"] = meta5["stare"] == 200 and bool(xml5) and i5["are_asset"]
    scrie(i5)

    # ── 6. AMORTIZAREA LUNARĂ ───────────────────────────────────────────────
    i6 = {"lant": "6 · amortizare: nota lunară → secțiunea Assets se schimbă",
          "ruta": "POST /tenants/{}/amortizare"}
    st, r = U.cere("POST", "/tenants/%d/amortizare?an=%d&luna=%d" % (tid, AN, LUNA), None, tok)
    i6["raspuns"] = {"stare": st, "corp": str(r)[:300]}
    xml6, meta6 = active(tok, tid)
    i6["d406_active"] = meta6
    i6["s_a_schimbat"] = (xml6 != xml5)
    i6["OK"] = st in (200, 201) and i6["s_a_schimbat"]
    scrie(i6)

    # ── 7. REEVALUAREA ──────────────────────────────────────────────────────
    i7 = {"lant": "7 · reevaluare-imobilizare → valoarea din Assets se schimbă",
          "ruta": "POST /tenants/{}/reevaluare-imobilizare"}
    mfid = None
    for m in (lista2 if isinstance(lista2, list) else []):
        if MARCA in str(m.get("denumire") or ""):
            mfid = m.get("id")
    i7["mijloc_fix_id"] = mfid
    if not mfid:
        i7["NEPROBAT"] = ("mijlocul fix al probei nu s-a regăsit în listă după denumire, deci "
                          "reevaluarea n-are subiect; se scrie, nu se sare")
        i7["OK"] = False
    else:
        st, r = U.cere("POST", "/tenants/%d/reevaluare-imobilizare" % tid,
                       {"data": "%d-%02d-26" % (AN, LUNA), "operatie": "reevaluare",
                        "reevaluare": {"mijloc_fix_id": mfid, "valoare_justa": VALOARE_MF + 500}},
                       tok)
        i7["raspuns"] = {"stare": st, "corp": str(r)[:300]}
        xml7, meta7 = active(tok, tid)
        i7["d406_active"] = meta7
        i7["s_a_schimbat"] = (xml7 != xml6)
        i7["OK"] = st in (200, 201) and i7["s_a_schimbat"]
    scrie(i7)

    # ── 8. SECȚIUNEA STOCURI ────────────────────────────────────────────────
    i8 = {"lant": "8 · d406-stocuri: secțiunea se generează pe perioada trimestrului",
          "ruta": "GET /tenants/{}/d406-stocuri"}
    st, r = U.cere("GET", "/tenants/%d/d406-stocuri?data_start=%d-07-01&data_end=%d-09-30&cui=%s"
                   % (tid, AN, AN, "95141537"), None, tok, timeout=180)
    xml8 = _xml_din(r)
    i8["raspuns"] = {"stare": st, "octeti": len(xml8), "corp": None if xml8 else str(r)[:300]}
    i8["OK"] = st == 200 and bool(xml8)
    scrie(i8)

    text = json.dumps(rez, indent=1, ensure_ascii=False)
    open(OUT, "w", encoding="utf-8").write(text)
    print(text)
    nep = [x for x in rez["lanturi"] if not x.get("OK")]
    print("\nLANTURI: %d · CU NEPOTRIVIRI: %d" % (len(rez["lanturi"]), len(nep)))
    for x in nep:
        print("   ! %s" % x["lant"])
    return 1 if nep else 0


if __name__ == "__main__":
    sys.exit(main())
