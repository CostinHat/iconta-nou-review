"""
core/solduri_api.py — import solduri inițiale (balanță de deschidere) per firmă.

Citește o balanță (.xlsx/.csv) cu coloanele: Cont, Denumire, Sold debitor, Sold creditor.
Soldurile se salvează în schema tenantului (tabel solduri_initiale, auto-creat).
Conturile analitice (4111.ALPHA, 401.GAMMA) se păstrează ca atare — așa intră planul
analitic, derivat direct din balanță.

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations


def _numar(v, strict=False):
    """Transformă o valoare în număr (acceptă '1.234,56', '1,234.56', '(500)', '', None).

    PARANTEZELE = sumă negativă — convenția contabilă din exporturile SAGA/Ciel/Excel
    (format „contabil"). Fără asta, `(500)` cădea pe `float()` și devenea 0.0 TĂCUT:
    soldul dispărea din balanță, iar totalurile păreau corecte. Dovedit de test, nu de
    utilizator (15.07.2026).

    strict=True → ridică ValueError pe text neinterpretabil, în loc să întoarcă 0.
    Un sold care devine 0 în tăcere e mai periculos decât un import refuzat.
    """
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip()
    if not t:
        return 0.0
    t = t.replace(" ", "").replace("\xa0", "")
    # format contabil: (500) = -500
    neg = t.startswith("(") and t.endswith(")")
    if neg:
        t = t[1:-1].strip()
    # sufixe de moneda din exporturi: "1.234,56 RON" / "500 lei"
    for suf in ("RON", "ron", "LEI", "Lei", "lei", "EUR", "eur"):
        if t.endswith(suf):
            t = t[:-len(suf)].strip()
    # dacă are și punct și virgulă, ultimul separator e zecimala
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")   # 1.234,56
        else:
            t = t.replace(",", "")                      # 1,234.56
    elif "," in t:
        # virgulă singură: zecimală dacă are 1-2 cifre după, altfel separator de mii
        parte = t.split(",")[-1]
        t = t.replace(",", ".") if len(parte) <= 2 else t.replace(",", "")
    try:
        x = float(t)
    except ValueError:
        if strict:
            raise ValueError("valoare numerică neinterpretabilă: %r" % (v,))
        return 0.0
    return -x if neg else x


# ── citirea balanței (C21, comanda Costin 14.10.2026, verbatim în DECIZII „Importul din SAGA”) ──────────────────────────
# Fișierul trece prin `core.import_tabel` (sursa unică: format, codare, antet, coloane). Aici rămâne numai ce e propriu
# balanței: CARE pereche debit/credit e soldul final, ce rânduri nu sunt conturi, și sinteticele dublate de analiticele lor.
from core import import_tabel as _it
from core.pdf_util import bani as _bani, data_ro as _data_ro   # DS cap.4: sumele și datele din text, canonic
import re as _re

CAMPURI = {
    "cont": ("simbol cont", "cont contabil", "nr cont", "=cont", "=simbol", "simbol*"),
    "denumire": ("denumire cont", "denumirea contului", "titlu cont", "denumire*", "explicatie", "nume"),
    "debit": ("debit*", "d"),
    "credit": ("credit*", "c"),
}

# un cont: 3–6 cifre, opțional un analitic după punct / cratimă / bară („401.00001” SAGA, „4111.ALPHA”, „5121-1”)
_CONT = _re.compile(r"^\d{3,6}(?:[.\-/][0-9A-Za-z][0-9A-Za-z.\-/_]*)?$")


def _e_stramos(a, b):
    """`a` e sinteticul lui `b` (b ≠ a): „411” -> „4111”, „4111” -> „4111.0001”, „401” -> „401.00001”."""
    if a == b:
        return False
    if b.startswith(a + "."):
        return True
    ra, rb = a.split(".")[0], b.split(".")[0]
    return "." not in a and ra.isdigit() and rb != ra and rb.startswith(ra)


def extrage_balanta_detaliat(continut, nume_fisier=""):
    """`{randuri, coloane, ignorate, sintetice_inlocuite, fara_sold}` din balanța din fișier.

    - `randuri` = [{cont, denumire, debit, credit}] — soldurile FINALE, numai frunzele (analiticele, nu și sinteticul lor);
    - `coloane` = antetul coloanelor citite (ecranul le arată: „s-au citit «Sold final debitor» / «Sold final creditor»”);
    - `ignorate` = rândurile care nu sunt conturi (totaluri, titluri de clasă) — numărate și arătate, nu importate;
    - `sintetice_inlocuite` = sinteticele scoase fiindcă fișierul are analiticele lor (cu același sold net);
    - `fara_sold` = conturi cu sold final 0 / 0 (au avut numai rulaje) — nu intră, nu schimbă nimic."""
    brut = _it.citeste(continut, nume_fisier)
    if not brut or all(_it.rand_gol(r) for r in brut):
        return {"randuri": [], "coloane": {}, "ignorate": [], "sintetice_inlocuite": [], "fara_sold": 0}
    antet, start = _it.gaseste_antet(brut, CAMPURI, obligatorii=("cont",), nume_fisier=nume_fisier)
    i_cont = _it.coloana(antet, CAMPURI["cont"], camp="cont")
    i_den = _it.coloana(antet, CAMPURI["denumire"], exclus=(i_cont,), camp="denumire")
    i_deb, i_cre = _it.pereche_sold_final(antet, nume_fisier)

    citite, ignorate, fara_sold = [], [], 0
    for nr, r in enumerate(brut[start:], start=start + 1):
        if _it.rand_gol(r):
            continue
        cont = _it.celula(r, i_cont)
        if not _CONT.match(cont):
            eticheta = cont or _it.celula(r, i_den) or "(rând fără cont)"
            ignorate.append(eticheta)
            continue
        try:
            deb = _numar(_it.valoare(r, i_deb), strict=True) if i_deb >= 0 else 0.0
            cre = _numar(_it.valoare(r, i_cre), strict=True) if i_cre >= 0 else 0.0
        except ValueError:
            raise _it.FisierNecitit("Rândul %d (contul %s): soldul final „%s” / „%s” nu e un număr. Corectează celula și "
                                    "încarcă fișierul din nou." % (nr, cont, _it.celula(r, i_deb), _it.celula(r, i_cre)))
        citite.append({"cont": cont, "denumire": _it.celula(r, i_den), "debit": deb, "credit": cre})

    # același cont de două ori: baza are UNIQUE(cont) (GARZI cat.1) — refuz numit, nu o eroare de bază la scriere
    vazute, dubluri = set(), []
    for x in citite:
        if x["cont"] in vazute and x["cont"] not in dubluri:
            dubluri.append(x["cont"])
        vazute.add(x["cont"])
    if dubluri:
        raise _it.FisierNecitit("Contul %s apare de mai multe ori în balanță. Fiecare cont are un singur rând de sold; corectează "
                                "fișierul și încarcă-l din nou." % ", ".join(dubluri[:8]))
    # sinteticele dublate de analiticele lor: păstrez frunzele, dacă netul sinteticului = suma netului frunzelor lui
    conturi = [x["cont"] for x in citite]
    net = {}
    for x in citite:
        net[x["cont"]] = net.get(x["cont"], 0.0) + x["debit"] - x["credit"]
    frunze = [c for c in conturi if not any(_e_stramos(c, d) for d in conturi)]
    inlocuite = []
    for c in sorted(set(conturi) - set(frunze)):
        fiice = [f for f in set(frunze) if _e_stramos(c, f)]
        suma = round(sum(net[f] for f in fiice), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
        if abs(round(net[c], 2) - suma) >= 0.01:  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            raise _it.FisierNecitit(
                "Contul %s are în fișier sold final net %s, iar analiticele lui (%s) însumează %s. Balanța amestecă "
                "sintetice și analitice care nu se potrivesc — exportă balanța numai cu analitice (sau numai sintetică) și "
                "încarcă-o din nou." % (c, _bani(net[c], "lei"), ", ".join(sorted(fiice)[:5]), _bani(suma, "lei")))
        inlocuite.append(c)
    out = []
    for x in citite:
        if x["cont"] in inlocuite:
            continue
        if round(x["debit"], 2) == 0 and round(x["credit"], 2) == 0:  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            fara_sold += 1
            continue
        out.append(x)
    return {"randuri": out,
            "coloane": {"cont": _it.eticheta(antet, i_cont), "debit": _it.eticheta(antet, i_deb),
                        "credit": _it.eticheta(antet, i_cre)},
            "ignorate": ignorate, "sintetice_inlocuite": inlocuite, "fara_sold": fara_sold}


def extrage_balanta(continut, nume_fisier=""):
    """Întoarce [{cont, denumire, debit, credit}] — soldurile finale din balanță (vezi `extrage_balanta_detaliat`)."""
    return extrage_balanta_detaliat(continut, nume_fisier)["randuri"]


def asigura_tabel(conn):
    """Creează tabelul solduri_initiale în schema curentă (search_path = tenantul)."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS solduri_initiale (
                id SERIAL PRIMARY KEY,
                cont TEXT NOT NULL,
                denumire TEXT NOT NULL DEFAULT '',
                sold_debitor NUMERIC(15,2) NOT NULL DEFAULT 0,
                sold_creditor NUMERIC(15,2) NOT NULL DEFAULT 0,
                data_referinta DATE
            )
        """)


def verifica_echilibru(randuri):
    """PURA: (ok, debit, credit, diferenta). O balanta de deschidere trebuie sa aiba
    totalul debitor egal cu cel creditor - altfel toata contabilitatea firmei porneste
    gresit."""
    td = round(sum(_numar(r.get("debit")) for r in (randuri or [])), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    tc = round(sum(_numar(r.get("credit")) for r in (randuri or [])), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    dif = round(td - tc, 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    return abs(dif) < 0.01, td, tc, dif


def balanta_valida(randuri):
    """PURA: (ok, motiv). O balanta reala are solduri (totaluri != 0) si conturi contabile.
    Un fisier strain (ex. istoric_declaratii.csv incarcat din greseala) e citit cu coloanele
    debit/credit NEGASITE -> toate 0 -> verifica_echilibru zice "echilibrat" (0==0). Fara
    aceasta poarta, o balanta GOALA se salva cu bulina verde si contabilul credea ca e in
    regula (constatare de ecran 09.08.2026). Paralela cu importul de parteneri, care compara
    cu balanta si arata diferenta; solduri n-avea nicio verificare de continut."""
    randuri = randuri or []
    if not randuri:
        return False, "Fișier gol: niciun rând de citit."
    td = round(sum(_numar(r.get("debit")) for r in randuri), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    tc = round(sum(_numar(r.get("credit")) for r in randuri), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    conturi_cont = sum(1 for r in randuri if str(r.get("cont") or "").strip()[:1].isdigit())
    if conturi_cont == 0:
        return False, ("Fișier nerecunoscut ca balanță: nicio valoare din coloana Cont nu arată "
                       "a cont contabil (un cont începe cu cifră; „D394” nu e cont). "
                       "Verifică dacă ai încărcat balanța de deschidere.")
    if td == 0 and tc == 0:
        return False, ("Balanță fără solduri: total debitor și total creditor sunt amândouă 0 "
                       "(coloanele Sold debitor/creditor lipsesc sau toate valorile sunt 0). "
                       "„Echilibrat” pe 0 = 0 nu înseamnă o balanță validă.")
    return True, ""


def _adauga_conturi_lipsa(conn, randuri):
    """Conturile din balanta care nu sunt in planul firmei intra in el.

    Ecranul promite: "conturile analitice (clienti, furnizori) intra automat in plan",
    iar docstringul modulului la fel - dar importa() nu atingea deloc plan_conturi
    (dovedit 15.07.2026: grep plan_conturi in solduri_api = 0). Planul avea doar cele
    185 de conturi standard OMFP; o balanta cu analitice reale (4111.01 DEDEMAN,
    401.05 ORANGE - cum au toate cabinetele) lasa soldurile pe conturi inexistente
    in nomenclator.
    Tipul ramane 'Bifunctional' (implicitul tabelei): natura contului se deduce din
    simbol, nu o inventam aici. ON CONFLICT DO NOTHING - nu suprascriem denumirile
    din planul oficial cu cele din balanta.
    """
    conturi = []
    for r in (randuri or []):
        c = str(r.get("cont") or "").strip()
        if c:
            conturi.append((c, (str(r.get("denumire") or "").strip() or c)))
    if not conturi:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO plan_conturi (simbol, denumire) VALUES (%s, %s) "
            "ON CONFLICT (simbol) DO NOTHING", conturi)
        return cur.rowcount


def data_balantei(v, azi=None):
    """[C22, comanda Costin 14.10.2026] Data la care sunt soldurile din balanță — CERUTĂ, nu dedusă. Din ea se propun data
    soldurilor inițiale și luna preluării (`luna_preluare`, `bilant_api.data_soldurilor`); fără ea, aplicația le deducea din
    data adăugării firmei sau din prima notă. `'YYYY-MM-DD'`; lipsă, neinterpretabilă sau în viitor -> `ValueError`."""
    import datetime as _dt
    t = str(v or "").strip()
    if not t:
        raise ValueError("Data balanței lipsește: scrie data la care sunt soldurile din fișier (de obicei ultima zi a lunii "
                         "dinaintea preluării). Din ea se stabilește luna de la care lucrezi în iConta.")
    try:
        d = _dt.date.fromisoformat(t[:10])
    except ValueError:
        raise ValueError("Data balanței „%s” nu se înțelege; se așteaptă o dată calendaristică." % t)
    if d > (azi or _dt.date.today()):
        raise ValueError("Data balanței (%s) e în viitor: soldurile se preiau la o dată încheiată." % _data_ro(d))
    return d.isoformat()


def importa(conn, randuri, data_referinta=None):
    """Înlocuiește soldurile (DELETE + INSERT). Întoarce {randuri, total_debit, total_credit}.
    Ridica ValueError daca balanta nu se echilibreaza.

    REFUZ dovedit necesar 15.07.2026, prin migrare reala: ecranul afisa "neechilibrat"
    rosu, dar importa() scria oricum, iar migrarea marca stratul "gata" verde. Firma
    ramanea cu o balanta de deschidere imposibila si contabilul credea ca e in regula.
    Semnalarea fara oprire e mai rea decat tacerea: da impresia ca produsul a verificat.
    """
    # REFUZUL E PRIMA POARTA: nimic nu se scrie dintr-o balanta respinsa. Pusesem
    # _adauga_conturi_lipsa inaintea verificarii - conturile intrau in plan chiar si
    # cand importul era refuzat. Prins de test (15.07.2026), nu de mine.
    vok, vmotiv = balanta_valida(randuri)
    if not vok:
        raise ValueError(vmotiv)
    ok, td_v, tc_v, dif = verifica_echilibru(randuri)
    if not ok:
        raise ValueError(
            "Balanța nu se echilibrează: debit %s, credit %s "
            "(diferență %s). O balanță de deschidere trebuie să aibă totalul "
            "debitor egal cu cel creditor — altfel toată contabilitatea firmei "
            "pornește greșit." % (_bani(td_v, "lei"), _bani(tc_v, "lei"), _bani(dif, "lei")))
    data_referinta = data_balantei(data_referinta)       # [C22] cerută, după validitate și echilibru
    asigura_tabel(conn)
    _adauga_conturi_lipsa(conn, randuri)
    td = tc = 0.0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM solduri_initiale")
        for r in randuri:
            cur.execute(
                "INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) "
                "VALUES (%s,%s,%s,%s,%s)",
                (r["cont"], r.get("denumire", ""), r.get("debit", 0), r.get("credit", 0), data_referinta))
            td += float(r.get("debit", 0) or 0)
            tc += float(r.get("credit", 0) or 0)
    return {"randuri": len(randuri), "total_debit": round(td, 2), "total_credit": round(tc, 2)}  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5


def rezumat(conn):
    """{are_solduri, randuri, total_debit, total_credit} pentru firma curentă."""
    asigura_tabel(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), COALESCE(sum(sold_debitor),0), COALESCE(sum(sold_creditor),0) FROM solduri_initiale")
        n, td, tc = cur.fetchone()
    return {"are_solduri": n > 0, "randuri": n, "total_debit": float(td), "total_credit": float(tc)}
