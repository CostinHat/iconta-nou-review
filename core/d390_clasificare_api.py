# -*- coding: utf-8 -*-
"""
core/d390_clasificare_api.py — [F125] clasificarea manuală D390 (reclasificare + adăugare).

Auto-maparea (d390.calcul_d390) pune orice factură IC pe BUNURI (emisă->L, primită->A). Contabilul:
  - RECLASIFICĂ o operațiune auto (partener + direcție) la alt tip legal pentru acea direcție
    (emisă: L/T/P/R; primită: A/S) — override, NU adaugă → fără dublă numărare (DECIZII 21.07 F125);
  - ADAUGĂ linii pur manuale (P/S/T/R fără factură în sistem).

Validează tranzițiile la sursă (nu se poate face o achiziție să fie livrare). Codul partenerului
(codO) e obligatoriu pentru L/T/P/R (ca în d390.valideaza), opțional pentru S/A.
"""
from decimal import Decimal
from core.d390 import TARI_UE, TIPURI, operatiuni_auto, pull, pull_manual, pull_reclasificari

# tipurile legale per direcție (emisă = livrări; primită = achiziții)
TIPURI_DIRECTIE = {"emisa": ("L", "T", "P", "R"), "primita": ("A", "S")}
_CU_COD_OBLIG = ("L", "T", "P", "R")  # codO obligatoriu (ca d390.valideaza)


def stare(conn, schema, an, luna):
    """Imaginea completă pt UI: operațiunile auto (cu tipul curent) + liniile manuale."""
    prof, facturi = pull(conn, schema, an, luna)
    recl = pull_reclasificari(conn, schema, an, luna)
    return {
        "auto": operatiuni_auto(facturi, recl),
        "manual": [dict(m, baza=float(m["baza"])) for m in pull_manual(conn, schema, an, luna)],
    }


def salveaza_reclasificare(conn, schema, an, luna, directie, tara, cod, tip):
    """Upsert override-ul de tip pe o operațiune auto. tip == default (L emisă / A primită) ->
    șterge override-ul (revine la auto). Validează direcția și tranziția."""
    directie = (directie or "").strip()
    if directie not in TIPURI_DIRECTIE:
        return {"eroare": "direcție invalidă: %r" % directie}
    tip = (tip or "").strip().upper()
    if tip not in TIPURI_DIRECTIE[directie]:
        return {"eroare": "tip %r nepermis pentru %s (permise: %s)"
                % (tip, directie, "/".join(TIPURI_DIRECTIE[directie]))}
    tara = (tara or "").strip().upper()
    cod = (cod or "").strip()
    tip_def = "L" if directie == "emisa" else "A"
    with conn.cursor() as cur:
        if tip == tip_def:  # revine la auto -> nu mai ține override
            cur.execute(f"DELETE FROM {schema}.d390_reclasificare "
                        f"WHERE an=%s AND luna=%s AND directie=%s AND tara=%s AND cod=%s",
                        (an, luna, directie, tara, cod))
        else:
            cur.execute(f"""INSERT INTO {schema}.d390_reclasificare (an,luna,directie,tara,cod,tip)
                            VALUES (%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (an,luna,directie,tara,cod) DO UPDATE SET tip=EXCLUDED.tip""",
                        (an, luna, directie, tara, cod, tip))
    conn.commit()
    return {"ok": True}


def manual_adauga(conn, schema, an, luna, tip, tara, cod, den, baza):
    """Adaugă o linie pur manuală (P/S/T/R). Validează tip/țară/cod/bază."""
    tip = (tip or "").strip().upper()
    if tip not in ("P", "S", "T", "R"):
        return {"eroare": "tip linie manuală trebuie P/S/T/R (servicii/triangulație/agricol)"}
    tara = (tara or "").strip().upper()
    if tara not in TARI_UE:
        return {"eroare": "țara %r nu e în nomenclatorul UE" % tara}
    cod = (cod or "").strip()
    if tip in _CU_COD_OBLIG and not cod:
        return {"eroare": "codul partenerului (fără prefix țară) e obligatoriu pentru %s" % tip}
    try:
        b = Decimal(str(baza or 0))
    except Exception:
        return {"eroare": "bază invalidă"}
    den = (den or "")[:200]
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.d390_manual (an,luna,tip,tara,cod,den,baza)
                        VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (an, luna, tip, tara, cod, den, b))
        mid = cur.fetchone()[0]
    conn.commit()
    return {"ok": True, "id": mid}


def manual_sterge(conn, schema, an, luna, id):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.d390_manual WHERE id=%s AND an=%s AND luna=%s",
                    (id, an, luna))
        ok = cur.rowcount > 0
    conn.commit()
    return {"ok": ok}
