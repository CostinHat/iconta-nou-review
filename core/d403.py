"""core/d403.py - D403: Declaratie informativa privind produsele de asigurare de viata /
schimb automat de informatii financiare (DAC2/CRS). Cod M.F.P. 14.13.01.13/1.

Declaratie INFORMATIVA depusa de institutia financiara raportoare din Romania catre ANAF,
in cadrul schimbului automat obligatoriu de informatii in domeniul fiscal (DAC2 / standardul
comun de raportare CRS). Raporteaza politele/conturile financiare ale persoanelor
raportabile - rezidenti fiscali intr-un alt stat participant. Act-cadru comun cu D402:
OMFP/OPANAF 2727/2015 pentru aprobarea modelului si continutului formularelor 402 si 403.

SURSA STRUCTURII = validatorul oficial ANAF (DUKIntegrator / D403Validator.jar). NU exista
XSD publicat pe disc/in jar; structura, radacina, campurile, domeniile si regderile R au fost
CITITE camp cu camp din bytecode:
  d403validator/v0/{Identificare, Polita, Persoana, Eveniment, ValCap, ValidatorImpl,
                    DataObjectRoot, DbAccessImpl} - operanzii nextAttribute*(name, len, tip,
  mandatory) dau numele, lungimea, tipul si flagul obligatoriu; nextAttributeInInterval /
  nextAttributeInList dau domeniile; mesajele R... dau corelatiile. Nomenclatoarele
  (_formaJuridica, _judete, _tari, _monezi, _nationalitati) au fost extrase din
  d403validator/parameters/Parameters_v0. Radacina CONFIRMATA din bytecode: `declaratie403`,
  namespace `mfp:anaf:dgti:d403:declaratie:v1`.

Ierarhie (elemente): <declaratie403> > <polita> (1-n) > { <persoana> (1-n), <eveniment>
(1-n), <val_cap> (0-n) }. Atributele identificarii raportorului stau pe radacina.

Reguli probate (citari "DUK regula ..."):
  - R24  : totalPlata_A = suma calculata = SUMA(val_capital din toate <val_cap>) +
           SUMA(Suma3 + Suma5 din toate <eveniment>). Suma de control pe radacina.
  - Rnr  : nr_pers = numarul total de elemente <persoana> din declaratie (count peste polite).
  - R9   : daca Judet_rap=40 (Bucuresti), Sector_rap este obligatoriu.
  - R33  : anul din data_I_polita <= anul de raportare.
  - R64  : pentru Tip_pers=1 (persoana fizica), In_calit este obligatoriu.
  - R65  : pentru Tip_pers=1, Tip_adresa2 este obligatoriu.
  - R67  : pentru Tip_pers=2 (persoana juridica), Tip_PJ este obligatoriu.
  - R68  : pentru Tip_pers=2, Sediu_DN2 este obligatoriu.
  - R120 : pentru Tip_pers=1, cel putin unul dintre Data_nasterii, CIF_SR sau CIF_rom.
  - R75.1: pentru Calit_pers in (1,3,4), tip_ben_plat_contr este obligatoriu.
  - R75.2: pentru Calit_pers=2, tip_ben_plat_contr trebuie sa fie null.
  - R75.3: pentru Calit_pers<>1, tip_ben_plat_contr nu poate fi 3.
  - R78  : pentru Calit_pers in (2,3,4), rel_ben este obligatoriu.
  - R79.1: pentru Calit_pers=1, stare_ben este obligatoriu.
  - R79.2: pentru Calit_pers<>1, stare_ben trebuie sa fie null.
  - Rpol : in fiecare <polita> trebuie sa existe cel putin o <persoana> cu Stat_SR<>RO si
           Calit_pers in (1,3,4) (persoana raportabila).
  - R111 : daca tip_polita=1, atunci tip_termen_polita=2.
  - R113 : daca frecv_plata=2, atunci tip_termen_polita trebuie completat.
  - R114 (Polita): daca tip_termen_polita=1, ani_contrib_polita completat si <> 0.
  - R115 (Polita): daca tip_benef_polita in (2,4), ani_contrib_polita completat si <> 0.
  - R114 (Eveniment): daca tip_polita=1, Tip_ev trebuie sa NU fie 3,4 sau 8.
  - R116 : daca Tip_ev in 3..9, Status_ev trebuie sa fie 2.
  - R117 : daca Tip_ev in 10..17, Status_ev trebuie completat.
  - R115 (Eveniment): daca Tip_ev in (1,2,18..25), Status_ev nu trebuie completat.
  - R118 : daca Tip_ev in 10..17, Tip_transfer trebuie completat.
  - R95/R96/R97 : daca Suma3>0, atunci Moneda3 / Data3 / Cont3 sunt obligatorii.
  - R103/R104/R105 : daca Suma5>0, atunci Moneda5 / Data5 / Cont5 sunt obligatorii.
  - R110.1/R110.2 : in <val_cap>, cele 3 campuri (tip_val_capital, val_capital,
           moneda_capital) sunt toate completate sau toate necompletate.
  - Data format ZZ.LL.AAAA (dd.mm.yyyy); luna raportarii = 12 (fix, raportare anuala).

Nomenclatoare (Parameters_v0): Forma_juridica in {1,8,9,10}; Judet_rap = coduri judet
"01".."41" + "51"/"52" (40=Bucuresti); Stat_SR / Tara_rap = state membre UE + RO (_tari);
Moneda3/Moneda5/moneda_capital in {CZK,CHF,DKK,EUR,GBP,HRK,HUF,PLN,RON,SKK,SEK,USD};
Nationalitate = nomenclatorul complet de tari (_nationalitati).

Declaratie MANUALA: institutia financiara furnizeaza TOATE datele prin `manual` (aplicatia nu
tine un registru de conturi raportabile). NU se fabrica valori. `conn` nu e folosit (pull
returneaza {}), deci genereaza(conn=None, ...) functioneaza.

NEPOPULAT deliberat (optional in validator, se completeaza de raportor la nevoie, aceeasi
metoda): Sector_rap (doar Judet=40), Den_repr1/CIF_repr1/Adr_repr1, Den_pers/Nume_pers/
Pren_pers, Strada_SR/Nr_SR/Codp_SR, CIF_rom/CIF_SR, Nationalitate, Data_nasterii, Act_id,
Tip_repr2/Den_repr2/CIF_repr2/Adr_repr2, nr_polita, data_I_polita/data_S_polita, frecv_plata,
tip_termen_polita, ani_contrib_polita, ani_benef_polita, tip_optiune, sumele si datele din
<eveniment> (Suma3/Suma5, Data*, Cont*, Tip_transfer, Status_ev, Tip_baza), tot <val_cap>.

Contract dXXX: pull / erori_generare / calcul_d403 / build_xml / genereaza(conn, schema,
perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d403:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
_CUI_W = [7, 5, 3, 2, 1, 7, 5, 3, 2]  # cheia de control CUI ANAF

# Nomenclatoare (domenii) - d403validator/parameters/Parameters_v0
_FORMA_JURID = frozenset(("1", "8", "9", "10"))  # _formaJuridica
_JUDETE = frozenset(["%02d" % j for j in range(1, 42)] + ["51", "52"])  # _judete (40=Bucuresti)
_TARI_MS = frozenset(("AT", "BE", "BG", "CZ", "CY", "HR", "DK", "EE", "DE", "EL", "FI", "FR",
                      "IE", "IT", "LV", "LU", "LT", "MT", "GB", "NL", "PL", "PT", "RO", "SI",
                      "SK", "ES", "SE", "HU"))  # _tari - Stat_SR si Tara_rap
_MONEZI = frozenset(("CZK", "CHF", "DKK", "EUR", "GBP", "HRK", "HUF", "PLN", "RON", "SKK",
                     "SEK", "USD"))  # _monezi
# _nationalitati (nomenclatorul complet de tari) - Nationalitate (optional)
_NATIONALITATI = frozenset((
    "JM", "JP", "KZ", "KE", "KG", "KI", "KW", "LA", "LS", "LV", "LB", "LR", "LY", "LI", "LT",
    "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "FM",
    "MC", "MN", "MS", "MZ", "NA", "NR", "NP", "NI", "NE", "NU", "NF", "CD", "CS", "GS", "MP",
    "PS", "RU", "SA", "TF", "TW", "UM", "WS", "XK", "XL", "AX", "AF", "FC", "ZA", "AL", "DZ",
    "AD", "AO", "AI", "AQ", "AG", "AN", "AR", "AM", "AU", "AT", "AZ", "BS", "BH", "BD", "BB",
    "BE", "BZ", "BJ", "BM", "BT", "BY", "BO", "BA", "BW", "BR", "BN", "BG", "BF", "BI", "KH",
    "CM", "CA", "CV", "CZ", "CL", "CN", "CX", "TD", "CI", "CC", "CO", "KM", "CG", "CK", "KP",
    "KR", "HR", "CU", "DK", "DM", "DO", "EC", "CH", "AE", "ER", "EE", "FO", "FJ", "FI", "FR",
    "GA", "GM", "GE", "DE", "GH", "GI", "TV", "EL", "GD", "GL", "GP", "GU", "GT", "GN", "GQ",
    "GW", "GY", "GF", "HT", "HM", "HN", "HK", "IN", "ID", "JO", "IQ", "IR", "IE", "IS", "IL",
    "IT", "EG", "ET", "FK", "MX", "MA", "NG", "NL", "PH", "UG", "UY", "CR", "GB", "SV", "AW",
    "BV", "KY", "XM", "PW", "NO", "NC", "NZ", "OM", "PK", "PA", "PG", "PY", "PE", "PN", "PF",
    "PL", "PT", "XC", "PR", "QA", "YE", "MD", "RE", "RO", "RW", "US", "EH", "SH", "KN", "LC",
    "PM", "VC", "AS", "SM", "ST", "SN", "XS", "SC", "SL", "SG", "SY", "SK", "GG", "SI", "SB",
    "SO", "ES", "LK", "SD", "SE", "SR", "SJ", "SZ", "TJ", "TZ", "IO", "TH", "TL", "TG", "TK",
    "TO", "TT", "TN", "TR", "TM", "TC", "UA", "HU", "MM", "UZ", "VU", "VA", "VE", "VN", "VI",
    "VG", "WF", "ZM", "ZW", "DJ"))

# Domenii numerice (min, max) - operanzii nextAttributeInInterval din bytecode
_R_CALIT_PERS = (1, 4)
_R_TIP_PERS = (1, 2)
_R_TIP_ADR1 = (1, 4)          # exclude 3 (nu e in nomenclator)
_R_SEDIU_DN1 = (1, 2)
_R_IN_CALIT = (1, 4)
_R_TIP_ADR2 = (1, 5)
_R_TIP_PJ = (1, 8)
_R_SEDIU_DN2 = (1, 2)
_R_TIP_REPR2 = (1, 2)
_R_TIP_BEN_PLAT = (1, 4)
_R_UNIC_MM = (1, 3)
_R_REL_BEN = (1, 4)
_R_STARE_BEN = (1, 2)
_R_TIP_POLITA = (1, 2)
_R_TRAT_FISC = (1, 5)
_R_FRECV_PLATA = (1, 2)
_R_TIP_TERMEN = (1, 2)
_R_TIP_BENEF_POLITA = (1, 4)
_R_TIP_OPTIUNE = (1, 3)
_R_TIP_EV = (1, 25)
_R_TIP_TRANSFER = (1, 4)
_R_PERIODICITATE = (1, 3)
_R_STATUS_EV = (1, 2)
_R_REGIM_EV = (1, 2)
_R_TIP_BAZA = (1, 4)
_R_MOD_IMP1 = (1, 6)
_R_MOD_IMP2 = (1, 2)
_R_TIP_VAL_CAP = (1, 4)


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cnp_valid(cnp):
    """CNP / NIF Romania: 13 cifre, prima nenula, cifra de control (CIF_rom)."""
    cnp = _cif(cnp)
    if len(cnp) != 13 or cnp[0] == "0":
        return False
    s = sum(int(cnp[i]) * _CNP_W[i] for i in range(12))
    c = s % 11
    c = 1 if c == 10 else c
    return c == int(cnp[12])


def _cui_valid(cui):
    """CUI raportor roman: 2-10 cifre, cheia de control ANAF (753217532)."""
    cui = _cif(cui)
    if not (2 <= len(cui) <= 10) or cui[0] == "0":
        return False
    body = cui[:-1].rjust(9, "0")
    s = sum(int(body[i]) * _CUI_W[i] for i in range(9))
    c = (s * 10) % 11
    c = 0 if c == 10 else c
    return c == int(cui[-1])


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _intval(x):
    """Intreg N(15) cu rotunjire half-up (Decimal.quantize), nu bancara."""
    if x in (None, ""):
        return 0
    d = Decimal(str(x).replace(",", ".")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(d)


def _dec2(x):
    """Zecimal cu 2 pozitii, rotunjire half-up (Decimal.quantize)."""
    if x in (None, ""):
        return Decimal("0.00")
    return Decimal(str(x).replace(",", ".")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


_RE_ZLLA = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$")
_RE_ISO = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")


def _parse_data(x):
    """Accepta ZZ.LL.AAAA, AAAA-LL-ZZ sau obiect date/datetime. Returneaza (an, luna, zi)
    validat sau None. Fara strftime."""
    if x in (None, ""):
        return None
    if hasattr(x, "year") and hasattr(x, "month") and hasattr(x, "day"):
        y, mo, d = int(x.year), int(x.month), int(x.day)
    else:
        s = str(x).strip()
        m = _RE_ZLLA.match(s)
        if m:
            d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            m = _RE_ISO.match(s)
            if not m:
                return None
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= mo <= 12 and 1 <= d <= 31 and 1000 <= y <= 9999):
        return None
    return (y, mo, d)


def _fmt_data(t):
    """(an, luna, zi) -> 'ZZ.LL.AAAA' (dd.mm.yyyy). Fara strftime."""
    return "%02d.%02d.%04d" % (t[2], t[1], t[0])


def _int_or_none(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def _in_range(x, rng):
    v = _int_or_none(x)
    return v is not None and rng[0] <= v <= rng[1]


@dataclass
class Rezultat403:
    an: int
    luna: int = 12
    total_plata_a: int = 0
    nr_persoane: int = 0
    nr_polite: int = 0
    nr_evenimente: int = 0
    avertismente: list = field(default_factory=list)


def _polite(manual):
    p = manual.get("polite")
    return list(p) if p else []


def _persoane(pol):
    p = pol.get("persoane")
    return list(p) if p else []


def _evenimente(pol):
    e = pol.get("evenimente")
    return list(e) if e else []


def _valcap(pol):
    v = pol.get("valori_capital")
    return list(v) if v else []


def calcul_d403(manual):
    """DUK regula R24: totalPlata_A = SUMA(val_capital) + SUMA(Suma3 + Suma5).

    Suma se acumuleaza ca zecimal (half-up 2 pozitii) apoi se rotunjeste la intreg N(15)
    pentru atributul totalPlata_A (Decimal.quantize half-up), asa cum valideaza DUK.
    """
    total = Decimal("0.00")
    npers = nev = 0
    for pol in _polite(manual):
        npers += len(_persoane(pol))
        for vc in _valcap(pol):
            total += _dec2(vc.get("val_capital"))
        for ev in _evenimente(pol):
            nev += 1
            total += _dec2(ev.get("suma3")) + _dec2(ev.get("suma5"))
    return {
        "totalPlata_A": _intval(total),
        "nr_pers": npers,
        "nr_evenimente": nev,
        "nr_polite": len(_polite(manual)),
    }


def pull(conn, schema, perioada):
    """D403 e MANUALA: institutia financiara raportoare furnizeaza politele/conturile,
    persoanele raportabile si evenimentele. Aplicatia nu tine un registru de conturi
    raportabile CRS; `conn` nu e folosit (merge conn=None)."""
    return {}


def erori_generare(prof, manual):
    er = []
    an = int(prof.get("an") or 0)
    # --- identificare raportor (radacina declaratie403) ---
    if not (_cui_valid(manual.get("cif")) or _cnp_valid(manual.get("cif"))):
        er.append("CIF raportor (cif) invalid - aștept CUI (2-10 cifre) sau CNP (13 cifre).")
    for camp, et in (("den_rap", "Denumire raportor (Den_rap)"),
                     ("localitate_rap", "Localitate raportor (Localitate_rap)"),
                     ("adresa_rap", "Adresa raportor (Adresa_rap)"),
                     ("nume_declar", "Nume declarant (nume_declar)"),
                     ("prenume_declar", "Prenume declarant (prenume_declar)"),
                     ("functie_declar", "Funcție declarant (functie_declar)")):
        if not str(manual.get(camp) or "").strip():
            er.append("Lipsa " + et + ".")
    judet = str(manual.get("judet_rap") or "").strip()
    if judet not in _JUDETE:
        er.append("Judet_rap (judet_rap) obligatoriu, cod județ valid (ex. 40=București).")
    elif judet == "40" and not str(manual.get("sector_rap") or "").strip():
        er.append("Pentru Judet_rap=40, Sector_rap (sector_rap) este obligatoriu (DUK regula R9).")
    if str(manual.get("tara_rap") or "").strip().upper() not in _TARI_MS:
        er.append("Tara_rap (tara_rap) obligatoriu, stat din nomenclator (ex. RO).")
    if str(manual.get("forma_juridica") or "").strip() not in _FORMA_JURID:
        er.append("Forma_juridica (forma_juridica) obligatoriu în {1,8,9,10}.")
    if not _in_range(manual.get("tip_adresa1"), _R_TIP_ADR1) or int(manual.get("tip_adresa1")) == 3:
        er.append("Tip_adresa1 (tip_adresa1) obligatoriu în {1,2,4}.")
    if not _in_range(manual.get("sediu_dn1"), _R_SEDIU_DN1):
        er.append("Sediu_DN1 (sediu_dn1) obligatoriu în (1,2).")
    try:
        d_rec = int(manual.get("d_rec") or 0)
    except (TypeError, ValueError):
        d_rec = -1
    if d_rec not in (0, 1):
        er.append("d_rec obligatoriu 0 (initiala) sau 1 (rectificativa).")

    polite = _polite(manual)
    if not polite:
        er.append("Cel putin o <polita> (polite) este obligatorie.")
    for pi, pol in enumerate(polite, 1):
        pp = "polita #%d: " % pi
        if not str(pol.get("id_polita") or "").strip():
            er.append(pp + "lipsă id_polita.")
        tp = _int_or_none(pol.get("tip_polita"))
        if not _in_range(tp, _R_TIP_POLITA):
            er.append(pp + "tip_polita obligatoriu în (1,2).")
        if not _in_range(pol.get("trat_fisc_polita"), _R_TRAT_FISC):
            er.append(pp + "trat_fisc_polita obligatoriu în (1..5).")
        tbp = _int_or_none(pol.get("tip_benef_polita"))
        if not _in_range(tbp, _R_TIP_BENEF_POLITA):
            er.append(pp + "tip_benef_polita obligatoriu în (1..4).")
        tt = _int_or_none(pol.get("tip_termen_polita"))
        if tp == 1 and tt != 2:
            er.append(pp + "tip_polita=1 impune tip_termen_polita=2 (DUK regula R111).")
        if _int_or_none(pol.get("frecv_plata")) == 2 and tt is None:
            er.append(pp + "frecv_plata=2 impune tip_termen_polita (DUK regula R113).")
        aci = _int_or_none(pol.get("ani_contrib_polita"))
        if tt == 1 and (aci is None or aci == 0):
            er.append(pp + "tip_termen_polita=1 impune ani_contrib_polita <> 0 (DUK regula R114).")
        if tbp in (2, 4) and (aci is None or aci == 0):
            er.append(pp + "tip_benef_polita în (2,4) impune ani_contrib_polita <> 0 (DUK regula R115).")
        di = _parse_data(pol.get("data_i_polita"))
        if pol.get("data_i_polita") and di is None:
            er.append(pp + "data_i_polita format ZZ.LL.AAAA.")
        elif di is not None and di[0] > an:
            er.append(pp + "anul din data_i_polita > anul raportarii (DUK regula R33).")

        pers = _persoane(pol)
        if not pers:
            er.append(pp + "cel putin o <persoana> este obligatorie.")
        raportabila = False
        for bi, b in enumerate(pers, 1):
            pb = pp + "persoana #%d: " % bi
            if not str(b.get("id_pers") or "").strip():
                er.append(pb + "lipsă id_pers.")
            calit = _int_or_none(b.get("calit_pers"))
            if not _in_range(calit, _R_CALIT_PERS):
                er.append(pb + "Calit_pers obligatoriu în (1..4).")
            tip_pers = _int_or_none(b.get("tip_pers"))
            if not _in_range(tip_pers, _R_TIP_PERS):
                er.append(pb + "Tip_pers obligatoriu în (1,2).")
            stat = str(b.get("stat_sr") or "").strip().upper()
            if stat not in _TARI_MS:
                er.append(pb + "Stat_SR obligatoriu, stat din nomenclator (_tari).")
            if not str(b.get("localitate_sr") or "").strip():
                er.append(pb + "lipsă Localitate_SR (localitate_sr).")
            if not _in_range(b.get("unic_mm"), _R_UNIC_MM):
                er.append(pb + "unic_mm obligatoriu în (1..3).")
            cp = b.get("cota_parte")
            if cp in (None, "") or _dec2(cp) < 0:
                er.append(pb + "cota_parte obligatorie (zecimal, ex. 100.00).")
            # tip_pers dependent
            if tip_pers == 1:
                if not _in_range(b.get("in_calit"), _R_IN_CALIT):
                    er.append(pb + "Tip_pers=1 impune In_calit în (1..4) (DUK regula R64).")
                if not _in_range(b.get("tip_adresa2"), _R_TIP_ADR2):
                    er.append(pb + "Tip_pers=1 impune Tip_adresa2 în (1..5) (DUK regula R65).")
                if not (b.get("data_nasterii") or _cif(b.get("cif_sr")) or _cnp_valid(b.get("cif_rom"))):
                    er.append(pb + "Tip_pers=1 impune Data_nasterii sau CIF_SR sau CIF_rom (DUK regula R120).")
                if not str(b.get("nume_pers") or "").strip():
                    er.append(pb + "Tip_pers=1 impune Nume_pers (DUK regula R53a).")
                if not str(b.get("pren_pers") or "").strip():
                    er.append(pb + "Tip_pers=1 impune Pren_pers (DUK regula R53b).")
            if tip_pers == 2:
                if not _in_range(b.get("tip_pj"), _R_TIP_PJ):
                    er.append(pb + "Tip_pers=2 impune Tip_PJ în (1..8) (DUK regula R67).")
                if not _in_range(b.get("sediu_dn2"), _R_SEDIU_DN2):
                    er.append(pb + "Tip_pers=2 impune Sediu_DN2 în (1,2) (DUK regula R68).")
                if not str(b.get("den_pers") or "").strip():
                    er.append(pb + "Tip_pers=2 impune Den_pers (DUK regula R53).")
            # calit_pers dependent
            tbpc = _int_or_none(b.get("tip_ben_plat_contr"))
            if calit in (1, 3, 4):
                if tbpc is None or not _in_range(tbpc, _R_TIP_BEN_PLAT):
                    er.append(pb + "Calit_pers în (1,3,4) impune tip_ben_plat_contr în (1..4) (DUK regula R75.1).")
                elif calit != 1 and tbpc == 3:
                    er.append(pb + "Calit_pers<>1: tip_ben_plat_contr nu poate fi 3 (DUK regula R75.3).")
            elif calit == 2 and tbpc is not None:
                er.append(pb + "Calit_pers=2: tip_ben_plat_contr trebuie să fie null (DUK regula R75.2).")
            if calit in (2, 3, 4) and not _in_range(b.get("rel_ben"), _R_REL_BEN):
                er.append(pb + "Calit_pers în (2,3,4) impune rel_ben în (1..4) (DUK regula R78).")
            sb = _int_or_none(b.get("stare_ben"))
            if calit == 1 and not _in_range(sb, _R_STARE_BEN):
                er.append(pb + "Calit_pers=1 impune stare_ben în (1,2) (DUK regula R79.1).")
            elif calit is not None and calit != 1 and sb is not None:
                er.append(pb + "Calit_pers<>1: stare_ben trebuie să fie null (DUK regula R79.2).")
            nat = b.get("nationalitate")
            if nat and str(nat).strip().upper() not in _NATIONALITATI:
                er.append(pb + "Nationalitate neregasita în nomenclator.")
            if b.get("data_nasterii") and _parse_data(b.get("data_nasterii")) is None:
                er.append(pb + "Data_nasterii format ZZ.LL.AAAA.")
            if calit in (1, 3, 4) and stat and stat != "RO":
                raportabila = True
        if pers and not raportabila:
            er.append(pp + "trebuie o persoana cu Stat_SR<>RO și Calit_pers în (1,3,4) "
                           "(persoana raportabila; DUK regula polita).")

        for ei, ev in enumerate(_evenimente(pol), 1):
            pe = pp + "eveniment #%d: " % ei
            if not str(ev.get("id_eveniment") or "").strip():
                er.append(pe + "lipsă id_eveniment.")
            tev = _int_or_none(ev.get("tip_ev"))
            if not _in_range(tev, _R_TIP_EV):
                er.append(pe + "Tip_ev obligatoriu în (1..25).")
            elif tp == 1 and tev in (3, 4, 8):
                er.append(pe + "tip_polita=1: Tip_ev nu poate fi 3,4,8 (DUK regula R114).")
            if not _in_range(ev.get("periodicitate"), _R_PERIODICITATE):
                er.append(pe + "Periodicitate obligatoriu în (1..3).")
            if not _in_range(ev.get("regim_ev"), _R_REGIM_EV):
                er.append(pe + "Regim_ev obligatoriu în (1,2).")
            if not _in_range(ev.get("mod_imp1"), _R_MOD_IMP1):
                er.append(pe + "Mod_imp1 obligatoriu în (1..6).")
            if not _in_range(ev.get("mod_imp2"), _R_MOD_IMP2):
                er.append(pe + "Mod_imp2 obligatoriu în (1,2).")
            sev = _int_or_none(ev.get("status_ev"))
            if tev in range(3, 10) and sev != 2:
                er.append(pe + "Tip_ev în 3..9 impune Status_ev=2 (DUK regula R116).")
            elif tev in range(10, 18) and sev is None:
                er.append(pe + "Tip_ev în 10..17 impune Status_ev (DUK regula R117).")
            elif tev is not None and (tev in (1, 2) or tev >= 18) and sev is not None:
                er.append(pe + "Tip_ev în (1,2,18..25): Status_ev trebuie null (DUK regula R115).")
            if tev in range(10, 18) and not _in_range(ev.get("tip_transfer"), _R_TIP_TRANSFER):
                er.append(pe + "Tip_ev în 10..17 impune Tip_transfer (DUK regula R118).")
            for sfx, rc in (("3", ("R95", "R96", "R97")), ("5", ("R103", "R104", "R105"))):
                if _dec2(ev.get("suma" + sfx)) > 0:
                    if str(ev.get("moneda" + sfx) or "").strip().upper() not in _MONEZI:
                        er.append(pe + "Suma%s>0 impune Moneda%s în nomenclator (DUK regula %s)."
                                  % (sfx, sfx, rc[0]))
                    if _parse_data(ev.get("data" + sfx)) is None:
                        er.append(pe + "Suma%s>0 impune Data%s (DUK regula %s)." % (sfx, sfx, rc[1]))
                    if not str(ev.get("cont" + sfx) or "").strip():
                        er.append(pe + "Suma%s>0 impune Cont%s (DUK regula %s)." % (sfx, sfx, rc[2]))

        for vi, vc in enumerate(_valcap(pol), 1):
            pv = pp + "val_cap #%d: " % vi
            comp = [bool(_int_or_none(vc.get("tip_val_capital")) is not None and str(vc.get("tip_val_capital")).strip()),
                    vc.get("val_capital") not in (None, ""),
                    bool(str(vc.get("moneda_capital") or "").strip())]
            if any(comp) and not all(comp):
                er.append(pv + "tip_val_capital, val_capital și moneda_capital: toate sau niciunul "
                               "(DUK regula R110).")
            if comp[0] and not _in_range(vc.get("tip_val_capital"), _R_TIP_VAL_CAP):
                er.append(pv + "tip_val_capital în (1..4).")
            if comp[2] and str(vc.get("moneda_capital")).strip().upper() not in _MONEZI:
                er.append(pv + "moneda_capital în nomenclator.")
    return er


def _add(lst, name, val, lim=None):
    lst.append('%s="%s"' % (name, _esc(val, lim)))


def build_xml(prof, an, luna, manual):
    d_rec = int(manual.get("d_rec") or 0)
    c = calcul_d403(manual)
    h = []
    h.append('an="%d"' % int(an))
    h.append('luna="12"')  # raportare anuala: luna fixata la 12 (DUK regula luna=12)
    h.append('d_rec="%d"' % d_rec)
    _add(h, "nume_declar", manual.get("nume_declar"), 75)
    _add(h, "prenume_declar", manual.get("prenume_declar"), 75)
    _add(h, "functie_declar", manual.get("functie_declar"), 50)
    h.append('cif="%s"' % _cif(manual.get("cif")))
    _add(h, "Den_rap", manual.get("den_rap"), 200)
    h.append('Judet_rap="%s"' % _esc(manual.get("judet_rap"), 2))
    if str(manual.get("sector_rap") or "").strip():
        h.append('Sector_rap="%d"' % int(manual.get("sector_rap")))
    _add(h, "Localitate_rap", manual.get("localitate_rap"), 75)
    _add(h, "Adresa_rap", manual.get("adresa_rap"), 200)
    h.append('Tara_rap="%s"' % _esc(str(manual.get("tara_rap")).upper(), 2))
    h.append('Forma_juridica="%s"' % _esc(manual.get("forma_juridica"), 2))
    h.append('Tip_adresa1="%d"' % int(manual.get("tip_adresa1")))
    h.append('Sediu_DN1="%d"' % int(manual.get("sediu_dn1")))
    if str(manual.get("den_repr1") or "").strip():
        _add(h, "Den_repr1", manual.get("den_repr1"), 200)
    if _cif(manual.get("cif_repr1")):
        h.append('CIF_repr1="%s"' % _cif(manual.get("cif_repr1")))
    if str(manual.get("adr_repr1") or "").strip():
        _add(h, "Adr_repr1", manual.get("adr_repr1"), 200)
    h.append('nr_pers="%d"' % c["nr_pers"])
    h.append('totalPlata_A="%d"' % c["totalPlata_A"])
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<declaratie403 xmlns="%s" %s>' % (NS, " ".join(h))]

    for pi, pol in enumerate(_polite(manual), 1):
        pa = []
        _add(pa, "id_polita", pol.get("id_polita") or pi, 15)
        if str(pol.get("nr_polita") or "").strip():
            _add(pa, "nr_polita", pol.get("nr_polita"), 50)
        pa.append('tip_polita="%d"' % int(pol.get("tip_polita")))
        pa.append('trat_fisc_polita="%d"' % int(pol.get("trat_fisc_polita")))
        if pol.get("frecv_plata") not in (None, ""):
            pa.append('frecv_plata="%d"' % int(pol.get("frecv_plata")))
        di = _parse_data(pol.get("data_i_polita"))
        if di:
            pa.append('data_I_polita="%s"' % _fmt_data(di))
        ds = _parse_data(pol.get("data_s_polita"))
        if ds:
            pa.append('data_S_polita="%s"' % _fmt_data(ds))
        if pol.get("tip_termen_polita") not in (None, ""):
            pa.append('tip_termen_polita="%d"' % int(pol.get("tip_termen_polita")))
        if pol.get("ani_contrib_polita") not in (None, ""):
            pa.append('ani_contrib_polita="%d"' % int(pol.get("ani_contrib_polita")))
        pa.append('tip_benef_polita="%d"' % int(pol.get("tip_benef_polita")))
        if pol.get("ani_benef_polita") not in (None, ""):
            pa.append('ani_benef_polita="%d"' % int(pol.get("ani_benef_polita")))
        if pol.get("tip_optiune") not in (None, ""):
            pa.append('tip_optiune="%d"' % int(pol.get("tip_optiune")))
        parts.append("  <polita %s>" % " ".join(pa))

        # ordinea elementelor din <polita> (DECTag _taguri): val_cap, persoana, eveniment
        for vc in _valcap(pol):
            if vc.get("val_capital") in (None, ""):
                continue
            va = []
            va.append('tip_val_capital="%d"' % int(vc.get("tip_val_capital")))
            va.append('val_capital="%d"' % _intval(vc.get("val_capital")))
            va.append('moneda_capital="%s"' % _esc(str(vc.get("moneda_capital")).upper(), 3))
            parts.append("    <val_cap %s/>" % " ".join(va))

        for bi, b in enumerate(_persoane(pol), 1):
            ba = []
            _add(ba, "id_pers", b.get("id_pers") or bi, 15)
            ba.append('Calit_pers="%d"' % int(b.get("calit_pers")))
            ba.append('Tip_pers="%d"' % int(b.get("tip_pers")))
            if str(b.get("den_pers") or "").strip():
                _add(ba, "Den_pers", b.get("den_pers"), 200)
            if str(b.get("nume_pers") or "").strip():
                _add(ba, "Nume_pers", b.get("nume_pers"), 40)
            if str(b.get("pren_pers") or "").strip():
                _add(ba, "Pren_pers", b.get("pren_pers"), 40)
            ba.append('Stat_SR="%s"' % _esc(str(b.get("stat_sr")).upper(), 2))
            _add(ba, "Localitate_SR", b.get("localitate_sr"), 75)
            if str(b.get("strada_sr") or "").strip():
                _add(ba, "Strada_SR", b.get("strada_sr"), 50)
            if str(b.get("nr_sr") or "").strip():
                _add(ba, "Nr_SR", b.get("nr_sr"), 10)
            if str(b.get("codp_sr") or "").strip():
                _add(ba, "Codp_SR", b.get("codp_sr"), 20)
            if _cif(b.get("cif_rom")):
                ba.append('CIF_rom="%s"' % _cif(b.get("cif_rom")))
            if str(b.get("cif_sr") or "").strip():
                _add(ba, "CIF_SR", b.get("cif_sr"), 20)
            if b.get("nationalitate"):
                ba.append('Nationalitate="%s"' % _esc(str(b.get("nationalitate")).upper(), 2))
            dn = _parse_data(b.get("data_nasterii"))
            if dn:
                ba.append('Data_nasterii="%s"' % _fmt_data(dn))
            if str(b.get("act_id") or "").strip():
                _add(ba, "Act_id", b.get("act_id"), 50)
            tip_pers = int(b.get("tip_pers"))
            if tip_pers == 1:
                ba.append('In_calit="%d"' % int(b.get("in_calit")))
                ba.append('Tip_adresa2="%d"' % int(b.get("tip_adresa2")))
            if tip_pers == 2:
                ba.append('Tip_PJ="%d"' % int(b.get("tip_pj")))
                ba.append('Sediu_DN2="%d"' % int(b.get("sediu_dn2")))
                if b.get("tip_repr2") not in (None, ""):
                    ba.append('Tip_repr2="%d"' % int(b.get("tip_repr2")))
                if str(b.get("den_repr2") or "").strip():
                    _add(ba, "Den_repr2", b.get("den_repr2"), 200)
                if _cif(b.get("cif_repr2")):
                    ba.append('CIF_repr2="%s"' % _cif(b.get("cif_repr2")))
                if str(b.get("adr_repr2") or "").strip():
                    _add(ba, "Adr_repr2", b.get("adr_repr2"), 200)
            calit = int(b.get("calit_pers"))
            if b.get("tip_ben_plat_contr") not in (None, ""):
                ba.append('tip_ben_plat_contr="%d"' % int(b.get("tip_ben_plat_contr")))
            ba.append('unic_mm="%d"' % int(b.get("unic_mm")))
            ba.append('cota_parte="%s"' % ("%.2f" % _dec2(b.get("cota_parte"))))
            if calit in (2, 3, 4):
                ba.append('rel_ben="%d"' % int(b.get("rel_ben")))
            if calit == 1:
                ba.append('stare_ben="%d"' % int(b.get("stare_ben")))
            parts.append("    <persoana %s/>" % " ".join(ba))

        for ei, ev in enumerate(_evenimente(pol), 1):
            ea = []
            _add(ea, "id_eveniment", ev.get("id_eveniment") or ei, 15)
            da = _parse_data(ev.get("data_act"))
            if da:
                ea.append('Data_Act="%s"' % _fmt_data(da))
            dr = _parse_data(ev.get("data_ref"))
            if dr:
                ea.append('Data_Ref="%s"' % _fmt_data(dr))
            ea.append('Tip_ev="%d"' % int(ev.get("tip_ev")))
            if ev.get("tip_transfer") not in (None, ""):
                ea.append('Tip_transfer="%d"' % int(ev.get("tip_transfer")))
            ea.append('Periodicitate="%d"' % int(ev.get("periodicitate")))
            if ev.get("status_ev") not in (None, ""):
                ea.append('Status_ev="%d"' % int(ev.get("status_ev")))
            ea.append('Regim_ev="%d"' % int(ev.get("regim_ev")))
            if ev.get("tip_baza") not in (None, ""):
                ea.append('Tip_baza="%d"' % int(ev.get("tip_baza")))
            s3 = _dec2(ev.get("suma3"))
            if s3 > 0:
                ea.append('Suma3="%s"' % ("%.2f" % s3))
                ea.append('Moneda3="%s"' % _esc(str(ev.get("moneda3")).upper(), 3))
                ea.append('Data3="%s"' % _fmt_data(_parse_data(ev.get("data3"))))
                _add(ea, "Cont3", ev.get("cont3"), 34)
            ea.append('Mod_imp1="%d"' % int(ev.get("mod_imp1")))
            ea.append('Mod_imp2="%d"' % int(ev.get("mod_imp2")))
            s5 = _dec2(ev.get("suma5"))
            if s5 > 0:
                ea.append('Suma5="%s"' % ("%.2f" % s5))
                ea.append('Moneda5="%s"' % _esc(str(ev.get("moneda5")).upper(), 3))
                ea.append('Data5="%s"' % _fmt_data(_parse_data(ev.get("data5"))))
                _add(ea, "Cont5", ev.get("cont5"), 34)
            parts.append("    <eveniment %s/>" % " ".join(ea))

        parts.append("  </polita>")
    parts.append("</declaratie403>")
    return "\n".join(parts) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = 12  # raportare anuala; luna raportarii = 12 (fix)
    prof = pull(conn, schema, perioada)
    prof["an"] = an
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D403 nu se poate genera: " + " ".join(er))
    c = calcul_d403(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat403(an=an, luna=luna, total_plata_a=c["totalPlata_A"],
                      nr_persoane=c["nr_pers"], nr_polite=c["nr_polite"],
                      nr_evenimente=c["nr_evenimente"])
    return xml, res
