"""
core/asociati_import_api.py — import asociati (stratul 5 migrare) per firma.

Citeste un export (.xlsx/.csv) cu nume, CNP/CUI, cota %. Mapeaza flexibil coloanele.
Importa in tabelul existent `asociati` (DELETE + INSERT per firma).
Valideaza CNP daca are 13 cifre (cheie 279146358279); CUI persoana juridica acceptat fara validare.
Coerenta: suma cotelor ar trebui sa dea 100% (informativ, nu blocant).
"""
from __future__ import annotations
import datetime

_CHEIE = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]


def valideaza_cnp(cnp):
    """(valid, motiv). Doar pentru coduri de 13 cifre (persoana fizica)."""
    cnp = str(cnp or "").strip()
    if len(cnp) != 13 or not cnp.isdigit():
        return False, "nu e CNP 13 cifre"
    if cnp[0] not in "123456789":
        return False, "prima cifra"
    s = int(cnp[0]); aa = int(cnp[1:3]); ll = int(cnp[3:5]); zz = int(cnp[5:7])
    sec = {1: 1900, 2: 1900, 3: 1800, 4: 1800, 5: 2000, 6: 2000,
           7: 2000, 8: 2000, 9: 1900}.get(s, 1900)
    an = sec + aa
    if not (1 <= ll <= 12):
        return False, "luna invalida"
    try:
        datetime.date(an, ll, zz)
    except ValueError:
        return False, "data invalida"
    jj = int(cnp[7:9])
    if not (1 <= jj <= 52):
        return False, "judet invalid"
    suma = sum(int(cnp[i]) * _CHEIE[i] for i in range(12))
    ctrl = suma % 11
    ctrl = 1 if ctrl == 10 else ctrl
    if ctrl != int(cnp[12]):
        return False, "cifra de control"
    return True, "ok"


def _gaseste_col(antet, *chei):
    for i, h in enumerate(antet):
        hl = str(h).strip().lower()
        for k in chei:
            if k in hl:
                return i
    return -1


def _numar(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip().replace(" ", "").replace("%", "")
    if not t:
        return 0.0
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


def extrage(continut, nume_fisier=""):
    """Intoarce [{nume, cnp, cota, tip, cnp_valid, cnp_motiv}]."""
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
    i_nume = _gaseste_col(antet, "nume", "asociat", "denumire")
    i_cod = _gaseste_col(antet, "cnp", "cui", "cif", "cod")
    i_cota = _gaseste_col(antet, "cota", "cotă", "procent", "participare", "%")

    out = []
    for r in randuri[1:]:
        def cel(i):
            return str(r[i]).strip() if (0 <= i < len(r)) else ""
        nume_v = cel(i_nume)
        cod = cel(i_cod).upper().replace("RO", "").replace(" ", "")
        cota = _numar(cel(i_cota))
        if not nume_v:
            continue
        # persoana fizica daca pare CNP de 13 cifre, altfel juridica
        este_cnp = len(cod) == 13 and cod.isdigit()
        if este_cnp:
            valid, motiv = valideaza_cnp(cod)
            tip = "fizica"
        else:
            valid, motiv = True, "CUI"   # juridica, nu validam CNP
            tip = "juridica"
        out.append({"nume": nume_v, "cnp": cod, "cota": cota,
                    "tip": tip, "cnp_valid": valid, "cnp_motiv": motiv})
    return out


def coerenta_cote(randuri):
    """{total, coincide} — suma cotelor vs 100%."""
    total = round(sum(r.get("cota", 0) for r in randuri), 2)
    return {"total": total, "coincide": abs(total - 100.0) < 0.01}


def rezumat(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('asociati')")
        if cur.fetchone()[0] is None:
            return {"are_asociati": False, "randuri": 0, "total_cota": 0}
        cur.execute("SELECT count(*), COALESCE(sum(cota),0) FROM asociati")
        n, tc = cur.fetchone()
    return {"are_asociati": n > 0, "randuri": n, "total_cota": float(tc)}


def verifica_randuri(randuri):
    """PURA: [{rand, motiv, mesaj}]. CNP/CUI valid + cotele insumeaza exact 100%.

    coerenta_cote() exista de la inceput, dar importa() n-o chema: cotele de 115% au
    intrat, iar migrarea a marcat stratul "gata" verde. D205 nu se poate genera cu ele
    (dovedit 15.07.2026, prin migrare reala).
    """
    er = []
    for i, r in enumerate(randuri or [], start=2):   # antetul e randul 1
        nume = str(r.get("nume") or "?").strip()
        cod = str(r.get("cnp") or "").strip()
        if cod and not valideaza_cnp(cod)[0]:
            er.append({"rand": i, "motiv": "cnp_invalid",
                       "mesaj": "%s: CNP/CUI invalid (%s)" % (nume, valideaza_cnp(cod)[1])})
    c = coerenta_cote(randuri or [])
    if (randuri or []) and not c["coincide"]:
        er.append({"rand": "-", "motiv": "cote",
                   "mesaj": "cotele asociatilor insumeaza %s%%, nu 100%%" % c["total"]})
    return er


def importa(conn, randuri):
    """DELETE + INSERT per firma. Intoarce {importati}.
    Ridica ValueError daca randurile nu pot intra (vezi verifica_randuri)."""
    er = verifica_randuri(randuri)
    if er:
        raise ValueError("%d probleme: %s. Asociatii si cotele lor intra in D205 "
                         "(dividende) - cotele trebuie sa dea exact 100%%."
                         % (len(er), "; ".join(x["mesaj"] for x in er[:6])))
    with conn.cursor() as cur:
        cur.execute("DELETE FROM asociati")
        n = 0
        for r in randuri:
            cur.execute(
                "INSERT INTO asociati (nume, cnp, cota) VALUES (%s,%s,%s)",
                (r["nume"], r.get("cnp", ""), r.get("cota", 0)))
            n += 1
    conn.commit()
    return {"importati": n}
