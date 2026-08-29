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
from core import facturi as _fc
from core import nomenclator_status_factura as _nsf
from core.common import _q

# ── Conturile care fac o notă „de factură". Măsurate, nu presupuse — vezi BLOC BBB.
CONTURI_TERT = ("4111", "401", "404")
CONTURI_TVA = ("4426", "4427", "4428")
CONTURI_FOND_PREFIX = ("70", "6")
CONTURI_FOND_EXACT = ("371", "301", "302", "303", "213")
# [29.08.2026, BLOC GGG] Trezoreria TAIE semnătura de contare, și motivul e măsurat prin citirea
# codului, nu presupus: `reconciliere_api` adaugă pe nota de PLATĂ, la o firmă cu TVA la încasare, o
# linie `4428 = 4427` (emisă) sau `4426 = 4428` (primită) — art. 282 alin. 3 și 8. Nota devine atunci
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
    `TVA_LA_INCASARE_MANUAL` · `POSIBILA_DUBLARE`.
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


def note_cu_cheia(cur, schema, factura_id):
    """Toate notele care poartă `factura_id`, cu liniile lor și cu verdictul „e contare?"."""
    cur.execute("SELECT i.id, i.status, i.sursa, l.cont_debit, l.cont_credit, l.suma "
                "FROM %sinregistrari i "
                "LEFT JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                "WHERE i.factura_id = %%s ORDER BY i.id"
                % (_p(schema), _p(schema)), (factura_id,))
    note = {}
    for r in cur.fetchall():
        nid, status, sursa, cd, cc, suma = (r["id"], r["status"], r["sursa"], r["cont_debit"],
                                            r["cont_credit"], r["suma"]) if isinstance(r, dict) else r
        n = note.setdefault(nid, {"id": nid, "status": status, "sursa": sursa, "linii": []})
        if cd is not None:
            n["linii"].append((cd, cc, Decimal(str(suma or 0))))
    for n in note.values():
        n["e_contare"] = e_nota_de_contare(n["linii"])
    return list(note.values())


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
    if e_nota_de_contare(linii):
        raise RefuzContare(
            "E_NOTA_DE_CONTARE",
            "Nota #%d E chiar evidența contabilă a facturii, nu o plată. Nu se dezleagă: o cifră "
            "fără documentul care o justifică nu se mai poate desface. Dacă factura trebuie "
            "corectată, se stornează." % nota_id,
            detalii={"nota_id": nota_id, "factura_id": cap["factura_id"], "iesire": "storno"})
    cur.execute("UPDATE %sinregistrari SET factura_id = NULL WHERE id = %%s" % _p(schema),
                (nota_id,))
    return cap["factura_id"]


# ══════════════════════════════════════════════════════════ GENERAREA NOTEI
MSG_FARA_COTA = ("factura fără cotă de TVA pe linii — nu se poate genera nota "
                 "(declară cota pe factură)")

TEMEI_TVA_INCASARE = "Cod fiscal art. 297 alin. 2"

MSG_TVA_INCASARE = (
    "Furnizorul aplică TVA la încasare, iar firma e în regim normal: deducerea se amână până la "
    "plată (Cod fiscal art. 297 alin. 2), deci TVA-ul intră pe 4428, nu pe 4426, iar exigibilitatea "
    "vine din reconcilierea bancară — un act pe care automatul nu-l poate declanșa. Factura se "
    "contează din butonul de contabilizare, de către om.")


def e_clasa_ambigua_tva(f, tva_incasare_firma):
    """[FFF2] Furnizor la încasare + firmă în regim normal. **2 facturi** pe portofoliul de azi
    (`tenant_004` #9, `tenant_017` #8). Automatul refuză clasa asta; omul o poate conta."""
    return (f.get("directie") == "primita"
            and bool(f.get("furnizor_tva_incasare"))
            and not bool(tva_incasare_firma))


def genereaza_note(cur, schema, f, tva_incasare_firma, cont_venit_implicit, cont_cheltuiala=None):
    """Notele unei facturi, ca listă de dict {debit, credit, suma}. **PUR față de bază la scriere**:
    citește, nu scrie — tiparul NIR, unde validarea se termină înainte ca ceva să înceapă.

    `tva_incasare` nu mai e regimul PROPRIU al firmei aplicat pe amândouă direcțiile, cum era în rută:
    pe **primită** contează și `furnizor_tva_incasare`. Divergența cu D300 — care rutează deja pe
    câmpul ăla (`core/test_d300_b1_rutare.py`) — a fost măsurată pe 2 facturi înainte de reparație."""
    fid = f["id"]
    directie = f.get("directie")
    tvai = bool(tva_incasare_firma) or (directie == "primita" and bool(f.get("furnizor_tva_incasare")))
    la_data = str(f["data_emitere"])

    if directie == "emisa":
        cvi = cont_venit_implicit or "707"
        cur.execute("SELECT COALESCE(NULLIF(cont_venit,''), %%s) AS cv, cota_tva, "
                    "       COALESCE(SUM(cantitate*pret_unitar),0) AS baza "
                    "FROM %sfactura_linii WHERE factura_id=%%s "
                    "GROUP BY cv, cota_tva ORDER BY cv, cota_tva" % _p(schema), (cvi, fid))
        grupuri = [dict(r) for r in cur.fetchall()]
        total_baza = sum((Decimal(str(g["baza"] or 0)) for g in grupuri), Decimal(0))
        if total_baza == 0:
            # factură fără linii (legacy): cade pe antet, un singur cont.
            baza = (Decimal(str(f.get("total_lei") or f.get("total") or 0))
                    - Decimal(str(f.get("tva") or 0)))
            cur.execute("SELECT MAX(cota_tva) AS cota FROM %sfactura_linii WHERE factura_id=%%s"
                        % _p(schema), (fid,))
            r = cur.fetchone()
            cota_h = r["cota"] if isinstance(r, dict) else r[0]
            if cota_h is None:
                raise RefuzContare("FARA_COTA", MSG_FARA_COTA)
            return _fc.factura_emisa(baza, cota=Decimal(str(cota_h)) / 100, la_data=la_data,
                                     tva_incasare=tvai, cont_venit=cvi)
        if any(g["cota_tva"] is None for g in grupuri):
            raise RefuzContare("FARA_COTA", MSG_FARA_COTA)
        note = []
        for g in grupuri:
            note += _fc.factura_emisa(Decimal(str(g["baza"] or 0)),
                                      cota=Decimal(str(g["cota_tva"])) / 100, la_data=la_data,
                                      tva_incasare=tvai, cont_venit=g["cv"])
        return note

    cur.execute("SELECT COALESCE(SUM(cantitate*pret_unitar),0) AS baza, MAX(cota_tva) AS cota "
                "FROM %sfactura_linii WHERE factura_id=%%s" % _p(schema), (fid,))
    fl = cur.fetchone()
    baza = Decimal(str((fl["baza"] if isinstance(fl, dict) else fl[0]) or 0))
    cota = (fl["cota"] if isinstance(fl, dict) else fl[1])
    if baza == 0:
        baza = (Decimal(str(f.get("total_lei") or f.get("total") or 0))
                - Decimal(str(f.get("tva") or 0)))
    if cota is None:
        raise RefuzContare("FARA_COTA", MSG_FARA_COTA)
    cota = Decimal(str(cota)) / 100
    if f.get("taxare_inversa"):
        # art. 331: la beneficiar 4426 = 4427 (autocolectare), nu TVA pe 401. Funcția exista în
        # `core/facturi.py` de la început și nu o chema nimeni — cât timp contarea era un act rar,
        # nu se vedea. De când e automată, se vede la fiecare factură.
        return _fc.taxare_inversa(baza, cota=cota, la_data=la_data, cont=cont_cheltuiala or None)
    return _fc.factura_primita(baza, cota=cota, la_data=la_data, tva_incasare=tvai,
                               cont=cont_cheltuiala or None)


def _descriere(f, data_nota=None, motiv_data=None):
    """Descrierea notei. Cand nota NU poarta data emiterii, descrierea o SPUNE, cu motivul.

    [JJJ2] *„nu doar o dată arbitrară"*: o notă datată altfel decât faptul pe care îl înregistrează
    trebuie să poarte legătura, altfel peste șase luni nimeni nu mai poate spune de ce e acolo.
    Legătura structurală există deja — `factura_id`, iar `jurnal_api.document_justificativ` derivă
    din ea *„Factură <serie><număr> din <data>"*. Mențiunea de aici e pentru omul care citește nota,
    nu pentru mașină."""
    serie, numar = f.get("serie"), f.get("numar") or f["id"]
    nr = numar if (serie and str(numar).startswith(str(serie))) else "%s%s" % (serie or "", numar)
    baza = "Contare factura %s" % nr
    if data_nota is not None and str(data_nota)[:10] != str(f["data_emitere"])[:10]:
        baza += " din %s — inregistrata la %s" % (str(f["data_emitere"])[:10], str(data_nota)[:10])
        if motiv_data:
            baza += ": %s" % motiv_data
    return baza[:200]


def contabilizeaza(cur, schema, factura_id, automat, cont_cheltuiala=None,
                   data_nota=None, motiv_data=None):
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
    """
    cur.execute("SELECT * FROM %sfacturi WHERE id=%%s" % _p(schema), (factura_id,))
    f = cur.fetchone()
    if not f:
        raise RefuzContare("INEXISTENTA", "factură inexistentă")
    f = dict(f)

    if (f.get("tip") or "factura") != "factura":
        raise RefuzContare("NU_E_DOCUMENT_FISCAL",
                           "proforma/avizul nu se contabilizează (nu e document fiscal)")

    # [EEE3 / FFF3] IDEMPOTENȚĂ: a doua chemare pe o factură deja contată e NO-OP, nu a doua notă
    # și nici eroare. Refuzul era corect, prezentarea lui nu — `422` face un comportament corect să
    # arate ca un defect.
    ex = contare_existenta(cur, schema, factura_id)
    if ex:
        return {"stare": "deja_contata", "inregistrare_id": ex["id"], "linii": [],
                "afirmatie": _af.afirmatie(
                    "neconformitate", "CONTARE_EXISTENTA",
                    "factura are deja notă de contare (#%d); a doua chemare nu face nimic"
                    % ex["id"],
                    unde="factura #%s" % factura_id, regula="o factură are o singură contare")}

    data_nota = data_nota or f.get("data_emitere")
    if luna_blocata(cur, schema, data_nota):
        raise RefuzContare(
            "LUNA_INCHISA",
            "luna în care ar intra nota (%s) e închisă; redeschide-o, sau contează la o dată "
            "deschisă, cu mențiunea care leagă nota de factură" % str(data_nota)[:10],
            detalii={"data_nota": str(data_nota)[:10],
                     "data_emitere": str(f.get("data_emitere"))[:10]})

    cur.execute("SELECT COALESCE(tva_la_incasare,false) AS tvai, cont_venit_implicit "
                "FROM %sfirma_profil WHERE id=1" % _p(schema))
    prof = cur.fetchone()
    prof = dict(prof) if prof else {"tvai": False, "cont_venit_implicit": None}

    if automat and e_clasa_ambigua_tva(f, prof.get("tvai")):
        raise RefuzContare("TVA_LA_INCASARE_MANUAL", MSG_TVA_INCASARE,
                           detalii={"cont_tva": "4428", "temei": TEMEI_TVA_INCASARE,
                                    "iesire": "contabilizare_manuala"})

    if cont_cheltuiala is None and f.get("directie") == "primita":
        cur.execute("SELECT cont_cheltuiala FROM %sefactura_primite WHERE factura_id=%%s "
                    "AND cont_cheltuiala IS NOT NULL ORDER BY id DESC LIMIT 1" % _p(schema),
                    (factura_id,))
        r = cur.fetchone()
        if r:
            cont_cheltuiala = (r["cont_cheltuiala"] if isinstance(r, dict) else r[0]) or None

    note = genereaza_note(cur, schema, f, prof.get("tvai"), prof.get("cont_venit_implicit"),
                          cont_cheltuiala=cont_cheltuiala)

    # [DDD2] PLASA, ultima verificare înainte de scriere.
    candidate = candidate_fara_cheie(cur, schema, f)
    if candidate and automat:
        raise RefuzContare(
            "POSIBILA_DUBLARE",
            "există deja o notă care pare să conteze factura asta, fără să o numească "
            "(#%s). Nu se scrie automat: leag-o sau contează manual."
            % ", #".join(str(n["id"]) for n in candidate),
            detalii={"note": [n["id"] for n in candidate]})

    cur.execute("INSERT INTO %sinregistrari (data, factura_id, descriere, sursa, status) "
                "VALUES (%%s,%%s,%%s,'facturi','ciorna') RETURNING id" % _p(schema),
                (data_nota, factura_id, _descriere(f, data_nota, motiv_data)))
    r = cur.fetchone()
    iid = r["id"] if isinstance(r, dict) else r[0]
    for n in note:
        cur.execute("INSERT INTO %sinregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                    "VALUES (%%s,%%s,%%s,%%s)" % _p(schema),
                    (iid, n["debit"], n["credit"], Decimal(str(n["suma"]))))
    out = {"stare": "contata", "inregistrare_id": iid,
           "tva_la_incasare": bool(prof.get("tvai")) or bool(f.get("furnizor_tva_incasare")),
           "linii": [{"debit": n["debit"], "credit": n["credit"], "suma": str(n["suma"])}
                     for n in note]}
    if candidate:
        # Omul a cerut contarea explicit, deci se scrie — dar nu tăcut. Plasa oprește automatul;
        # pe om îl AVERTIZEAZĂ, fiindcă el are ce n-are automatul: contextul.
        # Avertismentul e o STRUCTURĂ, nu o propoziție: `cod` și `note` se pot verifica mecanic,
        # iar mesajul se poate rescrie fără ca nimic să cadă.
        out["avertisment"] = dict(
            _af.afirmatie(
                "neconformitate", "POSIBILA_DUBLARE",
                "există și note fără legătură de factură care se potrivesc pe sumă și lună "
                "(#%s) — verifică să nu fie o a doua contare"
                % ", #".join(str(n["id"]) for n in candidate),
                unde="factura #%s" % factura_id,
                regula="o factură se contează o singură dată, oricare ar fi calea"),
            cod="POSIBILA_DUBLARE", note=[n["id"] for n in candidate])
    return out


def cursor_dict(conn):
    """Cursorul cerut de modul: rândurile se citesc pe NUME de coloană."""
    return conn.cursor(cursor_factory=RealDictCursor)
