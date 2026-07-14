# banca_parser.py - Parser extras bancar XLS/XLSX/CSV (ING/Jasper).
# Logica validata pe ING real: grid Data/Detalii/Debit/Credit,
# semn dupa pozitia coloanei, randuri multi-linie grupate, format dupa magic bytes.
import re
from io import BytesIO

def _e_data(v):
    return bool(re.match(r"^\d{1,2}[./-]\d{1,2}[./-]\d{2,4}", str(v or "").strip()))

def _numar(v):
    s = str(v or "").strip().replace(" ", "")
    if not s:
        return None
    # ultimul separator (. sau ,) = zecimal; celelalte = mii
    up, uv = s.rfind("."), s.rfind(",")
    if up > uv:
        s = s.replace(",", "")
    elif uv > up:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def _parse_grid(randuri):
    """randuri = lista de liste (celule). Detecteaza antet si extrage tranzactii."""
    antet_idx, col = None, {}
    for i, r in enumerate(randuri[:30]):
        jos = [str(c or "").lower() for c in r]
        if any("data" in c for c in jos) and any("debit" in c for c in jos):
            antet_idx = i
            for j, c in enumerate(jos):
                if "data" in c and "data" not in col: col["data"] = j
                if "detali" in c or "descriere" in c: col["detalii"] = j
                if "debit" in c: col["debit"] = j
                if "credit" in c: col["credit"] = j
            break
    if antet_idx is None:
        return []
    tranzactii, curenta = [], None
    for r in randuri[antet_idx + 1:]:
        celule = [str(c or "").strip() for c in r]
        if not any(celule):
            continue
        data_v = celule[col["data"]] if col.get("data") is not None and col["data"] < len(celule) else ""
        if _e_data(data_v):
            if curenta: tranzactii.append(curenta)
            deb = _numar(r[col["debit"]]) if col.get("debit") is not None and col["debit"] < len(r) else None
            cre = _numar(r[col["credit"]]) if col.get("credit") is not None and col["credit"] < len(r) else None
            suma = -(deb or 0) if deb else (cre or 0)
            det = celule[col["detalii"]] if col.get("detalii") is not None and col["detalii"] < len(celule) else ""
            curenta = {"data": data_v[:10], "detalii": det, "suma": round(suma, 2)}
        elif curenta:
            extra = " ".join(c for c in celule if c)
            if extra: curenta["detalii"] = (curenta["detalii"] + " " + extra).strip()
    if curenta: tranzactii.append(curenta)
    return tranzactii

def _parse_mt940(text):
    """Parser MT940 (SWIFT, format bancar standard).
    :61: linie tranzactie (data, semn C/D, suma). :86: detalii asociate.
    Intoarce aceeasi structura ca _parse_grid: {data, detalii, suma}.
    Sursa: specificatia SWIFT MT940 (Statement Message).
    """
    tranzactii, curenta = [], None
    for linie_raw in text.splitlines():
        linie = linie_raw.strip()
        if linie.startswith(":61:"):
            if curenta:
                tranzactii.append(curenta)
            corp = linie[4:]
            # format :61: YYMMDD[MMDD]{C|D|RC|RD}suma...
            m = re.match(r"(\d{6})(\d{4})?(R?[CD])([\d,]+)", corp)
            if not m:
                curenta = None
                continue
            yymmdd, _mmdd, semn, suma_s = m.groups()
            an = 2000 + int(yymmdd[:2])
            data = f"{yymmdd[4:6]}.{yymmdd[2:4]}.{an}"
            suma = float(suma_s.replace(",", "."))
            if semn in ("D", "RC"):  # D=debit(plata), RC=storno credit
                suma = -suma
            curenta = {"data": data, "detalii": "", "suma": round(suma, 2)}
        elif linie.startswith(":86:") and curenta is not None:
            curenta["detalii"] = linie[4:].strip()
        elif curenta is not None and not linie.startswith(":") and linie:
            # continuare detalii pe linia urmatoare
            curenta["detalii"] = (curenta["detalii"] + " " + linie).strip()
    if curenta:
        tranzactii.append(curenta)
    return tranzactii


def parse_extras(continut, nume_fisier=""):
    """Detecteaza formatul dupa magic bytes si intoarce lista de tranzactii."""
    if continut[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":  # OLE2 = .xls
        import xlrd
        wb = xlrd.open_workbook(file_contents=continut)
        sh = wb.sheet_by_index(0)
        randuri = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
    elif continut[:2] == b"PK":  # zip = .xlsx
        from openpyxl import load_workbook
        wb = load_workbook(BytesIO(continut), read_only=True)
        sh = wb.active
        randuri = [[c for c in rand] for rand in sh.iter_rows(values_only=True)]
    else:  # text: MT940 sau csv
        text = continut.decode("utf-8", errors="replace") if isinstance(continut, bytes) else continut
        if ":61:" in text or ":20:" in text:  # marker MT940
            return _parse_mt940(text)
        import csv
        dialect = csv.Sniffer().sniff(text[:2000]) if text.strip() else None
        randuri = list(csv.reader(text.splitlines(), dialect)) if dialect else []
    return _parse_grid(randuri)
