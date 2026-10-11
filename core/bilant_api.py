# -*- coding: utf-8 -*-
"""S1005 - strat DB: solduri finale + rulaje din note VALIDATE, apoi core.bilant."""
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import bilant as _b
from core.common import cere_coloane_cursor  # [garda coloane 27.07.2026]
from core.pdf_util import data_ro
_COLOANE_PROFIL = ("nume", "cui", "adresa", "caen")   # minimul citit de aici

def data_soldurilor(cur, schema):
    """[deficiența 221, 10.10.2026] Data LA CARE sunt soldurile de preluare (`solduri_initiale`), sau None dacă evidența firmei e
    întreagă în iConta.eu (nicio preluare). `data_referinta` când e scrisă; altfel ziua dinaintea lunii preluării (`luna_preluare` —
    decizia Costin 08.10.2026 §6 pct.4: evidența în iConta.eu începe cu luna preluării, deci soldurile sunt „la” ziua de dinainte).
    Aceeași regulă ca luna preluării din Date firmă și din Control fiscal, nu o a doua."""
    import datetime
    from core import luna_preluare as _lp
    cur.execute(f"""SELECT (SELECT luna_preluare FROM {schema}.firma_profil WHERE id = 1) AS salvata,
                           (SELECT creat_la FROM public.tenants WHERE schema_name = %s) AS creat_la,
                           (SELECT max(data_referinta) FROM {schema}.solduri_initiale) AS data_solduri,
                           (SELECT min(data) FROM {schema}.inregistrari) AS prima_nota,
                           (SELECT count(*) FROM {schema}.solduri_initiale) AS n_solduri""", (schema,))
    r = dict(cur.fetchone())
    if r["data_solduri"]:
        return r["data_solduri"]
    c = r["creat_la"]
    ef = _lp.efectiva(r["salvata"], c.date() if hasattr(c, "date") else c, None, r["prima_nota"])
    if not ef:
        return None
    return datetime.date(ef[0], ef[1], 1) - datetime.timedelta(days=1)


def sold_la(cur, schema, zi, ref="calculeaza"):
    """Soldurile conturilor LA `zi` (inclusiv): soldurile de preluare + mișcările validate de după data lor, până la `zi`.
    None dacă `zi` e înainte de data soldurilor de preluare: aplicația nu știe ce era atunci (nu se fabrică — OMFP 1802/2014 pct.130 cere
    valoarea REALĂ a exercițiului precedent, nu o copie). [deficiența 221: coloana „An precedent” era soldul de preluare oricare ar fi
    anul, deci pe anul preluării ieșea identică cu „An curent”.]"""
    if ref == "calculeaza":
        ref = data_soldurilor(cur, schema)
    if ref is not None and zi < ref:
        return None
    cur.execute(f"SELECT cont, sold_debitor, sold_creditor FROM {schema}.solduri_initiale")
    net = {}
    for r in cur.fetchall():
        net[r["cont"]] = net.get(r["cont"], Decimal("0")) + Decimal(str(r["sold_debitor"])) - Decimal(str(r["sold_creditor"]))
    cur.execute(f"""
        SELECT l.cont_debit, l.cont_credit, l.suma
        FROM {schema}.inregistrari_linii l
        JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
        WHERE i.status = 'validata' AND i.data <= %s AND (%s::date IS NULL OR i.data > %s::date)""", (zi, ref, ref))
    for r in cur.fetchall():
        s = Decimal(str(r["suma"]))
        net[r["cont_debit"]] = net.get(r["cont_debit"], Decimal("0")) + s
        net[r["cont_credit"]] = net.get(r["cont_credit"], Decimal("0")) - s
    return {c: ((v, Decimal("0")) if v >= 0 else (Decimal("0"), -v)) for c, v in net.items()}


def coloanele_f10(cur, schema, an, av):
    """(f10p, f10c) — bilanțul la 31.12 al anului precedent și la 31.12.an. Coloana curentă necunoscută -> refuz (bilanțul nu se poate
    întocmi pe un an dinaintea preluării); cea precedentă necunoscută -> goală, cu avertismentul care o spune (nu o copie)."""
    import datetime
    ref = data_soldurilor(cur, schema)
    s_c = sold_la(cur, schema, datetime.date(an, 12, 31), ref)
    if s_c is None:
        raise ValueError("Bilanțul pe %d nu se poate întocmi în iConta.eu: evidența firmei începe după soldurile de preluare de la %s, "
                         "deci soldurile de la %s nu sunt în aplicație." % (an, data_ro(ref), data_ro(datetime.date(an, 12, 31))))
    s_p = sold_la(cur, schema, datetime.date(an - 1, 12, 31), ref)
    if s_p is None:
        av.append("Coloana „An precedent” a bilanțului (soldurile de la %s) e necompletată: evidența firmei în iConta.eu începe "
                  "după soldurile de preluare de la %s, deci soldurile anului precedent nu sunt în aplicație. Se completează în "
                  "formularul ANAF — OMFP 1802/2014 pct.130 cere valoarea exercițiului financiar precedent."
                  % (data_ro(datetime.date(an, 1, 1)), data_ro(ref)))
    return (_b.f10_din_balanta(s_p) if s_p is not None else {}), _b.f10_din_balanta(s_c)


def _rulaje_67(cur, schema, an):
    cur.execute(f"""
        SELECT l.cont_debit, l.cont_credit, l.suma
        FROM {schema}.inregistrari_linii l
        JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
        WHERE i.status = 'validata' AND i.data BETWEEN %s AND %s""",
        (f"{an}-01-01", f"{an}-12-31"))
    rl = {}
    for r in cur.fetchall():
        s = Decimal(str(r["suma"]))
        for cont, idx in ((r["cont_debit"], 0), (r["cont_credit"], 1)):
            if str(cont)[:1] in ("6", "7"):
                v = rl.get(cont, [Decimal("0"), Decimal("0")])
                v[idx] += s
                rl[cont] = v
    return {c: (v[0], v[1]) for c, v in rl.items()}

_JUD = {"bucuresti": 40, "alba": 1, "arad": 2, "arges": 3, "bacau": 4, "bihor": 5,
        "bistrita-nasaud": 6, "botosani": 7, "brasov": 8, "braila": 9, "buzau": 10,
        "caras-severin": 11, "calarasi": 51, "cluj": 12, "constanta": 13, "covasna": 14,
        "dambovita": 15, "dolj": 16, "galati": 17, "giurgiu": 52, "gorj": 18, "harghita": 19,
        "hunedoara": 20, "ialomita": 21, "iasi": 22, "ilfov": 23, "maramures": 24,
        "mehedinti": 25, "mures": 26, "neamt": 27, "olt": 28, "prahova": 29, "satu mare": 30,
        "salaj": 31, "sibiu": 32, "suceava": 33, "teleorman": 34, "timis": 35, "tulcea": 36,
        "vaslui": 37, "valcea": 38, "vrancea": 39}

def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    if not str(prof.get("cui_numeric") or "").strip():
        erori.append("Lipsă CUI firmă.")
    if not str(prof.get("nume") or "").strip():
        erori.append("Lipsă denumire firmă.")
    # regCom e OBLIGATORIU in S1005/S1003 (verificat la sursa: DUKIntegrator -v S1005 respinge XML-ul cu
    # "eroare atribut: regCom: atributul trebuie sa existe"). Fara aceasta poarta, genereaza emitea un
    # bilant FARA regCom - exact "XML respins de ANAF" pe care docstring-ul spune ca poarta il previne.
    if not str(prof.get("reg_com") or "").strip():
        erori.append("Nr. registrul comerțului lipsește — obligatoriu în bilanț; fără el declarația e "
                     "respinsă de validatorul ANAF. Se completează la Date firmă.")
    return erori


def genereaza(conn, schema, an):
    import re
    av = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        p = dict(cur.fetchone() or {})
        f10p, f10c = coloanele_f10(cur, schema, an, av)
        rl = _rulaje_67(cur, schema, an)
    j = (p.get("judet") or "bucuresti").strip().lower()
    prof = {
        "cui_numeric": re.sub(r"\D", "", p.get("cui") or ""),
        "nume": p.get("nume"), "caen": re.sub(r"\D", "", p.get("caen") or ""),
        "reg_com": p.get("reg_com") or "", "adresa": p.get("adresa") or "",
        "cod_judet": _JUD.get(j, 40),
        "declarant_nume": p.get("declarant_nume"),
        "intocmit_nume": p.get("declarant_nume"),
    }
    if not prof["reg_com"]:
        av.append("Nr. Reg. Com. lipsă în Profil firma (câmp obligatoriu S1005).")
    if not prof.get("declarant_nume"):
        # [declarant thread 3] Regula 4: fara fabricare tacita a administratorului
        av.append("Bilanț: declarantul (administrator) lipsește din profil — se trece implicit "
                  "\"ADMINISTRATOR\". Completează declarantul în Date firmă.")
    f20c = _b.f20_din_rulaje(rl)
    f20p = {}
    av.append("F20 an precedent necompletat (istoric indisponibil) - de completat manual dacă e cazul.")
    if f10c.get(15) != f10c.get(49):
        av.append(f"Verificare: rândul 15 (F) = {f10c.get(15)} diferă de rândul 49 (J) = {f10c.get(49)} — datoriile peste un an, "
                  "provizioanele sau veniturile în avans pot explica diferența.")
    _er = erori_generare(prof)
    if _er:
        raise ValueError("Bilanț nu se poate genera: " + " ".join(_er))
    return _b.xml_s1005(prof, an, f10p, f10c, f20p, f20c), av


def genereaza_s1003(conn, schema, an):
    """S1003 (mici): F10 identic, F20 complet."""
    import re
    av = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        p = dict(cur.fetchone() or {})
        f10p, f10c = coloanele_f10(cur, schema, an, av)
        rl = _rulaje_67(cur, schema, an)
    j = (p.get("judet") or "bucuresti").strip().lower()
    prof = {
        "cui_numeric": re.sub(r"\D", "", p.get("cui") or ""),
        "nume": p.get("nume"), "caen": re.sub(r"\D", "", p.get("caen") or ""),
        "reg_com": p.get("reg_com") or "", "adresa": p.get("adresa") or "",
        "cod_judet": _JUD.get(j, 40),
        "declarant_nume": p.get("declarant_nume"),
        "intocmit_nume": p.get("declarant_nume"),
    }
    f20c = _b.f20_complet_din_rulaje(rl)
    av.append("F20 an precedent necompletat - de completat manual dacă e cazul.")
    _er = erori_generare(prof)
    if _er:
        raise ValueError("Bilanț nu se poate genera: " + " ".join(_er))
    return _b.xml_s1003(prof, an, f10p, f10c, {}, f20c), av
