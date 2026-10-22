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
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from core.solduri_api import _numar
# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Citirea fișierului și potrivirea coloanelor trec prin
# `core.import_tabel` (sursa unică: format, codare Windows-1250 recunoscută sau refuzată, antet sub titluri, coloane pe cuvinte
# întregi, ambiguitate refuzată numit) — nu mai e o copie a lui `_gaseste_col` aici.
from core import import_tabel as _it
from core.migrare_api import respinge, semnaleaza  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator
from core.pdf_util import data_ro as _data_ro   # DS cap.4: data din text, canonic


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
    """Normalizează metoda la numerar/banca (valorile din CHECK-ul DB, ca rip_api.py); None dacă e goală sau necunoscută.
    [372] Goală -> rândul intră prin bancă, cu semnalul pe rând (`metoda_plata_lipsa`); necunoscută -> rândul se respinge."""
    t = str(v or "").strip().lower()
    if "cas" in t or "numerar" in t or "cash" in t:
        return "numerar"
    if "banc" in t or "cont" in t or "virament" in t or "card" in t:
        return "banca"
    return None


CAMPURI = {
    "data": ("data operatiunii", "data operatiune", "=data", "data*"),
    "tip": ("tip operatiune", "=tip", "fel", "sens"),
    "explicatie": ("explicatie", "explicatii", "explica*", "descriere", "descrie*", "detalii"),
    "suma": ("=suma", "suma*", "valoare", "incasari", "plati"),
    "categorie": ("categorie", "categor*"),
    "metoda": ("metoda*", "=cont", "mod*"),
    "document": ("document*", "factura*", "chitanta*"),
}
#: [lotul 11] numele câmpului în refuzul coloanelor ambigue (`import_tabel.coloana`), în limba contabilului — nu cheia internă
#: (garda: core/test_lot11_import_etichete_camp.py)
ETICHETE_CAMP = {
    "data": "data operațiunii",
    "tip": "tipul operațiunii",
    "explicatie": "explicația",
    "suma": "suma operațiunii",
    "categorie": "categoria",
    "metoda": "metoda de plată",
    "document": "documentul",
}


def extrage(continut, nume_fisier=""):
    """Fiecare rând citit din registru, CU valorile din fișier (`*_brut`) lângă cele interpretate (None = neînțeles):
    [{rand_fisier, data, data_brut, tip, tip_brut, explicatie, suma, suma_brut, metoda, metoda_brut, categorie, document_numar}].

    [372, comanda Costin 8.2] Nimic nu se mai respinge și nu se mai scrie aici: până azi rândurile bune se scriau direct (fără
    previzualizare), iar data se trimitea ca TEXT la baza de date — „2026-13-01” oprea importul cu eroarea brută a Postgres-ului pe
    ecran. Acum data se interpretează aici (`import_tabel.data`), verdictul e al lui `verifica_randuri` (aceeași poartă la
    previzualizare și la salvare), iar ce se completează din oficiu e spus pe rând (`semnale_randuri`)."""
    # numerotarea e cea din FIȘIER: rândurile goale nu se scot înainte (un rând gol deasupra muta „rândul N” pe altul — găsit de garda
    # `core/test_regula_importurilor.py`), se sar în buclă
    randuri = _it.citeste(continut, nume_fisier)
    if not randuri or all(_it.rand_gol(r) for r in randuri):
        return []
    antet, start = _it.gaseste_antet(randuri, CAMPURI, obligatorii=("data",), nume_fisier=nume_fisier)
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=ETICHETE_CAMP[camp])
    i_data = col("data")
    i_tip  = col("tip", (i_data,))
    i_expl = col("explicatie")
    i_suma = col("suma")
    i_cat  = col("categorie")
    i_met  = col("metoda")
    i_doc  = col("document", (i_data,))
    randuri = randuri[start - 1:]          # randuri[0] = antetul, ca numerotarea de mai jos să rămână cea din fișier

    out = []
    for nr, rand in enumerate(randuri[1:], start=start + 1):
        if _it.rand_gol(rand):
            continue
        cel = lambda i: _it.celula(rand, i)
        suma_brut = cel(i_suma)
        try:
            suma = str(_bani(_numar(suma_brut, strict=True))) if suma_brut else None
        except (ValueError, ArithmeticError):
            suma = None
        out.append({
            "rand_fisier": nr,
            "data": _it.data(_it.valoare(rand, i_data)) if i_data >= 0 else None,
            "data_brut": cel(i_data),
            "tip": _norm_tip(cel(i_tip)) if i_tip >= 0 else None,
            "tip_brut": cel(i_tip),
            "explicatie": cel(i_expl),
            "suma": suma,
            "suma_brut": suma_brut,
            "metoda": _norm_metoda(cel(i_met)) if i_met >= 0 else None,
            "metoda_brut": cel(i_met),
            "categorie": cel(i_cat),
            "document_numar": cel(i_doc),
        })
    return out


def verifica_randuri(randuri, azi=None):
    """PURĂ: respingerile [{rand, motiv, mesaj}] — rândurile care NU intră. Aceeași poartă la previzualizare și la salvare."""
    import datetime as _dt
    azi = azi or _dt.date.today()
    er = []
    for i, r in enumerate(randuri or [], start=2):
        i = _it.nr_rand(r, i)
        brut = str(r.get("data_brut") or "").strip()
        d = r.get("data")
        if not d:
            if brut:
                er.append(respinge("operațiune RIP", i, "data_invalida",
                                   "data «%s» nu e o dată (ZZ.LL.AAAA sau AAAA-LL-ZZ)" % brut))
            else:
                er.append(respinge("operațiune RIP", i, "data_lipsa", "lipsă dată operațiune"))
        else:
            try:
                dd = _dt.date.fromisoformat(str(d)[:10])
            except ValueError:
                dd = None
                er.append(respinge("operațiune RIP", i, "data_invalida", "data «%s» nu e o dată" % (brut or d)))
            if dd is not None and dd > azi:
                er.append(respinge("operațiune RIP", i, "data_viitor",
                                   "data %s e în viitor — registrul preluat are numai operațiuni petrecute" % _data_ro(dd)))
        if r.get("tip") not in TIPURI:
            er.append(respinge("operațiune RIP", i, "tip_necunoscut",
                               "tipul operațiunii «%s» nu e încasare sau plată" % (r.get("tip_brut") or "")))
        if not str(r.get("explicatie") or "").strip():
            er.append(respinge("operațiune RIP", i, "explicatie_lipsa",
                               "lipsă explicație - coloana e obligatorie în registru"))
        try:
            suma = Decimal(str(r.get("suma"))) if r.get("suma") not in (None, "") else None
        except ArithmeticError:
            suma = None
        if suma is None or suma == 0:
            er.append(respinge("operațiune RIP", i, "suma_invalida",
                               "suma «%s» e 0 sau nu e un număr" % (r.get("suma_brut") or "")))
        if str(r.get("metoda_brut") or "").strip() and r.get("metoda") not in METODE:
            er.append(respinge("operațiune RIP", i, "metoda_plata_necunoscuta",
                               "metoda «%s» nu e bancă sau numerar" % r.get("metoda_brut")))
    return er


def semnale_randuri(randuri):
    """PURĂ: [comanda Costin 8.2 pct.4] ce se completează din oficiu pe un rând care intră e spus pe rând, nu numai numărat."""
    out = []
    for i, r in enumerate(randuri or [], start=2):
        i = _it.nr_rand(r, i)
        if not str(r.get("metoda_brut") or "").strip():
            out.append(semnaleaza("operațiune RIP", i, "metoda_plata_lipsa",
                                  "metoda lipsește — intră ca operațiune prin bancă; dacă a fost cu numerar, corectează în fișier"))
        if not str(r.get("categorie") or "").strip():
            out.append(semnaleaza("operațiune RIP", i, "categorie_lipsa",
                                  "categoria lipsește — intră „neclasificat”; o alegi în Registrul de încasări și plăți"))
        try:
            negativa = r.get("suma") not in (None, "") and Decimal(str(r.get("suma"))) < 0
        except ArithmeticError:
            negativa = False
        if negativa:
            out.append(semnaleaza("operațiune RIP", i, "suma_negativa_rip",
                                  "suma e negativă — intră cu valoarea ei absolută; sensul îl dă tipul (%s)" % (r.get("tip") or "?")))
    return out


def eticheteaza(randuri, azi=None):
    """[comanda Costin 8.2 pct.4] Starea fiecărui rând (ok / semnalat / respins), cu motivele, din aceleași două verificări."""
    er, sem = verifica_randuri(randuri, azi), semnale_randuri(randuri)
    for i, r in enumerate(randuri, start=2):
        n = _it.nr_rand(r, i)
        resp = [e["mesaj"] for e in er if e.get("rand") == n]
        obs = [e["mesaj"] for e in sem if e.get("rand") == n]
        r["stare"] = "respins" if resp else ("semnalat" if obs else "ok")
        r["motive"] = resp or obs
    return randuri


def _operatiune(r):
    """Rândul bun -> operațiunea scrisă: suma pozitivă (sensul îl dă tipul), metoda și categoria cele semnalate când lipsesc."""
    return {"data": r["data"], "tip": r["tip"], "explicatie": str(r["explicatie"]).strip(),
            "suma": str(abs(Decimal(str(r["suma"])))), "metoda": r.get("metoda") or "banca",
            "categorie": str(r.get("categorie") or "").strip() or "neclasificat",
            "document_numar": str(r.get("document_numar") or "").strip()}


def importa(conn, schema, randuri, azi=None):
    """
    Scrie rândurile BUNE (cele pe care `verifica_randuri` nu le respinge) în {schema}.rip_operatiuni cu status='validata' (istoric
    preluat). Întoarce {importate, sarite_duplicat, respinse}. Ridică ValueError dacă niciun rând nu poate intra.

    Idempotent la reimport: o operațiune identică ce EXISTĂ deja se sare (nu e eroare, doar
    exclusă din importate) — ca reimportul repetat al aceluiași fișier să nu dubleze registrul.
    Cheia de identitate practică = (data_operatiune, tip, suma, explicatie, metoda). NU include
    'categorie' / 'document' — sunt reclasificabile de contabil, iar includerea lor ar sparge
    idempotența după reclasificare. 'tip' e inclus fiindcă aceeași sumă/dată/explicație pe sens
    opus (încasare vs plată) sunt operațiuni distincte, nu duplicate.

    [372] O eroare a bazei de date nu mai ajunge la contabil ca text brut: datele care o puteau provoca se resping înainte, iar
    o eroare rămasă e o eroare INTERNĂ (urcă la apelant; tranzacția apelantului o anulează, nimic nu rămâne scris).
    """
    if not randuri:
        raise ValueError("nu ai trimis niciun rând — un import fără rânduri n-are ce adăuga în registru.")
    er = verifica_randuri(randuri, azi)
    respinse_idx = {e["rand"] for e in er}
    bune = [r for i, r in enumerate(randuri, start=2) if _it.nr_rand(r, i) not in respinse_idx]
    if not bune:
        raise ValueError("niciun rând nu poate intra: %s" % "; ".join("rândul %s: %s" % (e["rand"], e["mesaj"]) for e in er[:6]))
    importate, sarite_duplicat = 0, 0
    with conn.cursor() as cur:
        for op in map(_operatiune, bune):
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
    return {"importate": importate, "sarite_duplicat": sarite_duplicat, "respinse": er}


# NOTĂ status='validata': operațiunile preluate sunt evidența contabilului anterior,
# marcate ca istoric (nu ciornă de re-verificat manual una câte una). LIMITĂ, în spiritul
# control_incrucisat: preluarea NU certifică corectitudinea evidenței anterioare — la
# preluare se rulează F183 (audit de preluare) care raportează ce se poate/nu se poate
# verifica. RIP-ul preluat e punct de plecare, nu adevăr garantat.
