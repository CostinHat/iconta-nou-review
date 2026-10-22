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


def lista_clienti(conn, status=None):
    """Toți clienții, opțional filtrați pe status (activ/inactiv)."""
    cond, val = "", []
    if status is not None:
        cond = " WHERE status = %s"; val.append(status)
    return _lista(conn, "SELECT " + _COLOANE_LISTA + ", afiliat FROM clienti" + cond + " ORDER BY nume", val)


def lista_furnizori(conn, status=None):
    """[lotul 11, decizia 10.3] Toți furnizorii (fișele), opțional filtrați pe status."""
    cond, val = "", []
    if status is not None:
        cond = " WHERE status = %s"; val.append(status)
    return _lista(conn, "SELECT " + _COLOANE_LISTA + " FROM furnizori" + cond + " ORDER BY nume", val)


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
    return {"ok": ok}


# ============================================================
#  ȘTERGERE — protejată (refuz dacă are facturi)
# ============================================================
def sterge_client(conn, client_id):
    """
    Șterge clientul DOAR dacă nu are facturi legate (FK ar bloca oricum).
    Verific întâi, ca să întorc mesaj clar fără să stric tranzacția.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE client_id = %s", (client_id,))
        nr = cur.fetchone()[0]
        if nr:
            return {"ok": False, "cod": "ARE_FACTURI",
                    "mesaj": "clientul are %s — nu poate fi șters" % _cate(nr, "factură", "facturi")}
        cur.execute("DELETE FROM clienti WHERE id = %s", (client_id,))
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
    for r in out:
        r["cui"] = r["cui"] or None
        r["cheie"] = cheie_partener(r["cui"], r["nume"])
    return out


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
    return ("(CASE WHEN %(f)s.directie = 'emisa' THEN (SELECT NULLIF(btrim(p.%(c)s), '') FROM clienti p WHERE p.id = %(f)s.client_id "
            "OR %(m)s ORDER BY (p.id = %(f)s.client_id) DESC NULLS LAST, p.id LIMIT 1) "
            "ELSE (SELECT NULLIF(btrim(p.%(c)s), '') FROM furnizori p WHERE %(m)s ORDER BY p.id LIMIT 1) END)"
            % {"f": f, "c": camp, "m": potrivire})
