# -*- coding: utf-8 -*-
"""Categoria de mărime a entității — precondiția care lipsea din aplicație (R3, lista 3).

DE CE EXISTĂ. `POST /tenants/{id}/s1005-valideaza` și perechea `s1003` produc situații financiare
**fără să poată ști dacă e cea datorată**: regimul se alege dintr-un `<select>` de pe ecran. Cerința
lui Costin, 26.08.2026: *„situațiile financiare cerute depind de categoria de mărime. Dacă aceasta nu
există ca dimensiune, ruta nu poate ști ce datorează firma — se declară, nu se presupune."* Măsurat
atunci și reconfirmat pe 30.08: `categorie_marime`, `micro_entitate`, `CATEGORII_MARIME` — **zero
potriviri** în tot codul de producție. Nu era câmp, nu era derivare, nu era nici măcar un nume.

CE FACE, ȘI CE NU FACE. Derivă cele trei criterii din datele firmei și **încadrează**. NU alege
formularul în locul omului și nu atinge rutele de bilanț: încadrarea e o **afirmație**, cu domeniul
și temeiul ei; ce face cineva cu ea e altă decizie.

DOUĂ LUCRURI PE CARE O IMPLEMENTARE NAIVĂ LE-AR RATA, și amândouă sunt în normă:

  1. **Categoria nu se schimbă de la un an la altul.** pct. 13 alin. (2): entitatea schimbă categoria
     *„doar dacă în două exerciții financiare consecutive depășește sau încetează să depășească
     criteriile"*, iar alin. (3) spune care două: exercițiul **precedent** celui de raportare și cel
     **curent**. Deci o încadrare făcută pe un singur an **nu e încadrarea cerută de normă** — e cel
     mult indicatorul anului ăluia.
  2. **Pragul se trece pe DOUĂ din trei, nu pe unul.** pct. 9 alin. (2) și (3): *„nu depășesc
     limitele a cel puțin două dintre următoarele trei criterii"*.

CONSECINȚA CARE CONTEAZĂ: dacă indicatorii anului precedent nu se pot calcula, categoria **nu se
poate determina**. Nu se cade pe „micro" fiindcă e cea mai mică, și nu se cade pe anul curent fiindcă
e singurul disponibil. *Un necunoscut nu se rotunjește la ce știi* (interdicția 32).
"""
from decimal import Decimal

from core import bilant as _b
from core.afirmatii import afirmatie
from core.common import Temei

MODUL = "categorie_marime"

#: Nomenclator ÎNCHIS al categoriilor. `nedeterminata` NU e o categorie a normei — e starea în care
#: aplicația spune că nu poate încadra, și există tocmai ca să nu fie confundată cu „micro".
CATEGORII = ("micro", "mici", "mijlocii_mari", "nedeterminata")

_TEMEI_DOI_ANI = Temei(
    "OMFP", 1802, 2014, art="pct.13", alin="2",
    data_in="2015-01-01", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/omfp_1802_2014_reglementari_consolidat.txt",
    text_citat=("pct.13 alin.(2): entitatea schimba categoria in care se incadreaza doar daca in "
                "doua exercitii financiare consecutive depaseste sau inceteaza sa depaseasca "
                "criteriile de marime; alin.(3): prin doua exercitii consecutive se intelege "
                "exercitiul precedent celui pentru care se intocmesc situatiile financiare anuale "
                "si exercitiul curent"))

_TEMEI_TOTAL_ACTIVE = Temei(
    "OMFP", 1802, 2014, art="pct.15",
    data_in="2015-01-01", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/omfp_1802_2014_reglementari_consolidat.txt",
    text_citat=("pct.15: totalul activelor mentionat la pct. 9 si 10 consta in valoarea totala a "
                "activelor, asa cum apare prezentata la lit. A-C de la «Active» din formatul "
                "bilantului prevazut la pct. 132 sau din formatul bilantului prescurtat, pct. 451"))

#: {categorie: {criteriu: prag}}. Pragurile NU se scriu ca literale la locul folosirii — se citesc de
#: aici, iar fiecare poartă temeiul actului care le-a fixat.
# Fiecare prag stă ÎMPREUNĂ cu temeiul lui, în aceeași expresie — forma din `common.COTE`. Nu e stil:
# `scan_constante` citește constantele fiscale și cere `Temei` lângă valoare; un temei ținut ca
# cheie-soră arată, pentru orice cititor mecanic, ca o constantă nesursată. *Și are dreptate: o cifră
# și temeiul ei despărțite de o virgulă se pot despărți și de o editare.*
PRAGURI = {
    "micro": {
        "total_active": (Decimal("2250000"), Temei(
            "OMFP", 1802, 2014, art="pct.9", alin="2", lit="a",
            data_in="2024-08-23", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
                 url="anaf_surse/omfp_1802_2014_reglementari_consolidat.txt",
            text_citat=("pct.9 alin.(2) lit.a): microentitatile sunt entitatile care, la data "
                        "bilantului, nu depasesc limitele a cel putin doua dintre urmatoarele trei "
                        "criterii: a) totalul activelor: 2.250.000 lei"),
            lant_acte=("modificata de ORDINUL 4.164 din 12 august 2024, MO 843 din 23.08.2024, "
                       "art.I pct.2"))),
        "cifra_afaceri_neta": (Decimal("4500000"), Temei(
            "OMFP", 1802, 2014, art="pct.9", alin="2", lit="b",
            data_in="2024-08-23", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
                 url="anaf_surse/omfp_1802_2014_reglementari_consolidat.txt",
            text_citat="pct.9 alin.(2) lit.b): cifra de afaceri neta: 4.500.000 lei",
            lant_acte=("modificata de ORDINUL 4.164 din 12 august 2024, MO 843 din 23.08.2024, "
                       "art.I pct.2"))),
        "nr_mediu_salariati": (10, Temei(
            "OMFP", 1802, 2014, art="pct.9", alin="2", lit="c",
            data_in="2015-07-09", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
            url="anaf_surse/omfp_1802_2014_reglementari_consolidat.txt",
            text_citat=("pct.9 alin.(2) lit.c): numarul mediu de salariati in cursul exercitiului "
                        "financiar: 10"),
            lant_acte=("alin.(2) modificat de ORDINUL 773 din 1 iulie 2015, MO 509 din 09.07.2015, "
                       "art.8 alin.(1); literele a) si b) modificate ulterior de ORDINUL 4.164/2024"))),
    },
    "mici": {
        "total_active": (Decimal("25000000"), Temei(
            "OMFP", 1802, 2014, art="pct.9", alin="3", lit="a",
            data_in="2024-08-23", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
                 url="anaf_surse/omfp_1802_2014_reglementari_consolidat.txt",
            text_citat=("pct.9 alin.(3) lit.a): entitatile mici sunt entitatile care nu se incadreaza "
                        "in categoria microentitatilor si care nu depasesc limitele a cel putin doua "
                        "dintre urmatoarele trei criterii: a) totalul activelor: 25.000.000 lei"),
            lant_acte=("modificata de ORDINUL 4.164 din 12 august 2024, MO 843 din 23.08.2024, "
                       "art.I pct.3"))),
        "cifra_afaceri_neta": (Decimal("50000000"), Temei(
            "OMFP", 1802, 2014, art="pct.9", alin="3", lit="b",
            data_in="2024-08-23", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
                 url="anaf_surse/omfp_1802_2014_reglementari_consolidat.txt",
            text_citat="pct.9 alin.(3) lit.b): cifra de afaceri neta: 50.000.000 lei",
            lant_acte=("modificata de ORDINUL 4.164 din 12 august 2024, MO 843 din 23.08.2024, "
                       "art.I pct.3"))),
        "nr_mediu_salariati": (50, Temei(
            "OMFP", 1802, 2014, art="pct.9", alin="3", lit="c",
            data_in="2015-07-09", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
            url="anaf_surse/omfp_1802_2014_reglementari_consolidat.txt",
            text_citat=("pct.9 alin.(3) lit.c): numarul mediu de salariati in cursul exercitiului "
                        "financiar: 50"),
            lant_acte=("alin.(3) modificat de ORDINUL 773 din 1 iulie 2015, MO 509 din 09.07.2015, "
                       "art.8 alin.(1); literele a) si b) modificate ulterior de ORDINUL 4.164/2024"))),
    },
}


def prag(categorie, criteriu):
    """Valoarea pragului, fără temei. Există ca să nu se scrie `[0]` prin cod."""
    return PRAGURI[categorie][criteriu][0]


def temei(categorie, criteriu):
    return PRAGURI[categorie][criteriu][1]

CRITERII = ("total_active", "cifra_afaceri_neta", "nr_mediu_salariati")

#: Nomenclator ÎNCHIS al motivelor. Proza rămâne scrisă pentru om; codul e pentru mașină. Fără el,
#: orice gardă ar fi nevoită să caute cuvinte în mesaj — adică să păzească formularea, nu regula
#: (clichetul 50 / METODA §23).
MOTIVE = ("fara_exercitiu_precedent", "criterii_incomplete", "aceeasi_incadrare", "nu_se_schimba")


def depaseste(ind, praguri):
    """{criteriu: True/False/None} — pe fiecare criteriu, dacă indicatorul depășește pragul.

    `None` înseamnă **indicator necunoscut**, nu „nu depășește". Distincția e chiar miezul: norma
    cere „cel puțin două din trei", iar un necunoscut tratat ca zero ar împinge orice firmă spre
    micro.
    """
    out = {}
    for c in CRITERII:
        v = ind.get(c)
        p = praguri[c][0] if isinstance(praguri[c], tuple) else praguri[c]
        out[c] = None if v is None else (Decimal(str(v)) > Decimal(str(p)))
    return out


def _incadrare_an(ind):
    """Categoria pe UN singur exercițiu — pas intermediar, NU verdictul normei (vezi pct.13)."""
    d_micro = depaseste(ind, PRAGURI["micro"])
    d_mici = depaseste(ind, PRAGURI["mici"])
    if list(d_micro.values()).count(None) or list(d_mici.values()).count(None):
        # se poate totuși decide dacă cele CUNOSCUTE ajung singure la „două din trei"
        if sum(1 for v in d_micro.values() if v is True) < 2 and \
           sum(1 for v in d_micro.values() if v is False) < 2:
            return None
    if sum(1 for v in d_micro.values() if v is True) < 2:
        return "micro"
    if sum(1 for v in d_mici.values() if v is True) < 2:
        return "mici"
    return "mijlocii_mari"


def incadreaza(ind_curent, ind_precedent):
    """Verdictul NORMEI, pe două exerciții consecutive (pct. 9 + pct. 13).

    Întoarce `(categorie, motiv, cod)`. `categorie` e din `CATEGORII`, `cod` din `MOTIVE` — proza e
    pentru om, codul pentru mașină.
    """
    if not ind_precedent:
        return ("nedeterminata",
                "indicatorii exercițiului precedent nu se pot calcula, iar norma cere DOUĂ exerciții "
                "consecutive (pct.13 alin.(2) și (3)); pe un singur an nu se poate încadra",
                "fara_exercitiu_precedent")
    c = _incadrare_an(ind_curent)
    p = _incadrare_an(ind_precedent)
    if c is None or p is None:
        return ("nedeterminata",
                "cel puțin un criteriu nu se poate calcula pe unul dintre cele două exerciții, iar "
                "criteriile cunoscute nu ajung singure la «două din trei»",
                "criterii_incomplete")
    if c == p:
        return (c, "aceeași încadrare în amândouă exercițiile consecutive", "aceeasi_incadrare")
    return (p, "încadrarea NU se schimbă: categoria diferă între cele două exerciții, iar norma cere "
               "ca depășirea să se producă în două exerciții consecutive (pct.13 alin.(2)); rămâne "
               "categoria exercițiului precedent",
            "nu_se_schimba")


def nr_mediu_salariati(cur, schema, an):
    """Media lunară a salariaților cu contract activ, pe cele 12 luni ale exercițiului.

    LIMITA DECLARATĂ, și e importantă: **nu e „numărul mediu" în accepțiunea metodologiei INS**, care
    se calculează pe efectiv zilnic. E o aproximare lunară, din datele pe care aplicația le are.
    De-aia `incadreaza` marchează separat cazurile în care criteriul ăsta **decide** încadrarea —
    când cele două criterii monetare ajung singure la „două din trei", aproximarea nu contează.
    """
    cur.execute(f"""
        SELECT AVG(n)::numeric FROM (
            SELECT generate_series(1, 12) AS luna
        ) l, LATERAL (
            SELECT COUNT(*) AS n FROM {schema}.salariati s
             WHERE (s.data_angajare IS NULL
                    OR s.data_angajare < make_date(%s, l.luna, 1) + INTERVAL '1 month')
               AND (s.data_incetare IS NULL
                    OR s.data_incetare >= make_date(%s, l.luna, 1))
        ) x
    """, (an, an))
    r = cur.fetchone()
    v = r[0] if not isinstance(r, dict) else list(r.values())[0]
    return None if v is None else int(round(float(v)))


def indicatori(conn, schema, an):
    """Cele trei criterii, pentru UN exercițiu. `None` pe an fără date — nu zero."""
    from psycopg2.extras import RealDictCursor
    from core import bilant_api as _ba
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        rl = _ba._rulaje_67(cur, schema, an)
        if not rl:
            return None
        s_fin = _ba._solduri_la(cur, schema, an)
        f10 = _b.f10_din_balanta(s_fin)
        f20 = _b.f20_din_rulaje(rl)
        nms = nr_mediu_salariati(cur, schema, an)
    # pct.15: totalul activelor = lit. A-C din „Active" = imobilizate + circulante + chelt. in avans
    total_active = (f10.get(4) or Decimal("0")) + (f10.get(9) or Decimal("0")) + (f10.get(10) or Decimal("0"))
    return {"an": an,
            "total_active": total_active,
            "cifra_afaceri_neta": f20.get(1) or Decimal("0"),
            "nr_mediu_salariati": nms}


def categorie(conn, schema, an):
    """Încadrarea firmei, ca AFIRMAȚIE — cu domeniu, temei și motiv (DS cap.25.5)."""
    ic = indicatori(conn, schema, an)
    ip = indicatori(conn, schema, an - 1)
    cat, motiv, cod = incadreaza(ic or {}, ip)
    # `decis_de_salariati`: încadrarea ar fi ieșit altfel dacă numărul mediu ar fi fost necunoscut?
    # Contează fiindcă exact ăla e criteriul aproximat (vezi `nr_mediu_salariati`).
    decis_de_salariati = False
    if ic and ip and cat != "nedeterminata":
        fara = dict(ic, nr_mediu_salariati=None), dict(ip, nr_mediu_salariati=None)
        decis_de_salariati = incadreaza(fara[0], fara[1])[0] != cat
    return afirmatie(
        "fapt", tip="categorie_marime",
        motiv=motiv,
        temei_completitudine=("indicatorii se derivă din balanța și rulajele exercițiilor %d și %d, "
                              "prin aceleași funcții din care se produce bilanțul "
                              "(`bilant.f10_din_balanta`, `bilant.f20_din_rulaje`); un exercițiu "
                              "fără rulaje se declară necalculabil, nu zero" % (an, an - 1)),
        an=an, luna=None,
        **{
        "categorie": cat,
        "cod_motiv": cod,
        "temei_praguri": {k: {c: str(temei(k, c)) for c in CRITERII} for k in PRAGURI},
        "temei_doi_ani": str(_TEMEI_DOI_ANI),
        "temei_total_active": str(_TEMEI_TOTAL_ACTIVE),
        "indicatori_curent": _json(ic),
        "indicatori_precedent": _json(ip),
        "praguri": {k: {c: str(prag(k, c)) for c in CRITERII} for k in PRAGURI},
        "decis_de_numarul_de_salariati": decis_de_salariati,
        })


def _json(ind):
    if not ind:
        return None
    return {k: (str(v) if isinstance(v, Decimal) else v) for k, v in ind.items()}
