"""
core/facturi_api.py — facturi în schema unui tenant: listă, creare, detalii, ștergere.
Rulează pe conexiunea deja poziționată pe schema tenantului (get_conn(schema)).

total/tva se CALCULEAZĂ pe server din linii (o singură sursă de adevăr — clientul
nu poate trimite sume incoerente cu liniile). Calculul e PUR (testabil fără DB).

Convenție (confirmată din d300._segmente: baza = total - tva):
  total = Σ(cantitate × preț) + Σ(TVA)   -> include TVA
  tva   = Σ(cantitate × preț × cotă/100)
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP

REGULI = "2026.1"
MODUL = "facturi_api"


def _q(x):
    """Rotunjește la 2 zecimale (ca numeric(12,2)), ROUND_HALF_UP."""
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ============================================================
#  CALCUL totaluri — PUR
# ============================================================
def totaluri_din_linii(linii):
    """
    linii: listă de dict cu cantitate, pret_unitar, cota_tva.
    Întoarce {"total": Decimal, "tva": Decimal} (total include TVA).
    """
    baza = Decimal(0)
    tva = Decimal(0)
    for l in linii:
        b = Decimal(str(l["cantitate"])) * Decimal(str(l["pret_unitar"]))
        t = b * Decimal(str(l["cota_tva"])) / Decimal(100)
        baza += b
        tva += t
    return {"total": _q(baza + tva), "tva": _q(tva)}


# ============================================================
#  CREARE — DB
# ============================================================
from core import curs_bnr


def creeaza_factura(conn, numar, data_emitere, directie, linii,
                    client_id=None, tert_nume=None, tert_cui=None, tert_adresa=None,
                    data_scadenta=None, moneda="RON", status="emisa"):
    """
    Inserează factura + liniile, într-o tranzacție. total/tva calculate din linii.
    Întoarce {ok, factura_id, total, tva}.
    """
    if not linii:
        raise ValueError("factura trebuie să aibă cel puțin o linie")
    if directie not in ("emisa", "primita"):
        raise ValueError("directie trebuie 'emisa' sau 'primita'")
    t = totaluri_din_linii(linii)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO facturi (client_id, numar, data_emitere, data_scadenta, "
            "total, tva, status, moneda, directie, tert_nume, tert_cui, tert_adresa) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (client_id, numar, data_emitere, data_scadenta, t["total"], t["tva"],
             status, moneda, directie, tert_nume, tert_cui, tert_adresa))
        factura_id = cur.fetchone()[0]
        for l in linii:
            cur.execute(
                "INSERT INTO factura_linii (factura_id, descriere, um, cantitate, "
                "pret_unitar, cota_tva) VALUES (%s,%s,%s,%s,%s,%s)",
                (factura_id, l["descriere"], l.get("um", "buc"),
                 l["cantitate"], l["pret_unitar"], l["cota_tva"]))
    return {"ok": True, "factura_id": factura_id,
            "total": float(t["total"]), "tva": float(t["tva"])}


# ============================================================
#  LISTĂ — DB
# ============================================================
def lista_facturi(conn, an=None, luna=None, directie=None):
    """Lista facturilor (antet), filtrabilă pe an/lună/direcție."""
    import psycopg2.extras as _E
    cond, val = [], []
    if an is not None and luna is not None:
        inceput = "%04d-%02d-01" % (an, luna)
        sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
        cond.append("data_emitere >= %s AND data_emitere < %s"); val += [inceput, sfarsit]
    elif an is not None:
        cond.append("data_emitere >= %s AND data_emitere < %s")
        val += ["%04d-01-01" % an, "%04d-01-01" % (an + 1)]
    if directie is not None:
        cond.append("directie = %s"); val.append(directie)
    where = (" WHERE " + " AND ".join(cond)) if cond else ""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, numar, data_emitere, directie, total, tva, status, "
            "moneda, tert_nume, tert_cui, tert_adresa, tip, transformat_in_id, storno_din_id FROM facturi" + where +
            " ORDER BY data_emitere DESC, id DESC", val)
        return [dict(r) for r in cur.fetchall()]


# ============================================================
#  DETALII — DB
# ============================================================
def detalii_factura(conn, factura_id):
    """O factură cu liniile ei, sau None."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, client_id, numar, data_emitere, data_scadenta, total, tva, "
            "status, moneda, directie, tert_nume, tert_cui, tert_adresa, "
            "curs_bnr, tva_lei, total_lei, data_curs, curs_sursa, storno_din_id, tip, transformat_in_id "
            "FROM facturi WHERE id = %s",
            (factura_id,))
        f = cur.fetchone()
        if not f:
            return None
        f = dict(f)
        cur.execute(
            "SELECT id, descriere, um, cantitate, pret_unitar, cota_tva "
            "FROM factura_linii WHERE factura_id = %s ORDER BY id", (factura_id,))
        f["linii"] = [dict(r) for r in cur.fetchall()]
    return f


# ============================================================
#  ȘTERGERE — DB (liniile cad prin CASCADE)
# ============================================================
def sterge_factura(conn, factura_id):
    """Șterge factura (liniile cad automat prin ON DELETE CASCADE)."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM facturi WHERE id = %s", (factura_id,))
        sterse = cur.rowcount
    return {"ok": sterse > 0}


# ============================================================
#  EMITERE — numerotare, emitere, storno  [p103_emitere]
# ============================================================
def numerotare(conn):
    """Citeste serie + urmatorul numar de factura din firma_profil."""
    with conn.cursor() as cur:
        cur.execute("SELECT serie_factura, urmator_numar_factura FROM firma_profil LIMIT 1")
        row = cur.fetchone()
    serie = row[0] if row else None
    urmator = int(row[1]) if row and row[1] is not None else 1
    return {"serie": serie, "urmator_numar": urmator}


def seteaza_numerotare(conn, serie=None, numar_start=None):
    """Configureaza seria + numarul de start (continuitate cu istoricul).
    Se apeleaza o data; dupa, numarul se auto-incrementeaza la emitere."""
    seturi, val = [], []
    if serie is not None:
        seturi.append("serie_factura = %s"); val.append(serie.strip() or None)
    if numar_start is not None:
        seturi.append("urmator_numar_factura = %s"); val.append(int(numar_start))
    if not seturi:
        return {"ok": False, "mesaj": "nimic de setat"}
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET " + ", ".join(seturi), val)
    return {"ok": True}


def _potriveste_linii(conn, linii, platitor_tva=True):
    """Pentru fiecare linie fara cota_tva, o potriveste (nomenclator/AI) si o
    salveaza in nomenclator. Intoarce liniile cu cota completata."""
    from core import produse_api
    out = []
    for l in linii:
        linie = dict(l)
        if linie.get("cota_tva") is None:
            # creeaza() cauta in nomenclator, altfel AI + salveaza; nu dubleaza
            r = produse_api.creeaza(conn, linie.get("descriere", ""),
                                    um=linie.get("um", "buc"),
                                    pret_unitar=linie.get("pret_unitar", 0),
                                    platitor_tva=platitor_tva)
            linie["cota_tva"] = r.get("cota_tva", 21)
        out.append(linie)
    return out


def emite_factura(conn, linii, client_id=None, tert_nume=None, tert_cui=None, tert_adresa=None,
                  data_emitere=None, data_scadenta=None, moneda="RON",
                  platitor_tva=True, status="de_preluat", curs_manual=None, tip="factura"):
    """
    Emite o factura noua (directie=emisa):
      - potriveste cota pe liniile fara cota (nomenclator/AI)
      - numeroteaza automat (serie + urmator_numar din firma_profil)
      - salveaza + incrementeaza contorul
    Intoarce {ok, factura_id, numar, serie, total, tva}.
    """
    import datetime
    if not linii:
        raise ValueError("factura trebuie sa aiba cel putin o linie")
    data_emitere = data_emitere or datetime.date.today().isoformat()

    linii = _potriveste_linii(conn, linii, platitor_tva=platitor_tva)
    if tip == "factura":
        num = numerotare(conn)
        serie = num["serie"]
        numar_int = num["urmator_numar"]
        numar = f"{serie}{numar_int}" if serie else str(numar_int)
    else:
        prefix = "PF" if tip == "proforma" else "AV"
        col = "urmator_numar_proforma" if tip == "proforma" else "urmator_numar_aviz"
        with conn.cursor() as cur:
            cur.execute(f"SELECT {col} FROM firma_profil LIMIT 1")
            numar_int = (cur.fetchone() or [1])[0] or 1
        serie = prefix
        numar = f"{prefix}{numar_int}"

    r = creeaza_factura(conn, numar, data_emitere, "emisa", linii,
                        client_id=client_id, tert_nume=tert_nume, tert_cui=tert_cui, tert_adresa=tert_adresa,
                        data_scadenta=data_scadenta, moneda=moneda, status=status)
    # setez seria pe factura + incrementez contorul
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET serie = %s WHERE id = %s", (serie, r["factura_id"]))
        if tip == "factura":
            cur.execute("UPDATE firma_profil SET urmator_numar_factura = %s", (numar_int + 1,))
        else:
            col = "urmator_numar_proforma" if tip == "proforma" else "urmator_numar_aviz"
            cur.execute(f"UPDATE firma_profil SET {col} = %s", (numar_int + 1,))
        cur.execute("UPDATE facturi SET tip = %s WHERE id = %s", (tip, r["factura_id"]))
    # ---- CURS VALUTAR (art. 290/319 Cod fiscal): TVA obligatoriu si in lei ----
    import datetime as _dt
    _fid = r["factura_id"]
    _total = r["total"]
    _tva = r["tva"]
    if isinstance(data_emitere, str):
        _d = _dt.date.fromisoformat(data_emitere)
    elif isinstance(data_emitere, _dt.date):
        _d = data_emitere
    else:
        _d = _dt.date.today()

    if (moneda or "RON").upper() == "RON":
        _curs, _dcurs, _sursa = 1, _d, "ron"
    elif curs_manual is not None:
        _curs, _dcurs, _sursa = float(curs_manual), _d, "manual"
    else:
        try:
            _c, _dc, _s = curs_bnr.curs_pentru(conn, moneda, _d)
            _curs, _dcurs, _sursa = float(_c), _dc, _s
        except curs_bnr.CursIndisponibil:
            # nu emit factura in valuta fara curs valid; anulez inseratul si semnalez frontend-ului
            conn.rollback()
            return {"ok": False, "cod": "CURS_INDISPONIBIL",
                    "moneda": moneda, "data": _d.isoformat(),
                    "mesaj": "Cursul BNR nu e disponibil momentan."}

    _tva_lei = round(float(_tva) * _curs, 2)
    _total_lei = round(float(_total) * _curs, 2)
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE facturi SET curs_bnr=%s, tva_lei=%s, total_lei=%s, "
            "data_curs=%s, curs_sursa=%s WHERE id=%s",
            (_curs, _tva_lei, _total_lei, _dcurs, _sursa, _fid))

    r["curs_bnr"] = _curs
    r["tva_lei"] = _tva_lei
    r["total_lei"] = _total_lei
    r["curs_sursa"] = _sursa
    r["numar"] = numar
    r["serie"] = serie
    return r


def storneaza(conn, factura_id):
    """
    Creeaza o factura de stornare: copie a originalului cu cantitati NEGATIVE,
    numar nou din aceeasi serie, referinta la original (storno_din_id).
    Intoarce {ok, factura_id, numar, ...} sau ridica ValueError.
    """
    orig = detalii_factura(conn, factura_id)
    if not orig:
        raise ValueError("factura de stornat nu exista")
    if orig.get("directie") != "emisa":
        raise ValueError("se storneaza doar facturi emise")
    # linii negate
    linii_neg = []
    for l in orig.get("linii", []):
        linii_neg.append({
            "descriere": "STORNO: " + (l.get("descriere") or ""),
            "um": l.get("um", "buc"),
            "cantitate": -abs(float(l.get("cantitate", 0))),
            "pret_unitar": float(l.get("pret_unitar", 0)),
            "cota_tva": float(l.get("cota_tva", 21)),
        })
    num = numerotare(conn)
    serie = num["serie"]; numar_int = num["urmator_numar"]
    numar = f"{serie}{numar_int}" if serie else str(numar_int)
    import datetime
    r = creeaza_factura(conn, numar, datetime.date.today().isoformat(), "emisa",
                        linii_neg, client_id=orig.get("client_id"),
                        tert_nume=orig.get("tert_nume"), tert_cui=orig.get("tert_cui"), tert_adresa=orig.get("tert_adresa"),
                        moneda=orig.get("moneda", "RON"), status="de_preluat")
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET serie = %s, storno_din_id = %s WHERE id = %s",
                    (serie, factura_id, r["factura_id"]))
        cur.execute("UPDATE firma_profil SET urmator_numar_factura = %s", (numar_int + 1,))
    r["numar"] = numar
    r["storno_din_id"] = factura_id
    return r
