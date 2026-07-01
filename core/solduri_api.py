"""
core/solduri_api.py — import solduri inițiale (balanță de deschidere) per firmă.

Citește o balanță (.xlsx/.csv) cu coloanele: Cont, Denumire, Sold debitor, Sold creditor.
Soldurile se salvează în schema tenantului (tabel solduri_initiale, auto-creat).
Conturile analitice (4111.ALPHA, 401.GAMMA) se păstrează ca atare — așa intră planul
analitic, derivat direct din balanță.
"""
from __future__ import annotations


def _numar(v):
    """Transformă o valoare în număr (acceptă '1.234,56', '1,234.56', '', None)."""
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip()
    if not t:
        return 0.0
    t = t.replace(" ", "")
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
        return float(t)
    except ValueError:
        return 0.0


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


def importa(conn, randuri, data_referinta=None):
    """Înlocuiește soldurile (DELETE + INSERT). Întoarce {randuri, total_debit, total_credit}."""
    asigura_tabel(conn)
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
