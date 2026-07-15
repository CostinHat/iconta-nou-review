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
"""
from decimal import Decimal

TOLERANTA = Decimal("1")  # 1 leu: D300 rotunjeste la leu, contabilitatea are bani
MODUL = "control_incrucisat"
REGULI = "2026.1"


def _d(v):
    return Decimal(str(v or 0))


def rulaje_luna(conn, schema, an, luna, conturi):
    """Rulaje DEBIT/CREDIT pe LUNA (nu cumulat) pentru conturile date.
    Cumulatul din documente_api.balanta() NU se poate compara cu D300 (care e lunar)."""
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    out = {c: {"debit": Decimal("0"), "credit": Decimal("0")} for c in conturi}
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT l.cont_debit AS cont, SUM(l.suma) AS s, 'debit' AS sens
            FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE i.data >= %s AND i.data < %s AND l.cont_debit = ANY(%s)
            GROUP BY l.cont_debit
            UNION ALL
            SELECT l.cont_credit, SUM(l.suma), 'credit'
            FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE i.data >= %s AND i.data < %s AND l.cont_credit = ANY(%s)
            GROUP BY l.cont_credit
        """, (inceput, sfarsit, list(conturi), inceput, sfarsit, list(conturi)))
        for cont, suma, sens in cur.fetchall():
            if cont in out:
                out[cont][sens] += _d(suma)
    return out


def facturi_necontabilizate(conn, schema, an, luna):
    """Facturile lunii FARA inregistrare contabila - cauza dovedibila a divergentei."""
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.id, f.numar, f.directie, f.total, f.tva, f.tert_nume
            FROM {schema}.facturi f
            WHERE f.data_emitere >= %s AND f.data_emitere < %s
              AND NOT EXISTS (SELECT 1 FROM {schema}.inregistrari i WHERE i.factura_id = f.id)
            ORDER BY f.id
        """, (inceput, sfarsit))
        return [dict(r) for r in cur.fetchall()]


def compara_tva(d300_R, rulaje, necontate=None):
    """PURA: compara randurile D300 cu rulajele contabile.
    necontate: lista facturilor fara nota (pt remediu executabil cu cauza dovedita)."""
    necontate = necontate or []
    tva_necontat_emise = sum(_d(f.get("tva")) for f in necontate if f.get("directie") == "emisa")
    tva_necontat_primite = sum(_d(f.get("tva")) for f in necontate if f.get("directie") == "primita")

    perechi = (
        ("TVA colectata", "R17_2", "4427", "credit", tva_necontat_emise, "emise"),
        ("TVA deductibila", "R31_2", "4426", "debit", tva_necontat_primite, "primite"),
    )
    rez = []
    for eticheta, rand, cont, sens, tva_necontat, fel in perechi:
        decl = _d(d300_R.get(rand, 0))
        contabil = _d(rulaje.get(cont, {}).get(sens, 0))
        dif = decl - contabil
        temei = (f"D300 rand {rand} (facturi {fel} in luna, art. 281 CF) vs "
                 f"rulaj {sens} cont {cont} pe luna.")
        if abs(dif) <= TOLERANTA:
            rez.append({"stare": "verde", "eticheta": eticheta, "declarat": decl,
                        "contabil": contabil, "diferenta": dif, "temei": temei,
                        "mesaj": f"{eticheta}: D300 si contul {cont} coincid.",
                        "remediu": None})
            continue
        # cauza DOVEDITA: diferenta se explica exact prin facturile necontabilizate
        if tva_necontat and abs(dif - tva_necontat) <= TOLERANTA:
            rez.append({
                "stare": "rosu", "eticheta": eticheta, "declarat": decl,
                "contabil": contabil, "diferenta": dif, "temei": temei,
                "mesaj": (f"{eticheta}: D300 declara {decl} lei, contul {cont} are {contabil} lei "
                          f"(diferenta {dif} lei)."),
                "remediu": {
                    "fel": "executabil",
                    "cauza": f"{len([f for f in necontate if f.get('directie')==('emisa' if fel=='emise' else 'primita')])} "
                             f"facturi {fel} nu sunt contabilizate; TVA-ul lor ({tva_necontat} lei) "
                             f"explica exact diferenta.",
                    "actiune": "Contabilizeaza facturile listate.",
                    "facturi": [f["id"] for f in necontate
                                if f.get("directie") == ("emisa" if fel == "emise" else "primita")],
                },
            })
            continue
        # cauza NEDOVEDITA: nu propunem ajustari - spunem ce sa verifice
        rez.append({
            "stare": "rosu", "eticheta": eticheta, "declarat": decl,
            "contabil": contabil, "diferenta": dif, "temei": temei,
            "mesaj": (f"{eticheta}: D300 declara {decl} lei, contul {cont} are {contabil} lei "
                      f"(diferenta {dif} lei)."),
            "remediu": {
                "fel": "investigatie",
                "cauza": "Diferenta nu se explica integral prin facturi necontabilizate.",
                "actiune": ("Verifica: note manuale pe cont, storno neinregistrat, "
                            "TVA la incasare (exigibilitate decalata), regularizari, "
                            "facturi cu data in alta luna decat inregistrarea."),
                "facturi": [],
            },
        })
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
                                "cauza": "Date lipsa sau profil fiscal incomplet.",
                                "actiune": "Completeaza profilul firmei si reincearca.",
                                "facturi": []},
                }],
                "facturi_necontabilizate": [], "explicatie": "",
                "limita": "Verificarea TVA nu a fost efectuata - riscul ramane neacoperit."}

    R = res["R"] if isinstance(res, dict) else getattr(res, "R", {})
    necontate = facturi_necontabilizate(conn, schema, an, luna)
    rulaje = rulaje_luna(conn, schema, an, luna, ("4427", "4426"))
    constatari = compara_tva(R, rulaje, necontate)
    stare = "rosu" if any(c["stare"] == "rosu" for c in constatari) else "verde"
    return {
        "an": an, "luna": luna, "stare": stare, "constatari": constatari,
        "facturi_necontabilizate": necontate,
        "explicatie": (f"{len(necontate)} facturi ale lunii nu sunt contabilizate."
                       if necontate else ""),
        "limita": ("Verificat: D300 (calculat din facturile lunii) vs conturile 4427/4426. "
                   "NEVERIFICAT: daca D300 depus efectiv la ANAF coincide cu cel calculat aici "
                   "(necesita SPV)."),
        "modul": MODUL, "reguli": REGULI,
    }
