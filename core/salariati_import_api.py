"""
core/salariati_import_api.py — import salariati (stratul 4 migrare) per firma.

Citeste un export din vechea aplicatie (.xlsx/.csv) si mapeaza flexibil coloanele
(nume/prenume/CNP/salariu/functie/data angajare) indiferent de ordine sau denumire exacta.
Importa in tabelul existent `salariati` din schema tenantului (NU il recreeaza).
Valideaza CNP (cheie de control oficiala 279146358279 + structura data + judet).
"""
from __future__ import annotations
import datetime

_CHEIE = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]


def valideaza_cnp(cnp):
    """(valid: bool, motiv: str). Verifica format, data, judet, cifra de control."""
    cnp = str(cnp or "").strip()
    if len(cnp) != 13 or not cnp.isdigit():
        return False, "format (13 cifre)"
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


from core.numere import numar as _numar  # sursa unica (15.07.2026, vezi core/numere.py)


def _data(v):
    """Parseaza o data din diverse formate -> 'YYYY-MM-DD' sau None."""
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


def _split_nume(intreg):
    """Daca avem un singur camp 'nume complet', desparte in nume + prenume."""
    parti = str(intreg or "").strip().split()
    if len(parti) >= 2:
        return parti[0], " ".join(parti[1:])
    return (parti[0] if parti else ""), ""


def extrage(continut, nume_fisier=""):
    """
    Intoarce [{nume, prenume, cnp, data_angajare, tip_norma, ore_zi, salariu_brut,
               persoane_intretinere, judet_casa, cor, cnp_valid, cnp_motiv}].
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
    i_nume = _gaseste_col(antet, "nume")          # poate prinde "nume complet" sau "nume"
    i_pren = _gaseste_col(antet, "prenume")
    i_cnp = _gaseste_col(antet, "cnp", "cod numeric")
    i_data = _gaseste_col(antet, "angajare", "angajat", "data contract", "contract din")
    i_norma = _gaseste_col(antet, "norma", "norma")
    i_ore = _gaseste_col(antet, "ore")
    i_brut = _gaseste_col(antet, "brut", "salariu")
    i_intr = _gaseste_col(antet, "intretinere", "persoane")
    i_jud = _gaseste_col(antet, "judet", "casa")
    i_cor = _gaseste_col(antet, "cor", "ocupatie", "ocupație")
    if i_nume < 0 and i_cnp < 0:
        raise ValueError("nu gasesc coloana nume/CNP salariat - fisier nerecunoscut")

    out = []
    for r in randuri[1:]:
        def cel(i):
            return str(r[i]).strip() if (0 <= i < len(r)) else ""

        cnp = cel(i_cnp)
        nume_v = cel(i_nume)
        pren_v = cel(i_pren)
        # daca prenume lipseste dar numele pare complet, desparte
        if not pren_v and i_pren < 0 and " " in nume_v:
            nume_v, pren_v = _split_nume(nume_v)

        if not (cnp or nume_v):   # rand gol
            continue

        valid, motiv = valideaza_cnp(cnp)
        norma = cel(i_norma).lower()
        tip_norma = "partiala" if ("part" in norma or "parțial" in norma) else "intreaga"
        ore = _numar(cel(i_ore)) if i_ore >= 0 else 0.0
        if ore <= 0:
            ore = 8 if tip_norma == "intreaga" else 4

        out.append({
            "nume": nume_v,
            "prenume": pren_v,
            "cnp": cnp,
            "data_angajare": _data(r[i_data]) if (0 <= i_data < len(r)) else None,
            "tip_norma": tip_norma,
            "ore_zi": ore,
            "salariu_brut": _numar(cel(i_brut)),
            "persoane_intretinere": int(_numar(cel(i_intr))) if i_intr >= 0 else 0,
            "judet_casa": cel(i_jud),
            "cor": cel(i_cor),
            "cnp_valid": valid,
            "cnp_motiv": motiv,
        })
    return out


def rezumat(conn):
    """{are_salariati, randuri} pentru firma curenta (tabel existent salariati)."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('salariati')")
        if cur.fetchone()[0] is None:
            return {"are_salariati": False, "randuri": 0}
        cur.execute("SELECT count(*) FROM salariati")
        n = cur.fetchone()[0]
    return {"are_salariati": n > 0, "randuri": n}


JUDETE_CASA = ("AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ","CS","CL","CJ","CT",
               "CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS","IF","MM","MH","MS",
               "NT","OT","PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN","B")


def verifica_randuri(randuri, azi=None):
    """PURA: [{rand, motiv, mesaj}] - ce nu poate intra in evidenta.

    Pana la 15.07.2026 importa() verifica DOAR cnp_valid; restul intra oricum. Dovedit
    prin migrare reala: brut 1500 la norma intreaga (sub minimul de 4325 -> firma ar fi
    platit CAS/CASS pe 4125 fara sa stie, art.146(5^6)), angajare in 2027, 15 ore/zi,
    judet 'ZZ' inexistent, COR '999999' - toate au intrat, iar migrarea a zis "gata".
    """
    import datetime as _dt
    azi = azi or _dt.date.today()
    er = []
    for i, r in enumerate(randuri or [], start=2):   # antetul e randul 1
        nume = ("%s %s" % (r.get("nume") or "", r.get("prenume") or "")).strip() or "?"
        if not r.get("cnp_valid"):
            er.append({"rand": i, "motiv": "cnp_invalid",
                       "mesaj": "%s: CNP invalid (%s)" % (nume, r.get("cnp_motiv") or "-")})
            continue
        d = r.get("data_angajare")
        if d:
            try:
                dd = d if isinstance(d, _dt.date) else _dt.date.fromisoformat(str(d)[:10])
                if dd > azi:
                    er.append({"rand": i, "motiv": "data_viitor",
                               "mesaj": "%s: data angajarii (%s) e in viitor" % (nume, dd)})
            except ValueError:
                er.append({"rand": i, "motiv": "data_invalida",
                           "mesaj": "%s: data angajarii nu se intelege (%r)" % (nume, d)})
        ore = r.get("ore_zi")
        if ore is not None and not (1 <= float(ore or 0) <= 8):
            er.append({"rand": i, "motiv": "ore_invalide",
                       "mesaj": "%s: %s ore/zi (norma legala e de maximum 8)" % (nume, ore)})
        j = str(r.get("judet_casa") or "").strip().upper()
        if j and j not in JUDETE_CASA:
            er.append({"rand": i, "motiv": "judet_invalid",
                       "mesaj": "%s: judetul '%s' nu exista" % (nume, j)})
    return er


def importa(conn, randuri):
    """
    Insereaza salariatii in tabelul existent. UPSERT pe CNP (daca exista, actualizeaza).
    Ridica ValueError daca vreun rand nu poate intra (vezi verifica_randuri).
    Refuzul e PRIMA POARTA: nimic nu se scrie dintr-un import cu randuri invalide.
    Intoarce {importati, sarite_cnp}.
    """
    er = verifica_randuri(randuri)
    if er:
        det = "; ".join("rand %s: %s" % (e["rand"], e["mesaj"]) for e in er[:6])
        if len(er) > 6:
            det += " (si inca %d)" % (len(er) - 6)
        raise ValueError("%d randuri nu pot intra in evidenta: %s. Salariatii intra in "
                         "D112 si REGES - datele trebuie sa fie cele reale." % (len(er), det))
    importati = 0
    sarite = 0
    with conn.cursor() as cur:
        # asiguram constrangerea unica pe cnp pentru upsert (idempotent)
        cur.execute("""
            DO $$ BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM pg_constraint c
                JOIN pg_namespace n ON n.oid = c.connamespace
                WHERE c.conname = 'salariati_cnp_uniq' AND n.nspname = current_schema()
              ) THEN
                ALTER TABLE salariati ADD CONSTRAINT salariati_cnp_uniq UNIQUE (cnp);
              END IF;
            END $$;
        """)
        for r in randuri:
            if not r.get("cnp_valid"):
                sarite += 1
                continue
            part_time = (r.get("tip_norma", "intreaga") == "partiala")
            cur.execute("""
                INSERT INTO salariati
                  (cnp, nume, prenume, data_angajare, part_time, ore_zi,
                   persoane_intretinere, judet_casa, cor)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (cnp) DO UPDATE SET
                  nume=EXCLUDED.nume, prenume=EXCLUDED.prenume,
                  data_angajare=EXCLUDED.data_angajare, part_time=EXCLUDED.part_time,
                  ore_zi=EXCLUDED.ore_zi,
                  persoane_intretinere=EXCLUDED.persoane_intretinere,
                  judet_casa=EXCLUDED.judet_casa, cor=EXCLUDED.cor
                RETURNING id
            """, (r["cnp"], r["nume"], r["prenume"], r.get("data_angajare"),
                  part_time, r.get("ore_zi", 8),
                  r.get("persoane_intretinere", 0),
                  r.get("judet_casa", ""), r.get("cor", "")))
            # [PASUL 2b] salariul de baza pe salariu_istoric (sursa unica); reparat si activ (coloana retrasa PASUL 1)
            _sid = cur.fetchone()[0]
            from core import salariu_istoric as _si
            from datetime import date as _dm
            _si.seteaza(cur, _sid, r.get("salariu_brut", 0), r.get("data_angajare") or _dm.today().isoformat())
            importati += 1
    conn.commit()
    return {"importati": importati, "sarite_cnp": sarite}
