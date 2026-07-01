# anaf_api.py — validare CUI la ANAF (API public v9) + extragere CUI din fișier.
# Sursă oficială: https://static.anaf.ro/static/10/Anaf/Informatii_R/Servicii_web/doc_WS_V9.txt
# Endpoint: POST https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva
# Body: [{"cui": Numar, "data": "AAAA-LL-ZZ"}]  (max 100 CUI / cerere, max 1 cerere/sec)

import requests
from datetime import date

ANAF_URL = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
MAX_CUI = 100


def _curata(cui_brut):
    """Extrage doar cifrele (acceptă 'RO12345', ' 12345 ', etc.). None dacă nimic."""
    cifre = "".join(ch for ch in str(cui_brut) if ch.isdigit())
    return cifre or None


def _ghiceste_delim(text):
    prima = text.splitlines()[0] if text.splitlines() else ""
    return ";" if prima.count(";") > prima.count(",") else ","


def extrage_cui_din_fisier(continut, nume_fisier=""):
    """
    Extrage CUI-urile dintr-un .csv/.tsv sau .xlsx.
    Caută coloana al cărei antet conține 'cui'/'cif'; altfel ia prima coloană.
    Curăță fiecare valoare la cifre, păstrează doar 2–10 cifre, fără duplicate.
    """
    nume = (nume_fisier or "").lower()
    randuri = []

    if nume.endswith(".csv") or nume.endswith(".tsv") or nume.endswith(".txt"):
        import csv, io
        text = continut.decode("utf-8-sig", errors="replace") if isinstance(continut, bytes) else str(continut)
        delim = "\t" if nume.endswith(".tsv") else _ghiceste_delim(text)
        randuri = list(csv.reader(io.StringIO(text), delimiter=delim))
    elif nume.endswith(".xlsx") or nume.endswith(".xlsm"):
        import io
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(continut), read_only=True, data_only=True)
        ws = wb.active
        for r in ws.iter_rows(values_only=True):
            randuri.append(["" if c is None else str(c) for c in r])
        wb.close()
    else:
        raise ValueError("format neacceptat (doar .csv sau .xlsx)")

    if not randuri:
        return []

    # coloana CUI după antet; altfel prima coloană
    antet = [str(x).strip().lower() for x in randuri[0]]
    are_antet = any("cui" in h or "cif" in h for h in antet)
    col = 0
    for i, h in enumerate(antet):
        if "cui" in h or "cif" in h:
            col = i
            break

    cui_uri, vazute = [], set()
    for r in randuri[(1 if are_antet else 0):]:
        bruta = r[col] if col < len(r) else ""
        cifre = _curata(bruta)
        if cifre and 2 <= len(cifre) <= 10 and cifre not in vazute:
            vazute.add(cifre)
            cui_uri.append(cifre)
    return cui_uri


def valideaza_cui(lista_cui, data_interogare=None):
    """Întoarce [{cui, denumire, platitor_tva, stare, inactiv, gasit}], ordine păstrată, fără duplicate."""
    azi = data_interogare or date.today().isoformat()

    curatate, vazute = [], set()
    for c in lista_cui:
        cifre = _curata(c)
        if cifre and cifre not in vazute:
            vazute.add(cifre)
            curatate.append(int(cifre))
    if not curatate:
        return []

    rezultate = []
    for i in range(0, len(curatate), MAX_CUI):
        if i > 0:
            import time
            time.sleep(1.1)  # ANAF: max 1 cerere/sec
        lot = curatate[i:i + MAX_CUI]
        payload = [{"cui": c, "data": azi} for c in lot]
        r = requests.post(ANAF_URL, json=payload, timeout=20,
                          headers={"Content-Type": "application/json"})
        r.raise_for_status()
        dj = r.json()
        for f in dj.get("found", []):
            dg = f.get("date_generale", f.get("dategenerale", {})) or {}
            tva = f.get("inregistrare_scop_Tva", f.get("inregistrarescopTva", {})) or {}
            inactiv = f.get("stare_inactiv", {}) or {}
            rezultate.append({
                "cui": str(dg.get("cui", "")),
                "denumire": (dg.get("denumire") or "").strip(),
                "platitor_tva": bool(tva.get("scpTVA")),
                "stare": (dg.get("stare_inregistrare") or dg.get("stareinregistrare") or "").strip(),
                "inactiv": bool(inactiv.get("statusInactivi")),
                "adresa": (dg.get("adresa") or "").strip(),
                "gasit": True,
            })
        for c in dj.get("notFound", []):
            rezultate.append({
                "cui": str(c), "denumire": "", "platitor_tva": False,
                "stare": "", "inactiv": False, "adresa": "", "gasit": False,
            })
    return rezultate
