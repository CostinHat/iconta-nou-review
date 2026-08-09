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

Comparatie D112 (F162): totalurile DECLARATE se citesc din XML-ul generat
(angajatorA A_codOblig), NU dintr-o reagregare a salariatilor din pull(): generatorul
RECALCULEAZA cas/cass/impozit pe salariatii cu concediu medical (baza CM, OUG 158/2005)
si adauga suprataxa part-time separat. O reagregare ar fi o A TREIA cifra, care ar da
rosu fals exact pe cazurile grele. Ce parsam ESTE ce se depune.
  cod 602 (impozit)      <-> rulaj CREDIT 444
  cod 412 + 458 (CAS)    <-> rulaj CREDIT 4315   (458 = suprataxa part-time angajator,
  cod 432 + 459 (CASS)   <-> rulaj CREDIT 4316    contabilizata tot in 4315/4316 prin
  cod 480 (CAM)          <-> rulaj CREDIT 436     6451/6453 - vezi salarizare.py:161-163)
NEVERIFICAT: brutul (421). B_brutSalarii din D112 e baza de contributii, nu brut
contabil - pe lunile cu CM diverge legitim. Se declara ca limita, nu se falsifica.

Comparatie TVA:
  D300 R17_2 (colectata totala)      <->  rulaj CREDIT 4427 pe luna
  D300 R27_2 (deductibila totala)    <->  rulaj DEBIT  4426 pe luna

Regula EVIDENTA (15.07.2026): rulajele se citesc DOAR din note cu status='validata'.
Nota in ciorna e o PROPUNERE (nu a trecut patru-ochi), nu evidenta contabila. Daca ar
intra in rulaj, verdele ar fi IMPRUMUTAT: sistemul ar confirma coerenta pe baza a ceva
ce inca nu s-a intamplat. O factura cu nota ciorna ramane "necontabilizata" -> rosu, cu
remediu SUGERAT (asteapta validare), nu executabil (nota exista deja, nu se dubleaza).
"""
from decimal import Decimal
from core.pdf_util import bani

TOLERANTA = Decimal("1")  # 1 leu: D300 rotunjeste la leu, contabilitatea are bani
MODUL = "control_incrucisat"
REGULI = "2026.2"


def _d(v):
    return Decimal(str(v or 0))


def _lei(x):
    """Suma in format romanesc canonic + ' lei' (1.234,56 lei). Sursa unica: pdf_util.bani (DS cap.7)."""
    return bani(x, "lei")


def rulaje_interval(conn, schema, data_de, data_pana, conturi):
    """Rulaje DEBIT/CREDIT pe intervalul [data_de, data_pana) pentru conturile date, DOAR note
    validate (ciorna nu e evidenta - Regula EVIDENTA din capul modulului). GENERAL: rulaj pe cont,
    interval - refolosit de rulaje_luna SI de puntea fact-aware a semaforului (D205 anual). Datele =
    'YYYY-MM-DD'. Sursa UNICA de citit un rulaj pe cont (regula "nu construi paralel")."""
    out = {c: {"debit": Decimal("0"), "credit": Decimal("0")} for c in conturi}
    if not conturi:
        return out
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
        """, (data_de, data_pana, list(conturi), data_de, data_pana, list(conturi)))
        for cont, suma, sens in cur.fetchall():
            if cont in out:
                out[cont][sens] += _d(suma)
    return out


def rulaje_luna(conn, schema, an, luna, conturi):
    """Rulaje DEBIT/CREDIT pe LUNA (nu cumulat) pentru conturile date. Deleaga la rulaje_interval
    (o singura sursa). Cumulatul din documente_api.balanta() NU se poate compara cu D300 (lunar)."""
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    return rulaje_interval(conn, schema, inceput, sfarsit, conturi)


# ---- fapte fiscale pentru puntea semaforului (D205, D301). Traiesc LANGA sursa faptelor;
#      control_fiscal_api le CHEAMA, nu le absoarbe (motoarele raman separate - DECIZII 18.07 B).

def dividende_distribuite(conn, schema, an):
    """(suma_457, are_note) pentru anul `an`, DOAR note validate. Dividende distribuite = rulaj pe
    cont_debit LIKE '457%' (ACEEASI sursa ca d205.py, care genereaza D205). are_note = exista MACAR o
    nota validata pe an - ca sa distingem "nu s-au distribuit dividende" de "nu pot verifica, lipsesc
    note". Faptul pe care se decide D205 (semafor fact-aware)."""
    de = "%04d-01-01" % an
    pana = "%04d-01-01" % (an + 1)
    with conn.cursor() as cur:
        cur.execute(f"""SELECT COALESCE(SUM(l.suma), 0)
                        FROM {schema}.inregistrari_linii l
                        JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                        WHERE i.data >= %s AND i.data < %s AND i.status='validata'
                          AND l.cont_debit LIKE '457%%'""", (de, pana))
        suma = _d(cur.fetchone()[0])
        cur.execute(f"""SELECT 1 FROM {schema}.inregistrari
                        WHERE data >= %s AND data < %s AND status='validata' LIMIT 1""", (de, pana))
        are_note = cur.fetchone() is not None
    return suma, are_note


def d301_luni_operatiuni(conn, schema, an):
    """Set de luni (1-12) din anul `an` cu operatiuni IC inregistrate (tabelul d301_operatiuni,
    creat lazy de d301.py). Daca tabelul nu exista -> set gol. Faptul pe care se decide D301."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
        if cur.fetchone()[0] is None:
            return set()
        cur.execute(f"SELECT DISTINCT luna FROM {schema}.d301_operatiuni WHERE an=%s", (an,))
        return {r[0] for r in cur.fetchall()}


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
    # TVA deductibilă = R27_2 (TOTAL taxă deductibilă), NU R31_2 (care e doar AJUSTAREA
    # pro-rata, goala la pro_rata 100%). Bug dovedit 16.07.2026: pe tenant_002 D300
    # declara corect R27_2=210 (achizitie ORANGE), dar comparatia pe R31_2=0 vs 4426=210
    # dadea ROSU FALS pe orice firma cu achizitii deductibile normale. R17_2 (colectata)
    # e corect - totalul colectat, simetric cu R27_2 pe deductibila.
    perechi = (
        ("TVA colectată", "R17_2", "4427", "credit", "emisa", "emise"),
        ("TVA deductibilă", "R27_2", "4426", "debit", "primita", "primite"),
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
        mesaj = (f"{eticheta}: D300 declară {_lei(decl)}, contul {cont} are {_lei(contabil)} "
                 f"(diferență {_lei(dif)}).")
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
                cauza += f"; TVA-ul lor ({_lei(tva_grup)}) explică exact diferența."
                rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                    "fel": "executabil", "cauza": cauza,
                    "actiune": "Contabilizează facturile listate.",
                    "facturi": [f["id"] for f in fara_nota],
                }))
            else:
                rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                    "fel": "sugerat",
                    "cauza": (f"{len(cu_ciorna)} note ciornă create, așteaptă validare; "
                              f"TVA-ul lor ({_lei(tva_grup)}) explică exact diferența."),
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


COD_CONT_D112 = (
    ("Impozit pe venit", ("602",), "444"),
    ("CAS", ("412", "458"), "4315"),
    ("CASS", ("432", "459"), "4316"),
    ("CAM", ("480",), "436"),
)


def totaluri_d112_din_xml(xml):
    """Totalurile DECLARATE, citite din XML (angajatorA). Lipsa unui cod = declarat 0
    (add_oblig sare peste val=0), nu 'nu stiu'."""
    import re
    out = {}
    for m in re.finditer(r'A_codOblig="([^"]+)"[^>]*?A_datorat="([-0-9]+)"', xml):
        out[m.group(1)] = out.get(m.group(1), 0) + int(m.group(2))
    return out


def toleranta_d112(nr_salariati):
    """D112 rotunjeste la leu (_d112int pe TOTAL), contabilitatea tine bani per salariat.
    Diferenta legitima de rotunjire creste cu efectivul: pana la ~0.5 lei/salariat.
    O toleranta fixa de 1 leu ar da rosu fals pe orice firma cu peste ~2 salariati."""
    return max(TOLERANTA, Decimal("0.5") * Decimal(str(nr_salariati or 0)))


def compara_d112(totaluri, rulaje, note_ciorna=0, nr_salariati=0):
    """PURA: totaluri declarate (din XML) vs rulaj CREDIT pe conturile de datorii."""
    rez = []
    tol = toleranta_d112(nr_salariati)
    for eticheta, coduri, cont in COD_CONT_D112:
        decl = sum(_d(totaluri.get(c, 0)) for c in coduri)
        contabil = _d(rulaje.get(cont, {}).get("credit", 0))
        dif = decl - contabil
        cod_txt = "+".join(coduri)
        temei = (f"D112 angajatorA cod {cod_txt} (din XML-ul generat) vs "
                 f"rulaj credit cont {cont} pe lună, numai note validate. "
                 f"Toleranță {_lei(tol)}: D112 rotunjește la leu, evidența ține bani "
                 f"({nr_salariati} salariați × 0,5 lei).")
        baza = {"eticheta": eticheta, "declarat": decl, "contabil": contabil,
                "diferenta": dif, "temei": temei}
        if abs(dif) <= tol:
            rez.append(dict(baza, stare="verde",
                            mesaj=f"{eticheta}: D112 și contul {cont} coincid.", remediu=None))
            continue
        mesaj = (f"{eticheta}: D112 declară {_lei(decl)}, contul {cont} are {_lei(contabil)} "
                 f"(diferență {_lei(dif)}).")
        if contabil == 0 and decl > 0 and not note_ciorna:
            rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                "fel": "executabil",
                "cauza": f"Statul de plată nu este contabilizat: contul {cont} nu are rulaj în lună.",
                "actiune": "Contabilizează statul de plată.", "facturi": [],
            }))
        elif note_ciorna:
            rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                "fel": "sugerat",
                "cauza": f"{note_ciorna} note de salarii în ciornă, așteaptă validare.",
                "actiune": ("Un al doilea utilizator validează notele (patru ochi). "
                            "Până atunci operațiunile nu sunt în evidență."),
                "facturi": [],
            }))
        else:
            rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                "fel": "investigatie",
                "cauza": "Diferența nu se explică prin lipsa totală a notei de salarii.",
                "actiune": (f"Verifică: salariați adăugați/șterși după contabilizare, "
                            f"note manuale pe {cont}, corecții de lună anterioară, "
                            f"concedii medicale înregistrate diferit față de D112."),
                "facturi": [],
            }))
    return rez


def note_salarii_ciorna(conn, schema, an, luna):
    """DOAR statul de plata (document_ref 'SAL LL/AAAA'). nota_contract_special
    (zilieri/cenzori) scrie tot sursa='salarii' - nu e stat de plata, nu se numara."""
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor() as cur:
        cur.execute(f"""SELECT count(*) FROM {schema}.inregistrari
                        WHERE data >= %s AND data < %s AND status = 'ciorna'
                          AND sursa = 'salarii' AND document_ref = %s""",
                    (inceput, sfarsit, "SAL %02d/%04d" % (luna, an)))
        return int(cur.fetchone()[0] or 0)


def verifica_d112(conn, schema, an, luna):
    """F162: D112 vs contabilitate. Gri daca declaratia nu se poate genera."""
    from core import d112 as _d112
    try:
        xml, _av = _d112.genereaza(conn, schema, an, luna)
    except Exception as e:
        return {"an": an, "luna": luna, "stare": "gri", "constatari": [{
                    "stare": "gri", "eticheta": "Salarii", "temei": "D112 nu s-a putut genera.",
                    "mesaj": f"NU pot verifica salariile: declarația nu se poate calcula ({e}).",
                    "remediu": {"fel": "investigatie",
                                "cauza": "Date lipsă sau profil incomplet.",
                                "actiune": "Completează profilul firmei și salariații, apoi reîncearcă.",
                                "facturi": []}}],
                "explicatie": "",
                "limita": "Verificarea D112 nu a fost efectuată — riscul rămâne neacoperit.",
                "modul": MODUL, "reguli": REGULI}
    totaluri = totaluri_d112_din_xml(xml)
    import re as _re
    _m = _re.search(r'angajatorB[^>]*B_sal="(\d+)"', xml)
    totaluri["_nr_salariati"] = int(_m.group(1)) if _m else 0
    rulaje = rulaje_luna(conn, schema, an, luna, ("444", "4315", "4316", "436"))
    ciorne = note_salarii_ciorna(conn, schema, an, luna)
    nr_sal = int(totaluri.get("_nr_salariati", 0))
    if nr_sal == 0:
        # gardă: fără salariați, D112 nu se datorează -> NU producem verdict. Verdele pe 0-vs-0 ar fi
        # minciuna ("am verificat, coincide" despre un subiect inexistent) - absent, nu verde. DECIZII 23.07.
        return {"an": an, "luna": luna, "stare": "verde", "constatari": [],
                "explicatie": "", "limita": "Fără salariați în lună — D112 nu se datorează, nimic de verificat.",
                "modul": MODUL, "reguli": REGULI}
    constatari = compara_d112(totaluri, rulaje, ciorne, nr_sal)
    stare = "rosu" if any(c["stare"] == "rosu" for c in constatari) else "verde"
    return {"an": an, "luna": luna, "stare": stare, "constatari": constatari,
            "explicatie": (f"{ciorne} note de salarii în ciornă." if ciorne else ""),
            "limita": ("Verificat: totalurile din XML-ul D112 (cod 602/412+458/432+459/480) vs "
                       "conturile 444/4315/4316/436, numai note validate. "
                       "NEVERIFICAT: brutul (421) — D112 raportează baza de contribuții, "
                       "nu brutul contabil; pe lunile cu concedii medicale diverg legitim. "
                       "NEVERIFICAT: dacă D112 depus efectiv la ANAF coincide cu cel calculat aici."),
            "modul": MODUL, "reguli": REGULI}


def verifica_tva(conn, schema, an, luna):
    """Verificare TVA: D300 vs contabilitate + cauza + remediu.
    Conexiunea trebuie pozitionata pe schema: get_conn(schema) (ca la declaratii).
    Intoarce si starea GRI daca D300 nu se poate genera (nu ascunde necunoscutul)."""
    from core import d300 as _d300
    from core.common import Perioada
    # gardă subiect (analog cu d112 pe salariati): neplatitor de TVA -> D300 nu se aplica, NU producem verdict.
    # Verdele pe 0-vs-0 ar afirma o verificare fara subiect. platitor_tva==True cu luna goala e legitim (decont
    # nul coincide) -> ramane verde. None (vector incomplet) -> lasat sa ruleze; D300-declaratie e deja gri. DECIZII 23.07.
    with conn.cursor() as cur:
        cur.execute(f"SELECT platitor_tva FROM {schema}.firma_profil LIMIT 1")
        _row = cur.fetchone()
    if _row and _row[0] is False:
        return {"an": an, "luna": luna, "stare": "verde", "constatari": [], "facturi_necontabilizate": [],
                "explicatie": "", "limita": "Firmă neplătitoare de TVA — D300 nu se datorează, nimic de verificat.",
                "modul": MODUL, "reguli": REGULI}
    try:
        _xml, res = _d300.genereaza(conn, schema, Perioada(an, luna=luna))
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


# ============================================================
#  F163 — D390 (operațiuni intracomunitare de BUNURI) vs EVIDENȚA contabilă validată.
#
#  NU e control declarație-vs-declarație (D390↔D300). Verificat la sursă (19.07.2026,
#  vezi DECIZII.md): rândurile intracom ale D300 (R1_1 livrări, R5_1 achiziții) sunt
#  MANUAL-ONLY (d300.calcul_d300 le ia doar din `manual`, transmis prin body la generare,
#  declaratii_api.py) și NEPERSISTATE — public.declaratii_depuse (coada_api.py) e jurnal gol
#  (tenant/an/lună/tip/dată, fără valori de rânduri, fără XML depus). Un D300 regenerat de
#  aici ar avea mereu R1_1=R5_1=0 -> roșu pe orice firmă cu IC (zgomot); iar reconstruit din
#  aceleași facturi ca D390 -> verde trivial (aceeași sursă). Deci a doua sursă REALĂ e
#  evidența contabilă validată, nu a doua declarație. Când se vor persista rândurile
#  declarațiilor depuse -> abia atunci D-vs-D real (v2, prerechizit comun mai multor controale).
#
#  Regula direcțională (VIES = sursă mai autoritară pentru IC — partenerul a raportat pe latura
#  lui): declarat la VIES DAR absent din evidența validată = ROȘU (semnal tare + risc ANAF);
#  invers (în evidență, neraportat la VIES) = GRI (poate fi decalaj de perioadă); cifre diferite
#  = GRI (decalaj exigibilitate art.284, regularizări, rotunjire = legitim); ambele 0 = tăcut.
#  Remediu roșu = SUGERAT (corecția e în contabilitate SAU în recapitulativă — o confirmă omul,
#  nu e mecanică). DOAR BUNURI (auto-maparea D390: emisă->L, primită->A); serviciile IC (P/S)
#  rămân v2 (D390 le ia manual, iar d300 nu expune R3_1_1/R7_1_1).

D390_PERECHI = (
    ("Livrări intracomunitare de bunuri", "L", "emisa",
     "art. 294 alin.(2) lit.a) și d) Cod fiscal (livrări scutite cu drept de deducere)"),
    ("Achiziții intracomunitare de bunuri", "A", "primita",
     "art. 278 Cod fiscal (locul) / taxare inversă"),
)


def _fereastra_tva(tip_dec, an, luna):
    """Fereastra de comparație = perioada fiscală TVA după tip_decont. D390 e MEREU lunar; pentru
    firmă trimestrială se însumează cele 3 luni ale trimestrului și se compară cu o singură fereastră.
    Întoarce (luni, data_de, data_pana, eticheta). Datele = 'YYYY-MM-DD', interval [de, pana)."""
    t = str(tip_dec or "").strip().lower()
    if t == "t" or "trim" in t:
        tri = (luna - 1) // 3
        luni = [tri * 3 + 1, tri * 3 + 2, tri * 3 + 3]
        eticheta = "trimestrul %d/%d" % (tri + 1, an)
    elif t == "s" or "sem" in t:
        sem = (luna - 1) // 6
        luni = list(range(sem * 6 + 1, sem * 6 + 7))
        eticheta = "semestrul %d/%d" % (sem + 1, an)
    elif t == "a" or t.startswith("an"):
        luni = list(range(1, 13))
        eticheta = "anul %d" % an
    else:
        luni = [luna]
        eticheta = "%02d/%d" % (luna, an)
    data_de = "%04d-%02d-01" % (an, luni[0])
    lm = luni[-1]
    data_pana = ("%04d-01-01" % (an + 1,)) if lm == 12 else ("%04d-%02d-01" % (an, lm + 1))
    return luni, data_de, data_pana, eticheta


def facturi_ic(conn, schema, data_de, data_pana):
    """Facturile IC (partener UE, non-RO) în [data_de, data_pana), grupate pe directie, fiecare cu
    starea de contabilizare (are notă VALIDATĂ) și are_ciorna. Clasificarea UE = ACEEAȘI ca d390
    (refolosesc _CUI_UE + TARI_UE, nu construiesc paralel): emisă->livrări (L), primită->achiziții (A),
    doar BUNURI (auto-maparea D390). CUI-ul: întâi clientul din nomenclator, altfel tert_cui (ca d390.pull:
    facturile PRIMITE n-au niciodată client_id)."""
    import psycopg2.extras as _E
    from core.d390 import _CUI_UE, TARI_UE
    out = {"emisa": [], "primita": []}
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.id, f.numar, f.directie, f.total, f.tva, f.tert_nume,
                   c.cui AS c_cui, f.tert_cui,
                   EXISTS (SELECT 1 FROM {schema}.inregistrari i
                           WHERE i.factura_id = f.id AND i.status = 'validata') AS contabilizata,
                   EXISTS (SELECT 1 FROM {schema}.inregistrari ic
                           WHERE ic.factura_id = f.id AND ic.status = 'ciorna') AS are_ciorna
            FROM {schema}.facturi f
            LEFT JOIN {schema}.clienti c ON c.id = f.client_id
            WHERE f.data_emitere >= %s AND f.data_emitere < %s
            ORDER BY f.id
        """, (data_de, data_pana))
        for r in cur.fetchall():
            cui = (r["c_cui"] or r["tert_cui"] or "").strip().upper().replace(" ", "").replace("-", "")
            m = _CUI_UE.match(cui)
            if not m:
                continue
            tara = m.group(1)
            if tara == "RO" or tara not in TARI_UE:
                continue
            if r["directie"] in out:
                out[r["directie"]].append(dict(r))
    return out


def compara_d390(baze, ic_facturi):
    """PURA: bazele IC declarate în D390 (din facturi) vs evidența contabilă VALIDATĂ a acelorași
    facturi IC. baze = {"L": int, "A": int} (din res.rezumat D390); ic_facturi = {"emisa":[...],
    "primita":[...]} de la facturi_ic(). Regula direcțională documentată în capul secțiunii F163."""
    rez = []
    for eticheta, cheie, directie, art in D390_PERECHI:
        decl = _d(baze.get(cheie, 0))
        facturi = ic_facturi.get(directie, [])
        necontate = [f for f in facturi if not f.get("contabilizata")]
        contab = sum(_d(f.get("total")) - _d(f.get("tva")) for f in facturi if f.get("contabilizata"))
        dif = decl - contab
        temei = (f"D390 baza {cheie} (facturi intracomunitare, auto — art. 325 Cod fiscal, declarația "
                 f"recapitulativă) vs evidența contabilă validată a acelorași facturi ({art}; "
                 f"OMFP 1802/2014). Numai note validate — ciorna e propunere, nu dovadă. "
                 f"LIMITĂ: doar BUNURI IC, nu servicii (P/S); nu se compară cu D300 depus (nepersistat).")
        baza = {"eticheta": eticheta, "declarat": decl, "contabil": contab,
                "diferenta": dif, "temei": temei}
        # ambele 0 -> nimic de raportat
        if decl == 0 and contab == 0:
            continue
        # coerent (inclusiv toleranța de rotunjire la leu)
        if abs(dif) <= TOLERANTA:
            rez.append(dict(baza, stare="verde",
                mesaj=f"{eticheta}: D390 și evidența validată coincid ({_lei(decl)}).", remediu=None))
            continue
        # ROȘU: declarat la VIES, dar NIMIC în evidența validată (semnal tare)
        if decl > 0 and contab == 0:
            cioarna = [f for f in necontate if f.get("are_ciorna")]
            cauza = (f"D390 declară {_lei(decl)} operațiuni intracomunitare la VIES, dar nicio factură IC "
                     f"nu are notă validată în evidența contabilă")
            if cioarna:
                cauza += f" ({len(cioarna)} au note în ciornă, neconfirmate)"
            cauza += "."
            rez.append(dict(baza, stare="rosu",
                mesaj=(f"{eticheta}: D390 declară {_lei(decl)}, evidența validată are {_lei(contab)} "
                       f"(diferență {_lei(dif)})."),
                remediu={"fel": "sugerat", "cauza": cauza,
                    "actiune": ("Verifică operațiunile: fie contabilizează facturile IC (notă validată, "
                                "patru ochi), fie corectează declarația recapitulativă dacă au fost "
                                "raportate greșit la VIES. Corecția o confirmă omul — nu e mecanică."),
                    "facturi": [f["id"] for f in necontate]}))
            continue
        # GRI invers: evidență validată > declarat (în contabilitate, neraportat la VIES) — mai puțin sigur
        if dif < -TOLERANTA:
            rez.append(dict(baza, stare="gri",
                mesaj=(f"{eticheta}: evidența validată are {_lei(contab)}, D390 declară {_lei(decl)} "
                       f"(diferență {_lei(dif)})."),
                remediu={"fel": "investigatie",
                    "cauza": ("Operațiuni IC în evidența validată care nu apar în D390 — mai puțin sigur "
                              "decât inversul (poate fi decalaj de perioadă: nota validată în această "
                              "fereastră, recapitulativa cu altă cadență, sau operațiune neraportată încă)."),
                    "actiune": ("Verifică dacă operațiunile trebuie raportate la VIES pentru această "
                                "perioadă sau au fost/urmează a fi raportate în altă recapitulativă."),
                    "facturi": []}))
            continue
        # GRI: ambele > 0, cifre diferite — NICIODATĂ roșu pe diferență de cifre
        rez.append(dict(baza, stare="gri",
            mesaj=(f"{eticheta}: D390 declară {_lei(decl)}, evidența validată are {_lei(contab)} "
                   f"(diferență {_lei(dif)})."),
            remediu={"fel": "investigatie",
                "cauza": ("Ambele au valori, dar diferite — nu se declară roșu pe diferență de cifre "
                          "(decalaj de exigibilitate art. 284, regularizări, rotunjire = legitime)."),
                "actiune": ("Verifică: facturi IC încă necontabilizate, storno, corecții de perioadă, "
                            "operațiuni cu data în altă fereastră decât înregistrarea."),
                "facturi": [f["id"] for f in necontate]}))
    return rez


# ============================================================
#  F163 D-vs-D REAL (deblocat de F198) — A TREIA sursă: D390 vs D300 DEPUS.
#  Nu înlocuiește compara_d390 (evidența validată rămâne); o completează. Citește randurile
#  intracom ale D300 EFECTIV DEPUS din public.declaratii_depuse_curente.randuri (persistate la
#  depunere, F198). R1_1 (livrări IC) / R5_1 (achiziții IC) sunt MANUAL-ONLY (le introduce
#  contabilul la generare); cheie absentă => 0, dar temeiul spune de ce (contabilul vede CAUZA).
# ============================================================
D390_D300_PERECHI = (
    ("Livrări IC — D390 vs D300 depus", "L", "R1_1"),
    ("Achiziții IC — D390 vs D300 depus", "A", "R5_1"),
)


def compara_d390_vs_d300(baze, gasit, randuri, perioada=None):
    """PURA. baze = {"L": int, "A": int} (bazele IC din D390, recalculate pe ACEEAȘI perioadă ca D300
    depus). gasit = există D300 depus (bool). randuri = dict-ul `randuri` persistat al D300 depus (sau
    None = depus fără rânduri). perioada = eticheta perioadei evaluate (ex. "06/2026", "trimestrul
    2/2026") — se afișează explicit, fiindcă e alta decât restul ecranului (luna curentă).
    Reguli (cap secțiune F163 + regula direcțională VIES): zero depus -> GRI; randuri NULL -> GRI;
    D390>0 & D300 nu declară -> ROȘU (sugerat); ambele>0 diferite (sau D300>0 & D390=0) -> GRI (decalaj
    exigibilitate, NICIODATĂ roșu pe cifre); ambele 0 -> tăcut."""
    per_sufix = (", perioada %s" % perioada) if perioada else ""
    if not gasit:
        return [{"eticheta": "D390 vs D300 depus" + per_sufix, "stare": "gri",
                 "mesaj": "Nu există D300 depus în fereastră — nu pot compara recapitulativa cu decontul.",
                 "temei": ("D-vs-D real (F163, deblocat F198): D390 bază IC vs D300 depus (rânduri persistate). "
                           "Niciun D300 depus prin aplicație în fereastra TVA -> nimic de comparat. GRI, nu roșu."),
                 "remediu": None}]
    if randuri is None:
        return [{"eticheta": "D390 vs D300 depus" + per_sufix, "stare": "gri",
                 "mesaj": "D300 depus fără rânduri persistate — nu pot compara.",
                 "temei": ("D300 din fereastră a fost depus fără rânduri persistate (depunere anterioară "
                           "persistării F198 sau import istoric). GRI, nu roșu — absența datelor nu e divergență."),
                 "remediu": None}]
    R = (randuri or {}).get("R") or {}
    rez = []
    for eticheta, cheie, rand in D390_D300_PERECHI:
        eticheta = eticheta + per_sufix
        decl = _d(baze.get(cheie, 0))
        prezent = rand in R
        d300 = _d(R.get(rand, 0))
        if decl == 0 and d300 == 0:
            continue                                   # tăcut
        dif = decl - d300
        baza = {"eticheta": eticheta, "declarat_d390": int(decl), "declarat_d300": int(d300),
                "diferenta": int(dif)}
        absent_txt = ("" if prezent else
                      f" ATENȚIE: {rand} absent din D300 depus — rândurile intracomunitare ale D300 sunt "
                      "manual-only (le introduce contabilul la generare); absența nu dovedește lipsa operațiunilor.")
        temei = (f"D-vs-D (F163, deblocat F198): D390 bază {cheie} vs D300 depus rând {rand} "
                 f"(declaratii_depuse_curente.randuri). D390 = recapitulativa VIES, sursă mai autoritară.{absent_txt}")
        if abs(dif) <= TOLERANTA:
            rez.append(dict(baza, stare="verde",
                mesaj=f"{eticheta}: D390 și D300 depus coincid ({_lei(decl)}).", temei=temei, remediu=None))
        elif decl > 0 and d300 == 0:
            rez.append(dict(baza, stare="rosu",
                mesaj=(f"{eticheta}: D390 declară {_lei(decl)}, D300 depus declară {_lei(d300)} "
                       f"(diferență {_lei(dif)})."),
                temei=temei,
                remediu={"fel": "sugerat",
                    "cauza": (f"D390 raportează {_lei(decl)} operațiuni intracomunitare la VIES, dar D300 depus "
                              f"nu le declară pe rândul {rand}"
                              + ("" if prezent else " (rândul lipsește din decontul depus)") + "."),
                    "actiune": ("Verifică: fie completează rândul intracomunitar în D300 (rectificativă), fie "
                                "corectează D390 dacă a fost raportat greșit la VIES. Corecția o confirmă omul."),
                    "facturi": []}))
        else:
            rez.append(dict(baza, stare="gri",
                mesaj=(f"{eticheta}: D390 {_lei(decl)} vs D300 depus {_lei(d300)} (diferență {_lei(dif)})."),
                temei=temei + " Cifre diferite = decalaj de exigibilitate (art. 284), regularizări sau rotunjire — legitim, nu eroare.",
                remediu=None))
    return rez


def _d300_depus_randuri(conn, schema, an, luna):
    """(gasit, randuri) pentru D300 DEPUS CURENT (public.declaratii_depuse_curente) al firmei, în
    perioada (an, luna = ultima lună a ferestrei TVA). gasit=False -> niciun D300 depus; randuri=None
    -> depus fără rânduri persistate (pre-F198). Citește public.* calificat (conn e poziționat pe schema
    tenantului). tip='d300' = depunere prin app (importurile istorice sunt 'D300' uppercase, randuri NULL)."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
        row = cur.fetchone()
        if not row:
            return False, None
        cur.execute("SELECT randuri FROM public.declaratii_depuse_curente "
                    "WHERE tenant_id = %s AND tip = 'd300' AND an = %s AND luna = %s",
                    (row[0], an, luna))
        r = cur.fetchone()
    return (r is not None), (r[0] if r else None)


def _d300_depus_recent(conn, schema):
    """(an, luna, randuri) pentru CEA MAI RECENTĂ depunere D300 prin aplicație (tip='d300',
    public.declaratii_depuse_curente) a firmei — luna = ultima lună a perioadei TVA (cf. coada_api:
    lunar->luna, trim->trim*3, anual->12). None dacă firma n-a depus niciun D300 prin aplicație.
    randuri poate fi None (depunere pre-F198). AICI e reparat gri-ul permanent al D-vs-D: fereastra NU
    e luna curentă (D300 se depune în luna URMĂTOARE -> mereu gri), ci ultima perioadă efectiv depusă;
    baza D390 se recalculează pe ACEA perioadă (apelantul), ca ambele laturi să fie aceeași perioadă."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
        row = cur.fetchone()
        if not row:
            return None
        cur.execute("SELECT an, luna, randuri FROM public.declaratii_depuse_curente "
                    "WHERE tenant_id = %s AND tip = 'd300' ORDER BY an DESC, luna DESC LIMIT 1",
                    (row[0],))
        r = cur.fetchone()
    return (r[0], r[1], r[2]) if r else None


def verifica_d390(conn, schema, an, luna):
    """F163: D390 (bunuri IC) vs evidența contabilă validată a facturilor IC. Fereastra = periodicitatea
    TVA (tip_decont): lunar 1 lună, trimestrial 3 luni. Gri dacă D390 nu se poate genera. Vezi capul
    secțiunii F163 pentru filozofie (NU e D-vs-D)."""
    from core import d390 as _d390
    with conn.cursor() as cur:
        cur.execute(f"SELECT tip_decont FROM {schema}.firma_profil WHERE id = 1")
        row = cur.fetchone()
    tip_dec = row[0] if row else None
    luni, data_de, data_pana, fereastra = _fereastra_tva(tip_dec, an, luna)
    try:
        baze = {"L": 0, "A": 0}
        for m in luni:
            # calculeaza(), NU genereaza(): la VERIFICARE zero operatiuni e baza 0, nu eroare.
            # genereaza() are poarta fiscala (D390 nu se depune pe zero) - corecta la emitere,
            # gresita aici: ar face verificatorul gri pe orice luna fara operatiuni.
            res = _d390.calculeaza(conn, schema, an, m)
            rezumat = res["rezumat"] if isinstance(res, dict) else getattr(res, "rezumat", {})
            baze["L"] += int(rezumat.get("L", 0))
            baze["A"] += int(rezumat.get("A", 0))
    except Exception as e:
        return {"an": an, "luna": luna, "fereastra": fereastra, "stare": "gri", "constatari": [{
                    "stare": "gri", "eticheta": "Intracomunitar",
                    "temei": "D390 nu s-a putut genera.",
                    "mesaj": f"NU pot verifica operațiunile intracomunitare: D390 nu se poate calcula ({e}).",
                    "remediu": {"fel": "investigatie", "cauza": "Date lipsă sau profil incomplet.",
                                "actiune": "Completează profilul firmei și facturile, apoi reîncearcă.",
                                "facturi": []}}],
                "explicatie": "",
                "limita": "Verificarea D390 nu a fost efectuată — riscul rămâne neacoperit.",
                "modul": MODUL, "reguli": REGULI}
    ic_facturi = facturi_ic(conn, schema, data_de, data_pana)
    constatari = compara_d390(baze, ic_facturi)
    # [F163 D-vs-D real, deblocat F198] A TREIA sursă: D390 vs D300 DEPUS (randuri persistate).
    # Fereastra PROPRIE (nu luna curentă — D300 se depune în luna următoare, altfel permanent gri):
    # cea mai recentă perioadă cu D300 depus. Baza D390 se RECALCULEAZĂ pe acea perioadă, ca ambele
    # laturi să fie ACEEAȘI perioadă (comparație reală, nu perioade diferite). Perioada = afișată explicit.
    rec_d300 = _d300_depus_recent(conn, schema)
    if rec_d300 is None:
        constatari.append({"eticheta": "D390 vs D300 depus", "stare": "gri",
            "mesaj": "Nicio depunere D300 prin aplicație — nu am cu ce compara recapitulativa.",
            "temei": ("D-vs-D real (F163): D390 bază IC vs rândurile intracomunitare ale D300 EFECTIV "
                      "DEPUS (persistate F198). Nicio depunere D300 persistată -> comparația devine "
                      "posibilă după prima depunere prin aplicație. GRI, nu roșu — absență, nu divergență."),
            "remediu": None})
    else:
        an_d, luna_d, randuri_d = rec_d300
        luni_d, _de_d, _pana_d, eticheta_d = _fereastra_tva(tip_dec, an_d, luna_d)
        try:
            baze_d = {"L": 0, "A": 0}
            for m in luni_d:
                res_d = _d390.calculeaza(conn, schema, an_d, m)
                rez_d = res_d["rezumat"] if isinstance(res_d, dict) else getattr(res_d, "rezumat", {})
                baze_d["L"] += int(rez_d.get("L", 0))
                baze_d["A"] += int(rez_d.get("A", 0))
            constatari += compara_d390_vs_d300(baze_d, True, randuri_d, perioada=eticheta_d)
        except Exception as e:
            constatari.append({"eticheta": "D390 vs D300 depus, perioada %s" % eticheta_d, "stare": "gri",
                "mesaj": "NU pot recalcula D390 pe perioada depusă (%s) pentru comparație (%s)." % (eticheta_d, e),
                "temei": "D-vs-D real (F163): baza D390 se recalculează pe perioada D300 depus; recalcularea a eșuat.",
                "remediu": None})
    if any(c["stare"] == "rosu" for c in constatari):
        stare = "rosu"
    elif any(c["stare"] == "gri" for c in constatari):
        stare = "gri"
    else:
        stare = "verde"
    necontate_tot = sum(1 for d in ("emisa", "primita")
                        for f in ic_facturi.get(d, []) if not f.get("contabilizata"))
    return {"an": an, "luna": luna, "fereastra": fereastra, "stare": stare,
            "constatari": constatari,
            "explicatie": (f"{necontate_tot} facturi intracomunitare fără notă validată în fereastră."
                           if necontate_tot else ""),
            "limita": ("Verificat: D390 bunuri IC (livrări L / achiziții A, auto din facturi) vs (1) evidența "
                       f"contabilă validată a acelorași facturi pe fereastra TVA curentă ({fereastra}) ȘI (2) D300 "
                       "DEPUS (rânduri persistate F198), pe CEA MAI RECENTĂ perioadă efectiv depusă (afișată în "
                       "verdict, alta decât luna curentă — D300 se depune în luna următoare), cu baza D390 "
                       "recalculată pe acea perioadă. D-vs-D real: R1_1/R5_1 din D300 depus sunt manual-only (gri "
                       "dacă absente sau dacă D300 depus fără rânduri / nicio depunere). NEVERIFICAT: servicii "
                       "IC (P/S — D390 le ia manual, iar d300 nu expune R3_1_1/R7_1_1); triangulație (T/R)."),
            "modul": MODUL, "reguli": REGULI}


# ============================================================
#  F184 — Conformitate cota TVA pe facturile EMISE vs cota standard valabila LA DATA facturii.
#
#  NU e declaratie-vs-contabilitate, ci CONFORMITATE a facturilor emise (grup separat in ecran).
#  Puntea legislatie->re-verificare (v1): conecteaza un check VALUE-AWARE la push-ul F164. Cotele
#  fiscale traiesc parametrizate cu DATA in common.COTE; cota() e period-aware. Cand cota standard se
#  schimba (ex. 19%->21% de la 01.08.2025, Legea 141/2025), o factura emisa la cota VECHE dupa schimbare
#  e neconforma - dar declaratie-vs-contabilitate NU prinde asta (ambele laturi folosesc aceeasi cota).
#
#  Reutilizeaza PRIMITIVA verificatoare.verifica_tva_pe_cota (per-tranzactie, orfana pana acum), NU o
#  rescrie. Wrapper la nivel de firma: itereaza liniile facturilor emise ale lunii, cheama primitiva.
#  GARD anti-fals-pozitiv: se verifica DOAR liniile la o cota din FAMILIA STANDARD (istoricul tva_standard,
#  ex. {19,21}); cotele REDUSE (9/5) si scutit (0) NU depind de schimbarea cotei standard -> se ignora
#  (altfel 9% ar aparea mereu "gresit" fata de 21%). Rosu doar pe cota clar gresita pentru perioada; gri
#  daca nu pot citi facturile; verde/tacit daca toate liniile standard au cota corecta.

def _gri_cota_tva(an, luna, motiv):
    return {"an": an, "luna": luna, "stare": "gri", "constatari": [{
                "stare": "gri", "eticheta": "Cotă TVA facturi emise",
                "temei": "Conformitatea cotei TVA nu s-a putut evalua.",
                "mesaj": f"NU pot verifica cota TVA a facturilor emise: {motiv}",
                "remediu": {"fel": "investigatie", "cauza": "Date lipsă sau necitibile.",
                            "actiune": "Verifică facturile emise ale lunii, apoi reîncearcă.",
                            "facturi": []}}],
            "explicatie": "",
            "limita": "Verificarea cotei TVA nu a fost efectuată — riscul rămâne neacoperit.",
            "modul": MODUL, "reguli": REGULI}


def verifica_cota_tva(conn, schema, an, luna):
    """F184: cota TVA a facturilor EMISE ale lunii vs cota standard valabila LA DATA facturii.
    Vezi capul sectiunii F184. Conexiunea pozitionata pe schema. Citeste liniile, delega la
    constatare_cota_tva (PURA - testabila fara DB)."""
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    try:
        with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT f.id, f.numar, f.data_emitere, l.cantitate, l.pret_unitar, l.cota_tva
                FROM {schema}.facturi f
                JOIN {schema}.factura_linii l ON l.factura_id = f.id
                WHERE f.directie = 'emisa' AND f.data_emitere >= %s AND f.data_emitere < %s
                ORDER BY f.id
            """, (inceput, sfarsit))
            linii = [dict(r) for r in cur.fetchall()]
    except Exception as e:
        return _gri_cota_tva(an, luna, f"nu pot citi facturile emise ({e}).")
    return constatare_cota_tva(linii, an, luna)


def constatare_cota_tva(linii, an, luna):
    """PURA (fara DB): din liniile facturilor EMISE {id, numar, data_emitere, cantitate, pret_unitar,
    cota_tva}, verifica DOAR liniile la cota-familie-standard vs cota standard valabila la data facturii
    (verificatoare.verifica_tva_pe_cota, period-aware). Cote reduse/scutit -> ignorate."""
    from core import verificatoare as _vf
    from core import common as _c
    # familia cotelor standard = toate valorile istorice tva_standard (ex. {19, 21})
    try:
        standard_family = {int(round(float(v) * 100)) for _, v, _ in _c.COTE["tva_standard"]}
    except Exception as e:
        return _gri_cota_tva(an, luna, f"nu pot citi nomenclatorul cotelor ({e}).")

    verificate = 0
    nedeterminabile = 0   # linii cu cota neparsabila: SARITE, dar declarate in limita - nu ascunse tacit.
    gresite = {}   # factura_id -> {numar, cota_gasita, cota_corecta}
    for l in linii:
        try:
            cota_int = int(round(float(l["cota_tva"])))
        except Exception:
            nedeterminabile += 1   # skip la nivel de LINIE (nu gri global - ar ascunde verdele real pe rest)
            continue
        if cota_int not in standard_family:
            continue   # cota redusa/scutit -> in afara scopului (nu depinde de cota standard)
        baza = _d(l["cantitate"]) * _d(l["pret_unitar"])
        tva_linie = baza * _d(cota_int) / _d(100)
        rez = _vf.verifica_tva_pe_cota(baza, tva_linie, l["data_emitere"])  # PRIMITIVA, nerescrisa
        verificate += 1
        if not rez.get("ok", True) and l["id"] not in gresite:
            gresite[l["id"]] = {"numar": l["numar"], "cota_gasita": cota_int,
                                "cota_corecta": rez.get("cota_pct")}

    temei = ("Cota TVA de pe fiecare factură emisă trebuie să fie cota standard valabilă LA DATA facturii "
             "(common.COTE tva_standard, cu dată de valabilitate). Legea 141/2025: cota standard 21% din "
             "01.08.2025. LIMITĂ: se verifică doar liniile la cotă STANDARD; cotele reduse (9/5) și scutit "
             "nu depind de schimbarea cotei standard. Nu se verifică dacă produsul necesită cota standard "
             "(clasificare de produs), doar coerența de PERIOADĂ.")
    limita = ("Verificat: cota liniilor la cotă standard de pe facturile EMISE ale lunii vs cota standard "
              "valabilă la data facturii. NEVERIFICAT: cotele reduse/scutit (legitim neschimbate); "
              "clasificarea de produs (dacă produsul chiar cere cota standard).")
    if nedeterminabile:
        # linia sarita nu se ascunde: verdictul ramane pe ce s-a putut verifica, dar spune ce n-a intrat.
        limita += (" %d linie/linii cu cotă neparsabilă — NEVERIFICATE (verdictul acoperă doar liniile cu "
                   "cotă citibilă)." % nedeterminabile)

    if not gresite:
        constatari = [] if verificate == 0 else [{
            "stare": "verde", "eticheta": "Cotă TVA facturi emise", "temei": temei,
            "mesaj": "Toate facturile emise folosesc cota TVA corectă pentru perioadă.", "remediu": None}]
        return {"an": an, "luna": luna, "stare": "verde", "constatari": constatari,
                "explicatie": "", "limita": limita, "modul": MODUL, "reguli": REGULI}

    ids = sorted(gresite)
    n = len(ids)
    ex = gresite[ids[0]]
    mesaj = (f"{n} factur{'ă' if n == 1 else 'i'} emis{'ă' if n == 1 else 'e'} cu cotă TVA greșită pentru "
             f"perioadă (ex. {ex['cota_gasita']}% în loc de {ex['cota_corecta']}%).")
    constatare = {"stare": "rosu", "eticheta": "Cotă TVA facturi emise", "temei": temei, "mesaj": mesaj,
                  "remediu": {"fel": "sugerat",
                              "cauza": (f"{n} facturi emise au cotă TVA neconformă perioadei "
                                        f"(cotă veche folosită după schimbarea cotei standard)."),
                              "actiune": ("Verifică și corectează cota (stornare + reemitere sau factură de "
                                          "corecție). Cota o confirmă omul, nu se ajustează automat."),
                              "facturi": ids}}
    return {"an": an, "luna": luna, "stare": "rosu", "constatari": [constatare],
            "explicatie": f"{n} facturi emise cu cotă TVA neconformă perioadei.",
            "limita": limita, "modul": MODUL, "reguli": REGULI}
