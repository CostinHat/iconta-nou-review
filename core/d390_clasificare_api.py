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
from core import afirmatii as _af  # [P8] statutul e o afirmatie
from decimal import Decimal
from core.d390 import TARI_UE, TIPURI, TIPURI_DIRECTIE, operatiuni_auto, pull, pull_manual, pull_reclasificari

# TIPURI_DIRECTIE: sursa unica in core.d390 (regula de tranzitie, importata mai sus)
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
            # upsert-ok: override reclasificare D390 pe (an,luna,directie,tara,cod) - set intentionat
            cur.execute(f"""INSERT INTO {schema}.d390_reclasificare (an,luna,directie,tara,cod,tip)
                            VALUES (%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (an,luna,directie,tara,cod) DO UPDATE SET tip=EXCLUDED.tip""",
                        (an, luna, directie, tara, cod, tip))
    conn.commit()
    return {"ok": True}


def manual_adauga(conn, schema, an, luna, tip, tara, cod, den, baza):
    """Adaugă o linie pur manuală (P/S/T/R). Validează tip/țară/cod/bază."""
    # [gard consistenta vector<->D390, audit tenant_006] D390 e pentru firme cu operatiuni IC.
    # Daca operatiuni_ic=False, D390 e blocat in selector -> nu acceptam linii manuale. Simetric d300/d301.
    with conn.cursor() as _cur:
        _cur.execute(f"SELECT operatiuni_ic FROM {schema}.firma_profil WHERE id=1")
        _pr = _cur.fetchone()
    if _pr and _pr[0] is False:
        _t = ("Firma nu are operațiuni intracomunitare în Vectorul fiscal — D390 "
              "(declarația recapitulativă) nu i se aplică. Dacă firma face operațiuni "
              "intracomunitare, marchează-le în Vectorul fiscal.")
        return dict(_af.afirmatie("statut", "d390", _t,
                                  statut="fara_operatiuni_ic", statut_din=None), eroare=_t)
    # [G10 rule2/4] colecteaza TOATE erorile de camp (nu fail-fast), field-keyed.
    tip = (tip or "").strip().upper()
    tara = (tara or "").strip().upper()
    cod = (cod or "").strip()
    erori = []
    # [NOTA 1, OPANAF 394/2017 anexa2 instructiuni:189-201] Achizitia IC de bunuri de la un furnizor UE
    # care NU comunica un cod valabil de TVA se declara ca tip A cu tara statului membru din care s-au
    # transportat bunurile si COD GOL (A nu e in _CU_COD_OBLIG -> cod optional). Calea auto n-o poate
    # detecta (factura fara cod valid n-are camp de tara), deci se introduce manual de contabil.
    if tip not in ("A", "P", "S", "T", "R"):
        erori.append(("tip", "Tip linie manuală: A (achiziție bunuri IC fără cod furnizor, NOTA 1) / "
                             "P / S / T / R (servicii/triangulație/agricol)."))
    if tara not in TARI_UE:
        erori.append(("tara", "Țara %r nu e în nomenclatorul UE." % tara))
    if tip in _CU_COD_OBLIG and not cod:
        erori.append(("cod", "Codul partenerului (fără prefix țară) e obligatoriu pentru %s." % tip))
    b = None
    try:
        b = Decimal(str(baza or 0))
    except Exception:
        erori.append(("baza", "Bază invalidă."))
    if erori:
        return {"eroare": "; ".join(m for _c, m in erori),
                "erori_campuri": [{"camp": c, "mesaj": m} for c, m in erori]}
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
