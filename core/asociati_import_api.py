"""
core/asociati_import_api.py — import asociati (stratul 5 migrare) per firma.

Citeste un export (.xlsx/.csv) cu nume, CNP/CUI, cota %. Mapeaza flexibil coloanele.
Importa in tabelul existent `asociati` (DELETE + INSERT per firma).
Valideaza CNP daca are 13 cifre (cheie 279146358279); CUI persoana juridica acceptat fara validare.
Coerenta: suma cotelor ar trebui sa dea 100% (informativ, nu blocant).
"""
from __future__ import annotations
import datetime
from core.identitate import valideaza_cui as _valideaza_cui  # [Q4] CUI juridic validat ca CUI, nu ca CNP

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
        return False, "lună invalidă"
    try:
        datetime.date(an, ll, zz)
    except ValueError:
        return False, "dată invalidă"
    jj = int(cnp[7:9])
    if not (1 <= jj <= 52):
        return False, "județ invalid"
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


from core.numere import numar as _numar  # sursa unica (15.07.2026); "%" tratat acolo
from core.migrare_api import respinge  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator


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
        raise ValueError("Fișierul trimis nu se poate citi: se așteaptă un CSV sau un "
                         "XLSX. Salvează exportul în unul din formatele astea și "
                         "încarcă-l din nou.")

    if not randuri:
        return []

    antet = [str(x) for x in randuri[0]]
    i_nume = _gaseste_col(antet, "nume", "asociat", "denumire")
    i_cod = _gaseste_col(antet, "cnp", "cui", "cif", "cod")
    i_cota = _gaseste_col(antet, "cota", "cotă", "procent", "participare", "%")
    if i_nume < 0 and i_cod < 0:
        raise ValueError("nu găsesc coloana nume/cod asociat - fișier nerecunoscut")

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
        # [Q4] ramifica fizic/juridic ca extrage(): CUI de juridica se valideaza ca CUI (cifra de
        # control), NU ca CNP de 13 cifre. Altfel asociatul-firma acceptat la preview era respins aici.
        if cod:
            este_cnp = len(cod) == 13 and cod.isdigit()
            ok, motiv = valideaza_cnp(cod) if este_cnp else _valideaza_cui(cod)
            if not ok:
                er.append(respinge(
                    "asociat", i, "cnp_invalid" if este_cnp else "cui_invalid",
                    "%s: %s invalid (%s)" % (nume, "CNP" if este_cnp else "CUI", motiv)))
    c = coerenta_cote(randuri or [])
    if (randuri or []) and not c["coincide"]:
        # randul "-": afirmatia e despre SETUL de asociati, nu despre un rand anume - iar asta se
        # scrie, nu se ascunde alegand arbitrar primul rand.
        er.append(respinge("asociati (toti)", "-", "cote_nu_dau_suta",
                           "cotele asociaților însumează %s%%, nu 100%%" % c["total"]))
    return er


def importa(conn, randuri):
    """DELETE + INSERT per firma. Intoarce {importati}.
    Ridica ValueError daca randurile nu pot intra (vezi verifica_randuri)."""
    # [probare invalid, 03.09.2026 — aceeasi clasa ca importul de istoric] UN IMPORT GOL
    # STERGEA TOT, IN TACERE. Lista vida trecea de verificare (n-are ce respinge), ajungea la
    # `DELETE FROM asociati` de mai jos, si raspundea ca un import reusit cu zero randuri. Un fisier gol,
    # unul cu numai antet (`extrage` intoarce [] pe el), sau un apel de API cu lista goala — toate
    # ajungeau acolo. *Un import care nu aduce nimic n-are voie sa stearga ce era acolo.*
    if not randuri:
        raise ValueError("nu ai trimis niciun rând. Importul ar fi șters lista de asociați a "
                         "firmei, cu cotele lor de participare, și n-ar fi pus nimic în loc. "
                         "Dacă chiar vrei să golești lista, e altă operațiune.")
    er = verifica_randuri(randuri)
    if er:
        raise ValueError("%d probleme: %s. Asociații și cotele lor intră în D205 "
                         "(dividende) - cotele trebuie să dea exact 100%%."
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
