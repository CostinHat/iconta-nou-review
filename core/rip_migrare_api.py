"""
core/rip_migrare_api.py — import registru încasări-plăți (RIP) la preluarea unui PFA.

Partida simplă NU are balanță de deschidere (spre deosebire de solduri_api). Registrul
e CRONOLOGIC: la preluare se importă operațiunile anului curent de la 1 ian până la data
preluării. Soldul e implicit din sumă operațiuni, nu un rând separat.

Sursă: export din ce ținea contabilul anterior (.xlsx/.csv) — o linie per operațiune, cu
coloanele Data / Tip / Explicație / Sumă / (opțional) Document / Categorie / Metodă.

Reutilizează parserul numeric robust din solduri_api (_numar: paranteze=negativ, format
contabil RO/EN, sufixe RON/lei) — un singur loc pentru interpretarea sumelor, testat 15.07.

Operațiunile importate intră cu status='validata' (sunt istoric preluat, nu ciornă de
verificat) — dar vezi LIMITA la final: preluarea nu certifică corectitudinea contabilului
anterior; e evidență preluată, marcată ca atare.
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from core.solduri_api import _numar, _gaseste_col


# coloanele obligatorii din rip_operatiuni (din \d tenant_XXX.rip_operatiuni, 20.07):
#   data_operatiune, tip, explicatie, suma, valuta(def RON), metoda, categorie — NOT NULL
# opționale: document_tip/numar/data, suma_valuta, curs_valutar, deductibilitate
TIPURI = ("incasare", "plata")
# metoda VARCHAR(10) NOT NULL, CHECK metoda IN ('numerar','banca') — verificat 20.07 pe
# tenant_002.rip_operatiuni si aliniat cu core/rip_api.py (modulul live). NU 'casa'.
METODE = ("banca", "numerar")


def _bani(x):
    """Sumă la 2 zecimale, ROUND_HALF_UP (regula aritmetică iConta)."""
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _norm_tip(v):
    """Normalizează tipul operațiunii la incasare/plata."""
    t = str(v or "").strip().lower()
    if t in ("incasare", "încasare", "incasari", "intrare", "credit", "i"):
        return "incasare"
    if t in ("plata", "plată", "plati", "iesire", "ieșire", "debit", "p", "cheltuiala", "cheltuială"):
        return "plata"
    return None  # necunoscut → rândul se raportează, nu se ghicește


def _norm_metoda(v):
    """Normalizează metoda la numerar/banca (valorile din CHECK-ul DB, ca rip_api.py).
    Default 'banca' dacă lipsește (cele mai multe operațiuni preluate vin din extras) —
    dar se raportează câte au fost prezumate."""
    t = str(v or "").strip().lower()
    if "cas" in t or "numerar" in t or "cash" in t:
        return "numerar"
    if "banc" in t or "cont" in t or "virament" in t or "card" in t:
        return "banca"
    return None


def extrage_operatiuni(continut, nume_fisier=""):
    """
    Întoarce ({operatiuni:[...]}, raport) din fișierul de registru.
    Fiecare operațiune: {data, tip, explicatie, suma, metoda, categorie, document_*}.
    raport: {total, valide, respinse:[{rand, motiv}], metoda_prezumata}.

    Detectează coloanele după antet. NU ghicește tipul/metoda: rândurile ambigue merg
    în respinse cu motiv, ca importatorul (omul) să le vadă — nu se colorează verde tăcut.
    """
    nume = (nume_fisier or "").lower()
    randuri = _citeste_tabel(continut, nume)
    if not randuri:
        return {"operatiuni": []}, {"total": 0, "valide": 0, "respinse": [], "metoda_prezumata": 0}

    antet = randuri[0]
    i_data = _gaseste_col(antet, "data")
    i_tip  = _gaseste_col(antet, "tip", "fel", "sens")
    i_expl = _gaseste_col(antet, "explica", "descrie", "detalii")
    i_suma = _gaseste_col(antet, "suma", "sumă", "valoare", "incasari", "plati")
    i_cat  = _gaseste_col(antet, "categor")
    i_met  = _gaseste_col(antet, "metoda", "metodă", "cont", "mod")
    i_doc  = _gaseste_col(antet, "document", "factura", "chitanta")

    ops, respinse, metoda_prezumata = [], [], 0
    for nr, rand in enumerate(randuri[1:], start=2):
        def get(i):
            return rand[i] if 0 <= i < len(rand) else None

        data_op = get(i_data)
        if not data_op or not str(data_op).strip():
            respinse.append({"rand": nr, "motiv": "lipsă dată operațiune"})
            continue

        tip = _norm_tip(get(i_tip)) if i_tip >= 0 else None
        if tip is None:
            respinse.append({"rand": nr, "motiv": f"tip operațiune neclar: {get(i_tip)!r}"})
            continue

        expl = str(get(i_expl) or "").strip() if i_expl >= 0 else ""
        if not expl:
            respinse.append({"rand": nr, "motiv": "lipsă explicație (NOT NULL)"})
            continue

        suma = _numar(get(i_suma), strict=False) if i_suma >= 0 else 0.0
        if suma == 0.0:
            respinse.append({"rand": nr, "motiv": "sumă 0 sau neinterpretabilă"})
            continue
        suma = abs(suma)  # semnul e dat de tip, nu de sumă

        metoda = _norm_metoda(get(i_met)) if i_met >= 0 else None
        if metoda is None:
            metoda = "banca"
            metoda_prezumata += 1

        categorie = str(get(i_cat) or "").strip() if i_cat >= 0 else ""
        if not categorie:
            categorie = "neclasificat"  # NOT NULL; contabilul reclasifică în ecran

        ops.append({
            "data": str(data_op).strip(),
            "tip": tip,
            "explicatie": expl,
            "suma": str(_bani(suma)),
            "metoda": metoda,
            "categorie": categorie,
            "document_numar": str(get(i_doc) or "").strip() if i_doc >= 0 else "",
        })

    raport = {
        "total": len(randuri) - 1,
        "valide": len(ops),
        "respinse": respinse,
        "metoda_prezumata": metoda_prezumata,
    }
    return {"operatiuni": ops}, raport


def _citeste_tabel(continut, nume):
    """[[celule]] din .csv/.tsv/.xlsx. Clonă logica de citire din solduri_api."""
    if nume.endswith((".csv", ".tsv", ".txt")):
        import csv, io
        text = continut.decode("utf-8-sig", errors="replace") if isinstance(continut, bytes) else str(continut)
        linii = text.splitlines()
        if not linii:
            return []
        delim = "\t" if nume.endswith(".tsv") else (";" if linii[0].count(";") > linii[0].count(",") else ",")
        return [r for r in csv.reader(io.StringIO(text), delimiter=delim) if any(c.strip() for c in r)]
    # xlsx
    import io
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(continut) if isinstance(continut, bytes) else continut, read_only=True, data_only=True)
    ws = wb.active
    out = []
    for row in ws.iter_rows(values_only=True):
        if any(c is not None and str(c).strip() for c in row):
            out.append([("" if c is None else c) for c in row])
    return out


def importa(conn, schema, operatiuni):
    """
    Scrie operațiunile în {schema}.rip_operatiuni cu status='validata' (istoric preluat).
    Întoarce {importate, sarite_duplicat, erori:[...]}. Tranzacție atomică: totul sau nimic.

    Idempotent la reimport: o operațiune identică ce EXISTĂ deja se sare (nu e eroare, doar
    exclusă din importate) — ca reimportul repetat al aceluiași fișier să nu dubleze registrul.
    Cheia de identitate practică = (data_operatiune, tip, suma, explicatie, metoda). NU include
    'categorie' / 'document' — sunt reclasificabile de contabil, iar includerea lor ar sparge
    idempotența după reclasificare. 'tip' e inclus fiindcă aceeași sumă/dată/explicație pe sens
    opus (încasare vs plată) sunt operațiuni distincte, nu duplicate.
    """
    importate, sarite_duplicat, erori = 0, 0, []
    with conn.cursor() as cur:
        for op in operatiuni:
            try:
                cur.execute(
                    f"""SELECT 1 FROM {schema}.rip_operatiuni
                        WHERE data_operatiune=%s AND tip=%s AND suma=%s
                          AND explicatie=%s AND metoda=%s LIMIT 1""",
                    (op["data"], op["tip"], op["suma"], op["explicatie"], op["metoda"]),
                )
                if cur.fetchone():
                    sarite_duplicat += 1
                    continue
                cur.execute(
                    f"""INSERT INTO {schema}.rip_operatiuni
                        (data_operatiune, tip, explicatie, suma, valuta, metoda,
                         categorie, document_numar, status)
                        VALUES (%s, %s, %s, %s, 'RON', %s, %s, %s, 'validata')""",
                    (op["data"], op["tip"], op["explicatie"], op["suma"],
                     op["metoda"], op["categorie"], op.get("document_numar") or None),
                )
                importate += 1
            except Exception as e:
                erori.append({"op": op, "motiv": str(e)})
    if erori:
        conn.rollback()
        return {"importate": 0, "sarite_duplicat": 0, "erori": erori}
    conn.commit()
    return {"importate": importate, "sarite_duplicat": sarite_duplicat, "erori": []}


# NOTĂ status='validata': operațiunile preluate sunt evidența contabilului anterior,
# marcate ca istoric (nu ciornă de re-verificat manual una câte una). LIMITĂ, în spiritul
# control_incrucisat: preluarea NU certifică corectitudinea evidenței anterioare — la
# preluare se rulează F183 (audit de preluare) care raportează ce se poate/nu se poate
# verifica. RIP-ul preluat e punct de plecare, nu adevăr garantat.
