# -*- coding: utf-8 -*-
"""
core/control_incrucisat.py — verificare INCRUCISATA declaratie vs contabilitate.

Raspunde la intrebarea centrala a produsului: "ce declar la ANAF corespunde cu
ce am in evidenta?". Verificatoarele existente lucreaza IN INTERIORUL unei surse
(verificatoare.py pe balanta, control_fiscal_api pe termene); acesta compara INTRE surse.

PRINCIPII (stabilite 15.07.2026):
1. TREI stari, nu doua: verde (verificat, coerent), rosu (verificat, divergent),
   GRI (NU AM PUTUT verifica - lipsesc date). Un audit care nu poate spune "nu stiu"
   nu e audit; verdele tacit peste date lipsa e minciuna prin omisiune.
2. Fiecare constatare isi declara TEMEIUL si LIMITA (ce sursa, ce date, ce perioada).
3. Remediu in trei feluri:
   - executabil: cauza DOVEDITA mecanic -> se poate propune actiunea exacta
   - sugerat: cauza probabila -> omul verifica si confirma
   - investigatie: cauze multiple -> ce sa compare, FARA buton
   NICIODATA "ajusteaza contul ca sa dea verde": verdele se castiga prin adevar,
   nu prin cosmetizare. Un sistem care invata contabilul sa forteze semaforul e mai
   rau decat lipsa lui.

Regula fiscala: D300 se calculeaza pe FACTURILE lunii (fapt generator, art. 281 CF),
balanta pe INREGISTRARILE contabile. Divergenta apare cand facturi emise nu sunt
contabilizate. Nu e automat eroare - e semnal ca evidenta a ramas in urma.

Comparatie TVA:
  D300 R17_2 (colectata)  <->  rulaj CREDIT 4427 pe luna
  D300 R31_2 (dedusa)     <->  rulaj DEBIT  4426 pe luna

Regula EVIDENTA (15.07.2026): rulajele se citesc DOAR din note cu status='validata'.
Nota in ciorna e o PROPUNERE (nu a trecut patru-ochi), nu evidenta contabila. Daca ar
intra in rulaj, verdele ar fi IMPRUMUTAT: sistemul ar confirma coerenta pe baza a ceva
ce inca nu s-a intamplat. O factura cu nota ciorna ramane "necontabilizata" -> rosu, cu
remediu SUGERAT (asteapta validare), nu executabil (nota exista deja, nu se dubleaza).
"""
from decimal import Decimal

TOLERANTA = Decimal("1")  # 1 leu: D300 rotunjeste la leu, contabilitatea are bani
MODUL = "control_incrucisat"
REGULI = "2026.2"


def _d(v):
    return Decimal(str(v or 0))


def rulaje_luna(conn, schema, an, luna, conturi):
    """Rulaje DEBIT/CREDIT pe LUNA (nu cumulat) pentru conturile date.
    Cumulatul din documente_api.balanta() NU se poate compara cu D300 (care e lunar).
    DOAR note validate: ciorna nu e evidenta (vezi Regula EVIDENTA in capul modulului)."""
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    out = {c: {"debit": Decimal("0"), "credit": Decimal("0")} for c in conturi}
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT l.cont_debit AS cont, SUM(l.suma) AS s, 'debit' AS sens
            FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE i.data >= %s AND i.data < %s AND i.status = 'validata'
              AND l.cont_debit = ANY(%s)
            GROUP BY l.cont_debit
            UNION ALL
            SELECT l.cont_credit, SUM(l.suma), 'credit'
            FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE i.data >= %s AND i.data < %s AND i.status = 'validata'
              AND l.cont_credit = ANY(%s)
            GROUP BY l.cont_credit
        """, (inceput, sfarsit, list(conturi), inceput, sfarsit, list(conturi)))
        for cont, suma, sens in cur.fetchall():
            if cont in out:
                out[cont][sens] += _d(suma)
    return out


def facturi_necontabilizate(conn, schema, an, luna):
    """Facturile lunii FARA inregistrare VALIDATA - cauza dovedibila a divergentei.
    are_ciorna=True -> nota exista dar asteapta patru-ochi: NU se recontabilizeaza."""
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.id, f.numar, f.directie, f.total, f.tva, f.tert_nume,
                   EXISTS (SELECT 1 FROM {schema}.inregistrari ic
                           WHERE ic.factura_id = f.id AND ic.status = 'ciorna') AS are_ciorna
            FROM {schema}.facturi f
            WHERE f.data_emitere >= %s AND f.data_emitere < %s
              AND NOT EXISTS (SELECT 1 FROM {schema}.inregistrari i
                              WHERE i.factura_id = f.id AND i.status = 'validata')
            ORDER BY f.id
        """, (inceput, sfarsit))
        return [dict(r) for r in cur.fetchall()]


def _explicatie(necontate):
    fara = [f for f in necontate if not f.get("are_ciorna")]
    ciorne = [f for f in necontate if f.get("are_ciorna")]
    parti = []
    if fara:
        parti.append(f"{len(fara)} facturi ale lunii nu sunt contabilizate")
    if ciorne:
        parti.append(f"{len(ciorne)} au note în ciornă, în așteptarea validării")
    return ("; ".join(parti) + ".") if parti else ""


def compara_tva(d300_R, rulaje, necontate=None):
    """PURA: compara randurile D300 cu rulajele contabile.
    necontate: facturi FARA nota validata, fiecare cu are_ciorna (nota propusa, nevalidata).
    Ciorna nu intra in rulaj si NU inchide constatarea: verdele vine dupa patru-ochi."""
    necontate = necontate or []
    perechi = (
        ("TVA colectată", "R17_2", "4427", "credit", "emisa", "emise"),
        ("TVA deductibilă", "R31_2", "4426", "debit", "primita", "primite"),
    )
    rez = []
    for eticheta, rand, cont, sens, directie, fel in perechi:
        decl = _d(d300_R.get(rand, 0))
        contabil = _d(rulaje.get(cont, {}).get(sens, 0))
        dif = decl - contabil
        grup = [f for f in necontate if f.get("directie") == directie]
        fara_nota = [f for f in grup if not f.get("are_ciorna")]
        cu_ciorna = [f for f in grup if f.get("are_ciorna")]
        tva_grup = sum(_d(f.get("tva")) for f in grup)
        temei = (f"D300 rând {rand} (facturi {fel} în lună, art. 281 CF) vs "
                 f"rulaj {sens} cont {cont} pe lună, numai note validate "
                 f"(ciorna e propunere, nu evidență).")
        mesaj = (f"{eticheta}: D300 declară {decl} lei, contul {cont} are {contabil} lei "
                 f"(diferență {dif} lei).")
        baza = {"eticheta": eticheta, "declarat": decl, "contabil": contabil,
                "diferenta": dif, "temei": temei}
        if abs(dif) <= TOLERANTA:
            rez.append(dict(baza, stare="verde",
                            mesaj=f"{eticheta}: D300 și contul {cont} coincid.",
                            remediu=None))
            continue
        # cauza DOVEDITA: diferenta se explica exact prin facturile fara nota validata
        if tva_grup and abs(dif - tva_grup) <= TOLERANTA:
            if fara_nota:
                cauza = f"{len(fara_nota)} facturi {fel} nu sunt contabilizate"
                if cu_ciorna:
                    cauza += f", iar {len(cu_ciorna)} au note în ciornă, neconfirmate"
                cauza += f"; TVA-ul lor ({tva_grup} lei) explică exact diferența."
                rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                    "fel": "executabil", "cauza": cauza,
                    "actiune": "Contabilizează facturile listate.",
                    "facturi": [f["id"] for f in fara_nota],
                }))
            else:
                rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                    "fel": "sugerat",
                    "cauza": (f"{len(cu_ciorna)} note ciornă create, așteaptă validare; "
                              f"TVA-ul lor ({tva_grup} lei) explică exact diferența."),
                    "actiune": ("Un al doilea utilizator validează notele (patru ochi). "
                                "Până atunci operațiunile nu sunt în evidență."),
                    "facturi": [],
                }))
            continue
        # cauza NEDOVEDITA: nu propunem ajustari - spunem ce sa verifice
        rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
            "fel": "investigatie",
            "cauza": "Diferența nu se explică integral prin facturi necontabilizate.",
            "actiune": ("Verifică: note manuale pe cont, storno neînregistrat, "
                        "TVA la încasare (exigibilitate decalată), regularizări, "
                        "facturi cu data în altă lună decât înregistrarea."),
            "facturi": [],
        }))
    return rez


def verifica_tva(conn, schema, an, luna):
    """Verificare TVA: D300 vs contabilitate + cauza + remediu.
    Conexiunea trebuie pozitionata pe schema: get_conn(schema) (ca la declaratii).
    Intoarce si starea GRI daca D300 nu se poate genera (nu ascunde necunoscutul)."""
    from core import d300 as _d300
    try:
        _xml, res = _d300.genereaza(conn, schema, an, luna)
    except Exception as e:
        return {"an": an, "luna": luna, "stare": "gri",
                "constatari": [{
                    "stare": "gri", "eticheta": "TVA", "temei": "D300 nu s-a putut genera.",
                    "mesaj": f"NU pot verifica TVA: decontul nu se poate calcula ({e}).",
                    "remediu": {"fel": "investigatie",
                                "cauza": "Date lipsă sau profil fiscal incomplet.",
                                "actiune": "Completează profilul firmei și reîncearcă.",
                                "facturi": []},
                }],
                "facturi_necontabilizate": [], "explicatie": "",
                "limita": "Verificarea TVA nu a fost efectuată — riscul rămâne neacoperit."}

    R = res["R"] if isinstance(res, dict) else getattr(res, "R", {})
    necontate = facturi_necontabilizate(conn, schema, an, luna)
    rulaje = rulaje_luna(conn, schema, an, luna, ("4427", "4426"))
    constatari = compara_tva(R, rulaje, necontate)
    stare = "rosu" if any(c["stare"] == "rosu" for c in constatari) else "verde"
    return {
        "an": an, "luna": luna, "stare": stare, "constatari": constatari,
        "facturi_necontabilizate": necontate,
        "explicatie": _explicatie(necontate),
        "limita": ("Verificat: D300 (calculat din facturile lunii) vs conturile 4427/4426. "
                   "Evidența = note validate; ciornele nu intră în rulaj. "
                   "NEVERIFICAT: dacă D300 depus efectiv la ANAF coincide cu cel calculat aici "
                   "(necesită SPV)."),
        "modul": MODUL, "reguli": REGULI,
    }
