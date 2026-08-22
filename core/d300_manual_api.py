# -*- coding: utf-8 -*-
"""core/d300_manual_api.py — introducerea rândurilor manuale D300 (Decont TVA).

Geamăn cu d301_operatiuni_api / d390_clasificare_api: grilă lunară + adăugare + ștergere,
delegate din rute cu cere_cabinet. Rândurile pe care generatorul (core/d300.py) NU le derivă
din facturi (scutiri, regularizări, ajustări, cote istorice) se introduc de contabil și
PERSISTĂ în tabelul d300_manual — d300.genereaza le re-citește din DB pe calea de depunere
(paritate preview↔depunere).

CONTRACT rute:
  GET  /tenants/{id}/d300-manual?an&luna
       -> {randuri:[{id,rand,eticheta,baza,tva,descriere}],
           randuri_disponibile:[{cod,eticheta,cu_tva}]}
       randuri_disponibile = rândurile manual-acceptabile care NU sunt auto-derivate din
       facturi în perioadă ȘI nu sunt deja introduse (UNIQUE an,luna,rand).
  POST /tenants/{id}/d300-manual {an,luna,rand,baza,tva,descriere}
       -> validează rand ∈ allow-list ȘI nu e derivat automat (altfel 422 erori_campuri);
          upsert pe UNIQUE(an,luna,rand).
  DELETE /tenants/{id}/d300-manual/{rid}

UNITATE: LEI întregi (ca d300.py). baza=col.1, tva=col.2. Rândurile fără col.2 au tva=0.

SURSA ALLOW-LIST: identică cu prefixele acceptate manual în d300.calcul_d300 (colectată ~l.290,
deductibilă ~l.375). Rândurile COMPUTATE (R17/R27/R28/R31/R32/R33/R34/R37/R40/R41/R42) NU se
acceptă manual — nu apar aici.

SURSA ETICHETE: OPANAF 174/2026 (anaf_surse/opanaf_174_2026_d300.txt) + structura ANAF
(anaf_surse/d300_struct_anaf.txt, descrierea per cod R din col.2) — textul oficial cu diacritice,
nu rescris în JS. Fiecare etichetă e ancorată pe descrierea din structură (verificată la sursă).
"""
from core import afirmatii as _af  # [P8] statutul firmei e o afirmatie, nu un sir

# Rândurile de INTRARE acceptate manual (fără col.2 sunt marcate în _FARA_TVA). Sursă:
# d300.calcul_d300 allow-list (colectată + deductibilă). Ordinea = ordinea din formular.
COLECTATA = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8",
             "R12", "R13", "R14", "R15", "R16", "R64", "R65"]
DEDUCTIBILA = ["R18", "R19", "R20", "R21", "R23", "R25", "R26", "R29", "R30",
               "R35", "R36", "R38", "R39", "R43", "R44", "R72", "R73", "R75"]
ALLOW = COLECTATA + DEDUCTIBILA

# Rânduri FĂRĂ coloana 2 (TVA) — doar bază/valoare (col.2 absentă în structura ANAF).
# Sursă: d300_struct_anaf.txt (Rn_2 inexistent pentru aceste coduri).
_FARA_TVA = {"R1", "R2", "R3", "R4", "R13", "R14", "R15", "R26"}

# Etichete OFICIALE (diacritice). Sursă: OPANAF 174/2026 + d300_struct_anaf.txt (descriere per cod).
ETICHETE = {
    # --- COLECTATĂ ---
    "R1": "Livrări intracomunitare de bunuri, scutite conform art. 294 alin. (2) lit. a) și d) din Codul fiscal",
    "R2": "Regularizări livrări intracomunitare scutite conform art. 294 alin. (2) lit. a) și d) din Codul fiscal",
    "R3": "Livrări de bunuri sau prestări de servicii pentru care locul livrării/prestării este în afară României, precum și livrări intracomunitare de bunuri scutite conform art. 294 alin. (2) lit. b) și c) din Codul fiscal",
    "R4": "Regularizări privind prestările de servicii intracomunitare care nu beneficiază de scutire în statul membru în care taxa este datorată",
    "R5": "Achiziții intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA (taxare inversă)",
    "R6": "Regularizări privind achizițiile intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA (taxare inversă)",
    "R7": "Achiziții de bunuri, altele decât cele de la rd. 5 și 6, și achiziții de servicii pentru care beneficiarul din România este obligat la plată TVA (taxare inversă)",
    "R8": "Regularizări privind achizițiile de servicii intracomunitare pentru care beneficiarul este obligat la plată TVA (taxare inversă)",
    "R12": "Achiziții de bunuri și servicii supuse măsurilor de simplificare pentru care beneficiarul este obligat la plată TVA (taxare inversă)",
    "R13": "Livrări de bunuri și prestări de servicii supuse măsurilor de simplificare (taxare inversă)",
    "R14": "Livrări de bunuri și prestări de servicii scutite cu drept de deducere, altele decât cele de la rd. 1-3",
    "R15": "Livrări de bunuri și prestări de servicii scutite fără drept de deducere",
    "R16": "Regularizări taxă colectată",
    "R64": "Vânzări intracomunitare de bunuri la distanță și prestări de servicii de telecomunicații, radiodifuziune, televiziune sau furnizate pe cale electronică către persoane neimpozabile, pentru care locul livrării/prestării este în România (art. 278^1 alin. (1) din Codul fiscal)",
    "R65": "Regularizări privind vânzările intracomunitare de bunuri la distanță și prestările de servicii de telecomunicații, radiodifuziune, televiziune sau furnizate pe cale electronică (art. 278^1 alin. (1) din Codul fiscal)",
    # --- DEDUCTIBILĂ ---
    "R18": "Achiziții intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA (taxare inversă) — deductibil",
    "R19": "Regularizări privind achizițiile intracomunitare de bunuri pentru care cumpărătorul este obligat la plată TVA (taxare inversă)",
    "R20": "Achiziții de bunuri, altele decât cele de la rd. 20 și 21, și achiziții de servicii pentru care beneficiarul din România este obligat la plată TVA (taxare inversă) — deductibil",
    "R21": "Regularizări privind achizițiile de servicii intracomunitare pentru care beneficiarul din România este obligat la plată TVA (taxare inversă)",
    "R23": "Achiziții de bunuri și servicii, taxabile cu cota de 11% (deductibil)",
    "R25": "Achiziții de bunuri și servicii supuse măsurilor de simplificare pentru care beneficiarul este obligat la plată TVA (taxare inversă) — deductibil",
    "R26": "Achiziții de bunuri și servicii scutite de taxă sau neimpozabile",
    "R29": "TVA efectiv restituită cumpărătorilor străini, inclusiv comisionul unităților autorizate",
    "R30": "Regularizări taxă dedusă",
    "R35": "Soldul TVA de plată din decontul perioadei fiscale precedente, neachitat până la data depunerii decontului",
    "R36": "Diferențe de TVA de plată stabilite de organele fiscale prin decizie comunicată și neachitate până la data depunerii decontului",
    "R38": "Soldul sumei negative a TVA reportate din perioada precedentă pentru care nu s-a solicitat rambursarea",
    "R39": "Diferențe negative de TVA stabilite de organele de inspecție fiscală prin decizie comunicată",
    "R43": "Compensația în cotă forfetară pentru achiziții de produse și servicii agricole de la furnizori care aplică regimul special pentru agricultori",
    "R44": "Regularizări privind compensația în cotă forfetară",
    "R72": "Achiziții de bunuri și servicii supuse măsurilor de simplificare, taxabile cu cota de 9%",
    "R73": "Achiziții de bunuri supuse măsurilor de simplificare, taxabile cu cota de 5%",
    "R75": "Achiziții de bunuri și servicii deductibile, taxabile cu cota de 9%",
}


def _int(x):
    """LEI întregi, ca d300.py (fără default fabricat: text gol/None -> 0)."""
    if x is None or (isinstance(x, str) and not x.strip()):
        return 0
    from decimal import Decimal, ROUND_HALF_UP
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def randuri_derivate(conn, schema, an, luna):
    """Codurile de bază (R14, R5, …) pe care generatorul le DERIVĂ automat din facturi în
    perioadă — recalcul PUR fără manual (nu din DB), ca să vedem derivarea curată. Un rând
    derivat automat NU se poate introduce și manual (dublă numărare -> d300.calcul_d300 ridică
    ValueError). Întoarce set() de coduri de bază."""
    from core import d300
    from core.common import Perioada
    perioada = Perioada(int(an), luna=int(luna))
    prof, facturi = d300.pull(conn, schema, perioada)
    res = d300.calcul_d300(prof, perioada, facturi, manual=None)
    derivate = set()
    for cod in ALLOW:
        if (cod + "_1") in res.R or (cod + "_2") in res.R:
            derivate.add(cod)
    return derivate


def _disponibile(conn, schema, an, luna, deja):
    """Rândurile ofertabile: din allow-list, minus cele auto-derivate în perioadă, minus cele
    deja introduse (UNIQUE). Etichete din backend, cu diacritice."""
    derivate = randuri_derivate(conn, schema, an, luna)
    out = []
    for cod in ALLOW:
        if cod in derivate or cod in deja:
            continue
        out.append({"cod": cod, "eticheta": ETICHETE.get(cod, cod),
                    "cu_tva": cod not in _FARA_TVA})
    return out


def lista(conn, schema, an, luna):
    """Rândurile manuale ale perioadei + rândurile încă disponibile de adăugat."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"SELECT id, rand, baza, tva, descriere FROM {schema}.d300_manual "
                    f"WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        randuri = []
        deja = set()
        for r in cur.fetchall():
            deja.add(r["rand"])
            randuri.append({"id": r["id"], "rand": r["rand"],
                            "eticheta": ETICHETE.get(r["rand"], r["rand"]),
                            "baza": int(r["baza"] or 0), "tva": int(r["tva"] or 0),
                            "descriere": r["descriere"] or "",
                            "cu_tva": r["rand"] not in _FARA_TVA})
    return {"randuri": randuri,
            "randuri_disponibile": _disponibile(conn, schema, an, luna, deja)}


def adauga(conn, schema, an, luna, d):
    """Validează și face upsert pe UNIQUE(an,luna,rand). Colectează TOATE erorile de câmp
    (field-keyed pentru erori_campuri, contract [G10] ca la d301)."""
    # [gard consistenta vector<->D300, audit tenant_006] D300 (decontul de TVA) e pentru PLATITORI.
    # Daca platitor_tva=False, D300 e blocat in selector -> nu acceptam randuri manuale (altfel stare
    # inconsistenta ca la D301). Simetric cu d301_operatiuni_api / d390_clasificare_api.
    with conn.cursor() as _cur:
        _cur.execute(f"SELECT platitor_tva FROM {schema}.firma_profil WHERE id=1")
        _pr = _cur.fetchone()
    if _pr and _pr[0] is False:
        _t = ("Firma NU e înregistrată în scopuri de TVA — D300 (decontul de TVA) se "
              "depune doar de plătitori. Dacă firma e de fapt plătitoare, corectează "
              "înregistrarea în scopuri de TVA în Vectorul fiscal.")
        return dict(_af.afirmatie("statut", "d300", _t,
                                  statut="neplatitor_tva", statut_din=None), eroare=_t)
    erori = []
    rand = (d.get("rand") or "").strip().upper()
    if not rand:
        erori.append(("rand", "Alege rândul D300 de introdus."))
    elif rand not in ALLOW:
        erori.append(("rand", "Rândul %r nu e un rând de intrare acceptat manual (rândurile "
                              "computate — R17/R27/R32/R34 etc. — se calculează automat, nu se "
                              "introduc)." % rand))
    baza = tva = None
    try:
        baza = _int(d.get("baza"))
    except (TypeError, ValueError, ArithmeticError):
        erori.append(("baza", "Baza (col. 1) trebuie să fie un număr întreg de lei."))
    try:
        tva = _int(d.get("tva"))
    except (TypeError, ValueError, ArithmeticError):
        erori.append(("tva", "TVA (col. 2) trebuie să fie un număr întreg de lei."))
    if rand in _FARA_TVA and tva:
        erori.append(("tva", "Rândul %s nu are coloană de TVA — completează doar baza." % rand))
    if baza is not None and tva is not None and not baza and not tva:
        erori.append(("baza", "Completează cel puțin o valoare (bază sau TVA) — un rând gol nu "
                              "apare în decont."))
    # anti-dublă-numărare: rând deja derivat automat din facturi în perioadă -> refuz.
    if rand in ALLOW and not any(c == "rand" for c, _m in erori):
        try:
            derivate = randuri_derivate(conn, schema, an, luna)
        except Exception:  # noqa: BLE001 — derivarea nu trebuie să blocheze introducerea
            derivate = set()
        if rand in derivate:
            erori.append(("rand", "Rândul %s e deja DERIVAT automat din facturile perioadei "
                                  "(dublă numărare interzisă). Corectează facturile sau alege alt "
                                  "rând." % rand))
    if erori:
        return {"eroare": "; ".join(m for _c, m in erori),
                "erori_campuri": [{"camp": c, "mesaj": m} for c, m in erori]}
    descriere = (d.get("descriere") or "").strip() or None
    with conn.cursor() as cur:
        # upsert-ok: editare rand D300 manual pe (an,luna,rand) - re-scrierea aceluiasi rand
        cur.execute(f"""INSERT INTO {schema}.d300_manual (an, luna, rand, baza, tva, descriere)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (an, luna, rand)
                        DO UPDATE SET baza=EXCLUDED.baza, tva=EXCLUDED.tva,
                                      descriere=EXCLUDED.descriere
                        RETURNING id""",
                    (an, luna, rand, baza, tva, descriere))
        rid = cur.fetchone()[0]
    conn.commit()
    return {"ok": True, "id": rid, "rand": rand, "baza": baza, "tva": tva}


def sterge(conn, schema, rid):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.d300_manual WHERE id=%s", (rid,))
        ok = cur.rowcount > 0
    conn.commit()
    return {"ok": ok}


def incarca_manual(conn, schema, an, luna):
    """Dict-ul `manual` pentru d300.calcul_d300, citit din DB (persistat). Chei Rxx_1 (bază) și
    Rxx_2 (TVA), doar valorile nenule — exact forma pe care o consumă allow-list-ul din calcul_d300.
    Folosit de d300.genereaza când param `manual` e None (calea de depunere /coada)."""
    out = {}
    with conn.cursor() as cur:
        cur.execute(f"SELECT rand, baza, tva FROM {schema}.d300_manual WHERE an=%s AND luna=%s",
                    (an, luna))
        for rand, baza, tva in cur.fetchall():
            if baza:
                out[rand + "_1"] = int(baza)
            if tva:
                out[rand + "_2"] = int(tva)
    return out
