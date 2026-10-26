"""
core/pontaj.py — F135: pontajul lunar al salariatului. Calcul PUR + strat DB.

[lotul 13, deficiența 671, comanda Costin 13.1] „Pontajul, statul, tichetele și D112 pornesc din aceleași zile; ce e «informativ» și
ce blochează se decide o dată și se spune la fel peste tot.” Până la 25.10.2026 pontajul nu știa de certificatele medicale (Ionescu
Vasile, 10/2026: certificat 13–15.10, iar în pontaj 13, 14, 15 „prezent”) și nici de suspendări, iar două texte se contraziceau
(„calculele din aval se blochează până la confirmare” / „evidență informativă, nu schimbă statul”).

ZILELE LUNII, O SINGURĂ SURSĂ (`zilele_lunii`): fiecare zi a salariatului primește starea din locul care o stabilește:
  1. weekendul și sărbătorile legale — `scadente.e_zi_lucratoare` (același calendar ca proratarea CM, OUG 158/2005 art.10);
  2. zilele dinainte de angajare / de după încetare — fișa salariatului (contractul nu e în vigoare);
  3. concediul medical — CERTIFICATELE (`concedii_medicale`, intervalul de pe certificat); nu se marchează de mână;
  4. concediul fără plată și suspendarea — „Suspendare / CFP” (`suspendari_contract`); nu se marchează de mână;
  5. restul — ce a marcat contabilul în pontaj (concediu de odihnă, delegație, absențe, învoire), altfel „prezent”.
Statul de plată (`stat_plata_api`), D112 (`d112.pull`) și tichetele (`zile_fara_tichet`) citesc zilele de aici.

CE SCHIMBĂ CE (regula unică, `REGULA_PONTAJ`, afișată la fel în pontaj și în statul de plată). DECIZIA (varianta cea mai sigură
pentru contabil, păstrând decizia din 02.08.2026 — DECIZII „#1/#3”: pontajul neconfirmat nu mai blochează tot statul, care ducea la
blocaj): salariul se calculează din contract, certificatele medicale și suspendări — zile care vin din acte, nu din pontaj, deci
statul nu așteaptă confirmarea; zilele marcate în pontaj schimbă numai tichetele de masă (HG 1045/2018 art.10 alin.(3): tichetul se
acordă pe zilele efectiv lucrate), iar tichetele se calculează numai după confirmarea pontajului lunii (statul le arată blocate,
D112 cu tichete se refuză). ALTERNATIVA RESPINSĂ: statul, nota și D112 blocate toate până la confirmarea pontajului — ar schimba o
decizie luată (02.08.2026) și ar opri D112 la firmele fără tichete pentru o confirmare care nu schimbă nicio cifră a lor.
"""
import calendar
from datetime import date, timedelta
from core.scadente import e_zi_lucratoare
from core.migrare_pontaj import STARI
from core.common import cate as _cate

#: Stările pe care le marchează contabilul (fără „prezent”, care e implicit). Concediul medical NU e aici: vine din certificate.
STARI_MARCATE = ("concediu_odihna", "delegatie", "absent_motivat", "absent_nemotivat", "invoire")
ETICHETE = {"prezent": "prezent", "concediu_odihna": "concediu de odihnă", "delegatie": "delegație",
            "absent_motivat": "absent motivat", "absent_nemotivat": "absent nemotivat", "invoire": "învoire",
            "concediu_medical": "concediu medical", "cfp": "concediu fără plată", "suspendare": "contract suspendat",
            "nelucratoare": "zi nelucrătoare", "inainte_angajare": "înainte de angajare", "dupa_incetare": "după încetare"}

#: [671] Regula unică: ce schimbă pontajul și ce așteaptă confirmarea lui. Aceeași frază în pontaj, în statul de plată și în răspunsul
#: serverului (`grila`) — ecranele o citesc de aici, nu o rescriu.
REGULA_PONTAJ = ("Salariul se calculează din contract, din certificatele medicale și din suspendări — zilele lor apar aici "
                 "marcate. Zilele pe care le marchezi tu (concediu de odihnă, delegație, absențe, învoiri) schimbă numai "
                 "tichetele de masă, care se calculează după ce confirmi pontajul lunii.")

MESAJ_CM_MANUAL = ("Concediul medical nu se marchează în pontaj: se trece din certificat (butonul „Concediu medical” al "
                   "salariatului), iar zilele lui apar aici singure.")


def _zi(x):
    return x if isinstance(x, date) else date.fromisoformat(str(x)[:10])


def _p(schema):
    return ('"%s".' % str(schema).strip('"')) if schema else ""


def grila_pura(an, luna, data_angajare, exceptii, data_incetare=None, certificate=(), suspendari=()):
    """PURĂ. Zilele lunii cu starea fiecăreia (vezi antetul modulului pentru ordinea surselor).

    exceptii = {date: stare} (pontajul); certificate = [{data_inceput, data_sfarsit, serie, numar, zile, an, luna}];
    suspendari = [(inceput, sfarsit, tip)]. Intoarce {zile, rezumat, data_angajare, certificate, avertismente, regula}."""
    zile, rezumat = [], {"prezent": 0, "cfp": 0, "suspendare": 0, "cm_fara_certificat": 0}
    for s in STARI:
        rezumat[s] = 0
    certs = [dict(c, _a=_zi(c["data_inceput"]), _b=_zi(c["data_sfarsit"])) for c in certificate or ()
             if c.get("data_inceput") and c.get("data_sfarsit")]
    avert = []
    for z in range(1, calendar.monthrange(an, luna)[1] + 1):
        d = date(an, luna, z)
        lucr = e_zi_lucratoare(d)
        in_activ = ((data_angajare is None or d >= _zi(data_angajare))
                    and (data_incetare is None or d <= _zi(data_incetare)))
        sursa, editabil, motiv = None, False, ""
        cert = next((c for c in certs if c["_a"] <= d <= c["_b"]), None)
        susp = next((x for x in suspendari or () if _zi(x[0]) <= d <= _zi(x[1])), None)
        if not lucr:
            stare, motiv = "nelucratoare", "Weekend sau sărbătoare legală: nu se pontează."
        elif not in_activ:
            stare = "inainte_angajare" if (data_angajare is not None and d < _zi(data_angajare)) else "dupa_incetare"
            motiv = "Contractul nu era în vigoare în ziua asta."
        elif cert is not None:
            stare, sursa = "concediu_medical", "certificat"
            motiv = ("Concediu medical din certificatul %s %s — se schimbă din certificat."
                     % (cert.get("serie") or "", cert.get("numar") or "")).replace("  ", " ")
        elif susp is not None:
            stare, sursa = (susp[2] if susp[2] in ("cfp", "suspendare") else "suspendare"), "suspendare"
            motiv = "%s — se schimbă din „Suspendare / CFP”." % ETICHETE.get(stare, stare).capitalize()
        else:
            stare = exceptii.get(d) or "prezent"
            sursa, editabil = ("pontaj" if stare != "prezent" else None), True
            if stare == "concediu_medical":   # marcat de mână înainte de 671: fără certificat
                rezumat["cm_fara_certificat"] += 1
                motiv = "Marcată concediu medical fără certificat: adaugă certificatul sau marchează ziua altfel."
        zile.append({"zi": d.isoformat(), "zi_nr": z, "zi_saptamana": d.weekday(), "lucratoare": lucr,
                     "in_activitate": in_activ, "stare": stare, "eticheta": ETICHETE.get(stare, stare),
                     "sursa": sursa, "editabil": editabil, "motiv": motiv})
        if stare in rezumat and not (stare == "concediu_medical" and sursa != "certificat"):
            rezumat[stare] += 1
    n_fara = rezumat["cm_fara_certificat"]
    if n_fara:
        avert.append("Zile marcate concediu medical fără certificat: %s. Tichetele nu se dau pe ele, dar salariul le plătește — "
                     "adaugă certificatul (butonul „Concediu medical”) sau marchează-le altfel." % _cate(n_fara, "zi", "zile"))
    zile_cert_luna = sum(int(c.get("zile") or 0) for c in certs if c.get("an") in (None, an) and c.get("luna") in (None, luna))
    if certs and zile_cert_luna and zile_cert_luna != rezumat["concediu_medical"]:
        avert.append("Certificatele lunii au %s de concediu medical, iar calendarul arată %s: statul de plată folosește cifra de "
                     "pe certificat." % (_cate(zile_cert_luna, "zi lucrătoare", "zile lucrătoare"),
                                          _cate(rezumat["concediu_medical"], "zi", "zile")))
    return {"an": an, "luna": luna, "zile": zile, "rezumat": rezumat,
            "data_angajare": data_angajare.isoformat() if isinstance(data_angajare, date) else data_angajare,
            "certificate": [{"serie": c.get("serie"), "numar": c.get("numar"), "data_inceput": c["_a"].isoformat(),
                             "data_sfarsit": c["_b"].isoformat(), "zile": int(c.get("zile") or 0)} for c in certs],
            "avertismente": avert, "regula": REGULA_PONTAJ}


def zilele_lunii(conn, schema, salariat_id, an, luna):
    """Zilele lunii salariatului din cele trei surse (fișa, certificatele, suspendările) plus pontajul. None = salariat inexistent."""
    prima = date(an, luna, 1)
    ultima = date(an, luna, calendar.monthrange(an, luna)[1])
    urm = ultima + timedelta(days=1)
    p = _p(schema)
    with conn.cursor() as cur:
        cur.execute(f"SELECT data_angajare, data_incetare FROM {p}salariati WHERE id = %s", (salariat_id,))
        r = cur.fetchone()
        if r is None:
            return None
        data_ang, data_inc = (r["data_angajare"], r["data_incetare"]) if isinstance(r, dict) else (r[0], r[1])
        cur.execute(f"SELECT zi, stare FROM {p}pontaj WHERE salariat_id = %s AND zi >= %s AND zi < %s",
                    (salariat_id, prima, urm))
        exceptii = {}
        for row in cur.fetchall():
            zi, st = (row["zi"], row["stare"]) if isinstance(row, dict) else (row[0], row[1])
            exceptii[zi] = st
        cur.execute(f"SELECT data_inceput, data_sfarsit, serie, numar, zile, an, luna FROM {p}concedii_medicale "
                    "WHERE salariat_id = %s AND data_inceput IS NOT NULL AND data_sfarsit IS NOT NULL "
                    "AND data_inceput <= %s AND data_sfarsit >= %s ORDER BY data_inceput", (salariat_id, ultima, prima))
        cols = ("data_inceput", "data_sfarsit", "serie", "numar", "zile", "an", "luna")
        certificate = [dict(row) if isinstance(row, dict) else dict(zip(cols, row)) for row in cur.fetchall()]
        cur.execute(f"SELECT data_inceput, data_sfarsit, tip FROM {p}suspendari_contract WHERE salariat_id = %s "
                    "AND data_inceput <= %s AND data_sfarsit >= %s ORDER BY data_inceput", (salariat_id, ultima, prima))
        susp = [((row["data_inceput"], row["data_sfarsit"], row["tip"]) if isinstance(row, dict) else tuple(row))
                for row in cur.fetchall()]
    return grila_pura(an, luna, data_ang, exceptii, data_incetare=data_inc, certificate=certificate, suspendari=susp)


def grila(conn, schema, salariat_id, an, luna):
    """Grila pontajului (ecranul Pontaj): zilele lunii din `zilele_lunii`."""
    return zilele_lunii(conn, schema, salariat_id, an, luna)


def seteaza(conn, schema, salariat_id, zi, stare, tenant_id=None):
    """Set/clear o zi. stare='prezent' (sau gol) -> sterge randul (prezenta = implicit).
    Altfel trebuie sa fie in STARI_MARCATE. Intoarce {ok, mesaj?}.

    Reversibilitate (DESIGN_SYSTEM cap.23): o modificare DE-CONFIRMA automat luna (pontaj) - calculele din
    aval re-blocheaza pana la re-confirmare. DUPA depunerea D112 pe luna (tenant_id dat), editarea se
    BLOCHEAZA (fapt declarat la ANAF) -> corectie prin rectificativa.
    [671] Ziua de concediu medical (certificat) sau de suspendare nu se marchează de mână: se schimbă din actul ei."""
    from core import perioada as _per
    if stare == "concediu_medical":
        return {"ok": False, "mesaj": MESAJ_CM_MANUAL}
    if stare and stare != "prezent" and stare not in STARI_MARCATE:
        return {"ok": False, "mesaj": "Starea „%s” nu se poate pune în pontaj." % stare}
    d = _zi(zi)
    an, luna = d.year, d.month
    if tenant_id is not None:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM public.declaratii_depuse WHERE tenant_id = %s AND an = %s AND luna = %s "
                        "AND tip = 'd112' LIMIT 1", (tenant_id, an, luna))
            if cur.fetchone():
                return {"ok": False, "mesaj": "Pontajul lunii %02d/%d nu se poate modifica: D112 e deja depusă "
                        "la ANAF. Corectează prin rectificativă (nu prin editare liberă)." % (luna, an)}
    g = zilele_lunii(conn, schema, salariat_id, an, luna)
    if g is None:
        return {"ok": False, "mesaj": "Salariatul nu există."}
    ziua = next((x for x in g["zile"] if x["zi"] == d.isoformat()), None)
    if ziua is not None and not ziua["editabil"]:
        return {"ok": False, "mesaj": "Ziua %s nu se marchează în pontaj. %s" % (d.strftime("%d.%m.%Y"), ziua["motiv"])}
    if not stare or stare == "prezent":
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {_p(schema)}pontaj WHERE salariat_id = %s AND zi = %s", (salariat_id, d))
    else:
        with conn.cursor() as cur:
            # upsert-ok: set pontaj pe (salariat,zi) - re-marcarea aceleiasi zile rescrie intentionat
            cur.execute(f"INSERT INTO {_p(schema)}pontaj (salariat_id, zi, stare) VALUES (%s, %s, %s) "
                        "ON CONFLICT (salariat_id, zi) DO UPDATE SET stare = EXCLUDED.stare",
                        (salariat_id, d, stare))
    _per.deconfirma(conn, schema, an, luna, "pontaj")   # modificarea invalideaza confirmarea
    return {"ok": True}


# HG 1045/2018 art.10 alin.(3): tichetul de masa se acorda pe zile EFECTIV lucrate. Zilele de concediu de
# odihna, delegatie/detasare, absente (motivate/nemotivate) si invoire NU dau drept la tichet. Concediul MEDICAL din
# certificate se scade separat (statul il scade din cifra certificatului, nu se dubleaza aici); cel marcat de mana, fara
# certificat (date de dinainte de 671), nu da nici el tichet.
_STARI_FARA_TICHET = ("concediu_odihna", "delegatie", "absent_motivat", "absent_nemotivat", "invoire")


def fara_tichet(g):
    """PURĂ. Zilele grilei (`zilele_lunii`) care NU dau drept la tichet de masă, peste cele scăzute separat (CM din certificate,
    suspendări — statul le scade din actele lor)."""
    if g is None:
        return 0
    return sum(g["rezumat"].get(st, 0) for st in _STARI_FARA_TICHET) + g["rezumat"].get("cm_fara_certificat", 0)


def zile_fara_tichet(conn, schema, salariat_id, an, luna):
    """Zilele LUCRATOARE din pontaj cu o stare care NU da drept la tichet de masa (CO/delegatie/absente/
    invoire), pentru corectia numarului de tichete (D2, HG 1045/2018 art.10(3)). [671] Din `zilele_lunii`: o zi acoperita
    de un certificat medical sau de o suspendare nu se mai numara a doua oara (statul le scade deja). Firma FARA pontaj -> 0."""
    return fara_tichet(zilele_lunii(conn, schema, salariat_id, an, luna))
