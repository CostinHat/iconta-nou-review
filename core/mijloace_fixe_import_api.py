"""
core/mijloace_fixe_import_api.py — import mijloace fixe (stratul 6 migrare) per firma.

Citeste un registru de mijloace fixe (.xlsx/.csv) cu: cod, denumire, valoare intrare,
valoare ramasa (rezidual), durata (luni), data PIF, metoda, conturi.
Importa in tabelul existent `mijloace_fixe` (DELETE + INSERT per firma).

Verificari informative (nu blocante):
- rezidual <= valoare (altfel eroare de date)
- valoare >= 5000 lei (plafon 2026 OUG 8/2026); sub plafon = avertisment
  (mijloacele existente la 31.12.2025 raman amortizabile pe durata ramasa - regula tranzitorie)
Amortizarea cumulata = valoare - rezidual (afisata informativ).
"""
from __future__ import annotations
import re as _re
import datetime

PLAFON_MF_2026 = 5000.0


def _gaseste_col(antet, *chei):
    for i, h in enumerate(antet):
        hl = str(h).strip().lower()
        for k in chei:
            if k in hl:
                return i
    return -1


from core.numere import numar as _numar  # sursa unica (15.07.2026, vezi core/numere.py)
from core.migrare_api import respinge  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator


def _intreg(v):
    return int(round(_numar(v)))


def _data(v):
    if v is None or str(v).strip() == "":
        return None
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    t = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(t, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _normalizeaza_metoda(v):
    t = _re.sub(r"[\s._-]+", "", str(v or "").lower())   # colapseaza separatorii: "super accelerata" -> "superaccelerata"
    if "superaccel" in t:          # INAINTE de "acceler": "superaccelerata" contine "acceler"
        return "superaccelerata"   # CF art.28 alin.8^1 (OUG 8/2026)
    if "degres" in t:
        return "degresiva"
    if "acceler" in t:
        return "accelerata"
    return "liniara"


def extrage(continut, nume_fisier=""):
    """Intoarce lista de dicturi cu campurile mijlocului fix + verificari."""
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
    i_cod = _gaseste_col(antet, "cod", "inventar", "nr")
    i_den = _gaseste_col(antet, "denumire", "nume", "mijloc")
    i_val = _gaseste_col(antet, "valoare", "intrare", "achizitie", "achiziție")
    i_rez = _gaseste_col(antet, "rezidual", "ramas", "rămas", "neamortizat", "ramasa")
    i_dur = _gaseste_col(antet, "durata", "durată", "luni", "dnf")
    i_pif = _gaseste_col(antet, "pif", "punere", "functiune", "funcțiune", "data")
    i_met = _gaseste_col(antet, "metoda", "metodă", "amortizare")
    i_cimo = _gaseste_col(antet, "cont imob", "cont_imob", "imobilizare")
    i_camo = _gaseste_col(antet, "cont amort", "cont_amort", "amortizare cont")
    if i_den < 0:
        raise ValueError("nu găsesc coloana denumire mijloc fix - fișier nerecunoscut")

    out = []
    for idx, r in enumerate(randuri[1:], start=1):
        def cel(i):
            return str(r[i]).strip() if (0 <= i < len(r)) else ""

        den = cel(i_den)
        if not den:
            continue
        valoare = _numar(cel(i_val))
        rezidual = _numar(cel(i_rez)) if i_rez >= 0 else valoare
        durata = _intreg(cel(i_dur))
        # durata in ani -> luni daca pare ani (< 60 si fisierul zice "ani")
        if 0 < durata <= 50 and "an" in (antet[i_dur].lower() if 0 <= i_dur < len(antet) else ""):
            durata *= 12

        amortizat = round(valoare - rezidual, 2)
        avertismente = []
        if rezidual > valoare + 0.01:
            avertismente.append("rezidual > valoare")
        if 0 < valoare < PLAFON_MF_2026:
            avertismente.append("sub plafon 5000 (2026)")
        if durata <= 0:
            avertismente.append("durată lipsă")
        if not cel(i_cimo):
            avertismente.append("cont de imobilizare lipsă - categorie neclasificată "
                                "(CF art.28 alin.5 lit.c): doar liniar/degresiv; "
                                "accelerat/superaccelerat vor fi refuzate la D406 până se completează contul")

        out.append({
            "cod": cel(i_cod) or f"MF{idx:03d}",
            "denumire": den,
            "valoare": valoare,
            "rezidual": rezidual,
            "amortizat": amortizat,
            "dnf_luni": durata,
            "data_pif": _data(r[i_pif]) if (0 <= i_pif < len(r)) else None,
            "metoda": _normalizeaza_metoda(cel(i_met)),
            "cont_imobilizare": cel(i_cimo),   # NU se completeaza tacit cu 2131 (categoria permisiva); gol -> lit.c
            "cont_amortizare": cel(i_camo) or "2813",
            "avertismente": avertismente,
            "ok": len(avertismente) == 0,
        })
    return out


def rezumat(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('mijloace_fixe')")
        if cur.fetchone()[0] is None:
            return {"are_mijloace": False, "randuri": 0, "total_valoare": 0, "total_rezidual": 0}
        cur.execute("SELECT count(*), COALESCE(sum(valoare),0), COALESCE(sum(rezidual),0) FROM mijloace_fixe")
        n, tv, tr = cur.fetchone()
    return {"are_mijloace": n > 0, "randuri": n,
            "total_valoare": float(tv), "total_rezidual": float(tr)}


def verifica_randuri(randuri):
    """PURA: [{rand, motiv, mesaj}]. Nicio validare nu exista pana la 15.07.2026:
    durata 0 (amortizarea nu se poate calcula), valoare ramasa > valoare de intrare
    (imposibil), cod de inventar duplicat - toate intrau, iar migrarea zicea "gata"."""
    er, coduri = [], {}
    for i, r in enumerate(randuri or [], start=2):
        cod = str(r.get("cod") or "").strip()
        den = str(r.get("denumire") or cod or "?").strip()
        val = float(r.get("valoare") or 0)
        rez = float(r.get("rezidual") or 0)
        dur = int(r.get("dnf_luni") or r.get("durata") or 0)   # [Q3] cheia reala e dnf_luni (extrage:136); "durata" nu exista niciodata -> dadea 0 pe fiecare rand
        if not cod:
            er.append(respinge("mijloc fix", i, "cod_lipsa", "%s: fără cod de inventar" % den))
        elif cod in coduri:
            er.append(respinge("mijloc fix", i, "cod_duplicat",
                               "codul de inventar %s apare de două ori (rândurile %s și %s)"
                               % (cod, coduri[cod], i)))
        else:
            coduri[cod] = i
        if dur <= 0:
            er.append(respinge("mijloc fix", i, "durata_lipsa",
                               "%s: durata %s luni - fără ea nu se calculează amortizarea" % (den, dur)))
        if val <= 0:
            er.append(respinge("mijloc fix", i, "valoare_lipsa",
                               "%s: valoare de intrare %s" % (den, val)))
        elif rez > val + 0.01:
            er.append(respinge("mijloc fix", i, "rezidual_peste_intrare",
                               "%s: valoarea rămasă (%s) depășește valoarea de intrare (%s)"
                               % (den, rez, val)))
    return er


def importa(conn, randuri):
    """DELETE + INSERT per firma. Intoarce {importati}.
    Ridica ValueError daca randurile nu pot intra (vezi verifica_randuri)."""
    er = verifica_randuri(randuri)
    if er:
        raise ValueError("%d rânduri nu pot intra: %s. Mijloacele fixe intră în "
                         "amortizare și în D406 SAF-T."
                         % (len(er), "; ".join("rand %s: %s" % (x["rand"], x["mesaj"]) for x in er[:6])))
    with conn.cursor() as cur:
        cur.execute("DELETE FROM mijloace_fixe")
        n = 0
        for r in randuri:
            cur.execute("""
                INSERT INTO mijloace_fixe
                  (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual,
                   dnf_luni, data_pif, metoda, activ)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true)
            """, (r["cod"], r["denumire"], r.get("cont_imobilizare") or "",   # fara default 2131; gol = neclasificat -> lit.c la calc_asset
                  r.get("cont_amortizare", "2813"), r.get("valoare", 0),
                  r.get("rezidual", 0), r.get("dnf_luni", 0),
                  r.get("data_pif"), r.get("metoda", "liniara")))
            n += 1
    conn.commit()
    return {"importati": n}
