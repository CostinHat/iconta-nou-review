"""
core/solduri_api.py — import solduri inițiale (balanță de deschidere) per firmă.

Citește o balanță (.xlsx/.csv) cu coloanele: Cont, Denumire, Sold debitor, Sold creditor.
Soldurile se salvează în schema tenantului (tabel solduri_initiale, auto-creat).
Conturile analitice (4111.ALPHA, 401.GAMMA) se păstrează ca atare — așa intră planul
analitic, derivat direct din balanță.
"""
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


def _gaseste_col(antet, *chei):
    """Indexul primei coloane al cărei antet conține una din chei. -1 dacă lipsește."""
    for i, h in enumerate(antet):
        hl = str(h).strip().lower()
        for k in chei:
            if k in hl:
                return i
    return -1


def extrage_balanta(continut, nume_fisier=""):
    """
    Întoarce [{cont, denumire, debit, credit}] din balanță.
    Detectează coloanele după antet (cont / denumire / debit / credit).
    """
    nume = (nume_fisier or "").lower()
    randuri = []

    if nume.endswith(".csv") or nume.endswith(".tsv") or nume.endswith(".txt"):
        import csv, io
        text = continut.decode("utf-8-sig", errors="replace") if isinstance(continut, bytes) else str(continut)
        prima = text.splitlines()[0] if text.splitlines() else ""
        delim = "\t" if nume.endswith(".tsv") else (";" if prima.count(";") > prima.count(",") else ",")
        randuri = list(csv.reader(io.StringIO(text), delimiter=delim))
    elif nume.endswith(".xlsx") or nume.endswith(".xlsm"):
        import io
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(continut), read_only=True, data_only=True)
        ws = wb.active
        for r in ws.iter_rows(values_only=True):
            randuri.append(["" if c is None else c for c in r])
        wb.close()
    else:
        raise ValueError("format neacceptat (doar .csv sau .xlsx)")

    if not randuri:
        return []

    antet = [str(x) for x in randuri[0]]
    i_cont = _gaseste_col(antet, "cont", "simbol")
    i_den = _gaseste_col(antet, "denumire", "nume")
    i_deb = _gaseste_col(antet, "debitor", "debit")
    i_cre = _gaseste_col(antet, "creditor", "credit")
    if i_deb < 0 and i_cre < 0:
        raise ValueError("nu găsesc coloane debit/credit - fișier nerecunoscut")
    if i_cont < 0:
        i_cont = 0   # fallback: prima coloană e contul

    out = []
    for r in randuri[1:]:
        if i_cont >= len(r):
            continue
        cont = str(r[i_cont]).strip()
        if not cont:
            continue
        den = str(r[i_den]).strip() if (0 <= i_den < len(r)) else ""
        deb = _numar(r[i_deb]) if (0 <= i_deb < len(r)) else 0.0
        cre = _numar(r[i_cre]) if (0 <= i_cre < len(r)) else 0.0
        out.append({"cont": cont, "denumire": den, "debit": deb, "credit": cre})
    return out


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
    conn.commit()


def verifica_echilibru(randuri):
    """PURA: (ok, debit, credit, diferenta). O balanta de deschidere trebuie sa aiba
    totalul debitor egal cu cel creditor - altfel toata contabilitatea firmei porneste
    gresit."""
    td = round(sum(_numar(r.get("debit")) for r in (randuri or [])), 2)
    tc = round(sum(_numar(r.get("credit")) for r in (randuri or [])), 2)
    dif = round(td - tc, 2)
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
    td = round(sum(_numar(r.get("debit")) for r in randuri), 2)
    tc = round(sum(_numar(r.get("credit")) for r in randuri), 2)
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
            "Balanța nu se echilibrează: debit %.2f lei, credit %.2f lei "
            "(diferență %.2f lei). O balanță de deschidere trebuie să aibă totalul "
            "debitor egal cu cel creditor — altfel toată contabilitatea firmei "
            "pornește greșit." % (td_v, tc_v, dif))
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
    conn.commit()
    return {"randuri": len(randuri), "total_debit": round(td, 2), "total_credit": round(tc, 2)}


def rezumat(conn):
    """{are_solduri, randuri, total_debit, total_credit} pentru firma curentă."""
    asigura_tabel(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), COALESCE(sum(sold_debitor),0), COALESCE(sum(sold_creditor),0) FROM solduri_initiale")
        n, td, tc = cur.fetchone()
    return {"are_solduri": n > 0, "randuri": n, "total_debit": float(td), "total_credit": float(tc)}
