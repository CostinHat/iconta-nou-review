# -*- coding: utf-8 -*-
"""D112 - generator VALIDAT DUKIntegrator (portat din monolit /opt/iconta 04.07.2026).
Include CM: asiguratB3 + asiguratD + angajatorC2 (OUG 158/2005).
pull() citeste salariati + concedii_medicale din schema tenantului."""
import re

def _nzl(an, luna):  # cm_media6_v1
    if an == 2026:
        return _D112_NZL_2026.get(luna, 21)
    if an == 2025:
        return _D112_NZL_2025.get(luna, 21)
    return 21

def _sal_minim(an, luna):
    # salariul minim brut pe economie (HG 146/2026). Actualizabil anual.
    if an == 2026:
        return 4050 if luna <= 6 else 4325
    if an < 2026:
        return 4050
    return 4325  # 2027+ fallback pana la actualizare
_D112_NS = "mfp:anaf:dgti:declaratie_unica:declaratie:v7"
_D112_NZL_2026 = {1: 18, 2: 20, 3: 22, 4: 20, 5: 20, 6: 21, 7: 23, 8: 21, 9: 22, 10: 22, 11: 20, 12: 21}
_D112_NZL_2025 = {1: 18, 2: 20, 3: 21, 4: 20, 5: 21, 6: 20, 7: 23, 8: 20, 9: 22, 10: 23, 11: 20, 12: 20}  # cm_media6_v1
def _cm_media6(brut, data_ang, an, luna):  # cm_media6_v1
    """Media zilnica reala pe ultimele 6 luni (OUG 158). Returneaza (d17, d18, media).
    Presupune brut constant pe ferestra (istoric variabil/mariri -> deferat)."""
    try:
        brut = float(brut or 0)
    except Exception:
        brut = 0.0
    ay = al = None
    if data_ang:
        try:
            _p = str(data_ang)[:10].split("-")
            ay, al = int(_p[0]), int(_p[1])
        except Exception:
            ay = al = None
    d17 = 0.0
    d18 = 0
    cap = 0
    for k in range(1, 7):
        m = luna - k
        y = an
        while m <= 0:
            m += 12
            y -= 1
        if ay is not None and (y, m) < (ay, al):
            continue
        d17 += brut
        d18 += _nzl(y, m)
        cap += 12 * _sal_minim(y, m)
    if d18 <= 0:
        d17 = brut
        d18 = 21
    if cap and d17 > cap:
        d17 = float(cap)
    media = round(d17 / d18, 2) if d18 else 0.0
    return round(d17, 2), d18, media
_D112_CASA = {
    "bucuresti": "_B", "alba": "AB", "arad": "AR", "arges": "AG", "bacau": "BC", "bihor": "BH",
    "bistrita-nasaud": "BN", "bistrita nasaud": "BN", "botosani": "BT", "brasov": "BV", "braila": "BR",
    "buzau": "BZ", "caras-severin": "CS", "caras severin": "CS", "cluj": "CJ", "constanta": "CT",
    "covasna": "CV", "calarasi": "CL", "dambovita": "DB", "dolj": "DJ", "galati": "GL", "giurgiu": "GR",
    "gorj": "GJ", "harghita": "HR", "hunedoara": "HD", "ialomita": "IL", "iasi": "IS", "ilfov": "IF",
    "maramures": "MM", "mehedinti": "MH", "mures": "MS", "neamt": "NT", "olt": "OT", "prahova": "PH",
    "satu mare": "SM", "satu-mare": "SM", "salaj": "SJ", "sibiu": "SB", "suceava": "SV", "teleorman": "TR",
    "timis": "TM", "tulcea": "TL", "vaslui": "VS", "valcea": "VL", "vrancea": "VN",
}
def _d112esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))
def _d112_casa(judet):
    j = (judet or "").strip().lower()
    j = (j.replace("\u0103", "a").replace("\u00e2", "a").replace("\u00ee", "i")
          .replace("\u015f", "s").replace("\u0219", "s").replace("\u0163", "t").replace("\u021b", "t"))
    return _D112_CASA.get(j, "_B")
def _d112int(x):
    try:
        return int(round(float(x or 0)))
    except Exception:
        return 0
def _d112_data(s):
    """ISO 'AAAA-LL-ZZ' -> 'ZZ.LL.AAAA'. Daca nu se potriveste, intoarce ca atare."""
    s = (s or "").strip()
    p = s.split("-")
    if len(p) == 3 and len(p[0]) == 4:
        return "%s.%s.%s" % (p[2], p[1], p[0])
    return s
def _d112_genereaza(prof, salariati, an, luna):
    """D112: structura + angajator (impozit + CAS/CASS/CAM + C1) + asigurat grup B
    (contributii) + E1 (agregat impozit) + E3 (impozit). Returneaza (xml_str, avertismente)."""
    import re
    av = []
    nzl = _D112_NZL_2026.get(luna, 21)
    perioada = "%02d.%04d" % (luna, an)
    cui_f = re.sub(r"\D", "", (prof.get("cui") or ""))
    den_f = prof.get("nume") or ""
    caen_f = re.sub(r"\D", "", (prof.get("caen") or "")) or "0000"
    casa_ang = _d112_casa(prof.get("judet"))
    # nume_declar/prenume_declar: campul asteapta NUMELE PERSOANEI care depune, nu
    # denumirea firmei. Fallback-ul pe den_f (cand declarant_nume lipseste din profil)
    # putea depasi limita de 75 caractere a validatorului ANAF - dovedit 15.07.2026:
    # "nume_declar: sir mai lung de 75 caractere" pe o denumire de cabinet de 117.
    # Trunchiem defensiv la 74 (sub limita), pentru orice firma cu denumire lunga -
    # solutia corecta ramane completarea declarant_nume in profil (ecranul Date firma).
    nume_d = (prof.get("declarant_nume") or den_f or "ADMINISTRATOR")[:74]
    pren_d = (prof.get("declarant_prenume") or "-")[:74]
    func_d = (prof.get("declarant_functie") or "ADMINISTRATOR")[:74]
    if not cui_f:
        av.append("CUI firma lipsa - completeaza Profil firma.")
    if caen_f == "0000":
        av.append("CAEN firma lipsa/invalid - D112 cere CAEN valid in Profil firma.")
    sum_imp = sum_cas = sum_cass = sum_bazac = 0
    cas_ang_dif = cass_ang_dif = 0  # d112_b4p_v2
    c2_count = c2_d16 = c2_d14 = c2_d15 = c2_d20 = c2_d21 = 0  # d112_cm_v1
    c1_12 = 0
    AS = []
    idx = 0
    for s in salariati:
        idx += 1
        brut = _d112int(s.get("brut"))
        facil = _d112int(s.get("facilitate"))
        bazac = brut - facil
        if bazac < 0:
            bazac = 0
        cas = _d112int(s.get("cas"))
        cass = _d112int(s.get("cass"))
        _cas_w = cas; _cass_w = cass  # worked-only pt topup part-time+CM - d112_ptcm_v1
        imp = _d112int(s.get("impozit"))
        ore = int(s.get("ore_zi") or 8)
        if ore not in (6, 7, 8):
            ore = 8
        cms = s.get("cm") or []
        zile_cm = int(s.get("zile_cm") or 0)
        _b3 = []
        _dl = []
        brute = brut
        b4base = bazac
        if cms and zile_cm > 0:
            zile = nzl - zile_cm
            if zile < 0:
                zile = 0
            cm_ang = sum(_d112int(x.get("brut_ang")) for x in cms)
            cm_fnuass = sum(_d112int(x.get("brut_fnuass")) for x in cms)
            cm_base = cm_ang + cm_fnuass
            b3z = sum(int(x.get("zile_ang") or 0) + int(x.get("zile_fnuass") or 0) for x in cms)
            sza = sum(int(x.get("zile_ang") or 0) for x in cms)
            szf = sum(int(x.get("zile_fnuass") or 0) for x in cms)
            total_base = bazac + cm_base
            cas = _d112int(round(total_base * 0.25))
            cass = _d112int(round(total_base * 0.10))
            ded = float(s.get("deducere") or 0)
            bimp = total_base - cas - cass - ded
            if bimp < 0:
                bimp = 0
            imp = _d112int(round(bimp * 0.10))
            brute = brut + cm_base
            b4base = total_base
            _b3.append('    <asiguratB3 B3_1="%d" B3_6="%d" B3_7="%d" B3_11="0" B3_12="%d" B3_13="%d"/>' % (b3z, b3z, cm_base, cm_ang, cm_fnuass))
            for x in cms:
                za = int(x.get("zile_ang") or 0)
                zf = int(x.get("zile_fnuass") or 0)
                d16 = za + zf
                d20 = _d112int(x.get("brut_ang"))
                d21 = _d112int(x.get("brut_fnuass"))
                _m17, _m18, media = _cm_media6(x.get("baza"), s.get("data_angajare"), an, luna)  # cm_media6_v1
                d18 = _m18
                d17 = _d112int(round(_m17))
                if d17 == 0:  # d112_s107_v1: S107.1 - fara medie => si d18=0
                    d18 = 0
                d19 = round(d17 / d18, 2) if d18 else 0
                # d112_atrib_optionale_v1: atributele optionale se omit cand sunt goale (vid nepermis)
                _opt = ""
                for _a, _v in (("D_1", _d112esc(x.get("serie"))), ("D_2", _d112esc(x.get("numar"))),
                               ("D_5", x.get("da") or ""), ("D_6", x.get("di") or ""), ("D_7", x.get("ds") or "")):
                    if _v:
                        _opt += ' %s="%s"' % (_a, _v)
                _dl.append('    <asiguratD%s D_9="%s" D_10="%d" '
                           'D_14="%d" D_15="%d" D_16="%d" D_17="%d" D_18="%d" D_19="%.2f" D_20="%d" D_21="%d" D_23="%s"/>'
                           % (_opt, (x.get("cod") or "01"), int(x.get("loc_prescriere") or 1),
                              za, zf, d16, d17, d18, d19, d20, d21, _d112esc(x.get("diagnostic") or "999")))
            c2_count += len(cms)
            c2_d16 += b3z
            c2_d14 += sza
            c2_d15 += szf
            c2_d20 += cm_ang
            c2_d21 += cm_fnuass
            c1_12 += cm_base
        else:
            zile = nzl
        ore_lucr = zile * ore
        casa_sn = _d112_casa(s.get("judet_casa") or prof.get("judet"))
        dataang = _d112_data(s.get("data_angajare"))
        sum_imp += imp
        sum_cas += cas
        sum_cass += cass
        sum_bazac += bazac
        pt_ap = bool(s.get("pt_aplica"))  # part-time se aplica si cu CM (topup proratat) - d112_ptcm_v1
        b4_5p = b4_6p = b4_7p = b4_8p = b4_6d = b4_8d = 0
        asigexc = 0
        if bool(s.get("scutit")) and _d112int(s.get("motiv_exceptare")) in (1, 2, 3, 4, 5):  # d112_motivexc_v1
            asigexc = 1
        if pt_ap:
            b4_5p = b4_7p = _d112int(s.get("baza_minim_pt"))
            b4_6p = _d112int(s.get("cass_min_pt"))
            b4_8p = _d112int(s.get("cas_min_pt"))
            b4_6d = b4_6p - _cass_w
            b4_8d = b4_8p - _cas_w
            if b4_6d < 0:
                b4_6d = 0
            if b4_8d < 0:
                b4_8d = 0
            asigexc = 2
            cass_ang_dif += b4_6d
            cas_ang_dif += b4_8d
        a = []
        _mx = (' motivExc="%d"' % _d112int(s.get("motiv_exceptare"))) if asigexc == 1 else ""  # d112_motivexc_v1
        a.append('  <asigurat idAsig="%d" cnpAsig="%s" numeAsig="%s" prenAsig="%s" dataAng="%s" '
                 'casaSn="%s" asigCI="1" asigSO="1" asigExc="%d"%s Timp_E3="%d">'
                 % (idx, _d112esc(s.get("cnp")), _d112esc(s.get("nume")), _d112esc(s.get("prenume")),
                    _d112esc(dataang), casa_sn, asigexc, _mx, imp))
        a.append('    <asiguratB1 B1_1="1" B1_2="0" B1_3="N" B1_4="%d" B1_5="%d" B1_6="%d" '
                 'B1_10="%d" B1_15="%d" B1_sal1="%d" B1_sal2="%d"/>'
                 % (ore, bazac, ore_lucr, brut, zile, brut, brut))
        a.append('    <asiguratB2 B2_2="%d" B2_5="%d" B2_5P="%d"/>' % (zile, bazac, b4_7p))  # d112_b4p_v3
        a.extend(_b3)
        a.append('    <asiguratB4 B4_1="%d" B4_3="%d" B4_5="%d" B4_6="%d" B4_7="%d" B4_8="%d" B4_14="%d" '
                 'B4_5P="%d" B4_6P="%d" B4_7P="%d" B4_8P="%d" B4_7S="0" B4_7C="0" B4_8D="%d" B4_6D="%d"/>'
                 % (zile, brut, b4base, cass, b4base, cas, bazac, b4_5p, b4_6p, b4_7p, b4_8p, b4_8d, b4_6d))
        a.extend(_dl)
        a.append('    <asiguratE1 E1_1="%d" E1_2="%d" E1_3="0" E1_4="0" E1_5="0" E1_6="%d" E1_7="%d" '
                 'E1_41="0" E1_42="0" E1_421="0" E1_422="0"/>' % (brute, b4base, imp, imp))
        a.append('    <asiguratE3 E3_1="B" E3_2="1" E3_3="1" E3_4="A" E3_5="%s" E3_6="%s" E3_8="%d" '
                 'E3_9="%d" E3_14="%d" E3_15="%d" E3_16="0" E3_19="0" E3_21="0"/>'
                 % (perioada, perioada, brute, b4base, imp, imp))
        a.append('  </asigurat>')
        AS.append("\n".join(a))
    n = len(salariati)
    cam_total = _d112int(round(sum_bazac * 0.0225))
    A = []
    def add_oblig(cod, cb, val):
        if val > 0:
            A.append('    <angajatorA A_codOblig="%s" A_codBugetar="%s" A_datorat="%d" '
                     'A_deductibil="0" A_scutit="0" A_plata="%d"/>' % (cod, cb, val, val))
    add_oblig("602", "5503XXXXXX", sum_imp)
    add_oblig("412", "5503XXXXXX", sum_cas)
    add_oblig("432", "5503XXXXXX", sum_cass)
    add_oblig("480", "20470300XX", cam_total)
    add_oblig("458", "5503XXXXXX", cas_ang_dif)
    add_oblig("459", "5503XXXXXX", cass_ang_dif)
    total_plata = sum_imp + sum_cas + sum_cass + cam_total + cas_ang_dif + cass_ang_dif
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    H.append('<declaratieUnica xmlns="%s" luna_r="%d" an_r="%d" d_rec="0" '
             'nume_declar="%s" prenume_declar="%s" functie_declar="%s">'
             % (_D112_NS, luna, an, _d112esc(nume_d), _d112esc(pren_d), _d112esc(func_d)))
    H.append('  <angajator cif="%s" caen="%s" den="%s" casaAng="%s" datCAM="1" bifa_CAM="0" '
             'totalPlata_A="%d">' % (cui_f, caen_f, _d112esc(den_f), casa_ang, total_plata))
    H.extend(A)
    H.append('    <angajatorB B_cnp="%d" B_sanatate="%d" B_pensie="%d" B_brutSalarii="%d" B_sal="%d"/>'
             % (n, n, n, sum_bazac, n))
    H.append('    <angajatorC1 C1_11="%d" C1_12="%d" C1_T1="%d" C1_T2="%d" C1_T="0"/>' % (sum_bazac, c1_12, sum_bazac, c1_12))
    if c2_count > 0:
        H.append('    <angajatorC2 C2_11="%d" C2_12="%d" C2_13="%d" C2_14="%d" C2_15="%d" C2_16="%d" '
                 'C2_T6="%d" C2_10="%d" C2_140="%d"/>'
                 % (c2_count, c2_d16, c2_d14, c2_d15, c2_d20, c2_d21, c2_d21, c2_d21, c2_d21))
    H.append('    <angajatorC4 C4_baza="%d" C4_ct="%d"/>' % (sum_bazac, cam_total))
    H.append('  </angajator>')
    H.extend(AS)
    H.append('</declaratieUnica>')
    av.append("D112: %d salariati - impozit %d, CAS %d, CASS %d, CAM %d lei (luna %d/%d)."
              % (n, sum_imp, sum_cas, sum_cass, cam_total, luna, an))
    return ("\n".join(H), av)


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        prof = dict(cur.fetchone() or {})
        cur.execute(f"SELECT * FROM {schema}.salariati WHERE activ = true ORDER BY id")
        sal = [dict(r) for r in cur.fetchall()]
        cur.execute(f"""SELECT * FROM {schema}.concedii_medicale
                        WHERE an=%s AND luna=%s""", (an, luna))
        cms = [dict(r) for r in cur.fetchall()]
    pe_sal = {}
    for c in cms:
        pe_sal.setdefault(c["salariat_id"], []).append({
            "serie": c.get("serie"), "numar": c.get("numar"),
            "da": _d112_data(str(c.get("data_acordare") or "")),
            "di": _d112_data(str(c.get("data_inceput") or "")),
            "ds": _d112_data(str(c.get("data_sfarsit") or "")),
            "cod": c.get("cod") or "01",
            "loc_prescriere": c.get("loc_prescriere") or 1,
            "zile_ang": c.get("zile_ang") or 0,
            "zile_fnuass": c.get("zile_fnuass") or 0,
            "brut_ang": c.get("brut_ang") or 0,
            "brut_fnuass": c.get("brut_fnuass") or 0,
            "baza": c.get("baza") or 0,
            "diagnostic": c.get("diagnostic") or "",
        })
    salariati = []
    for s in sal:
        cm = pe_sal.get(s["id"], [])
        salariati.append({
            "nume": s.get("nume"), "prenume": s.get("prenume") or "-",
            "cnp": s.get("cnp"), "brut": s.get("salariu_brut"),
            "data_angajare": str(s.get("data_angajare") or ""),
            "ore_zi": s.get("ore_zi") or 8,
            "judet_casa": s.get("judet"),
            "part_time": bool(s.get("part_time")),
            "persoane_intretinere": s.get("persoane_intretinere") or 0,
            "scutit_pt": bool(s.get("scutit_contrib_minim")),
            "scutit": bool(s.get("scutit_contrib_minim")),
            "motiv_exceptare": s.get("motiv_exceptare"),
            "cm": cm,
            "zile_cm": sum(x["zile_ang"] + x["zile_fnuass"] for x in cm),
            # calcul din core.salarizare (facilitate/deducere/contributii pe brut)
        })
    from core import salarizare as _sz
    from core import common as _cm
    from datetime import date as _dt
    import calendar as _cal
    ref = _dt(an, luna, 1)
    sm, _t1 = _cm.cota("salariu_minim", ref)
    fac, _t2 = _cm.cota("facilitate_salariu_minim", ref)
    prag_pt = float(sm) - float(fac)  # baza minima part-time (structura D112: sm-facilitate)
    nzl = sum(1 for z in range(1, _cal.monthrange(an, luna)[1] + 1)
              if _dt(an, luna, z).weekday() < 5)
    # ALINIERE la stat_plata_api:36-38 (15.07.2026). pull() chema calcul_salariu(brut,
    # la_data) GOL: fara persoane / norma_intreaga / venit_brut_total, si pe brutul
    # INTREG, nu pe cel lucrat. Statul de plata le paseaza pe toate patru -> acelasi
    # salariat primea deducere personala, facilitate si plafon DIFERITE in D112 fata de
    # fluturas. Sursa unica de adevar: statul de plata (stat_plata_api).
    #  - persoane: deducerea personala (art. 77) reduce impozitul declarat
    #  - norma_intreaga: facilitatea (HG 146/2026 o da doar la norma intreaga)
    #  - venit_brut_total: plafonul facilitatii se judeca pe brutul CONTRACTUAL
    #  - brut_lucrat: pe zilele de CM salariul nu se plateste de angajator
    for s in salariati:
        brut_int = float(s["brut"] or 0)
        zile_cm_s = int(s.get("zile_cm") or 0)
        brut_lucrat = (brut_int * max(nzl - zile_cm_s, 0) / nzl) if (nzl and zile_cm_s) else brut_int
        r = _sz.calcul_salariu(brut_lucrat,
                               persoane=s.get("persoane_intretinere") or 0,
                               la_data=ref,
                               norma_intreaga=not s.get("part_time"),
                               venit_brut_total=brut_int)
        s["brut_lucrat"] = brut_lucrat   # consumat de salarii_contare (o singura cifra)
        s["facilitate"] = r.get("facilitate", 0)
        s["cas"] = r.get("cas", 0)
        s["cass"] = r.get("cass", 0)
        s["impozit"] = r.get("impozit", 0)
        s["deducere"] = (r.get("deducere") or {}).get("total", 0)
        # part-time supra-taxare (art. 146(5^6)/168(6^1) CF, structura D112 v7):
        # part_time = ROUND(prag_pt * zile_lucrate / NZL); daca 0 < baza < part_time
        # -> B4_*P la prag, diferenta pe angajator. Exceptati: scutit+motiv 1-5.
        zile_lucr = max(nzl - int(s.get("zile_cm") or 0), 0)
        baza = float(s["brut"] or 0)
        scutit = bool(s.get("scutit_pt"))
        prag_zile = round(prag_pt * zile_lucr / nzl) if nzl else 0
        if not scutit and 0 < baza < prag_zile:
            s["pt_aplica"] = True
            s["baza_minim_pt"] = prag_zile
            s["cas_min_pt"] = round(prag_zile * 0.25)
            s["cass_min_pt"] = round(prag_zile * 0.10)
        else:
            s["pt_aplica"] = False
    return prof, salariati


def genereaza(conn, schema, an, luna):
    prof, salariati = pull(conn, schema, an, luna)
    return _d112_genereaza(prof, salariati, an, luna)
