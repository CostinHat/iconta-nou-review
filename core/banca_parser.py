# banca_parser.py - Parser extras bancar XLS/XLSX/CSV (ING/Jasper).
# Logica validata pe ING real: grid Data/Detalii/Debit/Credit,
# semn dupa pozitia coloanei, randuri multi-linie grupate, format dupa magic bytes.
import re
from io import BytesIO

# [format_msg_v1] mesaj unic despre formatul asteptat, ridicat cand nu ies tranzactii.
FORMAT_ASTEPTAT = (
    "Format asteptat: coloane Data, Detalii, si fie Debit+Credit fie o coloana Suma "
    "(cu semn). Separator , sau ; . Zecimale cu . sau ,"
)


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


def _detecteaza_delimitator(text):
    """[delim_robust_v1] Inlocuieste csv.Sniffer (care crapa cand ',' e si
    delimitator si zecimala, ex export RO '01.08.2026,Plata,100,50').
    Numara ; vs , vs TAB pe primele ~10 linii ne-goale; daca zecimalele par
    cu virgula prefera ';'; fallback ';' apoi ','."""
    linii = [l for l in text.splitlines() if l.strip()][:10]
    if not linii:
        return ","
    pv = sum(l.count(";") for l in linii)
    tb = sum(l.count("\t") for l in linii)
    vg = sum(l.count(",") for l in linii)
    # daca ';' apare, e delimitatorul (zecimalele RO folosesc virgula in acest caz)
    if pv > 0:
        return ";"
    if tb > 0 and tb >= vg:
        return "\t"
    if vg > 0:
        return ","
    return ";"


def _extrage_suma(r, celule, col, n_expected):
    """Suma dintr-o coloana unica 'Suma' (cu semn) sau din Debit/Credit separate.
    Cand ',' e delimitator SI zecimala, coloana Suma se sparge in mai multe celule
    decat coloane -> se reunesc surplusul (overflow rejoin)."""
    if col.get("suma") is not None:
        idx = col["suma"]
        if len(celule) > n_expected and idx == n_expected - 1:
            brut = ",".join(celule[idx:])
        else:
            brut = celule[idx] if idx < len(celule) else ""
        return _numar(brut) or 0
    deb = _numar(r[col["debit"]]) if col.get("debit") is not None and col["debit"] < len(r) else None
    cre = _numar(r[col["credit"]]) if col.get("credit") is not None and col["credit"] < len(r) else None
    return -(deb or 0) if deb else (cre or 0)


def _parse_grid(randuri):
    """randuri = lista de liste (celule). Detecteaza antet si extrage tranzactii.
    Antet acceptat: 'data' + (debit/credit SAU suma/valoare/amount).
    Sinonime detalii: detalii/descriere/explicatie."""
    antet_idx, col = None, {}
    for i, r in enumerate(randuri[:30]):
        jos = [str(c or "").lower() for c in r]
        are_data = any("data" in c for c in jos)
        are_debit = any("debit" in c for c in jos)
        are_suma = any(("suma" in c or "valoare" in c or "amount" in c) for c in jos)
        if are_data and (are_debit or are_suma):
            antet_idx = i
            for j, c in enumerate(jos):
                if "data" in c and "data" not in col: col["data"] = j
                if ("detali" in c or "descriere" in c or "explicat" in c
                        or "detaliu" in c) and "detalii" not in col:
                    col["detalii"] = j
                if "debit" in c and "debit" not in col: col["debit"] = j
                if "credit" in c and "credit" not in col: col["credit"] = j
                if ("suma" in c or "valoare" in c or "amount" in c) and "suma" not in col:
                    col["suma"] = j
            break
    if antet_idx is None:
        return []
    n_expected = max(col.values()) + 1 if col else 0
    tranzactii, curenta = [], None
    for r in randuri[antet_idx + 1:]:
        celule = [str(c or "").strip() for c in r]
        if not any(celule):
            continue
        data_v = celule[col["data"]] if col.get("data") is not None and col["data"] < len(celule) else ""
        if _e_data(data_v):
            if curenta: tranzactii.append(curenta)
            suma = _extrage_suma(r, celule, col, n_expected)
            det = celule[col["detalii"]] if col.get("detalii") is not None and col["detalii"] < len(celule) else ""
            curenta = {"data": data_v[:10], "detalii": det, "suma": round(suma, 2)}
        elif curenta:
            extra = " ".join(c for c in celule if c)
            if extra: curenta["detalii"] = (curenta["detalii"] + " " + extra).strip()
    if curenta: tranzactii.append(curenta)
    return tranzactii


def _fara_antet(randuri):
    """[fara_antet_v1] Fallback fara antet: randuri care incep cu o data;
    ultima coloana numerica = suma (cu semn), restul intre data si suma = detalii."""
    tranzactii = []
    for r in randuri:
        celule = [str(c or "").strip() for c in r]
        if not celule or not _e_data(celule[0]):
            continue
        suma, suma_idx = None, None
        for j in range(len(celule) - 1, 0, -1):
            n = _numar(celule[j])
            if n is not None and celule[j] != "":
                suma, suma_idx = n, j
                break
        if suma is None:
            continue
        det = " ".join(c for c in celule[1:suma_idx] if c) if suma_idx else ""
        tranzactii.append({"data": celule[0][:10], "detalii": det, "suma": round(suma, 2)})
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
    """Detecteaza formatul dupa magic bytes si intoarce lista de tranzactii.
    Ridica ValueError (cu FORMAT_ASTEPTAT) daca parsarea esueaza sau da 0 tranzactii."""
    try:
        if continut[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":  # OLE2 = .xls
            import xlrd
            wb = xlrd.open_workbook(file_contents=continut)
            sh = wb.sheet_by_index(0)
            randuri = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
            tranzactii = _parse_grid(randuri) or _fara_antet(randuri)
        elif continut[:2] == b"PK":  # zip = .xlsx
            from openpyxl import load_workbook
            wb = load_workbook(BytesIO(continut), read_only=True)
            sh = wb.active
            randuri = [[c for c in rand] for rand in sh.iter_rows(values_only=True)]
            tranzactii = _parse_grid(randuri) or _fara_antet(randuri)
        else:  # text: MT940 sau csv
            text = continut.decode("utf-8", errors="replace") if isinstance(continut, bytes) else continut
            if ":61:" in text or ":20:" in text:  # marker MT940
                tranzactii = _parse_mt940(text)
            else:
                import csv
                delim = _detecteaza_delimitator(text)
                randuri = list(csv.reader(text.splitlines(), delimiter=delim)) if text.strip() else []
                tranzactii = _parse_grid(randuri) or _fara_antet(randuri)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Nu am putut citi extrasul ({e}). {FORMAT_ASTEPTAT}")
    if not tranzactii:
        raise ValueError(f"Nu am gasit tranzactii in extras. {FORMAT_ASTEPTAT}")
    return tranzactii
