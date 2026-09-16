# -*- coding: utf-8 -*-
"""R187 — vanzarea intracomunitara produce FACTURA, si ajunge in AMANDOUA declaratiile.

Comanda (Costin, 16.09.2026): *„vanzarea intracomunitara produce factura, ca orice livrare. Fara rand
in facturi nu ajunge in D300 rd.1/rd.3 si nici in D390. Probeaza lantul pana in ambele declaratii."*

ASTEPTAREA, SCRISA INAINTE:

| lant | intrarea | asteptat | de unde |
|---|---|---|---|
| 1 | vanzare IC de BUNURI, 900 lei | `facturi` +1 (emisa, tara clientului, axa `bunuri`) · D300 `R1_1` += 900 · D390 capata o operatiune `L` | `d300.py:222` (rd.1 = R1) · `d390.TIPURI_DIRECTIE` |
| 2 | vanzare IC de SERVICII, 700 lei | axa `servicii` · D300 `R3_1` += 700 · D390 capata `P` | `d300.py:229` (rd.3 = R3_1) |

*Cele doua lanturi sunt o pereche: pe acelasi client, in aceeasi luna. Daca axa n-ar fi pe document,
ele s-ar contopi si una din cele doua rutari ar dispărea — chiar imposibilitatea pe care decizia
R186 o numeste.*

CE NU DEMONSTREAZA, declarat: corectitudinea VIES (apelul e real, la serviciul UE — daca el refuza
codul, refuzul aplicatiei e rezultatul si se scrie ca atare) si nici cuantumul scutirii.
"""
import base64
import json
import re
import sys

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Comert Micro TVA SRL"
AN, LUNA, TRIM = 2026, 9, 3
COD_CLIENT = "DE811907980"
OUT = "/home/costin/iconta_nou/frontend_test/proba_r187_vanzare_ic.json"


def _xml(r):
    if isinstance(r, str):
        return r
    if isinstance(r, dict):
        if r.get("xml"):
            return r["xml"]
        if r.get("xml_b64"):
            return base64.b64decode(r["xml_b64"]).decode("utf-8", "replace")
    return ""


def d300(tok, tid):
    st, r = U.cere("POST", "/declaratii/d300", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok,
                   timeout=240)
    x = _xml(r)
    if st != 200 or not x:
        return None, {"stare": st, "raspuns": str(r)[:300]}
    cap = x.split("?>", 1)[-1]
    randuri = dict(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"',
                              cap.split(">", 1)[0]))
    if not any(k.startswith("R") for k in randuri):
        raise SystemExit("ANTI-VACUU: D300 s-a generat dar nu i s-a citit niciun rand `R*`")
    return randuri, {"stare": st, "octeti": len(x)}


def d390(tok, tid):
    st, r = U.cere("POST", "/declaratii/d390", {"tenant_id": tid, "an": AN, "luna": LUNA}, tok,
                   timeout=240)
    x = _xml(r)
    if st != 200 or not x:
        return None, {"stare": st, "raspuns": str(r)[:400]}
    ops = [dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
           for m in re.finditer(r"<(?:\w+:)?operatie\b([^>]*)", x)]
    return ops, {"stare": st, "operatiuni": len(ops)}


def numar(v):
    try:
        return int(float(str(v or 0)))
    except ValueError:
        return 0


def main():
    tok, tid, schema = U.context(FIRMA)
    rez = {"firma": FIRMA, "tenant_id": tid, "schema": schema,
           "perioada": "%d-T%d / luna %d" % (AN, TRIM, LUNA), "lanturi": []}

    r0, m0 = d300(tok, tid)
    o0, mo0 = d390(tok, tid)
    rez["la_pornire"] = {"d300": m0, "d390": mo0}
    if r0 is None:
        rez["OPRIT"] = "D300 nu se genereaza la pornire"
        print(json.dumps(rez, indent=1, ensure_ascii=False))
        return 2

    def pas(nume, tip, valoare, rand, tip_d390):
        i = {"lant": nume, "ruta": "POST /tenants/{}/vanzare-ic", "tip": tip}
        inainte_r, _ = d300(tok, tid)
        inainte_o, _ = d390(tok, tid)
        corp = {"data": "%d-%02d-27" % (AN, LUNA), "valoare": valoare,
                "cod_tva_client": COD_CLIENT, "tip": tip, "dovada_transport": True}
        st, r = U.cere("POST", "/tenants/%d/vanzare-ic" % tid, corp, tok, timeout=180)
        i["raspuns"] = {"stare": st, "corp": str(r)[:300]}
        i["factura_id"] = (r or {}).get("factura_id") if isinstance(r, dict) else None
        dupa_r, md = d300(tok, tid)
        dupa_o, mo = d390(tok, tid)
        i["d300"] = md
        i["d390"] = mo
        a, b = numar((inainte_r or {}).get(rand)), numar((dupa_r or {}).get(rand))
        i["rand"] = {"nume": rand, "inainte": a, "dupa": b, "delta": b - a}
        tipuri_inainte = sorted(x.get("tip") for x in (inainte_o or []))
        tipuri_dupa = sorted(x.get("tip") for x in (dupa_o or []))
        i["d390_tipuri"] = {"inainte": tipuri_inainte, "dupa": tipuri_dupa}
        i["d390_are_tipul"] = tip_d390 in tipuri_dupa
        i["OK"] = (st in (200, 201) and bool(i["factura_id"])
                   and (b - a) == valoare and i["d390_are_tipul"])
        rez["lanturi"].append(i)

    pas("1 · vanzare IC de BUNURI 900 → factura, D300 R1_1 += 900, D390 tip L",
        "bunuri", 900, "R1_1", "L")
    pas("2 · vanzare IC de SERVICII 700 → factura, D300 R3_1 += 700, D390 tip P",
        "servicii", 700, "R3_1", "P")

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
