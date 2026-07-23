"""
core/vector_fiscal_api.py — vectorul fiscal al unei firme.
Cei 4 atribute din firma_profil (id=1 in schema tenant) care decid ce
declaratii datoreaza firma: regim_fiscal, platitor_tva, tip_decont, operatiuni_ic.

Fara ele, firma e neprocesabila (control fiscal = gri). Acest modul le
citeste si le scrie. Conexiunea vine deja pe schema tenant (search_path setat).

Valori acceptate de motor (control_fiscal_api.declaratii_datorate):
  regim_fiscal: "micro" (-> D100 trimestrial) | "profit" (-> D101 anual)
  tip_decont:   "lunar" | "trimestrial" (doar daca platitor_tva -> D300)
  platitor_tva: bool (-> D300)
  operatiuni_ic: bool (-> D390 lunar)
"""

from core.migrare_api import regim_contabil, tip_firma_nrm  # [regim] fapt UNIC + normalizare tip_firma (default 'srl')

_REGIMURI = ("micro", "profit")
_DECONTURI = ("lunar", "trimestrial")


def citeste(conn_schema):
    """Intoarce vectorul curent al firmei (id=1) + flag 'completat'."""
    with conn_schema.cursor() as cur:
        cur.execute(
            "SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, "
            "       nume, cui "
            "  FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {"ok": False, "cod": "FARA_PROFIL"}
    regim, tva, decont, ic, nume, cui = r
    completat = bool(regim)  # regim_fiscal e obligatoriu -> daca exista, vectorul e setat
    return {
        "ok": True,
        "nume": nume, "cui": cui,
        "regim_fiscal": regim,
        "platitor_tva": bool(tva) if tva is not None else None,
        "tip_decont": decont,
        "operatiuni_ic": bool(ic) if ic is not None else False,
        "completat": completat,
    }


def salveaza(conn_schema, regim_fiscal, platitor_tva, tip_decont, operatiuni_ic,
             nume=None, cui=None):  # [p83_upsert] UPSERT
    """Scrie vectorul. Valideaza valorile. Daca nu e platitor TVA, decontul devine NULL.
    Daca randul firma_profil (id=1) nu exista, il creeaza (nume+cui obligatorii la insert)."""
    regim_in = (regim_fiscal or "").strip().lower()

    tva = bool(platitor_tva)
    ic = bool(operatiuni_ic)

    decont = (tip_decont or "").strip().lower()
    if tva:
        if decont not in _DECONTURI:
            return {"ok": False, "cod": "DECONT_INVALID",
                    "mesaj": "tip_decont trebuie sa fie 'lunar' sau 'trimestrial' pentru platitor TVA"}
    else:
        decont = None

    with conn_schema.cursor() as cur:
        # tip_firma se citeste SERVER-SIDE din firma_profil (NU vine din client). Rand absent -> INSERT
        # cu default 'srl' (partida dubla).
        cur.execute("SELECT tip_firma FROM firma_profil WHERE id = 1")
        _r = cur.fetchone()
        exista = _r is not None
        tip_firma = tip_firma_nrm(_r[0] if exista else None)   # default 'srl' -> primitiva, nu literal inline
        # regim CIT dupa MODUL de contabilitate (partida simpla/dubla), nu dupa ce trimite clientul:
        if regim_contabil(tip_firma) == "simpla":
            # PFA/II/PFL n-are regim CIT (impozit pe venit prin D212). Gol -> NULL valid; valoare ne-goala
            # -> eroare explicita (nu stocam micro/profit inexistent la partida simpla). Vezi DECIZII 23.07.
            if regim_in:
                return {"ok": False, "cod": "REGIM_LA_PARTIDA_SIMPLA",
                        "mesaj": "Firmă în partidă simplă (PFA/II/PFL) — nu are regim micro/profit; lasă regimul gol."}
            regim = None
        else:
            if regim_in not in _REGIMURI:
                return {"ok": False, "cod": "REGIM_INVALID",
                        "mesaj": "regim_fiscal trebuie sa fie 'micro' sau 'profit'"}
            regim = regim_in
        if exista:
            cur.execute(
                "UPDATE firma_profil "
                "   SET regim_fiscal = %s, platitor_tva = %s, "
                "       tip_decont = %s, operatiuni_ic = %s "
                " WHERE id = 1",
                (regim, tva, decont, ic))
        else:
            if not nume or not cui:
                return {"ok": False, "cod": "FARA_IDENTITATE",
                        "mesaj": "firma_profil gol si lipsesc nume/cui pentru creare"}
            cur.execute(
                "INSERT INTO firma_profil (id, nume, cui, regim_fiscal, platitor_tva, tip_decont, operatiuni_ic) "
                "VALUES (1, %s, %s, %s, %s, %s, %s)",
                (nume, cui, regim, tva, decont, ic))
    return {"ok": True, "regim_fiscal": regim, "platitor_tva": tva,
            "tip_decont": decont, "operatiuni_ic": ic}
