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

REGULI = "2026.1"
MODUL = "salariati_api"

_CNP = re.compile(r"^\d{13}$")
_NORME = ("intreaga", "partiala")
# [tranzitie 29.07.2026] salariu_brut nu mai e citit de calculul fiscal (d112, stat_plata); acela
# trece prin salariu_istoric.salariu_la(). salariu_brut se retrage complet din tabel in 2b.
# NU adauga citiri fiscale noi pe salariati.salariu_brut.
_CAMPURI_API = ("cnp", "nume", "prenume", "data_angajare", "tip_norma", "ore_zi",
                "persoane_intretinere", "judet_casa", "data_incetare",  # [2b] salariu_brut -> salariu_istoric
                "scutit_contrib_minim", "motiv_exceptare", "cor",
                "tichet_masa_valoare",  # [F133]
                "iban")  # [F134] cont beneficiar pt plata pe card


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
        return
    from core import cor_api
    if not cor_api.exista(conn, cod):
        raise ValueError("cod COR inexistent in nomenclator: %s (alege din lista)" % cod)


def valideaza_salariat(date):
    """Verifică datele unui salariat. Întoarce listă erori (gol = ok)."""
    erori = []
    if not (date.get("nume") and str(date["nume"]).strip()):
        erori.append("nume obligatoriu")
    cnp = date.get("cnp")
    if cnp and not _CNP.match(str(cnp)):
        erori.append("CNP invalid: aștept 13 cifre")
    brut = date.get("salariu_brut")
    if brut is not None:
        try:
            if float(brut) < 0:
                erori.append("salariu_brut nu poate fi negativ")
        except (TypeError, ValueError):
            erori.append("salariu_brut invalid")
    tn = date.get("tip_norma")
    if tn is not None and tn not in _NORME:
        erori.append("tip_norma trebuie 'intreaga' sau 'partiala'")
    # [F133] valoarea tichetului de masa: 0..plafon legal (nu poate depasi maximul legal/tichet)
    tmv = date.get("tichet_masa_valoare")
    if tmv is not None:
        try:
            v = float(tmv)
            if v < 0:
                erori.append("tichet_masa_valoare nu poate fi negativ")
            else:
                from core.common import cota
                plafon = float(cota("tichet_masa_plafon")[0])
                if v > plafon:
                    erori.append(f"tichet_masa_valoare depaseste plafonul legal ({plafon:g} lei/tichet)")
        except (TypeError, ValueError):
            erori.append("tichet_masa_valoare invalid")
    # [F134] IBAN optional; daca e completat trebuie sa fie IBAN romanesc valid (mod-97)
    iban = date.get("iban")
    if iban is not None and str(iban).strip():
        if not iban_valid(iban):
            erori.append("IBAN invalid (astept IBAN romanesc: RO + 22 caractere, cifra de control corecta)")
    # data_incetare (optional) >= data_angajare - contract activ o perioada coerenta (backstop: CHECK in DB)
    di, da = date.get("data_incetare"), date.get("data_angajare")
    if di is not None and str(di).strip() and da is not None and str(da).strip():
        try:
            from datetime import date as _date
            if _date.fromisoformat(str(di)[:10]) < _date.fromisoformat(str(da)[:10]):
                erori.append("data incetarii nu poate fi inainte de data angajarii")
        except (ValueError, TypeError):
            erori.append("data incetarii sau angajarii invalida")
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
        cond = " WHERE data_incetare IS NULL OR data_incetare >= CURRENT_DATE"
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
def creeaza_salariat(conn, **date):
    """Inserează un salariat (după validare). Întoarce {ok, salariat_id} sau ridică
    ValueError cu erorile."""
    erori = valideaza_salariat(date)
    if erori:
        raise ValueError("; ".join(erori))
    _verifica_cor(conn, date.get("cor"))  # [F137] codul COR (daca e dat) trebuie sa existe in nomenclator
    campuri_api = {k: date[k] for k in _CAMPURI_API if k in date and date[k] is not None}
    campuri_db = _api_spre_db(campuri_api)
    cols = list(campuri_db.keys())
    vals = list(campuri_db.values())
    ph = ", ".join(["%s"] * len(cols))
    from core import salariu_istoric as _si
    from datetime import date as _dm
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (%s) VALUES (%s) RETURNING id"
            % (", ".join(cols), ph), vals)
        sid = cur.fetchone()[0]
        # [PASUL 2b] salariul de baza trece pe salariu_istoric (SURSA UNICA), nu pe salariati.salariu_brut
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
            "scutit_contrib_minim, motiv_exceptare, cor, tichet_masa_valoare, iban "
            "FROM salariati WHERE id = %s", (salariat_id,))
        r = cur.fetchone()
        if r:
            r = dict(r)
            r["salariu_brut"] = _si.salariu_la(cur, None, salariat_id, _dm.today())  # [2b] curent din istoric
    return _db_spre_api(r) if r else None


# ============================================================
#  EDITARE (doar câmpurile trimise, validate)
# ============================================================
def actualizeaza_salariat(conn, salariat_id, **date):
    """Editează câmpurile date (validate). salariu_brut e o SCHIMBARE DE SALARIU -> intrare NOUĂ în
    salariu_istoric la valabil_din (implicit azi), nu UPDATE pe salariati (PASUL 2b, sursă unică)."""
    from core import salariu_istoric as _si
    from datetime import date as _dm
    campuri_api = {k: v for k, v in date.items() if k in _CAMPURI_API and v is not None}
    _sb = date.get("salariu_brut")
    if not campuri_api and _sb is None:
        return {"ok": True, "neschimbat": True}
    erori = valideaza_salariat({**campuri_api, "salariu_brut": _sb,
                                "data_angajare": date.get("data_angajare"),
                                "data_incetare": date.get("data_incetare"),
                                "nume": campuri_api.get("nume", "x")})
    erori = [e for e in erori if e != "nume obligatoriu"]
    if erori:
        raise ValueError("; ".join(erori))
    with conn.cursor() as cur:
        if campuri_api:
            if "cor" in campuri_api:
                _verifica_cor(conn, campuri_api.get("cor"))
            campuri = _api_spre_db(campuri_api)
            seturi = ", ".join("%s = %%s" % k for k in campuri)
            cur.execute("UPDATE salariati SET %s WHERE id = %%s" % seturi,
                        list(campuri.values()) + [salariat_id])
        if _sb is not None:
            _si.seteaza(cur, salariat_id, _sb, date.get("valabil_din") or _dm.today().isoformat())
    return {"ok": True}


# ============================================================
#  ȘTERGERE — protejată (concedii medicale legate)
# ============================================================
def _refuz_sterge():
    return {"ok": False, "cod": "ARE_LUNI_DECLARATE",
            "mesaj": ("Salariatul are luni declarate. Nu se sterge - completeaza data incetarii "
                      "contractului, altfel se pierde istoricul care sustine declaratiile deja depuse.")}


def sterge_salariat(conn, salariat_id):
    """Hard-delete DOAR pentru greseala de introducere: salariat fara nicio luna declarata. La PLECARE
    NU se sterge - se completeaza data_incetare (istoricul sustine declaratiile depuse). Refuza daca are
    concedii medicale, apare in stat de plata (state_plata) sau tenantul are vreun D112 depus pentru o
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
        cur.execute("SELECT count(*) FROM state_plata WHERE salariat_id = %s", (salariat_id,))
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


def salveaza_concediu(conn, salariat_id, date):
    """Calculeaza indemnizatia CM (calcul_cm + taxe_cm) si o salveaza in concedii_medicale.
    date: serie, numar, cod, data_acordare, data_inceput, data_sfarsit, loc_prescriere,
          diagnostic, spitalizare, zile_cm (lucratoare), venituri_6_luni, zile_6_luni,
          an, luna, procent_accident (optional). Intoarce randul salvat + breakdown calcul."""
    from core import salarizare as _s
    from decimal import Decimal
    cod = str(date.get("cod") or "01").zfill(2)
    zile_cm = int(date.get("zile_cm") or 0)
    ven6 = date.get("venituri_6_luni") or 0
    zile6 = int(date.get("zile_6_luni") or 1)
    spitalizare = bool(date.get("spitalizare"))
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
            raise ValueError("La codul 06 (urgenta medico-chirurgicala) completeaza codul de urgenta "
                             "(1..%d, nomenclator HG 423/2020) - D112 il cere obligatoriu (campul D_11)." % _maxu)
    import datetime as _dtmod
    _di = date.get("data_inceput") or None
    if isinstance(_di, str) and _di:
        try: la_data = _dtmod.date.fromisoformat(_di[:10])
        except ValueError: la_data = None
    else:
        la_data = _di

    # Validare: baza de calcul trebuie sa fie reala (altfel brut 0 dar net pozitiv = imposibil)
    if _dec_pos(ven6) <= 0:
        raise ValueError("Veniturile brute pe 6 luni lipsesc sau sunt 0 - completeaza baza de calcul din statele de plata.")
    if zile6 <= 0:
        raise ValueError("Zilele lucratoare din cele 6 luni lipsesc sau sunt 0.")
    if zile_cm <= 0:
        raise ValueError("Zilele lucratoare CM trebuie sa fie cel putin 1.")
    if cod == "10":  # [cod10] art. 19 OUG 158/2005: baza - venit realizat, plafon 25% din baza; integral FNUASS (art. 12)
        from decimal import Decimal as _D
        vr = date.get("venit_realizat")
        if vr in (None, ""):
            raise ValueError("La codul 10 completeaza venitul brut realizat in noua situatie.")
        mz = (_D(str(ven6)) / _D(zile6)).quantize(_D("0.01"))
        baza_per = (mz * _D(zile_cm)).quantize(_D("0.01"))
        brut10 = _s.calcul_cm_cod10(baza_per, vr, la_data=la_data)
        calc = {"brut": brut10, "media_zilnica": mz, "procent": _D("0.25"), "diminuare": False,
                "zile_platite": zile_cm, "zile_ang": 0, "zile_fnuass": zile_cm,
                "brut_ang": _D("0"), "brut_fnuass": brut10}
    else:
        calc = _s.calcul_cm(ven6, zile6, zile_cm, cod=cod, spitalizare=spitalizare,
                            la_data=la_data, procent_accident=pacc)
    taxe = _s.taxe_cm(calc["brut"], cod=cod, la_data=la_data)

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile, indemnizatie, "
            "baza, media_zilnica, procent, diminuare, zile_platite, zile_ang, zile_fnuass, "
            "brut_ang, brut_fnuass, cass, impozit, cas, net, serie, numar, data_acordare, "
            "data_inceput, data_sfarsit, loc_prescriere, diagnostic, cod_urgenta) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "RETURNING id",
            (salariat_id, date.get("an"), date.get("luna"), cod, zile_cm, calc["brut"],
             ven6, calc["media_zilnica"], calc["procent"], bool(calc["diminuare"]),
             calc["zile_platite"], calc["zile_ang"], calc["zile_fnuass"],
             calc["brut_ang"], calc["brut_fnuass"], taxe["cass"], taxe["impozit"],
             taxe["cas"], taxe["net"], date.get("serie"), date.get("numar"),
             date.get("data_acordare"), date.get("data_inceput"), date.get("data_sfarsit"),
             int(date.get("loc_prescriere") or 1), date.get("diagnostic"), cod_urgenta))
        cm_id = cur.fetchone()[0]
    return {"ok": True, "id": cm_id, "calcul": {**calc, **taxe}}


def sterge_concediu(conn, salariat_id, cm_id):
    """Sterge un concediu medical (verifica apartenenta la salariat)."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM concedii_medicale WHERE id=%s AND salariat_id=%s RETURNING id",
                    (cm_id, salariat_id))
        r = cur.fetchone()
    return {"ok": r is not None}
