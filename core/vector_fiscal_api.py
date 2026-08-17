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
            "       nume, cui, inreg_art317, platitor_tva_anaf_inceput, tip_firma "
            "  FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {"ok": False, "cod": "FARA_PROFIL"}
    regim, tva, decont, ic, nume, cui, art317, tva_inceput, tip_firma = r
    # [regim] partida simpla (PFA/II/PFL) NU are regim micro/profit -> frontendul nu cere regimul acolo
    # (fapt UNIC: regim_contabil, aceeasi sursa ca la salveaza). Vezi DECIZII 23.07.
    partida_simpla = regim_contabil(tip_firma_nrm(tip_firma)) == "simpla"
    completat = bool(regim)  # regim_fiscal e obligatoriu -> daca exista, vectorul e setat
    return {
        "ok": True,
        "nume": nume, "cui": cui,
        "regim_fiscal": regim,
        "platitor_tva": bool(tva) if tva is not None else None,
        "tip_decont": decont,
        # None = necompletat (nu False tacit) -> frontendul distinge "nesetat" de "Nu" (fara preselectie). Vezi DECIZII 23.07.
        "operatiuni_ic": bool(ic) if ic is not None else None,
        "inreg_art317": bool(art317),
        # [tva_inceput] data inregistrarii in scopuri de TVA (fapt ANAF sau introdusa manual de contabil) ca
        # ISO 'YYYY-MM-DD' -> pre-populeaza formularul; motorul o foloseste ca margine pt D300/D394/D406.
        "tva_data_inceput": tva_inceput.isoformat() if tva_inceput else None,
        "partida_simpla": partida_simpla,
        "completat": completat,
    }


def salveaza(conn_schema, regim_fiscal, platitor_tva, tip_decont, operatiuni_ic,
             nume=None, cui=None, inreg_art317=False, tva_data_inceput=None):  # [p83_upsert] UPSERT
    """Scrie vectorul. Valideaza valorile. Daca nu e platitor TVA, decontul devine NULL.
    Daca randul firma_profil (id=1) nu exista, il creeaza (nume+cui obligatorii la insert)."""
    regim_in = (regim_fiscal or "").strip().lower()

    # platitor_tva OBLIGATORIU (ca operatiuni_ic) - decide obligatia D300/D394. Fara default tacit:
    # None (necompletat) -> eroare, nu False. Altfel selectul fara optiune-placeholder din Date firma
    # trimitea "Nu" pe firma cu platitor_tva=NULL si se persista o alegere pe care contabilul n-a facut-o
    # (Regula 4). Vezi DECIZII 23.07 + DESIGN_SYSTEM cap.17; simetric cu operatiuni_ic de mai jos.
    if platitor_tva is None:
        return {"ok": False, "cod": "TVA_LIPSA",
                "mesaj": "Înregistrată în scopuri de TVA: alege Da sau Nu (obligatoriu)."}
    tva = bool(platitor_tva)
    # operatiuni_ic OBLIGATORIU la migrare (ca tip_decont) - decide obligatia D390. Fara default tacit:
    # None (necompletat) -> eroare, nu False. Vezi DECIZII 23.07 + DESIGN_SYSTEM cap.17.
    if operatiuni_ic is None:
        return {"ok": False, "cod": "IC_LIPSA",
                "mesaj": "Operațiuni intracomunitare: alege Da sau Nu (obligatoriu)."}
    ic = bool(operatiuni_ic)
    art317 = bool(inreg_art317)   # [art.317] inregistrare speciala scopuri TVA (art. 317 CF)

    # [tva_inceput] data inregistrarii in scopuri de TVA (de pe certificatul ANAF). Are sens DOAR la platitor
    # (la neplatitor -> NULL, nu se stocheaza). Accepta ISO 'YYYY-MM-DD' sau None; format invalid -> eroare
    # explicita (nu stocam gunoi si nu ghicim).
    tva_inceput = None
    if tva:
        _di = tva_data_inceput.strip() if isinstance(tva_data_inceput, str) else tva_data_inceput
        if _di:
            import datetime as _dt
            try:
                tva_inceput = _dt.date.fromisoformat(_di).isoformat()
            except (ValueError, TypeError):
                return {"ok": False, "cod": "TVA_INCEPUT_INVALID",
                        "mesaj": "Data înregistrării în scopuri de TVA trebuie în formatul AAAA-LL-ZZ (ex. 2020-01-15)."}

    decont = (tip_decont or "").strip().lower()
    if tva:
        if decont not in _DECONTURI:
            return {"ok": False, "cod": "DECONT_INVALID",
                    "mesaj": "tip_decont trebuie să fie 'lunar' sau 'trimestrial' pentru plătitor TVA"}
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
                        "mesaj": "regim_fiscal trebuie să fie 'micro' sau 'profit'"}
            regim = regim_in
        if exista:
            cur.execute(
                "UPDATE firma_profil "
                "   SET regim_fiscal = %s, platitor_tva = %s, "
                "       tip_decont = %s, operatiuni_ic = %s, inreg_art317 = %s, "
                "       platitor_tva_anaf_inceput = %s "
                " WHERE id = 1",
                (regim, tva, decont, ic, art317, tva_inceput))
        else:
            if not nume or not cui:
                return {"ok": False, "cod": "FARA_IDENTITATE",
                        "mesaj": "firma_profil gol și lipsesc nume/cui pentru creare"}
            cur.execute(
                "INSERT INTO firma_profil (id, nume, cui, regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, inreg_art317, platitor_tva_anaf_inceput) "
                "VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s)",
                (nume, cui, regim, tva, decont, ic, art317, tva_inceput))
    return {"ok": True, "regim_fiscal": regim, "platitor_tva": tva,
            "tip_decont": decont, "operatiuni_ic": ic, "inreg_art317": art317,
            "tva_data_inceput": tva_inceput}
