"""core/d169.py - D169: Declaratie de inregistrare a contractelor de fiducie sau a constructiilor
juridice similare fiduciilor si a modificarilor/incetarii acestora.

Temei: Legea nr.129/2019 pentru prevenirea si combaterea spalarii banilor si finantarii terorismului
(Registrul central al fiduciilor si al constructiilor juridice similare fiduciilor, tinut de ANAF) coroborata
cu Codul de procedura fiscala (Legea nr.207/2015). Declaratia se depune de fiduciarul desemnat.

ATENTIE - a NU se confunda cu D169n (core/d169n.py): D169n este declaratia de NECONCORDANTE privind
beneficiarul real (OPANAF 2175/2025 Anexa nr.6, namespace ...:d169n:...). D169 (namespace cu D169 MAJUSCUL,
...:D169:...) este declaratia de INREGISTRARE a contractului de fiducie, cu alta radacina si alta structura
(patru sectiuni repetabile: fiduciar, constituitor, beneficiar, benefR).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul peste anexe, DUKIntegrator / D169Validator.jar).
Radacina, atributele si sectiunile repetabile au fost CITITE din bytecode (d169validator/v0/D169.class,
Fiduciar.class, Constituitor.class, Beneficiar.class, BenefR.class) si PROBATE camp cu camp pe validator.
Confirmat:
  - RADACINA: <D169> (nu `declaratie`/`declaratie169`); namespace mfp:anaf:dgti:D169:declaratie:v1.
  - Sectiuni repetabile, in ordinea din schema: <fiduciar>, <constituitor>, <beneficiar>, <benefR>;
    fiecare cu min. 1 aparitie (obligatorie), max. nelimitat.
  - Radacina - datele declaratiei si ale sectiunii I (inregistrare): an, luna, nume+functie (semnatar),
    bifa_modif, bifa_incet (tipul operatiei), cif (CIF-ul fiduciarului declarant), nr_contract_I,
    data_contract_I, data1_I (inceput), data2_I (sfarsit, optional), ani_I/luni_I/zile_I (durata),
    scop_fiducie; bifa1i..bifa4i (optionale). Sectiunea M (modificare): nr_contract_M, data_contract_M,
    data1_M, data2_M, ani_M, luni_M, zile_M, bifa1m..bifa4m, modificari. Sectiunea incetare: nr_doc,
    data_doc, motiv_incetare.
  - fiduciar: bifa_F (1=fiduciar declarant), den_F, cif_F, judet_F, sector_F, localit_F, adresa_F, codp_F,
    tel_F, fax_F, email_F, tara_F.
  - constituitor: den_Ct, cif_Ct, judet_Ct, sector_Ct, localit_Ct, adresa_Ct, codp_Ct, tel_Ct, fax_Ct,
    email_Ct, tara_Ct.
  - beneficiar (beneficiarul fiduciei): den_B1, cif_B1, judet_B1, sector_B1, localit_B1, adresa_B1, codp_B1,
    tel_B1, fax_B1, email_B1, tara_B1.
  - benefR (beneficiarul real): den_B, cif_B, data_nasterii_B, actId_B, stat_cetatenie_B, stat_resedinta_B,
    adresa_B, mod_control_B, cal1_B..cal4_B (calitatea de beneficiar real), natura.

Reguli citite din validator si PROBATE camp cu camp:
  - DUK regula luna: luna trebuie sa fie 12 (valoare fixa; '8' -> "nu se incadreaza in intervalul cerut").
  - DUK regula judet: codul de judet se da pe DOUA cifre ('1' -> "nu se afla in lista"; '01' acceptat).
  - DUK regula fiduciar declarant: cel putin un <fiduciar> trebuie sa aiba cif_F = cif (radacina) si bifa_F=1
    ("Nu s-a gasit niciun fiduciar declarant printre fiduciari" / "nu exista niciun cif_F=cif").
  - DUK regula R83: daca tara_Ct este null atunci judet_Ct trebuie sa fie != null (idem pentru beneficiar B1).
  - DUK regula sector judet 40: daca judet=40 (Bucuresti) atunci sector trebuie sa fie 1-6.
  - DUK regula cif unic: cif_F / cif_Ct / cif_B1 / cif_B trebuie sa fie unice in cadrul sectiunii lor.
  - DUK regula cif_B1: daca are 13 cifre e verificat drept CNP; alte lungimi (2-10) sunt acceptate drept CUI.
  - DUK regula data2>=data1: daca data1_I si data2_I (resp. _M) sunt completate, data2 >= data1.
  - DUK regula bifa_modif: daca bifa_modif=1 se completeaza nr_contract_M, data_contract_M, data1_M,
    data2_M, ani_M, luni_M, zile_M, modificari si cel putin o bifa (bifa1m..bifa4m).
  - DUK regula bifa_incet: daca bifa_incet=1 se completeaza nr_doc, data_doc, motiv_incetare.

Modulul implementeaza CAZUL PRINCIPAL, PROBAT DUK VALID: INREGISTRAREA unui contract (bifa_modif=0,
bifa_incet=0, sectiunea I). LIMITARI documentate (nu se ghicesc, se adauga pe aceeasi metoda la nevoie):
modificarea (bifa_modif=1, campurile _M) si incetarea (bifa_incet=1, nr_doc/data_doc/motiv_incetare) - campurile
sunt cunoscute din bytecode dar nu au fost inca probate DUK.

NEPOPULAT deliberat: nu exista niciun camp monetar in schema (deci nici rotunjire) - declaratia nu contine
sume, doar durate intregi (ani/luni/zile). Registrul central al fiduciilor nu e in aplicatie, deci datele nu
se pot pre-completa automat; `pull` nu atinge baza -> `genereaza` merge si cu conn=None.

Contract dXXX: pull/erori_generare/calcul_d169/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:D169:declaratie:v1"
LUNA_FIXA = 12  # DUK regula luna: perioada declaratiei = luna 12 (valoare fixa acceptata de validator)

_NEDIGIT = re.compile(r"\D")
_DATA_RE = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")
_DATA_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_JUDET_BUCURESTI = "40"  # DUK regula sector judet 40
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cnp_valid(cnp):
    cnp = _cif(cnp)
    if len(cnp) != 13:
        return False
    s = sum(int(cnp[i]) * _CNP_W[i] for i in range(12))
    c = s % 11
    c = 1 if c == 10 else c
    return c == int(cnp[12])


def _cif_pf_pj_ok(x):
    """cod de identificare fiscala pentru persoana fizica SAU juridica:
    13 cifre -> verificat drept CNP (DUK regula cif_B1); alte lungimi -> CUI de 2-10 cifre."""
    v = _cif(x)
    if len(v) == 13:
        return _cnp_valid(v)
    return 2 <= len(v) <= 10


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _data(x):
    """Normalizeaza la zz.ll.aaaa (formatul acceptat de validator). Accepta si aaaa-ll-zz. Fara strftime."""
    s = str(x or "").strip()
    m = _DATA_RE.match(s)
    if m:
        return s
    m = _DATA_ISO.match(s)
    if m:
        return "%s.%s.%s" % (m.group(3), m.group(2), m.group(1))
    return ""


def _judet(x):
    """DUK regula judet: cod de judet pe 2 cifre ('1' respins, '01' acceptat). Sirul gol ramane gol."""
    j = _cif(x)
    return j.zfill(2) if j else ""


def _durata(x):
    """Componenta de durata (ani/luni/zile) ca intreg >= 0; implicit 0."""
    v = _cif(x)
    return int(v) if v else 0


def _attr(name, val, lim=None):
    v = _esc(val, lim)
    return '%s="%s"' % (name, v) if v != "" else ""


def _calitati(b):
    """Calitatile de beneficiar real bifate din {1,2,3,4}.
    Accepta `calitati=[...]` sau flag-uri individuale cal1_B..cal4_B (orice valoare truthy)."""
    out = set()
    for v in (b.get("calitati") or []):
        iv = _cif(v)
        if iv in ("1", "2", "3", "4"):
            out.add(iv)
    for i in ("1", "2", "3", "4"):
        v = b.get("cal%s_B" % i, b.get("cal%s" % i))
        if v not in (None, "", 0, "0", False):
            out.add(i)
    return sorted(out)


@dataclass
class Rezultat169:
    an: int
    luna: int
    nr_fiduciari: int = 0
    nr_constituitori: int = 0
    nr_beneficiari: int = 0
    nr_beneficiari_reali: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d169(manual):
    """Fara sume in schema (durata contractului = ani/luni/zile intregi). Agregatele sunt numerele de
    entitati declarate pe fiecare sectiune."""
    return {
        "nr_fiduciari": len(manual.get("fiduciari") or []),
        "nr_constituitori": len(manual.get("constituitori") or []),
        "nr_beneficiari": len(manual.get("beneficiari") or []),
        "nr_beneficiari_reali": len(manual.get("beneficiari_reali") or []),
    }


def pull(conn, schema, perioada):
    """D169 e MANUALA (Registrul central al fiduciilor nu e in aplicatie). Contractul cere `pull`.
    Nu atinge baza -> merge si cu conn=None."""
    return {}


def _erori_persoana(p, idx, sufix, eticheta, cif_ca_pf_pj=False, judet_obligatoriu=False):
    """Validare comuna pentru fiduciar (_F), constituitor (_Ct), beneficiar (_B1).
    judet_obligatoriu: DUK regula R83 - la constituitor si beneficiar judetul (sau tara) e obligatoriu;
    la fiduciar validatorul nu il cere (ramane optional)."""
    er = []
    pre = "%s %d:" % (eticheta, idx)
    if not str(p.get("den_" + sufix) or "").strip():
        er.append("%s lipsa denumire/nume (den_%s)." % (pre, sufix))
    cifv = _cif(p.get("cif_" + sufix))
    if cif_ca_pf_pj:
        if not _cif_pf_pj_ok(cifv):
            er.append("%s cod de identificare fiscala (cif_%s) invalid - CNP de 13 cifre sau CUI 2-10 cifre." % (pre, sufix))
    else:
        if not (2 <= len(cifv) <= 10):
            er.append("%s CIF (cif_%s) invalid - astept 2-10 cifre." % (pre, sufix))
    if not str(p.get("localit_" + sufix) or "").strip():
        er.append("%s lipsa localitate (localit_%s)." % (pre, sufix))
    if not str(p.get("adresa_" + sufix) or "").strip():
        er.append("%s lipsa adresa (adresa_%s)." % (pre, sufix))
    judet = _judet(p.get("judet_" + sufix))
    tara = str(p.get("tara_" + sufix) or "").strip()
    if judet_obligatoriu and not judet and not tara:
        er.append("%s lipsa judet (judet_%s) sau tara (tara_%s) - R83." % (pre, sufix, sufix))
    if judet == _JUDET_BUCURESTI:
        sector = _cif(p.get("sector_" + sufix))
        if sector not in ("1", "2", "3", "4", "5", "6"):
            er.append("%s sector_%s obligatoriu 1-6 pentru judetul 40 (Bucuresti)." % (pre, sufix))
    return er


def _erori_benefR(b, idx):
    er = []
    pre = "beneficiar real %d:" % idx
    if not str(b.get("den_B") or "").strip():
        er.append("%s lipsa nume si prenume (den_B)." % pre)
    stat_res = str(b.get("stat_resedinta_B") or "").strip().upper()
    if not stat_res:
        if not _cnp_valid(b.get("cif_B")):
            er.append("%s CNP (cif_B) invalid pentru rezident RO - astept 13 cifre cu cifra de control." % pre)
    else:
        if not str(b.get("cif_B") or "").strip():
            er.append("%s lipsa cod de identificare (cif_B)." % pre)
    if not _data(b.get("data_nasterii_B")):
        er.append("%s data nasterii (data_nasterii_B) invalida - astept zz.ll.aaaa." % pre)
    if not str(b.get("actId_B") or "").strip():
        er.append("%s lipsa serie si numar act de identitate (actId_B)." % pre)
    if not str(b.get("adresa_B") or "").strip():
        er.append("%s lipsa domiciliu/resedinta (adresa_B)." % pre)
    if not str(b.get("mod_control_B") or "").strip():
        er.append("%s lipsa modalitatea de exercitare a controlului (mod_control_B)." % pre)
    if not str(b.get("natura") or "").strip():
        er.append("%s lipsa natura si amploarea interesului (natura)." % pre)
    if not _calitati(b):
        er.append("%s cel putin o calitate de beneficiar real (1-4) trebuie bifata." % pre)
    return er


def _erori_unicitate(lista, sufix, eticheta):
    er = []
    vazute = set()
    for i, p in enumerate(lista, 1):
        c = _cif(p.get("cif_" + sufix))
        if c and c in vazute:
            er.append("%s %d: cif_%s '%s' duplicat - trebuie unic in sectiune." % (eticheta, i, sufix, c))
        vazute.add(c)
    return er


def erori_generare(prof, manual):
    er = []
    # semnatar + date declaratie
    if not str(manual.get("nume") or "").strip():
        er.append("Lipsa nume semnatar (nume).")
    if not str(manual.get("functie") or "").strip():
        er.append("Lipsa functie semnatar (functie).")
    cif = _cif(manual.get("cif"))
    if not (2 <= len(cif) <= 10):
        er.append("CIF fiduciar declarant (cif) invalid - astept 2-10 cifre.")
    # sectiunea I - inregistrarea contractului
    if not str(manual.get("nr_contract_I") or manual.get("nr_contract") or "").strip():
        er.append("Lipsa numarul contractului de fiducie (nr_contract_I).")
    if not _data(manual.get("data_contract_I") or manual.get("data_contract")):
        er.append("Data contractului de fiducie (data_contract_I) invalida - astept zz.ll.aaaa.")
    d1 = _data(manual.get("data1_I") or manual.get("data_inceput"))
    if not d1:
        er.append("Data de inceput a fiduciei (data1_I) invalida - astept zz.ll.aaaa.")
    d2 = _data(manual.get("data2_I") or manual.get("data_sfarsit"))
    if d1 and d2 and _cheie_data(d2) < _cheie_data(d1):
        er.append("data2_I trebuie sa fie >= data1_I.")
    if not str(manual.get("scop_fiducie") or "").strip():
        er.append("Lipsa scopul fiduciei (scop_fiducie).")
    # sectiuni obligatorii (min. 1 fiecare)
    fid = manual.get("fiduciari") or []
    ct = manual.get("constituitori") or []
    ben = manual.get("beneficiari") or []
    bR = manual.get("beneficiari_reali") or []
    if not fid:
        er.append("Lipsa fiduciar - cel putin unul este obligatoriu (sectiunea fiduciar).")
    if not ct:
        er.append("Lipsa constituitor - cel putin unul este obligatoriu (sectiunea constituitor).")
    if not ben:
        er.append("Lipsa beneficiar - cel putin unul este obligatoriu (sectiunea beneficiar).")
    if not bR:
        er.append("Lipsa beneficiar real - cel putin unul este obligatoriu (sectiunea benefR).")
    for i, f in enumerate(fid, 1):
        er.extend(_erori_persoana(f, i, "F", "fiduciar"))
    for i, c in enumerate(ct, 1):
        er.extend(_erori_persoana(c, i, "Ct", "constituitor", cif_ca_pf_pj=True, judet_obligatoriu=True))
    for i, b in enumerate(ben, 1):
        er.extend(_erori_persoana(b, i, "B1", "beneficiar", cif_ca_pf_pj=True, judet_obligatoriu=True))
    for i, b in enumerate(bR, 1):
        er.extend(_erori_benefR(b, i))
    er.extend(_erori_unicitate(fid, "F", "fiduciar"))
    er.extend(_erori_unicitate(ct, "Ct", "constituitor"))
    er.extend(_erori_unicitate(ben, "B1", "beneficiar"))
    er.extend(_erori_unicitate(bR, "B", "beneficiar real"))
    # DUK regula fiduciar declarant: cel putin un fiduciar cu cif_F = cif
    if fid and cif and not any(_cif(f.get("cif_F")) == cif for f in fid):
        er.append("Niciun fiduciar declarant: un <fiduciar> trebuie sa aiba cif_F = cif (%s) si bifa_F=1." % cif)
    return er


def _cheie_data(zzllaaaa):
    """Cheie comparabila (aaaammzz) dintr-un sir zz.ll.aaaa deja normalizat."""
    m = _DATA_RE.match(zzllaaaa or "")
    return (m.group(3) + m.group(2) + m.group(1)) if m else ""


def _persoana_xml(tag, p, sufix, cif_declarant=None):
    a = []
    if tag == "fiduciar":
        # bifa_F: 1 pentru fiduciarul declarant (cif_F = cif radacina) sau daca `declarant` e truthy
        este_decl = bool(p.get("declarant")) or (
            cif_declarant and _cif(p.get("cif_F")) == cif_declarant)
        a.append('bifa_F="%s"' % ("1" if este_decl else "0"))
    a.append(_attr("den_" + sufix, p.get("den_" + sufix), 200))
    a.append(_attr("cif_" + sufix, _cif(p.get("cif_" + sufix))))
    judet = _judet(p.get("judet_" + sufix))
    if judet:
        a.append('judet_%s="%s"' % (sufix, judet))
    if str(p.get("sector_" + sufix) or "").strip():
        a.append(_attr("sector_" + sufix, _cif(p.get("sector_" + sufix))))
    a.append(_attr("localit_" + sufix, p.get("localit_" + sufix), 100))
    a.append(_attr("adresa_" + sufix, p.get("adresa_" + sufix), 400))
    for k, lim in (("codp_", 6), ("tel_", 15), ("fax_", 15), ("email_", 250), ("tara_", 100)):
        key = k + sufix
        if str(p.get(key) or "").strip():
            a.append(_attr(key, p.get(key), lim))
    return "  <%s %s/>" % (tag, " ".join(x for x in a if x))


def _benefR_xml(b):
    a = []
    a.append(_attr("den_B", b.get("den_B"), 200))
    a.append(_attr("cif_B", _cif(b.get("cif_B"))))
    a.append(_attr("data_nasterii_B", _data(b.get("data_nasterii_B"))))
    a.append(_attr("actId_B", b.get("actId_B"), 50))
    stat_cet = str(b.get("stat_cetatenie_B") or "").strip().upper()
    if stat_cet:
        a.append(_attr("stat_cetatenie_B", stat_cet, 2))
    stat_res = str(b.get("stat_resedinta_B") or "").strip().upper()
    if stat_res:
        a.append(_attr("stat_resedinta_B", stat_res, 2))
    a.append(_attr("adresa_B", b.get("adresa_B"), 400))
    a.append(_attr("mod_control_B", b.get("mod_control_B"), 500))
    for i in _calitati(b):
        a.append('cal%s_B="1"' % i)
    a.append(_attr("natura", b.get("natura"), 500))
    return "  <benefR %s/>" % " ".join(x for x in a if x)


def build_xml(prof, an, luna, manual):
    cif = _cif(manual.get("cif"))
    h = []
    h.append('luna="%d"' % LUNA_FIXA)  # DUK regula luna: fix 12
    h.append('an="%d"' % int(an))
    h.append(_attr("nume", manual.get("nume"), 75))
    h.append(_attr("functie", manual.get("functie"), 75))
    h.append('bifa_modif="0"')  # cazul principal: inregistrare (nu modificare)
    h.append('bifa_incet="0"')  # cazul principal: inregistrare (nu incetare)
    h.append('cif="%s"' % cif)
    h.append(_attr("nr_contract_I", manual.get("nr_contract_I") or manual.get("nr_contract"), 50))
    h.append(_attr("data_contract_I", _data(manual.get("data_contract_I") or manual.get("data_contract"))))
    h.append(_attr("data1_I", _data(manual.get("data1_I") or manual.get("data_inceput"))))
    d2 = _data(manual.get("data2_I") or manual.get("data_sfarsit"))
    if d2:
        h.append('data2_I="%s"' % d2)
    h.append('ani_I="%d"' % _durata(manual.get("ani_I") or manual.get("durata_ani")))
    h.append('luni_I="%d"' % _durata(manual.get("luni_I") or manual.get("durata_luni")))
    h.append('zile_I="%d"' % _durata(manual.get("zile_I") or manual.get("durata_zile")))
    h.append(_attr("scop_fiducie", manual.get("scop_fiducie"), 500))
    fid = manual.get("fiduciari") or []
    ct = manual.get("constituitori") or []
    ben = manual.get("beneficiari") or []
    bR = manual.get("beneficiari_reali") or []
    corp = []
    corp += [_persoana_xml("fiduciar", f, "F", cif_declarant=cif) for f in fid]
    corp += [_persoana_xml("constituitor", c, "Ct") for c in ct]
    corp += [_persoana_xml("beneficiar", b, "B1") for b in ben]
    corp += [_benefR_xml(b) for b in bR]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<D169 xmlns="%s" %s>\n%s\n</D169>\n'
            % (NS, " ".join(x for x in h if x), "\n".join(corp)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = LUNA_FIXA
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D169 nu se poate genera: " + " ".join(er))
    xml = build_xml(prof, an, luna, manual)
    c = calcul_d169(manual)
    res = Rezultat169(an=an, luna=luna, nr_fiduciari=c["nr_fiduciari"],
                      nr_constituitori=c["nr_constituitori"], nr_beneficiari=c["nr_beneficiari"],
                      nr_beneficiari_reali=c["nr_beneficiari_reali"])
    return xml, res
