# -*- coding: utf-8 -*-
"""Proba R151 pe aplicația vie — cele două ramuri ale art. 291 alin. (5).

AȘTEPTAREA, SCRISĂ ÎNAINTE. Perechea e construită ca să DISCRIMINEZE, nu doar ca să treacă: aceleași
cifre, aceeași operațiune, singura diferență e ramura aleasă.

  livrarea:            2025-09-10  -> la data asta e în vigoare 21%
  factura/avansul:     2025-07-15  -> la data asta e în vigoare 19%
  cota declarată:      19

  · ramura `factura_avans`  -> **200**: cota se verifică la data facturii, unde 19% există;
  · ramura `fapt_generator` -> **422**: la 2025-09-10 nu există 19%.

*Dacă ambele ar trece, sau ambele ar cădea, data nu s-ar fi mutat cu ramura — și reparația ar fi
doar un câmp în plus.*

Și cele trei feluri de a nu ști, fiecare cu refuzul lui:
  · ramura nealeasă                       -> 422, numind AMÂNDOUĂ situațiile;
  · ramura de excepție fără data documentului -> 422, spunând de ce e obligatorie;
  · documentul DUPĂ livrare               -> 422 pentru CONTRADICȚIE, nu pentru lipsă — aici
    aplicația are amândouă datele, deci nu întreabă, arată.
"""
import json
import sys

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Comert Micro TVA SRL"
DATA_INCASARE = "2026-09-15"
LIVRARE = "2025-09-10"        # 21% în vigoare
DOCUMENT = "2025-07-15"       # 19% în vigoare
COTA = 19

rele = []


def cere(nume, corp, cod_asteptat, contine=None):
    tok, tid, _ = cere.ctx
    st, r = U.cere("POST", "/tenants/%d/nota-tva-incasare" % tid, dict(corp, tenant_id=tid), tok)
    mesaj = (r or {}).get("detail") if isinstance(r, dict) else str(r)
    ok = st == cod_asteptat
    if ok and contine:
        ok = all(c.lower() in str(mesaj).lower() for c in contine)
    print("%-46s %s %s" % (nume, "OK " if ok else "RAU", st))
    print("     %s" % str(mesaj if st != 200 else r)[:240])
    if not ok:
        rele.append((nume, cod_asteptat, st, str(mesaj)[:200]))
    return st, r


def main():
    cere.ctx = U.context(FIRMA)
    baza = {"data": DATA_INCASARE, "sens": "incasare", "suma_incasata": 1190,
            "cota": COTA, "data_fapt_generator": LIVRARE}

    print("== cele trei feluri de a nu ști ==")
    cere("ramura nealeasă -> refuz care numește ambele",
         baza, 422, ["291", "livrarea", "factur", "avans"])
    cere("excepție fără data documentului -> refuz",
         dict(baza, ramura_291_5="factura_avans"), 422, ["data", "291"])
    cere("document DUPĂ livrare -> CONTRADICȚIE, nu lipsă",
         dict(baza, ramura_291_5="factura_avans", data_factura_avans="2025-11-01"),
         422, ["înainte", "2025-11-01", LIVRARE])

    print()
    print("== perechea care DISCRIMINEAZĂ (aceleași cifre, altă ramură) ==")
    st1, r1 = cere("ramura EXCEPȚIE, cota 19 la data facturii -> intră",
                   dict(baza, ramura_291_5="factura_avans", data_factura_avans=DOCUMENT), 200)
    st2, _ = cere("ramura GENERALĂ, cota 19 la livrare -> refuz",
                  dict(baza, ramura_291_5="fapt_generator"), 422, ["19", "291"])

    if st1 == 200 and st2 == 422:
        print("\n  DISCRIMINEAZĂ: aceeași cerere, singura diferență e ramura, iar data cotei "
              "s-a mutat cu ea.")
    else:
        rele.append(("perechea nu discriminează", "200/422", "%s/%s" % (st1, st2), ""))

    print()
    print("== și ramura generală rămâne ce era (R149 neatins) ==")
    cere("ramura GENERALĂ cu cota corectă (21) -> intră",
         dict(baza, cota=21, ramura_291_5="fapt_generator"), 200)

    print("\nPROBA R151: %d nepotriviri" % len(rele))
    for x in rele:
        print("   RAU:", json.dumps(x, ensure_ascii=False)[:220])
    return 1 if rele else 0


if __name__ == "__main__":
    raise SystemExit(main())
