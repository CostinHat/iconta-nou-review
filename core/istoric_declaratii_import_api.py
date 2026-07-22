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


def rezumat(conn, tenant_id):
    """{are_istoric, randuri} pentru o firma (doar randurile din migrare).
    Coloana `sursa` e garantata de migrare_declaratii_depuse_randuri (public), nu mai lazy."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id=%s AND sursa='migrare'",
                    (tenant_id,))
        n = cur.fetchone()[0]
    return {"are_istoric": n > 0, "randuri": n}


TIPURI_CUNOSCUTE = ("D100", "D101", "D112", "D205", "D300", "D301", "D390", "D394",
                    "D406", "D212", "S1003", "S1005", "D394A", "D311", "D207")


def verifica_randuri(randuri, azi=None):
    """PURA: [{rand, motiv, mesaj}]. Nicio validare pana la 15.07.2026: tip D999
    inexistent, luna 13, data depunerii inaintea perioadei raportate - toate intrau."""
    import datetime as _dt
    azi = azi or _dt.date.today()
    er = []
    for i, r in enumerate(randuri or [], start=2):
        tip = str(r.get("tip") or "").strip().upper()
        an = int(r.get("an") or 0)
        luna = r.get("luna")
        if tip and tip not in TIPURI_CUNOSCUTE:
            er.append({"rand": i, "motiv": "tip",
                       "mesaj": "declaratia %s nu exista in nomenclatorul ANAF" % tip})
        if not (2000 <= an <= azi.year + 1):
            er.append({"rand": i, "motiv": "an", "mesaj": "%s: anul %s e in afara intervalului" % (tip or "?", an)})
        if luna is not None and str(luna).strip() != "":
            try:
                l = int(luna)
                if not (1 <= l <= 12):
                    er.append({"rand": i, "motiv": "luna", "mesaj": "%s: luna %s (asteptat 1-12)" % (tip or "?", l)})
            except (TypeError, ValueError):
                er.append({"rand": i, "motiv": "luna", "mesaj": "%s: luna %r nu e numar" % (tip or "?", luna)})
        d = r.get("data_depunere")
        if d:
            try:
                dd = d if isinstance(d, _dt.date) else _dt.date.fromisoformat(str(d)[:10])
                l = int(luna) if str(luna or "").strip().isdigit() else 12
                sfarsit = _dt.date(an, l, 1) if 2000 <= an <= 2100 and 1 <= l <= 12 else None
                if sfarsit and dd < sfarsit:
                    er.append({"rand": i, "motiv": "data_inainte",
                               "mesaj": "%s %s/%s: depusa la %s, inainte de perioada raportata"
                                        % (tip or "?", luna, an, dd)})
            except ValueError:
                er.append({"rand": i, "motiv": "data", "mesaj": "%s: data depunerii %r nu se intelege" % (tip or "?", d)})
    return er


def importa(conn, tenant_id, randuri):
    """DELETE doar randurile de migrare ale firmei + INSERT. NU atinge sursa='iconta'.
    Ridica ValueError daca randurile nu pot intra (vezi verifica_randuri)."""
    er = verifica_randuri(randuri)
    if er:
        raise ValueError("%d randuri nu pot intra: %s. Istoricul declaratiilor sta la "
                         "baza termenelor si a controlului fiscal."
                         % (len(er), "; ".join("rand %s: %s" % (x["rand"], x["mesaj"]) for x in er[:6])))
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
