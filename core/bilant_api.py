# -*- coding: utf-8 -*-
"""S1005 - strat DB: solduri finale + rulaje din note VALIDATE, apoi core.bilant."""
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import bilant as _b
from core.common import cere_coloane_cursor  # [garda coloane 27.07.2026]
_COLOANE_PROFIL = ("nume", "cui", "adresa", "caen")   # minimul citit de aici

def _solduri_la(cur, schema, an):
    """Solduri finale la 31.12.an: solduri_initiale + miscari validate pana la 31.12.an."""
    cur.execute(f"SELECT cont, sold_debitor, sold_creditor FROM {schema}.solduri_initiale")
    net = {}
    for r in cur.fetchall():
        net[r["cont"]] = net.get(r["cont"], Decimal("0")) + Decimal(str(r["sold_debitor"])) - Decimal(str(r["sold_creditor"]))
    cur.execute(f"""
        SELECT l.cont_debit, l.cont_credit, l.suma
        FROM {schema}.inregistrari_linii l
        JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
        WHERE i.status = 'validata' AND i.data <= %s""", (f"{an}-12-31",))
    for r in cur.fetchall():
        s = Decimal(str(r["suma"]))
        net[r["cont_debit"]] = net.get(r["cont_debit"], Decimal("0")) + s
        net[r["cont_credit"]] = net.get(r["cont_credit"], Decimal("0")) - s
    return {c: ((v, Decimal("0")) if v >= 0 else (Decimal("0"), -v)) for c, v in net.items()}

def _solduri_initiale(cur, schema):
    cur.execute(f"SELECT cont, sold_debitor, sold_creditor FROM {schema}.solduri_initiale")
    return {r["cont"]: (Decimal(str(r["sold_debitor"])), Decimal(str(r["sold_creditor"])))
            for r in cur.fetchall()}

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
        erori.append("LIPSĂ CUI firmă.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firmă.")
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
        s_fin = _solduri_la(cur, schema, an)
        s_ini = _solduri_initiale(cur, schema)
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
        av.append("Bilant: declarantul (administrator) lipsește din profil -> emis implicit "
                  "\"ADMINISTRATOR\". Completează declarantul în Date firma.")
    f10c = _b.f10_din_balanta(s_fin)
    f10p = _b.f10_din_balanta(s_ini)
    f20c = _b.f20_din_rulaje(rl)
    f20p = {}
    av.append("F20 an precedent necompletat (istoric indisponibil) - de completat manual dacă e cazul.")
    if f10c.get(15) != f10c.get(49):
        av.append(f"Verificare: F(rd15)={f10c.get(15)} != J(rd49)={f10c.get(49)} - datorii>1an/provizioane/ven.avans pot explica diferenta.")
    _er = erori_generare(prof)
    if _er:
        raise ValueError("Bilant nu se poate genera: " + " ".join(_er))
    return _b.xml_s1005(prof, an, f10p, f10c, f20p, f20c), av


def genereaza_s1003(conn, schema, an):
    """S1003 (mici): F10 identic, F20 complet."""
    import re
    av = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        p = dict(cur.fetchone() or {})
        s_fin = _solduri_la(cur, schema, an)
        s_ini = _solduri_initiale(cur, schema)
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
    f10c = _b.f10_din_balanta(s_fin)
    f10p = _b.f10_din_balanta(s_ini)
    f20c = _b.f20_complet_din_rulaje(rl)
    av.append("F20 an precedent necompletat - de completat manual dacă e cazul.")
    _er = erori_generare(prof)
    if _er:
        raise ValueError("Bilant nu se poate genera: " + " ".join(_er))
    return _b.xml_s1003(prof, an, f10p, f10c, {}, f20c), av
