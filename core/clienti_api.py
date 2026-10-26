"""
core/clienti_api.py — clienți/parteneri în schema unui tenant: listă, creare,
detalii, editare, ștergere. Rulează pe conexiunea poziționată pe schema tenantului.

Fără logică de business (doar date) — nu există parte „pură" de calcul.
Ștergerea e PROTEJATĂ: dacă clientul are facturi, refuz curat (nu las FK-ul să
arunce un 500 urât și să strice tranzacția).
"""
from __future__ import annotations

from core import chei_unice as _chei
from core import cui_forma as _cf
from core.common import cate as _cate

REGULI = "2026.1"
MODUL = "clienti_api"

_CAMPURI = ("nume", "cui", "adresa", "email", "telefon",
            "oras", "judet", "cod_postal", "status", "afiliat")
#: [lotul 11, decizia Costin 10.3 pct.4] fișa furnizorului: aceleași date ca a clientului, fără bifa „persoană afiliată” (care e a
#: livrărilor — CF art.282 alin.(6) lit.d)
_CAMPURI_FURNIZORI = ("nume", "cui", "adresa", "email", "telefon", "oras", "judet", "cod_postal", "status")

#: [lotul 10, deficiența 428, decizia Costin 20.10.2026 „Bifă pe client”] CUI-ul comparat fără spații și fără prefixul RO (clientul scris
#: „RO 18547290” e același cu factura către „18547290”). [lotul 11, decizia 10.3] forma unică: `cui_forma.SQL`
_CUI_SQL = _cf.SQL


# ============================================================
#  [lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”] „Localitatea și județul la PF și la firmele neînregistrate
#  se completează în fișa partenerului; refuzul declarației trimite direct acolo.” și „CUI-ul se păstrează fără «RO» și fără spații”.
# ============================================================
def _judet_cod(v):
    """Județul fișei, păstrat ca pe factură (`facturi.tert_judet`): codul ISO 3166-2:RO („B”, „CJ”), aceeași listă ca factura
    (`factura_pdf.JUDETE_NUME`) și ca D394 (`d394.JUDETE_SIRUTA`). Numele județului („Cluj”) e primit și trecut în cod; altceva = refuz."""
    from core.factura_pdf import JUDETE_NUME
    t = str(v or "").strip()
    if not t:
        return None
    if t.upper() in JUDETE_NUME:
        return t.upper()
    import unicodedata
    _f = lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().upper().replace("-", " ").strip()   # noqa: E731
    for cod, nume in JUDETE_NUME.items():
        if _f(nume) == _f(t):
            return cod
    raise ValueError("Județul %r nu e în listă: alege-l din listă (ex. Cluj, București)." % t)


#: [440] Lungimea maximă a câmpurilor de text ale fișei (tenant_template.sql, tabelele `clienti` și `furnizori`, aceleași coloane): o valoare
#: mai lungă cădea în INSERT / UPDATE (DataError -> 500, „eroare internă”). Acum se refuză lângă câmpul ei, împreună cu celelalte. Gard:
#: `core/test_lot11_w3b_clienti.py` (confruntă limitele cu schema bazei).
LUNGIMI = {"nume": 255, "cui": 20, "email": 255, "telefon": 50, "oras": 100, "cod_postal": 20}
_ETICHETE = {"nume": "Numele", "cui": "Codul fiscal", "email": "Emailul", "telefon": "Telefonul", "oras": "Localitatea",
             "cod_postal": "Codul poștal"}


def _curata(campuri, permise, er):
    """Câmpurile trimise, în forma păstrată: textul fără spații la capete (gol -> None), CUI-ul prin `cui_forma.stocare`, județul ca
    cod. [440] Fiecare valoare refuzată (județul necunoscut, textul peste coloană) se ADAUGĂ în `er` (`core.erori.ErorileFormularului`),
    cu `camp` = numele din cerere (ecranul Clienți / Furnizori îl pune lângă câmpul rândului), nu se ridică la prima."""
    out = {}
    for k in permise:
        if k not in campuri or campuri[k] is None:
            continue
        v = campuri[k]
        if k == "cui":
            v = _cf.stocare(v)
        elif k == "judet":
            try:
                v = _judet_cod(v)
            except ValueError as e:
                er.camp("judet", str(e))
                continue
        elif isinstance(v, str):
            v = v.strip() or None
        if k in LUNGIMI and v is not None and len(str(v)) > LUNGIMI[k]:
            er.camp(k, "%s are cel mult %s; are %d." % (_ETICHETE[k], _cate(LUNGIMI[k], "caracter", "caractere"), len(str(v))))
            continue
        out[k] = v
    return out


def _fisa(campuri, permise, titlu, mesaj_nume, la_creare=True):
    """[440, comanda Costin 11.1 pct.16] Fișa partenerului judecată întreagă: numele (obligatoriu la creare; la editare numai dacă e
    trimis), județul și lungimile, TOATE deodată (`core.erori.ErorileFormularului`), fiecare cu `camp` = numele din cerere — ecranul
    Clienți / Furnizori îl pune lângă câmpul rândului (`${P}-${camp}-${cheie}`). Înainte: numele lipsă oprea tot, iar o localitate peste
    coloană cădea în INSERT (500). Refuzul = `DateInvalide` (422, ca refuzul pe câmp de până acum)."""
    from core.erori import ErorileFormularului as _Erori
    er = _Erori(titlu + " nu s-a salvat")
    c = _curata(campuri, permise, er)
    if (la_creare or campuri.get("nume") is not None) and not str(c.get("nume") or "").strip() and not any(
            x["camp"] == "nume" for x in er.campuri):
        er.camp("nume", mesaj_nume)
    er.refuza()
    return c


def cheie_partener(cui, nume):
    """Identitatea partenerului pe ecranul fișelor, aceeași pe toate drumurile (fișă, factură, refuzul unei declarații): CUI-ul păstrat
    (`cui-<cod>`), altfel numele (`nume-<NUME>`, fără diacritice, litere și cifre) — persoana fizică / firma fără cod."""
    import re
    import unicodedata
    c = _cf.stocare(cui)
    if c:
        return "cui-" + re.sub(r"[^A-Z0-9]", "", c.upper())
    n = unicodedata.normalize("NFKD", str(nume or "")).encode("ascii", "ignore").decode().upper()
    n = re.sub(r"[^A-Z0-9]+", "_", n).strip("_")
    return ("nume-" + n) if n else None


def nume_diferit(nume_fisa, denumire_anaf):
    """[lotul 11, deficiența 444] Numele din fișă diferă de cel de la ANAF? Se compară fără majuscule / diacritice / puncte / spații în
    plus („S.R.L.” = „SRL”); un nume gol de oricare parte nu e o diferență (nu e nimic de propus)."""
    import re
    import unicodedata

    def _n(x):
        x = unicodedata.normalize("NFKD", str(x or "")).encode("ascii", "ignore").decode().upper()
        return re.sub(r"\s+", " ", re.sub(r"[.,]", "", x)).strip()
    a, b = _n(nume_fisa), _n(denumire_anaf)
    return bool(a and b and a.replace(" ", "") != b.replace(" ", ""))


# ============================================================
#  LISTĂ
# ============================================================
_COLOANE_LISTA = "id, nume, cui, adresa, email, telefon, oras, judet, cod_postal, status"


def _lista(conn, sql, val):
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(sql, val)
        out = [dict(r) for r in cur.fetchall()]
    for r in out:
        r["cheie"] = cheie_partener(r.get("cui"), r.get("nume"))
    return out


#: [lotul 13, deficiențele 632 / 640] fișa „pereche” a aceluiași partener (client <-> furnizor): aceeași firmă / persoană, deci aceeași
#: localitate și același județ — „Același partener (DANTE) are două fișe separate, client și furnizor, cu localitatea de completat de două
#: ori (la furnizor era goală, deși aplicația o știa).”
PERECHE = {"clienti": "furnizori", "furnizori": "clienti"}


def _sql_lista(fel, extra=""):
    """SELECT-ul listei de fișe `fel`: coloanele fișei + [632 a] numărul facturilor partenerului (emise la client, primite / borderouri la
    furnizor; după `client_id`, același CUI sau, fără CUI, același nume — ca `sql_camp_fisa`) + [640] localitatea și județul din fișa
    pereche cu același CUI (`oras_pereche`, `judet_pereche`)."""
    cui_f, cui_p = _CUI_SQL.format(c="f.tert_cui"), _CUI_SQL.format(c="p.cui")
    leg = ("(%(cf)s <> '' AND %(cf)s = %(cp)s) OR (%(cp)s = '' AND %(cf)s = '' AND upper(btrim(COALESCE(f.tert_nume, ''))) = "
           "upper(btrim(p.nume)))" % {"cf": cui_f, "cp": cui_p})
    if fel == "clienti":
        leg = "f.client_id = p.id OR " + leg
    cui_q = _CUI_SQL.format(c="q.cui")
    return ("SELECT p.id, p.nume, p.cui, p.adresa, p.email, p.telefon, p.oras, p.judet, p.cod_postal, p.status" + extra + ", "
            "(SELECT count(*) FROM facturi f WHERE " + _FACTURI_FEL[fel] + " AND (" + leg + ")) AS facturi, "
            "(SELECT NULLIF(btrim(q.oras), '') FROM " + PERECHE[fel] + " q WHERE " + cui_p + " <> '' AND " + cui_q + " = " + cui_p
            + " ORDER BY q.id LIMIT 1) AS oras_pereche, "
            "(SELECT NULLIF(btrim(q.judet), '') FROM " + PERECHE[fel] + " q WHERE " + cui_p + " <> '' AND " + cui_q + " = " + cui_p
            + " ORDER BY q.id LIMIT 1) AS judet_pereche "
            "FROM " + fel + " p")


def lista_clienti(conn, status=None):
    """Toți clienții, opțional filtrați pe status (activ/inactiv). [lotul 13, 632 / 640] cu numărul facturilor emise către fiecare și cu
    localitatea / județul din fișa de furnizor a aceluiași CUI (`oras_pereche`, `judet_pereche`)."""
    cond, val = "", []
    if status is not None:
        cond = " WHERE p.status = %s"; val.append(status)
    return _lista(conn, _sql_lista("clienti", ", p.afiliat") + cond + " ORDER BY p.nume", val)


def lista_furnizori(conn, status=None):
    """[lotul 11, decizia 10.3] Toți furnizorii (fișele), opțional filtrați pe status. [lotul 13, 632 / 640] cu numărul facturilor primite
    (și al borderourilor) și cu localitatea / județul din fișa de client a aceluiași CUI."""
    cond, val = "", []
    if status is not None:
        cond = " WHERE p.status = %s"; val.append(status)
    return _lista(conn, _sql_lista("furnizori") + cond + " ORDER BY p.nume", val)


def sincronizeaza_pereche(conn, fel, cui, oras=None, judet=None, campuri=("oras", "judet")):
    """[lotul 13, 640] Localitatea / județul scrise pe fișa `fel` trec și pe fișa pereche a aceluiași CUI (același partener: client și
    furnizor), ca să nu se completeze de două ori. Numai câmpurile trimise (`campuri`); fără CUI (persoane fizice: numele nu e o cheie
    sigură între cele două liste) nu se atinge nimic. Întoarce numărul fișelor pereche actualizate."""
    c = _cf.stocare(cui)
    seturi, val = [], []
    for k, v in (("oras", oras), ("judet", judet)):
        if k in campuri:
            seturi.append("%s = %%s" % k); val.append(v)
    if not c or not seturi:
        return 0
    with conn.cursor() as cur:
        cur.execute("UPDATE " + PERECHE[fel] + " SET " + ", ".join(seturi) + " WHERE " + _CUI_SQL.format(c="cui") + " = %s", val + [c])
        return cur.rowcount


# ============================================================
#  CREARE
# ============================================================
def creeaza_client(conn, nume, cui=None, adresa=None, email=None, telefon=None,
                   oras=None, judet=None, cod_postal=None, status="activ", afiliat=False):
    """Inserează un client. Întoarce {ok, client_id}. `afiliat` = persoană afiliată (Cod fiscal art.7 pct.26) — CF art.282 alin.(6) lit.d."""
    c = _fisa({"nume": nume, "cui": cui, "adresa": adresa, "email": email, "telefon": telefon, "oras": oras, "judet": judet,
               "cod_postal": cod_postal}, _CAMPURI, "Fișa clientului", "Scrie numele clientului: fără el, fișa nu se poate salva.")
    with conn.cursor() as cur:
        # [lotul 10, C73] un CUI deja în nomenclator -> refuzul numit, cu clientul existent (nu `500` din `clienti_cui_uniq`)
        with _chei.refuza_dublura(cur, (CONSTRANGERE_CUI,), _refuz_cui(None)):
            cur.execute(
                "INSERT INTO clienti (nume, cui, adresa, email, telefon, oras, judet, "
                "cod_postal, status, afiliat) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (c["nume"], c.get("cui"), c.get("adresa"), c.get("email"), c.get("telefon"), c.get("oras"), c.get("judet"),
                 c.get("cod_postal"), status, bool(afiliat)))
            client_id = cur.fetchone()[0]
    _sincronizeaza_dupa(conn, "clienti", c)   # [lotul 13, 640]
    return {"ok": True, "client_id": client_id}


def creeaza_furnizor(conn, nume, cui=None, adresa=None, email=None, telefon=None,
                     oras=None, judet=None, cod_postal=None, status="activ"):
    """[lotul 11, decizia 10.3] Inserează fișa unui furnizor. Întoarce {ok, furnizor_id}."""
    c = _fisa({"nume": nume, "cui": cui, "adresa": adresa, "email": email, "telefon": telefon, "oras": oras, "judet": judet,
               "cod_postal": cod_postal}, _CAMPURI_FURNIZORI, "Fișa furnizorului",
              "Scrie numele furnizorului: fără el, fișa nu se poate salva.")
    with conn.cursor() as cur:
        with _chei.refuza_dublura(cur, (CONSTRANGERE_CUI_FURNIZOR,), _refuz_cui_furnizor(None)):
            cur.execute(
                "INSERT INTO furnizori (nume, cui, adresa, email, telefon, oras, judet, cod_postal, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (c["nume"], c.get("cui"), c.get("adresa"), c.get("email"), c.get("telefon"), c.get("oras"), c.get("judet"),
                 c.get("cod_postal"), status))
            furnizor_id = cur.fetchone()[0]
    _sincronizeaza_dupa(conn, "furnizori", c)   # [lotul 13, 640]
    return {"ok": True, "furnizor_id": furnizor_id}


#: cheia naturală a clientului (`core/migrare_intrare_date_garduri.UNIQUE`): un CUI = o singură fișă de client
CONSTRANGERE_CUI = "clienti_cui_uniq"
#: [lotul 11] la fel la furnizori (`furnizori_cui_uniq`, tenant_template.sql)
CONSTRANGERE_CUI_FURNIZOR = "furnizori_cui_uniq"


def _refuz_cui(client_id):
    """[lotul 10, C73] Refuzul CUI-ului dublat, cu clientul care îl are deja: numele lui și id-ul fișei (`existent`), ca ecranul să
    poată duce la el. `client_id` = fișa editată (None la creare)."""
    def refuz(cur, e):
        cur.execute("SELECT id, nume, cui FROM clienti WHERE cui = %s AND id IS DISTINCT FROM %s ORDER BY id LIMIT 1",
                    (_chei.valoarea(e), client_id))
        r = cur.fetchone()
        if not r:   # cheia citită din detaliul bazei nu mai găsește rândul (șters între timp): spunem valoarea, fără nume
            return _chei.CheieDublata("Există deja un client cu CUI-ul %s. Un CUI are o singură fișă de client."
                                      % (_chei.valoarea(e) or ""), valoare=_chei.valoarea(e), camp="cui")
        ce = "Nu se creează a doua fișă pentru același CUI" if client_id is None else "Un CUI aparține unei singure fișe de client"
        return _chei.CheieDublata(
            "Există deja clientul %s cu CUI-ul %s (în lista Clienți). %s: deschide fișa existentă și schimbă acolo ce ai de schimbat."
            % (r[1], r[2], ce), valoare=r[2], existent={"client_id": r[0], "nume": r[1]}, camp="cui")
    return refuz


def _refuz_cui_furnizor(furnizor_id):
    """[lotul 11] Refuzul CUI-ului dublat pe fișele de furnizor, cu furnizorul care îl are deja (ca `_refuz_cui`)."""
    def refuz(cur, e):
        cur.execute("SELECT id, nume, cui FROM furnizori WHERE cui = %s AND id IS DISTINCT FROM %s ORDER BY id LIMIT 1",
                    (_chei.valoarea(e), furnizor_id))
        r = cur.fetchone()
        if not r:
            return _chei.CheieDublata("Există deja un furnizor cu CUI-ul %s. Un CUI are o singură fișă de furnizor."
                                      % (_chei.valoarea(e) or ""), valoare=_chei.valoarea(e), camp="cui")
        return _chei.CheieDublata(
            "Există deja furnizorul %s cu CUI-ul %s (în lista Furnizori): deschide fișa existentă și schimbă acolo ce ai de schimbat."
            % (r[1], r[2]), valoare=r[2], existent={"furnizor_id": r[0], "nume": r[1]}, camp="cui")
    return refuz


# ============================================================
#  DETALII
# ============================================================
def detalii_client(conn, client_id):
    """Un client complet, sau None."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, nume, cui, adresa, email, telefon, oras, judet, "
            "cod_postal, status, afiliat FROM clienti WHERE id = %s", (client_id,))
        r = cur.fetchone()
    return dict(r) if r else None


def detalii_furnizor(conn, furnizor_id):
    """[lotul 11] Un furnizor complet, sau None."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT " + _COLOANE_LISTA + " FROM furnizori WHERE id = %s", (furnizor_id,))
        r = cur.fetchone()
    return dict(r) if r else None


# ============================================================
#  EDITARE (doar câmpurile trimise)
# ============================================================
def actualizeaza_client(conn, client_id, **campuri):
    """Editează doar câmpurile date (din _CAMPURI). Întoarce {ok}. [lotul 11] CUI-ul fără „RO” / spații, județul ca cod (`_curata`);
    un câmp trimis gol („”) golește câmpul (localitatea, județul); `None` înseamnă „netrimis”."""
    c = _fisa(campuri, _CAMPURI, "Fișa clientului", "Numele clientului nu poate rămâne gol.", la_creare=False)
    seturi, valori = [], []
    for k in _CAMPURI:
        if k in c:
            seturi.append("%s = %%s" % k); valori.append(c[k])
    if not seturi:
        return {"ok": True, "neschimbat": True}
    valori.append(client_id)
    with conn.cursor() as cur:
        # [lotul 10, C73] CUI-ul schimbat pe unul care e deja al altui client -> același refuz numit ca la creare
        with _chei.refuza_dublura(cur, (CONSTRANGERE_CUI,), _refuz_cui(client_id)):
            cur.execute("UPDATE clienti SET %s WHERE id = %%s" % ", ".join(seturi), valori)
            ok = cur.rowcount > 0
    if ok:
        _sincronizeaza_dupa(conn, "clienti", c, client_id)   # [lotul 13, 640]
    return {"ok": ok}


def actualizeaza_furnizor(conn, furnizor_id, **campuri):
    """[lotul 11, decizia 10.3] Editează fișa furnizorului (doar câmpurile date, ca `actualizeaza_client`)."""
    c = _fisa(campuri, _CAMPURI_FURNIZORI, "Fișa furnizorului", "Numele furnizorului nu poate rămâne gol.", la_creare=False)
    seturi, valori = [], []
    for k in _CAMPURI_FURNIZORI:
        if k in c:
            seturi.append("%s = %%s" % k); valori.append(c[k])
    if not seturi:
        return {"ok": True, "neschimbat": True}
    valori.append(furnizor_id)
    with conn.cursor() as cur:
        with _chei.refuza_dublura(cur, (CONSTRANGERE_CUI_FURNIZOR,), _refuz_cui_furnizor(furnizor_id)):
            cur.execute("UPDATE furnizori SET %s WHERE id = %%s" % ", ".join(seturi), valori)
            ok = cur.rowcount > 0
    if ok:
        _sincronizeaza_dupa(conn, "furnizori", c, furnizor_id)   # [lotul 13, 640]
    return {"ok": ok}


def _sincronizeaza_dupa(conn, fel, c, fisa_id=None):
    """[lotul 13, 640] După scrierea fișei `fel` (câmpurile curățate `c`): localitatea / județul scrise trec pe fișa pereche cu același
    CUI (CUI-ul din cerere, altfel cel al fișei)."""
    campuri = tuple(k for k in ("oras", "judet") if k in c)
    if not campuri:
        return 0
    cui = c.get("cui")
    if not cui and fisa_id is not None:
        with conn.cursor() as cur:
            cur.execute("SELECT cui FROM " + fel + " WHERE id = %s", (fisa_id,))
            r = cur.fetchone()
            cui = (r[0] if not isinstance(r, dict) else r["cui"]) if r else None
    return sincronizeaza_pereche(conn, fel, cui, c.get("oras"), c.get("judet"), campuri)


# ============================================================
#  ȘTERGERE — protejată (refuz dacă are facturi)
# ============================================================
def sterge_client(conn, client_id):
    """
    Șterge clientul DOAR dacă nu are facturi legate (FK ar bloca oricum).
    Verific întâi, ca să întorc mesaj clar fără să stric tranzacția.
    [lotul 13, 640] „facturi legate” = cele numărate în listă (`client_id`, același CUI sau, fără CUI, același nume): fișa unui client cu
    facturi ține localitatea și județul pe care D394 / D406 le citesc din ea (`sql_camp_fisa`), deci nu se șterge.
    """
    return _sterge_fisa(conn, "clienti", client_id)


def sterge_furnizor(conn, furnizor_id):
    """[lotul 13, 640] Fișa furnizorului se șterge numai fără facturi primite / borderouri (aceeași regulă ca `sterge_client`)."""
    return _sterge_fisa(conn, "furnizori", furnizor_id)


def _sterge_fisa(conn, fel, fisa_id):
    ce = "clientul" if fel == "clienti" else "furnizorul"
    with conn.cursor() as cur:
        cur.execute(_sql_lista(fel) + " WHERE p.id = %s", (fisa_id,))
        r = cur.fetchone()
        if not r:
            return {"ok": False, "cod": "INEXISTENT", "mesaj": "Fișa nu mai există."}
        nr = r["facturi"] if isinstance(r, dict) else r[10]
        if nr:
            return {"ok": False, "cod": "ARE_FACTURI",
                    "mesaj": "%s are %s — fișa nu se șterge: localitatea și județul din ea intră în D394 / D406." % (
                        ce[0].upper() + ce[1:], _cate(nr, "factură", "facturi"))}
        cur.execute("DELETE FROM " + fel + " WHERE id = %s", (fisa_id,))
        sters = cur.rowcount > 0
    return {"ok": sters}


# ============================================================
#  PERSOANA AFILIATĂ (lotul 10, deficiența 428)
# ============================================================
def client_afiliat(cur, client_id=None, cui=None):
    """Beneficiarul e persoană afiliată (bifa clientului)? Clientul ales (`client_id`) sau, fără el, clientul cu același CUI (emiterea scrie
    numai CUI-ul). CF art.282 alin.(6) lit.d): sistemul TVA la încasare nu se aplică pentru „livrările de bunuri/prestările de servicii
    pentru care beneficiarul este o persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26”. Fără client găsit: False."""
    if client_id is None and not str(cui or "").strip():
        return False
    cur.execute("SELECT COALESCE(bool_or(afiliat), false) FROM clienti WHERE id = %s OR (%s::int IS NULL AND %s <> '' AND "
                + _CUI_SQL.format(c="cui") + " = " + _CUI_SQL.format(c="%s") + ")",
                (client_id, client_id, str(cui or "").strip(), str(cui or "")))
    r = cur.fetchone()
    return bool(r["coalesce"] if isinstance(r, dict) else r[0])


#: [lotul 11, decizia 10.3] facturile din care se ia partenerul fără fișă: emise -> clienți; primite (și borderourile de achiziție de la
#: persoane fizice) -> furnizori
_FACTURI_FEL = {"clienti": "f.directie = 'emisa' AND COALESCE(f.tip, 'factura') = 'factura'",
                "furnizori": "f.directie = 'primita' AND COALESCE(f.tip, 'factura') IN ('factura', 'borderou')"}


def parteneri_fara_fisa(conn, fel="clienti"):
    """Partenerii facturilor care n-au încă fișă (`clienti` / `furnizori`): cei cu CUI (CUI-ul lor nu e în fișe) și, [lotul 11, decizia
    10.3] cei FĂRĂ cod — persoane fizice, firme neînregistrate — după nume (nicio fișă fără CUI cu același nume). [{cui, nume, facturi,
    oras, judet, cheie}]: cel mai recent nume al partenerului, iar localitatea și județul de pe cea mai nouă factură care le are —
    ca PROPUNERE pe ecran (fișa se creează numai la „Salvează”)."""
    import psycopg2.extras as _E
    cui = _CUI_SQL.format(c="f.tert_cui")
    grup = "CASE WHEN " + cui + " <> '' THEN 'c' || " + cui + " ELSE 'n' || upper(btrim(COALESCE(f.tert_nume, ''))) END"
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT max(" + cui + ") AS cui, "
                    "(array_agg(f.tert_nume ORDER BY f.data_emitere DESC, f.id DESC))[1] AS nume, count(*) AS facturi, "
                    "(array_agg(NULLIF(btrim(f.tert_oras), '') ORDER BY f.data_emitere DESC, f.id DESC) "
                    " FILTER (WHERE NULLIF(btrim(f.tert_oras), '') IS NOT NULL))[1] AS oras, "
                    "(array_agg(NULLIF(btrim(f.tert_judet), '') ORDER BY f.data_emitere DESC, f.id DESC) "
                    " FILTER (WHERE NULLIF(btrim(f.tert_judet), '') IS NOT NULL))[1] AS judet "
                    "FROM facturi f WHERE " + _FACTURI_FEL[fel] + " AND (" + cui + " <> '' OR btrim(COALESCE(f.tert_nume, '')) <> '') "
                    "AND NOT EXISTS (SELECT 1 FROM " + fel + " p WHERE (" + cui + " <> '' AND " + _CUI_SQL.format(c="p.cui") + " = " + cui
                    + ") OR (" + cui + " = '' AND " + _CUI_SQL.format(c="p.cui") + " = '' AND upper(btrim(p.nume)) = "
                    "upper(btrim(f.tert_nume)))) "
                    "GROUP BY " + grup + " ORDER BY 2, 1")
        out = [dict(r) for r in cur.fetchall()]
    # [lotul 13, 640] fără localitate / județ pe facturi: cele din fișa pereche a aceluiași CUI (clientul care e și furnizor), ca propunere
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        for r in out:
            if r["cui"] and not (r["oras"] and r["judet"]):
                cur.execute("SELECT NULLIF(btrim(oras), '') AS oras, NULLIF(btrim(judet), '') AS judet FROM " + PERECHE[fel] + " WHERE "
                            + _CUI_SQL.format(c="cui") + " = %s ORDER BY id LIMIT 1", (r["cui"],))
                q = cur.fetchone()
                if q:
                    r["oras"], r["judet"] = r["oras"] or q["oras"], r["judet"] or q["judet"]
    for r in out:
        r["cui"] = r["cui"] or None
        r["cheie"] = cheie_partener(r["cui"], r["nume"])
    return out


def furnizor_sterge_uc(tenant_id, furnizor_id, ctx):
    """[lotul 13, 640] Corpul rutei `DELETE /tenants/{tenant_id}/furnizori/{furnizor_id}` (ca `uc_tenants.client_sterge`)."""
    from core import db, erori as _erori, uc_comun as _uc
    schema = _uc._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = sterge_furnizor(conn, furnizor_id)
    if not r.get("ok"):
        if r.get("cod") == "INEXISTENT":
            raise _erori.Inexistent(r["mesaj"])
        raise _erori.Conflict(r["mesaj"])
    return r


def fise_dupa_cui(cur, cui):
    """[lotul 11, deficiența 444] Fișele (client și / sau furnizor) care au acest CUI: [{fel, id, nume}]."""
    c = _cf.stocare(cui)
    if not c:
        return []
    out = []
    for fel in ("clienti", "furnizori"):
        cur.execute("SELECT id, nume FROM " + fel + " WHERE " + _CUI_SQL.format(c="cui") + " = %s ORDER BY id", (c,))
        for r in cur.fetchall():
            r = r if isinstance(r, (tuple, list)) else (r["id"], r["nume"])
            out.append({"fel": fel, "id": r[0], "nume": r[1]})
    return out


def compara_cu_anaf(cur, cui, denumire_anaf):
    """[lotul 11, deficiența 444, comanda Costin 11.1 pct.20, verbatim: „când numele de la ANAF diferă de fișa partenerului, se spune și
    se propune actualizarea.”] Fișele partenerului cu acest CUI, fiecare cu `diferit` (numele ei ≠ denumirea ANAF, `nume_diferit`), și
    mesajul de spus, când diferă. Sursa unică pentru toate drumurile care verifică partenerul la ANAF (fișa, factura, NIR, casa —
    răspunsul `verifica-cui`)."""
    fise = [dict(f, diferit=nume_diferit(f["nume"], denumire_anaf)) for f in fise_dupa_cui(cur, cui)]
    dif = [f for f in fise if f["diferit"]]
    mesaj = None
    if dif:
        mesaj = "Numele de la ANAF (%s) diferă de fișa %s: %s. Actualizează fișa cu numele de la ANAF, dacă e cel corect." % (
            denumire_anaf, "clientului" if dif[0]["fel"] == "clienti" else "furnizorului", dif[0]["nume"])
    return {"fise": fise, "nume_diferit": bool(dif), "mesaj_nume": mesaj}


def sql_camp_fisa(camp, f="f"):
    """[lotul 11, decizia Costin 10.3 pct.4: „declarațiile citesc din fișă când factura nu are”] Subinterogare SQL scalară: `camp`
    („oras” / „judet”) din fișa partenerului facturii cu aliasul `f` — fișa clientului la facturile emise (`client_id`, altfel același CUI,
    altfel, fără CUI, același nume), a furnizorului la cele primite (același CUI, altfel același nume). NULL fără fișă / câmp gol. Sursa
    unică pentru generatoare (`repo_d394`, D406 prin `repo_d406.parteneri_si_localitati`): `COALESCE(NULLIF(btrim(f.tert_judet), ''),
    <aceasta>)`."""
    if camp not in ("oras", "judet") or not f.isidentifier():
        raise TypeError("sql_camp_fisa: câmp / alias necunoscut: %r / %r" % (camp, f))   # greșeala apelantului (cod), nu a contabilului
    cui_f, cui_p = _CUI_SQL.format(c="%s.tert_cui" % f), _CUI_SQL.format(c="p.cui")
    potrivire = ("((%(cf)s <> '' AND %(cp)s = %(cf)s) OR (%(cf)s = '' AND %(cp)s = '' AND upper(btrim(p.nume)) = "
                 "upper(btrim(COALESCE(%(f)s.tert_nume, '')))))" % {"cf": cui_f, "cp": cui_p, "f": f})
    # [lotul 13, 640] fișa pereche (furnizorul / clientul cu același CUI) e același partener: când fișa directă n-are câmpul, se ia de acolo
    pereche = "(%(cf)s <> '' AND %(cp)s = %(cf)s)" % {"cf": cui_f, "cp": cui_p}
    return ("(CASE WHEN %(f)s.directie = 'emisa' THEN COALESCE((SELECT NULLIF(btrim(p.%(c)s), '') FROM clienti p WHERE p.id = %(f)s.client_id "
            "OR %(m)s ORDER BY (p.id = %(f)s.client_id) DESC NULLS LAST, p.id LIMIT 1), "
            "(SELECT NULLIF(btrim(p.%(c)s), '') FROM furnizori p WHERE %(pr)s ORDER BY p.id LIMIT 1)) "
            "ELSE COALESCE((SELECT NULLIF(btrim(p.%(c)s), '') FROM furnizori p WHERE %(m)s ORDER BY p.id LIMIT 1), "
            "(SELECT NULLIF(btrim(p.%(c)s), '') FROM clienti p WHERE %(pr)s ORDER BY p.id LIMIT 1)) END)"
            % {"f": f, "c": camp, "m": potrivire, "pr": pereche})


# ============================================================
#  [lotul 12, deficiența 461, comanda Costin 12.1: „lista de parteneri” cerută] PARTENERII FIRMEI: lista (clienți și furnizori, din toate
#  documentele firmei) și fișa partenerului (datele, documentele lui, soldul din contabilitate).
# ============================================================
def _rol_cont(cont):
    """Rolul partenerului după contul de terți: grupa 40 „Furnizori și conturi asimilate” -> furnizor, grupa 41 „Clienți și conturi
    asimilate” -> client (OMFP 1802/2014 pct.594, planul de conturi); orice alt cont -> None."""
    sint = str(cont or "").strip().split(".")[0]
    return "furnizor" if sint[:2] == "40" else ("client" if sint[:2] == "41" else None)


def _q(schema):
    from core import db as _db
    if not _db.schema_valida(schema):
        raise ValueError("Firma cerută nu poate fi deschisă: numele ei intern nu e valid (%r)." % schema)
    return '"%s"' % schema


def _bani(x):
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(str(x or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _fel_factura(directie, tip, storno):
    em = directie == "emisa"
    if storno:
        return "Factură de stornare " + ("emisă" if em else "primită")
    return {"factura": "Factură emisă" if em else "Factură primită", "borderou": "Borderou de achiziție",
            "proforma": "Proformă emisă" if em else "Proformă primită",
            # [lotul 12, 252] factura deschisă adusă la preluarea firmei (din programul vechi)
            "preluata": "Factură preluată, de încasat" if em else "Factură preluată, de plătit"}.get(tip or "factura",
                                                                          "%s %s" % (str(tip).capitalize(), "emisă" if em else "primită"))


def _surse(cur, schema):
    """Toate locurile din care firma își cunoaște partenerii, ca rânduri (cheie, cui, nume, rol, fisa, document) — `cheie` =
    `cheie_partener` (CUI-ul păstrat, altfel numele): fișele de clienți și de furnizori; facturile emise / primite (și borderourile,
    proformele); operațiunile de casă; liniile de extras bancar (CUI-ul detectat sau facturile alocate); notele cu partenerul scris pe linie
    (nota manuală pe 401 / 4111, compensarea); soldurile de preluare pe parteneri. `document` = rândul pentru fișa partenerului, sau None."""
    import psycopg2.extras as _E
    s = _q(schema)
    out = []
    c = cur.connection.cursor(cursor_factory=_E.RealDictCursor)
    for fel, rol in (("clienti", "client"), ("furnizori", "furnizor")):
        c.execute(f"SELECT id, nume, cui, adresa, oras, judet, email, telefon"
                  + (", afiliat" if fel == "clienti" else "") + f" FROM {s}.{fel} ORDER BY id")
        for r in c.fetchall():
            out.append((cheie_partener(r["cui"], r["nume"]), r["cui"], r["nume"], rol, dict(r, fel=fel), None))
    facturi = {}
    # [lotul 13, 546] suma documentului = totalul DE PLATĂ (`facturi.SQL_TOTAL_DE_PLATA_LEI`): factura primită cu taxare inversă e datorată
    # furnizorului fără TVA-ul determinat de beneficiar (CF art.331 alin.(3))
    from core import facturi as _fc
    c.execute(f"SELECT id, serie, numar, data_emitere, directie, COALESCE(tip, 'factura') AS tip, status, storno_din_id, "
              f"{_fc.SQL_TOTAL_DE_PLATA_LEI.format(a='facturi')} AS total_lei, total, tva, COALESCE(taxare_inversa, false) AS taxare_inversa, "
              f"COALESCE(moneda, 'RON') AS moneda, tert_cui, tert_nume "
              f"FROM {s}.facturi ORDER BY data_emitere DESC, id DESC")
    for r in c.fetchall():
        k = cheie_partener(r["tert_cui"], r["tert_nume"])
        facturi[r["id"]] = k
        doc = {"data": r["data_emitere"].isoformat() if r["data_emitere"] else None,
               "fel": _fel_factura(r["directie"], r["tip"], r["storno_din_id"]),
               "document": " ".join(x for x in (r["serie"] or "", r["numar"] or "") if x).strip(),
               "suma": _bani(r["total_lei"]), "moneda": r["moneda"],
               "suma_valuta": _bani(_fc.total_de_plata(r, r["total"], r["tva"])) if r["moneda"] != "RON" else None,
               "stare": "anulată" if r["status"] == "anulata" else None}
        out.append((k, r["tert_cui"], r["tert_nume"], "client" if r["directie"] == "emisa" else "furnizor", None, doc))
    c.execute(f"SELECT data, tip, document, partener, cui, suma FROM {s}.casa_operatiuni "
              f"WHERE COALESCE(btrim(cui), '') <> '' OR COALESCE(btrim(partener), '') <> '' ORDER BY data DESC, id DESC")
    for r in c.fetchall():
        out.append((cheie_partener(r["cui"], r["partener"]), r["cui"], r["partener"], None, None,
                    {"data": r["data"].isoformat(), "fel": "Încasare în numerar" if r["tip"] == "incasare" else "Plată în numerar",
                     "document": r["document"] or "", "suma": _bani(r["suma"]), "moneda": "RON", "suma_valuta": None, "stare": None}))
    c.execute(f"SELECT data, tip, descriere, suma, valuta, cui_detectat, status, alocari FROM {s}.extras_linii ORDER BY data DESC, id DESC")
    for r in c.fetchall():
        aloc = [a.get("factura_id") for a in ((r["alocari"] or {}).get("alocari") or []) if isinstance(a, dict)]
        chei = {facturi[f] for f in aloc if facturi.get(f)} or ({cheie_partener(r["cui_detectat"], None)} if r["cui_detectat"] else set())
        for k in chei - {None}:
            out.append((k, r["cui_detectat"] if k == cheie_partener(r["cui_detectat"], None) else None, None, None, None,
                        {"data": r["data"].isoformat(), "fel": "Încasare prin bancă" if r["tip"] == "incasare" else "Plată prin bancă",
                         "document": " ".join(str(r["descriere"] or "").split())[:120], "suma": _bani(r["suma"]),
                         "moneda": "valută" if r["valuta"] else "RON", "suma_valuta": None,
                         "stare": "contată" if r["status"] == "contat" else "necontată"}))
    note = {}
    for r in linii_partener(cur, schema):
        if not r["pe_linie"]:
            continue   # partenerul vine din factura / operațiunea de casă a notei: documentul e acela, nu nota
        k = cheie_partener(r["p_cui"], r["p_nume"])
        n = note.setdefault((k, r["id"]), {"cui": r["p_cui"], "nume": r["p_nume"], "rol": None, "suma": 0,
                                           "doc": {"data": r["data"].isoformat(), "fel": "Notă contabilă",
                                                   "document": ("nr %s · " % r["numar"] if r["numar"] else "") + (r["descriere"] or ""),
                                                   "moneda": "RON", "suma_valuta": None,
                                                   "stare": None if r["status"] == "validata" else "ciornă"}})
        n["rol"] = n["rol"] or _rol_cont(r["cont_debit"]) or _rol_cont(r["cont_credit"])
        n["suma"] += r["suma"]
    for (k, _nid), n in note.items():
        out.append((k, n["cui"], n["nume"], n["rol"], None, dict(n["doc"], suma=_bani(n["suma"]))))
    c.execute("SELECT to_regclass(%s) IS NOT NULL AS e", ("%s.solduri_parteneri" % s,))
    if c.fetchone()["e"]:
        c.execute(f"SELECT cont, cui, denumire FROM {s}.solduri_parteneri WHERE sold_debitor <> 0 OR sold_creditor <> 0")
        for r in c.fetchall():
            out.append((cheie_partener(r["cui"], r["denumire"]), r["cui"], r["denumire"], _rol_cont(r["cont"]), None, None))
    c.close()
    return [x for x in out if x[0]]


#: [461] Partenerul unei linii de notă, ca expresii SQL pe aliasurile `l` (linia), `f` (factura notei), `co` (prima operațiune de casă a notei):
#: cel scris pe linie, altfel al facturii, altfel al casei — regula deficienței 381, a doua oară scrisă în `repo_d406.select_inregistrari`
#: (de mutat acolo pe aceste constante: cerut în raportul lotului 12, pachetul PROD).
SQL_PARTENER_CUI = "COALESCE(NULLIF(l.partener_cui, ''), f.tert_cui, co.cui)"
SQL_PARTENER_NUME = "COALESCE(NULLIF(l.partener_nume, ''), f.tert_nume, co.partener)"


def linii_partener(cur, schema, cheie=None):
    """Liniile notelor pe conturile de terți (grupele 40 / 41), fiecare cu partenerul ei: cel scris pe linie (nota manuală pe 401 / 4111,
    compensarea), altfel al facturii legate, altfel al operațiunii de casă din care vine nota — aceeași regulă ca D406
    (`repo_d406.select_inregistrari`, deficiența 381). Toate stările (`status`); `cheie` = numai ale acestui partener (`cheie_partener`)."""
    import psycopg2.extras as _E
    s = _q(schema)
    with cur.connection.cursor(cursor_factory=_E.RealDictCursor) as c:
        c.execute(f"SELECT i.id, i.data, i.numar, i.descriere, i.status, l.cont_debit, l.cont_credit, l.suma, "
                  f"(COALESCE(btrim(l.partener_cui), '') <> '' OR COALESCE(btrim(l.partener_nume), '') <> '') AS pe_linie, "
                  f"{SQL_PARTENER_CUI} AS p_cui, {SQL_PARTENER_NUME} AS p_nume "
                  f"FROM {s}.inregistrari i JOIN {s}.inregistrari_linii l ON l.inregistrare_id = i.id "
                  f"LEFT JOIN {s}.facturi f ON f.id = i.factura_id "
                  f"LEFT JOIN LATERAL (SELECT x.cui, x.partener FROM {s}.casa_operatiuni x WHERE x.inregistrare_id = i.id "
                  f"ORDER BY x.id LIMIT 1) co ON true "
                  f"WHERE substr(split_part(l.cont_debit, '.', 1), 1, 2) IN ('40', '41') "
                  f"OR substr(split_part(l.cont_credit, '.', 1), 1, 2) IN ('40', '41') ORDER BY i.data, i.id, l.id")
        rows = [dict(r) for r in c.fetchall()]
    return [r for r in rows if cheie is None or cheie_partener(r["p_cui"], r["p_nume"]) == cheie]


def _eticheta_rol(roluri):
    return {frozenset(): None, frozenset({"client"}): "client", frozenset({"furnizor"}): "furnizor"}.get(frozenset(roluri),
                                                                                                        "client și furnizor")


def parteneri_firmei(conn, schema):
    """Lista partenerilor firmei: [{cheie, nume, cui, rol, documente, fisa}] — un rând pe partener (`cheie_partener`), din toate sursele
    (`_surse`), cu numele din fișă (altfel de pe cel mai nou document), rolul (client / furnizor / amândouă, din fișă, documente și
    conturile de terți), câte documente are și dacă are fișă. Ordonată după nume."""
    with conn.cursor() as cur:
        surse = _surse(cur, schema)
    acc = {}
    for k, cui, nume, rol, fisa, doc in surse:
        p = acc.setdefault(k, {"cheie": k, "nume": None, "cui": None, "roluri": set(), "documente": 0, "fisa": False})
        p["cui"] = p["cui"] or _cf.stocare(cui)
        nume = " ".join(str(nume or "").split()) or None
        if fisa:
            p["fisa"] = True
            p["nume_fisa"] = p.get("nume_fisa") or nume
        p["nume"] = p["nume"] or nume
        if rol:
            p["roluri"].add(rol)
        if doc:
            p["documente"] += 1
    out = []
    for p in acc.values():
        out.append({"cheie": p["cheie"], "nume": p.get("nume_fisa") or p["nume"] or p["cui"], "cui": p["cui"],
                    "rol": _eticheta_rol(p["roluri"]), "documente": p["documente"], "fisa": p["fisa"]})
    return sorted(out, key=lambda x: (str(x["nume"] or "").casefold(), x["cheie"]))


def sold_partener(cur, schema, cheie, linii=None):
    """Soldul partenerului din contabilitate, pe fiecare cont de terți (grupele 40 / 41), la zi — ACEEAȘI regulă ca balanța / bilanțul
    (`bilant_api.sold_la`: soldurile de preluare + mișcările din notele VALIDATE de după data lor, `bilant_api.data_soldurilor`), aplicată
    partenerului: soldul de preluare = rândurile lui din soldurile pe parteneri (`solduri_parteneri`, coerente cu balanța de deschidere —
    deficiența 346), mișcările = liniile atribuite lui (`linii_partener`). Ciornele nu sunt evidență (R36): se numără separat.
    -> {la, preluare, conturi: [{cont, denumire, debitor, creditor}], nedefalcat: [conturi cu sold de preluare nedefalcat pe parteneri],
    ciorne: câte note în ciornă ating partenerul, note_fara_partener: câte note validate au linii de terți fără partener (nu sunt în
    soldul niciunui partener)}. `linii` = toate liniile de terți ale firmei (`linii_partener` fără cheie), dacă apelantul le are."""
    import datetime as _dt
    from decimal import Decimal
    import psycopg2.extras as _E
    from core import bilant_api as _bil
    from core.common import azi_ro
    from core.plan_omfp import denumire_omfp
    s = _q(schema)
    azi = azi_ro()
    # toate liniile de terți ale firmei (`cheie=None` cu bună știință): din ele se numără și notele fără niciun partener, apoi se aleg ale lui
    toate = linii_partener(cur, schema, cheie=None) if linii is None else linii
    linii = [r for r in toate if cheie_partener(r["p_cui"], r["p_nume"]) == cheie]
    # liniile validate pe conturi de terți fără niciun partener (note manuale de dinainte de 381): nu sunt în soldul NICIUNUI partener
    fara_partener = len({r["id"] for r in toate if r["status"] == "validata" and not cheie_partener(r["p_cui"], r["p_nume"])})
    net = {}
    nedefalcat = []
    with cur.connection.cursor(cursor_factory=_E.RealDictCursor) as c:
        ref = _bil.data_soldurilor(c, schema)
        c.execute("SELECT to_regclass(%s) IS NOT NULL AS e", ("%s.solduri_parteneri" % s,))
        defalcate = set()
        if c.fetchone()["e"]:
            c.execute(f"SELECT cont, cui, denumire, sold_debitor, sold_creditor FROM {s}.solduri_parteneri")
            for r in c.fetchall():
                defalcate.add(str(r["cont"]).split(".")[0])
                if cheie_partener(r["cui"], r["denumire"]) == cheie:
                    net[r["cont"]] = net.get(r["cont"], Decimal("0")) + Decimal(str(r["sold_debitor"])) - Decimal(str(r["sold_creditor"]))
        c.execute(f"SELECT cont, sold_debitor, sold_creditor FROM {s}.solduri_initiale "
                  f"WHERE substr(split_part(cont, '.', 1), 1, 2) IN ('40', '41') AND (sold_debitor <> 0 OR sold_creditor <> 0)")
        for r in c.fetchall():
            sint = str(r["cont"]).split(".")[0]
            if sint not in defalcate and sint not in nedefalcat:
                nedefalcat.append(sint)
        ciorne = set()
        for r in linii:
            if r["status"] != "validata":
                ciorne.add(r["id"])
                continue
            d = r["data"]
            if (ref is not None and d <= ref) or d > azi:
                continue
            for cont, semn in ((r["cont_debit"], 1), (r["cont_credit"], -1)):
                if _rol_cont(cont):
                    net[cont] = net.get(cont, Decimal("0")) + semn * Decimal(str(r["suma"]))
        conturi = sorted(k for k, v in net.items() if v != 0)
        den = {}
        if conturi:
            c.execute(f"SELECT simbol, denumire FROM {s}.plan_conturi WHERE simbol = ANY(%s)", (conturi,))
            den = {r["simbol"]: r["denumire"] for r in c.fetchall()}
    return {"la": azi.isoformat() if isinstance(azi, _dt.date) else str(azi), "preluare": ref.isoformat() if ref else None,
            "conturi": [{"cont": k, "denumire": den.get(k) or denumire_omfp(k), "debitor": _bani(net[k]) if net[k] > 0 else 0.0,
                         "creditor": _bani(-net[k]) if net[k] < 0 else 0.0} for k in conturi],
            "nedefalcat": sorted(nedefalcat), "ciorne": len(ciorne), "note_fara_partener": fara_partener}


def fisa_partenerului(conn, schema, cheie):
    """Fișa unui partener (`cheie` din `parteneri_firmei`): {cheie, nume, cui, rol, fise: [fișele lui de client / furnizor, cu datele],
    documente: [{data, fel, document, suma, moneda, suma_valuta, stare}] (cele mai noi întâi), sold: `sold_partener`}. None dacă partenerul
    nu apare în datele firmei. Verificarea la ANAF o face ecranul, pe ruta existentă (`GET /verifica-cui/{cui}`, deficiența 444)."""
    with conn.cursor() as cur:
        surse = [x for x in _surse(cur, schema) if x[0] == cheie]
        if not surse:
            return None
        sold = sold_partener(cur, schema, cheie)
    fise = [x[4] for x in surse if x[4]]
    nume = next((x[2] for x in surse if x[4] and x[2]), None) or next((x[2] for x in surse if x[2]), None)
    cui = next((_cf.stocare(x[1]) for x in surse if _cf.stocare(x[1])), None)
    documente = sorted((x[5] for x in surse if x[5]), key=lambda d: d["data"] or "", reverse=True)
    return {"cheie": cheie, "nume": " ".join(str(nume or "").split()) or cui, "cui": cui,
            "rol": _eticheta_rol({x[3] for x in surse if x[3]}), "fise": fise, "documente": documente, "sold": sold}
