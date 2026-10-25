"""
core/salariati_api.py — salariați în schema unui tenant: listă, creare, detalii,
editare, ștergere. Alimentează D112 (payroll). Rulează pe conexiunea poziționată
pe schema tenantului.

Validare minimală pe server (PURĂ, testabilă): CNP 13 cifre, brut ≥ 0,
tip_norma ∈ {intreaga, partiala}. Prinde greșeli evidente devreme.

Traducere API<->DB: API foloseste tip_norma (text: intreaga/partiala), coloana
reala din DB e part_time (boolean). Traducerea se face la granita, contractul
API ramane neschimbat (compat cu main.py si frontend).

Ștergere PROTEJATĂ: dacă salariatul are concedii medicale, refuz curat.
"""
from __future__ import annotations
import re
from decimal import ROUND_HALF_UP

from core.common import cate as _cate
from core.pdf_util import data_ro as _data_ro   # DS cap.4: data pentru om, sursa unică

REGULI = "2026.1"
MODUL = "salariati_api"

_CNP = re.compile(r"^\d{13}$")
_NORME = ("intreaga", "partiala")
# [punctul 4, 04.10.2026] salariati.salariu_brut s-a retras: salariul contractual traieste numai in salariu_istoric
# (salariu_la/seteaza). Campul `salariu_brut` al API-ului ramane — e salariul CURENT citit din istoric.
_CAMPURI_API = ("cnp", "nume", "prenume", "data_angajare", "tip_norma", "ore_zi",
                "persoane_intretinere", "judet_casa", "data_incetare",  # [2b] salariu_brut -> salariu_istoric
                "data_nastere", "copii_scolarizati", "declaratie_copii",  # [deducere suplimentara]
                "scutit_contrib_minim", "motiv_exceptare", "cor", "functie_baza",  # [3c] CF art.77(1)
                "tichet_masa_valoare",  # [F133]
                "iban",  # [F134] cont beneficiar pt plata pe card
                "tip_contract", "nr_cim", "data_cim")  # [412] CIM pe fișă: Legea 53/2003 art.12 (durata), art.16 alin.(1) (scris)
# [412] durata CIM — Legea 53/2003 art.12: „(1) [...] se încheie pe durată nedeterminată. (2) Prin excepție, [...] și pe durată
# determinată”. Același nomenclator ca adeverința (`ad-tip`) și CHECK-ul coloanei (core/migrare_cim_salariat.py).
TIPURI_CONTRACT = ("nedeterminata", "determinata")


from core import chei_unice as _chei  # [R164 -> lotul 10, C73] refuzul bazei (CNP dublat) devine refuz citibil, prin helperul comun


def iban_valid(iban):
    """[F134] Verifica un IBAN romanesc: format (RO + 24 caractere) + cifra de control mod-97
    (ISO 13616/ISO 7064). PURA. NU se accepta IBAN neverificat in fisierul de plata catre banca
    (un IBAN gresit trimite banii altcuiva) - aceeasi disciplina ca CUI/CNP."""
    s = re.sub(r"\s", "", str(iban or "")).upper()
    if not re.match(r"^RO\d{2}[A-Z0-9]{20}$", s):  # RON domestic: RO + 2 control + 4 banca + 16 cont
        return False
    # mod-97: primele 4 caractere la coada, literele -> numere (A=10..Z=35), rest mod 97 == 1
    rearanjat = s[4:] + s[:4]
    numeric = "".join(str(int(c, 36)) if c.isalpha() else c for c in rearanjat)
    return int(numeric) % 97 == 1


def _api_spre_db(date):
    """Traduce cheile API (tip_norma) in coloane reale DB (part_time)."""
    d = dict(date)
    if "tip_norma" in d:
        tn = d.pop("tip_norma")
        if tn is not None:
            d["part_time"] = (tn == "partiala")
    for k in ("tip_contract", "nr_cim", "data_cim"):   # [412] câmp gol = necompletat (NULL), nu un text gol în coloană
        if k in d and d[k] is not None:
            d[k] = str(d[k]).strip() or None
    return d


def _db_spre_api(row):
    """Traduce un rand din DB (part_time bool) inapoi in forma API (tip_norma)."""
    if row is None:
        return None
    r = dict(row)
    if "part_time" in r:
        r["tip_norma"] = "partiala" if r.pop("part_time") else "intreaga"
    return r


# ============================================================
#  VALIDARE — PURĂ
# ============================================================
def _verifica_cor(conn, cod):
    """[F137] Ridica ValueError daca 'cod' e completat dar nu exista in nomenclatorul COR
    (public.cor_ocupatii). Gol = permis (COR optional). REGES respinge un cod inexistent."""
    cod = (str(cod).strip() if cod is not None else "")
    if not cod:
        # [#7] COR e OBLIGATORIU (necesar D112/REGES). Inainte "gol = permis" -> salariatul se salva fara COR.
        raise ValueError("Ocupația (cod COR) este obligatorie - alege ocupația din lista (necesară D112/REGES).")
    from core import cor_api
    if not cor_api.exista(conn, cod):
        raise ValueError("cod COR inexistent în nomenclator: %s (alege din lista)" % cod)


#: [lotul 12, C133] Motivul scutirii de contribuția minimă (D112 `motivExc`), după OPANAF 605/2026 anexa 2, secțiunea „Date de identificare
#: ale asiguratului”, pct.12: „se completează în cazul în care caseta de la pct.11 a fost completată cu valoarea «1»” — „1” elevi și
#: studenți până la 26 de ani (CF art.146 alin.(5^7) lit.a), „2” ucenici până la 18 ani (lit.b), „3” persoane cu dizabilități sau cărora
#: prin lege li se recunoaște lucrul mai puțin de 8 ore pe zi (lit.c), „4” pensionari pentru limită de vârstă (lit.d), „5” două sau mai
#: multe contracte cu baza cumulată cel puțin salariul minim (lit.e). Etichetele le arată ecranul (`firme.js`, `MOTIVE_EXCEPTARE`).
MOTIVE_EXCEPTARE = (1, 2, 3, 4, 5)

MESAJ_MOTIV_LIPSA = "Alege motivul scutirii de contribuția minimă — D112 îl declară (CF art.146 alin.(5^7))."
MESAJ_MOTIV_FARA_SCUTIRE = "Motivul scutirii se alege numai când salariatul e scutit de contribuția minimă."


def _motiv_valid(me):
    try:
        return me is not None and int(me) in MOTIVE_EXCEPTARE and str(me).strip() == str(int(me))
    except (TypeError, ValueError):
        return False


def _erori_motiv_exceptare(date, la_creare):
    """[C133] Scutit = Da cere motivul (altfel D112 nu-l poate declara exceptat: `asigExc` = 1 numai cu `motivExc` 1–5); motivul fără
    scutire nu are sens. La editare se verifică numai ce s-a trimis."""
    sc, me = date.get("scutit_contrib_minim"), date.get("motiv_exceptare")
    if me is not None:
        if not _motiv_valid(me):
            return [("motiv_exceptare", "Motivul scutirii e unul din cele cinci din listă (OPANAF 605/2026, D112 pct.12).")]
        if sc is False:
            return [("motiv_exceptare", MESAJ_MOTIV_FARA_SCUTIRE)]
    elif sc is True and ("motiv_exceptare" in date or la_creare):
        return [("motiv_exceptare", MESAJ_MOTIV_LIPSA)]
    return []


#: [lotul 12, C133 — comanda Costin 12.3 pct.8, verbatim în DECIZII: „«Scutit» și «Motiv» se pot corecta, cu jurnal (cine, când, vechi →
#: nou); motivul e obligatoriu când e bifat «Scutit».”] Câmpurile fișei a căror schimbare se consemnează în `salariati_jurnal`
#: (`core/migrare_salariati_jurnal.py`), pe ORICE drum care schimbă o fișă existentă: „Corectează datele” / „De verificat” / API
#: (`actualizeaza_salariat`) și reimportul (`salariati_import_api.importa`). Crearea nu e o corectură: nu se consemnează.
CAMPURI_JURNAL_SCUTIRE = ("scutit_contrib_minim", "motiv_exceptare")


def _text_jurnal(v):
    """Valoarea în jurnal: text, „true”/„false” pentru Da/Nu, None pentru gol (ca `firma_profil_jurnal`)."""
    return None if v is None else (str(v).lower() if isinstance(v, bool) else str(v))


def jurnalizeaza_scutirea(cur, salariat_id, vechi, nou):
    """[C133] Un rând în `salariati_jurnal` pentru fiecare câmp al scutirii (`CAMPURI_JURNAL_SCUTIRE`) prezent în `nou` care chiar s-a
    schimbat față de `vechi` (fișa de dinainte). Cine = utilizatorul cererii (`autor_cerere`, pus de middleware pe orice cerere); fără el,
    corectura se REFUZĂ înainte de scriere — o schimbare fără autor n-ar fi consemnată (ca la cota produsului, 472). Întoarce câte rânduri
    a scris."""
    schimbate = [(c, _text_jurnal((vechi or {}).get(c)), _text_jurnal(nou[c])) for c in CAMPURI_JURNAL_SCUTIRE
                 if c in nou and _text_jurnal((vechi or {}).get(c)) != _text_jurnal(nou[c])]
    if not schimbate:
        return 0
    from core import autor_cerere as _autor
    uid = _autor.uid()
    if uid is None:
        raise ValueError("Corectura scutirii de contribuția minimă se consemnează cu utilizatorul care o face — lipsește (cerere fără autor).")
    for camp, v, n in schimbate:
        cur.execute("INSERT INTO salariati_jurnal (salariat_id, camp, valoare_veche, valoare_noua, user_id) VALUES (%s, %s, %s, %s, %s)",
                    (salariat_id, camp, v, n, uid))
    return len(schimbate)


def jurnal_scutire(cur, salariat_id):
    """[C133] Toate corecturile scutirii salariatului (ecranul arată ultimele și numără restul), cea mai nouă prima: {camp, vechi, nou, cine, la}. „Cine” = numele persoanei (prenume
    nume), emailul numai dacă numele lipsește — ca jurnalul Date firmă (`repo_firma_profil.jurnal_firma`). Fără tabel (migrarea
    nerulată) -> []."""
    cur.execute("SELECT to_regclass('salariati_jurnal') IS NOT NULL")
    r = cur.fetchone()
    if not (list(r.values())[0] if isinstance(r, dict) else r[0]):
        return []
    cur.execute("SELECT j.camp, j.valoare_veche, j.valoare_noua, "
                "COALESCE(NULLIF(TRIM(CONCAT_WS(' ', u.prenume, u.nume)), ''), u.email) AS cine, j.la FROM salariati_jurnal j "
                "LEFT JOIN public.users u ON u.id = j.user_id WHERE j.salariat_id = %s ORDER BY j.la DESC, j.id DESC", (salariat_id,))
    out = []
    for x in cur.fetchall():
        x = tuple(x.values()) if isinstance(x, dict) else x
        out.append({"camp": x[0], "vechi": x[1], "nou": x[2], "cine": x[3], "la": x[4].isoformat() if x[4] else None})
    return out


def efect_corectura_d112(cur):
    """[C133] Ce face corectura scutirii cu D112, spus contabilului la salvare. D112 citește scutirea de pe fișă la generare
    (`d112.pull`), deci corectura intră în prima D112 generată după ea — cea a lunii de după ultima D112 depusă. Nimic deja depus sau emis
    nu se rescrie: D112 depusă rămâne cea depusă (o lună depusă se corectează numai prin rectificativă, generată de contabil — C77), iar
    fluturașul emis e exemplarul înghețat (`stat_plata_api.exemplar_curent`)."""
    cur.execute("SELECT max(make_date(d.an, d.luna, 1)) FROM public.declaratii_depuse d JOIN public.tenants t ON t.id = d.tenant_id "
                "WHERE t.schema_name = current_schema() AND d.tip = 'd112'")
    r = cur.fetchone()
    ult = (list(r.values())[0] if isinstance(r, dict) else r[0]) if r else None
    emise = "Fluturașii deja emiși rămân cum au fost tipăriți."
    if ult is None:
        return "Corectura scutirii intră în statul de plată și în D112 calculate de acum înainte. " + emise
    urm_an, urm_luna = (ult.year + 1, 1) if ult.month == 12 else (ult.year, ult.month + 1)
    return ("Corectura scutirii intră în D112 de la luna %02d/%d (ultima D112 depusă e pe luna %02d/%d). D112 deja depuse nu se rescriu: "
            "o lună depusă se corectează numai printr-o rectificativă, pe care o generezi tu din Declarații. %s"
            % (urm_luna, urm_an, ult.month, ult.year, emise))


def valideaza_salariat(date, la_creare=False):
    """Verifică datele unui salariat. Întoarce listă erori (gol = ok).
    la_creare=True -> câmpuri OBLIGATORII la creare: salariu brut (>0, #8) și COR (#7). La editare
    (la_creare=False) validăm doar câmpurile trimise (nu forțăm prezența lor)."""
    erori = []
    if not (date.get("nume") and str(date["nume"]).strip()):
        erori.append(("nume", "Numele este obligatoriu."))
    cnp = date.get("cnp")
    if cnp:
        # [cnp_control_v1] refolosim validarea COMPLETA (format + data + judet + CIFRA DE CONTROL)
        # din salariati_import_api - aceeasi cheie 279146358279 ca la import si cnp_ingrijit.
        # Inainte: doar _CNP (13 cifre) => un CNP cu cifra de control gresita intra tacut si strica
        # D112 (respins de DUK: cnpAsig invalid). Vezi GARZI 07.08 + E1E12_GASITE DEFECT-2.
        from core.salariati_import_api import valideaza_cnp as _vcnp
        _ok_cnp, _motiv_cnp = _vcnp(str(cnp))
        if not _ok_cnp:
            erori.append(("cnp", "CNP invalid: %s" % _motiv_cnp))
    elif la_creare:
        # [lotul 11, deficiența 454] CNP-ul e obligatoriu la creare: D112 identifică asiguratul după el (`d112.pull` refuză salariatul
        # fără CNP: „Completează-l în fisa salariatului, nu se emite D112 invalid”), deci un salariat salvat fără el oprește declarația
        erori.append(("cnp", "CNP-ul este obligatoriu — D112 declară salariatul după CNP."))
    brut = date.get("salariu_brut")
    _brut_gol = brut is None or (isinstance(brut, str) and not brut.strip())
    if la_creare and _brut_gol:
        # [#8] fara brut -> nicio intrare in salariu_istoric -> D112 baza zero. Obligatoriu la creare.
        erori.append(("salariu_brut", "Salariul brut este obligatoriu."))
    elif not _brut_gol:
        try:
            _b = float(brut)
            if _b < 0:
                erori.append(("salariu_brut", "Salariul brut nu poate fi negativ."))
            elif la_creare and _b <= 0:
                erori.append(("salariu_brut", "Salariul brut trebuie să fie mai mare ca 0."))
        except (TypeError, ValueError):
            erori.append(("salariu_brut", "Salariul brut e invalid."))
    cor = date.get("cor")
    if la_creare and not (cor is not None and str(cor).strip()):
        # [#7] COR obligatoriu la creare (per-camp; existenta in nomenclator o verifica _verifica_cor cu conn).
        erori.append(("cor", "Ocupația (cod COR) este obligatorie (necesară în D112 și REGES)."))
    tn = date.get("tip_norma")
    if tn is not None and tn not in _NORME:
        erori.append(("tip_norma", "Tip normă: alege 'intreaga' sau 'parțială'."))
    # [decizia Costin 07.10, pct.4] pe calea API, aceeași regulă ca pe ecran: cele trei fapte se cer explicit la creare
    if la_creare:
        if tn is None:
            erori.append(("tip_norma", "Tipul normei (întreagă / parțială) e obligatoriu — intră în D112."))
        if date.get("functie_baza") is None:
            erori.append(("functie_baza", "Funcția de bază la acest angajator (Da/Nu) e obligatorie — de ea depinde deducerea "
                                          "personală (CF art. 77 alin. (1))."))
        if date.get("scutit_contrib_minim") is None:
            erori.append(("scutit_contrib_minim", "Scutirea de contribuția minimă (Da/Nu) e obligatorie — intră în D112."))
    erori += _erori_motiv_exceptare(date, la_creare)
    # [F133] valoarea tichetului de masa: 0..plafon legal (nu poate depasi maximul legal/tichet)
    tmv = date.get("tichet_masa_valoare")
    if tmv is not None:
        try:
            v = float(tmv)
            if v < 0:
                erori.append(("tichet_masa_valoare", "Tichetul de masă nu poate fi negativ."))
            else:
                from core.common import cota
                plafon = float(cota("tichet_masa_plafon")[0])
                if v > plafon:
                    erori.append(("tichet_masa_valoare", f"Tichetul de masă depășește plafonul legal ({plafon:g} lei/tichet)."))
        except (TypeError, ValueError):
            erori.append(("tichet_masa_valoare", "Tichetul de masă e invalid."))
    # [F134] IBAN optional; daca e completat trebuie sa fie IBAN romanesc valid (mod-97)
    iban = date.get("iban")
    if iban is not None and str(iban).strip():
        if not iban_valid(iban):
            erori.append(("iban", "IBAN invalid (se așteaptă IBAN românesc: RO + 22 caractere, cifra de control corectă)."))
    # [412] contractul individual de muncă (opțional pe fișă): durata din nomenclatorul art.12, data CIM o dată din calendar
    tc = date.get("tip_contract")
    if tc is not None and str(tc).strip() and str(tc).strip() not in TIPURI_CONTRACT:
        erori.append(("tip_contract", "Tipul contractului: alege „nedeterminată” sau „determinată” (Codul muncii art. 12)."))
    dc = date.get("data_cim")
    if dc is not None and str(dc).strip():
        try:
            from datetime import date as _date
            _date.fromisoformat(str(dc)[:10])
        except (ValueError, TypeError):
            erori.append(("data_cim", "Data contractului individual de muncă nu e o dată din calendar."))
    # data_incetare (optional) >= data_angajare - contract activ o perioada coerenta (backstop: CHECK in DB)
    di, da = date.get("data_incetare"), date.get("data_angajare")
    if di is not None and str(di).strip() and da is not None and str(da).strip():
        try:
            from datetime import date as _date
            if _date.fromisoformat(str(di)[:10]) < _date.fromisoformat(str(da)[:10]):
                # [lotul 11, 454] pe câmp, ca toate celelalte: un șir simplu în listă rupea `_eroare_campuri` (despachetare) -> 500, nu refuz
                erori.append(("data_incetare", "Data încetării nu poate fi înainte de data angajării."))
        except (ValueError, TypeError):
            erori.append(("data_incetare", "Data încetării sau a angajării e invalidă."))
    return erori


# ============================================================
#  LISTĂ
# ============================================================
def lista_salariati(conn, activ=None):
    """Salariații, opțional filtrați pe cei ÎN SERVICIU (activ=True) / PLECAȚI (activ=False).
    'În serviciu' = data_incetare NULL sau în viitor. Parametrul `activ` e păstrat pentru
    compatibilitate API; sursa reală e data_incetare (Opțiunea A, PASUL 1)."""
    import psycopg2.extras as _E
    cond, val = "", []
    if activ is True:
        cond = " WHERE (data_incetare IS NULL OR data_incetare >= CURRENT_DATE) AND (data_angajare IS NULL OR data_angajare <= CURRENT_DATE)"
    elif activ is False:
        cond = " WHERE data_incetare < CURRENT_DATE"
    from core import salariu_istoric as _si
    from datetime import date as _dm
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, cnp, nume, prenume, data_angajare, part_time, ore_zi, "
            "persoane_intretinere, data_incetare, cor, tichet_masa_valoare, iban "
            "FROM salariati" + cond + " ORDER BY nume, prenume", val)
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r["salariu_brut"] = _si.salariu_la(cur, None, r["id"], _dm.today())  # [2b] salariul curent din istoric
    return [_db_spre_api(r) for r in rows]


# ============================================================
#  CREARE
# ============================================================
def _eroare_campuri(erori):
    """[G10 rule2/4] ValueError care poarta si erorile per-camp (lista {camp, mesaj}) pentru
    contractul backend {detail, erori_campuri}. camp = cheia semantica (frontend o prefixeaza cu forma)."""
    e = ValueError("; ".join(m for _c, m in erori))
    e.erori_campuri = [{"camp": c, "mesaj": m} for c, m in erori]
    return e


#: cheia naturală a salariatului: un CNP = un singur dosar la firmă
CONSTRANGERE_CNP = "salariati_cnp_uniq"


def _refuz_cnp(cnp):
    """[R164] Refuzul CNP-ului dublat, pe câmp (422) — la creare și [lotul 10, C73] la schimbarea CNP-ului unei fișe."""
    return _eroare_campuri([(
        "cnp",
        "Există deja un salariat cu CNP-ul %s la firma asta. Dacă e aceeași "
        "persoană reangajată, deschide-i fișa și completează noua dată de angajare "
        "— nu se creează un al doilea dosar pentru același om."
        % (cnp or ""))])


def _erori_din_baza(conn, date, erori, verifica_cor, salariat_id=None):
    """[lotul 11, deficiența 454] Verificările care cer baza — codul COR în nomenclator, CNP-ul deja la alt salariat al firmei — se ADAUGĂ
    la erorile de formă (`erori`, lista de perechi), ca refuzul să plece o dată, cu toate. Înainte fiecare pleca singur, după celelalte
    (`_verifica_cor` după validare, CNP-ul dublat abia la INSERT / UPDATE), iar contabilul afla erorile pe rând, la salvări succesive.
    Constrângerea `salariati_cnp_uniq` rămâne plasa (două salvări simultane): refuzul ei e același (`_refuz_cnp`)."""
    cu_eroare = {c for c, _m in erori}
    if verifica_cor and "cor" not in cu_eroare:
        try:
            _verifica_cor(conn, date.get("cor"))  # [F137] codul COR trebuie sa existe in nomenclator
        except ValueError as e:
            erori.append(("cor", str(e)))
    cnp = str(date.get("cnp") or "").strip()
    if cnp and "cnp" not in cu_eroare:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM salariati WHERE cnp = %s AND id IS DISTINCT FROM %s LIMIT 1", (cnp, salariat_id))
            if cur.fetchone():
                erori.extend((c["camp"], c["mesaj"]) for c in _refuz_cnp(cnp).erori_campuri)
    return erori


def creeaza_salariat(conn, **date):  # [R164] traduce refuzul bazei in refuzul casei
    """Inserează un salariat (după validare). Întoarce {ok, salariat_id} sau ridică
    ValueError cu erorile."""
    erori = valideaza_salariat(date, la_creare=True)
    if conn is not None:
        _erori_din_baza(conn, date, erori, verifica_cor=True)
    if erori:
        raise _eroare_campuri(erori)
    campuri_api = {k: date[k] for k in _CAMPURI_API if k in date and date[k] is not None}
    campuri_db = _api_spre_db(campuri_api)
    cols = list(campuri_db.keys())
    vals = list(campuri_db.values())
    ph = ", ".join(["%s"] * len(cols))
    from core import salariu_istoric as _si
    from datetime import date as _dm
    with conn.cursor() as cur:
        # [R164, 05.09.2026] Constrangerea `salariati_cnp_uniq` apara datele corect, dar
        # refuzul ei nu ajungea la om: exceptia iesea neprinsa si ruta raspundea **500**.
        # Se traduce in refuzul casei — `ValueError` cu eroare PE CAMP —, pe care ruta il
        # intoarce ca 422. *O poarta al carei mesaj se pierde pe drum apara datele si
        # lasa omul fara nimic de citit* — clasa R163/R134/R131.
        # [lotul 10, C73] prin helperul comun al clasei (`core/chei_unice.py`), nu printr-un `except` propriu
        with _chei.refuza_dublura(cur, (CONSTRANGERE_CNP,), lambda cur, e: _refuz_cnp(date.get("cnp"))):
            cur.execute(
                "INSERT INTO salariati (%s) VALUES (%s) RETURNING id"
                % (", ".join(cols), ph), vals)
            sid = cur.fetchone()[0]
        # [PASUL 2b] salariul de baza traieste pe salariu_istoric (SURSA UNICA)
        _sb = date.get("salariu_brut")
        if _sb is not None:
            _si.seteaza(cur, sid, _sb, date.get("data_angajare") or _dm.today().isoformat())
    return {"ok": True, "salariat_id": sid}


# ============================================================
#  DETALII
# ============================================================
def detalii_salariat(conn, salariat_id):
    """Un salariat complet, sau None."""
    import psycopg2.extras as _E
    from core import salariu_istoric as _si
    from datetime import date as _dm
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, cnp, nume, prenume, data_angajare, part_time, ore_zi, "
            "persoane_intretinere, judet_casa, data_incetare, "
            "scutit_contrib_minim, motiv_exceptare, cor, tichet_masa_valoare, iban, de_verificat, "
            "tip_contract, nr_cim, data_cim, "   # [412] CIM-ul de pe fișă (adeverința îl precompletează)
            # [lotul 10, SalariatEdit] „Corectează datele” le arată pe cele salvate (deducerile CF art.77 alin.(1), (10), (12) depind de ele)
            "functie_baza, data_nastere, copii_scolarizati, declaratie_copii "
            "FROM salariati WHERE id = %s", (salariat_id,))
        r = cur.fetchone()
        if r:
            r = dict(r)
            r["salariu_brut"] = _si.salariu_la(cur, None, salariat_id, _dm.today())  # [2b] curent din istoric
            # [salariul în timp] istoricul vizibil în ecranul de schimbare (ce date sunt deja ocupate)
            r["istoric_salariu"] = [{"valabil_din": v.isoformat(), "salariu_brut": float(s)}
                                    for v, s in _si.intrari(cur, None, salariat_id)]
            # [C133] corecturile scutirii (cine, când, vechi -> nou), vizibile în „Corectează datele”
            r["jurnal_scutire"] = jurnal_scutire(cur, salariat_id)
    return _db_spre_api(r) if r else None


# ============================================================
#  EDITARE (doar câmpurile trimise, validate)
# ============================================================
def _refuz_suspendare(cod, mesaj):
    """[lot 19 pct.4c] Refuzul unei suspendări: mesajul pentru om + `cod` (motivul, ca dată — gărzile asertează pe el)."""
    e = _eroare_campuri([("suspendari", mesaj)])
    e.cod = cod
    return e


TIPURI_SUSPENDARE = {"cfp": "Concediu fără plată (Codul muncii art.54, art.153)",
                     "suspendare": "Suspendare fără drepturi salariale (Codul muncii art.49 alin.(2))"}


def valideaza_suspendari(conn, salariat_id, lista):
    """[lot 19 pct.4c] Lista de suspendări a salariatului, validată ÎNAINTE de scriere. Întoarce
    `[(inceput, sfarsit, tip, temei)]` sau ridică cu câmpul numit. Refuză: tip necunoscut, dată lipsă/invalidă, sfârșit
    înaintea începutului, interval în afara contractului (art.49: se suspendă un contract EXISTENT), suprapuneri între
    ele, suprapunere cu un concediu medical (aceeași zi nu poate fi și CM, și CFP — ar scădea de două ori din brut)."""
    from datetime import date as _dm
    from core import repo_salariati as _rs
    if not isinstance(lista, list):
        raise _refuz_suspendare("nu_e_lista", "Lista de suspendări trebuie să fie o listă.")
    with conn.cursor() as cur:
        contract = _rs.contract_salariat(cur, salariat_id)
    da, di = (contract or (None, None))[:2]
    out = []
    for i, x in enumerate(lista, 1):
        x = x if isinstance(x, dict) else {}
        tip = str(x.get("tip") or "").strip()
        if tip not in TIPURI_SUSPENDARE:
            raise _refuz_suspendare("tip_necunoscut", "Suspendarea %d: tipul trebuie să fie „cfp” sau „suspendare”." % i)
        try:
            a = _dm.fromisoformat(str(x.get("data_inceput") or "")[:10])
            b = _dm.fromisoformat(str(x.get("data_sfarsit") or "")[:10])
        except ValueError:
            raise _refuz_suspendare("data_lipsa", "Suspendarea %d: data de început și data de sfârșit sunt "
                                                  "obligatorii (AAAA-LL-ZZ)." % i)
        if b < a:
            raise _refuz_suspendare("interval_inversat", "Suspendarea %d: sfârșitul (%s) e înaintea începutului (%s)." % (i, b, a))
        if da and a < da:
            raise _refuz_suspendare("inainte_de_angajare", "Suspendarea %d începe pe %s, înainte de angajare (%s): se "
                                    "suspendă doar un contract în vigoare (Codul muncii art.49)." % (i, a, da))
        if di and b > di:
            raise _refuz_suspendare("dupa_incetare", "Suspendarea %d se termină pe %s, după încetarea contractului (%s)."
                                    % (i, b, di))
        out.append((a, b, tip, (str(x.get("temei") or "").strip() or None)))
    out.sort()
    for (a1, b1, _t1, _), (a2, b2, _t2, _) in zip(out, out[1:]):
        if a2 <= b1:
            raise _refuz_suspendare("suprapunere", "Suspendările %s–%s și %s–%s se suprapun." % (a1, b1, a2, b2))
    with conn.cursor() as cur:
        for a, b, _t, _ in out:
            cm = _rs.concedii_medicale_suprapuse(cur, salariat_id, a, b)
            if cm:
                raise _refuz_suspendare("suprapunere_cm", "Suspendarea %s–%s se suprapune cu concediul medical %s–%s: "
                                        "aceeași zi nu poate fi și CM, și suspendare." % (a, b, cm[0][0], cm[0][1]))
    return out


def seteaza_suspendari(conn, salariat_id, lista_validata):
    from core import repo_salariati as _rs
    with conn.cursor() as cur:
        _rs.inlocuieste_suspendari(cur, salariat_id, lista_validata)


COD_DATA_OCUPATA = "SALARIU_DATA_OCUPATA"


def _ro(d):
    from core.pdf_util import data_ro   # formatarea unică a datei pentru om
    return data_ro(d)


def valideaza_schimbare_salariu(conn, salariat_id, salariu_brut, valabil_din, inlocuieste=False,
                                data_angajare=None, data_incetare=None):
    """[salariul în timp, decizia Costin 04.10.2026] Verifică o schimbare de salariu ÎNAINTE de scriere și întoarce
    (data, ultima_zi_atinsa): data e ziua de la care se aplică, ultima_zi_atinsa = ziua dinaintea următoarei intrări din
    istoric (sau None: schimbarea ține până la o nouă schimbare) — apelantul trece lunile atinse prin poarta de perioadă.

    Refuzuri NUMITE, ca erori pe câmpul `valabil_din` (ecranul le pune lângă câmp, valorile tastate rămân):
      * nu e o dată din calendar;
      * e înainte de angajare sau după încetare (salariul unei zile fără contract n-are unde intra);
      * există deja o intrare în istoric la aceeași dată — „suprapusă”: refuz cu intrarea existentă (cod
        SALARIU_DATA_OCUPATA), afară de cazul în care apelantul cere EXPLICIT înlocuirea (`inlocuieste`).
    `data_angajare` / `data_incetare` = valorile trimise în aceeași cerere (au prioritate față de cele din bază)."""
    import datetime as _dt
    from core import salariu_istoric as _si
    try:
        d = _dt.date.fromisoformat(str(valabil_din)[:10]) if valabil_din else _dt.date.today()
    except ValueError:
        raise _eroare_campuri([("valabil_din", "Data de la care se aplică salariul (%r) nu e o dată din calendar. "
                                               "Alege ziua din câmpul „de la”." % (valabil_din,))])
    with conn.cursor() as cur:
        cur.execute("SELECT data_angajare, data_incetare FROM salariati WHERE id = %s", (salariat_id,))
        r = cur.fetchone()
        da = _dt.date.fromisoformat(str(data_angajare)[:10]) if data_angajare else (r[0] if r else None)
        di = _dt.date.fromisoformat(str(data_incetare)[:10]) if data_incetare else (r[1] if r else None)
        if da and d < da:
            raise _eroare_campuri([("valabil_din", "Salariul nu se poate aplica de la %s: contractul începe pe %s. Alege o "
                                                   "dată de la angajare încolo." % (_ro(d), _ro(da)))])
        if di and d > di:
            raise _eroare_campuri([("valabil_din", "Salariul nu se poate aplica de la %s: contractul a încetat pe %s."
                                                   % (_ro(d), _ro(di)))])
        istoric = _si.intrari(cur, None, salariat_id)
    existent = next((s for v, s in istoric if v == d), None)
    if existent is not None and not inlocuieste:
        e = _eroare_campuri([("valabil_din", "Există deja un salariu de la %s: %s lei. Alege altă dată pentru o schimbare "
                                             "nouă sau înlocuiește explicit salariul de la această dată."
                              % (_ro(d), _fmt_lei(existent)))])
        e.cod, e.existent = COD_DATA_OCUPATA, {"valabil_din": d.isoformat(), "salariu_brut": float(existent),
                                               "salariu_nou": float(salariu_brut)}
        raise e
    urm = next((v for v, _s in istoric if v > d), None)
    return d, (urm - _dt.timedelta(days=1)) if urm else None


def _fmt_lei(v):
    return "{:,.2f}".format(float(v)).replace(",", "X").replace(".", ",").replace("X", ".")


def actualizeaza_salariat(conn, salariat_id, _golite=(), **date):
    """Editează câmpurile date (validate). salariu_brut e o SCHIMBARE DE SALARIU -> intrare NOUĂ în
    salariu_istoric la valabil_din (implicit azi), nu UPDATE pe salariati (PASUL 2b, sursă unică).

    [R51] `_golite` = cheile pe care apelantul le-a trimis EXPLICIT cu `null`. Fără ele, `None`
    ar însemna și „n-am trimis câmpul", și „golește-l" — iar o dată de încetare pusă din
    greșeală n-ar mai putea fi scoasă. Apelanții vechi nu-l trimit; comportamentul lor nu se
    schimbă."""
    from core import salariu_istoric as _si
    from datetime import date as _dm
    campuri_api = {k: v for k, v in date.items() if k in _CAMPURI_API and v is not None}
    for k in (_golite or ()):
        if k in _CAMPURI_API:
            campuri_api[k] = None
    _sb = date.get("salariu_brut")
    if not campuri_api and _sb is None:
        return {"ok": True, "neschimbat": True}
    # [C133] scutirea pusă pe „Nu” golește motivul ei; pusă pe „Da”, motivul se cere (trimis acum sau deja în fișă)
    if campuri_api.get("scutit_contrib_minim") is False and "motiv_exceptare" not in campuri_api:
        campuri_api["motiv_exceptare"] = None
    scutire_veche = None
    if any(c in campuri_api for c in CAMPURI_JURNAL_SCUTIRE):
        # [C133, comanda Costin 12.3 pct.8] fișa de dinainte, cu rândul BLOCAT (două salvări simultane nu scriu același „vechi” în jurnal)
        with conn.cursor() as cur:
            cur.execute("SELECT scutit_contrib_minim, motiv_exceptare FROM salariati WHERE id = %s FOR UPDATE", (salariat_id,))
            _r = cur.fetchone()
        scutire_veche = dict(zip(CAMPURI_JURNAL_SCUTIRE, (tuple(_r.values()) if isinstance(_r, dict) else _r) if _r else (None, None)))
    erori = valideaza_salariat({**campuri_api, "salariu_brut": _sb,
                                "data_angajare": date.get("data_angajare"),
                                "data_incetare": date.get("data_incetare"),
                                "nume": campuri_api.get("nume", "x")})
    erori = [(c, m) for (c, m) in erori if c != "nume"]
    if scutire_veche is not None and "motiv_exceptare" not in {c for c, _m in erori}:
        # [C133] starea REZULTATĂ (fișa + ce s-a trimis), nu numai ce s-a trimis: „Scutit” = Da rămas fără motiv (motivul golit, sau
        # scutirea pusă pe Da peste o fișă fără motiv) și motivul ales pe o fișă nescutită se refuză pe câmpul motivului
        sc = campuri_api.get("scutit_contrib_minim", scutire_veche["scutit_contrib_minim"])
        me = campuri_api.get("motiv_exceptare", scutire_veche["motiv_exceptare"])
        if sc is True and not _motiv_valid(me):
            erori.append(("motiv_exceptare", MESAJ_MOTIV_LIPSA))
        elif not sc and me is not None:
            erori.append(("motiv_exceptare", MESAJ_MOTIV_FARA_SCUTIRE))
    # [lotul 11, 454 — aceeași clasă la „Corectează datele”] COR-ul și CNP-ul dublat în același refuz cu restul
    _erori_din_baza(conn, campuri_api, erori, verifica_cor="cor" in campuri_api, salariat_id=salariat_id)
    if erori:
        raise _eroare_campuri(erori)
    consemnate = 0
    with conn.cursor() as cur:
        if scutire_veche is not None:
            # [C133] jurnalul (cine, când, vechi -> nou) ÎNAINTEA scrierii: fără autorul cererii corectura se refuză, nu se scrie neconsemnată
            consemnate = jurnalizeaza_scutirea(cur, salariat_id, scutire_veche, campuri_api)
        if campuri_api:
            campuri = _api_spre_db(campuri_api)
            seturi = ", ".join("%s = %%s" % k for k in campuri)
            # [lotul 10, C73] CNP-ul schimbat pe al altui salariat -> același refuz pe câmp ca la creare, nu 500
            with _chei.refuza_dublura(cur, (CONSTRANGERE_CNP,), lambda cur, e: _refuz_cnp(campuri_api.get("cnp"))):
                cur.execute("UPDATE salariati SET %s WHERE id = %%s" % seturi,
                            list(campuri.values()) + [salariat_id])
            # [decizia Costin 14.10.2026 pct.3–4] câmpul salvat de contabil e CONFIRMAT: iese din marcajul de import
            # („persoane în întreținere de completat”, „scutirea de verificat”) — avertismentul din statul de plată dispare
            # [lotul 10, deficiența 420] și norma / funcția de bază propuse la import (sursa unică a câmpurilor marcabile: DE_VERIFICAT)
            from core.salariati_import_api import DE_VERIFICAT as _DV
            _confirmate = [c for c in _DV if c in campuri_api]
            if _confirmate:
                cur.execute("UPDATE salariati SET de_verificat = ARRAY(SELECT x FROM unnest(de_verificat) x "
                            "WHERE x <> ALL(%s::text[])) WHERE id = %s", (_confirmate, salariat_id))
        if _sb is not None:
            _si.seteaza(cur, salariat_id, _sb, date.get("valabil_din") or _dm.today().isoformat())
        if consemnate:
            # [C133] ce face corectura cu D112: intră de la luna de după ultima D112 depusă; ce e depus sau emis nu se rescrie
            return {"ok": True, "scutire_corectata": True, "efect_d112": efect_corectura_d112(cur)}
    return {"ok": True}


# ============================================================
#  ȘTERGERE — protejată (concedii medicale legate)
# ============================================================
def _refuz_sterge():
    return {"ok": False, "cod": "ARE_LUNI_DECLARATE",
            "mesaj": ("Salariatul are luni declarate. Nu se șterge - completează data încetării "
                      "contractului, altfel se pierde istoricul care susține declarațiile deja depuse.")}


def sterge_salariat(conn, salariat_id):
    """Hard-delete DOAR pentru greseala de introducere: salariat fara nicio luna declarata. La PLECARE
    NU se sterge - se completeaza data_incetare (istoricul sustine declaratiile depuse). Refuza daca are
    concedii medicale, are o perioada CONFIRMATA (pontaj/salarizare) de la angajare incoace, sau
    tenantul are vreun D112 depus pentru o
    luna >= luna angajarii (grosier per tenant+luna: declaratii_depuse nu e per-salariat -> err-on-refuse,
    vezi DECIZII + datoria state_plata)."""
    with conn.cursor() as cur:
        cur.execute("SELECT data_angajare FROM salariati WHERE id = %s", (salariat_id,))
        r = cur.fetchone()
        if not r:
            return {"ok": False, "cod": "INEXISTENT"}
        data_ang = r[0]
        cur.execute("SELECT count(*) FROM concedii_medicale WHERE salariat_id = %s", (salariat_id,))
        if cur.fetchone()[0]:
            return _refuz_sterge()
        # [get_safe_v1 20.08.2026] AICI se citea `state_plata` ca dovada ca salariatul "a fost pe un
        # stat de plata". NU era o dovada: tabelul se popula ca efect secundar al lui GET /stat-plata -
        # simpla deschidere a ecranului Salariati scria un rand per salariat si il comitea, deci poarta
        # se inchidea din VIZITARE, nu din emitere. De cand GET-ul nu mai scrie (main.py), nimic nu mai
        # populeaza tabelul, iar verificarea ar fi ramas logica moarta care PARE protectie si care ar fi
        # prins doar reziduu de navigare ramas in baza.
        # Semnalul REAL ca luna e blocata e perioada CONFIRMATA - scrisa deliberat de utilizator prin
        # core/perioada.confirma(). Grosier per tenant+luna, ca si poarta D112 de mai jos: err-on-refuse.
        if data_ang is not None:
            cur.execute("SELECT count(*) FROM perioada_confirmata "
                        "WHERE domeniu IN ('pontaj', 'salarizare') "
                        "AND make_date(an, luna, 1) >= date_trunc('month', %s::date)", (data_ang,))
            if cur.fetchone()[0]:
                return _refuz_sterge()
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = current_schema()")
        t = cur.fetchone()
        if t and data_ang is not None:
            cur.execute("SELECT count(*) FROM public.declaratii_depuse "
                        "WHERE tenant_id = %s AND tip = %s "
                        "AND make_date(an, luna, 1) >= date_trunc(%s, %s::date)",
                        (t[0], "d112", "month", data_ang))
            if cur.fetchone()[0]:
                return _refuz_sterge()
        # [orfani_salariu_istoric 20.08.2026] salariu_istoric NU are FK catre salariati (tenant_template
        # l.1176-1183), deci nimic nu cascadeaza: pana acum stergerea lasa istoricul salarial in urma
        # (24 din 30 randuri orfane pe tenant_001, gasit la auditul t001). Hard-delete-ul asta e rezervat
        # greselii de introducere, deci trebuie sa stearga inregistrarea INTREAGA. Copiii se sterg
        # INAINTE de parinte, in aceeasi tranzactie. Celelalte tabele cu salariat_id (concedii_medicale,
        # state_plata) sunt deja porti de REFUZ mai sus; beneficii_lunare are FK fara ON DELETE, deci
        # blocheaza stergerea zgomotos - nu o sterg tacit.
        cur.execute("DELETE FROM salariu_istoric WHERE salariat_id = %s", (salariat_id,))
        cur.execute("DELETE FROM pontaj WHERE salariat_id = %s", (salariat_id,))
        cur.execute("DELETE FROM salariati WHERE id = %s", (salariat_id,))
        sters = cur.rowcount > 0
    return {"ok": sters}


# ============================================================
#  CONCEDII MEDICALE — calcul (calcul_cm + taxe_cm) + salvare
# ============================================================
def lista_concedii(conn, salariat_id, an=None):
    """Concediile medicale ale unui salariat, optional filtrate pe an. Desc dupa data inceput."""
    with conn.cursor() as cur:
        if an:
            cur.execute("SELECT * FROM concedii_medicale WHERE salariat_id=%s AND an=%s "
                        "ORDER BY data_inceput DESC NULLS LAST, id DESC", (salariat_id, an))
        else:
            cur.execute("SELECT * FROM concedii_medicale WHERE salariat_id=%s "
                        "ORDER BY data_inceput DESC NULLS LAST, id DESC", (salariat_id,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


def _dec_pos(v):
    try: return float(v)
    except (TypeError, ValueError): return 0.0


#: [lotul 11, 440] câmpul de dată al cererii -> id-ul din formularul Concediu medical (`flux_concediu.js`)
_ID_DATA_CM = {"data_inceput": "cm-inceput", "data_sfarsit": "cm-sfarsit", "data_acordare": "cm-acord"}
#: etichetele câmpurilor de dată din formularul concediului (`static/js/ecrane/flux_concediu.js`), pentru refuz
_ETICHETA_DATA_CM = {"data_inceput": "Data început", "data_sfarsit": "Data sfârșit", "data_acordare": "Data acordării"}


#: [lotul 11, C92] structura D112 (nu normă — regulă de validator): „D_12<= 36 daca (D_5<=29.05.2020 sau D_5>=24.10.2023)” — codul bolii
#: infecto-contagioase are plafonul 36 în afara ferestrei dintre cele două date (D_5 = data acordării); în fereastră se cere numai prezența
LIMITE_D12_COD_BOALA = {"pana_la": "2020-05-29", "de_la": "2023-10-24", "maxim": 36}


def salveaza_concediu(conn, salariat_id, date):
    """Calculeaza indemnizatia CM (calcul_cm + taxe_cm) si o salveaza in concedii_medicale.
    date: serie, numar, cod, data_acordare, data_inceput, data_sfarsit, loc_prescriere,
          diagnostic, spitalizare, zile_cm (lucratoare), venituri_6_luni, zile_6_luni,
          an, luna, procent_accident (optional). Intoarce randul salvat + breakdown calcul."""
    from core import salarizare as _s
    from decimal import Decimal
    # [lotul 11, deficiența 440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp”]
    # Refuzurile de formă (codul, codul de urgență, CNP-ul, datele, veniturile, zilele, certificatul inițial) se ADAUGĂ, cu id-ul
    # câmpului din formularul Concediu medical (`flux_concediu.js`), și pleacă o dată (`DateInvalide`, 422 — ca `ValueError`-ul de
    # dinainte, prins de `cm_salveaza`). Certificatul inițial negăsit (starea evidenței) rămâne refuzul unic de după.
    from core.erori import ErorileFormularului as _Erori
    _er = _Erori("Concediul medical nu s-a salvat")
    cod = str(date.get("cod") or "01").zfill(2)
    zile_cm = int(date.get("zile_cm") or 0)
    ven6 = date.get("venituri_6_luni") or 0
    zile6 = int(date.get("zile_6_luni") or 1)
    # CM4 [optional] venituri_lunare = [[venit, zile, luna_iso], ...] -> plafon 12sm per-luna in calcul_cm.
    # Backward-compat: fara defalcare, comportament vechi (ven6/zile6 pe suma, fara plafon).
    _vlun_raw = date.get("venituri_lunare")
    venituri_lunare = None
    if _vlun_raw:
        import datetime as _dtl
        venituri_lunare = []
        for _e in _vlun_raw:
            _v, _z, _l = _e[0], _e[1], _e[2]
            _ld = _l if hasattr(_l, "year") else _dtl.date.fromisoformat(str(_l)[:10])
            venituri_lunare.append((_v, int(_z), _ld))
        ven6 = sum((_dec_pos(_e[0]) for _e in venituri_lunare), _dec_pos(0))
        zile6 = sum(int(_e[1]) for _e in venituri_lunare)
    spitalizare = bool(date.get("spitalizare"))
    program_national = bool(date.get("program_national"))  # [D_9a] marcaj program national de sanatate
    pacc = int(date.get("procent_accident") or 100)
    cod_urgenta = date.get("cod_urgenta")
    cod_urgenta = int(cod_urgenta) if cod_urgenta not in (None, "") else None
    if cod == "06":
        # [D_11] D112 C(3): la cod 06 (urgenta medico-chirurgicala) D_11 e OBLIGATORIU
        # (nomenclator HG 423/2020). D_11<=177 daca data_acordare>29.05.2020, altfel <=175.
        import datetime as _dtu
        _dac = date.get("data_acordare")
        try:
            _ddac = _dtu.date.fromisoformat(str(_dac)[:10]) if _dac else None
        except ValueError:
            _ddac = None
        _maxu = 175 if (_ddac and _ddac <= _dtu.date(2020, 5, 29)) else 177
        if cod_urgenta is None or not (1 <= cod_urgenta <= _maxu):
            _er.camp("cm-urgenta", "La codul 06 (urgență medico-chirurgicală) completează codul de urgență "
                                   "(1..%d, nomenclator HG 423/2020) - D112 îl cere obligatoriu." % _maxu)
    # [lotul 11, C92] structura D112: D_13 „D_13#null pentru D_9 = 10” (DUK regula S102); D_12 „daca D_9= (05,51) atunci D_12#null”,
    # „D_12<= 36 daca (D_5<=29.05.2020 sau D_5>=24.10.2023)” — același câmp de pe ecran (`cm-urgenta`), eticheta după cod
    if cod == "10" and (cod_urgenta is None or cod_urgenta < 1):
        _er.camp("cm-urgenta", "La codul 10 completează numărul avizului medicului expert — D112 îl cere.")
    if cod in ("05", "51"):
        _d5 = str(date.get("data_acordare") or "")[:10]   # ISO: comparația pe text e comparația pe dată
        _lim = LIMITE_D12_COD_BOALA
        _cu_plafon = not _d5 or _d5 <= _lim["pana_la"] or _d5 >= _lim["de_la"]
        if cod_urgenta is None or cod_urgenta < 1 or (_cu_plafon and cod_urgenta > _lim["maxim"]):
            _er.camp("cm-urgenta", "La codurile 05 și 51 completează codul bolii infecto-contagioase (1–36) — D112 îl cere.")
    # [D_8/D_8a, regula DUK S97] cod 09/91/92 cer CNP copil, cod 17 cere CNP pacient oncologic. Validare
    # cifra de control (valideaza_cnp) - un CNP invalid NU intra (part 2). Restul codurilor: cnp_ingrijit=None.
    cnp_ingrijit = str(date.get("cnp_ingrijit") or "").strip() or None
    if cod in ("09", "91", "92", "17"):
        from core.salariati_import_api import valideaza_cnp as _vcnp
        _okc, _motc = _vcnp(cnp_ingrijit or "")
        if not _okc:
            _cmp = "CNP-ul pacientului cu afectiuni oncologice" if cod == "17" else "CNP-ul copilului"
            _er.camp("cm-cnp-ingrijit", "La codul %s completează %s (persoana pentru care s-a eliberat certificatul) - "
                                        "D112 îl cere obligatoriu, regula DUK S97: %s." % (cod, _cmp, _motc))
    import datetime as _dtmod
    _di = date.get("data_inceput") or None
    if isinstance(_di, str) and _di:
        try: la_data = _dtmod.date.fromisoformat(_di[:10])
        except ValueError: la_data = None
    else:
        la_data = _di
    # [gating diminuare] OUG 91/2025 art.II(1): fereastra se aplica dupa DATA ELIBERARII certificatului
    # (data_acordare), nu dupa data_inceput -> data_eliberare pt dispecerul de variante din calcul_cm.
    _dacg = date.get("data_acordare") or None
    if isinstance(_dacg, str) and _dacg:
        try: data_elib = _dtmod.date.fromisoformat(_dacg[:10])
        except ValueError: data_elib = None
    else:
        data_elib = _dacg

    # [G9] Data de sfarsit e OBLIGATORIE (asterisc UI real): un CM fara sfarsit = perioada corupta in D112.
    if not (date.get("data_sfarsit") or None):
        _er.camp("cm-sfarsit", "Data de sfârșit a concediului medical e obligatorie (perioada concediului medical, de la început până la "
                               "sfârșit, intră în D112).")
    # [lotul 4, 04.09.2026] ORDINEA. Pana azi, un cod inexistent, o data care nu e in calendar si un
    # sfarsit inaintea inceputului primeau, toate trei, mesajul despre VENITURILE PE 6 LUNI — fiindca
    # verificarea bazei de calcul rula inaintea formei campurilor. A patra instanta a clasei „refuzul
    # numeste alt camp", dupa loturile 1, 2 si 3. Forma intai: ce a tastat omul, apoi ce lipseste din
    # dosarul firmei.
    from core import nomenclator_cm as _ncm
    if _ncm.normalizeaza(cod) not in _ncm.CODURI:
        _er.camp("cm-cod", "Codul de indemnizație %r nu există în nomenclatorul concediilor medicale. "
                           "Codurile cunoscute: %s." % (date.get("cod"), ", ".join(sorted(_ncm.CODURI))))
    _dati = {}
    for _camp in ("data_inceput", "data_sfarsit", "data_acordare"):
        _v = date.get(_camp)
        if not _v:
            continue
        try:
            _dati[_camp] = _dtmod.date.fromisoformat(str(_v)[:10])
        except ValueError:
            _er.camp(_ID_DATA_CM[_camp], "%s: %r nu e o dată din calendar. Se așteaptă forma AAAA-LL-ZZ, cu o zi "
                                         "care există în luna aia." % (_ETICHETA_DATA_CM[_camp], _v))
    if ("data_inceput" in _dati and "data_sfarsit" in _dati
            and _dati["data_sfarsit"] < _dati["data_inceput"]):
        _er.camp("cm-sfarsit", "Concediul se sfârșește (%s) înaintea zilei în care începe (%s). "
                               "Verifică cele două date de pe certificat."
                               % (_data_ro(_dati["data_sfarsit"]), _data_ro(_dati["data_inceput"])))
    # Validare: baza de calcul trebuie sa fie reala (altfel brut 0 dar net pozitiv = imposibil)
    if _dec_pos(ven6) <= 0:
        _er.camp("cm-ven6", "Veniturile brute pe 6 luni lipsesc sau sunt 0 - completează baza de calcul din statele de plata.")
    if zile6 <= 0:
        _er.camp("cm-zile6", "Zilele lucrătoare din cele 6 luni lipsesc sau sunt 0.")
    if zile_cm <= 0:
        _er.camp("cm-zile", "Zilele lucrătoare CM trebuie să fie cel puțin 1.")
    # ===== [CM-episod] context de EPISOD — OUG 158/2005 art.17(1): indemnizatia se raporteaza la
    # fiecare EPISOD de boala, nu la certificatul izolat. Certificatul de continuare apartine
    # aceluiasi episod ca cel initial (transcriere de pe hartie, nu deductie). =====
    este_continuare = bool(date.get("este_continuare"))
    if este_continuare:
        serie_ini = (str(date.get("serie_initiala") or "")).strip()
        numar_ini = (str(date.get("numar_initial") or "")).strip()
        if not serie_ini:
            _er.camp("cm-serie-ini", "Certificat de continuare: introdu seria certificatului inițial al episodului (e tipărită pe "
                                     "certificatul de continuare) - fără ea episodul nu se leagă.")
        if not numar_ini:
            _er.camp("cm-numar-ini", "Certificat de continuare: introdu numărul certificatului inițial al episodului (e tipărit pe "
                                     "certificatul de continuare) - fără el episodul nu se leagă.")
    # [lotul 11, deficiența 440] toate refuzurile de formă ale certificatului, deodată, fiecare lângă câmpul ei din Concediu medical
    _er.refuza()
    # [lotul 12, C102.1] Zilele lucrătoare CM peste zilele lucrătoare ale intervalului certificatului (L–V, fără sărbătorile legale:
    # `scadente.zile_lucratoare_interval`, același calendar ca propunerea din ecran) = de regulă o greșeală de introducere („10 zile” pe un
    # interval cu 5), care ar merge mai departe în indemnizație și în D112. Nu se refuză (programul de lucru al salariatului poate avea
    # zile lucrătoare în weekend — atunci cifra e corectă), dar nici nu se salvează tăcut: răspunsul cere confirmarea, iar „Salvează cu N
    # zile” retrimite certificatul cu `confirma_zile_peste_interval`. Același tipar ca nota neschimbată (`cod` + `mesaj`, ecranul întreabă).
    zile_interval = None
    if "data_inceput" in _dati and "data_sfarsit" in _dati:
        from core import scadente as _scad
        try:
            zile_interval = _scad.zile_lucratoare_interval(_dati["data_inceput"], _dati["data_sfarsit"])
        except ValueError:   # an în afara calendarului de sărbători (`scadente.sarbatori_legale`): intervalul nu se poate număra
            zile_interval = None
    if zile_interval is not None and zile_cm > zile_interval and not date.get("confirma_zile_peste_interval"):
        return {"ok": False, "cod": "CONFIRMA_ZILE_PESTE_INTERVAL", "zile_cm": zile_cm, "zile_interval": zile_interval,
                "mesaj": "Ai scris %s de concediu medical, dar între %s și %s sunt %s (fără weekend și sărbători legale). Verifică "
                         "cifra de pe certificat. Salvezi certificatul cu %s?"
                         % (_cate(zile_cm, "zi lucrătoare", "zile lucrătoare"), _data_ro(_dati["data_inceput"]),
                            _data_ro(_dati["data_sfarsit"]), _cate(zile_interval, "zi lucrătoare", "zile lucrătoare"),
                            _cate(zile_cm, "zi", "zile"))}
    if este_continuare:
        with conn.cursor() as cur:
            cur.execute("SELECT data_inceput FROM concedii_medicale WHERE salariat_id=%s AND serie=%s "
                        "AND numar=%s ORDER BY data_inceput LIMIT 1", (salariat_id, serie_ini, numar_ini))
            _rini = cur.fetchone()
        if not _rini:
            raise ValueError("Certificatul inițial %s/%s nu există pentru acest salariat - verifică seria/numărul "
                             "certificatului anterior de pe certificatul de continuare." % (serie_ini, numar_ini))
        data_ini = _rini[0]
        prima_zi = False
    else:
        serie_ini, numar_ini, data_ini, prima_zi = date.get("serie"), date.get("numar"), la_data, True
    with conn.cursor() as cur:
        cur.execute("SELECT id, an, luna, cod, zile, media_zilnica, data_inceput, "
                    "(serie IS NOT DISTINCT FROM serie_initiala AND numar IS NOT DISTINCT FROM numar_initial), "
                    "data_acordare "
                    "FROM concedii_medicale WHERE salariat_id=%s AND serie_initiala=%s AND numar_initial=%s "
                    "ORDER BY data_inceput NULLS FIRST, id",
                    (salariat_id, serie_ini, numar_ini))
        _ep_existente = cur.fetchall()
    zile_episod = sum(int(r[4] or 0) for r in _ep_existente) + zile_cm
    # [validare_note 06.10.2026] zilele angajatorului se socotesc pe EPISOD (Norme OUG 158/2005 art.35 alin.(1), art.36):
    # fiecare certificat primește cota rămasă după cele dinaintea lui; `_ang_episod` le recalculează în ordinea datelor.
    def _ang_episod():
        """{id_certificat: zile_ang_deja} pentru certificatele existente + totalul de după ele (pentru cel nou)."""
        out, deja = {}, 0
        for (_cid, _an, _lu, _cod2, _zile2, _mz2, _di2, _eini2, _dac2) in _ep_existente:
            out[_cid] = deja
            if str(_cod2).zfill(2) == "10":
                continue
            _r = _s.calcul_cm(_dec_pos(_mz2), 1, int(_zile2 or 0), cod=str(_cod2).zfill(2), zile_episod=zile_episod,
                              prima_zi_din_episod=bool(_eini2), la_data=_di2, data_episod_initial=data_ini,
                              data_eliberare=_dac2, zile_ang_deja=deja)
            deja += int(_r["zile_ang"])
        return out, deja
    _deja_pe_cert, _deja_nou = _ang_episod() if (este_continuare and _ep_existente) else ({}, 0)

    # LOCK perioada confirmata (decizie Costin): un certificat de continuare care ar recalcula certificate
    # din perioade DEJA CONFIRMATE (D112 depus) e REFUZAT cu INSTRUCTIUNE (ce/unde/de ce/cat), nu un "nu" opac.
    if este_continuare and _ep_existente:
        from core import perioada as _per
        _blocate, _delta = set(), Decimal("0")
        for (_cid, _an, _lu, _cod2, _zile2, _mz2, _di2, _eini2, _dac2) in _ep_existente:
            if _per.e_confirmat(conn, "", _an, _lu, "d112").get("confirmat"):
                if str(_cod2).zfill(2) != "10":
                    _rc = _s.calcul_cm(_dec_pos(_mz2), 1, int(_zile2 or 0), cod=str(_cod2).zfill(2),
                                       zile_episod=zile_episod, prima_zi_din_episod=bool(_eini2),
                                       la_data=_di2, data_episod_initial=data_ini, data_eliberare=_dac2,
                                       zile_ang_deja=_deja_pe_cert.get(_cid, 0))
                    with conn.cursor() as cur:
                        cur.execute("SELECT indemnizatie FROM concedii_medicale WHERE id=%s", (_cid,))
                        _bv = cur.fetchone()[0] or 0
                    _delta += (_rc["brut"] - Decimal(str(_bv or 0)))
                _blocate.add("%02d/%d" % (_lu, _an))
        if _blocate:
            _fn = "firma curentă"
            with conn.cursor() as cur:
                cur.execute("SELECT nume FROM firma_profil LIMIT 1")
                _fr = cur.fetchone()
            if _fr and _fr[0]:  # firma_profil e in template (exista mereu); 0 randuri -> fallback
                _fn = _fr[0]
            _ll = ", ".join(sorted(_blocate))
            raise ValueError(
                "Nu se poate adăuga certificatul de continuare: recalculul episodului ar modifica certificate din "
                "perioade deja confirmate la %s (luna %s). Indemnizația se calculează pe episodul întreg "
                "(OUG 158/2005 art.17(1)): cu acest certificat episodul are %s, deci procentul certificatelor "
                "anterioare crește de la 55%%/65%% la 75%% (+%s lei). Deschide perioada %s (anulează confirmarea D112) sau "
                "depune D112 rectificativă pe luna %s, apoi adaugă din nou certificatul."
                % (_fn, _ll, _cate(zile_episod, "zi", "zile"), _delta.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), _ll, _ll))

    if cod == "10":  # [cod10] art. 19 OUG 158/2005: baza - venit realizat, plafon 25% din baza; integral FNUASS (art. 12)
        vr = date.get("venit_realizat")
        if vr in (None, ""):
            raise ValueError("La codul 10 completează venitul brut realizat în noua situatie.")
        mz = (Decimal(str(ven6)) / Decimal(zile6)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        baza_per = (mz * Decimal(zile_cm)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        brut10 = _s.calcul_cm_cod10(baza_per, vr, la_data=la_data)
        calc = {"brut": brut10, "media_zilnica": mz, "procent": Decimal("0.25"), "diminuare": False,
                "zile_platite": zile_cm, "zile_ang": 0, "zile_fnuass": zile_cm,
                "brut_ang": Decimal("0"), "brut_fnuass": brut10}
    else:
        calc = _s.calcul_cm(ven6, zile6, zile_cm, cod=cod, spitalizare=spitalizare,
                            la_data=la_data, procent_accident=pacc, venituri_lunare=venituri_lunare,
                            zile_episod=zile_episod, prima_zi_din_episod=prima_zi,
                            zile_ang_deja=_deja_nou, data_episod_initial=data_ini,
                            data_eliberare=data_elib, program_national=program_national)
    taxe = _s.taxe_cm(calc["brut"], cod=cod, la_data=la_data)

    # [R189, etapa 2 lotul H, 15.09.2026] LOCUL PRESCRIERII: `int(...)` pe o valoare venita de la om
    # ridica mesajul Python, si acela ajungea la utilizator („invalid literal for int() with base 10").
    # Campul pleaca in D112 ca `D_10` (`d112.py:522`), deci trebuie sa fie numeric. NU se enumera
    # codurile — structura ANAF nu s-a verificat la sursa in tura in care s-a gasit defectul —, dar se
    # numeste campul, campul-tinta si de unde se ia valoarea.
    _loc = date.get("loc_prescriere")
    if _loc not in (None, ""):
        try:
            int(_loc)
        except (TypeError, ValueError):
            raise ValueError(
                "Locul prescrierii trebuie să fie codul numeric de pe certificatul medical, nu un "
                "text (primit: %r). El pleacă în D112, iar declarația nu acceptă acolo "
                "decât un număr. Ia-l din certificat, de la rubrica locului prescrierii."
                % (_loc,))

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile, indemnizatie, "
            "baza, media_zilnica, procent, diminuare, zile_platite, zile_ang, zile_fnuass, "
            "brut_ang, brut_fnuass, cass, impozit, cas, net, serie, numar, data_acordare, "
            "data_inceput, data_sfarsit, loc_prescriere, diagnostic, cod_urgenta, cnp_ingrijit, "
            "serie_initiala, numar_initial, este_continuare, data_certificat_initial, venituri_6_luni, zile_6_luni, program_national) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "RETURNING id",
            (salariat_id, date.get("an"), date.get("luna"), cod, zile_cm, calc["brut"],
             calc.get("baza", ven6), calc["media_zilnica"], calc["procent"], bool(calc["diminuare"]),
             calc["zile_platite"], calc["zile_ang"], calc["zile_fnuass"],
             calc["brut_ang"], calc["brut_fnuass"], taxe["cass"], taxe["impozit"],
             taxe["cas"], taxe["net"], date.get("serie"), date.get("numar"),
             date.get("data_acordare"), date.get("data_inceput"), date.get("data_sfarsit"),
             int(date.get("loc_prescriere") or 1), date.get("diagnostic"), cod_urgenta, cnp_ingrijit,
             serie_ini, numar_ini, este_continuare, data_ini, _dec_pos(ven6), int(zile6), program_national))
        cm_id = cur.fetchone()[0]

    # [CM-episod] RECALCUL RETROACTIV: episodul a crescut -> re-aplica procentul (55/65->75), diminuarea
    # (o data/episod) si portia angajator (o data/episod) pe certificatele ANTERIOARE neconfirmate.
    if este_continuare and _ep_existente:
        for (_cid, _an, _lu, _cod2, _zile2, _mz2, _di2, _eini2, _dac2) in _ep_existente:
            if str(_cod2).zfill(2) == "10":
                continue
            _rc = _s.calcul_cm(_dec_pos(_mz2), 1, int(_zile2 or 0), cod=str(_cod2).zfill(2),
                               zile_episod=zile_episod, prima_zi_din_episod=bool(_eini2),
                               la_data=_di2, data_episod_initial=data_ini, data_eliberare=_dac2,
                               zile_ang_deja=_deja_pe_cert.get(_cid, 0))
            _rt = _s.taxe_cm(_rc["brut"], cod=str(_cod2).zfill(2), la_data=_di2)
            with conn.cursor() as cur:
                cur.execute("UPDATE concedii_medicale SET indemnizatie=%s, procent=%s, diminuare=%s, "
                            "zile_platite=%s, zile_ang=%s, zile_fnuass=%s, brut_ang=%s, brut_fnuass=%s, "
                            "cass=%s, impozit=%s, cas=%s, net=%s WHERE id=%s",
                            (_rc["brut"], _rc["procent"], bool(_rc["diminuare"]), _rc["zile_platite"],
                             _rc["zile_ang"], _rc["zile_fnuass"], _rc["brut_ang"], _rc["brut_fnuass"],
                             _rt["cass"], _rt["impozit"], _rt["cas"], _rt["net"], _cid))

    return {"ok": True, "id": cm_id, "calcul": {**calc, **taxe}, "zile_episod": zile_episod,
            "recalculat_anterioare": (len(_ep_existente) if este_continuare else 0)}


def sterge_concediu(conn, salariat_id, cm_id):
    """Sterge un concediu medical (verifica apartenenta la salariat)."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM concedii_medicale WHERE id=%s AND salariat_id=%s RETURNING id",
                    (cm_id, salariat_id))
        r = cur.fetchone()
    return {"ok": r is not None}
