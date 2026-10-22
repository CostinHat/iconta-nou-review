"""
core/produse_api.py — nomenclatorul de produse per firma (schema tenant).
Cota TVA se potriveste automat cu AI (cote_tva.potriveste_cota) la prima
introducere a unei denumiri; apoi produsul e salvat si cota vine din nomenclator
(nu se mai intreaba AI). Un om poate confirma/corecta cota (control fiscal).
[R193, 10.10.2026] Modelul NU se intreaba de aici: functiile care primesc o conexiune primesc si
raspunsurile, cerute inainte de ea (`de_intrebat` -> `cote_tva.intreaba` -> `raspunsuri=`).

Conexiunea vine deja pe schema tenant (search_path setat de apelant).
"""
import unicodedata as _ud

from core import cote_tva


def cheie_denumire(x):
    """[lotul 11, deficiența 450] Cheia unei denumiri de articol / produs: „Grâu”, „grau”, „GRAU ” sunt același articol pentru om — fără
    deosebire de majuscule, de spațiile multiple și de diacritice (ă/â/î/ș/ş/ț/ţ și orice semn diacritic, prin descompunerea Unicode NFKD).
    O SINGURĂ definiție, în Python (nu o expresie SQL paralelă), folosită de borderou, de intrarea manuală în stoc și de nomenclator: la F1,
    borderoul a creat al doilea articol „grau” lângă cel existent (articolele 5 și 6, aceeași denumire)."""
    s = _ud.normalize("NFKD", str(x or ""))
    return " ".join("".join(ch for ch in s if not _ud.combining(ch)).split()).casefold()


def articol_dupa_denumire(cur, schema, denumire):
    """[450] Articolul de stoc existent cu aceeași cheie (`cheie_denumire`), cel mai vechi: (id, denumire, um) sau None. `schema` gol = schema
    din calea conexiunii."""
    k = cheie_denumire(denumire)
    if not k:
        return None
    p = ('"%s".' % schema) if schema else ""
    cur.execute("SELECT id, denumire, um FROM %sarticole ORDER BY id" % p)
    for r in cur.fetchall():
        r = r if isinstance(r, dict) else {"id": r[0], "denumire": r[1], "um": r[2]}
        if cheie_denumire(r["denumire"]) == k:
            return (r["id"], r["denumire"], r["um"])
    return None


def _produs_cu_cheia(cur, p, denumire):
    """[450] id-ul produsului cu aceeași cheie (`cheie_denumire`), cel mai vechi, sau None. `p` = prefixul schemei („"tenant_x".” sau gol)."""
    k = cheie_denumire(denumire)
    if not k:
        return None
    cur.execute("SELECT id, denumire FROM %sproduse ORDER BY id" % p)
    for r in cur.fetchall():
        rid, den = (r["id"], r["denumire"]) if isinstance(r, dict) else (r[0], r[1])
        if cheie_denumire(den) == k:
            return rid
    return None


#: [lotul 11, deficiența 449 — comanda Costin 11.1 pct.10, verbatim] „la cota TVA a produsului lipsesc taxarea inversă (art. 331), scutit cu drept
#: de deducere (art. 294) și neimpozabil.” Categoriile cotei 0% care țin de PRODUS (sursa: `core/categorii_tva.CATEGORII` — codul UBL, motivul,
#: rândul D300). Livrarea intracomunitară, exportul și prestarea cu locul în afara României țin de CLIENT (țara lui), nu de produs: le alege
#: factura, nu nomenclatorul.
CATEGORII_PRODUS = ("taxare_inversa", "scutit_cu_drept", "scutit_fara_drept", "in_afara_sferei")

#: [449] Cerealele și plantele tehnice (CF art.331 alin.(2) lit.c) se declară în D394 cu SUBCODUL NC, nu cu centralizatorul 21 („la op11 codul 21
#: NU e valid”, `d394.codpr_N_din_categorie`): produsul din nomenclator poartă codul NC al lui. Lista și denumirile, verbatim din HG 1/2016 pct.109
#: alin.(7) (`anaf_surse/hg_1_2016_norme_cod_fiscal.txt`): „Codurile NC aferente cerealelor, plantelor tehnice, semințelor oleaginoase și sfeclei
#: de zahăr, prevăzute la art. 331 alin. (2) lit. c), sunt următoarele”. Gard: aceleași coduri ca `d394.CODPR_CEREALE`.
NC_CEREALE = {"1001": "Grâu și meslin", "1002": "Secară", "1003": "Orz", "1004": "Ovăz", "1005": "Porumb", "10086000": "Triticale",
              "1201": "Boabe de soia, chiar sfărâmate", "120400": "Semințe de in, chiar sfărâmate",
              "1205": "Semințe de rapiță sau de rapiță sălbatică, chiar sfărâmate", "120600": "Semințe de floarea-soarelui, chiar sfărâmate",
              "121291": "Sfeclă de zahăr"}


def coduri_331():
    """[449] Bunul cu taxare inversă al unui produs: categoriile D394 (`d394.CODPR`), cu cerealele pe subcodul NC (`NC_CEREALE`) în locul
    centralizatorului „cereale” — {cod: (eticheta, codul din D394)}."""
    from core import d394 as _d394, taxare_inversa as _ti
    out = {}
    for k, v in _d394.CODPR.items():
        if k == "cereale":
            out.update({nc: ("Cereale: %s (NC %s)" % (den, nc), nc) for nc, den in NC_CEREALE.items()})
        else:
            out[k] = (_ti.CATEGORII[k]["eticheta"], v)   # [lotul 11] denumirea, nu cheia
    return out


def categorii_pentru_ecran():
    """[449] Lista din ecranul Produse: [{cod, eticheta}] pentru `CATEGORII_PRODUS`, cu eticheta din `categorii_tva` (sursa unică)."""
    from core import categorii_tva as _ct
    return [{"cod": c, "eticheta": _ct.CATEGORII[c]["eticheta"]} for c in CATEGORII_PRODUS]


def categorii_331_pentru_ecran():
    """[449] Bunurile cu taxare inversă (CF art.331 alin.(2)), cu codul lor din D394: [{cod, eticheta, cod_d394}]."""
    return [{"cod": k, "eticheta": e, "cod_d394": c} for k, (e, c) in coduri_331().items()]


def verifica_categoria(cota_tva, categorie_tva, categorie_331):
    """[449] Refuzul (text) sau None: categoria se alege numai la cota 0%, dintre `CATEGORII_PRODUS`; taxarea inversă (CF art.331 alin.(2))
    cere și categoria bunului din D394 (cereale, deșeuri, masă lemnoasă ...), fiindcă D394 o declară cu codul ei."""
    r = refuzul_categoriei(cota_tva, categorie_tva, categorie_331)
    return r[1] if r else None


def refuzul_categoriei(cota_tva, categorie_tva, categorie_331):
    """[440] Ca `verifica_categoria`, cu câmpul din ecranul Produse care poartă greșeala: (`pr-cota` — cota și categoria ei sunt aceeași
    listă — sau `pr-c331` — bunul cu taxare inversă, text) sau None."""
    from core import categorii_tva as _ct
    if categorie_tva in (None, ""):
        return ("pr-c331", "Categoria art.331 se alege numai la taxarea inversă.") if categorie_331 not in (None, "") else None
    if categorie_tva not in CATEGORII_PRODUS:
        return ("pr-cota", "Categoria %r nu e una din listă (%s)."
                % (categorie_tva, ", ".join(_ct.CATEGORII[c]["eticheta"] for c in CATEGORII_PRODUS)))
    if cota_tva is None or float(cota_tva) != 0:
        return ("pr-cota", "Categoria (%s) se alege numai la cota 0%%: o cotă de %s%% e o livrare taxabilă." % (
            _ct.CATEGORII[categorie_tva]["eticheta"], cota_tva))
    if categorie_tva == "taxare_inversa":
        if categorie_331 in (None, ""):
            return ("pr-c331", "La taxarea inversă (art.331) alege și categoria bunului (cereale, deșeuri, masă lemnoasă ...): D394 o "
                               "declară cu codul ei.")
        if categorie_331 not in coduri_331():
            return ("pr-c331", "Categoria bunului %r nu e una din D394; la cereale se alege codul NC al produsului (HG 1/2016 pct.109 "
                               "alin.(7)): %s." % (categorie_331, ", ".join(sorted(coduri_331()))))
    elif categorie_331 not in (None, ""):
        return ("pr-c331", "Categoria art.331 se alege numai la taxarea inversă.")
    return None


#: [440] Limitele coloanelor `produse` (LIMITE de structură a bazei, nu valori fiscale — `scan_constante.NOM`) (tenant_template.sql: `um character varying(10)`, `pret_unitar numeric(12,2)`). O valoare peste ele
#: nu se putea scrie: baza o refuza în INSERT / UPDATE (DataError -> 500, „eroare internă”), după ce restul formularului fusese judecat.
#: Acum se refuză lângă câmpul ei, împreună cu celelalte. Gard: `core/test_lot11_w3b_produse.py` (confruntă limitele cu schema).
LIMITE_UM = 10
LIMITE_PRET = 10 ** 10   # numeric(12,2): cel mult 10 cifre înaintea virgulei


def _erori_produs(er, denumire, um, pret_unitar, cere_denumirea):
    """[440] Denumirea, UM-ul și prețul produsului, judecate împreună (`core.erori.ErorileFormularului`), fiecare lângă câmpul ei din ecranul
    Produse (`pr-den`, `pr-um`, `pr-pret`). `cere_denumirea` = la creare denumirea e obligatorie; la editare, numai dacă e trimisă."""
    import math
    if (cere_denumirea or denumire is not None) and not str(denumire or "").strip():
        er.camp("pr-den", "Scrie denumirea produsului sau a serviciului.")
    if um is not None and len(str(um).strip()) > LIMITE_UM:
        from core.common import cate as _cate
        er.camp("pr-um", "Unitatea de măsură are cel mult %s (ex. buc, kg, ore, mp); „%s” are %d."
                % (_cate(LIMITE_UM, "caracter", "caractere"), str(um).strip(), len(str(um).strip())))
    if pret_unitar is not None:
        try:
            p = float(pret_unitar)
        except (TypeError, ValueError):
            p = None
        if p is None or not math.isfinite(p):
            er.camp("pr-pret", "Prețul %r nu e un număr." % (pret_unitar,))
        elif abs(p) >= LIMITE_PRET:
            er.camp("pr-pret", "Prețul are cel mult 10 cifre înaintea virgulei (sub 10.000.000.000 lei).")
    return er


def lista(conn, doar_confirmate=False):
    """Toate produsele firmei, ordonate alfabetic."""
    import psycopg2.extras as _E
    cond = " WHERE confirmat = true" if doar_confirmate else ""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, denumire, um, pret_unitar, cota_tva, categorie, categorie_tva, categorie_331, "
            "justificare, sursa, confirmat "
            "FROM produse" + cond + " ORDER BY lower(denumire)")
        out = []
        for r in cur.fetchall():
            d = dict(r)
            d["pret_unitar"] = float(d["pret_unitar"]) if d["pret_unitar"] is not None else 0.0
            # [R29 24.08.2026] NULL ramane NULL. Inainte: `else 21.0` - un produs fara cota
            # era prezentat ca 21%, pe o cale VIE (main.py:2513). Aceeasi clasa cu defaultul
            # din ecranul de NIR, dar in Python - clasa pe care R26 o declarase golita.
            d["cota_tva"] = float(d["cota_tva"]) if d["cota_tva"] is not None else None
            out.append(d)
        if not doar_confirmate:
            out = sorted(out + _din_stoc_fara_produs(cur), key=lambda x: (x["denumire"] or "").lower())
    return out


def _din_stoc_fara_produs(cur):
    """[lotul 10, deficiența 435 — comanda Costin 10.2 pct.5, verbatim] „la F1, Produse arată doar Marfa A și Marfa C. Marfa B (din NIR 3),
    Carte tehnica (din importul XML) și grâu (din borderou) sunt în stoc, dar lipsesc din nomenclator, iar cota Marfei B nu se poate
    completa nicăieri, deși factura trimite la Produse. Orice articol din stoc apare în nomenclator.”
    Cauza: nomenclatorul primea articolul numai când documentul de intrare avea cota (`asigura_din_document`, 415); fără cotă (borderoul,
    un NIR / import de dinainte de 415, importul de articole) articolul rămânea numai în stoc. Reparația ține de CITIRE, deci acoperă orice
    drum, de azi și de mâine: fiecare articol din stoc (`articole`) fără produs cu aceeași denumire apare în listă „cotă lipsă”, iar cota
    aleasă pe rând îl scrie în nomenclator (POST /produse, cu cota). Cota nu se ghicește: rândul vine fără cotă (`cota_tva` None).
    [lotul 11, 450] „aceeași denumire” = aceeași `cheie_denumire` (și fără diacritice), ca la borderou și la intrarea în stoc."""
    cur.execute("SELECT denumire FROM produse")
    vazute = {cheie_denumire(r["denumire"]) for r in cur.fetchall()}
    cur.execute("SELECT a.id AS articol_id, a.denumire, a.um FROM articole a ORDER BY lower(a.denumire), a.id")
    out = []
    for r in cur.fetchall():
        cheie = cheie_denumire(r["denumire"])
        if not cheie or cheie in vazute:
            continue
        vazute.add(cheie)
        out.append({"id": None, "articol_id": r["articol_id"], "denumire": " ".join(str(r["denumire"]).split()), "um": r["um"] or "buc",
                    "pret_unitar": 0.0, "cota_tva": None, "categorie": None, "categorie_tva": None, "categorie_331": None,
                    "justificare": None, "sursa": "stoc", "confirmat": False, "din_stoc": True})
    return out


def cauta_dupa_denumire(conn, denumire):
    """Cauta un produs existent dupa denumire (case-insensitive). Intoarce dict sau None.
    [lotul 11, 450] aceeași denumire = aceeași `cheie_denumire` (și fără diacritice: „grau” găsește „Grâu”)."""
    import psycopg2.extras as _E
    d = (denumire or "").strip()
    if not d:
        return None
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        pid = _produs_cu_cheia(cur, "", d)
        if pid is None:
            return None
        cur.execute(
            "SELECT id, denumire, um, pret_unitar, cota_tva, categorie, categorie_tva, categorie_331, "
            "justificare, sursa, confirmat "
            "FROM produse WHERE id = %s", (pid,))
        r = cur.fetchone()
    if not r:
        return None
    out = dict(r)
    out["pret_unitar"] = float(out["pret_unitar"] or 0)
    if out["cota_tva"] is None:
        # produs incomplet in nomenclator: NU se ghiceste 21 (baza nula). 0 (scutit) NU e None.
        raise ValueError("produs fără cota TVA în nomenclator: %r" % out.get("denumire"))
    out["cota_tva"] = float(out["cota_tva"])
    return out


def propunere_pentru_linie(conn, denumire, platitor_tva=True, raspunsuri=None):
    """[comanda Costin 05.10.2026 pct.9] Ce se propune pe o linie de factură când se scrie denumirea: produsul din NOMENCLATORUL
    firmei, dacă există (cota, UM, prețul), altfel cota din potrivirea automată. Înainte, linia întreba doar cota (AI), iar
    prețul și UM din nomenclator nu se precompletau. Neplătitorul primește cota 0 (CF art.310 alin.(10) lit.b), iar prețul și
    UM tot din nomenclator."""
    p = cauta_dupa_denumire(conn, denumire)
    if not p:
        return cote_tva.raspuns(raspunsuri, denumire, platitor_tva)
    cota = p["cota_tva"] if platitor_tva else 0
    # [lotul 11, 449] categoria cotei 0% a produsului (taxare inversă / scutit cu sau fără drept / neimpozabil) și, la taxarea inversă,
    # categoria bunului din D394: factura le propune pe linie (`categorie_tva`) și pe document (`categorie_331`). La neplătitor nu se
    # propune nimic: categoria lui („neplătitor”, O) o pune automat regimul firmei (`categorii_tva.verifica_linii`).
    return {"ok": True, "cota": int(cota) if float(cota).is_integer() else cota, "categorie": p.get("categorie"),
            "categorie_tva": p.get("categorie_tva") if platitor_tva else None,
            "categorie_331": p.get("categorie_331") if platitor_tva else None,
            "justificare": p.get("justificare"), "sursa": "nomenclator", "produs_id": p["id"],
            "um": p.get("um"), "pret_unitar": p["pret_unitar"]}


def de_intrebat(conn, denumire, cota_tva=None):
    """[R193] Faza de citire: denumirea pentru care `creeaza` / `propunere_pentru_linie` vor avea nevoie de răspunsul modelului —
    produsul fără cotă dată și absent din nomenclator. Întrebarea se pune apoi cu pool-ul liber (`cote_tva.intreaba`)."""
    d = (denumire or "").strip()
    return [d] if d and cota_tva is None and not cauta_dupa_denumire(conn, d) else []


def creeaza(conn, denumire, um="buc", pret_unitar=0, cota_tva=None,
            categorie=None, justificare=None, sursa="manual",
            confirmat=False, platitor_tva=True, raspunsuri=None, categorie_tva=None, categorie_331=None):
    """
    Creeaza un produs in nomenclator. Daca cota_tva nu e data, o ia din `raspunsuri` (modelul, intrebat inaintea conexiunii).
    Daca produsul exista deja (aceeasi denumire), intoarce cel existent (nu dubleaza).
    Intoarce {ok, id, denumire, cota_tva, categorie, justificare, sursa, confirmat, existent}.
    [lotul 11, 449] `categorie_tva` (categoria cotei 0%, `CATEGORII_PRODUS`) și `categorie_331` (bunul cu taxare inversă, codul D394) se
    verifică împreună cu cota (`verifica_categoria`): refuzul e {ok: False, cod: "CATEGORIE_TVA", mesaj}, nimic scris.
    """
    d = (denumire or "").strip()
    categorie_tva = (categorie_tva or "").strip() or None
    categorie_331 = (categorie_331 or "").strip() or None
    # [440, comanda Costin 11.1 pct.16] denumirea, UM-ul, prețul și categoria cotei aleasă se judecă toate deodată; înainte, denumirea
    # lipsă oprea tot („denumire lipsă”), iar un UM / preț peste coloană cădea în INSERT (500)
    from core.erori import ErorileFormularului as _Erori
    er = _erori_produs(_Erori("Produsul nu s-a salvat"), d, um, pret_unitar, cere_denumirea=True)
    _rc = refuzul_categoriei(cota_tva, categorie_tva, categorie_331) if cota_tva is not None else None
    if _rc:
        er.camp(*_rc)
    if er:
        return dict(er.detaliu(), ok=False, cod="GOL" if not d else ("CATEGORIE_TVA" if _rc else "DATE_INVALIDE"))

    existent = cauta_dupa_denumire(conn, d)
    if existent:
        existent["existent"] = True
        existent["ok"] = True
        return existent

    # daca nu s-a dat cota, o luam din raspunsul modelului, cerut INAINTEA conexiunii (`de_intrebat` + `cote_tva.intreaba`, R193)
    sursa_finala = sursa
    if cota_tva is None:
        rez = cote_tva.raspuns(raspunsuri, d, platitor_tva)
        if rez.get("cota") is None:
            # auto-match esuat: NU salvam un produs cu cota ghicita -> NEDETERMINAT (baza nula).
            # (0 = scutit/neplatitor NU e None -> se salveaza normal)
            return {"ok": False, "cod": "NEDETERMINAT", "denumire": d,
                    "mesaj": rez.get("justificare") or "cota TVA nedeterminată"}
        cota_tva = rez["cota"]
        categorie = categorie or rez.get("categorie")
        justificare = justificare or rez.get("justificare")
        sursa_finala = rez.get("sursa", "ai")
    refuz = verifica_categoria(cota_tva, categorie_tva, categorie_331)
    if refuz:
        return {"ok": False, "cod": "CATEGORIE_TVA", "mesaj": refuz, "denumire": d}

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO produse (denumire, um, pret_unitar, cota_tva, categorie, categorie_tva, categorie_331, "
            "justificare, sursa, confirmat) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (d, um or "buc", pret_unitar or 0, cota_tva, categorie, categorie_tva, categorie_331,
             justificare, sursa_finala, bool(confirmat)))
        pid = cur.fetchone()[0]

    return {"ok": True, "id": pid, "denumire": d, "um": um or "buc",
            "pret_unitar": float(pret_unitar or 0), "cota_tva": float(cota_tva),
            "categorie": categorie, "categorie_tva": categorie_tva, "categorie_331": categorie_331, "justificare": justificare,
            "sursa": sursa_finala, "confirmat": bool(confirmat), "existent": False}


def asigura_din_document(cur, schema, denumire, um, cota_tva, document):
    """[deficiența 415, retestul Costin 19.10.2026] „Articol creat din NIR («+ articol nou», Marfa B, cotă 21%) rămâne fără cotă; preia
    cota de pe rândul NIR.” Articolul de stoc își ia cota din nomenclatorul Produse (aceeași denumire, `cauta_dupa_denumire`): când
    un document (NIR, factura primită) creează articolul, nomenclatorul primește cota aleasă pe rândul documentului — dacă denumirea
    nu e deja acolo (un produs existent nu se schimbă pe tăcute). Cota a ales-o omul pe document, deci produsul e confirmat."""
    from decimal import Decimal
    d = " ".join(str(denumire or "").split())
    if not d or cota_tva is None:
        return None
    # [lotul 11, 450] „denumirea e deja acolo” = aceeași `cheie_denumire` (și fără diacritice)
    if _produs_cu_cheia(cur, schema + ".", d) is not None:
        return None
    cur.execute(f"""INSERT INTO {schema}.produse (denumire, um, pret_unitar, cota_tva, justificare, sursa, confirmat)
                    VALUES (%s, %s, 0, %s, %s, 'document', true) RETURNING id""",
                (d, um or "buc", Decimal(str(cota_tva)), ("cota de pe " + str(document or "documentul de intrare"))[:500]))
    r = cur.fetchone()
    return (r["id"] if isinstance(r, dict) else r[0]) if r else None


def actualizeaza(conn, produs_id, denumire=None, um=None, pret_unitar=None,
                 cota_tva=None, categorie=None, confirmat=None, categorie_tva=None, categorie_331=None):
    """Actualizeaza campurile date ale unui produs. Daca se schimba cota manual,
    sursa devine 'manual'. Intoarce {ok} sau {ok:False}.
    [lotul 11, 449] `categorie_tva` / `categorie_331`: None = neschimbat, "" = golit. Se verifică pe starea REZULTATĂ
    (cota nouă sau cea existentă): o cotă nenulă golește categoria cotei 0%, dacă nu s-a cerut alta (care atunci se refuză)."""
    with conn.cursor() as cur:
        cur.execute("SELECT cota_tva, categorie_tva, categorie_331 FROM produse WHERE id = %s", (produs_id,))
        vechi = cur.fetchone()
    if not vechi:
        return {"ok": False, "id": produs_id}
    # [440] denumirea golită, UM-ul / prețul peste coloană și categoria cotei, toate deodată (`ErorileFormularului`); înainte, denumirea
    # golită se scria goală, iar UM-ul / prețul lung cădeau în UPDATE (500)
    from core.erori import ErorileFormularului as _Erori
    er = _erori_produs(_Erori("Produsul nu s-a salvat"), denumire, um, pret_unitar, cere_denumirea=False)
    seturi, val = [], []
    if denumire is not None:
        seturi.append("denumire = %s"); val.append(denumire.strip())
    if um is not None:
        seturi.append("um = %s"); val.append(um)
    if pret_unitar is not None:
        seturi.append("pret_unitar = %s"); val.append(pret_unitar)
    if cota_tva is not None:
        seturi.append("cota_tva = %s"); val.append(cota_tva)
        seturi.append("sursa = 'manual'")  # corectat de om
    if categorie is not None:
        seturi.append("categorie = %s"); val.append(categorie)
    if confirmat is not None:
        seturi.append("confirmat = %s"); val.append(bool(confirmat))
    cota_noua = cota_tva if cota_tva is not None else vechi[0]
    if categorie_tva is not None or categorie_331 is not None or cota_tva is not None:
        cat = (categorie_tva.strip() or None) if categorie_tva is not None else (
            None if cota_tva is not None and float(cota_tva) != 0 else vechi[1])
        c331 = (categorie_331.strip() or None) if categorie_331 is not None else (vechi[2] if cat == "taxare_inversa" else None)
        refuz = refuzul_categoriei(cota_noua, cat, c331)
        if refuz:
            er.camp(*refuz)
        seturi.append("categorie_tva = %s"); val.append(cat)
        seturi.append("categorie_331 = %s"); val.append(c331)
    if er:
        # `cod` CATEGORIE_TVA rămâne al refuzului categoriei (contractul 449); restul = date invalide
        _cod = "CATEGORIE_TVA" if any(c["camp"] in ("pr-cota", "pr-c331") for c in er.campuri) else "DATE_INVALIDE"
        return dict(er.detaliu(), ok=False, cod=_cod, id=produs_id)
    if not seturi:
        return {"ok": False, "cod": "NIMIC", "mesaj": "nimic de actualizat"}
    val.append(produs_id)
    with conn.cursor() as cur:
        cur.execute("UPDATE produse SET " + ", ".join(seturi) + " WHERE id = %s", val)
        afectate = cur.rowcount
    return {"ok": afectate > 0, "id": produs_id}


def sterge(conn, produs_id):
    """Sterge un produs din nomenclator."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM produse WHERE id = %s", (produs_id,))
        afectate = cur.rowcount
    return {"ok": afectate > 0}
