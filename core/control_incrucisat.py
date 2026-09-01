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
from core import afirmatii as _af  # [P8] o constatare E o afirmatie, imbracata pentru ecran

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


def d301_luni_facturi_ic(conn, schema, an):
    """Lunile (1-12) din `an` cu ACHIZITII intracomunitare inregistrate ca FACTURI (facturi IC primite).
    [ruptura D301<->facturi 14.08.2026] Faptul care declanseaza D301 la un neplatitor NU e doar tabelul
    manual d301_operatiuni: o achizitie IC inregistrata ca factura (fluxul normal de utilizator) datoreaza
    D301. Simetric cu D390 (d390_are_operatiuni citeste tot facturi_ic). Reutilizeaza clasificarea UE din
    facturi_ic (nu construieste una paralela)."""
    import datetime as _dt
    fic = facturi_ic(conn, schema, _dt.date(an, 1, 1), _dt.date(an + 1, 1, 1))
    return {r["data_emitere"].month for r in fic.get("primita", []) if r.get("data_emitere")}


def are_salariat_activ_luna(conn, schema, an, luna):
    """[#6 D112 per-luna] Firma avea >=1 salariat ACTIV in (an, luna)? True/False.
    Activ = data_angajare <= ultima zi a lunii SI (data_incetare IS NULL OR data_incetare >= prima zi a lunii).
    (data_angajare NULL = tratat ca dintotdeauna angajat, ca in stat_plata_api / lista_salariati.)
    Tabelul salariati lipsa -> False (firma fara payroll ramane neaplicabila). Faptul pe care se datoreaza
    D112 LUNAR - inlocuieste snapshot-ul are_salariati pe CURRENT_DATE aplicat la toate lunile (bug #6:
    firma cu primul salariat angajat la mijloc de an primea D112 restant pe lunile de dinainte de angajare)."""
    import calendar as _cal, datetime as _dt
    prima = _dt.date(an, luna, 1)
    ultima = _dt.date(an, luna, _cal.monthrange(an, luna)[1])
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".salariati",))
        if cur.fetchone()[0] is None:
            return False
        cur.execute(f"""SELECT 1 FROM {schema}.salariati
                        WHERE (data_angajare IS NULL OR data_angajare <= %s)
                          AND (data_incetare IS NULL OR data_incetare >= %s) LIMIT 1""",
                    (ultima, prima))
        return cur.fetchone() is not None


def existenta_firma_an(conn, schema, an):
    """[#existenta - regula 4] Firma are ACTIVITATE reala demonstrabila in anul `an`? True/False.
    Activitate = macar o OPERATIUNE DATATA in an: factura (emisa/primita), salariat activ candva in an,
    inregistrare contabila, achizitie intracomunitara (d301_operatiuni), operatiune de casa, linie de extras
    bancar, bon, chitanta, sau mijloc fix pus in functiune. Tabelele lipsa -> se sar. Faptul pe care se decide
    daca o RESTANTA D100/D101/D406(neplatitor) pe un an trecut are premisa (firma exista/era activa) - simetric
    cu are_salariat_activ_luna. NU dovedeste inexistenta (o firma poate exista fara activitate); absenta
    activitatii -> 'necunoscut', decis in motor (control_fiscal_api._existenta_fapt, care combina cu creat_la).
    Nomenclatoarele (articole/furnizori/plan) si soldurile initiale (pot preceda existenta firmei) NU sunt
    activitate -> EXCLUSE. Aceeasi logica ca audit_restante.existenta_an."""
    import datetime as _dt
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".facturi",))
        if cur.fetchone()[0]:
            cur.execute(f"SELECT 1 FROM {schema}.facturi WHERE EXTRACT(year FROM data_emitere)=%s LIMIT 1", (an,))
            if cur.fetchone():
                return True
        cur.execute("SELECT to_regclass(%s)", (schema + ".salariati",))
        if cur.fetchone()[0]:
            cur.execute(f"""SELECT 1 FROM {schema}.salariati
                            WHERE (data_angajare IS NULL OR data_angajare <= %s)
                              AND (data_incetare IS NULL OR data_incetare >= %s) LIMIT 1""",
                        (_dt.date(an, 12, 31), _dt.date(an, 1, 1)))
            if cur.fetchone():
                return True
        cur.execute("SELECT to_regclass(%s)", (schema + ".inregistrari",))
        if cur.fetchone()[0]:
            cur.execute(f"SELECT 1 FROM {schema}.inregistrari WHERE EXTRACT(year FROM data)=%s LIMIT 1", (an,))
            if cur.fetchone():
                return True
        # [#existenta d301/casa/banca - audit tenant_006, 18.08.2026] Activitatea reala NU trece doar prin
        # facturi/salariati/note: un NEPLATITOR cu achizitii intracomunitare isi inregistreaza operatiunile
        # in d301_operatiuni (din care se naste CHIAR restanta D301 - vezi control_fiscal_api obligatii), iar
        # casa/banca/bonuri/chitante/mijloace fixe sunt tot operatiuni DATATE. Fara ele, semaforul afisa
        # simultan "operatiuni IC in iun 2026" (restanta D301) SI "nu pot demonstra ca firma era activa in
        # 2026" (D100/D406) -> contradictie pe acelasi ecran (Regula 14 pct.2). Criteriu: tabel de OPERATIUNI
        # datate, autor firma. Nomenclatoarele si soldurile_initiale/parteneri (pot preceda existenta) EXCLUSE.
        for _tab, _unde in (("d301_operatiuni", "an = %s"),
                            ("casa_operatiuni", "EXTRACT(year FROM data) = %s"),
                            ("extras_linii", "EXTRACT(year FROM data) = %s"),
                            ("bonuri", "EXTRACT(year FROM data) = %s"),
                            ("chitante", "EXTRACT(year FROM data) = %s"),
                            ("mijloace_fixe", "EXTRACT(year FROM data_pif) = %s")):
            cur.execute("SELECT to_regclass(%s)", (schema + "." + _tab,))
            if cur.fetchone()[0]:
                cur.execute(f"SELECT 1 FROM {schema}.{_tab} WHERE {_unde} LIMIT 1", (an,))
                if cur.fetchone():
                    return True
    return False


def facturi_necontabilizate(conn, schema, inceput, sfarsit):
    """Facturile din fereastra fiscala [inceput, sfarsit) FARA nota VALIDATA care ATINGE contul de
    TVA (4427 credit pt emise, 4426 debit pt primite) - cauza dovedibila a divergentei D300<->cont.
    inceput/sfarsit = 'YYYY-MM-DD', interval semi-deschis; fereastra = perioada fiscala TVA (trimestrul
    intreg pt trimestriali), ACEEASI ca a D300 (vezi verifica_tva) - altfel D300=trimestru vs rulaj=luna
    dadea rosu fals.
    O DECONTARE (incasare 5311/4111, plata 5311/401) leaga factura_id dar NU atinge 4427/4426 -> nu mai
    bifeaza factura drept contabilizata (bug: nota de vanzare/achizitie lipsa, mascata de incasare).
    Facturile FARA TVA (tva=0) sau cu taxare inversa (fara TVA pe vanzare, nu au 4427/4426 de atins):
    orice nota validata le contabilizeaza.
    are_ciorna=True -> nota exista dar asteapta patru-ochi: NU se recontabilizeaza."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.id, f.numar, f.directie, f.total, f.tva, f.tert_nume,
                   EXISTS (SELECT 1 FROM {schema}.inregistrari ic
                           WHERE ic.factura_id = f.id AND ic.status = 'ciorna') AS are_ciorna
            FROM {schema}.facturi f
            WHERE f.data_emitere >= %s AND f.data_emitere < %s
              AND NOT EXISTS (
                    SELECT 1 FROM {schema}.inregistrari i
                    LEFT JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                    WHERE i.factura_id = f.id AND i.status = 'validata'
                      AND ( COALESCE(f.tva, 0) = 0
                         OR COALESCE(f.taxare_inversa, false) = true
                         OR (f.directie = 'emisa'   AND l.cont_credit = '4427')
                         OR (f.directie = 'primita' AND l.cont_debit  = '4426') ) )
            ORDER BY f.id
        """, (inceput, sfarsit))
        return [dict(r) for r in cur.fetchall()]





def _patru_ochi_activ(conn, schema):
    """Starea REALA four-eyes a cabinetului care deține schema tenantului (nu o presupunere).
    Fail-open pe True (formularea prudentă "al doilea utilizator") dacă maparea nu se poate citi."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT accounting_firm_id FROM public.tenants WHERE schema_name = %s", (schema,))
            r = cur.fetchone()
            if not r or r[0] is None:
                return True
            cur.execute("SELECT patru_ochi_activ FROM public.accounting_firms WHERE id = %s", (r[0],))
            r2 = cur.fetchone()
        return bool(r2[0]) if r2 and r2[0] is not None else False
    except Exception:
        return True


def _actiune_valideaza(patru_ochi):
    """Textul remediului "validează nota", condiționat de four-eyes REAL. Activat -> un al doilea
    utilizator (patru ochi); neactivat -> același user își validează propria notă (bara de sus încă
    oferă activarea, dar deocamdată e un singur pas)."""
    if patru_ochi:
        return ("Un al doilea utilizator validează notele (patru ochi). "
                "Până atunci operațiunile nu sunt în evidență.")
    return "Validează nota (din ciornă în evidență)."


def compara_tva(d300_R, rulaje, an, luna, necontate=None, patru_ochi=True,
                sursa_declarat="regenerat"):
    """PURA: compara randurile D300 cu rulajele contabile.

    [P8, 21.08.2026] `an`/`luna` sunt OBLIGATORII. Prima forma le-a pus optionale, „ca sa nu ating
    testele pure" - si ramura contului 4428 cadea cu AfirmatieIncompleta, fiindca un fapt fara
    perioada nu se poate construi. Niciun test n-o atingea (`_rulaje()` nu pune 4428), deci suita era
    verde peste o cadere. A doua oara azi cand un default comod ascunde o cale netestata: un FAPT
    despre datele firmei ARE o perioada, iar semnatura trebuie s-o ceara, nu s-o spere.
    necontate: facturi FARA nota validata, fiecare cu are_ciorna (nota propusa, nevalidata).
    Ciorna nu intra in rulaj si NU inchide constatarea: verdele vine dupa patru-ochi."""
    necontate = necontate or []
    # [interdictia 32] DIN CE s-a comparat, spus o data si folosit in ambele temeiuri de mai jos.
    _de_unde = ("din rândurile DEPUSE, persistate la depunere" if sursa_declarat == "depus"
                else "REGENERAT acum — nu s-a păstrat ce s-a depus, deci comparația e evidența "
                     "de azi față de decontul care S-AR genera azi")
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
        temei = (f"D300 rând {rand} ({_de_unde}; facturi {fel} în lună, art. 281 CF) vs "
                 f"rulaj {sens} cont {cont} pe lună, numai note validate "
                 f"(ciorna e propunere, nu evidență).")
        mesaj = (f"{eticheta}: D300 declară {_lei(decl)}, contul {cont} are {_lei(contabil)} "
                 f"(diferență {_lei(dif)}).")
        baza = {"eticheta": eticheta, "declarat": decl, "contabil": contabil,
                "diferenta": dif, "temei": temei, "sursa_declarat": sursa_declarat}
        if abs(dif) <= TOLERANTA:
            # [R35, 28.08.2026] NECUNOSCUTUL DOMINA FAVORABILUL (P6, interdictia 10).
            # Pana azi ramura asta dadea VERDE fara sa se uite deloc la `necontate` - desi lista
            # aia e chiar in apelul curent. Cand ambii termeni sunt ZERO (factura neinregistrata
            # nu intra nici in rulaj, nici in decontul REGENERAT din evidenta), egalitatea se
            # producea prin ABSENTA amandurora, iar ecranul spunea „D300 si contul coincid" pe o
            # luna in care o factura emisa statea in afara conturilor. Masurat pe 27 de perechi
            # (schema x luna cu facturi): 6 verzi peste un necunoscut din propriul payload.
            # Nu devine ROSU: nu se stie ca cifrele sunt gresite - se stie ca nu se poate afirma
            # ca sunt bune. Deci GRI, cu domeniul necunoasterii numit.
            if grup:
                _tva_txt = (f"TVA-ul lor ({_lei(tva_grup)})" if tva_grup
                            else "TVA-ul lor e 0,00 sau nu se cunoaste")
                # [DS cap.13 / clichet 50] necunoscutul e un OBIECT cu atribute, nu un sir:
                # cate facturi si ce TVA. `tva=None` inseamna „0 sau nu se cunoaste" - cele doua
                # NU se pot deosebi azi, fiindca o valoare absenta si un zero arata la fel in
                # `f.get("tva")` (aceeasi clasa cu interdictia 32). Textul il compune ecranul;
                # cifrele nu se pot compune inapoi dintr-o fraza.
                rez.append(dict(baza, stare="gri",
                    necunoscut={"cate": len(grup), "tva": (tva_grup if tva_grup else None),
                                "fara_nota": len(fara_nota), "cu_ciorna": len(cu_ciorna)},
                    mesaj=(f"{eticheta}: D300 și contul {cont} coincid ({_lei(decl)}), dar "
                           f"{len(grup)} facturi {fel} din lună nu sunt în evidență — "
                           f"{_tva_txt}. Coincidența NU spune nimic despre ele."),
                    remediu={"fel": "investigatie",
                             "cauza": ("Egalitatea se poate produce și prin absența ambilor "
                                       "termeni: o factură necontabilizată lipsește deopotrivă "
                                       "din rulaj și din decontul regenerat."),
                             "actiune": ("Contabilizează facturile listate, apoi reia "
                                         "verificarea — abia atunci egalitatea afirmă ceva."),
                             "facturi": [f["id"] for f in fara_nota]}))
            else:
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
                    "actiune": _actiune_valideaza(patru_ochi),
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

    # REZULTATUL decontului, nu doar cele doua totaluri: sold de plata (rd.41) <-> 4423,
    # de recuperat (rd.42) <-> 4424. Note validate, pe fereastra fiscala. Ambele 0 -> tacut
    # (nu orice luna are nota de inchidere TVA - nu producem zgomot).
    for eticheta, rand, cont, sens in (
        ("TVA de plată (rezultat decont)", "R41_2", "4423", "credit"),
        ("TVA de recuperat (rezultat decont)", "R42_2", "4424", "debit"),
    ):
        decl = _d(d300_R.get(rand, 0))
        contabil = _d(rulaje.get(cont, {}).get(sens, 0))
        if decl == 0 and contabil == 0:
            continue
        dif = decl - contabil
        temei = (f"D300 rând {rand} ({_de_unde}; rezultatul decontului, sold la sfârșitul perioadei fiscale) vs "
                 f"rulaj {sens} cont {cont}, numai note validate. Reconciliază rezultatul, nu doar "
                 f"totalurile colectată/deductibilă.")
        baza = {"eticheta": eticheta, "declarat": decl, "contabil": contabil,
                "diferenta": dif, "temei": temei, "sursa_declarat": sursa_declarat}
        if abs(dif) <= TOLERANTA:
            rez.append(dict(baza, stare="verde",
                            mesaj=f"{eticheta}: D300 și contul {cont} coincid ({_lei(decl)}).",
                            remediu=None))
        else:
            rez.append(dict(baza, stare="rosu",
                mesaj=(f"{eticheta}: D300 declară {_lei(decl)}, contul {cont} are {_lei(contabil)} "
                       f"(diferență {_lei(dif)})."),
                remediu={"fel": "investigatie",
                         "cauza": "Rezultatul decontului nu coincide cu nota de închidere TVA.",
                         "actiune": (f"Verifică nota de închidere TVA a perioadei (4427/4426 → {cont}), "
                                     f"regularizări și soldul reportat din perioada precedentă."),
                         "facturi": []}))

    # SEMNAL pe 4428 (TVA neexigibilă): exigibilitate decalată (TVA la încasare / taxare inversă),
    # fără rând D300 corespondent direct. Dacă soldul net s-a mișcat în perioadă -> gri (informativ,
    # NU roșu: nu are contrapartidă declarată), ca să nu treacă tăcut.
    _nx = rulaje.get("4428")
    if _nx:
        _net = _d(_nx.get("credit", 0)) - _d(_nx.get("debit", 0))
        if abs(_net) > TOLERANTA:
            _c4428 = _fapt_liber(
                "d300", "TVA neexigibilă (cont 4428)",
                ("Cont 4428 (TVA neexigibilă) — exigibilitate decalată (TVA la încasare / "
                 "taxare inversă). Fără rând D300 corespondent direct."),
                (f"Cont 4428 (TVA neexigibilă) are sold net {_lei(_net)} în perioadă — "
                 f"exigibilitate decalată, încă nedeclarată în acest decont."),
                an, luna,
                "rulajele contabile ale perioadei pe contul 4428",
                # GRI, nu verde: e informativ (nu are contrapartida declarata), dar ramane un FAPT.
                stare="gri",
                remediu={"fel": "investigatie",
                         "cauza": "TVA neexigibilă în sold — devine exigibilă la încasare/plată.",
                         "actiune": ("Verifică dacă TVA neexigibilă trebuia să devină exigibilă "
                                     "în perioadă (încasări/plăți efectuate)."),
                         "facturi": []})
            _c4428.update({"declarat": Decimal(0), "contabil": _net, "diferenta": _net})
            rez.append(_c4428)
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


def compara_d112(totaluri, rulaje, note_ciorna=0, nr_salariati=0, patru_ochi=True,
                 sursa_declarat="regenerat"):
    """PURA: totaluri declarate (din XML) vs rulaj CREDIT pe conturile de datorii.

    `note_ciorna` are TREI valori, nu doua: un numar (se stie cate note in ciorna sunt), `0` (se
    stie ca nu e niciuna) si **`None` = NU SE POATE STI**. A treia exista fiindca filtrul care le
    numara se sprijina pe `inregistrari.document_ref`, o coloana pe care nu o scrie nicio cale de
    INSERT (R39). Un `0` de acolo n-ar fi o observatie, ci o constanta - iar o cauza afirmata pe el
    ar fi interdictia 10.
    """
    rez = []
    tol = toleranta_d112(nr_salariati)
    for eticheta, coduri, cont in COD_CONT_D112:
        decl = sum(_d(totaluri.get(c, 0)) for c in coduri)
        contabil = _d(rulaje.get(cont, {}).get("credit", 0))
        dif = decl - contabil
        cod_txt = "+".join(coduri)
        de_unde = ("din XML-ul DEPUS, persistat la depunere" if sursa_declarat == "depus"
                   else "din XML-ul REGENERAT acum — nu s-a păstrat ce s-a depus, deci comparația "
                        "e evidența de azi față de declarația care S-AR genera azi")
        temei = (f"D112 angajatorA cod {cod_txt} ({de_unde}) vs "
                 f"rulaj credit cont {cont} pe lună, numai note validate. "
                 f"Toleranță {_lei(tol)}: D112 rotunjește la leu, evidența ține bani "
                 f"({nr_salariati} salariați × 0,5 lei).")
        # [interdictia 32] DIN CE s-a comparat e un FAPT despre constatare, deci e camp - nu doar o
        # fraza in temei. Un consumator (ecran, gard, raport) trebuie sa poata intreba structura,
        # nu sa caute un cuvant intr-o proza destinata omului.
        baza = {"eticheta": eticheta, "declarat": decl, "contabil": contabil,
                "diferenta": dif, "temei": temei, "sursa_declarat": sursa_declarat}
        if abs(dif) <= tol:
            rez.append(dict(baza, stare="verde",
                            mesaj=f"{eticheta}: D112 și contul {cont} coincid.", remediu=None))
            continue
        mesaj = (f"{eticheta}: D112 declară {_lei(decl)}, contul {cont} are {_lei(contabil)} "
                 f"(diferență {_lei(dif)}).")
        if contabil == 0 and decl > 0 and note_ciorna is None:
            # [R39/interdictia 10] NU se afirma cauza: nu se stie daca statul e necontabilizat sau
            # doar lasat in ciorna, fiindca `document_ref` nu se scrie de nicaieri (0 din 48 de cai
            # de INSERT). Se spune ce se vede, se declara ce nu se stie, si se numesc AMANDOUA
            # actiunile - un verdict care alege una din ele ar fi ghicit.
            rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                "fel": "investigatie",
                "cauza": (f"Contul {cont} nu are rulaj în lună — se numără doar notele validate. "
                          f"Dacă statul de plată e înregistrat și lăsat în ciornă nu se poate ști: "
                          f"nota nu poartă documentul justificativ care ar deosebi cele două "
                          f"situații."),
                "actiune": ("Verifică dacă statul de plată e contabilizat. Dacă nu este, "
                            "contabilizează-l; dacă este și a rămas în ciornă, "
                            + _actiune_valideaza(patru_ochi)),
                "facturi": [],
            }))
        elif contabil == 0 and decl > 0 and not note_ciorna:
            rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                "fel": "executabil",
                "cauza": f"Statul de plată nu este contabilizat: contul {cont} nu are rulaj în lună.",
                "actiune": "Contabilizează statul de plată.", "facturi": [],
            }))
        elif note_ciorna:
            rez.append(dict(baza, stare="rosu", mesaj=mesaj, remediu={
                "fel": "sugerat",
                "cauza": f"{note_ciorna} note de salarii în ciornă, așteaptă validare.",
                "actiune": _actiune_valideaza(patru_ochi),
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


def _document_ref_populat(conn, schema):
    """Coloana `document_ref` e scrisa VREODATA pe schema asta?

    [R39/interdictia 32] Daca nu e, orice filtru pe ea nu poate deosebi nimic, iar un 0 din el nu e
    o observatie - e o constanta. Masurat 24.08.2026: 0 din 48 de cai de INSERT o ating."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT EXISTS (SELECT 1 FROM {schema}.inregistrari
                                       WHERE document_ref IS NOT NULL)""")
        return bool(cur.fetchone()[0])


def note_salarii_ciorna(conn, schema, an, luna):
    """DOAR statul de plata (document_ref 'SAL LL/AAAA'). nota_contract_special
    (zilieri/cenzori) scrie tot sursa='salarii' - nu e stat de plata, nu se numara."""
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    # [R39] Necunoscutul se DECLARA, nu se rotunjeste la 0: daca nimeni n-a scris niciodata
    # `document_ref`, filtrul de mai jos nu poate distinge statul de plata de restul, iar cifla lui
    # ar fi 0 indiferent de realitate. P6: ce nu se poate sti se spune, nu se presupune favorabil.
    if not _document_ref_populat(conn, schema):
        return None
    with conn.cursor() as cur:
        cur.execute(f"""SELECT count(*) FROM {schema}.inregistrari
                        WHERE data >= %s AND data < %s AND status = 'ciorna'
                          AND sursa = 'salarii' AND document_ref = %s""",
                    (inceput, sfarsit, "SAL %02d/%04d" % (luna, an)))
        return int(cur.fetchone()[0] or 0)


def _d112_depus_xml(conn, schema, an, luna):
    """XML-ul D112 EFECTIV DEPUS pentru (an, luna), sau None daca nu s-a pastrat.

    [interdictia 32] O pozitie de declaratie nu se poate desface pana la document daca nici
    declaratia nu se pastreaza. Calea de coada (`coada_api`) persista `xml`; importul istoric
    (`istoric_declaratii_import_api`) NU - el consemneaza CA s-a depus, nu CE s-a depus.
    Masurat 24.08.2026: 0 din 54 de depuneri au xml, fiindca toate cele 54 sunt importuri.

    Aceeasi disciplina cu `_d300_depus_randuri`: trei valori, nu doua - aici None inseamna
    "nu se poate sti ce s-a depus", si NU se rotunjeste la "s-a depus ce as genera eu acum"."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
        row = cur.fetchone()
        if not row:
            return None
        cur.execute("SELECT xml FROM public.declaratii_depuse_curente "
                    "WHERE tenant_id = %s AND tip = 'd112' AND an = %s AND luna = %s",
                    (row[0], an, luna))
        r = cur.fetchone()
    return r[0] if r and r[0] else None


def verifica_d112(conn, schema, an, luna):
    """F162: D112 vs contabilitate. Gri daca declaratia nu se poate genera."""
    from core import d112 as _d112
    # [interdictia 32] Intai ce s-a DEPUS. Daca s-a pastrat, aia e declaratia care traieste la ANAF
    # si aia trebuie confruntata cu evidenta. Regenerarea e a doua alegere, si se spune in temei.
    sursa_declarat = "regenerat"
    try:
        # Generarea ramane PRIMA, ca semantica erorilor sa nu se schimbe: "gri daca declaratia nu se
        # poate genera" e contractul functiei, si el se decide inainte de orice preferinta de sursa.
        xml, _av = _d112.genereaza(conn, schema, an, luna)
        depus = _d112_depus_xml(conn, schema, an, luna)
        if depus:
            xml, sursa_declarat = depus, "depus"
    except Exception as e:
        from core.perioada import PerioadaNeconfirmata
        if isinstance(e, PerioadaNeconfirmata):
            cauza = str(e).replace("PERIOADA_BLOCATA: ", "")
            actiune = "Confirmă pontajul lunii (rol admin_firma)."
        elif isinstance(e, ValueError):
            # [cauza_precisa] eroare de business din d112.genereaza (CAEN out-of-enum, CUI invalid):
            # mesajul ei E deja explicatia utila; nu-l acoperi cu genericul care CONTRAZICE (profil complet).
            cauza = str(e)
            actiune = "Corectează în Date firmă ce indică mesajul, apoi reîncearcă."
        else:
            cauza = "Date lipsă sau profil incomplet."
            actiune = "Completează profilul firmei și salariații, apoi reîncearcă."
        return {"an": an, "luna": luna, "stare": "gri", "constatari": [_gri_liber(
                    "d112", "Salarii", "D112 nu s-a putut genera.",
                    f"NU pot verifica salariile: declarația nu se poate calcula ({e}).", an, luna,
                    {"fel": "investigatie", "cauza": cauza, "actiune": actiune, "facturi": []})],
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
                "limita": "Fără salariați în lună — D112 nu se datorează, nimic de verificat.",
                "modul": MODUL, "reguli": REGULI}
    constatari = compara_d112(totaluri, rulaje, ciorne, nr_sal,
                              sursa_declarat=sursa_declarat,
                              patru_ochi=_patru_ochi_activ(conn, schema))
    stare = "rosu" if any(c["stare"] == "rosu" for c in constatari) else "verde"
    return {"an": an, "luna": luna, "stare": stare, "constatari": constatari,

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
    from core.common import Perioada, fereastra_tva, perioada_tva_tip
    # gardă subiect (analog cu d112 pe salariati): neplatitor de TVA -> D300 nu se aplica, NU producem verdict.
    # Verdele pe 0-vs-0 ar afirma o verificare fara subiect. platitor_tva==True cu luna goala e legitim (decont
    # nul coincide) -> ramane verde. None (vector incomplet) -> lasat sa ruleze; D300-declaratie e deja gri. DECIZII 23.07.
    with conn.cursor() as cur:
        cur.execute(f"SELECT platitor_tva, tip_decont FROM {schema}.firma_profil LIMIT 1")
        _row = cur.fetchone()
    _prof = {}
    if _row is not None:
        _prof["platitor_tva"] = _row[0]
        if len(_row) > 1:
            _prof["tip_decont"] = _row[1]
    if _prof.get("platitor_tva") is False:
        return {"an": an, "luna": luna, "stare": "verde", "constatari": [], "facturi_necontabilizate": [],
                "limita": "Firmă neplătitoare de TVA — D300 nu se datorează, nimic de verificat.",
                "modul": MODUL, "reguli": REGULI}
    try:
        _xml, res = _d300.genereaza(conn, schema, Perioada(an, luna=luna))
    except Exception as e:
        from core.perioada import PerioadaNeconfirmata
        if isinstance(e, PerioadaNeconfirmata):
            cauza = str(e).replace("PERIOADA_BLOCATA: ", "")
            actiune = "Confirmă perioada lunii (rol admin_firma)."
        elif isinstance(e, ValueError):
            # [cauza_precisa] eroare de business precisa - nu o acoperi cu genericul
            cauza = str(e)
            actiune = "Corectează în Date firmă ce indică mesajul, apoi reîncearcă."
        else:
            cauza = "Date lipsă sau profil fiscal incomplet."
            actiune = "Completează profilul firmei și reîncearcă."
        return {"an": an, "luna": luna, "stare": "gri",
                "constatari": [_gri_liber(
                    "d300", "TVA", "D300 nu s-a putut genera.",
                    f"NU pot verifica TVA: decontul nu se poate calcula ({e}).", an, luna,
                    {"fel": "investigatie", "cauza": cauza, "actiune": actiune, "facturi": []})],
                "facturi_necontabilizate": [],
                "limita": "Verificarea TVA nu a fost efectuată — riscul rămâne neacoperit."}

    R = res["R"] if isinstance(res, dict) else getattr(res, "R", {})
    # FEREASTRA FISCALA (3a): rulajele si facturile se compara pe ACEEASI fereastra ca D300 - pentru
    # trimestriali D300 agrega tot trimestrul (fereastra_tva), deci comparatia cu O luna calendaristica
    # dadea rosu fals garantat. Foloseste perioada fiscala TVA din vectorul firmei (tip_decont).
    _inc, _sf = fereastra_tva(Perioada(an, luna=luna), perioada_tva_tip(_prof))
    _de, _pana = _inc.isoformat(), _sf.isoformat()
    # [interdictia 32 / R40] Intai ce s-a DEPUS. Cheia depunerii NU e luna curenta, ci ULTIMA LUNA A
    # FERESTREI TVA: pentru trimestriali, coada scrie luna 3/6/9/12 (eticheta decontului), nu luna
    # calendaristica. Fereastra e semi-deschisa [inceput, sfarsit), deci ultima luna e sfarsit-1 zi.
    # Fara corectia asta, cautarea ar rata sistematic exact firmele trimestriale - si ar rata TACUT.
    from datetime import timedelta as _td
    _ult = _sf - _td(days=1)
    _gasit_dep, _randuri_dep = _d300_depus_randuri(conn, schema, _ult.year, _ult.month)
    sursa_declarat = "regenerat"
    if _gasit_dep and _randuri_dep:
        _R_dep = (_randuri_dep or {}).get("R") or {}
        if _R_dep:
            R, sursa_declarat = _R_dep, "depus"
    necontate = facturi_necontabilizate(conn, schema, _de, _pana)
    rulaje = rulaje_interval(conn, schema, _de, _pana, ("4427", "4426", "4423", "4424", "4428"))
    constatari = compara_tva(R, rulaje, an, luna, necontate,
                             sursa_declarat=sursa_declarat,
                             patru_ochi=_patru_ochi_activ(conn, schema))
    # [R35, 28.08.2026] A DOUA INSTANTA, in aceeasi functie, si nu se vede din prima: agregarea
    # era `rosu if any(rosu) else verde` - fara ramura de GRI. Orice constatare gri (semnalul pe
    # 4428 exista de dinainte, iar de azi si verdele-peste-necunoscut) se COLAPSA in verde la
    # nivelul de sus. Fara randul asta, reparatia de mai sus ar fi aratat facuta si n-ar fi fost.
    # Aceeasi forma pe care o au deja `verifica_d390` si `verifica_d112`.
    if any(c["stare"] == "rosu" for c in constatari):
        stare = "rosu"
    elif any(c["stare"] == "gri" for c in constatari):
        stare = "gri"
    else:
        stare = "verde"
    return {
        "an": an, "luna": luna, "stare": stare, "constatari": constatari,
        "facturi_necontabilizate": necontate,

        "limita": (("Verificat: D300 DEPUS (rândurile persistate la depunere) vs conturile "
                    "4427/4426. " if sursa_declarat == "depus" else
                    "Verificat: D300 REGENERAT acum din facturile lunii — nu s-a păstrat ce s-a "
                    "depus, deci comparația e evidența de azi față de decontul care s-ar genera "
                    "azi — vs conturile 4427/4426. ") +
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
            SELECT f.id, f.numar, f.directie, f.total, f.tva, f.tert_nume, f.data_emitere,
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


def compara_d390(baze, ic_facturi, patru_ochi=True):
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
                    "actiune": ("Verifică operațiunile: fie contabilizează facturile IC (%s), "
                                "fie corectează declarația recapitulativă dacă au fost "
                                "raportate greșit la VIES. Corecția o confirmă omul — nu e mecanică."
                                % ("notă validată, patru ochi" if patru_ochi else "notă validată")),
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


#: Tipul de constatare al SINGUREI perechi orizontale care exista azi (declaratie contra
#: declaratie, nu declaratie contra propriei surse). Masurat 01.09.2026: din tot ce confrunta
#: aplicatia, asta e singura pereche orizontala. `core/supervizor.py` o culege dupa eticheta asta.
TIP_D390_VS_D300 = "D390_VS_D300_IC"


def _stampileaza(constatari, tip):
    """Pune `tip_constatare` pe fiecare constatare. INVELIS, nu editare pe fiecare `return`: functia
    de mai jos are patru cai de iesire, iar una ratata ar fi lasat o constatare fara tip — iar
    supervizorul ar fi sarit-o TACUT, adica exact felul de tacere care arata ca un raspuns."""
    for c in constatari:
        if isinstance(c, dict):
            c["tip_constatare"] = tip
    return constatari


def compara_d390_vs_d300(baze, gasit, randuri, perioada=None):
    """Invelis: cheama comparatia si stampileaza tipul. Corpul e in `_compara_d390_vs_d300`."""
    return _stampileaza(_compara_d390_vs_d300(baze, gasit, randuri, perioada), TIP_D390_VS_D300)


def _compara_d390_vs_d300(baze, gasit, randuri, perioada=None):
    """PURA. baze = {"L": int, "A": int} (bazele IC din D390, recalculate pe ACEEAȘI perioadă ca D300
    depus). gasit = există D300 depus (bool). randuri = dict-ul `randuri` persistat al D300 depus (sau
    None = depus fără rânduri). perioada = eticheta perioadei evaluate (ex. "06/2026", "trimestrul
    2/2026") — se afișează explicit, fiindcă e alta decât restul ecranului (luna curentă).
    Reguli (cap secțiune F163 + regula direcțională VIES): zero depus -> GRI; randuri NULL -> GRI;
    D390>0 & D300 nu declară -> ROȘU (sugerat); ambele>0 diferite (sau D300>0 & D390=0) -> GRI (decalaj
    exigibilitate, NICIODATĂ roșu pe cifre); ambele 0 -> tăcut."""
    per_sufix = (", perioada %s" % perioada) if perioada else ""
    if not gasit:
        return [_absenta_libera(
            "d390", "D390 vs D300 depus" + per_sufix,
            ("Declarație-vs-declarație: D390 bază IC vs D300 depus (rânduri persistate). "
             "Niciun D300 depus prin aplicație în fereastra TVA -> nimic de comparat. GRI, nu roșu."),
            "Nu există D300 depus în fereastră — nu pot compara recapitulativa cu decontul.",
            "declarațiile D300 depuse prin aplicație, în fereastra TVA")]
    if randuri is None:
        return [_absenta_libera(
            "d390", "D390 vs D300 depus" + per_sufix,
            ("D300 din fereastră a fost depus fără rânduri persistate (depunere anterioară "
             "persistării rândurilor sau import istoric). GRI, nu roșu — absența datelor nu e divergență."),
            "D300 depus fără rânduri persistate — nu pot compara.",
            "rândurile persistate ale D300 depus din fereastră")]
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
                      f" ATENȚIE: {rand} absent din D300 depus. Rândul se derivă AUTOMAT din facturile "
                      "cu partener din UE (core/d300.py), și se scrie doar dacă existau astfel de "
                      "facturi la generare; în lipsa lor poate fi introdus manual, dar nu peste cel "
                      "derivat (dublă numărare, refuzată). Absența lui înseamnă că la generare nu "
                      "erau facturi IC înregistrate — NU că n-au existat operațiuni.")
        temei = (f"Declarație-vs-declarație: D390 bază {cheie} vs D300 depus rând {rand} "
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


def orizontal_d390_vs_d300(conn, schema, tip_dec, an, luna):
    """AXA ORIZONTALA a lui F163, cu O SINGURA iesire — invelis peste corpul de mai jos.

    **DE CE EXISTA ca functie, si nu ca bloc in `verifica_d390` (01.09.2026).** Comparatia
    declaratie-contra-declaratie avea CINCI cai de iesire, nu patru. Patru sunt in functia PURA
    `compara_d390_vs_d300` si aveau gard
    (`core/test_supervizor.py::test_perechea_orizontala_e_stampilata_pe_TOATE_caile`). A cincea —
    *nicio depunere D300 prin aplicatie* — traia un nivel mai sus, in corpul lui `verifica_d390`, si
    chema `_absenta_libera` DIRECT, fara `_stampileaza`. Constatarea iesea fara `tip_constatare`,
    iar `core/supervizor.constatari_firma` o SAREA tacut, socotind-o verticala.

    **MASURAT 01.09.2026, pe cele 19 firme ale portofoliului:** supervizorul vedea **3** constatari
    orizontale si pierdea tacut **13** — cele 13 firme fara nicio depunere D300. Tacerea arata exact
    ca un raspuns: pe ele supervizorul raporta *zero constatari*, care se citeste „n-am ce semnala",
    cand adevarul era „comparatia nici nu e posibila".

    **DE CE INVELIS, si nu inca un `_stampileaza` pe ramura care lipsea.** Peticirea ramurii ar fi
    lasat clasa in picioare: a sasea cale s-ar fi nascut la fel de tacut. Cu o singura iesire,
    ORICE cale noua din corp iese stampilata prin constructie. Aceeasi alegere ca la
    `compara_d390_vs_d300` (vezi `_stampileaza`), aplicata cu un nivel mai sus."""
    return _stampileaza(_orizontal_d390_vs_d300(conn, schema, tip_dec, an, luna),
                        TIP_D390_VS_D300)


def _orizontal_d390_vs_d300(conn, schema, tip_dec, an, luna):
    """CORPUL. Mutat VERBATIM din `verifica_d390` (01.09.2026) — comparatia nu s-a schimbat, doar
    locul ei si invelisul. `an`/`luna` raman perioada de RAPORTARE a constatarii (luna evaluata),
    nu perioada comparata: aia e a D300-ului depus si se afiseaza in eticheta."""
    from core import d390 as _d390   # local, ca in `verifica_d390` de unde a fost mutat blocul
    constatari = []
    rec_d300 = _d300_depus_recent(conn, schema)
    if rec_d300 is None:
        constatari.append(_absenta_libera(
            "d390", "D390 vs D300 depus",
            ("Declarație-vs-declarație: D390 bază IC vs rândurile intracomunitare ale D300 EFECTIV "
             "DEPUS (rânduri persistate). Nicio depunere D300 persistată -> comparația devine "
             "posibilă după prima depunere prin aplicație. GRI, nu roșu — absență, nu divergență."),
            "Nicio depunere D300 prin aplicație — nu am cu ce compara recapitulativa.",
            "depunerile D300 persistate prin aplicație"))
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
            constatari += _stampileaza([_gri_liber(
                "d390", "D390 vs D300 depus, perioada %s" % eticheta_d,
                "Declarație-vs-declarație: baza D390 se recalculează pe perioada D300 depus; recalcularea a eșuat.",
                "NU pot recalcula D390 pe perioada depusă (%s) pentru comparație (%s)." % (eticheta_d, e),
                an, luna)], TIP_D390_VS_D300)
    return constatari


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
        from core.perioada import PerioadaNeconfirmata
        if isinstance(e, PerioadaNeconfirmata):
            _cauza = str(e).replace("PERIOADA_BLOCATA: ", "")
            _actiune = "Confirmă perioada lunii (rol admin_firma)."
        elif isinstance(e, ValueError):
            _cauza = str(e)  # [cauza_precisa] eroare de business - nu o acoperi cu genericul
            _actiune = "Corectează în Date firmă ce indică mesajul, apoi reîncearcă."
        else:
            _cauza = "Date lipsă sau profil incomplet."
            _actiune = "Completează profilul firmei și facturile, apoi reîncearcă."
        return {"an": an, "luna": luna, "fereastra": fereastra, "stare": "gri",
                # [01.09.2026] IESIRE TIMPURIE: comparatia ORIZONTALA nu s-a atins. Se DECLARA,
                # ca supervizorul sa nu citeasca „n-am verificat" drept „n-am ce semnala".
                "orizontal_rulat": False, "constatari": [_gri_liber(
                    "d390", "Intracomunitar", "D390 nu s-a putut genera.",
                    f"NU pot verifica operațiunile intracomunitare: D390 nu se poate calcula ({e}).",
                    an, luna,
                    {"fel": "investigatie", "cauza": _cauza, "actiune": _actiune, "facturi": []})],
                "limita": "Verificarea D390 nu a fost efectuată — riscul rămâne neacoperit.",
                "modul": MODUL, "reguli": REGULI}
    ic_facturi = facturi_ic(conn, schema, data_de, data_pana)
    constatari = compara_d390(baze, ic_facturi, patru_ochi=_patru_ochi_activ(conn, schema))
    # [F163 D-vs-D real, deblocat F198] A TREIA sursă: D390 vs D300 DEPUS (randuri persistate).
    # Fereastra PROPRIE (nu luna curentă — D300 se depune în luna următoare, altfel permanent gri):
    # cea mai recentă perioadă cu D300 depus. Baza D390 se RECALCULEAZĂ pe acea perioadă, ca ambele
    # laturi să fie ACEEAȘI perioadă (comparație reală, nu perioade diferite). Perioada = afișată explicit.
    constatari += orizontal_d390_vs_d300(conn, schema, tip_dec, an, luna)
    if any(c["stare"] == "rosu" for c in constatari):
        stare = "rosu"
    elif any(c["stare"] == "gri" for c in constatari):
        stare = "gri"
    else:
        stare = "verde"
    necontate_tot = sum(1 for d in ("emisa", "primita")
                        for f in ic_facturi.get(d, []) if not f.get("contabilizata"))
    return {"an": an, "luna": luna, "fereastra": fereastra, "stare": stare,
            "orizontal_rulat": True, "constatari": constatari,

            "limita": ("Verificat: D390 bunuri IC (livrări L / achiziții A, auto din facturi) vs (1) evidența "
                       f"contabilă validată a acelorași facturi pe fereastra TVA curentă ({fereastra}) ȘI (2) D300 "
                       "DEPUS (rânduri persistate), pe CEA MAI RECENTĂ perioadă efectiv depusă (afișată în "
                       "verdict, alta decât luna curentă — D300 se depune în luna următoare), cu baza D390 "
                       "recalculată pe acea perioadă. CE CONFRUNTĂ, EXACT: R1_1/R5_1 ale D300 DEPUS se derivă "
                       "din ACELEAȘI facturi IC ca baza D390 (core/d300.py) — deci nu sunt două surse "
                       "independente. Ce prinde comparația e DERIVA dintre ce s-a depus ATUNCI și ce arată "
                       "evidența ACUM; NU prinde o eroare pe care ambele motoare o fac la fel. Gri dacă "
                       "rândurile lipsesc, dacă D300 e depus fără rânduri, sau dacă nu există nicio depunere. "
                       "NEVERIFICAT: servicii "
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
    return {"an": an, "luna": luna, "stare": "gri", "constatari": [_gri_liber(
                "d300", "Cotă TVA facturi emise",
                "Conformitatea cotei TVA nu s-a putut evalua.",
                f"NU pot verifica cota TVA a facturilor emise: {motiv}", an, luna,
                {"fel": "investigatie", "cauza": "Date lipsă sau necitibile.",
                 "actiune": "Verifică facturile emise ale lunii, apoi reîncearcă.",
                 "facturi": []})],
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
             "01.08.2025. LIMITĂ: se verifică doar liniile la cotă STANDARD; cota redusă (11%) și scutit "
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
        constatari = [] if verificate == 0 else [_fapt_liber(
            "d300", "Cotă TVA facturi emise", temei,
            "Toate facturile emise folosesc cota TVA corectă pentru perioadă.", an, luna,
            "cele %d linii cu cotă citibilă din facturile emise ale lunii" % verificate)]
        return {"an": an, "luna": luna, "stare": "verde", "constatari": constatari,
                "limita": limita, "modul": MODUL, "reguli": REGULI}

    ids = sorted(gresite)
    n = len(ids)
    ex = gresite[ids[0]]
    mesaj = (f"{n} factur{'ă' if n == 1 else 'i'} emis{'ă' if n == 1 else 'e'} cu cotă TVA greșită pentru "
             f"perioadă (ex. {ex['cota_gasita']}% în loc de {ex['cota_corecta']}%).")
    constatare = _neconform_liber(
        "d300", "Cotă TVA facturi emise", temei, mesaj,
        unde="facturile emise %s" % ", ".join(str(i) for i in ids[:6]),
        regula="cota_tva_neconforma_perioadei",
        remediu={"fel": "sugerat",
                 "cauza": (f"{n} facturi emise au cotă TVA neconformă perioadei "
                           f"(cotă veche folosită după schimbarea cotei standard)."),
                 "actiune": ("Verifică și corectează cota (stornare + reemitere sau factură de "
                             "corecție). Cota o confirmă omul, nu se ajustează automat."),
                 "facturi": ids})
    return {"an": an, "luna": luna, "stare": "rosu", "constatari": [constatare],
            "limita": limita, "modul": MODUL, "reguli": REGULI}


# ============================================================
#  RECONCILIERE SURSA <-> DECLARATIE, VIZIBILA IN CONTROL FISCAL (Tura 4, 10.08.2026)
#
#  CE E: ACEEASI reconciliere care ruleaza ca POARTA la generare (dXXX.genereaza cheama
#  dXXX_reconciliere.verifica_reconciliere, care RIDICA pe divergenta) - expusa AICI ca verdict
#  cu trei stari, ca sa se VADA in Control fiscal. NU un mecanism duplicat: refolosim FORMA care
#  NU ridica (dXXX_reconciliere.reconciliaza), identica cu ce cheama poarta; recalculul independent
#  din sursa NU se reimplementeaza - traieste o singura data, in dXXX_reconciliere.
#
#  res se produce prin functiile GENERATORULUI, read-only, pe calea GATE-FREE (pull + calcul_*,
#  ori d390.calculeaza / d112._d112_genereaza / d406.construieste) - exact ce face genereaza INAINTE
#  de poarta. NU chemam genereaza insasi, fiindca poarta ei ar RIDICA pe divergenta INAINTE sa
#  intoarca res, iar noi vrem raportul STRUCTURAT (care numeste AMBELE valori), nu o exceptie-string
#  colapsata (regula verificator VERDICT_COLAPSAT).
#
#  ANTI-"D300 mort" (lectia core/test_control_incrucisat_wiring.py): un apel rupt prin deriva de
#  semnatura / bug de cod NU trebuie inghitit tacit intr-un gri (acolo a murit tacit cross-check-ul
#  TVA: except Exception -> gri, verdict permanent gri). Distingem MECANIC, in doi pasi separati:
#    1. res nu se poate PRODUCE fiindca lipsesc date/profil -> generatorul ridica ValueError
#       ("nu se poate genera") -> GRI genuin ("nu pot verifica"), cu temei.
#    2. reconciliaza (recalculul) RIDICA ORICE -> contractul ei e sa NU ridice, deci e RUPTA
#       (deriva/bug) -> ROSU ZGOMOTOS "verificare intrerupta", NICIODATA gri.
#    Orice ALTA exceptie la producerea res (TypeError/AttributeError = deriva) -> tot ROSU rupt.
#  Divergenta reala (recalcul != generator) -> ROSU care NUMESTE AMBELE VALORI.
# ============================================================

class _SkipSubiect(Exception):
    """Semnal INTERN: declaratia nu are subiect in perioada (D100 pe zero, D205 fara dividende,
    D301 fara operatiuni) -> nimic de reconciliat, se SARE tacut (nu verde fara subiect, nu gri)."""


# ---- producere res GATE-FREE + thunk de reconciliere (aceeasi reconciliaza ca poarta) ------------
def _thunk_d300(conn, schema, an, luna):
    from core import d300 as _g, d300_reconciliere as _r
    from core.common import Perioada
    per = Perioada(an, luna=luna)
    prof, facturi = _g.pull(conn, schema, per)
    res = _g.calcul_d300(prof, per, facturi, None)
    return lambda: _r.reconciliaza(conn, per, res, None)


def _thunk_d394(conn, schema, an, luna):
    from core import d394 as _g, d394_reconciliere as _r
    from core.common import Perioada
    per = Perioada(an, luna=luna)
    prof, date = _g.pull(conn, schema, per)
    res = _g.calcul_d394(prof, per, date, None)
    return lambda: _r.reconciliaza(conn, per, res, None)


def _thunk_d301(conn, schema, an, luna):
    from core import d301 as _g, d301_reconciliere as _r
    from core.common import Perioada
    per = Perioada(an, luna=luna)
    prof, ops = _g.pull(conn, schema, per)
    res = _g.calcul_d301(prof, per, ops)
    return lambda: _r.reconciliaza(conn, per, res)


def _thunk_d390(conn, schema, an, luna):
    from core import d390 as _g, d390_reconciliere as _r
    res = _g.calculeaza(conn, schema, an, luna)   # calculeaza = gate-free (fara poarta zero, prin design)
    return lambda: _r.reconciliaza(conn, schema, an, luna, res)


def _thunk_d406(conn, schema, an, luna):
    from core import d406 as _g, d406_reconciliere as _r
    pulled = _g.pull(conn, schema, an, luna)
    prof, conturi, clienti, furnizori, note, fv, fc, plati = pulled[:8]
    res = _g.construieste(prof, an, luna, conturi, clienti, furnizori, note=note,
                          facturi_vanzare=fv, facturi_cumparare=fc, plati=plati)
    return lambda: _r.reconciliaza(conn, schema, an, luna, res)


def _thunk_d112(conn, schema, an, luna):
    from core import d112 as _g, d112_reconciliere as _r
    prof, salariati = _g.pull(conn, schema, an, luna)
    _g._d112_genereaza(prof, salariati, an, luna)   # scrie contributiile EMISE inapoi in salariati
    return lambda: _r.reconciliaza(conn, schema, an, luna, salariati)


def _thunk_d100(conn, schema, an, luna):
    from core import d100 as _g, d100_reconciliere as _r
    from core.common import Perioada
    per = Perioada(an, trim=(luna - 1) // 3 + 1)
    a2, l2 = per.an, per.trim * 3
    # pull intoarce (prof, venituri, cheltuieli); derivarea obligatiei NU se re-implementeaza aici -
    # o CHEAMA pe cea din generator (d100.deriva_obligatii), sursa unica -> thunk-ul nu poate drifta
    # de generator nici in aritate, nici in formula (baza profit = venituri - cheltuieli).
    prof, venituri, cheltuieli = _g.pull(conn, schema, per)
    obligatii, _ = _g.deriva_obligatii(prof, venituri, cheltuieli, a2, l2)
    if not obligatii:
        raise _SkipSubiect("D100 fara obligatie (venituri cont 70x = 0) - nimic de reconciliat.")
    res = _g.calcul_d100(prof, a2, l2, obligatii)
    return lambda: _r.reconciliaza(conn, per, res, None)


def _thunk_d101(conn, schema, an, luna):
    from core import d101 as _g, d101_reconciliere as _r
    from core.common import Perioada
    per = Perioada(an)
    prof, r = _g.pull(conn, schema, per)
    intrari = {"P1": r.get("ven_expl", 0), "P2": r.get("chelt_expl", 0),
               "P4": r.get("ven_fin", 0), "P5": r.get("chelt_fin", 0)}
    res = _g.calcul_d101(prof, per.an, intrari,
                         rezerva={"capital": r.get("capital", 0),
                                  "rezerva_existenta": r.get("rezerva_existenta", 0),
                                  "chelt_impozit": r.get("chelt_impozit", 0)})
    return lambda: _r.reconciliaza(conn, schema, per, res, None)


def _thunk_d205(conn, schema, an, luna):
    from core import d205 as _g, d205_reconciliere as _r
    from core.common import Perioada, cota as _cota
    from datetime import date as _date
    per = Perioada(an)
    prof, asoc, total_distribuit, total_platit = _g.pull(conn, schema, per)
    beneficiari = []   # replica derivarii automate din d205.genereaza (fara poarta)
    if total_platit > 0 and asoc:
        cd = _cota("impozit_dividend", _date(per.an, 12, 31))[0]   # period-aware, din registrul de lege
        for a in asoc:
            platit = _g._i(Decimal(str(total_platit)) * Decimal(str(a["cota"])) / Decimal(100))
            distribuit = _g._i(Decimal(str(total_distribuit)) * Decimal(str(a["cota"])) / Decimal(100))
            if platit > 0:
                impozit = _g._i(Decimal(platit) * cd)
                beneficiari.append({"categ": "1.a", "nume": a["nume"], "cif": a.get("cnp") or "",
                                    "baza": platit, "imp": impozit, "castig": 0, "pierdere": 0,
                                    "divid_d": max(distribuit, platit), "divid_p": platit, "tip_plata": "2"})
    if not beneficiari:
        raise _SkipSubiect("D205 fara dividende platite (cont 457) - nimic de reconciliat.")
    res = _g.calcul_d205(prof, per.an, beneficiari)
    return lambda: _r.reconciliaza(conn, schema, per, res, None)


# ---- descriere STRUCTURATA a divergentei (numeste AMBELE valori, prin _lei) ----------------------
def _descrie_div(d):
    """Un rand de divergenta de reconciliere -> propozitie care NUMESTE ambele valori (declarat vs
    recalcul din sursa). Acopera formele tuturor celor 9 reconciliatoare (rand/camp/cont/beneficiar...)."""
    ce = (d.get("eticheta") or d.get("camp") or d.get("rand") or d.get("sectiune"))
    if not ce and d.get("cont"):
        ce = "cont %s %s" % (d.get("cont"), d.get("latura"))
    if not ce and d.get("salariat") is not None:
        ce = "salariat %s" % d.get("salariat")
    if not ce and d.get("beneficiar"):
        ce = "beneficiar %s" % d.get("beneficiar")
    ce = ce or "valoare"
    gen = d.get("generator")
    if gen is None:
        gen = d.get("saft")
    c2 = d.get("cale2")
    if c2 is None:
        c2 = d.get("cale2_imp")
    if gen is not None and c2 is not None:
        return "%s: declarat %s, recalcul din sursa %s (diferenta %s)." % (
            ce, _lei(gen), _lei(c2), _lei(_d(gen) - _d(c2)))
    if d.get("cale2_baza") is not None:
        return "%s: lipseste din declaratie; recalcul din sursa baza %s, impozit %s." % (
            ce, _lei(d.get("cale2_baza")), _lei(d.get("cale2_imp") or 0))
    return "%s: divergenta intre declaratie si recalculul independent din sursa." % ce


# ---- constructori de constatare (anatomia control_incrucisat: stare + eticheta + mesaj + temei) --
# [P8, 21.08.2026] O CONSTATARE E O AFIRMATIE, imbracata pentru ecran. Pana azi era proza intr-un
# dictionar: `mesaj` purta tot - ce s-a constatat, pe ce perioada, pe ce se sprijina - iar cine randa
# trebuia sa ghiceasca. Acum textul vine din afirmatie (`motiv`), iar felul e DECLARAT, nu dedus.
#
# `mesaj` ramane, cu ACEEASI valoare ca `motiv`, fiindca randorul il citeste. NU sunt doua texte:
# `_imbraca` il deriva, si `test_control_incrucisat` asertaza ca nu pot diverge. Ziua in care randorul
# citeste `motiv` e ziua in care `mesaj` dispare - dar aia atinge ecranul, deci e alta decizie.
def _imbraca(eticheta, temei, stare, remediu, a, cheie=None):
    """Afirmatia -> constatarea pe care o asteapta ecranul. Textul are o singura sursa.

    Campurile se pun UNUL CATE UNUL, nu printr-un al doilea dictionar-literal: un `{... "mesaj": ...}`
    aici ar fi numarat de `core/scan_afirmatii` drept inca o afirmatie netipata, iar constructorul
    afirmatiilor ar aparea pe vecie in clichet ca datorie. Nu e cosmetica - e adevarat ca nu exista
    doua dictionare, ci unul singur, imbogatit."""
    c = dict(a)
    c["stare"] = stare
    c["eticheta"] = eticheta
    c["mesaj"] = a["motiv"]
    c["temei"] = temei
    c["remediu"] = remediu
    if cheie is not None:
        c["declaratie"] = cheie
    return c


def _c_verde(cheie, eticheta, temei, an=None, luna=None):
    """FAPT: recalculul independent din sursa confirma valorile declarate.

    `temei_completitudine` numeste PE CE se sprijina afirmatia - aici, faptul ca recalculul a pornit
    din sursa, nu din declaratie. Fara el, „se reconciliaza" ar fi o absenta bine imbracata."""
    return _imbraca(eticheta, temei, "verde", None, cheie=cheie, a=_af.afirmatie(
        "fapt", cheie,
        "Declarația se reconciliază cu sursa - recalculul independent confirmă valorile.",
        an=an, luna=luna,
        temei_completitudine="recalcul independent sursă->declarație (core/%s_reconciliere.py)" % cheie))


def _c_rosu(cheie, eticheta, temei, mesaj, an=None, luna=None):
    """CONTRADICTIE: declaratia si recalculul independent spun lucruri incompatibile.

    NU e „declaratia e gresita" - gardul nu alege singur cine are dreptate, si `sursele` le numeste pe
    amandoua tocmai ca sa se poata arbitra."""
    return _imbraca(eticheta, temei, "rosu", cheie=cheie,
                    remediu={"fel": "investigatie",
                     "cauza": "Recalculul independent din sursa NU confirma valoarea declarata.",
                     "actiune": ("Verifică agregarea și datele sursă - gardul nu alege singur cine are "
                                 "dreptate. ACEEAȘI reconciliere blochează generarea declarației la depunere."),
                     "facturi": []},
                    a=_af.afirmatie("contradictie", cheie, mesaj,
                                    sursele="valoarea declarată în %s; recalculul independent din sursă"
                                            % eticheta))


def _c_gri(cheie, eticheta, temei, motiv, an=None, luna=None):
    """NECUNOASTERE: nu pot reconcilia, si spun pe ce perioada nu pot.

    Domeniul e LUNA evaluata, nu „toate perioadele": o necunoastere fara capete se citeste peste sase
    luni ca fapt permanent."""
    dom = ("%04d-%02d" % (an, luna)) if (an and luna) else (str(an) if an else None)
    return _imbraca(eticheta, temei, "gri", cheie=cheie,
                    remediu={"fel": "investigatie", "cauza": "Date sau profil fiscal incomplet.",
                             "actiune": "Completează datele firmei și reîncearcă.", "facturi": []},
                    a=_af.afirmatie("necunoastere", cheie,
                                    "NU pot reconcilia %s: %s" % (eticheta, motiv),
                                    domeniu_de=dom, domeniu_pana=dom))


def _c_rupt(cheie, eticheta, e, an=None, luna=None):
    """ANTI-"D300 mort": verificarea s-a RUPT (bug/deriva de semnatura), NU e "nu pot verifica" (gri).
    Se semnaleaza ROSU ZGOMOTOS, ca sa nu redevina un verdict permanent gri, ascuns.

    [P8] Felul e `verificare_rupta`, nu `necunoastere` - pe ecran arata la fel, in date NU mai arata:
    cine numara „cate nu pot fi verificate" nu mai inghite si rupturile."""
    return _imbraca(
        eticheta + " - VERIFICARE INTRERUPTA",
        ("Contractul reconciliere: recalculul (reconciliaza) NU ridică; dacă ridică, e derivă de "
         "semnătură / bug de cod. Un except->gri l-ar ascunde ca verdict permanent gri - vezi "
         "core/test_control_incrucisat_wiring.py."),
        "rosu",
        cheie=cheie,
        remediu={"fel": "investigatie", "cauza": "Cod / semnătură reconciliere ruptă.",
                 "actiune": "Verifică semnătura apelului de reconciliere pentru această declarație.",
                 "facturi": []},
        a=_af.afirmatie("verificare_rupta", cheie,
                      ("Reconcilierea %s s-a oprit cu o eroare (%s: %s) - NU e 'date lipsă', ci verificare "
                       "RUPTĂ. Semnalat ROȘU, nu ascuns gri (lecția D300 mort)."
                       % (eticheta, type(e).__name__, e)),
                      eroare="%s: %s" % (type(e).__name__, e)))


def _interpreteaza(cheie, eticheta, temei, rap, an=None, luna=None):
    """Raportul (non-raising) al reconciliatorului -> constatare cu trei stari. Rosu numeste AMBELE valori."""
    div = list(rap.get("divergente") or [])
    susp = list(rap.get("suspecte") or [])     # D112: date corupte pe angajat emis (loud, nu tacut)
    dez = rap.get("dezechilibru")              # D406: dubla partida dezechilibrata
    if div or susp or dez:
        parti = [_descrie_div(d) for d in div[:6]]
        for s in susp[:6]:
            parti.append("salariat %s: %s (date suspecte, nu caz fiscal legitim)." % (s.get("salariat"), s.get("motiv")))
        if dez:
            parti.append("dubla partida dezechilibrata in declaratie: debit %s vs credit %s (diferenta %s)."
                         % (_lei(dez["debit"]), _lei(dez["credit"]), _lei(dez["diferenta"])))
        return _c_rosu(cheie, eticheta, temei, eticheta + ": " + " ".join(parti), an, luna)
    if rap.get("acoperit") is False and rap.get("neacoperit"):
        # Reconcilierea nu se APLICA (limita declarata). Afirmatia vine GATA de la reconciliator, cu
        # domeniul ei - nu se reconstruieste aici, ca sa nu existe doua surse ale perioadei.
        return _imbraca(eticheta, temei, "gri", cheie=cheie,
                        remediu={"fel": "investigatie",
                                 "cauza": "Date sau profil fiscal incomplet.",
                                 "actiune": "Completează datele firmei și reîncearcă.",
                                 "facturi": []},
                        a=rap["neacoperit"])
    return _c_verde(cheie, eticheta, temei, an, luna)

# [P8] Constatari produse in AFARA caii de reconciliere (verificarile incrucisate). Aceleasi feluri,
# alta imbracaminte: unele locuri n-au `declaratie`, altele n-au remediu. Nu un al doilea nomenclator.
def _gri_liber(tip, eticheta, temei, mesaj, an=None, luna=None, remediu=None):
    """NECUNOASTERE: nu pot verifica, si spun PE CE PERIOADA nu pot. O necunoastere fara capete se
    citeste peste sase luni ca fapt permanent."""
    dom = ("%04d-%02d" % (an, luna)) if (an and luna) else (str(an) if an else None)
    return _imbraca(eticheta, temei, "gri", remediu,
                    _af.afirmatie("necunoastere", tip, mesaj, domeniu_de=dom, domeniu_pana=dom))


def _absenta_libera(tip, eticheta, temei, mesaj, surse):
    """ABSENTA_OBSERVATIE: n-am inregistrari intr-o sursa NUMITA. Deosebita de necunoastere fiindca
    aici stim unde ne-am uitat - iar „nicio depunere D300 persistata" nu inseamna „nu stiu"."""
    return _imbraca(eticheta, temei, "gri", None,
                    _af.afirmatie("absenta_observatie", tip, mesaj, surse_consultate=surse))


def _fapt_liber(tip, eticheta, temei, mesaj, an, luna, temei_completitudine, remediu=None,
                stare="verde"):
    """FAPT pe o perioada anume. `temei_completitudine` spune pe ce se sprijina - fara el, un fapt
    negativ e o absenta bine imbracata.

    `stare` e parametru, nu ceva de pus dupa. Prima forma o suprascria la apel
    (`c["stare"] = "gri"`) si verificatorul a prins-o (VERDICT_COLAPSAT, stare-literal): un verdict
    carpit dupa constructie e un verdict cu doua surse. Un fapt poate fi VERDE (confirma) sau GRI
    (informativ, fara contrapartida declarata) - amandoua sunt fapte."""
    return _imbraca(eticheta, temei, stare, remediu,
                    _af.afirmatie("fapt", tip, mesaj, an=an, luna=luna,
                                  temei_completitudine=temei_completitudine))


def _neconform_liber(tip, eticheta, temei, mesaj, unde, regula, remediu=None):
    """NECONFORMITATE: valori care nu satisfac o regula. `unde` le NUMESTE (id-uri), `regula` spune
    de ce nu tin - altfel e un repros fara adresa."""
    return _imbraca(eticheta, temei, "rosu", remediu,
                    _af.afirmatie("neconformitate", tip, mesaj, unde=unde, regula=regula))


def _ruleaza_una(conn, schema, cheie, eticheta, thunk_builder, an, luna):
    """Ruleaza O reconciliere cu clasificarea anti-"D300 mort" (vezi capul sectiunii). Nu ridica."""
    temei = ("Aceeasi reconciliere sursa<->declaratie care blocheaza generarea (%s vs recalcul independent "
             "din sursa, core/%s_reconciliere.py); expusa aici ca verdict, NU mecanism nou." % (eticheta, cheie))
    # PASUL 1 - producerea res (functiile generatorului, read-only). ValueError = "nu se poate genera"
    # (date/profil) -> gri genuin; orice altceva = deriva/bug -> ROSU rupt (nu gri).
    try:
        thunk = thunk_builder(conn, schema, an, luna)
    except _SkipSubiect:
        return None
    except ValueError as e:
        return _c_gri(cheie, eticheta, temei, str(e), an, luna)
    except Exception as e:
        return _c_rupt(cheie, eticheta, e, an, luna)
    # PASUL 2 - recalculul independent (reconciliaza). Contractul ei e sa NU ridice: ORICE exceptie aici
    # e o RUPTURA (deriva de semnatura = exact bug-ul D300 mort) -> ROSU, NICIODATA gri.
    try:
        rap = thunk()
    except Exception as e:
        return _c_rupt(cheie, eticheta, e, an, luna)
    return _interpreteaza(cheie, eticheta, temei, rap, an, luna)


def _vector_firma(conn, schema):
    """Vectorul fiscal (regim/platitor/decont/IC/partida) + are_salariati - o singura citire, calificata
    pe schema. FARA default fiscal inline (fiecare camp e citit ca FAPT; partida din regim_contabil)."""
    from core.migrare_api import regim_contabil
    vector = {}
    with conn.cursor() as cur:
        cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, tip_firma "
                    "FROM %s.firma_profil LIMIT 1" % schema)
        row = cur.fetchone()
        if row:
            vector = {"regim_fiscal": row[0], "platitor_tva": row[1], "tip_decont": row[2],
                      "operatiuni_ic": row[3], "tip_firma": row[4],
                      "partida_simpla": regim_contabil(row[4]) == "simpla"}
        cur.execute("SELECT to_regclass(%s)", (schema + ".salariati",))
        are_sal = False
        if cur.fetchone()[0]:
            cur.execute("SELECT count(*) FROM %s.salariati WHERE "
                        "(data_incetare IS NULL OR data_incetare >= CURRENT_DATE) AND "
                        "(data_angajare IS NULL OR data_angajare <= CURRENT_DATE)" % schema)
            are_sal = cur.fetchone()[0] > 0
    return vector, are_sal


def _d301_are_ops(conn, schema, an, luna):
    """D301 se reconciliaza doar daca luna are operatiuni IC inregistrate (altfel n-are subiect)."""
    try:
        return luna in d301_luni_operatiuni(conn, schema, an)
    except Exception:
        return False


def reconciliaza_declaratii(conn, schema, an, luna):
    """SUPRAFATA UNIFICATA: reconciliere SURSA <-> DECLARATIE pentru toate declaratiile APLICABILE firmei,
    cu trei stari (verde/rosu/gri), refolosind ACEEASI reconciliere ca poarta de generare (vezi capul
    sectiunii). Nu ridica. Perioadele: lunare/TVA pe (an, luna); D100 pe trimestrul lunii; D101/D205 pe
    anul `an`. Intoarce {an, luna, stare, constatari:[...structurate...], limita, modul, reguli}.

    [21.08.2026] `explicatie` SCOASA din container: camp mort. Nu-l citea nimeni - nici
    control_verdict.js (randeaza `limita`), nici firme.js (il declara IGNORAT), nici vreun modul
    Python; nu iesea prin /api/v1 (firme/facturi/kpi/balanta), nu se persista, nu ajungea in PDF.
    Sapte din douasprezece erau sirul gol; cinci calculau o fraza pe care n-o vedea nimeni.
    Daca vreodata containerul chiar are ce explica, se construieste atunci - cu un consumator real."""
    vector, are_sal = _vector_firma(conn, schema)
    platitor = vector.get("platitor_tva")
    regim = (vector.get("regim_fiscal") or "").strip().lower()
    partida_simpla = vector.get("partida_simpla")
    operatiuni_ic = vector.get("operatiuni_ic")

    plan = []   # (cheie, eticheta, thunk_builder) - DOAR declaratiile aplicabile pe vector/fapt
    if platitor is True:
        plan.append(("d300", "D300 (decont TVA)", _thunk_d300))
        plan.append(("d394", "D394 (informativa TVA)", _thunk_d394))
        if operatiuni_ic is True:
            plan.append(("d390", "D390 (recapitulativa IC)", _thunk_d390))
    if platitor is False and _d301_are_ops(conn, schema, an, luna):
        plan.append(("d301", "D301 (TVA neinregistrati)", _thunk_d301))
    if are_sal:
        plan.append(("d112", "D112 (salarii)", _thunk_d112))
    if not partida_simpla:
        plan.append(("d406", "D406 (SAF-T)", _thunk_d406))
        if regim in ("micro", "profit"):
            plan.append(("d100", "D100 (impozit micro/profit)", _thunk_d100))
        if regim == "profit":
            plan.append(("d101", "D101 (impozit pe profit)", _thunk_d101))
        plan.append(("d205", "D205 (impozit dividende)", _thunk_d205))

    constatari = []
    for cheie, eticheta, tb in plan:
        c = _ruleaza_una(conn, schema, cheie, eticheta, tb, an, luna)
        if c is not None:
            constatari.append(c)

    if any(c["stare"] == "rosu" for c in constatari):
        stare = "rosu"
    elif any(c["stare"] == "gri" for c in constatari):
        stare = "gri"
    else:
        stare = "verde"

    return {"an": an, "luna": luna, "stare": stare, "constatari": constatari,
            "limita": ("Reconciliere sursă<->declarație pentru declarațiile aplicabile firmei, cu ACEEAȘI "
                       "reconciliere care blochează generarea (dXXX_reconciliere.reconciliaza - recalcul "
                       "independent din sursă). Verde=recalculul confirmă; roșu=divergență (ambele valori "
                       "numite) sau verificare ruptă; gri=nu pot verifica (date/profil lipsă). NEVERIFICAT: "
                       "declarațiile fără subiect în perioadă (sărite tăcut, nu verde fals). Perioade: TVA/"
                       "salarii/SAF-T pe lună; D100 pe trimestru; D101/D205 pe an."),
            "modul": MODUL, "reguli": REGULI}


# ============================================================
#  AXA ORIZONTALĂ, PERECHILE ANUALE ALE D101 (02.09.2026, la comanda lui Costin)
#
#  DE CE EXISTĂ, spus de el: *„perechea de azi nu o face, și tu ai scris de ce"*. D390 și D300 se
#  derivă amândouă din aceleași facturi IC — deci verdele lor înseamnă „cele două motoare sunt de
#  acord", nu „declarația se potrivește cu realitatea". Perechile de mai jos confruntă surse care
#  NU se derivă una din alta.
#
#  FIECARE IDENTITATE E VERIFICATĂ LA SURSĂ, ÎN CORPUS, ÎNAINTE DE A FI SCRISĂ AICI.
# ============================================================

#: Codurile de obligație din D100 care sunt impozit pe profit / plăți anticipate în contul lui.
#: `d100.COD_BUGETAR` emite azi doar `103`; `102`/`105` sunt tratate ca aceeași familie de
#: `d100._scadenta` (v. `if cod in ("102", "103", "105")`), deci intră aici ca să nu se rateze
#: tăcut o depunere veche sau una făcută în afara aplicației. **`121` (impozit micro) NU intră** —
#: e altă taxă, iar amestecul ei ar produce divergență falsă pe firmele cu trecere micro->profit.
COD_OBLIG_PROFIT = frozenset(("102", "103", "105"))

#: Contul în care se înregistrează impozitul pe profit. **OMFP 1802/2014, verbatim:**
#: „691. Cheltuieli cu impozitul pe profit". NU se folosește rândul 35 al F20 — acolo
#: `core/bilant.py` pune `691 + 698`, iar 698 e, tot verbatim, „Cheltuieli cu impozitul pe venit
#: și cu alte impozite care nu apar în elementele de mai sus": **altă taxă**. Pe o firmă cu trecere
#: micro->profit în același an, sumarea celor două ar produce o divergență falsă. În plus, antetul
#: lui `core/bilant.py` își declară singur sursa formulelor de rând ca „VERSIUNE NECUNOSCUTĂ" —
#: deci numerotarea F20 n-ar fi un temei, ci o presupunere.
CONT_IMPOZIT_PROFIT = "691"

TIP_D101_VS_D100 = "D101_VS_D100_PLATI_ANTICIPATE"
TIP_D101_VS_691 = "D101_VS_CONT_691"


def _depuneri(conn, schema, tip, an):
    """[(an, luna, randuri)] — TOATE depunerile de tipul dat, pe anul dat, prin aplicație.

    Spre deosebire de `_d300_depus_randuri` (care ia o perioadă anume), aici se adună **anul
    întreg**: identitatea D101↔D100 e pe an, iar D100 se depune trimestrial."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
        row = cur.fetchone()
        if not row:
            return []
        cur.execute("SELECT an, luna, randuri FROM public.declaratii_depuse_curente "
                    "WHERE tenant_id = %s AND tip = %s AND an = %s ORDER BY luna",
                    (row[0], tip, an))
        return [(r[0], r[1], r[2]) for r in cur.fetchall()]


def _plati_anticipate_din_d100(depuneri):
    """PURĂ. Suma „Suma de plată" a obligațiilor de impozit pe profit din D100-urile depuse.

    Întoarce `(suma, nr_depuneri_cu_obligatie, nr_depuneri_fara_randuri)`. A treia cifră contează:
    o depunere fără rânduri persistate **nu e** o depunere cu zero — iar dacă le-aș aduna la fel,
    aș produce un total mai mic decât realitatea și l-aș numi divergență."""
    total = Decimal("0")
    cu = 0
    fara_randuri = 0
    for _an, _luna, randuri in depuneri:
        if not randuri:
            fara_randuri += 1
            continue
        obligatii = (randuri or {}).get("obligatii") or []
        gasit = False
        for o in obligatii:
            if str((o or {}).get("cod_oblig") or "") in COD_OBLIG_PROFIT:
                total += _d((o or {}).get("suma_plata") or 0)
                gasit = True
        if gasit:
            cu += 1
    return total, cu, fara_randuri


def orizontal_d101(conn, schema, an):
    """ÎNVELIȘ: o singură ieșire, și fiecare constatare își poartă tipul ei.

    **De ce NU `_stampileaza` ca la perechea D390.** Acolo toate constatările au ACELAȘI tip, deci
    un înveliș care pune un tip fix e corect. Aici sunt **două** tipuri; un înveliș cu tip fix ar
    pune tipul greșit pe jumătate dintre ele, **tăcut** — adică exact clasa pe care învelișul o
    apăra. Deci învelișul verifică, nu atribuie."""
    cs = _orizontal_d101(conn, schema, an)
    fara = [c for c in cs if not (isinstance(c, dict) and c.get("tip_constatare"))]
    if fara:
        raise AssertionError(
            "%d constatări ale perechilor D101 au ieșit fără `tip_constatare` — supervizorul le-ar "
            "sări tăcut, iar firma ar părea curată" % len(fara))
    return cs


def _d101_depus_recent(conn, schema):
    """Anul CELUI MAI RECENT D101 depus prin aplicație, sau None.

    **De ce nu se evaluează anul curent.** D101 se depune pentru anul ÎNCHEIAT, deci pe anul curent
    nu există niciodată — iar o pereche ancorată pe el ar fi GRI PERMANENT prin construcție. Aceeași
    capcană pe care perechea D390 a rezolvat-o cu `_d300_depus_recent`; se refolosește tiparul."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
        row = cur.fetchone()
        if not row:
            return None
        cur.execute("SELECT max(an) FROM public.declaratii_depuse_curente "
                    "WHERE tenant_id = %s AND tip = 'd101'", (row[0],))
        r = cur.fetchone()
    return r[0] if (r and r[0]) else None


def _orizontal_d101(conn, schema, _an_curent):
    """CORPUL. Cele două perechi anuale ale D101, pe surse independente.

    `_an_curent` NU e anul evaluat — v. `_d101_depus_recent`. Se primește ca să nu se schimbe
    semnătura culegerii, și se ignoră deliberat; numele îl spune."""
    rez = []
    an = _d101_depus_recent(conn, schema)
    if an is None:
        for tip, et in ((TIP_D101_VS_D100, "D101 vs D100 depuse (plăți anticipate)"),
                        (TIP_D101_VS_691, "D101 vs contabilitate (cont 691)")):
            rez += _stampileaza([_absenta_libera(
                "d101", et,
                ("Confruntare declarație-vs-sursă-independentă, pe an. Niciun D101 depus prin "
                 "aplicație, pe niciun an -> comparația devine posibilă după prima depunere. GRI, "
                 "nu roșu: absența unei depuneri nu e o divergență."),
                "Niciun D101 depus prin aplicație — nu pot confrunta nimic.",
                "declarațiile D101 depuse prin aplicație")], tip)
        return rez
    d101 = _depuneri(conn, schema, "d101", an)
    cu_randuri = [(a, l, r) for (a, l, r) in d101 if r]

    if not d101:
        for tip, et in ((TIP_D101_VS_D100, "D101 vs D100 depuse (plăți anticipate)"),
                        (TIP_D101_VS_691, "D101 vs contabilitate (cont 691)")):
            rez += _stampileaza([_absenta_libera(
                "d101", "%s — %d" % (et, an),
                ("Confruntare declarație-vs-sursă-independentă pe anul %d. Niciun D101 depus prin "
                 "aplicație pe anul ăsta -> nu am ce confrunta. GRI, nu roșu: absența unei depuneri "
                 "nu e o divergență." % an),
                "Niciun D101 depus prin aplicație pe %d — nu pot confrunta nimic." % an,
                "declarațiile D101 depuse prin aplicație, pe anul %d" % an)], tip)
        return rez
    if not cu_randuri:
        for tip, et in ((TIP_D101_VS_D100, "D101 vs D100 depuse (plăți anticipate)"),
                        (TIP_D101_VS_691, "D101 vs contabilitate (cont 691)")):
            rez += _stampileaza([_absenta_libera(
                "d101", "%s — %d" % (et, an),
                "D101 depus fără rânduri persistate (depunere anterioară persistării sau import "
                "istoric). GRI, nu roșu — absența datelor nu e divergență.",
                "D101 depus pe %d, dar fără rânduri persistate — nu pot confrunta." % an,
                "rândurile persistate ale D101 depus pe %d" % an)], tip)
        return rez

    _a, _l, r101 = cu_randuri[-1]
    P = (r101 or {}).get("P") or {}
    d_grup = int((r101 or {}).get("d_grup") or 0)
    p48 = _d(P.get("P48") or 0)
    p50 = _d(P.get("P50") or 0)

    rez += _stampileaza(_pereche_p50(conn, schema, an, p50, d_grup), TIP_D101_VS_D100)
    rez += _stampileaza(_pereche_691(conn, schema, an, p48, d_grup), TIP_D101_VS_691)
    return rez


def _pereche_p50(conn, schema, an, p50, d_grup):
    """D101 rd.50 vs suma „Suma de plată" din D100-urile depuse pe an.

    **IDENTITATEA, VERBATIM (OPANAF 206/2025, instrucțiunile formularului 101):** *„Rândul 50 - se
    înscriu, pentru anul de raportare, după caz, sumele reprezentând impozit pe profit, impozit pe
    profit la nivelul impozitului minim pe cifra de afaceri sau plăți anticipate în contul
    impozitului pe profit, declarate trimestrial prin formularul 100, la rândul «Suma de plată»."*

    **SURSE INDEPENDENTE, și de-aia perechea are rost:** rândul 50 e o valoare pe care o pune
    contabilul în D101; suma din dreapta e ce s-a **declarat efectiv** trimestrial. Niciuna nu se
    derivă din cealaltă.

    **EXCEPȚIA DE GRUP, tot verbatim:** *„În cazul membrilor unui grup fiscal în domeniul
    impozitului pe profit, rândurile 41.2, 48, 50, 52 și 53 din formular nu se completează."* Deci
    pe `d_grup=1` perechea **tace** — nu e verde, nu e gri: nu se aplică."""
    eticheta = "D101 rd.50 vs D100 depuse — %d" % an
    temei = ("OPANAF 206/2025, instrucțiunile formularului 101, rândul 50: sumele declarate "
             "trimestrial prin formularul 100, la rândul «Suma de plată». Confruntă ce a scris "
             "contabilul în D101 cu ce s-a declarat efectiv în D100 — două surse independente.")
    if d_grup:
        return []                      # membru de grup: rândul nu se completează -> fără subiect
    dep = _depuneri(conn, schema, "d100", an)
    if not dep:
        if p50 == 0:
            return []                  # nimic declarat, nimic depus: tăcut, fără subiect
        return [_gri_liber(
            "d101", eticheta,
            temei + " Niciun D100 depus prin aplicație pe anul ăsta.",
            "D101 declară %s plăți anticipate, dar niciun D100 nu e depus prin aplicație pe %d — "
            "nu pot confrunta. Absența depunerii prin aplicație NU dovedește că n-a fost depusă."
            % (_lei(p50), an), an, 12)]
    suma, cu, fara = _plati_anticipate_din_d100(dep)
    if fara:
        return [_gri_liber(
            "d101", eticheta,
            temei + " %d din %d depuneri D100 n-au rânduri persistate." % (fara, len(dep)),
            "Nu pot confrunta: %d din %d depuneri D100 pe %d n-au rânduri persistate, deci suma "
            "lor nu se poate citi. O depunere fără rânduri nu e o depunere cu zero."
            % (fara, len(dep), an), an, 12)]
    dif = p50 - suma
    baza = {"eticheta": eticheta, "declarat_d101": int(p50), "declarat_d100": int(suma),
            "diferenta": int(dif), "nr_d100": cu}
    if p50 == 0 and suma == 0:
        return []
    if abs(dif) <= TOLERANTA:
        return [dict(baza, stare="verde", temei=temei, remediu=None,
                     mesaj="%s: rândul 50 și suma «de plată» din cele %d D100 depuse coincid (%s)."
                           % (eticheta, cu, _lei(p50)))]
    return [dict(baza, stare="rosu", temei=temei,
                 mesaj="%s: D101 rândul 50 = %s, iar D100 depuse însumează %s (diferență %s)."
                       % (eticheta, _lei(p50), _lei(suma), _lei(dif)),
                 remediu={"fel": "sugerat",
                          "cauza": "Rândul 50 din D101 trebuie să fie suma «de plată» declarată "
                                   "trimestrial prin D100 pe anul %d; cele %d depuneri D100 "
                                   "însumează %s." % (an, cu, _lei(suma)),
                          "actiune": "Verifică dacă rândul 50 a fost completat din alt an, dacă "
                                     "lipsește un trimestru, sau dacă o depunere s-a făcut în afara "
                                     "aplicației. Corecția o confirmă omul.",
                          "facturi": []})]


def _ciorna_pe_cont(conn, schema, an, cont):
    """Exista note NEVALIDATE care ating contul, in anul dat? `rulaje_interval` numara doar
    `status='validata'` — deci fara intrebarea asta, o nota in ciorna arata identic cu absenta ei."""
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT count(*) FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE i.data >= %s AND i.data < %s AND i.status <> 'validata'
              AND (l.cont_debit = %s OR l.cont_credit = %s)
        """, ("%d-01-01" % an, "%d-01-01" % (an + 1), cont, cont))
        return (cur.fetchone() or [0])[0] > 0


def _pereche_691(conn, schema, an, p48, d_grup):
    """D101 rd.48 vs rulajul debitor al contului 691 pe an.

    **IDENTITATEA:** rd.48 e, verbatim (OPANAF 206/2025), *„impozitul pe profit anual datorat"*
    (prin rd.48.1) sau impozitul la nivelul impozitului minim pe cifra de afaceri (rd.48.2).
    Contabil, acesta se înregistrează în contul **691** — OMFP 1802/2014, verbatim: *„691.
    Cheltuieli cu impozitul pe profit"*.

    **SURSE INDEPENDENTE:** stânga e calculul fiscal al declarației, dreapta e ce s-a înregistrat
    efectiv în contabilitate. Costin: *„Doar impozitul; baza diferă legitim prin cheltuieli
    nedeductibile"* — de-aia se compară impozitul, nu profitul.

    **NU se compară cu rândul 35 al F20**, care adună `691 + 698`; 698 e „Cheltuieli cu impozitul pe
    venit și cu alte impozite" — altă taxă. Vezi `CONT_IMPOZIT_PROFIT`.

    **Pe membrii de grup, rd.48 nu se completează** (verbatim, aceeași frază ca la rd.50), iar
    impozitul din decontările de grup merge în contul 694, nu 691 — deci perechea nu se aplică."""
    eticheta = "D101 rd.48 vs cont 691 — %d" % an
    temei = ("OPANAF 206/2025 rd.48 («impozitul pe profit anual datorat») față de contul 691 "
             "(«Cheltuieli cu impozitul pe profit», OMFP 1802/2014), rulaj debitor pe anul %d, "
             "numai note VALIDATE. Declarația față de evidență — surse independente. NU se "
             "folosește rândul 35 al F20: acolo 691 e adunat cu 698 (impozit pe VENIT), iar "
             "numerotarea F20 stă pe o sursă declarată de modul ca versiune necunoscută." % an)
    if d_grup:
        return []
    rulaje = rulaje_interval(conn, schema, "%d-01-01" % an, "%d-01-01" % (an + 1),
                             [CONT_IMPOZIT_PROFIT])
    contabil = _d(rulaje.get(CONT_IMPOZIT_PROFIT, {}).get("debit") or 0)
    dif = p48 - contabil
    # O nota de regularizare inca in CIORNA explica LEGITIM diferenta — iar o explicatie legitima
    # strica definitia unei constatari CERTE (criteriul lui Costin). Se inchide numind-o: cat timp
    # exista ciorna pe 691, perechea nu afirma o eroare, spune ca nu poate inca sa se pronunte.
    if abs(dif) > TOLERANTA and _ciorna_pe_cont(conn, schema, an, CONT_IMPOZIT_PROFIT):
        return [_gri_liber(
            "d101", eticheta,
            temei + " Exista note NEVALIDATE pe contul 691 in anul evaluat.",
            "Nu ma pronunt inca: D101 declara %s, contul 691 are %s validat, dar exista note in "
            "CIORNA pe 691 pe %d. Diferenta se poate inchide la validarea lor — deci nu e o eroare "
            "constatata, e o verificare care asteapta." % (_lei(p48), _lei(contabil), an), an, 12)]
    baza = {"eticheta": eticheta, "declarat_d101": int(p48), "inregistrat_691": int(contabil),
            "diferenta": int(dif)}
    if p48 == 0 and contabil == 0:
        return []
    if abs(dif) <= TOLERANTA:
        return [dict(baza, stare="verde", temei=temei, remediu=None,
                     mesaj="%s: impozitul declarat și cel înregistrat în 691 coincid (%s)."
                           % (eticheta, _lei(p48)))]
    return [dict(baza, stare="rosu", temei=temei,
                 mesaj="%s: D101 declară %s, iar contul 691 are rulaj debitor %s (diferență %s)."
                       % (eticheta, _lei(p48), _lei(contabil), _lei(dif)),
                 remediu={"fel": "sugerat",
                          "cauza": "Impozitul pe profit anual datorat (rd.48) diferă de cheltuiala "
                                   "înregistrată în contul 691 pe %d." % an,
                          "actiune": "Verifică nota de regularizare a impozitului la închiderea "
                                     "anului, și dacă impozitul micro (cont 698) n-a fost "
                                     "înregistrat din greșeală în 691. Corecția o confirmă omul.",
                          "facturi": []})]
