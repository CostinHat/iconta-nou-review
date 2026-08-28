# -*- coding: utf-8 -*-
"""
core/salarii_contare.py — contabilizarea statului de plata (nota ciorna).

CONSTRUIT, nu portat din /opt/iconta:10475 (autocont_sal_v1). Vechiul avea doua
defecte dovedite mecanic la 15.07.2026, care ar fi migrat intacte:
  1. _sum("cam") = 0 -- pull() nu seteaza "cam" (verificat: grep pe core/d112.py
     nu-l gaseste). Filtrul `if s > 0` sarea linia 646=436 -> CAM NU se contabiliza
     NICIODATA. Bug tacit viu in productie pe port 8000: contul 436 gol, dar
     declaratia cere CAM la plata.
  2. status='validata' direct -- ocolea patru-ochi.
Al treilea motiv de reconstructie: vechiul reagrega din pull(), dar generatorul D112
RECALCULEAZA cas/cass/impozit pe salariatii cu concediu medical (baza CM) si adauga
suprataxa part-time separat. O nota construita din pull() ar contrazice declaratia
exact pe cazurile grele -- adica ar fabrica chiar erorile pe care F163 le prinde.

  [R34, 28.08.2026] PARAGRAFUL DE MAI SUS A DESCRIS EXACT DEFECTUL PE CARE MODULUL L-A AVUT
  PANA AZI. Reconstructia n-a scapat de a doua socoteala: `note_lunare` chema din nou
  `calcul_salariu`, sub un comentariu care spunea ca nu recalculeaza. Masurat pe 40 de perechi:
  29 de divergente pe 10 perechi, fix pe cele patru pozitii fiscale. DECIZIA lui Costin: sursa
  e D112. Cele patru se CITESC din obligatiile declarate ale perioadei (`d112.obligatii`), iar
  `calcul_salariu` ramane pentru ce e legitim al lui — brutul si tichetele.

CE FACE control_coerenta, DUPA DECIZIA DIN 25.08.2026 (Costin, R33): compara totalul notei
propuse cu XML-ul D112, cont cu cont, in limita toleranta_d112(N), si SEMNALEAZA divergentele.
NU blocheaza. Motivul, in cuvintele lui: *"aplicatia compara o propunere cu o declaratie generata
din alte date. Cand cele doua difera, nu se stie CARE greseste - poate declaratia e veche, poate
nota e corecta. Un blocaj ar presupune ca declaratia are dreptate."* Masurat: 10 din 40 de perechi
diverg; un blocaj pe un sfert din cazuri, fara sa stim cine greseste, opreste munca fara sa spuna
nimic.

TEXTUL DE MAI SUS A FOST FALS PANA AZI, si merita spus fiindca e clasa R16. Scria: *"nota se scrie
DOAR daca totalul coincide ... refuzam sa scriem"*. Nimic nu se scria si nimic nu refuza:
`control_coerenta` n-avea niciun apelant, si nici `note_lunare` - deci salariile nu deveneau
niciodata nota contabila. Proza descria o garantie inexistenta, iar testele treceau, fiindca
testele cheama functiile direct.
"""
from decimal import Decimal

MODUL = "salarii_contare"
REGULI = "2026.1"


# [R34, 28.08.2026] HARTA: fiecare obligatie declarata la ANAF are UN debit contabil si UN
# credit. Nu e o distributie inventata de mine — codurile D112 sunt deja despartite pe exact
# distinctia care conteaza in contabilitate (retinut de la salariat vs suportat de unitate):
#   602 impozit          -> 421 = 444    (retinut din salariu)
#   412 CAS              -> 421 = 4315   (retinut)
#   432 CASS             -> 421 = 4316   (retinut)
#   480 CAM              -> 646 = 436    (cheltuiala unitatii)
#   458 CAS part-time    -> 6451 = 4315  (suprataxarea, suportata de unitate)
#   459 CASS part-time   -> 6453 = 4316  (idem)
# De-aia trecerea nu cere nicio regula de repartizare: 412 si 458 cad amandoua pe 4315, dar din
# debite diferite, si fiecare stie din care.
CONT_D112 = (
    ("602", "421", "444"),
    ("412", "421", "4315"),
    ("432", "421", "4316"),
    ("480", "646", "436"),
    ("458", "6451", "4315"),
    ("459", "6453", "4316"),
)
#: creditele care NU se mai calculeaza per salariat — vin din declaratie
CREDITE_DIN_D112 = frozenset(c for _cod, _dt, c in CONT_D112)

# [R33/QQ, 28.08.2026] CELE DOUA POZITII PE CARE CONTROLUL CHIAR POATE GASI CEVA.
# Dupa R34, cele patru pozitii fiscale sunt copiate din declaratie, deci comparatia lor cu
# declaratia e o tautologie (vezi `control_coerenta`). Ce ramane calculat INDEPENDENT de D112 in
# nota propusa sunt exact doua conturi, si alea capata acum contra-valoarea lor DECLARATA:
#   * 641 = 421 — salariile brute REALIZATE. Contrapartida in declaratie e `B_brutSalarii`
#     (= C1_11 = suma B2_5), despre care generatorul spune explicit ca e „DOAR salariul REALIZAT
#     (bazac), EXCLUDE indemnizatia" — adica exact ce intra pe 641. NU `B4_3` (brutul
#     CONTRACTUAL): pe o luna cu concediu medical alea difera prin constructie, iar o ancora care
#     difera prin constructie produce zgomot, nu masuratoare.
#   * 642 = 5328 — biletele de valoare ACORDATE. Contrapartida e sectiunea 8.3: `E3_10` (masa) +
#     `E3_75` (vacanta), aceleasi doua tipuri pe care nota le pune pe 5328.
#
# [R86-B, DIAGNOSTIC 28.08.2026] ANCORA LUI 641 ARE O ABATERE CUNOSCUTA, SI NU E A NOTEI.
# Masurat pe tenant_001, salariat cu salariat, 5 luni: din 12 salariati diverge EXACT UNUL - cel de
# la salariul minim - si diverge EXACT cu facilitatea: 300,00 in aprilie-iunie (minim 4.050, nivel
# de referinta 3.750), 200,00 in iulie-august (4.325 / 4.125). Restul e rotunjire sub-leu (±0,14 /
# ±0,48 / ±0,24), din rotunjirea D112 la leu per salariat.
# CAUZA, structural: cele doua cifre NU SUNT ACEEASI MARIME.
#   * `calc["brut"]` = salariul brut REALIZAT, intreg - ce datoreaza angajatorul, deci ce intra pe 641;
#   * `B_brutSalarii` (= C1_11 = suma B2_5) = BAZA CONTRIBUTIVA, din care facilitatea de la salariul
#     minim e SCAZUTA (OUG 89/2025 art.III: nivelul de referinta se diminueaza cu 300 lei).
# Iar D112 nu declara nicaieri „brutul realizat" ca atare: are baza contributiva (B2_5), brutul
# CONTRACTUAL (B4_3, care pe o luna cu concediu medical difera prin constructie) si venitul brut
# total (E1_1, care include tichetele). Deci lipsa nu e o cifra gresita in nota - e o CONTRAPARTIDA
# care nu exista in declaratie. Ce se face cu asta e o decizie, nu o corectura: vezi R86.
VERIFICARE_REALA = (
    ("Salarii brute realizate", "421", ("angajatorB", ("B_brutSalarii",))),
    ("Bilete de valoare acordate", "5328", ("asiguratE3", ("E3_10", "E3_75"))),
)


def _suma_din_xml(xml, tag, atribute):
    """Suma unui atribut peste toate elementele cu tagul dat. Citeste ARTEFACTUL emis."""
    import re
    total = 0
    for m in re.finditer(r"<%s ([^>]*)/>" % tag, xml):
        corp = m.group(1)
        for a in atribute:
            g = re.search(r'%s="(-?\d+)"' % a, corp)
            if g:
                total += int(g.group(1))
    return total


def _d(v):
    return Decimal(str(v or 0))


def document_ref(an, luna):
    return "SAL %02d/%04d" % (luna, an)


def note_lunare(conn, schema, an, luna, xml_d112=None):
    """Notele statului de plata, agregate pe (debit, credit) din monografie_salariu per salariat.

    [R34 — DECIZIA lui Costin, 28.08.2026] CELE PATRU POZITII FISCALE NU SE MAI CALCULEAZA AICI.
    444 (impozit), 4315 (CAS), 4316 (CASS) si 436 (CAM) se CITESC din D112-ul perioadei, prin
    `d112.obligatii`. Motivul e chiar comentariul de mai jos, care spunea din 15.07 *"NU
    recalculam: al doilea calcul ar fi a doua cifra"* — si care era FALS, fiindca exact sub el
    `calcul_salariu` era chemat din nou. Codul se aliniaza la propria lui intentie scrisa.

    CE MASURA, inainte: 40 de perechi firma x luna, **29 de divergente pe 10 perechi**, pe fix
    aceste patru pozitii. Cea mai mare: `tenant_001` 2026-06, CAS 24.114,54 in nota vs 28.539
    declarat. Al doilea calcul nu reproducea primul — generatorul D112 recalculeaza pe baza CM
    si adauga suprataxarea part-time separat, iar reagregarea din `calcul_salariu` nu le vedea.

    DE CE 436 NU PUTEA VENI DIN `pull()`, desi asa suna litera deciziei: `pull()` **nu poarta
    CAM** — nu seteaza cheia deloc (e chiar bug-ul nr.1 din antetul modulului, dovedit la
    15.07). Singurul loc unde CAM exista ca valoare a perioadei e obligatia **480** din
    declaratia emisa. Deci sursa e D112 ca ARTEFACT, nu dictionarul intermediar al lui `pull`.
    Litera spunea `pull`, intentia spunea *"cifra declarata, nu una recalculata"* — s-a urmat
    intentia, si se scrie de ce.

    CE NU MAI POATE SPUNE `control_coerenta`, si trebuie spus tare: comparand nota cu
    declaratia pe cele patru pozitii, compara acum declaratia cu ea insasi. **Pe pozitiile
    astea nu mai poate iesi rosu niciodata** — nu fiindca s-ar potrivi, ci fiindca sunt aceeasi
    cifra. Divergenta a fost eliminata la sursa, nu detectata mai bine. Ce ramane sub control
    real: 641/421 (brut), 642/5328 (tichete) si structura notei. *(Consemnat si la R34 in
    `CONFORMITATE.md`; daca pe viitor se vrea un control CU dinti pe cele patru, el nu poate fi
    „nota vs declaratie" — trebuie sa fie „declaratie vs o a treia sursa".)*

    `xml_d112` se paseaza cand XML-ul a fost deja generat (vezi `propunere`), ca sa nu se
    genereze de doua ori pentru acelasi raspuns.
    """
    from core import d112 as _d112, salarizare as _sz, beneficii_api as _ben
    from datetime import date as _dt
    _prof, salariati = _d112.pull(conn, schema, an, luna)
    ref = _dt(an, luna, 1)
    agg = {}
    # [F133 Faza 2b1] cadou NEIMPOZABIL: nu trece prin calcul_salariu/D112, dar e cheltuiala reala
    # (bilete de valoare 642=5328) pe valoarea TOTALA acordata in luna. Acordarea, nu achizitia
    # biletelor (5328=5121/401 = tranzactie separata). 5328 nu e cont D112 -> nu rupe control_coerenta.
    cadou_total = sum(_ben.lista_luna(conn, schema, an, luna, "cadou").values())
    if cadou_total > 0:
        agg[("642", "5328")] = agg.get(("642", "5328"), Decimal("0")) + _d(cadou_total)
    for s in salariati:
        # pull() a calculat DEJA salariatul, cu toti parametrii (persoane, norma,
        # venit contractual, brut lucrat). NU recalculam: al doilea calcul ar fi a
        # doua cifra. Aceleasi valori pe care le declara D112 -> coerenta prin
        # constructie. (15.07.2026: aici a fost bug - calcul_salariu(brut, la_data)
        # gol, aceeasi greseala ca in pull inainte de aliniere; prins de control_coerenta.)
        calc = _sz.calcul_salariu(
            (s.get("brut_lucrat") if s.get("brut_lucrat") is not None else s.get("brut")) or 0,
            persoane=s.get("persoane_intretinere") or 0, la_data=ref,
            norma_intreaga=not s.get("part_time"),
            venit_brut_total=float(s.get("brut") or 0),
            sub_26=_sz.sub_26_la(s.get("data_nastere"), ref),   # [deducere suplimentara] coerenta contare<->D112
            copii_scoala=(int(s.get("copii_scolarizati") or 0) if s.get("declaratie_copii") else 0),
            declaratie_copii=bool(s.get("declaratie_copii")),
            data_angajare=s.get("data_angajare"),
            data_incetare=s.get("data_incetare"),
            # [R86/RR1] TICHETELE. Fara ele, `tichete_nominal` iesea 0 si linia 642=5328 nu se
            # producea deloc — o cheltuiala reala care nu intra in evidenta. Valorile vin din
            # `pull`, care le-a calculat o data (zile din pontaj, exces peste plafonul anual);
            # NU se recalculeaza aici, ca sa nu apara a doua socoteala — chiar clasa R34.
            tichet_valoare=float(s.get("tichet_masa_valoare") or 0),
            tichet_zile=int(s.get("tichet_zile") or 0),
            tichet_vacanta=float(s.get("tichet_vacanta_net") or 0),
            tichet_vacanta_exces=float(s.get("exces_vacanta") or 0),
            tichet_cultural=float(s.get("tichet_cultural") or 0),
            tichet_cresa=float(s.get("tichet_cresa") or 0),
            cadou_taxabil=float(s.get("cadou_taxabil") or 0))
        for n in _sz.monografie_salariu(calc):
            # [R34] pozitiile fiscale se sar aici: vin din declaratie, mai jos. Filtrul e pe
            # CREDIT fiindca acolo stau cele patru conturi, indiferent din ce debit vin (421
            # pentru retineri, 646/6451/6453 pentru ce suporta unitatea).
            if n["credit"] in CREDITE_DIN_D112:
                continue
            k = (n["debit"], n["credit"])
            agg[k] = agg.get(k, Decimal("0")) + _d(n["suma"])
    # [R34] cele patru pozitii, CITITE din obligatiile declarate ale perioadei
    obl = _d112.obligatii(conn, schema, an, luna, xml_d112)
    for cod, debit, credit in CONT_D112:
        v = _d(obl.get(cod, 0))
        if v > 0:
            agg[(debit, credit)] = agg.get((debit, credit), Decimal("0")) + v
    return [(d, c, s) for (d, c), s in sorted(agg.items()) if s > 0], len(salariati)


def _bani(x):
    return float(_d(x).quantize(Decimal("0.01")))


def control_coerenta(note, conn, schema, an, luna, xml_d112=None):
    """Nota propusa vs D112 declarat. Intoarce lista de DIVERGENTE (goala = coerent).

    Fiecare divergenta e un obiect cu ambele cifre, nu o fraza:

        {"eticheta": "CAS", "cont": "4315",
         "nota": 1234.00,          # ce ar scrie nota propusa
         "declaratie": 1200.00,    # ce declara D112
         "diferenta": -34.00,      # declaratie - nota
         "toleranta": 4.00}

    Costin, 25.08.2026: *"ce trebuie sa arate semnalul: ce spune nota, ce spune declaratia, si
    care e diferenta. Nu «exista o divergenta» - cifrele amandoua."* Textul il compune ecranul
    (DS cap.13: textul nu e purtator de decizie), iar cifrele nu se pot compune din proza inapoi.

    [R33/QQ, 28.08.2026] DOUA FELURI DE DIVERGENTA, si diferenta NU e cosmetica — `fel`:

      * **`"regresie"`** — cele patru pozitii fiscale (444, 4315, 4316, 436). Dupa R34 ele se
        CITESC din declaratie, deci comparatia lor cu declaratia compara declaratia cu ea insasi.
        **Nu pot diverge azi.** Raman comparate mecanic fiindca un rosu acolo ar insemna ca cineva
        a reintrodus un calcul independent — adica **cablaj stricat, nu dezacord fiscal**. Cel care
        vede un asemenea rosu sa nu caute in date: sa caute in `note_lunare`.
      * **`"verificare"`** — 641/421 si 642/5328, singurele doua pozitii pe care nota le calculeaza
        INDEPENDENT de D112. Aici un rosu inseamna ce insemna inainte: cele doua cai spun lucruri
        diferite despre aceeasi luna, si nu se stie care greseste.

    *Cine citeste rezultatul si nu se uita la `fel` primeste acelasi lucru ca inainte; cine se uita
    afla daca semnalul e despre bani sau despre cablaj.*

    NU ridica si nu refuza nimic: semnalul e informatie pentru om, nu o poarta."""
    from core import d112 as _d112
    from core import control_incrucisat as _ci
    xml = xml_d112 if xml_d112 is not None else _d112.genereaza(conn, schema, an, luna)[0]
    totaluri = _ci.totaluri_d112_din_xml(xml)
    rulaj = {}
    for d, c, s in note:
        rulaj.setdefault(c, {"credit": Decimal("0"), "debit": Decimal("0")})["credit"] += s
    tol = _ci.toleranta_d112(_nr_salariati_xml(xml))
    div = []

    def _confrunta(eticheta, cont, decl, fel):
        prop = rulaj.get(cont, {}).get("credit", Decimal("0"))
        if abs(decl - prop) > tol:
            div.append({"eticheta": eticheta, "cont": cont, "fel": fel,
                        "nota": _bani(prop), "declaratie": _bani(decl),
                        "diferenta": _bani(decl - prop), "toleranta": _bani(tol)})

    # [R34] cele patru pozitii fiscale — garda de REGRESIE: nu pot diverge azi
    for eticheta, coduri, cont in _ci.COD_CONT_D112:
        _confrunta(eticheta, cont, sum(_d(totaluri.get(k, 0)) for k in coduri), "regresie")
    # [QQ2] cele doua pozitii calculate independent — verificarea REALA
    for eticheta, cont, (tag, atribute) in VERIFICARE_REALA:
        _confrunta(eticheta, cont, _d(_suma_din_xml(xml, tag, atribute)), "verificare")
    return div


def propunere(conn, schema, an, luna):
    """Propunerea de nota a statului de plata, IMPREUNA cu semnalul de coerenta.

    Cele doua stau intr-un singur raspuns fiindca decizia lui Costin le leaga: semnalul apare
    *"la propunere - singurul moment in care omul poate face ceva cu informatia; la inchiderea
    lunii e prea tarziu, iar pe suprafata de control fiscal e o constatare despre trecut."*

    NU SCRIE NIMIC. `note_lunare` si `control_coerenta` doar citesc si calculeaza; generarea D112
    din interior nu persista (verificat: `d112.py`, `d112_reconciliere.py` si `reconciliere_emis.py`
    n-au niciun INSERT/UPDATE/DELETE)."""
    from core import d112 as _d112
    xml, _av = _d112.genereaza(conn, schema, an, luna)   # [R34] o singura generare pe raspuns
    note, nr = note_lunare(conn, schema, an, luna, xml_d112=xml)
    div = control_coerenta(note, conn, schema, an, luna, xml_d112=xml)
    return {
        "an": an, "luna": luna,
        "document_ref": document_ref(an, luna),
        "nr_salariati": nr,
        "note": [{"debit": d, "credit": c, "suma": _bani(v)} for d, c, v in note],
        "total": _bani(sum(v for _d1, _c1, v in note)),
        "divergente": div,
    }


def _nr_salariati_xml(xml):
    import re
    m = re.search(r'angajatorB[^>]*B_sal="(\d+)"', xml)
    return int(m.group(1)) if m else 0
