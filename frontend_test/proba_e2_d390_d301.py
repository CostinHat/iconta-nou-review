# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL B — D390 (recapitulativa IC) si D301 (decontul special de TVA), pe date VALIDE.

Amandoua se hranesc din OPERATIUNI introduse de contabil, nu din facturi — de-aia sunt un lot:
nucleul lor, derivat cu `scan_lanturi_declaratie.py`, e format din exact aceleasi trei feluri de
rute (adauga / listeaza / sterge), pe doua registre diferite.

ASTEPTAREA, SCRISA INAINTE — fiecare rand cu temeiul citirii lui:

| lant | intrarea | randul | de unde stiu |
|---|---|---|---|
| 1 | linie manuala D390, tip `P`, tara `DE`, baza 1.500 | `<operatie tip="P" tara="DE" baza="1500"/>` | `d390.build_xml`, l.470 |
| 2 | reclasificarea unei operatiuni AUTO, `A` -> `S` | aceeasi operatie, cu `tip="S"` | `TIPURI_DIRECTIE = {"primita": ("A","S")}` |
| 3 | operatiune D301 tip 1, 1.000 EUR la curs 5,0000, cota 21% | `baza1` = 5.000, `tva1` = 1.050 | `d301.calc_baza` = `round(val × curs)`; `build_xml` scrie `bazaN`/`tvaN` |
| 4 | stergerea / revenirea | randul DISPARE, iar tipul revine la cel automat | mesajul rutei + `manual_adauga` (tip == tip_def -> stergerea override-ului) |

**DOUA LUCRURI PE CARE LE-A CORECTAT PRIMA RULARE**, si amandoua erau ale asteptarii mele:
  · **tipul `L` nu se poate introduce manual.** Ruta refuza, si spune exact ce accepta:
    *„Tip linie manuala: A (achizitie bunuri IC fara cod furnizor, NOTA 1) / P / S / T / R"* —
    livrarile de bunuri IC vin din FACTURI, nu de la tastatura;
  · **firma trebuie sa aiba operatiuni IC in Vectorul fiscal.** Pe `tenant_003` ruta refuza cu
    *„Firma nu are operatiuni intracomunitare in Vectorul fiscal"*. Lantul D390 se probeaza pe
    firma care le are — `Distributie Profit IC SRL` (`tenant_004`), unde exista deja o achizitie
    IC automata din facturi (BAUHAUS GMBH, DE, 12.000), deci si RECLASIFICAREA are subiect.

**D390 nu se depune pe zero** — ruta o spune cu temei (*OPANAF 705/2020 pct. 1.2; art. 325 Cod
fiscal*). Asta e chiar prima si ultima proba a lantului: fara operatiune, refuz; cu ea, declaratie.

SCENARIUL, pe DOUA firme, fiindca declaratiile cer doua stari fiscale diferite:
  · **D390** pe «Distributie Profit IC SRL» (`tenant_004`), **luna 08/2026** — are IC in vector;
  · **D301** pe «Achizitii IC Neplatitor SRL» (`tenant_006`), **luna 08/2026** — decontul
    SPECIAL e pentru NEplatitori de TVA, si ruta o spune singura cand incerci pe un platitor.
"""
import json
import os
import re
import sys
from decimal import Decimal

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA_D390 = "Distributie Profit IC SRL"      # are operatiuni IC in Vectorul fiscal
# D301 e decontul SPECIAL: ruta refuza pe o firma platitoare de TVA, si spune de ce —
# «D301 (decontul special) e pentru NEplatitori». A treia oara in lotul asta cand asteptarea mea
# a fost cea gresita: alesesem firma campaniei, nu firma careia i se aplica declaratia.
FIRMA_D301 = "Achizitii IC Neplatitor SRL"
AN, LUNA = 2026, 8
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_d390_d301.json"

# ── intrarile ───────────────────────────────────────────────────────────────
# tipul manual e `P` (prestari servicii IC): `L` e refuzat, si pe drept — livrarile de bunuri IC
# vin din facturi. Ruta enumera ce accepta, deci lista nu se ghiceste.
D390 = {"tip": "P", "tara": "DE", "cod": "DE811907980", "den": "Partener DE Proba E2",
        "baza": 1500}
D390_RECLAS = "S"                     # A -> S, pe latura de achizitie (TIPURI_DIRECTIE["primita"])
D301 = {"tip": 1, "nr_doc": "E2-B-1", # formatul cerut e ZZ.LL.AAAA, nu ISO — ruta o spune pe litere:
        # «Data documentului e obligatorie în format ZZ.LL.AAAA (ex. 15.06.2026)»
        "data_doc": "20.%02d.%d" % (LUNA, AN),
        "val_valuta": 1000, "tip_valuta": "EUR", "curs": 5.0, "cota": 21}
D301_BAZA = int(Decimal("1000") * Decimal("5.0"))          # calc_baza = round(val × curs)
D301_TVA = int((Decimal(D301_BAZA) * Decimal(21) / Decimal(100)).quantize(Decimal("1")))

_OP = re.compile(r"<operatie\b([^>]*)/>")
_ATR = re.compile(r'(\w+)="([^"]*)"')


def operatii(xml):
    return [dict(_ATR.findall(m.group(1))) for m in _OP.finditer(xml)]


def main():
    tok9, tid9, _s9 = U.context(FIRMA_D390)
    tok1, tid1, _s1 = U.context(FIRMA_D301)
    jurnal = {"d390": {"firma": FIRMA_D390, "tenant_id": tid9},
              "d301": {"firma": FIRMA_D301, "tenant_id": tid1},
              "perioada": {"an": AN, "luna": LUNA}, "pasi": []}
    rele = []

    def pas(nume, **kw):
        jurnal["pasi"].append(dict(nume=nume, **kw))
        print("\u00b7 %-48s %s" % (nume, json.dumps(kw, ensure_ascii=False, default=str)[:150]))

    def nepotrivit(ce, vrut, avut):
        rele.append((ce, vrut, avut))
        print("   NEPOTRIVIT %-42s asteptat %-12s obtinut %s" % (ce, vrut, avut))

    def d390_ops():
        st, r = U.cere("POST", "/declaratii/d390",
                       {"tenant_id": tid9, "an": AN, "luna": LUNA}, tok9)
        return st, (operatii(r["xml"]) if st == 200 and isinstance(r, dict) else r)

    # BAZA: ce operatiuni AUTO exista deja (din facturi), inainte de orice atingere
    st, baza_ops = d390_ops()
    if st != 200:
        raise SystemExit("D390 nu genereaza nici pe baza existenta: %s %s" % (st, baza_ops))
    jurnal["d390"]["baza"] = baza_ops
    pas("baza D390 - operatiunile AUTO din facturi", operatii=baza_ops)
    auto = [o for o in baza_ops if o.get("tip") == "A"]
    if not auto:
        raise SystemExit("nicio operatiune AUTO de tip A in %02d/%d - reclasificarea n-ar avea "
                         "subiect" % (LUNA, AN))
    o_auto = auto[0]
    cod_auto = o_auto.get("codO") or o_auto.get("cod") or ""
    pas("ASTEPTARE 1: reclasificarea A -> %s schimba tipul acestei operatiuni, si NUMAI tipul"
        % D390_RECLAS, operatie=o_auto)

    # 1. RECLASIFICAREA unei operatiuni AUTO: A -> S
    st, r = U.cere("PUT", "/tenants/%d/d390-clasificare/reclasificare" % tid9,
                   {"an": AN, "luna": LUNA, "directie": "primita", "tara": o_auto.get("tara"),
                    "cod": cod_auto, "tip": D390_RECLAS}, tok9)
    pas("intrare 1 - reclasificare A -> %s" % D390_RECLAS, cod=st, raspuns=r)
    st, ops = d390_ops()
    dupa = [o for o in (ops or []) if (o.get("codO") or o.get("cod")) == cod_auto]
    if not dupa:
        nepotrivit("operatiunea reclasificata, in XML", "prezenta", ops)
    elif dupa[0].get("tip") != D390_RECLAS:
        nepotrivit("tipul dupa reclasificare", D390_RECLAS, dupa[0].get("tip"))
    else:
        pas("D390: tipul s-a schimbat in XML", operatie=dupa[0])
    if dupa and U.numar(dupa[0].get("baza")) != U.numar(o_auto.get("baza")):
        nepotrivit("baza NU trebuia sa se miste la reclasificare",
                   U.numar(o_auto.get("baza")), U.numar(dupa[0].get("baza")))

    # 2. LINIA MANUALA se adauga peste, ca a doua operatiune
    st, r = U.cere("POST", "/tenants/%d/d390-clasificare/manual" % tid9,
                   dict(D390, an=AN, luna=LUNA), tok9)
    pas("intrare 2 - linie manuala (%s %s, baza %s)"
        % (D390["tip"], D390["tara"], D390["baza"]), cod=st, raspuns=r)
    mid = (r or {}).get("id") if isinstance(r, dict) else None
    st, ops = d390_ops()
    jurnal["d390"]["dupa_manual"] = ops
    man = [o for o in (ops or []) if U.numar(o.get("baza")) == D390["baza"]]
    if not man:
        nepotrivit("<operatie> manuala, baza %s" % D390["baza"], "prezenta", ops)
    elif man[0].get("tip") != D390["tip"]:
        nepotrivit("tipul liniei manuale", D390["tip"], man[0].get("tip"))
    else:
        pas("D390: linia manuala apare ca <operatie>", operatie=man[0])

    st, rv = U.cere("POST", "/declaratii/d390/valideaza",
                    {"tenant_id": tid9, "an": AN, "luna": LUNA}, tok9, timeout=300)
    jurnal.setdefault("duk", {})["d390"] = {"cod": st, "stare": (rv or {}).get("stare"),
                                            "erori": (rv or {}).get("erori")}
    print("DUK d390: %s" % json.dumps(jurnal["duk"]["d390"], ensure_ascii=False)[:220])

    # 3. CAPATUL CELALALT: se scot amandoua, iar declaratia revine EXACT la starea de baza
    st, r = U.cere("DELETE", "/tenants/%d/d390-clasificare/manual/%s?an=%d&luna=%d"
                   % (tid9, mid, AN, LUNA), None, tok9)
    pas("iesire 2 - linia manuala, stearsa", cod=st, raspuns=r)
    st, r = U.cere("PUT", "/tenants/%d/d390-clasificare/reclasificare" % tid9,
                   {"an": AN, "luna": LUNA, "directie": "primita", "tara": o_auto.get("tara"),
                    "cod": cod_auto, "tip": "A"}, tok9)
    pas("iesire 1 - reclasificare inapoi la A (scoate override-ul)", cod=st, raspuns=r)
    st, ops = d390_ops()
    jurnal["d390"]["final"] = ops
    _k = lambda L: sorted(json.dumps(o, sort_keys=True) for o in (L or []))
    if _k(ops) != _k(baza_ops):
        nepotrivit("D390 dupa desfacere revine la starea de baza", baza_ops, ops)
    else:
        pas("D390 a revenit exact la starea de baza", operatii=ops)

    # ── D301 ────────────────────────────────────────────────────────────────
    st, r = U.cere("POST", "/declaratii/d301", {"tenant_id": tid1, "an": AN, "luna": LUNA}, tok1)
    baza301 = U.randuri_xml(r["xml"].split("?>", 1)[-1]) if st == 200 else {}
    b0 = U.numar(baza301.get("baza%d" % D301["tip"], "0")) or 0
    t0 = U.numar(baza301.get("tva%d" % D301["tip"], "0")) or 0
    pas("baza D301", cod=st, baza=b0, tva=t0)
    pas("ASTEPTARE 2: baza%d = %s + %s . tva%d = %s + %s"
        % (D301["tip"], b0, D301_BAZA, D301["tip"], t0, D301_TVA))

    st, r = U.cere("POST", "/tenants/%d/d301-operatiuni" % tid1, dict(D301, an=AN, luna=LUNA), tok1)
    pas("intrare 3 - operatiune D301 tip %s (%s %s x %s, cota %s%%)"
        % (D301["tip"], D301["val_valuta"], D301["tip_valuta"], D301["curs"], D301["cota"]),
        cod=st, raspuns=r)
    opid = (r or {}).get("id") if isinstance(r, dict) else None

    st, r = U.cere("POST", "/declaratii/d301", {"tenant_id": tid1, "an": AN, "luna": LUNA}, tok1)
    if st != 200:
        raise SystemExit("D301 n-a generat: %s %s" % (st, r))
    cap = U.randuri_xml(r["xml"].split("?>", 1)[-1])
    jurnal["d301"]["cap"] = cap
    pas("D301 generat", baza=cap.get("baza%d" % D301["tip"]),
        tva=cap.get("tva%d" % D301["tip"]), avertismente=r.get("avertismente"))
    if U.numar(cap.get("baza%d" % D301["tip"], "0")) != b0 + D301_BAZA:
        nepotrivit("D301 baza%d" % D301["tip"], b0 + D301_BAZA,
                   U.numar(cap.get("baza%d" % D301["tip"], "0")))
    if U.numar(cap.get("tva%d" % D301["tip"], "0")) != t0 + D301_TVA:
        nepotrivit("D301 tva%d" % D301["tip"], t0 + D301_TVA,
                   U.numar(cap.get("tva%d" % D301["tip"], "0")))

    st, rv = U.cere("POST", "/declaratii/d301/valideaza",
                    {"tenant_id": tid1, "an": AN, "luna": LUNA}, tok1, timeout=300)
    jurnal.setdefault("duk", {})["d301"] = {"cod": st, "stare": (rv or {}).get("stare"),
                                            "erori": (rv or {}).get("erori")}
    print("DUK d301: %s" % json.dumps(jurnal["duk"]["d301"], ensure_ascii=False)[:220])

    # perioada se trimite si la stergere: ruta o cere pe litere («an - lipseste; luna - lipseste»),
    # din acelasi motiv ca la D390 — nu se sterge dintr-o luna trimitand alta.
    st, r = U.cere("DELETE", "/tenants/%d/d301-operatiuni/%s?an=%d&luna=%d"
                   % (tid1, opid, AN, LUNA), None, tok1)
    pas("iesire 3 - operatiunea D301, stearsa", cod=st, raspuns=r)
    st, r = U.cere("POST", "/declaratii/d301", {"tenant_id": tid1, "an": AN, "luna": LUNA}, tok1)
    if st == 200:
        c2 = U.randuri_xml(r["xml"].split("?>", 1)[-1])
        if U.numar(c2.get("baza%d" % D301["tip"], "0")) != b0:
            nepotrivit("D301 baza%d dupa stergere" % D301["tip"], b0,
                       U.numar(c2.get("baza%d" % D301["tip"], "0")))
        else:
            pas("D301 a revenit la baza", baza=b0)
    else:
        pas("D301 dupa stergere: refuz (fara continut)", cod=st, mesaj=str(r)[:160])

    jurnal["nepotriviri"] = rele
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(jurnal, f, ensure_ascii=False, indent=1, default=str)
    print("\nCONFRUNTARE LOT B: %d nepotriviri . artefact: %s"
          % (len(rele), os.path.basename(OUT)))
    return 1 if rele else 0


if __name__ == "__main__":
    raise SystemExit(main())
