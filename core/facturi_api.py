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

from core.common import (NUMEROTARE_SECVENTIALA,
                         cote_tva_in_vigoare as _cote_tva_in_vigoare)

REGULI = "2026.1"
MODUL = "facturi_api"


class LiniiIncomplete(ValueError):
    """[cap.24/cap.6] Linii de factura fara denumire sau cu cantitate<=0 -> erori PER-LINIE field-keyed
    {camp, eticheta} (id-uri DOM em-l{i}-*, i = pozitia in lista PRIMITA). Backendul e autoritatea de validare
    per-linie; frontendul NU tine oglinda. Ruta o converteste intr-un 422 care poarta lista `campuri`."""
    def __init__(self, campuri):
        self.campuri = campuri
        super().__init__("Linii incomplete: " + "; ".join(x["eticheta"] for x in campuri))


#: Direcțiile posibile ale unei facturi. Erau scrise de două ori — o dată ca refuz în
#: `creeaza_factura` și o dată deloc în `lista_facturi`, care tăcea pe orice altă valoare și
#: întorcea lista goală. O singură sursă: filtrul respinge exact ce respinge și crearea.
DIRECTII = ("emisa", "primita")


def _data_ceruta(camp, valoare):
    """Data unui câmp, ca `date`, sau `ValueError` care spune CARE câmp și CE s-a primit.

    Până azi `data_emitere` mergea neatinsă până în `INSERT`, iar Postgres refuza `2026-02-31`
    cu o eroare de driver — contabilul primea `500 Internal Server Error`, adică nimic. O zi
    care nu există în calendar e o greșeală de tastare, nu o cădere de sistem."""
    import datetime as _d
    if valoare is None or valoare == "":
        return None
    if isinstance(valoare, _d.date):
        return valoare
    try:
        return _d.date.fromisoformat(str(valoare).strip())
    except ValueError:
        raise ValueError("%s: %r nu e o dată din calendar. Aștept forma AAAA-LL-ZZ, cu o zi care "
                         "există în luna aia." % (camp, valoare))


def _cota_necunoscuta(linii, la_data):
    """Prima linie a cărei cotă de TVA nu exista în lege la data facturii, ca `(linie, cota,
    cote_permise, temeiuri)`; `None` dacă toate se recunosc SAU dacă nu se poate ști.

    **Nu confunda „e invalidă" cu „n-am putut verifica"**: dacă registrul de cote nu acoperă
    perioada facturii, `cote_tva_in_vigoare` întoarce `None`, iar aici nu se refuză nimic. Un
    refuz pe necunoaștere ar bloca introducerea unei facturi vechi corecte."""
    if la_data is None:
        return None   # fara data facturii nu se poate sti ce cote erau atunci — deci nu se refuza
    permise, temeiuri = _cote_tva_in_vigoare(la_data)
    if permise is None:
        return None
    for l in linii:
        c = l.get("cota_tva")
        if c is None:
            continue
        try:
            v = Decimal(str(c))
        except Exception:
            v = None
        if v is None or v not in permise:
            return l, c, permise, temeiuri
    return None


def linii_campuri_lipsa(linii, prefix="em-l"):
    """Campuri obligatorii per linie goale -> [{camp, eticheta}]. Obligatorii: denumire (nevida) + cantitate>0
    (aceleasi criterii pe care frontendul le filtra tacit inainte). id camp = {prefix}{i}-{camp}, i = pozitia in
    lista. prefix parametrizat ca acelasi contract sa serveasca emitere (em-l) + facturi-recurente (fr-l)
    FARA a duplica criteriile (o singura sursa de adevar, cap.24 regula 4)."""
    lipsa = []
    for i, l in enumerate(linii):
        n = i + 1
        d = l.get("descriere")
        if d is None or str(d).strip() == "":
            lipsa.append({"camp": "%s%d-descriere" % (prefix, i), "eticheta": "Linia %d: denumire" % n})
        try:
            ok = float(l.get("cantitate") or 0) > 0
        except (TypeError, ValueError):
            ok = False
        if not ok:
            lipsa.append({"camp": "%s%d-cantitate" % (prefix, i), "eticheta": "Linia %d: cantitate" % n})
    return lipsa


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


# ─────────────────────────────────────────── CODUL DE PARTENER (prag 2, 23.08.2026)
# NORMA: Codul fiscal art. 319 alin. (20) cere pe factura codul de identificare fiscala al
# beneficiarului. Pana azi `tert_cui` era default de parametru (`None`) si NIMIC nu-l verifica -
# nici prezenta, nici cifra de control. Masurat: 2 din 42 de facturi fara cod, una catre un SRL,
# intrata PRIN APLICATIE (status `de_preluat`, produs de `emite_factura`).
#
# DE CE PRAG 2 SI NU O SEMNALARE (decizia lui Costin, 23.08): o factura fara CUI de partener
# NU INTRA IN D394 si nu se poate corela in VIES. Nu e o coloana goala, e o DECLARATIE INCOMPLETA
# la prima firma reala. Iar un CUI lipsa nu se poate completa retroactiv de nimeni altcineva decat
# cel care a emis factura - deci momentul e introducerea, nu un raport de mai tarziu.
#
# EXCEPTIA e EXPLICITA, nu dedusa: `tert_pf=True` spune ca partenerul e persoana fizica fara cod de
# identificare fiscala. Nu se ghiceste din nume si nici din lipsa codului - a ghici ar readuce exact
# tacerea pe care o inlocuim.
def cere_cod_partener(tert_cui, tert_pf=False, tert_nume=None):
    """Ridica daca lipseste codul de partener si nu s-a declarat persoana fizica."""
    if tert_pf:
        return None
    cod = (tert_cui or "").strip()
    if cod:
        return cod
    cine = (" (%s)" % tert_nume.strip()) if (tert_nume or "").strip() else ""
    raise ValueError(
        "Factura nu se poate salva fără codul fiscal al partenerului%s. Completează-l, sau bifează "
        "că partenerul e persoană fizică fără cod fiscal. Fără el, factura nu intră în D394 și nu "
        "se poate corela în VIES, iar codul nu mai poate fi completat mai târziu de altcineva decât "
        "cel care a emis-o (Cod fiscal art. 319 alin. 20)." % cine)


def creeaza_factura(conn, numar, data_emitere, directie, linii,
                    client_id=None, tert_nume=None, tert_cui=None, tert_adresa=None,
                    data_scadenta=None, moneda="RON", status="emisa",
                    categorie_331=None, data_faptului_generator=None, taxare_inversa=False,
                    tert_platitor_tva=None, tert_tara="RO", tip_operatiune="normal",
                    furnizor_tva_incasare=False, tert_pf=False, tip="factura"):
    """
    Inserează factura + liniile, într-o tranzacție. total/tva calculate din linii.
    Întoarce {ok, factura_id, total, tva}.
    """
    if not linii:
        raise ValueError("factura trebuie să aibă cel puțin o linie")
    cere_cod_partener(tert_cui, tert_pf, tert_nume)
    for _l in linii:
        if _l.get("cota_tva") is None:
            raise ValueError("Linia %r nu are cotă de TVA. Completează cota pe linie — 0 (scutit) "
                             "e o valoare validă, dar absența nu se poate ghici."
                             % (_l.get("descriere") or "",))
    if directie not in DIRECTII:
        raise ValueError("Direcția facturii trebuie să fie 'emisă' sau 'primită'.")
    # [probare invalid lot 2, 03.09.2026] Cele trei refuzuri de mai jos au înlocuit, în ordine:
    # un `500` pe o dată inexistentă în calendar, o factură cu cota de TVA 99% acceptată ȘI
    # contabilizată (4427 = 99 lei), și un al doilea document cu un număr deja folosit.
    _d_emitere = _data_ceruta("data emiterii", data_emitere)
    _data_ceruta("data scadenței", data_scadenta)
    _rea = _cota_necunoscuta(linii, _d_emitere)
    if _rea is not None and (directie == "emisa" or (tert_tara or "RO").strip().upper() == "RO"):
        # Numai pe ce ține de legea română: pe o factură PRIMITĂ dintr-un alt stat, cota lui e
        # legitimă și n-avem de unde ști lista lui. Limita e declarată, nu ascunsă.
        _l, _c, _permise, _temeiuri = _rea
        raise ValueError(
            "Linia %r are cota de TVA %s%%, care nu există în legea română la data facturii (%s). "
            "Cotele de atunci: %s. Temei: %s."
            % (_l.get("descriere") or "", _c, _d_emitere.isoformat() if _d_emitere else "azi",
               ", ".join("%s%%" % _f for _f in sorted(_permise)),
               "; ".join(sorted({str(_t) for _t in _temeiuri}))))
    if directie == "emisa" and numar:
        with conn.cursor() as _cur:
            _cur.execute("SELECT id FROM facturi WHERE numar=%s AND directie='emisa' LIMIT 1",
                         (numar,))
            _existent = _cur.fetchone()
        if _existent:
            raise ValueError(
                "Numărul %s e deja pe factura #%s. Două documente emise cu același număr rup "
                "secvența cerută de %s. Dacă documentul dinainte e greșit, se stornează — nu se "
                "reia numărul." % (numar, _existent[0], NUMEROTARE_SECVENTIALA))
    # [B1 D300] campuri de clasificare/temporizare. tip_operatiune distinge avansul (exigibil la
    # emitere, art.282 alin.2 lit.b); furnizor_tva_incasare doar pe PRIMITE (deducere amanata la
    # plata, art.297 alin.2). Fara default tacit peste o valoare invalida -> refuz cu mesaj clar.
    tert_tara_v = (tert_tara or "RO").strip().upper() or "RO"
    tip_op_v = (tip_operatiune or "normal").strip().lower() or "normal"
    if tip_op_v not in ("normal", "avans", "regularizare_avans"):
        raise ValueError("Tipul operațiunii %r nu e recunoscut. Alege: normal, avans sau "
                         "regularizare de avans." % tip_operatiune)
    # [EEE1] `tip` intra la INSERT, nu printr-un UPDATE de dupa. Motivul nu e stilistic: nota
    # automata se scrie in ACEEASI tranzactie, iar ea trebuie sa stie daca documentul e factura sau
    # proforma. Cat timp tipul se punea dupa, o proforma ar fi primit nota si abia apoi ar fi devenit
    # proforma.
    tip_v = (tip or "factura").strip().lower() or "factura"
    if tip_v not in ("factura", "proforma", "aviz"):
        raise ValueError("Tipul documentului %r nu e recunoscut. Alege: factură, proformă sau aviz."
                         % tip)
    furnizor_incasare_v = bool(furnizor_tva_incasare)
    if furnizor_incasare_v and directie != "primita":
        raise ValueError("TVA la încasare la furnizor se poate bifa doar pe facturile primite "
                         "— pe cele emise nu se aplică.")
    t = totaluri_din_linii(linii)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO facturi (client_id, numar, data_emitere, data_scadenta, "
            "total, tva, status, moneda, directie, tert_nume, tert_cui, tert_adresa, "
            "categorie_331, data_faptului_generator, taxare_inversa, tert_platitor_tva, "
            "tert_tara, tip_operatiune, furnizor_tva_incasare, tip) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (client_id, numar, data_emitere, data_scadenta, t["total"], t["tva"],
             status, moneda, directie, tert_nume, tert_cui, tert_adresa,
             categorie_331 or None, data_faptului_generator or None, bool(taxare_inversa),
             tert_platitor_tva, tert_tara_v, tip_op_v, furnizor_incasare_v, tip_v))
        factura_id = cur.fetchone()[0]
        for l in linii:
            cur.execute(
                "INSERT INTO factura_linii (factura_id, descriere, um, cantitate, "
                "pret_unitar, cota_tva, articol_id, cont_venit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (factura_id, l["descriere"], l.get("um", "buc"),
                 l["cantitate"], l["pret_unitar"], l["cota_tva"], l.get("articol_id"),
                 (l.get("cont_venit") or None)))  # #11 cont venit pe linie (auto din denumire, editabil)
    _redeschide_luna(conn, data_emitere)   # [cap.23] evidenta lunii s-a schimbat -> luna se redeschide
    out = {"ok": True, "factura_id": factura_id,
           "total": float(t["total"]), "tva": float(t["tva"])}
    out["contare"] = _conteaza_la_creare(conn, factura_id, directie, tip_v)
    return out


def _conteaza_la_creare(conn, factura_id, directie, tip):
    """[EEE1 / R87] Nota contabila a facturii EMISE se scrie in ACELASI act cu emiterea.

    DE CE AICI, si nu in ruta: `creeaza_factura` e punctul UNIC prin care trec toate emiterile
    aplicatiei — `POST /facturi`, `POST /facturi/emite`, stornarea si transformarea proformei o
    cheama pe toate. Legat de o singura ruta, decizia R36 ar fi fost adevarata doar pe un drum din
    patru. *Masurat prin citire, nu presupus: `emite_factura` si `storneaza` cheama chiar functia
    asta.*

    DE CE NUMAI `emisa`: la primita, faptul economic nu e sosirea documentului, ci recunoasterea
    cheltuielii — nota se scrie la `/valideaza` (R88, decizia din 29.08.2026).

    ROLLBACK COMPLET, ca la NIR: nu se comite nimic aici. Daca emiterea cade mai tarziu — curs BNR
    indisponibil, de pilda —, nota cade cu ea. **Nu exista factura fara nota, si nici nota fara
    factura.**

    UN REFUZ NU E O EROARE. `RefuzContare` opreste NOTA, nu emiterea: factura se creeaza oricum, iar
    motivul pleaca in raspuns. Altfel o factura perfect valida n-ar mai putea fi emisa dintr-un motiv
    de contabilitate — iar semnalul ca lipseste nota exista deja, in verdictul de TVA (R35).

    CE NU ACOPERA, DECLARAT (ZZ4 cere ca absenta sa fie scrisa, nu deduse): facturile intrate prin
    `main._factura_din_parsat` — importul din SPV si incarcarea manuala de XML — NU trec pe aici, ci
    printr-un INSERT propriu. O factura EMISA care se intoarce din SPV a fost emisa in alta parte;
    pentru ea, sosirea documentului nu e faptul economic. Ramane necontata si vizibila ca atare in
    verdictul de TVA.
    """
    from core import contare_facturi as _cf
    from core import afirmatii as _af
    if directie != "emisa" or tip != "factura":
        return {"stare": "neaplicabil", "afirmatie": _af.afirmatie(
            "absenta_observatie", "CONTARE_NEAPLICABILA",
            "nota automată se scrie doar pentru facturi EMISE de tip factură; documentul ăsta e "
            "%s / %s" % (directie, tip),
            surse_consultate=["facturi.directie", "facturi.tip"])}
    try:
        with _cf.cursor_dict(conn) as cur:
            return _cf.contabilizeaza(cur, "", factura_id, automat=True)
    except _cf.RefuzContare as e:
        return {"stare": "refuzata", "cod": e.cod, "detalii": e.detalii,
                "afirmatie": _af.afirmatie(
                    "neconformitate", e.cod, e.mesaj,
                    unde="factura #%s" % factura_id,
                    regula="nota automată se scrie doar când toate intrările ei sunt cunoscute")}


# ============================================================
#  LISTĂ — DB
# ============================================================
def lista_facturi(conn, an=None, luna=None, directie=None, limit=None, offset=0):
    """Lista facturilor (antet), filtrabilă pe an/lună/direcție. limit=None -> tot istoricul
    (folosit intern de alte module: verificatoare, D390 etc.); UI foloseste limit pentru paginare."""
    import psycopg2.extras as _E
    # [probare invalid lot 2, 03.09.2026] Trei feluri de a nu răspunde, toate reparate aici:
    # `luna=13` construia intervalul „2026-13-01 … 2026-14-01" și pica în driver (`500`);
    # `limit=-5` ajungea în `LIMIT -5`, refuzat de Postgres (`500`); iar `directie=lateral`
    # întorcea `200` cu listă goală — „nu există facturi așa" arăta identic cu „direcția asta
    # nu există", exact clasa scoasă din `GET /coada` în lotul 1.
    if luna is not None and not (1 <= luna <= 12):
        raise ValueError("luna invalidă: %r (aștept 1-12)" % (luna,))
    if an is not None and not (1990 <= an <= 2100):
        raise ValueError("an invalid: %r (aștept 1990-2100)" % (an,))
    if directie is not None and directie not in DIRECTII:
        raise ValueError("direcție necunoscută: %r (direcțiile facturii: %s)"
                         % (directie, ", ".join(DIRECTII)))
    if limit is not None and limit < 0:
        raise ValueError("limit invalid: %r (aștept un număr pozitiv, sau nimic pentru tot)"
                         % (limit,))
    if offset is not None and offset < 0:
        raise ValueError("offset invalid: %r (aștept un număr pozitiv sau 0)" % (offset,))
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
    limitclause = ""
    if limit is not None:
        limitclause = " LIMIT %s OFFSET %s"; val += [limit, offset]
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, numar, data_emitere, directie, total, tva, status, "
            "moneda, tert_nume, tert_cui, tert_adresa, tip, transformat_in_id, storno_din_id, "
            "EXISTS(SELECT 1 FROM inregistrari i WHERE i.factura_id = facturi.id) AS contabilizata "
            "FROM facturi" + where +
            " ORDER BY data_emitere DESC, id DESC" + limitclause, val)
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
            "tert_tara, tip_operatiune, furnizor_tva_incasare, "
            "curs_bnr, tva_lei, total_lei, data_curs, curs_sursa, storno_din_id, tip, transformat_in_id, "
            "link_plata, platita_la, "
            "(SELECT numar FROM facturi f2 WHERE f2.id = facturi.transformat_in_id) AS transformat_in_numar, "
            "EXISTS(SELECT 1 FROM inregistrari i WHERE i.factura_id = facturi.id) AS contabilizata "
            "FROM facturi WHERE id = %s",
            (factura_id,))
        f = cur.fetchone()
        if not f:
            return None
        f = dict(f)
        cur.execute(
            "SELECT id, descriere, um, cantitate, pret_unitar, cota_tva, cont_venit "
            "FROM factura_linii WHERE factura_id = %s ORDER BY id", (factura_id,))
        f["linii"] = [dict(r) for r in cur.fetchall()]
    return f


# ============================================================
#  ȘTERGERE — DB (liniile cad prin CASCADE)
# ============================================================
def _redeschide_luna(conn, data_emitere):
    """[cap.23, 21.08.2026] Orice modificare a evidenței facturilor DE-CONFIRMĂ luna. O închidere care
    supraviețuiește unei modificări ar afirma „evidența lunii e completă" despre alte date decât cele
    pe care cineva le-a văzut când a închis — exact „verde e o afirmație". Simetric cu `pontaj.seteaza`.
    Conexiunea e pe schema tenantului (search_path), ca restul modulului."""
    if not data_emitere:
        return
    d = data_emitere
    if isinstance(d, str):
        import datetime as _dt
        try:
            d = _dt.date.fromisoformat(d[:10])
        except ValueError:
            return
    from core import perioada as _per
    _per.deconfirma(conn, "", d.year, d.month, "facturi")


def _luna_facturii(conn, factura_id):
    with conn.cursor() as cur:
        cur.execute("SELECT data_emitere FROM facturi WHERE id = %s", (factura_id,))
        r = cur.fetchone()
    return r[0] if r else None


def sterge_factura(conn, factura_id):
    """Șterge factura (liniile cad automat prin ON DELETE CASCADE).

    [EEE2] **REFUZĂ MOTIVAT dacă factura are notă de contare.** Până azi ștergerea nu verifica nimic,
    iar cheia străină `inregistrari_factura_id_fkey` n-are `ON DELETE` — deci trecea *de cele mai
    multe ori* doar fiindcă majoritatea facturilor n-aveau notă (28 din 41, măsurat). Cu note
    automate, fiecare factură are una, iar ștergerea ar fi început să pice cu o eroare brută de bază
    în loc de un refuz explicat. **Automatizarea nu creează problema — o face vizibilă la fiecare
    ștergere.**

    O notă de **plată** nu blochează ștergerea: nu e evidența facturii, e a încasării. Aceeași
    distincție ca la idempotență, din același loc (`contare_facturi.contare_existenta`).

    Varianta aleasă de Costin (29.08.2026) e (i) — refuz + trimitere la storno. Respinse: (ii)
    ștergerea notei odată cu factura — *o notă ștearsă e o gaură în evidență, nu o corecție* —, și
    (iii) ștergerea condiționată de starea ciornă, care ar face comportamentul să depindă de un pas
    de validare pe care omul nu-l are în minte când apasă „șterge"."""
    from core import contare_facturi as _cf
    with _cf.cursor_dict(conn) as cur:
        n = _cf.contare_existenta(cur, "", factura_id)
        legate = _cf.note_cu_cheia(cur, "", factura_id)
    if not n and legate:
        # GĂSIT DE PROPRIA GARDĂ, la prima rulare, și nu era în comandă: cheia străină blochează
        # ștergerea pentru ORICE notă legată, nu doar pentru o contare. O notă de PLATĂ n-ar trebui
        # să apere factura de ștergere — dar `inregistrari_factura_id_fkey` n-are `ON DELETE`, deci
        # o blochează oricum, cu o eroare brută de bază. EEE2 cere ca ștergerea să nu mai pice așa;
        # refuzul acoperă și clasa asta, cu ALT cod și ALT motiv, fiindcă **ieșirea e alta**:
        # aici dezlegi nota, nu stornezi factura.
        # Mesajul NUMEȘTE starea notei, fiindcă de ea depinde dacă ieșirea există. O ciornă se
        # poate șterge (patru-ochi n-a fost consumat); o notă VALIDATĂ nu — `jurnal_api.sterge`
        # refuză orice notă care nu e ciornă, iar rută de dezlegare nu există. Pe portofoliul de
        # azi, toate cele 3 facturi din clasa asta au nota VALIDATĂ, deci nu se pot șterge deloc.
        # Restanța e deschisă (R90); mesajul nu are voie s-o ascundă promițând o ieșire inexistentă.
        # [R90, varianta (a)] Ieșirea EXISTĂ de azi și se numește: nota se dezleagă, explicit, prin
        # actul ei. Până azi mesajul trimitea într-un zid pentru o notă validată — `jurnal_api.sterge`
        # refuză orice notă care nu e ciornă, iar dezlegare nu era. *Un refuz care numește o ieșire
        # inexistentă e mai rău decât unul care spune «nu se poate».*
        _n0 = legate[0]
        raise _cf.RefuzContare(
            "ARE_NOTA_LEGATA",
            "Factura are o notă legată care nu e de contare (#%d, %s, %s) — o plată sau o încasare. "
            "Dezleag-o întâi: potrivirea rămâne consemnată pe linia de extras, iar factura redevine "
            "neîncasată." % (_n0["id"], _n0.get("sursa") or "fără sursă", _n0.get("status") or "?"),
            detalii={"inregistrare_id": _n0["id"], "status_nota": _n0.get("status"),
                     "iesire": "dezleaga_nota"})
    if n:
        raise _cf.RefuzContare(
            "ARE_NOTA_DE_CONTARE",
            "Factura are notă contabilă (#%d) și nu se mai șterge: o notă ștearsă lasă o gaură în "
            "evidență. Corecția unei facturi contabilizate se face prin STORNO — un al doilea "
            "document, care își produce propria notă." % n["id"],
            detalii={"inregistrare_id": n["id"], "iesire": "storno"})
    _d = _luna_facturii(conn, factura_id)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM facturi WHERE id = %s", (factura_id,))
        sterse = cur.rowcount
    if sterse:
        _redeschide_luna(conn, _d)
    return {"ok": sterse > 0}


# ============================================================
#  EMITERE — numerotare, emitere, storno  [p103_emitere]
# ============================================================
def numerotare(conn):
    """Citeste serie + urmatorul numar de factura din firma_profil."""
    with conn.cursor() as cur:
        cur.execute("SELECT serie_factura, urmator_numar_factura, numerotare_configurata FROM firma_profil LIMIT 1")
        row = cur.fetchone()
    serie = row[0] if row else None
    urmator = int(row[1]) if row and row[1] is not None else 1
    configurata = bool(row[2]) if row and len(row) > 2 and row[2] is not None else False
    return {"serie": serie, "urmator_numar": urmator, "configurata": configurata}  # numerotare_configurata_v1


def seteaza_numerotare(conn, serie=None, numar_start=None):
    """Configureaza seria + numarul de start (continuitate cu istoricul).
    Se apeleaza o data; dupa, numarul se auto-incrementeaza la emitere."""
    # [probare invalid lot 2, 03.09.2026] Trei valori treceau cu `200 {"ok": true}`:
    # `serie="   "` ștergea seria firmei în tăcere (`strip() or None`), `numar_start=-5` intra
    # ca atare, iar `numar_start=100` dădea contorul înapoi peste numere deja emise — următoarea
    # factură ar fi purtat un număr existent. Probat: după el, emiterea prin API a produs
    # documentul „100", fără serie.
    with conn.cursor() as _cur:
        _cur.execute("SELECT serie_factura, urmator_numar_factura FROM firma_profil LIMIT 1")
        _acum = _cur.fetchone() or (None, None)
    seturi, val = [], []
    if serie is not None:
        if not str(serie).strip():
            return {"ok": False, "mesaj": "Seria e goală (numai spații). Nu se poate ghici dacă "
                                          "ai vrut s-o ștergi sau ai greșit tastarea, iar seria "
                                          "firmei e pe documentele deja emise."}
        seturi.append("serie_factura = %s"); val.append(serie.strip())
    if numar_start is not None:
        try:
            _n = int(numar_start)
        except (TypeError, ValueError):
            return {"ok": False, "mesaj": "Numărul de start: %r nu e un număr întreg." % (numar_start,)}
        if _n < 1:
            return {"ok": False, "mesaj": "Numărul de start trebuie să fie cel puțin 1; am primit "
                                          "%s. Numerotarea documentelor pornește de la 1, nu de la "
                                          "zero sau de la un număr negativ (%s)."
                                          % (_n, NUMEROTARE_SECVENTIALA)}
        _urm = _acum[1]
        if _urm is not None and _n < _urm:
            return {"ok": False, "mesaj": "Numărul de start %s e sub cel la care a ajuns seria "
                                          "(%s). Dat înapoi, următoarea factură ar primi un număr "
                                          "deja emis, iar secvența cerută de %s s-ar rupe. Un "
                                          "număr mai mare sau egal se acceptă."
                                          % (_n, _urm, NUMEROTARE_SECVENTIALA)}
        seturi.append("urmator_numar_factura = %s"); val.append(_n)
    if not seturi:
        return {"ok": False, "mesaj": "Nu ai trimis nici seria, nici numărul de "
                                      "start, deci n-am ce schimba în numerotarea "
                                      "facturilor."}
    seturi.append("numerotare_configurata = true")  # numerotare_configurata_v1
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET " + ", ".join(seturi), val)
    return {"ok": True}


def _potriveste_linii(conn, linii, platitor_tva=True):
    """Pentru fiecare linie fara cota_tva, o potriveste (nomenclator/AI) si o
    salveaza in nomenclator. Determina si contul de venit PE LINIE din denumire
    (#11: marfa->707/produse->701/serviciu->704, OMFP 1802/2014), editabil ulterior.
    Intoarce liniile cu cota + cont_venit completate."""
    from core import produse_api, cote_tva
    from core import facturi as _fc
    # contul de venit implicit al firmei = fallback cand clasificarea liniei nu reuseste
    cv_firma = None
    try:
        with conn.cursor() as _cur:
            _cur.execute("SELECT cont_venit_implicit FROM firma_profil LIMIT 1")
            _row = _cur.fetchone()
            cv_firma = (_row[0] if _row else None) or None
    except Exception:
        cv_firma = None
    out = []
    for l in linii:
        linie = dict(l)
        if linie.get("cota_tva") is None:
            # creeaza() cauta in nomenclator, altfel AI + salveaza; nu dubleaza
            r = produse_api.creeaza(conn, linie.get("descriere", ""),
                                    um=linie.get("um", "buc"),
                                    pret_unitar=linie.get("pret_unitar", 0),
                                    platitor_tva=platitor_tva)
            if r.get("cota_tva") is None:
                # auto-match esuat (AI indisponibil/nedeterminat): intrare incompleta, NU cota 21
                raise ValueError("cota TVA nedeterminata pentru %r: nomenclatorul/AI nu a putut "
                                 "stabili cota. Declara cota explicit pe linie."
                                 % (linie.get("descriere") or "",))
            linie["cota_tva"] = r["cota_tva"]
        # cont de venit pe linie: pastreaza ce a pus contabilul; altfel clasifica din denumire.
        # Best-effort: daca AI indisponibil/nedeterminat NU blocheaza (spre deosebire de cota) ->
        # cade pe cont_venit_implicit al firmei; daca nici acela nu e setat lasa None (contabilizarea decide).
        if not str(linie.get("cont_venit") or "").strip():
            cont = None
            try:
                rez = cote_tva.potriveste_cota(linie.get("descriere", ""), platitor_tva=platitor_tva)
                tip = rez.get("tip") if rez.get("ok") else None
                if tip:
                    cont = _fc.VENIT.get(tip)
            except Exception:
                cont = None
            linie["cont_venit"] = cont or cv_firma
        out.append(linie)
    return out


def emite_factura(conn, linii, client_id=None, tert_nume=None, tert_cui=None, tert_adresa=None,
                  data_emitere=None, data_scadenta=None, moneda="RON",
                  platitor_tva=True, status="de_preluat", curs_manual=None, tip="factura",
                  tert_tara="RO", tip_operatiune="normal", tert_pf=False,
                  data_curs_manual=None, curs_manual_de=None):
    """
    Emite o factura noua (directie=emisa):
      - potriveste cota pe liniile fara cota (nomenclator/AI)
      - numeroteaza automat (serie + urmator_numar din firma_profil)
      - salveaza + incrementeaza contorul
    Intoarce {ok, factura_id, numar, serie, total, tva}.
    """
    # [probare invalid lot 2, 03.09.2026] ORDINEA e reparația: codul de partener se cerea
    # ÎNAINTE de a se uita la linii, deci cine trimitea `linii=[]`, o cantitate negativă sau o
    # monedă inexistentă primea, toți trei, mesajul despre codul fiscal al partenerului — un
    # refuz care numește alt câmp. Aceeași clasă ca „trimestru invalid: None" din lotul 1.
    import datetime
    if not linii:
        raise ValueError("Factura trebuie să aibă cel puțin o linie.")
    _lipsa = linii_campuri_lipsa(linii)   # [cap.24 3b] validare per-linie field-keyed (autoritatea)
    if _lipsa:
        raise LiniiIncomplete(_lipsa)
    cere_cod_partener(tert_cui, tert_pf, tert_nume)
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
                        data_scadenta=data_scadenta, moneda=moneda, status=status,
                        tert_tara=tert_tara, tip_operatiune=tip_operatiune, tip=tip)
    # setez seria pe factura + incrementez contorul
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET serie = %s WHERE id = %s", (serie, r["factura_id"]))
        if tip == "factura":
            cur.execute("UPDATE firma_profil SET urmator_numar_factura = %s", (numar_int + 1,))
        else:
            col = "urmator_numar_proforma" if tip == "proforma" else "urmator_numar_aviz"
            cur.execute(f"UPDATE firma_profil SET {col} = %s", (numar_int + 1,))
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

    _urma_manual = None            # (cine, cand) — se scrie numai pe calea manuala
    if (moneda or "RON").upper() == "RON":
        _curs, _dcurs, _sursa = 1, _d, "ron"
    elif curs_manual is not None:
        # [R130, decizia lui Costin 04.09.2026] Cursul de mână vine cu DATA LUI, nu cu data
        # facturii. Până azi `data_curs` primea data facturii — adică documentul spunea „curs din
        # 4 septembrie" despre o cifră pe care contabilul o luase din altă zi. Iar „consemnat cine
        # și când" cere un autor: fără el, „manual" e o stare, nu un act.
        _dcm = _data_ceruta("data cursului", data_curs_manual)
        if _dcm is None:
            raise ValueError(
                "Cursul introdus manual are nevoie de data la care a fost comunicat. Fără ea, "
                "factura ar spune că e cursul zilei de emitere, ceea ce nu se știe.")
        if _dcm > _d:
            raise ValueError(
                "Data cursului (%s) e după data facturii (%s). Se folosește ultimul curs comunicat "
                "PÂNĂ la data facturii — unul de după ea n-avea cum să fie cunoscut atunci."
                % (_dcm.isoformat(), _d.isoformat()))
        if not (curs_manual_de or "").strip():
            raise ValueError(
                "Cursul introdus manual se consemnează cu autorul lui. Fără el, peste șase luni "
                "nimeni nu poate spune cine a ales cifra cu care s-a calculat TVA-ul.")
        _curs, _dcurs, _sursa = float(curs_manual), _dcm, "manual"
        _urma_manual = (curs_manual_de.strip(), _dt.datetime.now(_dt.timezone.utc))
    else:
        try:
            _c, _dc, _s = curs_bnr.curs_pentru(conn, moneda, _d)
            _curs, _dcurs, _sursa = float(_c), _dc, _s
        except curs_bnr.CursPreaVechi as _pv:
            # Emiterea AUTOMATĂ se oprește — dar facturarea nu se blochează: refuzul își numește
            # ieșirea, iar cursul găsit merge cu el, ca omul să vadă de la ce pornește.
            conn.rollback()
            return {"ok": False, "cod": "CURS_PREA_VECHI", "moneda": moneda,
                    "data": _d.isoformat(), "data_curs_gasit": _pv.data_curs.isoformat(),
                    "curs_gasit": str(_pv.curs), "vechime_zile": _pv.vechime_zile,
                    "prag_zile": _pv.prag_zile, "mesaj": str(_pv),
                    "iesire": {"camp": "curs_manual",
                               "cere": ["curs_manual", "data_curs_manual"],
                               "cum": "Introdu cursul de mână, cu data la care a fost comunicat. "
                                      "Se consemnează cine l-a introdus și când."}}
        except curs_bnr.MonedaNecotata as _mn:
            # Moneda nu exista: nu e o intarziere, deci nu se ofera nici „reincearca", nici
            # „curs manual" — al doilea ar baga factura in contabilitate pe o moneda inventata.
            conn.rollback()
            return {"ok": False, "cod": "MONEDA_NECOTATA", "moneda": moneda,
                    "data": _d.isoformat(), "mesaj": str(_mn)}
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
            "data_curs=%s, curs_sursa=%s, curs_manual_de=%s, curs_manual_la=%s WHERE id=%s",
            (_curs, _tva_lei, _total_lei, _dcurs, _sursa,
             _urma_manual[0] if _urma_manual else None,
             _urma_manual[1] if _urma_manual else None, _fid))

    r["curs_bnr"] = _curs
    r["tva_lei"] = _tva_lei
    r["total_lei"] = _total_lei
    r["curs_sursa"] = _sursa
    # [R130] Data cursului și cât e de vechi ies din rută, nu doar în PDF. *„Sub prag: se
    # folosește, dar cursul și data lui apar pe factură ȘI în răspunsul rutei. Nu se mai tace
    # niciodată."* (Costin, 04.09.2026)
    r["data_curs"] = _dcurs.isoformat() if hasattr(_dcurs, "isoformat") else _dcurs
    r["curs_vechime_zile"] = (_d - _dcurs).days if hasattr(_dcurs, "isoformat") else None
    if _urma_manual:
        r["curs_manual_de"] = _urma_manual[0]
        r["curs_manual_la"] = _urma_manual[1].isoformat()
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
            "cota_tva": float(l["cota_tva"]),
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
