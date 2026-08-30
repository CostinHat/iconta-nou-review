# -*- coding: utf-8 -*-
"""D112 - generator VALIDAT DUKIntegrator (portat din monolit /opt/iconta 04.07.2026).
Include CM: asiguratB3 + asiguratD + angajatorC2 (OUG 158/2005).
pull() citeste salariati + concedii_medicale din schema tenantului."""

from core.common import text_anaf as _t, cere_coloane_cursor, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp (03.08.2026)
from dataclasses import dataclass, field
import re
from core import scadente as _scad
from core import pontaj as _pontaj
from core import perioada as _per
from core import beneficii_api as _ben
from core.pdf_util import bani
import os as _os
from core.identitate import valideaza_cnp as _vcnp_id, valideaza_cui as _vcui_id  # T1: checksum CUI/CNP pre-DUK (read-only)

_D112_XSD = _os.path.join(_os.path.dirname(__file__), "..", "anaf_surse", "d112_06082026.xsd")
_ENUM_XSD_CACHE = {}
from core import nomenclator_cm as _ncm


@dataclass
class ObligatieD112:
    """Un rand `angajatorA` — creanta care pleaca la buget. Aceeasi forma ca la D100."""
    cod_oblig: str
    cod_bugetar: str
    datorat: int


@dataclass
class AsiguratD112:
    """Contributiile UNUI asigurat, exact cifrele care intra in XML pentru el.

    CNP-ul NU e aici, si e o alegere: componentele cerute de lista 5 raspund la „din ce e facuta
    cifra", iar CNP-ul nu compune nicio suma. Iar `coada_api.randuri_din_res` serializeaza obiectul
    asta in `public.declaratii_depuse.randuri` — deci ce se pune aici se si PASTREAZA. LIMITA
    DECLARATA: cine cauta asiguratul dupa CNP nu-l gaseste din componente; il gaseste in statul de
    plata, unde ii e locul.
    """
    nume: str
    brut: int
    baza_cas: int
    cas: int
    cass: int
    impozit: int


@dataclass
class RezultatD112:
    """[R105, 30.08.2026] Obiectul de rezultat pe care D112 nu l-a avut niciodata.

    DE CE ACUM. Pana azi `_d112_genereaza` intorcea `(xml, avertismente)` — un sir si o lista de
    texte. Consecinta masurata la 1c: din cele noua declaratii, D112 era SINGURA care nu-si putea
    desface cifra, fiindca nu exista nimic structurat de citit; pozitiile se scriau in XML si nu mai
    existau nicaieri dupa aceea.

    DECIZIA CARE SE ANULEAZA, cu locul ei: `coada_api.randuri_din_res` scria, din 22.07.2026, ca
    refactorizarea „e o decizie de arhitectura pe modulul validat DUK (F181), NU se face aici".
    Amanarea era corecta atunci — avea si conditie, si loc. Costin a dat decizia pe 30.08.2026:
    *„R105: motorul se schimba."* Deci nu se ocoleste, se schimba.

    DOUA EFECTE care nu sunt evidente si se scriu:
      1. `main.py` citea `getattr(res, "avertismente", None)` — pe o LISTA, asta da `None`. Deci
         avertismentele D112 se calculau si **se aruncau**. De acum ajung la contabil.
      2. `randuri_din_res` intoarce `None` pe ce nu e dataclass. De acum D112 isi persista randurile
         in `public.declaratii_depuse.randuri`, ca celelalte.
    """
    an: int
    luna: int
    prof: dict = field(default_factory=dict)
    obligatii: list = field(default_factory=list)
    asigurati: list = field(default_factory=list)
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def _cod_boala_acceptat(cod):
    """Poarta pe care o probeaza garda `core/test_cod_boala_nomenclator.py`. Sursa e NOMENCLATORUL,
    nu enumerarea XSD - vezi motivul la locul folosirii."""
    return _ncm.accepta(cod)


def _enum_xsd(tip):
    """Valorile enumerate ale unui xs:simpleType din XSD-ul D112 (anaf_surse/d112_06082026.xsd,
    autoritatea in-repo pt nomenclatoarele inchise). Extrage <xs:enumeration value=...> din blocul
    simpleType; cache la prima citire. La lipsa fisierului intoarce set gol (caller-ul cade pe fallback)."""
    if tip in _ENUM_XSD_CACHE:
        return _ENUM_XSD_CACHE[tip]
    vals = set()
    try:
        with open(_D112_XSD, encoding="utf-8") as _f:
            _txt = _f.read()
        _m = re.search(r'<xs:simpleType name="%s">(.*?)</xs:simpleType>' % re.escape(tip), _txt, re.S)
        if _m:
            vals = set(re.findall(r'<xs:enumeration value="([^"]*)"', _m.group(1)))
    except Exception:
        vals = set()
    _ENUM_XSD_CACHE[tip] = vals
    return vals

def caen_in_nomenclator(caen):
    """[Q1] True daca CAEN-ul e acceptat de D112 (enumerare inchisa Str_caenListSType). Gol/'0000' ->
    True (lipsa CAEN e camp obligatoriu, alt tip de problema, nu 'prezent-dar-invalid'). Folosit de
    ecranul Date firma ca sa NU pretinda 'toate declaratiile se pot genera' cand CAEN-ul ar face D112
    respins de ANAF. Aceeasi regula ca poarta din genereaza - o singura sursa a nomenclatorului."""
    caen_f = str(caen or "").strip()
    if not caen_f or caen_f == "0000":
        return True
    _caene = _enum_xsd("Str_caenListSType")
    return (caen_f in _caene) if _caene else (len(caen_f) == 4 and caen_f not in ("0000", "9999"))

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
    from core.common import salariu_minim_luna
    valoare, _temei = salariu_minim_luna(_date(an, luna, 1))  # [#12] art.77(3): cea mai mica din luna
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
    media = round(d17 / d18, 2) if d18 else 0.0  # round-ok: medie (rație), nu suma persistata
    return round(d17, 2), d18, media  # round-ok: d17 = suma de brute deja la 2 zecimale (no-op)
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
    # [baze contributii] cotele salariale PERIOD-AWARE din COTE (nu literale): CAS CF art.138, CASS art.156,
    # impozit art.78, CAM art.220^3 (cota 2.25%). Valori 25/10/10/2.25% verificate la sursa (anaf_surse/cod_fiscal).
    from core.common import cota as _cota112
    _cota_cas = float(_cota112("cas", ref)[0]); _cota_cass = float(_cota112("cass", ref)[0])
    _cota_imp = float(_cota112("impozit_venit", ref)[0]); _cota_cam = float(_cota112("cam", ref)[0])
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
    nume_d = _t(prof.get("declarant_nume") or den_f or "ADMINISTRATOR", _LIM["d112"]["nume_declar"])
    pren_d = _t(prof.get("declarant_prenume") or "-", _LIM["d112"]["prenume_declar"])
    func_d = _t(prof.get("declarant_functie") or "ADMINISTRATOR", _LIM["d112"]["functie_declar"])   # structura D112: functie_declar C(50)
    if not (prof.get("declarant_nume") and prof.get("declarant_functie")):
        av.append("D112: declarantul (nume/funcție) lipsește din profil -> emis implicit "
                  "\"ADMINISTRATOR\". Completează declarantul în Date firma.")
    if not cui_f:
        av.append("CUI firmă lipsă — completează Profil firmă.")
    if caen_f == "0000":
        av.append("CAEN firmă lipsă/invalid — D112 cere CAEN valid în Profil firmă.")
    # [T1 identitate firma, 10.08.2026] CUI prezent-dar-invalid (cifra de control / lungime) pleca TACIT ->
    # DUK "CUI invalid". Pre-validam cu core.identitate.valideaza_cui (checksum offline). Golul ramane
    # avertisment / poarta erori_generare; blocam doar valoarea PREZENTA si gresita.
    if cui_f:
        _ok_cui, _mot_cui = _vcui_id(cui_f)
        if not _ok_cui:
            raise ValueError(
                "D112: CUI firmă %s invalid (%s) — se corectează în Profil firmă (ecran Date firmă), "
                "nu se emite D112 respins de DUK." % (cui_f, _mot_cui))
    # [caen out-of-enum, 10.08.2026] CAEN prezent-dar-neenumerat (ex '9999') pleca TACIT -> XSD reject
    # (caen type=Str_caenListSType, enumerare INCHISA in d112_06082026.xsd). '0000' = LIPSA (avertisment
    # mai sus). Validam contra enumerarii din XSD (autoritatea in-repo); fallback pe forma daca XSD lipseste.
    if caen_f != "0000":
        _caene = _enum_xsd("Str_caenListSType")
        _caen_ok = (caen_f in _caene) if _caene else (len(caen_f) == 4 and caen_f not in ("0000", "9999"))
        if not _caen_ok:
            raise ValueError(
                "Codul CAEN al firmei, '%s', nu e în nomenclatorul CAEN pe care îl acceptă D112. "
                "Corectează-l în Profil firmă — un D112 trimis cu el ar fi respins de ANAF." % caen_f)
    sum_imp = sum_cas = sum_cass = sum_bazac = 0
    cas_ang_dif = cass_ang_dif = 0  # d112_b4p_v2
    _c2_cazuri = []  # [D112 C2 pe rand] (cod, d16, d14=za, d15=zf, d20, d21) per certificat
    c1_12 = 0
    AS = []
    asigurati = []   # [R105] componentele, stranse in acelasi loc in care se scrie XML-ul
    idx = 0
    for s in salariati:
        idx += 1
        # [T1 CNP angajat + numeAsig/dataAng obligatorii, 10.08.2026] Passthrough per-salariat: CNP gresit
        # (lungime/format/leading-zero/alpha = XSD CnpSType pattern; cifra de control = DUK), numeAsig gol
        # (DUK: vid nepermis) sau data_angajare NULL (dataAng lipsa, XSD) plecau TACIT la ANAF. Refuz la
        # radacina care NUMESTE salariatul - aceeasi clasa ca hard-block-ul D_8/asiguratD (nu se trunchiaza).
        _cnp_s = str(s.get("cnp") or "").strip()
        _nume_s = str(s.get("nume") or "").strip()
        _ok_cnp, _mot_cnp = _vcnp_id(_cnp_s)
        if not _ok_cnp:
            raise ValueError(
                "D112: salariatul %s (CNP %s) are CNP invalid (%s) - se corectează în fisa salariatului, "
                "nu se emite D112 invalid." % (_nume_s or "(nume necompletat)", _cnp_s or "(gol)", _mot_cnp))
        if not _nume_s:
            raise ValueError(
                "D112: salariatul cu CNP %s are numeAsig gol - numele e obligatoriu (DUK: vid nepermis). "
                "Completează-l în fisa salariatului, nu se emite D112 invalid." % _cnp_s)
        if not str(s.get("data_angajare") or "").strip():
            raise ValueError(
                "D112: salariatul %s (CNP %s) are data_angajare necompletată - dataAng e obligatoriu în "
                "D112 (XSD). Completeaz-o în fisa salariatului, nu se emite D112 invalid." % (_nume_s, _cnp_s))
        brut = _d112int(s.get("brut")) + _d112int(s.get("exces_vacanta", 0)) + _d112int(s.get("e83_cadou", 0))  # [D3] exces vacanta + [cadou 16.08] cadou taxabil in brutul declarat (S731)
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
            # [d112_cm_baza_realizata_v1, 05.08.2026] CF art.139(1): baza CAS/CASS = castigul brut REALIZAT din
            # salarii; in luna cu concediu medical salariul realizat = zile LUCRATE (brut_lucrat), NU brutul
            # contractual (care ramane informativ in B1_sal1/B4_3). Structura D112: B4_7=B2_5+B3_7 (baza salariala
            # REALIZATA + baza indemnizatiei CM, aditive; B4_8=ROUND(B4_7*25%)). Fara asta B2_5/B4_7/B4_5/B4_14
            # emiteau brutul INTREG = supra-declarare CAS/CASS/CAM la ANAF + divergenta fata de fluturas
            # (calcul_salariu pe brut_lucrat). Gard: test_pull_declaratii.
            # test_d112_cm_baza_salariala_realizata_nu_brut_intreg. (Rotunjirea Sigma(round) vs round(total) = 2b,
            # datorie separata in GARZI 05.08 - neatinsa aici.)
            bazac = _d112int(s.get("brut_lucrat", s.get("brut"))) + _d112int(s.get("exces_vacanta", 0)) + _d112int(s.get("e83_cadou", 0)) - facil
            if bazac < 0:
                bazac = 0
            zile = nzl - zile_cm
            if zile < 0:
                zile = 0
            # [d112_cm_suma_din_media_v1, 10.08.2026] Indemnizatia CM (D_20/D_21 = brut angajator/FNUASS)
            # se ia din certificatul stocat (salariati_api.salveaza_concediu o calculeaza cu
            # salarizare.calcul_cm). DAR d112 RECALCULEAZA deja media pe 6 luni (D_17/D_18/D_19 via
            # _cm_media6) la generare: un certificat cu media>0 si zile>0 dar brut_ang=brut_fnuass=0
            # (stocare incompleta) producea XML AUTO-CONTRADICTORIU (media X lei/zi x N zile, dar
            # indemnizatie 0) -> DUKIntegrator V47/V52 ('baza CAS ptr indemnizatii OUG158=0 si exista
            # zile prestatii<>0'; spec anaf_surse/d112_struct_anaf.txt asiguratB3 B3_7: 'ERR daca B3_7=0
            # si B3_6>0'). Completam suma DOAR cand lipseste, din ACEEASI formula OUG 158/2005 art.17
            # (Ci = media_zilnica x procent x zile), cu procentul canonic salarizare.procent_cm si
            # split-ul angajator/FNUASS stocat (za/zf). Certificatele cu suma stocata (fluxul de salvare)
            # raman NEATINSE (productia neschimbata). GARD: test_pull_declaratii.
            # test_d112_cm_suma_lipsa_din_stocare_recalc_din_media.
            for _c in cms:
                if _d112int(_c.get("brut_ang")) or _d112int(_c.get("brut_fnuass")):
                    continue
                _za = int(_c.get("zile_ang") or 0); _zf = int(_c.get("zile_fnuass") or 0)
                if _za + _zf <= 0:
                    continue
                _mm17, _mm18, _mmedia = _cm_media6(_c.get("baza"), s.get("data_angajare"), an, luna)
                if _mmedia <= 0:
                    continue
                _pct = float(_sz.procent_cm(str(_c.get("cod") or "01").zfill(2), _za + _zf, la_data=ref))
                _c["brut_ang"] = _d112int(_mmedia * _pct * _za)
                _c["brut_fnuass"] = _d112int(_mmedia * _pct * _zf)
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
            cm_base_imp = 0   # [impozit CF art.62 lit.c] baza CM IMPOZABILA (exclude 08/09/15/17/91/92 - salarizare._CM_COD_NEIMPOZABIL)
            cm_cas_imp = 0    # [impozit] CAS pe CM impozabila (simetrie scazaminte - vezi bimp)
            cm_cass_imp = 0   # [impozit] CASS pe CM impozabila
            for _x in cms:
                _cod = str(_x.get("cod") or "01").zfill(2)
                _xb = _d112int(_x.get("brut_ang")) + _d112int(_x.get("brut_fnuass"))
                _xt = _sz.taxe_cm(_xb, _cod, la_data=ref)
                _xcas = _d112int(_xt["cas"]); _xcass = _d112int(_xt["cass"])
                cm_cas += _xcas
                cm_cass += _xcass
                if _xcass > 0:
                    cm_cass_base += _xb
                if _cod not in _sz._CM_COD_NEIMPOZABIL:   # indemnizatie IMPOZABILA -> intra in baza impozit + scazamintele ei
                    cm_base_imp += _xb
                    cm_cas_imp += _xcas
                    cm_cass_imp += _xcass
                _cza = int(_x.get("zile_ang") or 0); _czf = int(_x.get("zile_fnuass") or 0)
                _c2_cazuri.append((str(_x.get("cod") or "01").zfill(2), _cza + _czf, _cza, _czf,
                                   _d112int(_x.get("brut_ang")), _d112int(_x.get("brut_fnuass"))))
            cas = _d112int(bazac * _cota_cas) + cm_cas
            cass = _d112int(bazac * _cota_cass) + cm_cass
            cass_base_cm = bazac + cm_cass_base
            ded = float(s.get("deducere") or 0)
            # [impozit CM, CF art.62 lit.c] indemnizatiile de maternitate(08)/ingrijire copil(09/91/92)/risc maternal(15)/
            # oncologic(17) sunt NEIMPOZABILE. Baza impozit = salariu REALIZAT + CM IMPOZABILA; se scad DOAR CAS/CASS pe
            # partea IMPOZABILA (SIMETRIE - altfel CAS 25% pe indemnizatia neimpozabila ar cobori bimp = sub-declarare).
            # cas/cass EMISE (B4_8/B4_6) raman pe TOATE codurile (CAS art.139(1)(o) uniform); doar baza impozit exclude.
            _cas_imp = _d112int(bazac * _cota_cas) + cm_cas_imp
            _cass_imp = _d112int(bazac * _cota_cass) + cm_cass_imp
            bimp = (bazac + cm_base_imp) - _cas_imp - _cass_imp - ded
            if bimp < 0:
                bimp = 0
            imp = _d112int(bimp * _cota_imp)
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
                d19 = round(d17 / d18, 2) if d18 else 0  # round-ok: medie (rație)
                # [d112 asiguratD zero-base v1] D_1/D_2/D_5/D_6/D_7 sunt use="required" in AsiguratDType
                # (d112_06082026.xsd l.665-671; struct rd.90-96 D_1..D_7). Un certificat cu vreunul gol =>
                # XML respins de ANAF ("D_1: atributul trebuie sa exista"). REFUZ pe gol la radacina (aceeasi
                # clasa ca hard-block-ul D_8 de mai jos si ca D205 cifR): nu se emite D112 invalid. Campurile
                # NU se mai omit (comportamentul vechi masca certificatele corupte).
                _obl = (("D_1", "serie certificat", _d112esc(x.get("serie"))),
                        ("D_2", "număr certificat", _d112esc(x.get("numar"))),
                        ("D_5", "data acordarii", x.get("da") or ""),
                        ("D_6", "data început valabilitate", x.get("di") or ""),
                        ("D_7", "data incetare", x.get("ds") or ""))
                _lipsa = ["%s (%s)" % (_a, _lbl) for _a, _lbl, _v in _obl if not str(_v).strip()]
                if _lipsa:
                    raise ValueError(
                        "D112: certificatul de concediu medical (salariat CNP %s) are câmpuri obligatorii goale: %s. "
                        "AsiguratDType le cere use=required în d112_06082026.xsd - un XML cu ele goale e respins de "
                        "ANAF. Completează-le în certificat (ecran Concedii medicale) - nu se emite D112 invalid."
                        % (s.get("cnp"), ", ".join(_lipsa)))
                # [cod boala D_9, sursa = NOMENCLATORUL 9, 22.08.2026] Pana azi se valida contra
                # enumerarii din XSD ('01'..'15'), cu fallback pe un interval GHICIT (1..15) cand
                # XSD-ul nu se putea citi. Amandoua erau gresite: XSD-ul e mai INGUST decat
                # validatorul insusi. Probat la arbitru pe declaratie generata - D_9=91 iese VALID,
                # iar 51 si 17 primesc reguli de FOND (S101.1, S97), deci sunt coduri cunoscute.
                # Efectul de pana azi: un certificat cu cod 16/17/51/91 - coduri legale, pe care
                # ecranul le OFERA - bloca depunerea D112, cu motivul fals „nu e in nomenclator".
                # Vezi core/nomenclator_cm.py si registru_interpretari:nomenclator_cm_sursa.
                _cod_b = _ncm.normalizeaza(x.get("cod") or "01")
                if not _cod_boala_acceptat(_cod_b):
                    raise ValueError(
                        "Certificatul de concediu medical al salariatului cu CNP %s are codul de "
                        "indemnizație '%s', care nu există în Nomenclatorul 9 (coduri 01-17, plus "
                        "51, 91, 92). Corectează codul în certificat (ecran Concedii medicale) — "
                        "un D112 trimis cu el ar fi respins." % (s.get("cnp"), _cod_b))
                # [T6 passthrough NETRUNCHIAT, 10.08.2026] serie(D_1)/numar(D_2)/diagnostic(D_23) sunt
                # identificatori de certificat - NU se trunchiaza tacit (spre deosebire de nume/den prin _t):
                # o serie/numar trunchiat = alt certificat la ANAF. Overflow lungime (XSD Str5/Str10/Str3)
                # -> hard-block care numeste campul + limita. (Golul e deja blocat mai sus.)
                _diag = "RM" if _cod_b == "15" else str(x.get("diagnostic") or "999")
                _t6 = (("D_1 (serie)", str(x.get("serie") or ""), 5),
                       ("D_2 (număr)", str(x.get("numar") or ""), 10),
                       ("D_23 (diagnostic)", _diag, 3))
                _ovf = ["%s = %d caractere (max %d)" % (_lbl, len(_v), _lim) for _lbl, _v, _lim in _t6 if len(_v) > _lim]
                if _ovf:
                    raise ValueError(
                        "D112: certificatul de concediu medical (salariat CNP %s) are câmpuri care depășesc "
                        "lungimea maximă XSD: %s - se corectează în certificat (ecran Concedii medicale); "
                        "identificatorii de certificat NU se trunchiază tacit, nu se emite D112 invalid."
                        % (s.get("cnp"), ", ".join(_ovf)))
                _opt = ""
                for _a, _lbl, _v in _obl:
                    _opt += ' %s="%s"' % (_a, _v)
                if str(x.get("cod") or "01").zfill(2) == "06" and x.get("cod_urgenta"):
                    _opt += ' D_11="%d"' % int(x.get("cod_urgenta"))  # [D_11] cod urgenta HG 423/2020, oblig. la cod 06 (D112 C(3), mutex D_12)
                if str(x.get("cod") or "01").zfill(2) == "10" and x.get("cod_urgenta"):
                    _opt += ' D_13="%d"' % int(x.get("cod_urgenta"))  # [cod10] nr aviz medic expert (art.19 OUG 158/2005, regula DUK S102); reutilizeaza cod_urgenta
                # [D_8/D_8a, regula DUK S97] cod 09/91/92 cer CNP copil (D_8), cod 17 cere CNP pacient oncologic
                # (D_8a) - N(13), verificare CNP. Lipsa/invalid -> HARD-BLOCK (regula bazei nule): nu se emite
                # D112 invalid, se semnaleaza. Certificatele existente fara CNP opresc generarea explicit.
                _cod_c = str(x.get("cod") or "01").zfill(2)
                if _cod_c in ("09", "91", "92", "17"):
                    from core.salariati_import_api import valideaza_cnp as _vcnp
                    _cnp_i = str(x.get("cnp_ingrijit") or "").strip()
                    _ok_c, _mot_c = _vcnp(_cnp_i)
                    if not _ok_c:
                        _camp = "D_8a (CNP pacient oncologic)" if _cod_c == "17" else "D_8 (CNP copil)"
                        raise ValueError(
                            "D112: certificatul de concediu medical cod %s (salariat CNP %s) cere %s conform "
                            "regulii DUK S97, dar CNP-ul persoanei îngrijite lipsește sau e invalid (%s). "
                            "Completează-l în certificat (ecran Concedii medicale) - nu se emite D112 invalid."
                            % (_cod_c, s.get("cnp"), _camp, _mot_c))
                    _opt += (' D_8a="%s"' if _cod_c == "17" else ' D_8="%s"') % _cnp_i
                # [d112 v1.03-072026] Ordin comun 605/95/928/2314/2026 (D112_A7.2.6 v7, se aplica din 07/2026):
                # D_14a/D_15a = "Zile prestatii (zile lucratoare) suportate de angajator/FNUASS"
                # (structura_D112_0726_030826.pdf rd.103a/104a); D_16a = D_14a+D_15a (rd.105a, formula VERBATIM).
                # Zilele-prestatii = za/zf (exact ce statea deja in D_14/D_15). D_14/D_15/D_16 raman "14.1/15.1/16.1
                # din care zile platite" (regula D_14<=D_14a, D_15<=D_15a; aplicatia n-are distinctie platit-vs-
                # prestatii pe zile CM => egale). Restul campurilor 07/2026 (D_20a/D_21a/C2_155/C2_156/E2_156/
                # B3_7D/C_10D/D_9a/D_9b/E3_97) = datorie GARZI (fara formula verbatim sau fara date in aplicatie).
                _da = ""
                if (an, luna) >= (2026, 7):
                    _da = ' D_14a="%d" D_15a="%d" D_16a="%d"' % (za, zf, d16)
                    if x.get("program_national"):  # [D_9a] N(1): =1 pt CM acordate pacientilor inclusi in programe nationale de sanatate
                        _da += ' D_9a="1"'
                _dl.append('    <asiguratD%s D_9="%s" D_10="%d" '
                           'D_14="%d" D_15="%d" D_16="%d"%s D_17="%d" D_18="%d" D_19="%.2f" D_20="%d" D_21="%d" D_23="%s"/>'
                           % (_opt, (x.get("cod") or "01"), int(x.get("loc_prescriere") or 1),
                              za, zf, d16, _da, d17, d18, d19, d20, d21,
                              _d112esc("RM" if _cod_c == "15" else (x.get("diagnostic") or "999"))))  # [cod15] D_23="RM" (risc maternal)
            c1_12 += cm_base
        else:
            zile = nzl
        # [F133] adauga tichetele uniform (dupa ambele ramuri): CASS + impozit pe tichete,
        # baza CASS include nominalul; baza CAS (b4base) NU se atinge (tichetele n-au CAS).
        cass += cass_tichete
        imp += impozit_tichete
        baza_cass = cass_base_cm + tichete_nom   # [UNIFICARE CM] baza CASS exclude CM ne-eligibil (08/09 etc.)
        # [B poarta pe valori EMISE, 05.08.2026] scrie contributiile EMISE (B4_8=cas / B4_6=cass, dupa tichete)
        # inapoi in salariat, ca verifica_reconciliere (chemat DUPA _d112_genereaza) sa reconcilieze ce PLEACA la
        # ANAF, nu pre-emisia din pull. Cazul simplu: emis==_d112int(pull s[cas]) -> mutatiile existente pica la fel.
        # CM: emisul (salariu realizat + cm_cas) devine vizibil portii (inainte vedea salariul-only pre-emisie).
        s["cas"] = cas
        s["cass"] = cass
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
                 % (idx, _d112esc(s.get("cnp")), _d112esc(_t(s.get("nume"), _LIM["d112"]["numeAsig"])), _d112esc(_t(s.get("prenume"), _LIM["d112"]["prenAsig"])),   # C(75)
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
        # [8.3 avantaje] bilete de valoare defalcate pe tip: E3_10 masa / E3_75 vacanta / E3_74 cultural /
        # E3_72 cresa / E3_73 cadou (partea taxabila); E3_60 = suma (structura D112: E3_60 >= E3_10+E3_72+E3_73+E3_74+E3_75). INFORMATIV -
        # NU se atinge E3_8/E1_1 (ar rupe DUK regula S111: E1_1 = Suma(E3_8)); E3_8 (venit, mii) >= E3_60 (bilete,
        # sute) prin constructie. Emise DOAR cand exista avantaje (salariatii fara bilete raman neschimbati).
        # Probat DUK 04.08.2026. Cadou (E3_73): partea TAXABILA (excedent >300 la eveniment legal / integral la nelegal, CF art.76(4)a + art.142) intra in brut + E3_73 (16.08 - inainte era neinclus).
        _m = _d112int(s.get("e83_masa", 0)); _vc = _d112int(s.get("e83_vacanta", 0))
        _cu = _d112int(s.get("e83_cultural", 0)); _cr = _d112int(s.get("e83_cresa", 0))
        _cd = _d112int(s.get("e83_cadou", 0))   # [cadou] E3_73
        _e83_total = _m + _vc + _cu + _cr + _cd
        _e83 = ""
        if _e83_total > 0:
            _e83 = ' E3_60="%d"' % _e83_total
            if _m:  _e83 += ' E3_10="%d"' % _m
            if _cr: _e83 += ' E3_72="%d"' % _cr
            if _cd: _e83 += ' E3_73="%d"' % _cd
            if _cu: _e83 += ' E3_74="%d"' % _cu
            if _vc: _e83 += ' E3_75="%d"' % _vc
        a.append('    <asiguratE3 E3_1="B" E3_2="1" E3_3="1" E3_4="A" E3_5="%s" E3_6="%s" E3_8="%d" '
                 'E3_9="%d" E3_14="%d" E3_15="%d" E3_16="0" E3_19="0" E3_21="0"%s/>'
                 % (perioada, perioada, brute, b4base, imp, imp, _e83))
        # [R105] Se strange AICI, nu se recalculeaza altundeva: `brute`, `b4base`, `imp`, `cas` si
        # `cass` sunt chiar valorile pe care le-a scris E3/B4 mai sus. `int()` face ce face si `%d`
        # din formatul XML, deci componenta nu poate diverge de declaratie printr-o rotunjire.
        asigurati.append(AsiguratD112(
            nume=("%s %s" % (s.get("nume") or "", s.get("prenume") or "")).strip(),
            brut=int(brute), baza_cas=int(b4base),
            cas=int(cas), cass=int(cass), impozit=int(imp)))
        a.append('  </asigurat>')
        AS.append("\n".join(a))
    n = len(salariati)
    # round() Python (bancar) se aplica ICI, INAINTE ca _d112int() sa poata
    # rotunji aritmetic - 112.5 devenea deja 112 prin round() inainte sa ajunga
    # la _d112int. Eliminat round() exterior, _d112int face rotunjirea corecta.
    # [CAM baza, citare corectata 05.08.2026] sum_bazac = DOAR salariul REALIZAT (bazac), EXCLUDE indemnizatia
    # CM (cm_base): CAM nu se datoreaza pe prestatiile suportate din FNUASS - CF art.220^5 (Exceptii specifice
    # contributiei asiguratorii pentru munca), NU art.220^3 (=cota 2.25%). Valoarea nu se schimba, doar temeiul.
    cam_total = _d112int(sum_bazac * _cota_cam)
    A = []
    obligatii = []   # [R105] aceleasi randuri, in forma citibila de om
    def add_oblig(cod, cb, val):
        # [d112 v1.03-072026] sectiunea angajatorA ("Creante") e OBLIGATORIE minim 1 (XSD d112_06082026.xsd:
        # angajatorA minOccurs implicit=1, maxOccurs=29; structura_D112_0726_030826.pdf: "1-41 aparitii"). Se
        # emite si la obligatii zero - garda `if val > 0` scoasa (altfel A ramane [] -> 0 angajatorA -> DUK:
        # "ACreante: sectiunea Creante este obligatorie pt cif <> cif AJPIS"). Continut la zero confirmat empiric
        # pe validatorul J27.0.1 (autoritatea).
        A.append('    <angajatorA A_codOblig="%s" A_codBugetar="%s" A_datorat="%d" '
                 'A_deductibil="0" A_scutit="0" A_plata="%d"/>' % (cod, cb, val, val))
        obligatii.append(ObligatieD112(cod_oblig=cod, cod_bugetar=cb, datorat=int(val)))
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
             'totalPlata_A="%d">' % (cui_f, caen_f, _d112esc(_t(den_f, _LIM["d112"]["den"])), casa_ang, total_plata))
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
        _r1 = _c2row(_C2_RD1); _r2 = _c2row(("07", "10", "11")); _r3 = _c2row(("08",))  # [cod07] carantina in agregatul Rd.2 (prevenire) + sub-rand propriu C2_211-216 mai jos
        _r4 = _c2row(("09", "91", "92")); _r41 = _c2row(("17",)); _r5 = _c2row(("15",))
        _r07 = _c2row(("07",))  # [cod07] carantina - rand C2 propriu (prevenire imbolnavire, FNUASS)
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
        if _r07[0]:  # carantina (cod 07): rand propriu C2_211-216 (Rd2.2) - TOATE 6 coloanele.
            # C2_211=nr cazuri, C2_212=Sum D_16 (total zile), C2_213=Sum D_14 (zile suportate de angajator,
            # struct rd.49c l.1684), C2_214=Sum D_15 (zile FNUASS, rd.49d), C2_215=Sum D_20 (suma angajator,
            # rd.49e l.1699), C2_216=Sum D_21 (suma FNUASS, rd.49f). Carantina 07 NU e FNUASS-integral
            # (salarizare._CM_COD_FNUASS_INTEGRAL: angajatorul suporta primele zile) -> C2_213/C2_215 > 0 si
            # OBLIGATORII. Omiterea lor => DUK A49c (C2_213 lipsa), A43d.2 (C2_212=C2_213+C2_214), A49e (C2_215 lipsa).
            _c2a.append('C2_211="%d" C2_212="%d" C2_213="%d" C2_214="%d" C2_215="%d" C2_216="%d"'
                        % (_r07[0], _r07[1], _r07[2], _r07[3], _r07[4], _r07[5]))
        _c2t6 = _r1[5] + _r2[5] + _r3[5] + _r4[5] + _r41[5] + _r5[5]  # carantina e deja in _r2[5]=C2_26 (nu se dubleaza)
        _c2a.append('C2_T6="%d" C2_10="%d" C2_140="%d"' % (_c2t6, _c2t6, _c2t6))
        H.append('    <angajatorC2 %s/>' % " ".join(_c2a))
    H.append('    <angajatorC4 C4_baza="%d" C4_ct="%d"/>' % (sum_bazac, cam_total))
    H.append('  </angajator>')
    H.extend(AS)
    H.append('</declaratieUnica>')
    av.append("D112: %d salariati - impozit %s, CAS %s, CASS %s, CAM %s lei (luna %d/%d)."
              % (n, bani(sum_imp), bani(sum_cas), bani(sum_cass), bani(cam_total), luna, an))
    # [R105] Tuplul ramane tuplu — `d112.genereaza` foloseste `rezultat[0]`, si o schimbare de forma
    # acolo ar atinge portile de reconciliere fara motiv. Se schimba doar AL DOILEA element.
    return ("\n".join(H), RezultatD112(
        an=an, luna=luna, prof=prof, obligatii=obligatii, asigurati=asigurati,
        total_plata_a=int(total_plata), avertismente=av))


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
        # [fix data-angajare 06.08.2026] salariat activ IN luna = angajat pana la sfarsitul lunii SI
        # neincetat inainte de inceputul ei. Fara gardul pe data_angajare, D112 pe o luna anterioara angajarii
        # includea salariatul -> DUK S7 (dataAng > data raportare). Aceeasi clasa ca migrarea date-aware pe jumatate.
        cur.execute(f"SELECT * FROM {schema}.salariati WHERE (data_incetare IS NULL OR data_incetare >= %s) "
                    f"AND (data_angajare IS NULL OR data_angajare < (%s::date + INTERVAL '1 month')) ORDER BY id",
                    (_dsal(an, luna, 1), _dsal(an, luna, 1)))
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
    cresa_luna = _ben.lista_luna(conn, schema, an, luna, "cresa")  # [tichete de cresa]
    cadou_tax = _ben.cadou_taxabil_luna(conn, schema, an, luna)  # [cadou] suma taxabila (CF art.76(4)a)
    pe_sal = {}
    for c in cms:
        pe_sal.setdefault(c["salariat_id"], []).append({
            "serie": c.get("serie"), "numar": c.get("numar"),
            "da": _d112_data(str(c.get("data_acordare") or "")),
            "di": _d112_data(str(c.get("data_inceput") or "")),
            "ds": _d112_data(str(c.get("data_sfarsit") or "")),
            "cod": c.get("cod") or "01",
            "cod_urgenta": c.get("cod_urgenta"),
            "cnp_ingrijit": c.get("cnp_ingrijit"),   # [D_8/D_8a] CNP persoana ingrijita (copil 09/91/92 / pacient oncologic 17)
            "program_national": bool(c.get("program_national")),   # [D_9a] pacient in program national de sanatate
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
            "data_nastere": s.get("data_nastere"),                       # [deducere suplimentara] tineri <26
            "copii_scolarizati": s.get("copii_scolarizati") or 0,        # [deducere suplimentara] 100 lei/copil
            "declaratie_copii": bool(s.get("declaratie_copii")),         # [deducere suplimentara] declaratia parintelui
            "scutit_pt": bool(s.get("scutit_contrib_minim")),
            "scutit": bool(s.get("scutit_contrib_minim")),
            "motiv_exceptare": s.get("motiv_exceptare"),
            "tichet_masa_valoare": s.get("tichet_masa_valoare") or 0,  # [F133]
            "tichet_vacanta": vac_luna.get(s["id"], 0),  # [F133 Faza 2a]
            "tichet_cultural": cult_luna.get(s["id"], 0),  # [tichete culturale] impozit only, NU in baza CASS
            "tichet_cresa": cresa_luna.get(s["id"], 0),  # [tichete de cresa] impozit only, NU in baza CASS
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
    # [part-time-floor 20.08.2026 — REVENIRE la sm-facilitate, decizia „urmeaza arbitrul"] Nivelul de
    # referinta pentru baza minima part-time (CAS art.146 alin.(5^6) / CASS art.168 alin.(6^1)) e salariul
    # minim DIMINUAT cu facilitatea, NU cel integral.
    #   TEMEI: OUG 156/2024 art.LXVI alin.(5) = OUG 89/2025 art.III — derogarea „NIVELUL ... SE DIMINUEAZA
    #   cu 300 lei" REDEFINESTE nivelul de referinta (3750 in S1 2026 / 4125 in S2), nu acorda o facilitate.
    #   Structura ANAF o pune INAUNTRUL formulei part_time (structura_D112_0726_030826.txt l.3128-3129
    #   pentru B4_7P si l.3157-3158 pentru B4_5P: „sm=4050 ... sm=sm-300 ... part_time=ROUND(sm*zile_PT/NZL)").
    #   ARBITRUL: DUKIntegrator, DUK regula SP1B4_1, calculeaza 3750 si semnala 4050/4325 ca atentionare.
    # Pe 06.08.2026 scaderea fusese scoasa de aici (rationament: facilitatea e doar pentru norma intreaga)
    # SI din core/d112_reconciliere.py, dar NU si din core/salarizare.py:309 — care ramasese pe forma
    # corecta si isi cita temeiul. Rezultat: fluturasul si D112 declarau sume diferite pentru acelasi
    # salariat si aceeasi luna (70,25 lei/luna pe PARTTIME SUBFLOOR, august 2026). Vezi DECIZII 20.08.
    prag_pt = float(sm - fac)
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
                               tichet_cultural=float(s.get("tichet_cultural") or 0),
                               tichet_cresa=float(s.get("tichet_cresa") or 0),
                               cadou_taxabil=float(cadou_tax.get(s["id"], 0) or 0),
                               sub_26=_sz.sub_26_la(s.get("data_nastere"), ref),   # [deducere suplimentara]
                               copii_scoala=(int(s.get("copii_scolarizati") or 0) if s.get("declaratie_copii") else 0),
                               declaratie_copii=bool(s.get("declaratie_copii")))
        s["brut_lucrat"] = brut_lucrat   # consumat de salarii_contare (o singura cifra)
        # [fix salariu-la-data 06.08.2026] brutul DECLARAT (B4_3/B1_sal1) si baza non-CM = salariul LUNII
        # (date-aware _sal_luna=brut_int), NU salariati.salariu_brut (contractual CURENT, stale). Migrarea 29.07
        # mutase doar CONTRIBUTIILE pe date-aware; brutul/baza ramasesera stale -> B4_7 vs B4_8 divergente
        # (DUK S74d) pt orice salariat cu schimbare de salariu in an. Consumat de d112.build + salarii_contare.
        s["brut"] = brut_int
        s["facilitate"] = r.get("facilitate", 0)
        s["cas"] = r.get("cas", 0)
        s["cass"] = r.get("cass", 0)
        # [R85, 28.08.2026] A PATRA CONTRIBUTIE, pusa inapoi ca celelalte trei.
        # Pana azi `cam` era singura care nu se scria pe salariat, si fara motiv scris. Cine suma
        # `s.get("cam")` peste salariatii intorsi de `pull` primea 0, TACUT - o cheie absenta e
        # indistincta de valoarea zero. E chiar bugul nr.1 din antetul lui `core/salarii_contare.py`,
        # dovedit pe 15.07.2026 pe versiunea veche (`_sum("cam") = 0` -> contul 436 ramanea gol), pe
        # care reconstructia l-a OCOLIT, nu desfiintat. Aceeasi clasa cu intrarile de tichete (R86/RR1).
        #
        # CE ESTE, si de ce nu se poate folosi in locul declaratiei: CAM-ul salariatului calculat pe
        # brutul LUI INTREG, valoare PRE-EMISIE - la fel ca `cas` si `cass` de mai sus. Obligatia
        # DECLARATA (codul 480) se calculeaza altfel: `_d112_genereaza` o scoate o singura data, din
        # `sum_bazac` - baza contributiva, din care facilitatea de la salariul minim e SCAZUTA - si o
        # rotunjeste la leu pe TOTAL, nu per salariat.
        # MASURAT pe cele 30 de perechi (28.08.2026): suma per salariat difera de codul 480 cu cel
        # mult **6,78 lei pe 12 salariati** - adica 2,25% x 300 (facilitatea) + rotunjire; pe lunile
        # cu facilitate de 200 devine 4,54-4,69; pe firmele fara salariat la minim, doar rotunjire
        # (sub 0,5 lei). Aceeasi diferenta structurala ca la R86-B: brut realizat vs baza contributiva.
        # DECI: cine are nevoie de cifra DECLARATA foloseste `d112.obligatii(...)["480"]`, nu suma
        # asta. Iar diferenta ei fata de `cas`/`cass` e ca alea sunt REscrise de `_d112_genereaza` cu
        # valorile emise, pe cand `cam` nu are corespondent per salariat acolo - deci ramane pre-emisie.
        s["cam"] = r.get("cam", 0)

        s["exces_vacanta"] = _exces_van   # [D3] intra in brutul declarat (B4 base)
        # [R86/RR1, 28.08.2026] INTRARILE de tichete, puse inapoi in salariat.
        # Pana azi pull() punea inapoi doar IESIRILE lui calcul_salariu (cas, cass, impozit,
        # tichete_nominal, e83_*). Cine chema calcul_salariu a doua oara pe acelasi salariat -
        # si `salarii_contare.note_lunare` chiar asta face - n-avea de unde sa ia zilele cu
        # tichet, excesul de vacanta si cadoul taxabil: alea se CALCULEAZA aici, din pontaj si
        # din plafonul anual. Rezultatul era ca nota contabila iesea cu `tichete_nominal = 0`,
        # deci FARA linia 642=5328: cheltuiala cu biletele de valoare nu intra deloc in
        # evidenta, desi declaratia o poarta (masurat: 800/800/25.140/920/840 pe tenant_001).
        # Aceeasi clasa cu R85 (`cam` lipsa din dictionar), alta instanta: ce nu se pune inapoi
        # nu se poate reciti, iar absenta unei chei e indistincta de valoarea zero.
        s["tichet_zile"] = tichet_zile
        s["tichet_vacanta_net"] = max(_vac_l - _exces_van, 0.0)
        s["cadou_taxabil"] = float(cadou_tax.get(s["id"], 0) or 0)
        s["impozit"] = r.get("impozit", 0)          # TOTAL (salariu + tichete)
        s["deducere"] = (r.get("deducere") or {}).get("total", 0)
        s["cass_tichete"] = r.get("cass_tichete", 0)        # [F133] CASS pe tichete
        s["impozit_tichete"] = r.get("impozit_tichete", 0)  # impozit pe tichete
        # [F133] baza CASS D112 = valoarea TOTALA a biletelor (masa + vacanta)
        s["tichete_nominal"] = r.get("tichete_nominal", 0) + r.get("tichete_vacanta", 0)
        # [8.3 avantaje] nominalele PER TIP pt sectiunea 8.3 D112 (E3_10 masa / E3_75 vacanta /
        # E3_74 cultural / E3_72 cresa). Separate de tichete_nominal (baza CASS, masa+vacanta) - aici
        # e defalcarea informativa. Cadou (E3_73) nu apare: nu e in pipeline-ul de impozit al calcul_salariu.
        s["e83_masa"] = r.get("tichete_nominal", 0)
        s["e83_vacanta"] = r.get("tichete_vacanta", 0)
        s["e83_cultural"] = r.get("tichete_cultural", 0)
        s["e83_cresa"] = r.get("tichete_cresa", 0)
        s["e83_cadou"] = r.get("tichete_cadou", 0)   # [cadou] E3_73 (partea taxabila)
        # part-time supra-taxare (art. 146(5^6)/168(6^1) CF, structura D112 v7):
        # part_time = ROUND(prag_pt * zile_lucrate / NZL); daca 0 < baza < part_time
        # -> B4_*P la prag, diferenta pe angajator. Exceptati: scutit+motiv 1-5.
        zile_lucr = max(nzl - int(s.get("zile_cm") or 0), 0)
        baza = _sal_luna  # [tranzitie] date-aware, nu salariati.salariu_brut
        scutit = bool(s.get("scutit_pt"))
        prag_zile = _d112int(prag_pt * zile_lucr / nzl) if nzl else 0  # A91b: aritmetic, nu bancar
        if not scutit and 0 < baza < prag_zile:
            s["pt_aplica"] = True
            s["baza_minim_pt"] = prag_zile
            s["cas_min_pt"] = _d112int(prag_zile * float(_cm.cota("cas", ref)[0]))   # A91b aritmetic
            s["cass_min_pt"] = _d112int(prag_zile * float(_cm.cota("cass", ref)[0]))  # A91b aritmetic
        else:
            s["pt_aplica"] = False
    _cs_sal.close()
    return prof, salariati


def obligatii(conn, schema, an, luna, xml=None):
    """Cele sase obligatii ale angajatorului (sectiunea `angajatorA`), pe cod de obligatie.

    `{"602": impozit, "412": CAS retinut, "432": CASS retinut, "480": CAM,
      "458": CAS angajator part-time, "459": CASS angajator part-time}` — in LEI INTREGI,
    exact valorile care pleaca la ANAF.

    [R34, 28.08.2026] Exista fiindca `salarii_contare` are nevoie de valorile DECLARATE, nu de
    o a doua socoteala a lor. Nu recalculeaza nimic: citeste artefactul emis. `xml` se poate
    pasa cand a fost deja generat, ca sa nu se genereze de doua ori pe acelasi apel.
    """
    if xml is None:
        xml, _av = genereaza(conn, schema, an, luna)
    from core import control_incrucisat as _ci   # lazy: _ci importa d112
    return _ci.totaluri_d112_din_xml(xml)


def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    if not str(prof.get("cui") or "").strip():
        erori.append("LIPSĂ CUI firmă.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firmă.")
    from core.firma_profil_api import erori_declarant as _ed   # [R101] sursa unica
    erori += _ed(prof)
    return erori


def genereaza(conn, schema, an, luna):
    prof, salariati = pull(conn, schema, an, luna)
    _er = erori_generare(prof)
    if _er:
        raise ValueError("D112 nu se poate genera: " + " ".join(_er))
    # POARTA A DOUA CALE pe valorile EMISE (B, 05.08.2026): generam XML INTAI (_d112_genereaza scrie
    # contributiile emise B4_8/B4_6 inapoi in salariati), apoi reconciliem ce PLEACA la ANAF. Inainte poarta
    # vedea PRE-emisia din pull (blind-spot pe layerul de emisie - descoperit pe CM). Divergenta = HARD-BLOCK
    # care numeste ambele valori. Vezi core/d112_reconciliere.py.
    rezultat = _d112_genereaza(prof, salariati, an, luna)
    from core.d112_reconciliere import verifica_reconciliere
    verifica_reconciliere(conn, schema, an, luna, salariati)
    from core.reconciliere_emis import verifica_d112 as _vd112
    _vd112(rezultat[0])   # poarta pe ARTEFACT: totalPlata_A == suma A_datorat emise (self-consistency lossless)
    return rezultat
