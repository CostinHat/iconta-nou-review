"""core/d402.py - D402: Declaratie informativa privind veniturile de natura salariala
sau asimilate salariilor, inclusiv remuneratiile administratorilor si ale altor persoane
asimilate acestora, rezidenti ai altor state membre ale UE, realizate in Romania (schimb
automat de informatii - DAC1). Cod M.F.P. 14.13.01.13/1.

Declaratie INFORMATIVA depusa de platitorul roman de venituri (angajator/entitate) pentru
beneficiari NEREZIDENTI - persoane fizice rezidente in alt stat membru UE - carora le-a platit
in Romania venituri salariale/asimilate (indemnizatii administratori, remuneratii directori
in baza contractului de mandat, avantaje etc.). Termen: ultima zi a lunii februarie pentru
anul expirat (OMFP 2727/2015).

SURSA STRUCTURII = XSD OFICIAL ANAF (arbitrul, DUKIntegrator / D402Validator.jar). Structura
in vigoare (namespace declaratie:v1, version 1.02, universalCode D402_A1.0.0) a fost CITITA din:
  - anaf_surse/d402_20160226.xsd            (schema oficiala static.anaf.ro; sha256 in
                                             d402_surse_sha256.txt)
  - anaf_surse/structuraXML_D402_2022.pdf   (structura + nomenclatoare N1/N3/N4 + corelatii)
  - bytecode D402Validator.jar (d402validator/v0/{Declaratie402,Beneficiar,Venit}) - confirmare
    radacina `declaratie402`, campuri, domenii enum, mesajele de validare R49 si R50.
Toate campurile si domeniile de mai jos sunt PROBATE camp cu camp pe validatorul oficial (DUK).

Ierarhie: <declaratie402> > <beneficiar> (1-n aparitii) > <venit> (1-n aparitii).

Reguli probate (citari "DUK regula ..."):
  - R14 : totalPlata_A = suma tuturor Suma_venit (suma de control).
  - R34 : Impozit_venit >= 0.
  - R39 : anul(Data_I) <= anul raportarii.
  - R40 : daca Data_S completat -> Data_S >= Data_I si anul(Data_S) = anul raportarii.
  - R43 : declaratie initiala (d_rec=0) => Suma_venit > 0; rectificativa (d_rec=1) => >= 0.
  - R49.1: Categ_B=1 (dependent)      => Tip_venit NU in (1,2,3).
  - R49.2: Categ_B=2 (alte categorii) => Tip_venit NU in (5,6,8,9,10).
  - R50 : <beneficiar> unic dupa CIF_Rom (fara aparitii multiple pe acelasi CIF_Rom).
  - Data format ZZ.LL.AAAA (dd.mm.yyyy); luna raportare = 12 (fix, camp de raportare anuala).

Nomenclatoare (din XSD/PDF): Tip_P(1-4), Forma_jurid_P(1-8), Nationalitate=N3 (toate statele),
Stat_R=N1 (state membre UE), Moneda_venit=N4 (CZK,DKK,EUR,GBP,HRK,HUF,PLN,RON,SKK,SEK,USD),
Calitate_B(1-4: 1-interes personal, 2-scop afaceri, 3-ambele, 4-altele), Tip_adr(1-3),
Categ_B(1-dependent, 2-alte categorii), Tip_venit(1-14), Per_venit(1-5), Regim_fisc(1-3),
DA_NU(1=venit declarat in D112, 2=nu).

Declaratie MANUALA: platitorul furnizeaza TOATE datele prin `manual` (aplicatia nu are registru
de beneficiari nerezidenti). NU se fabrica valori. `conn` nu e folosit (pull returneaza {}),
deci genereaza(conn=None, ...) functioneaza.

NEPOPULAT deliberat (optional in XSD, se completeaza de platitor la nevoie, aceeasi metoda):
Nationalitate, Data_nasterii, NIF_R, Act_id, Strada_R, Nr_R, Codp_R, Data_S, Cont.

Contract dXXX: pull / erori_generare / calcul_d402 / build_xml / genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d402:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
_CUI_W = [7, 5, 3, 2, 1, 7, 5, 3, 2]  # cheia de control CUI ANAF

# Nomenclatoare (domenii enum) - XSD d402_20160226.xsd
_STATE_UE = frozenset(("AT", "BE", "BG", "CZ", "CY", "HR", "DK", "EE", "DE", "EL", "FI",
                       "FR", "IE", "IT", "LV", "LU", "LT", "MT", "GB", "NL", "PL", "PT",
                       "SI", "SK", "ES", "SE", "HU"))  # N1 - Stat_R
_MONEDE = frozenset(("CZK", "DKK", "EUR", "GBP", "HRK", "HUF", "PLN", "RON", "SKK",
                     "SEK", "USD"))  # N4 - Moneda_venit
_TARI = frozenset((  # N3 - Nationalitate (Str_tariSType din XSD)
    "MM", "NA", "NR", "NP", "NL", "AN", "AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI",
    "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE",
    "BZ", "BJ", "BM", "BT", "BO", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI",
    "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CG",
    "CD", "CK", "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG",
    "SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA",
    "GM", "GE", "DE", "GH", "GI", "EL", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW",
    "GY", "HT", "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM",
    "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA",
    "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV",
    "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS",
    "MA", "MZ", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW",
    "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU",
    "RW", "BL", "SH", "KN", "LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS",
    "SC", "SL", "SG", "SK", "SI", "SB", "SO", "ZA", "GS", "ES", "LK", "SD", "SR", "SJ",
    "SZ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN",
    "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VE",
    "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW", "IC", "CW", "BQ", "NM", "XI", "XJ"))
_TIP_P = frozenset((1, 2, 3, 4))
_FORMA_JURID = frozenset((1, 2, 3, 4, 5, 6, 7, 8))
_CALITATE_B = frozenset((1, 2, 3, 4))
_TIP_ADR = frozenset((1, 2, 3))
_CATEG_B = frozenset((1, 2))
_TIP_VENIT = frozenset(range(1, 15))
_PER_VENIT = frozenset((1, 2, 3, 4, 5))
_REGIM_FISC = frozenset((1, 2, 3))
_DA_NU = frozenset((1, 2))
# R49 - corelatie Categ_B x Tip_venit (Tip_venit INTERZIS pe fiecare categorie)
_TIP_INTERZIS = {1: frozenset((1, 2, 3)), 2: frozenset((5, 6, 8, 9, 10))}


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cnp_valid(cnp):
    """CNP / NIF Romania: 13 cifre, prima nenula, cifra de control (CIF_Rom = CnpSType)."""
    cnp = _cif(cnp)
    if len(cnp) != 13 or cnp[0] == "0":
        return False
    s = sum(int(cnp[i]) * _CNP_W[i] for i in range(12))
    c = s % 11
    c = 1 if c == 10 else c
    return c == int(cnp[12])


def _cui_valid(cui):
    """CUI platitor roman: 2-10 cifre, cheia de control ANAF (753217532)."""
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


@dataclass
class Rezultat402:
    an: int
    luna: int = 12
    total_plata_a: int = 0
    nr_beneficiari: int = 0
    nr_venituri: int = 0
    avertismente: list = field(default_factory=list)


def _venituri(benef):
    v = benef.get("venituri")
    return list(v) if v else []


def _int_in(val, dom):
    try:
        return int(val) in dom
    except (TypeError, ValueError):
        return False


def calcul_d402(manual):
    """DUK regula R14: totalPlata_A = suma tuturor Suma_venit din toate <venit>."""
    total = 0
    nv = 0
    for b in (manual.get("beneficiari") or []):
        for v in _venituri(b):
            total += _intval(v.get("suma_venit"))
            nv += 1
    return {"totalPlata_A": total, "nr_venituri": nv}


def pull(conn, schema, perioada):
    """D402 e MANUALA: platitorul furnizeaza beneficiarii nerezidenti si veniturile.
    Aplicatia nu are registru de nerezidenti; `conn` nu e folosit (merge conn=None)."""
    return {}


def erori_generare(prof, manual):
    er = []
    an = int(prof.get("an") or 0)
    # --- antet platitor de venit (sectiunea A) ---
    if not (_cui_valid(manual.get("cif")) or _cnp_valid(manual.get("cif"))):
        er.append("CIF platitor (cif) invalid - astept CUI (2-10 cifre) sau CNP (13 cifre).")
    for camp, et in (("den_p", "Denumire platitor (Den_P)"),
                     ("adresa_p", "Adresa platitor (Adresa_P)"),
                     ("nume_declar", "Nume declarant (nume_declar)"),
                     ("prenume_declar", "Prenume declarant (prenume_declar)"),
                     ("functie_declar", "Functie declarant (functie_declar)")):
        if not str(manual.get(camp) or "").strip():
            er.append("Lipsa " + et + ".")
    if not _int_in(manual.get("tip_p"), _TIP_P):
        er.append("Tip_P (tip_p) obligatoriu in (1,2,3,4).")
    if not _int_in(manual.get("forma_jurid_p"), _FORMA_JURID):
        er.append("Forma_jurid_P (forma_jurid_p) obligatoriu in (1..8).")
    try:
        d_rec = int(manual.get("d_rec") or 0)
    except (TypeError, ValueError):
        d_rec = -1
    if d_rec not in (0, 1):
        er.append("d_rec obligatoriu 0 (initiala) sau 1 (rectificativa).")

    # --- beneficiari nerezidenti (sectiunea C) ---
    benefs = manual.get("beneficiari") or []
    if not benefs:
        er.append("Cel putin un <beneficiar> (beneficiari) este obligatoriu.")
    cifuri = []
    for i, b in enumerate(benefs, 1):
        p = "beneficiar #%d: " % i
        if not str(b.get("nume") or "").strip():
            er.append(p + "lipsa Nume (nume).")
        if not _cnp_valid(b.get("cif_rom")):
            er.append(p + "CIF_Rom (cif_rom) invalid - CNP/NIF Romania 13 cifre "
                          "(DUK regula verificare cif(13)).")
        else:
            cifuri.append(_cif(b.get("cif_rom")))
        if str(b.get("stat_r") or "").strip().upper() not in _STATE_UE:
            er.append(p + "Stat_R (stat_r) obligatoriu, stat membru UE (N1).")
        if not str(b.get("localitate_r") or "").strip():
            er.append(p + "lipsa Localitate_R (localitate_r).")
        if not _int_in(b.get("calitate_b"), _CALITATE_B):
            er.append(p + "Calitate_B (calitate_b) obligatoriu in (1,2,3,4).")
        if not _int_in(b.get("tip_adr"), _TIP_ADR):
            er.append(p + "Tip_adr (tip_adr) obligatoriu in (1,2,3).")
        if not _int_in(b.get("categ_b"), _CATEG_B):
            er.append(p + "Categ_B (categ_b) obligatoriu in (1,2).")
        if _intval(b.get("impozit_venit")) < 0:
            er.append(p + "Impozit_venit (impozit_venit) >= 0 (DUK regula R34).")
        nat = b.get("nationalitate")
        if nat and str(nat).strip().upper() not in _TARI:
            er.append(p + "Nationalitate (nationalitate) neregasita in N3.")
        if b.get("data_nasterii") and _parse_data(b.get("data_nasterii")) is None:
            er.append(p + "Data_nasterii format ZZ.LL.AAAA.")
        try:
            categ = int(b.get("categ_b"))
        except (TypeError, ValueError):
            categ = None
        vs = _venituri(b)
        if not vs:
            er.append(p + "cel putin un <venit> (venituri) este obligatoriu.")
        for j, v in enumerate(vs, 1):
            pv = p + "venit #%d: " % j
            tv = None
            if not _int_in(v.get("tip_venit"), _TIP_VENIT):
                er.append(pv + "Tip_venit (tip_venit) obligatoriu in (1..14).")
            else:
                tv = int(v.get("tip_venit"))
                if categ in _TIP_INTERZIS and tv in _TIP_INTERZIS[categ]:
                    er.append(pv + "Categ_B=%d incompatibil cu Tip_venit=%d (DUK regula R49.%d)."
                              % (categ, tv, 1 if categ == 1 else 2))
            if not _int_in(v.get("da_nu"), _DA_NU):
                er.append(pv + "DA_NU (da_nu) obligatoriu in (1=da, 2=nu).")
            di = _parse_data(v.get("data_i"))
            if di is None:
                er.append(pv + "Data_I (data_i) obligatoriu, format ZZ.LL.AAAA.")
            elif di[0] > an:
                er.append(pv + "anul din Data_I > anul raportarii (DUK regula R39).")
            ds = _parse_data(v.get("data_s"))
            if v.get("data_s") and ds is None:
                er.append(pv + "Data_S format ZZ.LL.AAAA.")
            elif ds is not None:
                if ds[0] != an:
                    er.append(pv + "anul din Data_S <> anul raportarii (DUK regula R40).")
                if di is not None and ds < di:
                    er.append(pv + "Data_S < Data_I (DUK regula R40).")
            if not _int_in(v.get("per_venit"), _PER_VENIT):
                er.append(pv + "Per_venit (per_venit) obligatoriu in (1..5).")
            if not _int_in(v.get("regim_fisc"), _REGIM_FISC):
                er.append(pv + "Regim_fisc (regim_fisc) obligatoriu in (1,2,3).")
            sv = _intval(v.get("suma_venit"))
            if d_rec == 0 and sv <= 0:
                er.append(pv + "Suma_venit > 0 intr-o declaratie initiala (DUK regula R43).")
            elif sv < 0:
                er.append(pv + "Suma_venit >= 0 (DUK regula R43).")
            if str(v.get("moneda_venit") or "").strip().upper() not in _MONEDE:
                er.append(pv + "Moneda_venit (moneda_venit) obligatoriu in N4 (EUR,RON,USD,...).")
    dup = sorted(set(x for x in cifuri if cifuri.count(x) > 1))
    if dup:
        er.append("CIF_Rom duplicat intre beneficiari: %s (DUK regula R50)." % ", ".join(dup))
    return er


def build_xml(prof, an, luna, manual):
    d_rec = int(manual.get("d_rec") or 0)
    total = calcul_d402(manual)["totalPlata_A"]
    h = []
    h.append('an="%d"' % int(an))
    h.append('luna="12"')  # camp de raportare anuala: luna fixata la 12 (DUK regula luna=12)
    h.append('d_rec="%d"' % d_rec)
    h.append('cif="%s"' % _cif(manual.get("cif")))
    h.append('Den_P="%s"' % _esc(manual.get("den_p"), 200))
    h.append('Adresa_P="%s"' % _esc(manual.get("adresa_p"), 200))
    h.append('Tip_P="%d"' % int(manual.get("tip_p")))
    h.append('Forma_jurid_P="%d"' % int(manual.get("forma_jurid_p")))
    h.append('nume_declar="%s"' % _esc(manual.get("nume_declar"), 75))
    h.append('prenume_declar="%s"' % _esc(manual.get("prenume_declar"), 75))
    h.append('functie_declar="%s"' % _esc(manual.get("functie_declar"), 50))
    h.append('totalPlata_A="%d"' % total)
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<declaratie402 xmlns="%s" %s>' % (NS, " ".join(h))]
    for i, b in enumerate(manual.get("beneficiari") or [], 1):
        ba = []
        ba.append('id_benef="%d"' % int(b.get("id_benef") or i))
        ba.append('Nume="%s"' % _esc(b.get("nume"), 200))
        if b.get("nationalitate"):
            ba.append('Nationalitate="%s"' % _esc(str(b.get("nationalitate")).upper(), 2))
        dn = _parse_data(b.get("data_nasterii"))
        if dn:
            ba.append('Data_nasterii="%s"' % _fmt_data(dn))
        if b.get("nif_r"):
            ba.append('NIF_R="%s"' % _esc(b.get("nif_r"), 20))
        if b.get("act_id"):
            ba.append('Act_id="%s"' % _esc(b.get("act_id"), 50))
        ba.append('Stat_R="%s"' % _esc(str(b.get("stat_r")).upper(), 2))
        ba.append('Localitate_R="%s"' % _esc(b.get("localitate_r"), 75))
        if b.get("strada_r"):
            ba.append('Strada_R="%s"' % _esc(b.get("strada_r"), 50))
        if b.get("nr_r"):
            ba.append('Nr_R="%s"' % _esc(b.get("nr_r"), 10))
        if b.get("codp_r"):
            ba.append('Codp_R="%s"' % _esc(b.get("codp_r"), 20))
        ba.append('CIF_Rom="%s"' % _cif(b.get("cif_rom")))
        ba.append('Calitate_B="%d"' % int(b.get("calitate_b")))
        ba.append('Tip_adr="%d"' % int(b.get("tip_adr")))
        ba.append('Categ_B="%d"' % int(b.get("categ_b")))
        ba.append('Impozit_venit="%d"' % _intval(b.get("impozit_venit")))
        parts.append("  <beneficiar %s>" % " ".join(ba))
        for j, v in enumerate(_venituri(b), 1):
            va = []
            va.append('id_venit="%d"' % int(v.get("id_venit") or j))
            va.append('Tip_venit="%d"' % int(v.get("tip_venit")))
            va.append('DA_NU="%d"' % int(v.get("da_nu")))
            va.append('Data_I="%s"' % _fmt_data(_parse_data(v.get("data_i"))))
            ds = _parse_data(v.get("data_s"))
            if ds:
                va.append('Data_S="%s"' % _fmt_data(ds))
            va.append('Per_venit="%d"' % int(v.get("per_venit")))
            va.append('Regim_fisc="%d"' % int(v.get("regim_fisc")))
            va.append('Suma_venit="%d"' % _intval(v.get("suma_venit")))
            va.append('Moneda_venit="%s"' % _esc(str(v.get("moneda_venit")).upper(), 3))
            if v.get("cont"):
                va.append('Cont="%s"' % _esc(v.get("cont"), 34))
            parts.append("    <venit %s/>" % " ".join(va))
        parts.append("  </beneficiar>")
    parts.append("</declaratie402>")
    return "\n".join(parts) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = 12  # raportare anuala; luna raportarii = 12 (fix)
    prof = pull(conn, schema, perioada)
    prof["an"] = an
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D402 nu se poate genera: " + " ".join(er))
    c = calcul_d402(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat402(an=an, luna=luna, total_plata_a=c["totalPlata_A"],
                      nr_beneficiari=len(manual.get("beneficiari") or []),
                      nr_venituri=c["nr_venituri"])
    return xml, res
