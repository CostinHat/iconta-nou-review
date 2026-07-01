"""
core/istoric_declaratii_import_api.py — import istoric declaratii (stratul 7) per firma.

Citeste o lista de declaratii deja depuse (.xlsx/.csv): tip, an, luna, data depunere.
Scrie in tabelul global public.declaratii_depuse cu sursa='migrare' (ca sa nu apara fals
restanta). Import per firma: DELETE WHERE tenant_id=X AND sursa='migrare', apoi INSERT.
NU sterge declaratiile depuse prin iConta (sursa='iconta').
"""
from __future__ import annotations
import datetime

# tipuri cunoscute (pentru normalizare + recunoastere)
_TIPURI = ["D100", "D101", "D112", "D205", "D300", "D301", "D390", "D394", "D406"]


def _gaseste_col(antet, *chei):
    for i, h in enumerate(antet):
        hl = str(h).strip().lower()
        for k in chei:
            if k in hl:
                return i
    return -1


def _intreg(v):
    try:
        return int(round(float(str(v).strip().replace(",", ".")))) if str(v).strip() else 0
    except ValueError:
        return 0


def _normalizeaza_tip(v):
    """'100' / 'd100' / 'Declaratia 100' -> 'D100'. Necunoscut -> uppercase trim."""
    t = str(v or "").strip().upper().replace(" ", "")
    # extrage cifrele
    cifre = "".join(ch for ch in t if ch.isdigit())
    if cifre:
        cand = "D" + cifre
        if cand in _TIPURI:
            return cand, True
    if t in _TIPURI:
        return t, True
    # poate are deja Dxxx
    for tip in _TIPURI:
        if tip in t:
            return tip, True
    return (t or "?"), False   # necunoscut


def _data(v):
    if v is None or str(v).strip() == "":
        return None
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    t = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(t, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def extrage(continut, nume_fisier=""):
    """Intoarce [{tip, an, luna, data_depunere, tip_cunoscut, ok, avertisment}]."""
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
    i_tip = _gaseste_col(antet, "tip", "declaratie", "declarație", "formular")
    i_an = _gaseste_col(antet, "an")
    i_luna = _gaseste_col(antet, "luna", "lună", "perioada", "perioadă")
    i_data = _gaseste_col(antet, "depunere", "depus", "data")

    out = []
    for r in randuri[1:]:
        def cel(i):
            return str(r[i]).strip() if (0 <= i < len(r)) else ""
        tip_raw = cel(i_tip)
        if not tip_raw:
            continue
        tip, cunoscut = _normalizeaza_tip(tip_raw)
        an = _intreg(cel(i_an))
        luna = _intreg(cel(i_luna))
        data_dep = _data(r[i_data]) if (0 <= i_data < len(r)) else None

        avert = []
        if not cunoscut:
            avert.append("tip necunoscut")
        if not (2018 <= an <= 2027):
            avert.append("an neplauzibil")
        if not (1 <= luna <= 12):
            avert.append("lună invalidă")

        out.append({"tip": tip, "an": an, "luna": luna, "data_depunere": data_dep,
                    "tip_cunoscut": cunoscut, "avertisment": avert, "ok": len(avert) == 0})
    return out


def asigura_coloana_sursa(conn):
    """Adauga coloana sursa daca lipseste (default 'iconta')."""
    with conn.cursor() as cur:
        cur.execute("""
            DO $$ BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='public' AND table_name='declaratii_depuse' AND column_name='sursa'
              ) THEN
                ALTER TABLE public.declaratii_depuse ADD COLUMN sursa TEXT NOT NULL DEFAULT 'iconta';
              END IF;
            END $$;
        """)
    conn.commit()


def rezumat(conn, tenant_id):
    """{are_istoric, randuri} pentru o firma (doar randurile din migrare)."""
    asigura_coloana_sursa(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id=%s AND sursa='migrare'",
                    (tenant_id,))
        n = cur.fetchone()[0]
    return {"are_istoric": n > 0, "randuri": n}


def importa(conn, tenant_id, randuri):
    """DELETE doar randurile de migrare ale firmei + INSERT. NU atinge sursa='iconta'."""
    asigura_coloana_sursa(conn)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id=%s AND sursa='migrare'",
                    (tenant_id,))
        n = 0
        for r in randuri:
            cur.execute("""
                INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, data_depunere, sursa)
                VALUES (%s,%s,%s,%s,%s,'migrare')
            """, (tenant_id, r.get("an"), r.get("luna"), r["tip"],
                  r.get("data_depunere")))
            n += 1
    conn.commit()
    return {"importati": n}
