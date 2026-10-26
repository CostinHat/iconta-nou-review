# -*- coding: utf-8 -*-
"""CONTAREA UNEI FACTURI — un adevăr, un loc (P1).

DE CE EXISTĂ CA MODUL (29.08.2026, blocurile DDD/EEE/FFF). Până azi, generarea notei dintr-o factură
trăia **în corpul rutei** `main.factura_contabilizeaza`, iar mecanismul anti-dublare era un
`SELECT COUNT(*) FROM inregistrari WHERE factura_id=%s`. Decizia lui Costin — *aplicația
contabilizează automat orice fapt economic nou construit* (R36, varianta (a)) — cere ca aceeași
generare să pornească din **trei** locuri: la emitere, la validarea unei facturi primite, și din ruta
manuală. Trei copii ar fi dat trei răspunsuri la prima divergență.

CE REPARĂ, ȘI E MĂSURAT ÎNAINTE (blocul BBB, `CONFORMITATE.md` R87): cheia `factura_id` greșea în
**amândouă** direcțiile.
  * **fals-negativ** — o notă scrisă din jurnalul liber nu poartă `factura_id`, deci e invizibilă
    pentru verificare, iar automatul ar scrie a doua notă peste ea. Plasa e `candidate_fara_cheie`;
    reparația la sursă e `leaga_nota_de_factura`, chemată din `jurnal_api.creeaza`.
  * **fals-pozitiv** — o notă de **PLATĂ** poartă și ea `factura_id` (reconcilierea bancară scrie
    `401 = 5121` pe factura plătită), iar `COUNT(*)` o citea ca pe o contare. **3 facturi** măsurate
    pe portofoliul de azi ar fi fost refuzate cu mesajul *„factura are deja înregistrare"* — care ar
    fi fost fals. Reparația e `contare_existenta`: se întreabă dacă există o notă **de contare**, nu
    dacă există o notă.

CE E O NOTĂ DE CONTARE, ca definiție mecanică și singură: atinge un cont de **terț** (4111 · 401 ·
404) **și** un cont de **fond** sau de **TVA**. O notă de plată atinge terțul și trezoreria (5121,
5311), deci nu trece. O notă de casă (`5311 = 707`) atinge fondul, dar nu terțul, deci nu trece.
*Definiția stă aici, nu în sonde: sondele o importă de aici, ca să nu existe două.*

CE NU FACE, DECLARAT:
  * nu decide dacă factura **trebuia** contabilizată în luna aia — spune doar dacă e sau nu în evidență;
  * nu vede o factură contată manual pe `461`/`462` — conturile alea nu sunt scrise de niciun drum
    factură→notă din cod, iar includerea lor ar trage în clasă operațiuni care nu sunt facturi;
  * nu atinge **starea** notei: intră `ciorna`, ca la NIR. Patru-ochi rămâne unde e (R47).
"""
from decimal import Decimal

from psycopg2.extras import RealDictCursor

from core import afirmatii as _af
from core import eticheta_nota as _et
from core import facturi as _fc
from core import nomenclator_status_factura as _nsf
from core.common import _q

# ── Conturile care fac o notă „de factură". Măsurate, nu presupuse — vezi BLOC BBB.
CONTURI_TERT = ("4111", "401", "404")
CONTURI_TVA = ("4426", "4427", "4428")
#: [lotul 6, 278] avansul încasat de la client (OMFP 1802/2014, funcțiunea contului 419) — contul facturii de avans
CONT_AVANS_CLIENT = "419"
CONTURI_FOND_PREFIX = ("70", "6")
CONTURI_FOND_EXACT = ("371", "301", "302", "303", "213", CONT_AVANS_CLIENT)   # [lotul 6, 278] 4111 = 419 (avans la cota 0)
# [29.08.2026, BLOC GGG] Trezoreria TAIE semnătura de contare, și motivul e măsurat prin citirea
# codului, nu presupus: încasarea / plata unei facturi în sistemul TVA la încasare (bancă — `reconciliere_api`, casă — `casa_api`,
# prin punctul unic `tva_incasare.linii_la_incasare`) adaugă pe nota ei o linie `4428 = 4427` (emisă) sau `4426 = 4428` (primită) —
# art. 282 alin. 3 și 8, art. 297 alin. 2-3. Nota devine atunci
# **terț + TVA**, adică exact semnătura de contare. Fără regula asta, fals-pozitivul închis la DDD1
# s-ar fi întors pe altă ușă: o factură plătită de o firmă la încasare ar fi părut deja contată.
# **Clasa e LATENTĂ azi** — nicio firmă din portofoliu nu e în regim de TVA la încasare, deci n-are
# nicio instanță vie. Se repară pe CLASĂ, nu pe instanță; calibrarea o construiește sintetic.
# O contare de factură nu atinge NICIODATĂ trezoreria: 4111 = venit, 4111 = 4427.
CONTURI_TREZORERIE = ("51", "53")


def egale(a, b):
    """Două sume sunt egale dacă sunt egale **în unitatea în care se scriu**: banul.

    N-are prag propriu, și e deliberat. Un `abs(a-b) <= 0.01` scris aici ar fi fost o a doua
    definiție a preciziei, alături de `numeric(12,2)` din schemă și de `common._q`, cu care
    `core/facturi.py` cuantizează chiar sumele astea. Trei definiții, trei răspunsuri la prima
    divergență."""
    return _q(Decimal(str(a or 0))) == _q(Decimal(str(b or 0)))


class RefuzContare(Exception):
    """Un refuz DECLARAT, nu o eroare.

    POARTĂ MOTIVUL CA DATE — `cod`, `mesaj`, `detalii` —, nu doar în text. Un apelant care ar
    distinge felurile de refuz căutând un șir în mesaj ar păzi formularea, nu comportamentul
    (clichetul 50 / METODA §23).

    Felurile: `INEXISTENTA` · `NU_E_DOCUMENT_FISCAL` · `LUNA_INCHISA` · `FARA_COTA` ·
    `POSIBILA_DUBLARE` · `FACTURA_EMISA` (regula a, R6: nu se șterge, se stornează) · `EMISA_DIN_BON` (factura din bon: vânzarea e în nota Z) ·
    `NIR_DE_LEGAT` / `NIR_NELEGABIL` / `COST_DIFERIT_DE_FACTURA` (NIR-ul „fără factură” al livrării, decizia 08.10 pct.2).
    """

    def __init__(self, cod, mesaj, detalii=None):
        super().__init__(mesaj)
        self.cod = cod
        self.mesaj = mesaj
        self.detalii = detalii or {}


# ══════════════════════════════════════════════ CLASIFICAREA CONTURILOR ȘI A NOTEI
def e_cont_tert(c):
    return any(str(c or "").startswith(p) for p in CONTURI_TERT)


def e_cont_tva(c):
    return any(str(c or "").startswith(p) for p in CONTURI_TVA)


def e_cont_fond(c):
    s = str(c or "")
    return (any(s.startswith(p) for p in CONTURI_FOND_PREFIX)
            or any(s.startswith(p) for p in CONTURI_FOND_EXACT))


def e_cont_trezorerie(c):
    return any(str(c or "").startswith(p) for p in CONTURI_TREZORERIE)


def e_nota_de_contare(linii):
    """`linii` = [(cont_debit, cont_credit, suma), ...]. Terț ȘI (fond SAU TVA) ȘI **fără trezorerie**.

    Direcția inversă contează la fel de mult: o notă de PLATĂ (`401 = 5121`) atinge terțul și
    trezoreria, deci **nu** e contare — și tocmai de-aia `COUNT(*)` greșea.

    A treia condiție — **fără trezorerie** — nu e prudență, e o clasă măsurată prin citirea codului:
    la o firmă cu TVA la încasare, `reconciliere_api` adaugă pe nota de plată linia de exigibilitate
    (`4428 = 4427` / `4426 = 4428`), iar nota devine terț + TVA. Fără ea, o factură plătită ar fi
    părut contată. *Latentă azi; reparată pe clasă.*"""
    tert = tva = fond = trez = False
    for cd, cc, _s in linii:
        for c in (cd, cc):
            if e_cont_tert(c):
                tert = True
            if e_cont_tva(c):
                tva = True
            if e_cont_fond(c):
                fond = True
            if e_cont_trezorerie(c):
                trez = True
    return tert and (tva or fond) and not trez


def valoare_pe_tert(linii):
    """Totalul facturii, dacă nota e o contare: pe emisă terțul se DEBITEAZĂ (4111 = venit,
    4111 = 4427), pe primită se CREDITEAZĂ (cheltuială = 401, 4426 = 401)."""
    s = Decimal(0)
    for cd, cc, suma in linii:
        if (str(cd or "").startswith("4111")
                or str(cc or "").startswith("401") or str(cc or "").startswith("404")):
            s += Decimal(str(suma or 0))
    return s


# ══════════════════════════════════════════════════════════════════════ AJUTOARE DB
def _p(schema):
    """Prefixul de schemă. Modulul e chemat din două convenții: rutele de facturi lucrează pe
    `db.get_conn(schema)` (search_path fixat, nume necalificate), cele din `main.py` pe
    `db.get_conn()` cu nume calificate. Un singur cod, amândouă convențiile."""
    return ("%s." % schema) if schema else ""


def luna_blocata(cur, schema, data):
    """True dacă luna datei e blocată. **Definiția lui «lună blocată» stă aici**, iar
    `main._perioada_blocata` o cheamă — altfel ar fi fost două."""
    if not data:
        return False
    d = str(data)[:10]
    cur.execute("SELECT 1 FROM %sperioade_blocate WHERE an=%%s AND luna=%%s" % _p(schema),
                (int(d[:4]), int(d[5:7])))
    return cur.fetchone() is not None


def note_pe_facturi(cur, schema, factura_ids):
    """{factura_id: [note]} — toate notele care poartă una din chei, cu liniile lor și cu verdictul „e contare?". O singură
    interogare pentru o listă întreagă de facturi (lista de facturi o folosește pe pagină)."""
    ids = [int(x) for x in factura_ids]
    if not ids:
        return {}
    cur.execute("SELECT i.factura_id, i.id, i.status, i.sursa, i.data, l.cont_debit, l.cont_credit, l.suma "
                "FROM %sinregistrari i "
                "LEFT JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                "WHERE i.factura_id = ANY(%%s) ORDER BY i.id, l.id"
                % (_p(schema), _p(schema)), (ids,))
    pe, note = {}, {}
    for r in cur.fetchall():
        fid, nid, status, sursa, data, cd, cc, suma = (
            (r["factura_id"], r["id"], r["status"], r["sursa"], r["data"], r["cont_debit"], r["cont_credit"], r["suma"])
            if isinstance(r, dict) else r)
        n = note.get(nid)
        if n is None:
            n = note[nid] = {"id": nid, "status": status, "sursa": sursa, "data": data, "linii": []}
            pe.setdefault(fid, []).append(n)
        if cd is not None:
            n["linii"].append((cd, cc, Decimal(str(suma or 0))))
    for n in note.values():
        n["e_contare"] = e_nota_de_contare(n["linii"])
    return pe


def note_cu_cheia(cur, schema, factura_id):
    """Toate notele care poartă `factura_id`, cu liniile lor și cu verdictul „e contare?"."""
    return note_pe_facturi(cur, schema, [factura_id]).get(int(factura_id), [])


def stare_contare(cur, schema, factura_ids):
    """[05.10.2026, comanda Costin pct.7] {factura_id: {"id", "status", "data"} | None} — nota de CONTARE a fiecărei facturi,
    cu starea ei. „Contabilizată” = nota de contare VALIDATĂ; o ciornă e „notă propusă, de validat”; o încasare nu e contare
    (înainte, `EXISTS(orice notă)` le punea pe toate trei sub „contabilizată”)."""
    pe = note_pe_facturi(cur, schema, factura_ids)
    out = {}
    for fid in factura_ids:
        n = next((x for x in pe.get(int(fid), []) if x["e_contare"]), None)
        out[fid] = {"id": n["id"], "status": n["status"], "data": str(n["data"])} if n else None
    # [258] `eticheta` = nota cum o arată Registrul jurnal („nr. crt. 5 din 12.03.2026”); ecranul facturii n-o mai numește prin id
    et = dict(_et.note(cur, schema, [v["id"] for v in out.values() if v]))
    for v in out.values():
        if v:
            v["eticheta"] = et.get(v["id"])
    return out


def contare_existenta(cur, schema, factura_id):
    """[DDD1] Nota de CONTARE care ocupă factura, sau None.

    Înlocuiește `COUNT(*)`. Cele **3** facturi măsurate azi (`tenant_004` #9, `tenant_017` #8,
    `tenant_013` #14) au notă cu cheia — de plată sau de încasare — și trec pe aici."""
    for n in note_cu_cheia(cur, schema, factura_id):
        if n["e_contare"]:
            return n
    return None


def candidate_fara_cheie(cur, schema, f):
    """[DDD2] PLASA, pe criteriul STRICT: note FĂRĂ `factura_id`, cu semnătură de contare, în luna
    facturii, a căror valoare pe terț coincide cu totalul facturii la un ban.

    **Strict, nu larg, și motivul e măsurat**: criteriul larg (baza, sau suma tuturor liniilor) a
    produs 3 fals-pozitive pe datele de azi — două note de încasare care se potrivesc cu factura pe
    care chiar o încasează, și o amortizare care nimerește un total. Un automat oprit pe încasări
    n-ar mai fi o plasă, ar fi un obstacol."""
    d = f.get("data_emitere")
    if not d:
        return []
    an, luna = int(str(d)[:4]), int(str(d)[5:7])
    total = Decimal(str(f.get("total_lei") or f.get("total") or 0))
    if not total:
        return []
    cur.execute("SELECT i.id, i.data, i.descriere, i.status, i.sursa, "
                "       l.cont_debit, l.cont_credit, l.suma "
                "FROM %sinregistrari i "
                "JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                "WHERE i.factura_id IS NULL "
                "  AND EXTRACT(YEAR FROM i.data)::int = %%s "
                "  AND EXTRACT(MONTH FROM i.data)::int = %%s "
                "ORDER BY i.id" % (_p(schema), _p(schema)), (an, luna))
    note = {}
    for r in cur.fetchall():
        if isinstance(r, dict):
            nid, data, desc, status, sursa = r["id"], r["data"], r["descriere"], r["status"], r["sursa"]
            cd, cc, suma = r["cont_debit"], r["cont_credit"], r["suma"]
        else:
            nid, data, desc, status, sursa, cd, cc, suma = r
        n = note.setdefault(nid, {"id": nid, "data": data, "descriere": desc,
                                  "status": status, "sursa": sursa, "linii": []})
        n["linii"].append((cd, cc, Decimal(str(suma or 0))))
    out = []
    for n in note.values():
        if not e_nota_de_contare(n["linii"]):
            continue
        if egale(valoare_pe_tert(n["linii"]), total):
            out.append(n)
    return out


def leaga_nota_de_factura(cur, schema, nota_id, linii, data):
    """[DDD3] LA SURSĂ: o notă scrisă pe calea liberă care contează **evident** o factură primește
    `factura_id` la scriere. Întoarce id-ul facturii legate, sau None.

    „Evident" e definit îngust, deliberat: semnătură de contare · **exact una** dintre facturile
    declarabile ale lunii se potrivește pe total la un ban · factura aia n-are deja o notă de
    contare. **Dacă se potrivesc două, nu se leagă niciuna** — o legătură greșită e mai rea decât
    lipsa ei, fiindcă ar face factura să pară contată de altcineva.

    De ce e reparația de la sursă și nu plasa: după ce nota poartă cheia, `contare_existenta` o
    vede, deci `candidate_fara_cheie` rămâne **plasă**, nu mecanism principal."""
    if not data or not e_nota_de_contare(linii):
        return None
    v = valoare_pe_tert(linii)
    if not v:
        return None
    an, luna = int(str(data)[:4]), int(str(data)[5:7])
    cur.execute("SELECT f.id, COALESCE(f.total_lei, f.total, 0) AS tot "
                "FROM %sfacturi f "
                "WHERE %s AND COALESCE(f.tip,'factura')='factura' "
                "  AND EXTRACT(YEAR FROM f.data_emitere)::int = %%s "
                "  AND EXTRACT(MONTH FROM f.data_emitere)::int = %%s"
                % (_p(schema), _nsf.clauza_sql(alias="f")), (an, luna))
    potrivite = []
    for r in cur.fetchall():
        fid, tot = (r["id"], r["tot"]) if isinstance(r, dict) else r
        if egale(tot, v):
            potrivite.append(fid)
    potrivite = [fid for fid in potrivite if contare_existenta(cur, schema, fid) is None]
    if len(potrivite) != 1:
        return None
    cur.execute("UPDATE %sinregistrari SET factura_id=%%s WHERE id=%%s" % _p(schema),
                (potrivite[0], nota_id))
    return potrivite[0]


def dezleaga_nota(cur, schema, nota_id):
    """[GGG2 / R90] Rupe legătura dintre o notă și factura ei. Întoarce id-ul facturii dezlegate.

    **O notă de CONTARE nu se dezleagă.** Ea *este* evidența facturii; ruptă, cifra n-ar mai avea
    documentul care o justifică (P14), iar factura ar redeveni „necontată" fără ca nimic să se fi
    întâmplat în realitate. Se dezleagă numai ce nu e contare: plăți, încasări, orice altceva a
    ajuns să poarte cheia.

    **CE SE SCHIMBĂ, dincolo de ștergere** — se scrie aici fiindcă nu e evident și nu era în
    întrebare: `reconciliere_api.facturi_deschise` calculează soldul unei facturi din notele legate
    prin `factura_id` (credit 4111 la emise, debit 401 la primite). Dezlegarea unei plăți **face
    factura să reapară ca neîncasată**. E chiar efectul dorit când potrivirea a fost greșită, dar e
    un efect asupra unei cifre pe care o vede omul, nu o operație tehnică.

    **Poarta de perioadă NU e aici, și e deliberat.** Dezlegarea modifică evidența lunii notei, deci
    cade sub P15 — dar verificarea stă în rută, la `_cere_perioada_deschisa`, exact ca la editarea,
    ștergerea și validarea unei note care există. *Două locuri care întreabă „e luna închisă?" ar fi
    două definiții ale aceleiași porți; garda `test_r42_criteriu` o citește pe cea din rută.*

    **Ce NU se pierde:** `extras_linii.alocari` păstrează potrivirea originală (`factura_id` + sumă)
    ca fapt al liniei de extras, independent de notă. Deci urma potrivirii rămâne chiar după
    dezlegare — de-aia actul e reversibil în înțeles, nu doar în date."""
    cur.execute("SELECT i.id, i.data, i.factura_id, i.status, i.sursa, "
                "       l.cont_debit, l.cont_credit, l.suma "
                "FROM %sinregistrari i "
                "LEFT JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                "WHERE i.id = %%s" % (_p(schema), _p(schema)), (nota_id,))
    randuri = cur.fetchall()
    if not randuri:
        raise RefuzContare("NOTA_INEXISTENTA", "nota nu există")
    cap = dict(randuri[0])
    linii = [(r["cont_debit"], r["cont_credit"], Decimal(str(r["suma"] or 0)))
             for r in randuri if r["cont_debit"] is not None]
    if cap.get("factura_id") is None:
        raise RefuzContare("NOTA_NELEGATA", "nota nu e legată de nicio factură",
                           detalii={"nota_id": nota_id})
    from core import coada_api as _coada   # [lotul 07.10 pct.6] nota la validare nu se modifică
    if _coada.nota_la_validare(cur, schema, nota_id):
        raise RefuzContare(_coada.COD_NOTA_LA_VALIDARE, _coada.mesaj_nota_la_validare(cur, schema, nota_id), detalii={"nota_id": nota_id})
    if e_nota_de_contare(linii):
        raise RefuzContare(
            "E_NOTA_DE_CONTARE",
            "Nota %s e chiar evidența contabilă a facturii, nu o plată. Nu se dezleagă: o cifră "
            "fără documentul care o justifică nu se mai poate desface. Dacă factura trebuie "
            "corectată, se stornează." % _et.nota(cur, schema, nota_id),
            detalii={"nota_id": nota_id, "factura_id": cap["factura_id"], "iesire": "storno"})
    cur.execute("UPDATE %sinregistrari SET factura_id = NULL WHERE id = %%s" % _p(schema),
                (nota_id,))
    return cap["factura_id"]


# ══════════════════════════════════════════════════════════ GENERAREA NOTEI
MSG_FARA_COTA = ("factura fără cotă de TVA pe linii — nu se poate genera nota "
                 "(declară cota pe factură)")

def _ms_citeste(cur, schema):
    from core import metoda_stoc as _ms
    return _ms.citeste(cur, schema)


def cont_venit_linie(cont_venit, cont_venit_implicit=None, tip_operatiune=None):
    """Contul de venit al unei linii de factură EMISĂ — sursa UNICĂ pentru nota de contare (`genereaza_note`) și pentru D406 (SalesInvoices).
    [deficiența 380, comanda Costin 8.2, 18.10.2026: „Contul de venit vine dintr-o singură sursă”] D406 punea pe linii 707 fix, iar nota
    contul liniei (704 la servicii): aceeași factură apărea pe două conturi. Ordinea: contul liniei; altfel contul de venit implicit al
    firmei; altfel 707. Factura de avans (și regularizarea ei) e pe 419 (OMFP 1802/2014, funcțiunea contului 419)."""
    if (tip_operatiune or "normal") in ("avans", "regularizare_avans"):
        return CONT_AVANS_CLIENT
    return (cont_venit or "").strip() or (cont_venit_implicit or "").strip() or "707"


def _linii_facturii(cur, schema, fid):
    """Liniile facturii (contul de venit / de cheltuială al liniei, cota, cantitatea, prețul), în ordinea lor."""
    # [lotul 11, C82] + `valoare_neta` (BT-131 de pe factură, la factura importată): valoarea liniei e aceea, nu cantitate × preț
    cur.execute("SELECT cont_venit, cont_cheltuiala, cota_tva, cantitate, pret_unitar, valoare_neta FROM %sfactura_linii WHERE factura_id=%%s "
                "ORDER BY id" % _p(schema), (fid,))
    return [dict(r) for r in cur.fetchall()]


def _note_pe_cote(linii, curs, nota_baza, nota_tva, tva_factura=None, tva_lei_document=None):
    """[lotul 11, decizia Costin 10.3: „Rotunjirea TVA: o singură regulă pe toată aplicația, cea cerută de validatorul e-Factura.”] Notele
    unei facturi din liniile ei, pe REGULA UNICĂ (`core/tva_calcul.py`, EN 16931 BR-DEC-23 / BR-S-08 / BR-CO-17): baza pe (cont, cotă) =
    Σ valorilor nete ale liniilor (la ban), TVA-ul pe COTĂ = baza cotei × cotă / 100, rotunjit o dată — același TVA ca pe PDF și în XML-ul
    e-Factura. Înainte: TVA-ul pe fiecare grup (cont, cotă) din Σ cantitate × preț nerotunjit — două conturi de venit pe aceeași cotă
    rotunjeau de două ori. Cartea e în lei (A1): baza × curs; TVA-ul pe cote în lei, cu suma egală cu TVA-ul documentului în lei
    (`tva_calcul.tva_lei_pe_cote`). `nota_baza(cont, suma)` / `nota_tva(suma)` -> (debit, credit, suma).

    `tva_factura` = {cotă: TVA} de pe factura FURNIZORULUI (`tva_facturii_pe_cote`, lotul 11, C79): pe factura primită TVA-ul cotei e cel
    înscris pe factură (CF art.299 alin.(1) lit.a, art.319 alin.(20) lit.j), nu recalculul din baze; baza pe cont rămâne a liniilor.
    `tva_lei_document` = TVA-ul facturii în lei scris de furnizor (BT-111, lotul 11, C81), împărțit pe cote (`tva_lei_pe_cote`)."""
    from core import tva_calcul as _tc
    baze = {}   # {cota: {cont: baza}} — rândurile se grupează direct pe cotă (fără comparație pe valoarea cotei)
    for l in linii:
        pe_cont = baze.setdefault(Decimal(str(l["cota_tva"])), {})
        pe_cont[l["cont"]] = (pe_cont.get(l["cont"], Decimal(0))
                              + _tc.net_linie(l["cantitate"], l["pret_unitar"], l.get("valoare_neta")))   # [C82] BT-131
    pc = _tc.pe_cote(linii)
    if tva_factura is not None:
        pc = {c: (b, tva_factura[c]) for c, (b, _t) in pc.items()}
    tva_lei = _tc.tva_lei_pe_cote(pc, curs, tva_lei_document=tva_lei_document)
    note = []
    for cota in sorted(pc):
        for cont, b in sorted(baze.get(cota, {}).items()):
            note.append(_fc._nota(*nota_baza(cont, b * curs)))
        if tva_lei[cota]:
            d, cr, s = nota_tva(tva_lei[cota])
            note.append(_fc._nota(d, cr, s, temei=(
                "CF art.299 alin.(1) lit.a: TVA-ul cotei de %s%% de pe factura furnizorului" if tva_factura is not None else
                "EN 16931 BR-CO-17: TVA-ul cotei de %s%% din baza ei, rotunjit o dată") % cota.normalize()))
    return note


def cote_nepotrivite(tva_factura, cote_linii):
    """(cotele cu TVA de pe factură pe care nu stă nicio linie, cotele pozitive ale liniilor fără TVA pe factură) — amândouă goale când
    defalcarea facturii și liniile ei au aceleași cote. Regula unică pentru contare (`tva_facturii_pe_cote`) și D300 (`_cu_tva_facturii`)."""
    return (sorted(c for c, t in tva_factura.items() if t and c not in cote_linii),
            sorted(c for c in cote_linii if c > 0 and c not in tva_factura))


def tva_facturii_pe_cote(cur, schema, f, linii):
    """[lotul 11, C79] {cotă (Decimal, procente): TVA} de pe factura PRIMITĂ, în moneda ei — sau None când factura nu-l poartă separat.

    TEMEI. CF art.299 alin.(1) lit.a: deducerea cere ca beneficiarul „să dețină o factură emisă în conformitate cu prevederile art. 319”;
    CF art.319 alin.(20) lit.j: factura cuprinde „indicarea cotei de taxă aplicate și a sumei taxei colectate, exprimate în lei, în funcție
    de cotele taxei”. Taxa deductibilă e deci cea scrisă de furnizor pe factură, pe cotele ei — nu una recalculată din baze de beneficiar.
    Înainte: TVA-ul notei era recalculat din liniile facturii (regula unică, `core/tva_calcul.py`); pe un XML cu 143,52 lei nota avea 143,54.

    SURSA: `factura_tva_cote` (defalcarea BG-23 a XML-ului e-Factura, salvată la import — `efactura_import.tva_cote_din_xml`). O factură
    fără rânduri acolo (introdusă în aplicație, nu din XML) -> None: TVA-ul ei e chiar cel scris pe factură de aplicație din linii
    (`facturi_api.totaluri_din_linii`), deci recalculul e TVA-ul facturii. Cotele defalcării și ale liniilor trebuie să fie aceleași (vin
    din același XML: BT-119 / BT-152); altfel împărțirea TVA-ului pe cote ar fi ghicită -> refuz numit, contarea o face omul."""
    from core import repo_efactura as _re
    randuri = _re.tva_cote(cur, schema, [f["id"]]).get(f["id"])
    if not randuri:
        return None
    tf = {}
    for cota, tva, _sursa, _cat, _baza in randuri:
        c = Decimal(str(cota))
        tf[c] = tf.get(c, Decimal(0)) + Decimal(str(tva))
    cote_linii = {Decimal(str(l["cota_tva"])) for l in linii}
    if any(cote_nepotrivite(tf, cote_linii)):
        _proc = lambda cs: ", ".join("%s%%" % c.normalize() for c in cs)   # noqa: E731
        raise RefuzContare(
            "TVA_FACTURA_ALTE_COTE",
            "%s: defalcarea TVA a furnizorului (XML, BG-23) are cotele %s, iar liniile facturii cotele %s — TVA-ul de dedus nu se poate "
            "împărți pe cote fără a ghici. Verifică XML-ul furnizorului și scrie nota manual." % (
                _et.factura_din_rand(f) or "Factura primită", _proc(sorted(tf)), _proc(sorted(cote_linii))),
            detalii={"factura_id": f["id"], "cote_factura": [str(c) for c in sorted(tf)],
                     "cote_linii": [str(c) for c in sorted(cote_linii)]})
    return {c: tf.get(c, Decimal(0)) for c in cote_linii}


def tva_lei_furnizor(f):
    """[lotul 11, C81] TVA-ul în lei al facturii PRIMITE din XML, în valută — `facturi.tva_lei`, scris la import din BT-111 (TVA-ul în lei pe
    care l-a scris furnizorul) sau, fără BT-111, TVA × curs, ca la emitere (`curs_factura_importate`); None la RON sau fără curs. CF
    art.319 alin.(20) lit.j: factura cuprinde „suma taxei colectate, exprimate în lei, în funcție de cotele taxei”."""
    from core import sume_lei as _sl
    if _sl.e_ron(f.get("moneda")) or f.get("tva_lei") is None:
        return None
    return Decimal(str(f["tva_lei"]))


def tva_lei_facturii(tva_factura, cote_linii, f):
    """[lotul 11, C79 / C81] {cotă (Decimal): TVA în lei} de pe factura PRIMITĂ din XML: TVA-ul cotei de pe factura furnizorului (BG-23,
    moneda ei), în lei cu `tva_calcul.tva_lei_pe_cote` — împărțind BT-111 (`tva_lei_furnizor`) când factura e în valută. None când cotele
    defalcării nu sunt ale liniilor (`cote_nepotrivite`: împărțirea ar fi ghicită). Regula unică pentru contare, D300, D394 și D406."""
    from core import sume_lei as _sl, tva_calcul as _tc
    tf = {Decimal(str(c)): Decimal(str(t)) for c, t in tva_factura.items()}
    cl = {Decimal(str(c)) for c in cote_linii}
    if any(cote_nepotrivite(tf, cl)):
        return None
    return _tc.tva_lei_pe_cote({c: (None, tf.get(c, Decimal(0))) for c in cl}, _sl.curs_factura(f), tva_lei_document=tva_lei_furnizor(f))


def curs_factura_importate(cur, schema, f):
    """[lotul 11, C83] Cursul facturii din XML în valută, pus pe factură cum îl pune emiterea în valută (`facturi_api.creeaza_factura`):
    `curs_bnr`, `data_curs`, `curs_sursa`, `total_lei`, `tva_lei`. Până azi importul nu scria cursul, iar nimic nu-l mai completa: factura
    primită în valută nu se putea conta (LIPSA_CURS_LEI) și nu intra în D300 / D394 / D406.

    TEMEI. CF art.290 alin.(2): „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României [...]
    valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză”; HG 1/2016 pct.35 alin.(1): „prin ultimul curs de
    schimb comunicat de Banca Națională a României se înțelege cursul de schimb comunicat de respectiva bancă în ziua anterioară și care
    este valabil pentru operațiunile care se vor desfășura în ziua următoare.” Regula e a lui `curs_bnr` (`REGULA_OPERATIUNE`), prin
    `facturi_api.curs_automat` — aceeași ca la emitere și în formular; nu se rescrie aici.
    TVA-ul în lei: BT-111 (TVA-ul în lei scris de furnizor, `efactura_import.tva_lei_din_xml`; CF art.319 alin.(20) lit.j) când XML-ul îl
    are; altfel TVA × curs, ca la emitere (`facturi_api.sume_lei`). Totalul în lei = baza × curs + TVA-ul în lei.

    Cursul se ADUCE (descărcarea BNR) înaintea tranzacției, de apelant (`uc_comun._preincalzeste_cursul`); aici se decide pe cache.
    Întoarce None (RON, are deja curs, nu e din XML și nici introdusă de mână — `manuala`, lotul 12, 477), {"curs": …} (scris) sau refuzul cursului (dict cu `ok` False, `cod`, `mesaj`,
    nimic scris) — factura rămâne fără curs, iar contarea o refuză cu ieșirea numită (`contabilizeaza`, LIPSA_CURS_LEI)."""
    import datetime as _dt
    from core import sume_lei as _sl, tva_calcul as _tc, facturi_api as _fa, efactura_import as _ef, repo_efactura as _re
    # [lotul 12, 477] și factura primită introdusă de mână (`manuala`, fără XML), chemată de validarea ei (`uc_factura_primita.valideaza`)
    if _sl.e_ron(f.get("moneda")) or f.get("curs_bnr") is not None or not (str(f.get("xml") or "").strip() or f.get("manuala")):
        return None
    zi = f["data_emitere"]
    zi = zi if isinstance(zi, _dt.date) else _dt.date.fromisoformat(str(zi)[:10])
    ca = _fa.curs_automat(cur.connection, f["moneda"], zi)
    if isinstance(ca, dict):
        return ca
    curs, data_curs, sursa = ca
    import xml.etree.ElementTree as _ET
    bt111 = None
    if str(f.get("xml") or "").strip():
        _x = f["xml"].encode("utf-8") if isinstance(f["xml"], str) else f["xml"]
        bt111 = _ef.tva_lei_din_xml(_ET.fromstring(_x), f["moneda"])
    tot, tva = Decimal(str(f.get("total") or 0)), Decimal(str(f.get("tva") or 0))
    if bt111 is not None:
        tva_lei = _tc.q2(bt111)
        total_lei = _tc.q2((tot - tva) * Decimal(str(curs))) + tva_lei
    else:
        tva_lei, total_lei = _fa.sume_lei({"tva": tva, "total": tot}, curs)
    _re.seteaza_cursul_importului(cur, schema, f["id"], curs, data_curs, sursa, tva_lei, total_lei)
    f.update({"curs_bnr": curs, "data_curs": data_curs, "curs_sursa": sursa, "tva_lei": tva_lei, "total_lei": total_lei})
    return {"curs": curs, "data_curs": data_curs, "tva_lei": tva_lei, "total_lei": total_lei, "bt111": bt111 is not None}


def genereaza_note(cur, schema, f, pe_4428, cont_venit_implicit, cont_cheltuiala=None):
    """Notele unei facturi, ca listă de dict {debit, credit, suma}. **PUR față de bază la scriere**:
    citește, nu scrie — tiparul NIR, unde validarea se termină înainte ca ceva să înceapă.

    `pe_4428` = TVA-ul facturii e neexigibil (emisă) / cu deducerea amânată (primită) și intră pe 4428 în loc de 4427 / 4426. Îl decide
    apelantul din REGIMUL FACTURII LA DATA EI (`tva_incasare.regim`), nu din bifa firmei de azi — [lotul 10, deficiența 428]: „totul
    trebuie să decidă pe DATA documentului”. Înainte era bifa firmei (`firma_profil.tva_la_incasare`) aplicată pe amândouă direcțiile."""
    fid = f["id"]
    directie = f.get("directie")
    tvai = bool(pe_4428)
    la_data = str(f["data_emitere"])
    # [A1, 17.09.2026] CARTEA E IN LEI. Baza notelor (4111/401/4426/4427) se inmulteste cu cursul
    # facturii — altfel o factura in valuta ar posta valuta drept lei, iar D300/D394/D406 (care citesc
    # cartea) ar mosteni greseala. `contabilizeaza` refuza deja o factura in valuta fara curs (poarta
    # de mai sus), deci aici `curs_factura` nu ridica: RON->1, valuta->cursul de pe document.
    from core import sume_lei as _sl
    _curs = _sl.curs_factura(f)

    if directie == "emisa":
        cvi = cont_venit_implicit or "707"
        # [lotul 6 pct.3b, 278] Factura de AVANS (și regularizarea ei) nu e venit: OMFP 1802/2014, funcțiunea contului 419 — „În creditul
        # contului 419 «Clienți - creditori» se înregistrează: sumele facturate clienților reprezentând avansuri pentru livrări de bunuri
        # sau prestări de servicii (411)”. Nota: 4111 = 419 + 4427; regularizarea (rândurile cu minus) o inversează. Până azi ieșea
        # 4111 = 707 + 4427, adică venit înaintea livrării.
        if (f.get("tip_operatiune") or "normal") in ("avans", "regularizare_avans"):
            linii = _linii_facturii(cur, schema, fid)
            if not linii or any(l["cota_tva"] is None for l in linii):
                raise RefuzContare("FARA_COTA", MSG_FARA_COTA)
            return _note_pe_cote([dict(l, cont=CONT_AVANS_CLIENT) for l in linii], _curs,
                                 lambda c, s: ("4111", c, s), lambda s: ("4111", "4428" if tvai else "4427", s))
        # [380] contul liniei prin `cont_venit_linie` (aceeași regulă ca D406), grupat pe (cont, cotă)
        linii = [dict(l, cont=cont_venit_linie(l["cont_venit"], cvi)) for l in _linii_facturii(cur, schema, fid)]
        total_baza = sum(((Decimal(str(l["valoare_neta"])) if l.get("valoare_neta") is not None
                      else Decimal(str(l["cantitate"] or 0)) * Decimal(str(l["pret_unitar"] or 0))) for l in linii), Decimal(0))   # [lotul 11, C82]
        if total_baza == 0:
            # factură fără linii (legacy): cade pe antet, un singur cont. Antetul IN LEI.
            _tl, _vl = _sl.antet_lei(f)
            baza = _tl - _vl
            cur.execute("SELECT MAX(cota_tva) AS cota FROM %sfactura_linii WHERE factura_id=%%s"
                        % _p(schema), (fid,))
            r = cur.fetchone()
            cota_h = r["cota"] if isinstance(r, dict) else r[0]
            if cota_h is None:
                raise RefuzContare("FARA_COTA", MSG_FARA_COTA)
            return _fc.factura_emisa(baza, cota=Decimal(str(cota_h)) / 100, la_data=la_data,
                                     tva_incasare=tvai, cont_venit=cvi)
        if any(l["cota_tva"] is None for l in linii):
            raise RefuzContare("FARA_COTA", MSG_FARA_COTA)
        return _note_pe_cote(linii, _curs, lambda c, s: ("4111", c, s), lambda s: ("4111", "4428" if tvai else "4427", s))

    # [E1/A6-runda2, 18.09.2026] PRIMITĂ pe COTE, ca emisa — nu `MAX(cota_tva)` pe toată factura.
    # O factură mixtă 21/11 aplica 21% pe toată baza -> 4426 supraevaluat, iar controlul încrucișat cu
    # D300 (care calculează corect pe rânduri) ieșea roșu -> risc de „corectare" a declarației după carte.
    # [deficiența 418b] și pe CONTUL LINIEI (`factura_linii.cont_cheltuiala`, gol = contul facturii), ca emisa pe (cont_venit, cotă)
    linii = _linii_facturii(cur, schema, fid)
    total_baza = sum(((Decimal(str(l["valoare_neta"])) if l.get("valoare_neta") is not None
                      else Decimal(str(l["cantitate"] or 0)) * Decimal(str(l["pret_unitar"] or 0))) for l in linii), Decimal(0))   # [lotul 11, C82]

    def _nota_primita(baza_lei, cota_frac, cont_linie=None):
        cont = (cont_linie or "").strip() or cont_cheltuiala or None
        if f.get("taxare_inversa"):
            # art. 331: la beneficiar 4426 = 4427 (autocolectare), nu TVA pe 401. Funcția exista în
            # `core/facturi.py` de la început și nu o chema nimeni — cât timp contarea era un act rar,
            # nu se vedea. De când e automată, se vede la fiecare factură.
            return _fc.taxare_inversa(baza_lei, cota=cota_frac, la_data=la_data, cont=cont)
        return _fc.factura_primita(baza_lei, cota=cota_frac, la_data=la_data, tva_incasare=tvai, cont=cont)

    if total_baza == 0:
        # factură fără linii (legacy): cade pe antet, o singură cotă (MAX). Antetul IN LEI.
        _tl, _vl = _sl.antet_lei(f)
        baza = _tl - _vl
        cur.execute("SELECT MAX(cota_tva) AS cota FROM %sfactura_linii WHERE factura_id=%%s"
                    % _p(schema), (fid,))
        r = cur.fetchone()
        cota_h = r["cota"] if isinstance(r, dict) else r[0]
        if cota_h is None:
            raise RefuzContare("FARA_COTA", MSG_FARA_COTA)
        if not f.get("taxare_inversa"):
            # [lotul 11, C79] fără baze pe linii, TVA-ul e cel din antetul facturii (în lei), nu baza × cotă (CF art.299 alin.(1) lit.a)
            cont = cont_cheltuiala or _fc.ACHIZITIE["marfa"]
            return [_fc._nota(cont, "401", baza)] + ([_fc._nota("4428" if tvai else "4426", "401", _vl,
                                                               temei="CF art.299 alin.(1) lit.a: TVA-ul de pe factura furnizorului")]
                                                     if _vl else [])
        return _nota_primita(baza, Decimal(str(cota_h)) / 100)
    if any(l["cota_tva"] is None for l in linii):
        raise RefuzContare("FARA_COTA", MSG_FARA_COTA)
    if f.get("taxare_inversa"):   # art. 331: la beneficiar 4426 = 4427 (autocolectare), nu TVA pe 401
        nota_tva = lambda s: ("4426", "4427", s)   # noqa: E731
        tva_factura = None   # taxarea inversă: factura nu poartă TVA, beneficiarul îl calculează (art.331)
    else:
        nota_tva = lambda s: ("4428" if tvai else "4426", "401", s)   # noqa: E731
        tva_factura = tva_facturii_pe_cote(cur, schema, f, linii)   # [lotul 11, C79] TVA-ul de pe factura furnizorului
    return _note_pe_cote([dict(l, cont=(l["cont_cheltuiala"] or "").strip() or cont_cheltuiala or _fc.ACHIZITIE["marfa"]) for l in linii],
                         _curs, lambda c, s: (c, "401", s), nota_tva, tva_factura=tva_factura,
                         # [lotul 11, C81] factura în valută: TVA-ul ei în lei de pe factură (BT-111), împărțit pe cote
                         tva_lei_document=tva_lei_furnizor(f) if tva_factura is not None else None)


def note_propuse(cur, schema, f, cont_cheltuiala=None):
    """(regimul TVA al facturii, notele ei) — ce ar scrie contarea facturii `f` (rândul din `facturi`) ACUM, fără nicio scriere. Sursa unică
    pentru `contabilizeaza` și pentru regenerarea pe uscat a ciornei la validare (`ciorne_depasite`, felul „factura_emisa”, lotul 11, 451):
    o regulă schimbată aici se vede pe ciornele scrise înainte. Cursor dict (`_linii_facturii`).

    [lotul 10, deficiența 428] Regimul TVA al FACTURII, la DATA EI (CF art.282 alin.(3), (6), (7); art.297 alin.(2)-(3)): emisă în
    sistem -> TVA pe 4428 (neexigibil până la încasare); primită de la un furnizor în sistem sau de o firmă în sistem -> 4428 (deducerea
    amânată până la plată); stornarea urmează factura stornată (alin.(10)). Până azi: bifa firmei de AZI, iar automatul REFUZA
    factura primită de la un furnizor în sistem („exigibilitatea vine din reconcilierea bancară”) — acum plata, prin bancă sau casă,
    mută singură TVA-ul (`tva_incasare.linii_la_incasare`), deci contarea nu mai are de ce să aștepte omul."""
    from core import tva_incasare as _tvi
    cur.execute("SELECT cont_venit_implicit FROM %sfirma_profil WHERE id=1" % _p(schema))
    prof = cur.fetchone()
    cvi = (prof["cont_venit_implicit"] if isinstance(prof, dict) else prof[0]) if prof else None
    regim_tva = _tvi.regim(cur, schema, f)
    note = genereaza_note(cur, schema, f, regim_tva in (_tvi.REGIM_INCASARE, _tvi.REGIM_STORNO), cvi, cont_cheltuiala=cont_cheltuiala)
    if regim_tva == _tvi.REGIM_STORNO:
        # CF art.282 alin.(10) lit.a): stornarea anulează întâi TVA-ul rămas neexigibil pe factura stornată (4428), iar ce depășește
        # devine exigibil / deductibil la data stornării (4427 / 4426)
        note = _tvi.note_storno(note, f.get("directie"), _tvi.anulare_storno(cur, schema, f)[0])
    return regim_tva, note


def _descriere(f, data_nota=None, motiv_data=None):
    """Descrierea notei. Cand nota NU poarta data emiterii, descrierea o SPUNE, cu motivul.

    [JJJ2] *„nu doar o dată arbitrară"*: o notă datată altfel decât faptul pe care îl înregistrează
    trebuie să poarte legătura, altfel peste șase luni nimeni nu mai poate spune de ce e acolo.
    Legătura structurală există deja — `factura_id`, iar `jurnal_api.document_justificativ` derivă
    din ea *„Factură <serie><număr> din <data>"*. Mențiunea de aici e pentru omul care citește nota,
    nu pentru mașină."""
    serie, numar = f.get("serie"), f.get("numar") or f["id"]
    from core import pdf_util as _pu
    nr = _pu.serie_nr(serie, numar)   # [lotul 11, 443] „F6 nr. 1”: seria și numărul separate; notele scrise înainte: core/migrare_serie_nr_descrieri.py
    baza = "Contare factura %s" % nr
    if data_nota is not None and str(data_nota)[:10] != str(f["data_emitere"])[:10]:
        baza += " din %s — inregistrata la %s" % (str(f["data_emitere"])[:10], str(data_nota)[:10])
        if motiv_data:
            baza += ": %s" % motiv_data
    return baza[:200]


def contabilizeaza(cur, schema, factura_id, automat, cont_cheltuiala=None,
                   data_nota=None, motiv_data=None, nir_legat=None):
    """Scrie nota de contare a facturii. Tiparul NIR, punct cu punct:

    1. **validarea se termină înainte de orice scriere** — tot ce poate refuza refuză mai sus de
       primul `INSERT`, deci nu există stare pe jumătate;
    2. **o singură tranzacție** — nu comite; comite apelantul, odată cu faptul care a produs nota.
       Dacă faptul cade, nota cade cu el;
    3. **nota intră `ciorna`** — automat nu înseamnă validat;
    4. **`sursa` numește actul**, nu omul: `facturi`;
    5. **referință inversă**: `inregistrari.factura_id`.

    `automat=True` e calea care pornește singură (emitere, validare). `automat=False` e actul explicit
    al omului (ruta de contabilizare). Diferența nu e de politețe: automatul **refuză** clasele pe
    care nu le poate decide singur, omul le poate duce mai departe.

    **`data_nota` — [JJJ, 29.08.2026].** Implicit, nota poartă **data emiterii**: faptul și evidența
    lui au aceeași dată, și așa rămâne pentru orice factură nouă. Un `data_nota` explicit e pentru
    **istoric**: o factură veche pe care abia acum o descoperi necontată. Atunci:
      * poarta de perioadă se mută pe **data notei**, fiindcă luna care se modifică e a notei, nu a
        facturii. *Asta e chiar ramura pe care se sprijină decizia din JJJ2: dacă luna emiterii e
        închisă, nota se scrie la data descoperirii — altfel n-ar exista nicio dată validă;*
      * **descrierea o spune**, cu motivul (`motiv_data`). O notă datată altfel decât faptul, fără
        mențiune, e o dată arbitrară.
    *Ce NU se schimbă: `factura_id` rămâne, deci documentul justificativ derivat din el arată tot
    factura originală, cu data ei. Legătura nu se pierde, doar se adaugă mențiunea.*

    **`nir_legat` — [decizia Costin 08.10.2026, pct.2].** O factură primită care încarcă 371 la global-valoric, de la un
    furnizor cu NIR „fără factură” nelegat (`nir_legare.candidati`), cere alegerea: id-ul NIR-ului (legare: stornarea în roșu
    a costului NIR-ului, `nir_legare.leaga`) sau `nir_legare.ALTA_LIVRARE` (contare normală, consemnată în descriere). Fără
    alegere: `RefuzContare(NIR_DE_LEGAT)` cu candidații și propunerea dedusă, ÎNAINTE de orice scriere — pe ambele căi
    (automat sau act explicit), fiindcă nici automatul nu poate ști dacă e aceeași livrare.
    """
    # [lotul 10, C73 / U2] contarea e SERIALIZATĂ pe factură (lacătul ține până la comiterea notei): două contări simultane treceau
    # amândouă de verificarea „deja contată” de mai jos, scriau două note, iar dacă alegeau NIR-uri diferite a doua cădea cu 500 pe
    # `nir_factura_id_uq` (`nir_legare.leaga`). Acum a doua așteaptă, apoi vede nota primei („deja_contata”).
    cur.execute("SELECT * FROM %sfacturi WHERE id=%%s FOR NO KEY UPDATE" % _p(schema), (factura_id,))
    f = cur.fetchone()
    if not f:
        raise RefuzContare("INEXISTENTA", "factură inexistentă")
    f = dict(f)

    if _nsf.e_sold_preluat(f.get("tip")):   # [lotul 12, 252] soldul ei e deja în soldurile inițiale: o notă l-ar înregistra a doua oară
        raise RefuzContare("SOLD_PRELUAT", _nsf.MESAJ_SOLD_PRELUAT)
    if (f.get("tip") or "factura") != "factura":
        raise RefuzContare("NU_E_DOCUMENT_FISCAL",
                           "proforma/avizul nu se contabilizează (nu e document fiscal)")
    if _fc.e_din_bon_fiscal(f):
        # [decizia A 02.10] vânzarea e deja în nota raportului Z (5311 = 707, 707 = 4427): o notă 4111 = 707 + 4427 ar
        # dubla venitul și TVA colectat. Factura e documentul cerut de client (HG 479/2003 anexa art.2), nu un fapt nou.
        raise RefuzContare("EMISA_DIN_BON",
                           "factura e emisă pe baza bonului fiscal %s — vânzarea e deja înregistrată din raportul Z, "
                           "deci nu primește o a doua notă de vânzare" % _fc.mentiune_bon(f))

    # [A3, 17.09.2026] O factură ANULATĂ / STORNATĂ nu primește notă: e un document VOID, iar nota
    # ar afirma un fapt economic care nu există. Până azi `_conteaza_la_creare` nu se uita la status,
    # deci un `POST /facturi {"status":"anulata"}` producea 4111=707/4111=4427 pentru o factură
    # anulată. (`ciorna`/`descarcata` NU se blochează aici — nota-ciornă a unei de_preluat e normală.)
    _st = (f.get("status") or "").strip().lower()
    if _st in ("anulata", "stornata"):
        raise RefuzContare(
            "STATUS_VOID",
            "Factura e %s și nu se contabilizează: o notă ar înregistra un fapt economic care nu "
            "există. Un document anulat nu se contează; o stornare se declară prin documentul ei nou."
            % _st, detalii={"factura_id": factura_id, "status": _st})

    # [A1, 17.09.2026] POARTA CONVERSIEI: o factură în valută FĂRĂ curs BNR nu se poate exprima în
    # lei, iar cartea e în lei. Nu se ghicește 1 (asta e chiar greșeala A1) — se refuză cu ieșirea
    # numită. Criteriul cerut: o factură fără total în lei nu poate fi contată și nu intră în
    # declarație. RON și facturile cu curs trec neatinse.
    from core import sume_lei as _sl_gate
    # [lotul 11, C83] factura din XML în valută fără curs (BNR n-a răspuns la import, sau importată înainte de C83): cursul se pune aici,
    # pe aceeași regulă ca la import (CF art.290 alin.(2), HG 1/2016 pct.35 alin.(1)) — ruta de contare îl aduce înaintea tranzacției
    _rc = curs_factura_importate(cur, schema, f)
    try:
        _sl_gate.curs_factura(f)
    except _sl_gate.LipsaCurs as _e:
        if isinstance(_rc, dict) and _rc.get("ok") is False:
            raise RefuzContare(
                "LIPSA_CURS_LEI",
                "%s e în %s și n-are încă curs BNR: %s Cursul se pune singur, pe regula legală (cursul comunicat de BNR în ziua dinaintea "
                "facturii, CF art.290 alin.(2)), la următoarea contare — apasă din nou „Contabilizează” când BNR răspunde."
                % (_et.factura_din_rand(f), (f.get("moneda") or "?"), _rc.get("mesaj") or "cursul nu e disponibil."),
                detalii={"factura_id": factura_id, "moneda": f.get("moneda"), "cod_curs": _rc.get("cod"),
                         "iesire": "reincearca_contarea"})
        raise RefuzContare(
            "LIPSA_CURS_LEI",
            "%s e în %s și nu are curs BNR — nota s-ar scrie în valută drept lei. "
            "Completează cursul pe factură (ultimul curs comunicat până la data ei); abia apoi se "
            "contează și intră în declarații (A1, Cod fiscal art. 290)."
            % (_et.factura_din_rand(f), (f.get("moneda") or "?")),
            detalii={"factura_id": factura_id, "moneda": f.get("moneda"),
                     "iesire": "completeaza_curs"})

    # [EEE3 / FFF3] IDEMPOTENȚĂ: a doua chemare pe o factură deja contată e NO-OP, nu a doua notă
    # și nici eroare. Refuzul era corect, prezentarea lui nu — `422` face un comportament corect să
    # arate ca un defect.
    ex = contare_existenta(cur, schema, factura_id)
    if ex and not automat:
        # [lotul 07.10 B, C9, decizia Costin] actul explicit („Contabilizează”) pe o factură a cărei contare a fost RESPINSĂ la
        # validare: nota respinsă (ciornă) se înlocuiește cu una scrisă din factura de acum; noua ciornă intră singură în coadă
        from core import note_derivate as _nd
        if _nd.respinsa(cur, schema, ex["id"]):
            _nd.sterge_respinsa(cur, schema, ex["id"])
            ex = None
    if ex:
        return {"stare": "deja_contata", "inregistrare_id": ex["id"], "linii": [],
                "afirmatie": _af.afirmatie(
                    "neconformitate", "CONTARE_EXISTENTA",
                    "factura are deja notă de contare (nota %s); a doua chemare nu face nimic"
                    % _et.nota(cur, schema, ex["id"]),
                    unde=_et.factura_din_rand(f), regula="o factură are o singură contare")}

    data_nota = data_nota or f.get("data_emitere")
    if luna_blocata(cur, schema, data_nota):
        raise RefuzContare(
            "LUNA_INCHISA",
            "luna în care ar intra nota (%s) e închisă; redeschide-o, sau contează la o dată "
            "deschisă, cu mențiunea care leagă nota de factură" % str(data_nota)[:10],
            detalii={"data_nota": str(data_nota)[:10],
                     "data_emitere": str(f.get("data_emitere"))[:10]})

    from core import tva_incasare as _tvi
    if cont_cheltuiala is None and f.get("directie") == "primita":
        cur.execute("SELECT cont_cheltuiala FROM %sefactura_primite WHERE factura_id=%%s "
                    "AND cont_cheltuiala IS NOT NULL ORDER BY id DESC LIMIT 1" % _p(schema),
                    (factura_id,))
        r = cur.fetchone()
        if r:
            cont_cheltuiala = (r["cont_cheltuiala"] if isinstance(r, dict) else r[0]) or None

    regim_tva, note = note_propuse(cur, schema, f, cont_cheltuiala=cont_cheltuiala)

    # [decizia Costin 08.10.2026, pct.2] NIR-ul „fără factură” al aceleiași livrări: legarea se propune, alegerea e a omului
    from core import nir_legare as _nl
    nir_ales, alta_livrare = None, False
    deja_legat = _nl.legat_de_factura(cur, schema, factura_id) if _nl.se_aplica(cur, schema, f, note) else None
    if deja_legat:   # re-contare după respingere: NIR-ul ales la prima contare (forma nouă) rămâne legat
        nir_ales = deja_legat
    elif _nl.se_aplica(cur, schema, f, note):
        cands = _nl.candidati(cur, schema, f, data_nota)
        if cands:
            if nir_legat in (None, ""):
                cod, mesaj, det = _nl.refuz_de_ales(f, cands)
                raise RefuzContare(cod, mesaj, detalii=det)
            if nir_legat == _nl.ALTA_LIVRARE:
                alta_livrare = True
            else:
                nir_ales, er = _nl.verifica_alegerea(cands, f, nir_legat)
                if er:
                    raise RefuzContare(er[0], er[1], detalii={"camp": "nir-legat", "candidati": cands,
                                                              "propus": _nl.propus(cands), "factura_id": factura_id,
                                                              "alta_livrare": _nl.ALTA_LIVRARE})

    # [08.10.2026, deciziile Costin §6 pct.1–3] NIR-ul în FORMA NOUĂ (datoria pe 408): factura nu mai încarcă 371 — închide 408, trece
    # TVA-ul 4428 -> 4426 și scrie diferența de preț în perioada ei (`nir_legare.note_factura_legata`). Forma veche: stornarea de jos.
    plan_cv = []
    if nir_ales and nir_ales.get("forma_noua"):
        cur.execute("SELECT id, inregistrari_ids FROM %snir WHERE id = %%s" % _p(schema), (nir_ales["id"],))
        _n = cur.fetchone()
        cost_nir, tva_nir = _nl.sume_nir(cur, schema, dict(_n) if isinstance(_n, dict) else {"id": _n[0], "inregistrari_ids": _n[1]})
        net_marfa = sum(Decimal(str(n["suma"])) for n in note if n["debit"] == _nl.CONT_MARFA and n["credit"] == "401")
        metoda = _ms_citeste(cur, schema)
        if metoda == "cantitativ_valoric":
            plan_cv = _nl.plan_ajustare_cv(cur, schema, nir_ales["id"], net_marfa - cost_nir, data_nota)
        note = _nl.note_factura_legata(note, cost_nir, tva_nir, metoda,
                                       d_607=sum((x[1] for x in plan_cv if not x[2]), Decimal(0)))
        # [deficiența 405, decizia Costin „Avans 409x = 5311”] avansul plătit în numerar pentru NIR se compensează cu factura: 401 = 4091
        from core import casa_api as _casa
        note = note + _casa.compensare_avans_nir(cur, schema, nir_ales["id"], note)

    # [DDD2] PLASA, ultima verificare înainte de scriere.
    candidate = candidate_fara_cheie(cur, schema, f)
    if candidate and automat:
        raise RefuzContare(
            "POSIBILA_DUBLARE",
            "există deja o notă care pare să conteze factura asta, fără să o numească "
            "(nota %s). Nu se scrie automat: leag-o sau contează manual."
            % _et.lista(cur, schema, [n["id"] for n in candidate]),
            detalii={"note": [n["id"] for n in candidate]})

    # [lotul 13, deficiența 634 (c) — „Titlul notei include «altă livrare decât NIR-urile nelegate (confirmat)»”] titlul notei e al
    # documentului („Contare factura …”), nu al unei alegeri de pe ecran: confirmarea „altă livrare” rămâne în răspuns (`alta_livrare`)
    descriere = _descriere(f, data_nota, motiv_data)
    cur.execute("INSERT INTO %sinregistrari (data, factura_id, descriere, sursa, status) "
                "VALUES (%%s,%%s,%%s,'facturi','ciorna') RETURNING id" % _p(schema),
                (data_nota, factura_id, descriere))
    r = cur.fetchone()
    iid = r["id"] if isinstance(r, dict) else r[0]
    for n in note:
        cur.execute("INSERT INTO %sinregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                    "VALUES (%%s,%%s,%%s,%%s)" % _p(schema),
                    (iid, n["debit"], n["credit"], Decimal(str(n["suma"]))))
    stornare_nir = None
    if nir_ales and nir_ales.get("forma_noua"):
        from core import pdf_util as _pu
        _nl.leaga_forma_noua(cur, schema, nir_ales["id"], f)
        _nl.scrie_ajustari_cv(cur, schema, plan_cv, data_nota, iid, nir_ales["id"], factura_id,
                              "Diferență de preț NIR %s / factura %s" % (nir_ales["numar"], _pu.serie_nr(f.get("serie"), f.get("numar"))))
    elif nir_ales:
        stornare_nir = _nl.leaga(cur, schema, nir_ales["id"], f, data_nota)
    out = {"stare": "contata", "inregistrare_id": iid,
           "tva_la_incasare": regim_tva == _tvi.REGIM_INCASARE,
           # [lotul 11, 428] regimul complet (general / incasare / storno_incasare): stornarea unei facturi din sistem își spune pe ecran
           # împărțirea CF art.282 alin.(10) — `tva_la_incasare` e fals pe ea, deși nota e în sistem
           "regim_tva_incasare": regim_tva,
           "linii": [{"debit": n["debit"], "credit": n["credit"], "suma": str(n["suma"])}
                     for n in note]}
    if nir_ales:
        out["nir_legat"] = {"nir_id": nir_ales["id"], "numar": nir_ales["numar"], "stornare_id": stornare_nir,
                            "forma_noua": bool(nir_ales.get("forma_noua"))}
    if alta_livrare:
        out["alta_livrare"] = True
    if candidate:
        # Omul a cerut contarea explicit, deci se scrie — dar nu tăcut. Plasa oprește automatul;
        # pe om îl AVERTIZEAZĂ, fiindcă el are ce n-are automatul: contextul.
        # Avertismentul e o STRUCTURĂ, nu o propoziție: `cod` și `note` se pot verifica mecanic,
        # iar mesajul se poate rescrie fără ca nimic să cadă.
        out["avertisment"] = dict(
            _af.afirmatie(
                "neconformitate", "POSIBILA_DUBLARE",
                "există și note fără legătură de factură care se potrivesc pe sumă și lună "
                "(nota %s) — verifică să nu fie o a doua contare"
                % _et.lista(cur, schema, [n["id"] for n in candidate]),
                unde=_et.factura_din_rand(f),
                regula="o factură se contează o singură dată, oricare ar fi calea"),
            cod="POSIBILA_DUBLARE", note=[n["id"] for n in candidate])
    return out


def cursor_dict(conn):
    """Cursorul cerut de modul: rândurile se citesc pe NUME de coloană."""
    return conn.cursor(cursor_factory=RealDictCursor)
