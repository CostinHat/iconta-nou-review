# -*- coding: utf-8 -*-
"""D112 - generator VALIDAT DUKIntegrator (portat din monolit /opt/iconta 04.07.2026).
Include CM: asiguratB3 + asiguratD + angajatorC2 (OUG 158/2005).
pull() citeste salariati + concedii_medicale din schema tenantului."""

from core.common import text_anaf as _t, cere_coloane_cursor  # limita 75 car. ANAF + garda coloane (27.07.2026)
import re
from core import scadente as _scad
from core import pontaj as _pontaj
from core import perioada as _per
from core import beneficii_api as _ben
from core.pdf_util import bani

def _nzl(an, luna):
    # Zile lucratoare din luna, FARA sarbatori legale (OUG 158/2005 art.10). Sursa UNICA
    # scadente.zile_lucratoare_luna - inainte erau tabele hardcodate _D112_NZL_2025/2026
    # (corecte, dar a doua sursa de adevar + drift pe 2027+) SI un weekday<5 gresit.
    return _scad.zile_lucratoare_luna(an, luna)

def _sal_minim(an, luna):
    """Salariul minim brut pe economie, din registrul unic de cote.

    29.07.2026: era hardcodat aici (4050/4325 + fallback 4325 pentru 2027+), desi
    common.COTE il tine cu perioada si temei (HG 1510/2024, HG 146/2026). A doua sursa de
    adevar: la urmatoarea majorare se schimba in doua locuri, iar fallback-ul ar fi dat
    tacit o valoare care nu mai e a nimanui.

    Registrul RIDICA daca nu exista valoare pentru data ceruta - preferabil unei cifre
    plauzibile si gresite intr-o declaratie depusa la ANAF."""
    from datetime import date as _date
    from core.common import cota
    valoare, _temei = cota("salariu_minim", _date(an, luna, 1))
    return int(valoare)
_D112_NS = "mfp:anaf:dgti:declaratie_unica:declaratie:v7"
def _cm_media6(brut, data_ang, an, luna):  # cm_media6_v1
    """Media zilnica reala pe ultimele 6 luni (OUG 158). Returneaza (d17, d18, media).
    Presupune brut constant pe ferestra (istoric variabil/mariri -> deferat)."""
    from core.numere import numar_fiscal
    brut = float(numar_fiscal(brut, "brut concediu medical"))
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
    """Rotunjire ARITMETICA (nu bancara): daca partea zecimala >= 0.5, se adauga 1
    - regula explicita din ANAF structura D112 0126_030226 ("Contributiile se rotunjesc
    aritmetic"). round() din Python foloseste rotunjire bancara (half-to-even:
    112.5 -> 112), care contrazice regula ANAF (112.5 -> 113) - dovedit prin
    validator: CAM calculat 112, cerut 113 (DUK regula A91b)."""
    from decimal import Decimal, ROUND_HALF_UP
    from core.numere import numar_fiscal
    # MASCA SCOASA 27.07.2026: `except: return 0` facea ca o valoare stricata sa
    # devina tacit 0 lei in declaratie. Rotunjirea ramane NESCHIMBATA (aritmetica).
    return int(numar_fiscal(x, "D112").quantize(Decimal("1"), rounding=ROUND_HALF_UP))
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
    from core import salarizare as _sz
    from datetime import date as _d112date
    ref = _d112date(an, luna, 1)
    av = []
    nzl = _nzl(an, luna)
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
    # [:74] local inlocuit cu _t (common.text_anaf) - aceeasi regula, un singur loc.
    nume_d = _t(prof.get("declarant_nume") or den_f or "ADMINISTRATOR")
    pren_d = _t(prof.get("declarant_prenume") or "-")
    func_d = _t(prof.get("declarant_functie") or "ADMINISTRATOR")
    if not cui_f:
        av.append("CUI firma lipsa - completeaza Profil firma.")
    if caen_f == "0000":
        av.append("CAEN firma lipsa/invalid - D112 cere CAEN valid in Profil firma.")
    sum_imp = sum_cas = sum_cass = sum_bazac = 0
    cas_ang_dif = cass_ang_dif = 0  # d112_b4p_v2
    _c2_cazuri = []  # [D112 C2 pe rand] (cod, d16, d14=za, d15=zf, d20, d21) per certificat
    c1_12 = 0
    AS = []
    idx = 0
    for s in salariati:
        idx += 1
        brut = _d112int(s.get("brut")) + _d112int(s.get("exces_vacanta", 0))  # [D3] excesul de vacanta in brutul declarat (S731)
        facil = _d112int(s.get("facilitate"))
        bazac = brut - facil
        if bazac < 0:
            bazac = 0
        cas = _d112int(s.get("cas"))
        cass = _d112int(s.get("cass"))
        _cas_w = cas; _cass_w = cass  # worked-only pt topup part-time+CM - d112_ptcm_v1
        # [F133] tichete: CASS + impozit pe tichete se adauga peste salariu(+CM), uniform mai jos.
        # imp din s = TOTAL (salariu+tichete) -> il reducem la salariu-only aici (in ramura CM
        # imp se recalculeaza oricum fara tichete). Tichetele n-au CAS.
        cass_tichete = _d112int(s.get("cass_tichete", 0))
        impozit_tichete = _d112int(s.get("impozit_tichete", 0))
        tichete_nom = _d112int(s.get("tichete_nominal", 0))
        imp = _d112int(s.get("impozit")) - impozit_tichete
        ore = int(s.get("ore_zi") or 8)
        if ore not in (6, 7, 8):
            ore = 8
        cms = s.get("cm") or []
        zile_cm = int(s.get("zile_cm") or 0)
        _b3 = []
        _dl = []
        brute = brut
        b4base = bazac
        cass_base_cm = bazac   # [UNIFICARE CM] baza CASS (salariu + CM doar 01/07/10); default = salariu
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
            # [UNIFICARE CM 31.07.2026] contributiile pe indemnizatia CM prin functia canonica
            # salarizare.taxe_cm, apelata PER CERTIFICAT (cod): CAS 25% UNIFORM (CF art.139(1)(o)+140),
            # CASS doar 01/07/10 (OUG 34/2024). Salariul (bazac) isi pastreaza 25%/10%. Fluturasul (la
            # salvare) si D112 (aici) consuma ACEEASI functie - divergenta celor doua lanturi dispare.
            cm_cas = 0
            cm_cass = 0
            cm_cass_base = 0
            for _x in cms:
                _xb = _d112int(_x.get("brut_ang")) + _d112int(_x.get("brut_fnuass"))
                _xt = _sz.taxe_cm(_xb, _x.get("cod") or "01", la_data=ref)
                cm_cas += _d112int(_xt["cas"])
                cm_cass += _d112int(_xt["cass"])
                if _d112int(_xt["cass"]) > 0:
                    cm_cass_base += _xb
                _cza = int(_x.get("zile_ang") or 0); _czf = int(_x.get("zile_fnuass") or 0)
                _c2_cazuri.append((str(_x.get("cod") or "01").zfill(2), _cza + _czf, _cza, _czf,
                                   _d112int(_x.get("brut_ang")), _d112int(_x.get("brut_fnuass"))))
            cas = _d112int(bazac * 0.25) + cm_cas
            cass = _d112int(bazac * 0.10) + cm_cass
            cass_base_cm = bazac + cm_cass_base
            ded = float(s.get("deducere") or 0)
            bimp = total_base - cas - cass - ded
            if bimp < 0:
                bimp = 0
            imp = _d112int(bimp * 0.10)
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
                d17 = _d112int(_m17)
                if d17 == 0:  # d112_s107_v1: S107.1 - fara medie => si d18=0
                    d18 = 0
                d19 = round(d17 / d18, 2) if d18 else 0
                # d112_atrib_optionale_v1: atributele optionale se omit cand sunt goale (vid nepermis)
                _opt = ""
                for _a, _v in (("D_1", _d112esc(x.get("serie"))), ("D_2", _d112esc(x.get("numar"))),
                               ("D_5", x.get("da") or ""), ("D_6", x.get("di") or ""), ("D_7", x.get("ds") or "")):
                    if _v:
                        _opt += ' %s="%s"' % (_a, _v)
                if str(x.get("cod") or "01").zfill(2) == "06" and x.get("cod_urgenta"):
                    _opt += ' D_11="%d"' % int(x.get("cod_urgenta"))  # [D_11] cod urgenta HG 423/2020, oblig. la cod 06 (D112 C(3), mutex D_12)
                _dl.append('    <asiguratD%s D_9="%s" D_10="%d" '
                           'D_14="%d" D_15="%d" D_16="%d" D_17="%d" D_18="%d" D_19="%.2f" D_20="%d" D_21="%d" D_23="%s"/>'
                           % (_opt, (x.get("cod") or "01"), int(x.get("loc_prescriere") or 1),
                              za, zf, d16, d17, d18, d19, d20, d21, _d112esc(x.get("diagnostic") or "999")))
            c1_12 += cm_base
        else:
            zile = nzl
        # [F133] adauga tichetele uniform (dupa ambele ramuri): CASS + impozit pe tichete,
        # baza CASS include nominalul; baza CAS (b4base) NU se atinge (tichetele n-au CAS).
        cass += cass_tichete
        imp += impozit_tichete
        baza_cass = cass_base_cm + tichete_nom   # [UNIFICARE CM] baza CASS exclude CM ne-eligibil (08/09 etc.)
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
                 % (zile, brut, baza_cass, cass, b4base, cas, bazac, b4_5p, b4_6p, b4_7p, b4_8p, b4_8d, b4_6d))
        a.extend(_dl)
        a.append('    <asiguratE1 E1_1="%d" E1_2="%d" E1_3="0" E1_4="0" E1_5="0" E1_6="%d" E1_7="%d" '
                 'E1_41="0" E1_42="0" E1_421="0" E1_422="0"/>' % (brute, b4base, imp, imp))
        a.append('    <asiguratE3 E3_1="B" E3_2="1" E3_3="1" E3_4="A" E3_5="%s" E3_6="%s" E3_8="%d" '
                 'E3_9="%d" E3_14="%d" E3_15="%d" E3_16="0" E3_19="0" E3_21="0"/>'
                 % (perioada, perioada, brute, b4base, imp, imp))
        a.append('  </asigurat>')
        AS.append("\n".join(a))
    n = len(salariati)
    # round() Python (bancar) se aplica ICI, INAINTE ca _d112int() sa poata
    # rotunji aritmetic - 112.5 devenea deja 112 prin round() inainte sa ajunga
    # la _d112int. Eliminat round() exterior, _d112int face rotunjirea corecta.
    cam_total = _d112int(sum_bazac * 0.0225)
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
             'totalPlata_A="%d">' % (cui_f, caen_f, _d112esc(_t(den_f)), casa_ang, total_plata))
    # angajatorA ("sectiunea Creante" in mesajul validatorului; tag-ul real e
    # "angajatorA"). ANAF structura D112 0126_030226 (structura_D112_0126_030226.pdf,
    # confirmat prin lista completa de elemente <angajatorX>) o pozitioneaza
    # PRIMA, inaintea lui angajatorB - nu dupa cum presupusesem gresit prima
    # data (mutand-o dupa C4 a produs aceeasi eroare "gresit pozitionata",
    # semn ca directia era inversa). Codurile (602/412/432/480/458/459) erau
    # deja corecte in add_oblig() - problema era doar pozitia in XML.
    H.extend(A)
    H.append('    <angajatorB B_cnp="%d" B_sanatate="%d" B_pensie="%d" B_brutSalarii="%d" B_sal="%d"/>'
             % (n, n, n, sum_bazac, n))
    H.append('    <angajatorC1 C1_11="%d" C1_12="%d" C1_T1="%d" C1_T2="%d" C1_T="0"/>' % (sum_bazac, c1_12, sum_bazac, c1_12))
    _C2_RD1 = ("01", "02", "03", "04", "05", "06", "12", "13", "14", "16", "51")
    def _c2row(coduri):
        _f = [c for c in _c2_cazuri if c[0] in coduri]
        return (len(_f), sum(c[1] for c in _f), sum(c[2] for c in _f), sum(c[3] for c in _f),
                sum(c[4] for c in _f), sum(c[5] for c in _f))  # count, d16, d14, d15, d20, d21
    if _c2_cazuri:
        _r1 = _c2row(_C2_RD1); _r2 = _c2row(("10", "11")); _r3 = _c2row(("08",))
        _r4 = _c2row(("09", "91", "92")); _r41 = _c2row(("17",)); _r5 = _c2row(("15",))
        _c2a = ['C2_11="%d" C2_12="%d" C2_13="%d" C2_14="%d" C2_15="%d" C2_16="%d"' % _r1[:6]]
        if _r2[0]:
            _c2a.append('C2_21="%d" C2_22="%d" C2_23="%d" C2_24="%d" C2_25="%d" C2_26="%d"' % _r2[:6])
        if _r3[0]:  # Rd.3 sarcina/lauzie: doar FNUASS (fara angajator)
            _c2a.append('C2_31="%d" C2_32="%d" C2_34="%d" C2_36="%d"' % (_r3[0], _r3[1], _r3[3], _r3[5]))
        if _r4[0]:  # Rd.4 ingrijire copil
            _c2a.append('C2_41="%d" C2_42="%d" C2_44="%d" C2_46="%d"' % (_r4[0], _r4[1], _r4[3], _r4[5]))
        if _r41[0]:  # Rd.4.1 ingrijire pacient oncologic (cod 17)
            _c2a.append('C2_41a="%d" C2_42a="%d" C2_44a="%d" C2_46a="%d"' % (_r41[0], _r41[1], _r41[3], _r41[5]))
        if _r5[0]:  # Rd.5 risc maternal
            _c2a.append('C2_51="%d" C2_52="%d" C2_54="%d" C2_56="%d"' % (_r5[0], _r5[1], _r5[3], _r5[5]))
        _c2t6 = _r1[5] + _r2[5] + _r3[5] + _r4[5] + _r41[5] + _r5[5]  # C2_16+26+36+46+56 (sume FNUASS)
        _c2a.append('C2_T6="%d" C2_10="%d" C2_140="%d"' % (_c2t6, _c2t6, _c2t6))
        H.append('    <angajatorC2 %s/>' % " ".join(_c2a))
    H.append('    <angajatorC4 C4_baza="%d" C4_ct="%d"/>' % (sum_bazac, cam_total))
    H.append('  </angajator>')
    H.extend(AS)
    H.append('</declaratieUnica>')
    av.append("D112: %d salariati - impozit %s, CAS %s, CASS %s, CAM %s lei (luna %d/%d)."
              % (n, bani(sum_imp), bani(sum_cas), bani(sum_cass), bani(cam_total), luna, an))
    return ("\n".join(H), av)


# Coloanele din `salariati` pe care D112 le CITESTE efectiv (vezi maparea de la finalul
# lui pull). Lista e un CONTRACT cu schema: daca una dispare, generarea se opreste zgomotos
# in loc sa declare zero.
_COLOANE_SALARIAT = ("id", "nume", "prenume", "cnp", "data_angajare", "salariu_brut",
                     "ore_zi", "judet_casa", "part_time", "persoane_intretinere",
                     "scutit_contrib_minim", "motiv_exceptare", "tichet_masa_valoare", "data_incetare")


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        prof = dict(cur.fetchone() or {})
        from datetime import date as _dsal
        cur.execute(f"SELECT * FROM {schema}.salariati WHERE (data_incetare IS NULL OR data_incetare >= %s) ORDER BY id",
                    (_dsal(an, luna, 1),))
        sal = [dict(r) for r in cur.fetchall()]
        # GARDA COLOANE (27.07.2026): SELECT * nu crapa cand o coloana dispare din schema -
        # randul iese fara cheia aceea, s.get() da None, iar None e absenta legitima ->
        # valoarea devine TACIT 0. Dovedit: cu salariu_brut redenumita, D112 emitea o
        # declaratie cu salarii ZERO, fara niciun semnal.
        # Pe CURSOR, nu pe randuri: asa prinde si firma FARA salariati (tabela goala are
        # cur.description complet). Verificam PREZENTA coloanei; valoarea 0 ramane legitima
        # (salariat in concediu medical toata luna).
        cere_coloane_cursor(cur, _COLOANE_SALARIAT, "salariati")
        cur.execute(f"""SELECT * FROM {schema}.concedii_medicale
                        WHERE an=%s AND luna=%s""", (an, luna))
        cms = [dict(r) for r in cur.fetchall()]
    # [F133 Faza 2a] tichete de vacanta acordate in luna (one-off, din beneficii_lunare)
    vac_luna = _ben.lista_luna(conn, schema, an, luna, "vacanta")
    cult_luna = _ben.lista_luna(conn, schema, an, luna, "cultural")  # [tichete culturale]
    pe_sal = {}
    for c in cms:
        pe_sal.setdefault(c["salariat_id"], []).append({
            "serie": c.get("serie"), "numar": c.get("numar"),
            "da": _d112_data(str(c.get("data_acordare") or "")),
            "di": _d112_data(str(c.get("data_inceput") or "")),
            "ds": _d112_data(str(c.get("data_sfarsit") or "")),
            "cod": c.get("cod") or "01",
            "cod_urgenta": c.get("cod_urgenta"),
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
            "id": s.get("id"),
            "nume": s.get("nume"), "prenume": s.get("prenume") or "-",
            "cnp": s.get("cnp"), "brut": s.get("salariu_brut"),
            "data_angajare": str(s.get("data_angajare") or ""),
            "data_incetare": s.get("data_incetare"),
            "ore_zi": s.get("ore_zi") or 8,
            "judet_casa": s.get("judet"),
            "part_time": bool(s.get("part_time")),
            "persoane_intretinere": s.get("persoane_intretinere") or 0,
            "scutit_pt": bool(s.get("scutit_contrib_minim")),
            "scutit": bool(s.get("scutit_contrib_minim")),
            "motiv_exceptare": s.get("motiv_exceptare"),
            "tichet_masa_valoare": s.get("tichet_masa_valoare") or 0,  # [F133]
            "tichet_vacanta": vac_luna.get(s["id"], 0),  # [F133 Faza 2a]
            "tichet_cultural": cult_luna.get(s["id"], 0),  # [tichete culturale] impozit only, NU in baza CASS
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
    nzl = _nzl(an, luna)  # zile lucratoare fara sarbatori (OUG 158 art.10)
    # ALINIERE la stat_plata_api:36-38 (15.07.2026). pull() chema calcul_salariu(brut,
    # la_data) GOL: fara persoane / norma_intreaga / venit_brut_total, si pe brutul
    # INTREG, nu pe cel lucrat. Statul de plata le paseaza pe toate patru -> acelasi
    # salariat primea deducere personala, facilitate si plafon DIFERITE in D112 fata de
    # fluturas. Sursa unica de adevar: statul de plata (stat_plata_api).
    #  - persoane: deducerea personala (art. 77) reduce impozitul declarat
    #  - norma_intreaga: facilitatea (HG 146/2026 o da doar la norma intreaga)
    #  - venit_brut_total: plafonul facilitatii se judeca pe brutul CONTRACTUAL
    #  - brut_lucrat: pe zilele de CM salariul nu se plateste de angajator
    from core import salariu_istoric as _si  # [tranzitie 29.07.2026] salariul contractual DATE-AWARE, nu salariati.salariu_brut
    _ultima_luna = _dt(an, luna, _cal.monthrange(an, luna)[1])
    _cs_sal = conn.cursor()
    for s in salariati:
        _sal_luna = float(_si.salariu_la(_cs_sal, schema, s["id"], _ultima_luna) or 0)
        _zlm, _zll = _si.zile_la_minim(_cs_sal, schema, s["id"], an, luna, s.get("data_angajare"), s.get("data_incetare"))
        _fac_prorata = (_zlm / _zll) if _zll else 0.0  # lit.a): fractia de zile ACTIVE si LA MINIM
        brut_int = _sal_luna
        zile_cm_s = int(s.get("zile_cm") or 0)
        brut_lucrat = (brut_int * max(nzl - zile_cm_s, 0) / nzl) if (nzl and zile_cm_s) else brut_int
        # [D2 02.08] tichete pe zile EFECTIV lucrate (HG 1045/2018 art.10(3)): nzl - CM - CO/deleg/absente/invoire (pontaj)
        # [D2/cap.23] tichetele cer pontaj CONFIRMAT
        if float(s.get("tichet_masa_valoare") or 0) > 0 and not _per.e_confirmat(conn, schema, an, luna, "pontaj")["confirmat"]:
            raise _per.PerioadaNeconfirmata("Tichetele de masa (D112)", an, luna, "pontaj", "HG 1045/2018 art.10(3)")
        _fara_t = _pontaj.zile_fara_tichet(conn, schema, s["id"], an, luna) if float(s.get("tichet_masa_valoare") or 0) > 0 else 0
        tichet_zile = max(nzl - zile_cm_s - _fara_t, 0)
        # [D3 02.08] exces tichete vacanta peste plafonul ANUAL (6 sm) -> venit salarial in brut (cumulat an)
        _vac_l = float(s.get("tichet_vacanta") or 0)
        _plaf_van = 6.0 * float(sm)
        _cum_c = float(_ben.total_an(conn, schema, s["id"], an, "vacanta", pana_luna=luna) or 0)
        _cum_a = float(_ben.total_an(conn, schema, s["id"], an, "vacanta", pana_luna=luna - 1) or 0) if luna > 1 else 0.0
        _exces_van = _ben.exces_vacanta_luna(_cum_c, _cum_a, _plaf_van)
        r = _sz.calcul_salariu(brut_lucrat,
                               persoane=s.get("persoane_intretinere") or 0,
                               la_data=ref,
                               norma_intreaga=not s.get("part_time"),
                               venit_brut_total=brut_int,
                               data_angajare=s.get("data_angajare"),
                               data_incetare=s.get("data_incetare"),
                               facilitate_prorata=_fac_prorata,
                               tichet_valoare=float(s.get("tichet_masa_valoare") or 0),
                               tichet_zile=tichet_zile,
                               tichet_vacanta=max(_vac_l - _exces_van, 0.0),
                               tichet_vacanta_exces=_exces_van,
                               tichet_cultural=float(s.get("tichet_cultural") or 0))
        s["brut_lucrat"] = brut_lucrat   # consumat de salarii_contare (o singura cifra)
        s["facilitate"] = r.get("facilitate", 0)
        s["cas"] = r.get("cas", 0)
        s["cass"] = r.get("cass", 0)
        s["exces_vacanta"] = _exces_van   # [D3] intra in brutul declarat (B4 base)
        s["impozit"] = r.get("impozit", 0)          # TOTAL (salariu + tichete)
        s["deducere"] = (r.get("deducere") or {}).get("total", 0)
        s["cass_tichete"] = r.get("cass_tichete", 0)        # [F133] CASS pe tichete
        s["impozit_tichete"] = r.get("impozit_tichete", 0)  # impozit pe tichete
        # [F133] baza CASS D112 = valoarea TOTALA a biletelor (masa + vacanta)
        s["tichete_nominal"] = r.get("tichete_nominal", 0) + r.get("tichete_vacanta", 0)
        # part-time supra-taxare (art. 146(5^6)/168(6^1) CF, structura D112 v7):
        # part_time = ROUND(prag_pt * zile_lucrate / NZL); daca 0 < baza < part_time
        # -> B4_*P la prag, diferenta pe angajator. Exceptati: scutit+motiv 1-5.
        zile_lucr = max(nzl - int(s.get("zile_cm") or 0), 0)
        baza = _sal_luna  # [tranzitie] date-aware, nu salariati.salariu_brut
        scutit = bool(s.get("scutit_pt"))
        prag_zile = round(prag_pt * zile_lucr / nzl) if nzl else 0
        if not scutit and 0 < baza < prag_zile:
            s["pt_aplica"] = True
            s["baza_minim_pt"] = prag_zile
            s["cas_min_pt"] = round(prag_zile * 0.25)
            s["cass_min_pt"] = round(prag_zile * 0.10)
        else:
            s["pt_aplica"] = False
    _cs_sal.close()
    return prof, salariati


def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    if not str(prof.get("cui") or "").strip():
        erori.append("LIPSA CUI firma.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSA denumire firma.")
    return erori


def genereaza(conn, schema, an, luna):
    prof, salariati = pull(conn, schema, an, luna)
    _er = erori_generare(prof)
    if _er:
        raise ValueError("D112 nu se poate genera: " + " ".join(_er))
    return _d112_genereaza(prof, salariati, an, luna)
