"""
core/solduri_parteneri_api.py — import solduri parteneri (defalcare 4111/401 per client/furnizor).

Citeste un fisier (.xlsx/.csv) cu coloanele: Cont, CUI, Denumire, Sold debitor, Sold creditor.
Un rand = un partener pe un cont. Se salveaza in schema tenantului (tabel solduri_parteneri).

Coerenta cu stratul 2 (solduri_initiale): suma soldurilor partenerilor pe contul sintetic
(4111, 401) se compara cu soldul sintetic din balanta (analiticele 4111.X grupate pe radacina).
Informativ, NU blocant — contabilul decide.
"""
from __future__ import annotations


def _numar(v):
    """Transforma o valoare in numar (accepta '1.234,56', '1,234.56', '', None)."""
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip()
    if not t:
        return 0.0
    t = t.replace(" ", "")
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif "," in t:
        parte = t.split(",")[-1]
        t = t.replace(",", ".") if len(parte) <= 2 else t.replace(",", "")
    try:
        return float(t)
    except ValueError:
        return 0.0


def _gaseste_col(antet, *chei, exclus=None):
    """Indexul primei coloane al carei antet contine una din chei. -1 daca lipseste.
    `exclus` = indecsi deja atribuiti altui camp; nu pot fi si acesta.

    Fara `exclus`, un antet "CUI partener" se potriveste si la "cui", si la "partener":
    prima potrivire castiga, iar denumirea ajunge sa fie CUI-ul. Dovedit 15.07.2026
    prin migrare reala - cabinetele isi numesc chiar asa coloanele.
    """
    lua = set(x for x in (exclus or []) if x is not None) if not isinstance(exclus, int) else {exclus}
    for i, h in enumerate(antet):
        if i in lua:
            continue
        hl = str(h).strip().lower()
        for k in chei:
            if k in hl:
                return i
    return -1


def _radacina(cont):
    """Sinteticul de baza al unui cont: '4111.ALPHA' -> '4111', '401' -> '401'."""
    return str(cont).split(".")[0].strip()


def _curata_cui(v):
    """Normalizeaza CUI: RO14837428 -> 14837428, scoate spatii."""
    t = str(v or "").strip().upper().replace(" ", "")
    if t.startswith("RO"):
        t = t[2:]
    return t


def extrage(continut, nume_fisier=""):
    """
    Intoarce [{cont, cui, denumire, debit, credit}] din fisierul de parteneri.
    Detecteaza coloanele dupa antet (cont / cui / denumire / debit / credit).
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
    i_cui = _gaseste_col(antet, "cui", "cif", "cod fiscal")
    # denumirea se cauta DUPA cont si cui, sarind peste coloanele lor
    i_den = _gaseste_col(antet, "denumire", "nume", "partener", exclus=[i_cont, i_cui])
    i_deb = _gaseste_col(antet, "debitor", "debit")
    i_cre = _gaseste_col(antet, "creditor", "credit")
    if i_cont < 0:
        i_cont = 0

    out = []
    for r in randuri[1:]:
        if i_cont >= len(r):
            continue
        cont = str(r[i_cont]).strip()
        if not cont:
            continue
        cui = _curata_cui(r[i_cui]) if (0 <= i_cui < len(r)) else ""
        den = str(r[i_den]).strip() if (0 <= i_den < len(r)) else ""
        deb = _numar(r[i_deb]) if (0 <= i_deb < len(r)) else 0.0
        cre = _numar(r[i_cre]) if (0 <= i_cre < len(r)) else 0.0
        out.append({"cont": cont, "cui": cui, "denumire": den, "debit": deb, "credit": cre})
    return out


def asigura_tabel(conn):
    """Creeaza tabelul solduri_parteneri in schema curenta (search_path = tenantul)."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS solduri_parteneri (
                id SERIAL PRIMARY KEY,
                cont TEXT NOT NULL,
                cui TEXT NOT NULL DEFAULT '',
                denumire TEXT NOT NULL DEFAULT '',
                sold_debitor NUMERIC(15,2) NOT NULL DEFAULT 0,
                sold_creditor NUMERIC(15,2) NOT NULL DEFAULT 0,
                data_referinta DATE
            )
        """)
    conn.commit()


def coerenta(conn, randuri):
    """
    Compara soldurile partenerilor pe sintetic (radacina) cu soldurile din solduri_initiale.
    Intoarce [{cont, suma_parteneri, sold_balanta, diferenta, coincide}] per sintetic.
    Daca solduri_initiale nu exista inca, sold_balanta = None (nu putem verifica).
    """
    # suma partenerilor pe radacina sintetica, sold net (debit - credit)
    pe_sintetic = {}
    for r in randuri:
        rad = _radacina(r["cont"])
        net = float(r.get("debit", 0) or 0) - float(r.get("credit", 0) or 0)
        pe_sintetic[rad] = pe_sintetic.get(rad, 0.0) + net

    # soldurile din balanta, grupate pe radacina
    bal = {}
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('solduri_initiale')")
        exista = cur.fetchone()[0] is not None
        if exista:
            cur.execute("SELECT cont, sold_debitor, sold_creditor FROM solduri_initiale")
            for cont, sd, sc in cur.fetchall():
                rad = _radacina(cont)
                bal[rad] = bal.get(rad, 0.0) + (float(sd) - float(sc))

    out = []
    for rad in sorted(pe_sintetic.keys()):
        sp = round(pe_sintetic[rad], 2)
        if exista and rad in bal:
            sb = round(bal[rad], 2)
            dif = round(sp - sb, 2)
            out.append({"cont": rad, "suma_parteneri": sp, "sold_balanta": sb,
                        "diferenta": dif, "coincide": abs(dif) < 0.01})
        else:
            out.append({"cont": rad, "suma_parteneri": sp, "sold_balanta": None,
                        "diferenta": None, "coincide": None})
    return out


def importa(conn, randuri, data_referinta=None):
    """Inlocuieste partenerii (DELETE + INSERT). Intoarce {randuri, total_debit, total_credit}."""
    asigura_tabel(conn)
    td = tc = 0.0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM solduri_parteneri")
        for r in randuri:
            cur.execute(
                "INSERT INTO solduri_parteneri (cont, cui, denumire, sold_debitor, sold_creditor, data_referinta) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (r["cont"], r.get("cui", ""), r.get("denumire", ""),
                 r.get("debit", 0), r.get("credit", 0), data_referinta))
            td += float(r.get("debit", 0) or 0)
            tc += float(r.get("credit", 0) or 0)
    conn.commit()
    return {"randuri": len(randuri), "total_debit": round(td, 2), "total_credit": round(tc, 2)}


def rezumat(conn):
    """{are_parteneri, randuri, total_debit, total_credit} pentru firma curenta."""
    asigura_tabel(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), COALESCE(sum(sold_debitor),0), COALESCE(sum(sold_creditor),0) FROM solduri_parteneri")
        n, td, tc = cur.fetchone()
    return {"are_parteneri": n > 0, "randuri": n, "total_debit": float(td), "total_credit": float(tc)}
