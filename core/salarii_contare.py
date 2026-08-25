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


def _d(v):
    return Decimal(str(v or 0))


def document_ref(an, luna):
    return "SAL %02d/%04d" % (luna, an)


def note_lunare(conn, schema, an, luna):
    """Notele statului de plata, agregate pe (debit, credit) din monografie_salariu
    per salariat. Sursa: aceiasi salariati pe care ii declara D112."""
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
            data_incetare=s.get("data_incetare"))
        for n in _sz.monografie_salariu(calc):
            k = (n["debit"], n["credit"])
            agg[k] = agg.get(k, Decimal("0")) + _d(n["suma"])
    return [(d, c, s) for (d, c), s in sorted(agg.items()) if s > 0], len(salariati)


def _bani(x):
    return float(_d(x).quantize(Decimal("0.01")))


def control_coerenta(note, conn, schema, an, luna):
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

    NU ridica si nu refuza nimic: semnalul e informatie pentru om, nu o poarta."""
    from core import d112 as _d112
    from core import control_incrucisat as _ci
    xml, _av = _d112.genereaza(conn, schema, an, luna)
    totaluri = _ci.totaluri_d112_din_xml(xml)
    rulaj = {}
    for d, c, s in note:
        rulaj.setdefault(c, {"credit": Decimal("0"), "debit": Decimal("0")})["credit"] += s
    tol = _ci.toleranta_d112(_nr_salariati_xml(xml))
    div = []
    for eticheta, coduri, cont in _ci.COD_CONT_D112:
        decl = sum(_d(totaluri.get(k, 0)) for k in coduri)
        prop = rulaj.get(cont, {}).get("credit", Decimal("0"))
        if abs(decl - prop) > tol:
            div.append({"eticheta": eticheta, "cont": cont,
                        "nota": _bani(prop), "declaratie": _bani(decl),
                        "diferenta": _bani(decl - prop), "toleranta": _bani(tol)})
    return div


def propunere(conn, schema, an, luna):
    """Propunerea de nota a statului de plata, IMPREUNA cu semnalul de coerenta.

    Cele doua stau intr-un singur raspuns fiindca decizia lui Costin le leaga: semnalul apare
    *"la propunere - singurul moment in care omul poate face ceva cu informatia; la inchiderea
    lunii e prea tarziu, iar pe suprafata de control fiscal e o constatare despre trecut."*

    NU SCRIE NIMIC. `note_lunare` si `control_coerenta` doar citesc si calculeaza; generarea D112
    din interior nu persista (verificat: `d112.py`, `d112_reconciliere.py` si `reconciliere_emis.py`
    n-au niciun INSERT/UPDATE/DELETE)."""
    note, nr = note_lunare(conn, schema, an, luna)
    div = control_coerenta(note, conn, schema, an, luna)
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
